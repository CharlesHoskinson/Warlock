#!/usr/bin/env python3
"""Model-based test: replay Quint traces of fileops.qnt against the real ops.sh.

    python3 mbt.py [--traces N] [--steps N] [--seed S] [--keep]

1. `quint run fileops.qnt --mbt --n-traces N --out-itf ...` samples random
   operation sequences from the model (each state records the call it made and
   the exit code the model expects).
2. For every trace a fresh sandbox is built on the home filesystem
   (~/.cache/omarchy-files-mbt/<run>/root) with its own trash
   (XDG_DATA_HOME=<run>/data), matching the model's initial tree; locked folders
   are chmod 555.
3. Each step runs ops.sh with the same arguments — as the user, or for
   `asRoot` steps inside `unshare -r` (a user namespace where we are root, so
   permission checks are bypassed on sandbox files exactly like sudo) — and
   compares exit code, printed path, the whole tree and the trash with the model.

Only paths inside the sandbox are ever touched.
"""
import argparse, glob, json, os, shutil, stat, subprocess, sys, tempfile, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OPS = os.environ.get("MBT_OPS") or os.path.join(os.path.dirname(HERE), "scripts", "ops.sh")
SPEC = os.path.join(HERE, "fileops.qnt")
BASE = os.path.expanduser("~/.cache/omarchy-files-mbt")


# ------------------------------------------------------------------ ITF decode
def dec(v):
    if isinstance(v, dict):
        if "#bigint" in v: return int(v["#bigint"])
        if "#map" in v: return {freeze(dec(k)): dec(x) for k, x in v["#map"]}
        if "#set" in v: return [dec(x) for x in v["#set"]]
        if "#tup" in v: return tuple(dec(x) for x in v["#tup"])
        if "tag" in v and "value" in v: return v["tag"]
        return {k: dec(x) for k, x in v.items()}
    if isinstance(v, list): return [dec(x) for x in v]
    return v

def freeze(x):
    if isinstance(x, list): return tuple(freeze(i) for i in x)
    if isinstance(x, dict): return tuple(sorted((k, freeze(v)) for k, v in x.items()))
    return x


# --------------------------------------------------------------------- render
def name_str(n):
    n = dict(n) if not isinstance(n, dict) else n
    s = n["base"]
    for k in n["copies"]:
        s += " (copy)" if k == 1 else f" (copy {k})"
    return s + n["ext"]

def rel(path):  # model path (tuple of frozen names) -> relative string
    return "/".join(name_str(dict(p) if isinstance(p, tuple) else p) for p in path)

def absp(root, path):
    r = rel(path)
    return root if r == "" else os.path.join(root, r)


# ------------------------------------------------------------------ snapshots
def model_tree(fs):
    out = {}
    for p, node in fs.items():
        out[rel(p)] = (node["kind"], node["content"] if node["kind"] == "File" else 0,
                       bool(node["locked"]) if node["kind"] == "Dir" else False)
    return out

def model_trash(trash, root):
    return sorted((os.path.join(root, rel(e["orig"])) if rel(e["orig"]) else root,
                   rel(e["rel"]), e["node"]["kind"],
                   e["node"]["content"] if e["node"]["kind"] == "File" else 0) for e in trash)

def content_of(path):
    with open(path) as f:
        t = f.read()
    return 0 if t == "" else int(t.strip()[1:])   # files hold "c<k>"

def real_tree(root):
    out = {"": ("Dir", 0, not (os.stat(root).st_mode & stat.S_IWUSR))}
    for dirpath, dirnames, filenames in os.walk(root):
        for d in dirnames:
            p = os.path.join(dirpath, d)
            out[os.path.relpath(p, root)] = ("Dir", 0, not (os.lstat(p).st_mode & stat.S_IWUSR))
        for f in filenames:
            p = os.path.join(dirpath, f)
            out[os.path.relpath(p, root)] = ("File", content_of(p), False)
    return out

def real_trash(data):
    info, files, out = os.path.join(data, "Trash/info"), os.path.join(data, "Trash/files"), []
    if not os.path.isdir(info): return out
    for inf in os.listdir(info):
        with open(os.path.join(info, inf)) as f:
            orig = next(l[5:].strip() for l in f if l.startswith("Path="))
        orig = urllib.parse.unquote(orig)
        top = os.path.join(files, inf[:-len(".trashinfo")])
        entries = [(top, "")]
        if os.path.isdir(top) and not os.path.islink(top):
            for dp, dn, fn in os.walk(top):
                entries += [(os.path.join(dp, x), os.path.relpath(os.path.join(dp, x), top)) for x in dn + fn]
        for p, r in entries:
            if os.path.isdir(p): out.append((orig, "" if r == "" else r, "Dir", 0))
            else: out.append((orig, "" if r == "" else r, "File", content_of(p)))
    return sorted(out)


# ------------------------------------------------------------------- sandbox
def build(root, fs):
    os.makedirs(root)
    for p in sorted(fs, key=len):
        node, a = fs[p], absp(root, p)
        if p == (): continue
        if node["kind"] == "Dir": os.mkdir(a)
        else:
            with open(a, "w") as f:
                f.write("" if node["content"] == 0 else f"c{node['content']}")
    for p in sorted(fs, key=len, reverse=True):  # lock deepest first
        if fs[p]["kind"] == "Dir" and fs[p]["locked"]:
            os.chmod(absp(root, p), 0o555)

def cleanup(top):
    unlock_all(top)
    shutil.rmtree(top, ignore_errors=True)

def unlock_all(top):
    for dp, dn, fn in os.walk(top):
        os.chmod(dp, 0o755)
        for d in dn:
            try: os.chmod(os.path.join(dp, d), 0o755)
            except OSError: pass

def argv_for(call, root):
    op, a = call["op"], lambda p: absp(root, p)
    if op in ("copy", "move"): return [op, a(call["dst"])] + [a(s) for s in call["srcs"]]
    if op in ("mkdir", "newfile"): return [op, a(call["dst"]), name_str(call["name"])]
    if op == "rename":
        s = a(call["srcs"][0])
        return [op, s, os.path.join(os.path.dirname(s), name_str(call["name"]))]
    if op == "trash": return [op] + [a(s) for s in call["srcs"]]
    raise ValueError(op)


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", type=int, default=200)
    ap.add_argument("--steps", type=int, default=12)
    ap.add_argument("--seed")
    ap.add_argument("--keep", action="store_true", help="keep sandboxes of failing traces")
    args = ap.parse_args()

    run_dir = tempfile.mkdtemp(prefix="run-", dir=(os.makedirs(BASE, exist_ok=True) or BASE))
    itf_dir = os.path.join(run_dir, "itf")
    os.makedirs(itf_dir)
    cmd = ["quint", "run", SPEC, "--mbt", "--max-steps", str(args.steps),
           "--max-samples", str(args.traces), "--n-traces", str(args.traces),
           "--out-itf", os.path.join(itf_dir, "t{seq}.itf.json")]
    if args.seed: cmd += ["--seed", args.seed]
    q = subprocess.run(cmd, capture_output=True, text=True)
    traces = sorted(glob.glob(os.path.join(itf_dir, "*.itf.json")))
    if not traces:
        print(q.stdout[-2000:], q.stderr[-2000:]); sys.exit(2)

    steps = fails = 0
    by_op = {}
    for ti, tf in enumerate(traces):
        states = [dec(s) for s in json.load(open(tf))["states"]]
        sb = os.path.join(run_dir, f"t{ti}")
        root, data = os.path.join(sb, "root"), os.path.join(sb, "data")
        os.makedirs(data)
        build(root, states[0]["fs"])
        env = dict(os.environ, XDG_DATA_HOME=data, GIO_USE_VFS="local")  # no gvfs daemons/metadata
        bad = None
        for si, st in enumerate(states[1:], 1):
            call = st["lastCall"]
            argv = argv_for(call, root)
            pre = ["unshare", "-r"] if call["asRoot"] else []
            r = subprocess.run(pre + ["bash", OPS] + argv, capture_output=True, text=True, env=env)
            steps += 1
            key = call["op"] + ("/root" if call["asRoot"] else "") + f" →{st['lastCode']}"
            by_op[key] = by_op.get(key, 0) + 1
            problems = []
            if r.returncode != st["lastCode"]:
                problems.append(f"exit {r.returncode}, model expects {st['lastCode']}")
            if st["lastCode"] == 0 and call["op"] in ("mkdir", "newfile"):
                want = absp(root, st["lastCreated"])
                if r.stdout.strip() != want:
                    problems.append(f"printed {r.stdout.strip()!r}, model created {want!r}")
            mt, rt = model_tree(st["fs"]), real_tree(root)
            if mt != rt:
                for k in sorted(set(mt) | set(rt)):
                    if mt.get(k) != rt.get(k):
                        problems.append(f"tree {k!r}: model {mt.get(k)} real {rt.get(k)}")
            mtr, rtr = model_trash(st["trash"], root), real_trash(data)
            if mtr != rtr:
                problems.append(f"trash differs:\n      model {mtr}\n      real  {rtr}")
            if problems:
                bad = (si, call, argv, problems)
                break
        if bad:
            fails += 1
            si, call, argv, problems = bad
            print(f"\n✗ trace {ti} step {si}: {'sudo ' if call['asRoot'] else ''}ops.sh "
                  + " ".join(repr(os.path.relpath(a, root)) if a.startswith(root) else repr(a) for a in argv))
            for p in problems[:8]: print("    " + p)
            if not args.keep:
                cleanup(sb)
        else:
            cleanup(sb)

    print(f"\n{len(traces)} traces · {steps} steps replayed against ops.sh · {fails} failing trace(s)")
    for k in sorted(by_op): print(f"  {k:24} {by_op[k]}")
    if not (args.keep and fails):
        cleanup(run_dir)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

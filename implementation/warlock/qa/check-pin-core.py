"""Protected single-TU maximized pin policy; preserve the exact owning core archive."""
import hashlib, importlib.util, json, pathlib, resource, shlex, shutil, subprocess, sys, time
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope = require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OWNER = REPO / 'implementation/maximized-stack-v1/native-core-v2'
pointer=json.loads((ROOT/'qa/current-focus-core.json').read_text())
PRIOR=(REPO/pointer['report']).parent
HELPER = REPO/'implementation/warlock-core-family-crop-v16/qa/archive.py'
spec = importlib.util.spec_from_file_location('owning_archive', HELPER)
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)
OUT = ROOT / 'qa/runs' / ('pin-core-' + str(time.time_ns()))
OUT.mkdir()
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r = dict(passed=False, nativeAcceptance=False, installed=False, protectedScope=scope, commands=[],
         scope='One owning ConfigActions pin/MAX TU and exact relink; native eligibility/input remains separately verified')

def run(name, argv):
    p = subprocess.run(list(map(str, argv)), cwd=OWNER/'build', capture_output=True, timeout=240)
    (OUT/(name+'.stdout')).write_bytes(p.stdout)
    (OUT/(name+'.stderr')).write_bytes(p.stderr)
    r['commands'].append(dict(name=name, command=list(map(str, argv)), exitCode=p.returncode))
    print(name, p.returncode, flush=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
    return p.stdout

def dependencies(path):
    names = shlex.split(path.read_text().replace('\\\n', ' ').split(':', 1)[1])
    names = names[:next((i for i, name in enumerate(names) if name.endswith(':')), len(names))]
    return {str((pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n).resolve()):
            sha(pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n) for n in names}

try:
    assert sha(PRIOR/'report.json')==pointer['reportSHA256']
    prior = json.loads((PRIOR/'report.json').read_text())
    assert prior['passed'] and sha(PRIOR/'Hyprland') == prior['binarySHA256']
    assert sha(PRIOR/'libhyprland_lib.a') == prior['archiveSHA256']
    originals = archive.archive_payloads(PRIOR/'libhyprland_lib.a')
    seat = [row for row in originals if row['name'] == 'ConfigActions.cpp.o']
    assert len(seat) == 1 and len(originals) == 433
    tree = OUT/'owning-headers'
    for rel, digest in prior['owningHeaders'].items():
        p = PRIOR/'owning-headers'/rel
        assert sha(p) == digest
        q = tree/rel
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, q)
    source = ROOT/'native/core/ConfigActions.cpp'
    source_hash = sha(source)
    compiled = tree/'src/config/shared/actions/ConfigActions.cpp'
    shutil.copyfile(source, compiled)
    original = OWNER/'src/config/shared/actions/ConfigActions.cpp'
    assert subprocess.check_output(['git', '-C', str(REPO), 'show', 'HEAD:'+str(original.relative_to(REPO))]) == original.read_bytes()
    entry = next(e for e in json.loads((OWNER/'build/compile_commands.json').read_text()) if e['file'] == str(original))
    args = shlex.split(entry['command'])
    command, i = [], 0
    while i < len(args):
        a = args[i]
        if a in ('-o', '-include'):
            i += 2
            continue
        if a == '-c' or a == str(original):
            i += 1
            continue
        if a.startswith('-I'+str(OWNER)) and '/build/' not in a and '/subprojects/' not in a:
            a = '-I'+str(tree)+a[len('-I'+str(OWNER)):]
        command.append(a)
        i += 1
    obj = OUT/'ConfigActions.cpp.o'
    run('compile-pin', command+['-MD', '-MF', str(OUT/'pin.d'), '-o', str(obj), '-c', str(compiled)])
    deps = dependencies(OUT/'pin.d')
    assert not any(p.startswith('/usr/include/hyprland') or p.startswith(str(OWNER)+'/src/') for p in deps)
    target = OUT/'libhyprland_lib.a'
    archive.replace_payload(PRIOR/'libhyprland_lib.a', target, seat[0]['sha256'], obj)
    run('archive-index', ['ar', 's', target])
    new = archive.archive_payloads(target)
    assert len(new) == len(originals)
    for a, b in zip(originals, new):
        assert a['name'] == b['name']
        assert b['sha256'] == sha(obj) if a == seat[0] else a == b
    link = next(c['command'] for c in prior['commands'] if c['name'] == 'link').copy()
    for i, a in enumerate(link):
        if i and link[i-1] == '-o': link[i] = str(OUT/'Hyprland')
        elif a == str(PRIOR/'libhyprland_lib.a'): link[i] = str(target)
        elif a.startswith('-Wl,--dependency-file='): link[i] = '-Wl,--dependency-file='+str(OUT/'link.d')
    run('link', link)
    actual = dependencies(OUT/'link.d')
    expected = {str(target) if p == str(PRIOR/'libhyprland_lib.a') else p:
                sha(target) if p == str(PRIOR/'libhyprland_lib.a') else digest
                for p, digest in prior['linkDependencies'].items()}
    assert actual == expected
    exports = []
    for name, binary in [('ancestor', PRIOR/'Hyprland'), ('candidate', OUT/'Hyprland')]:
        exports.append({tuple(line.split()[1:]) for line in run(name+'-exports', ['nm', '-D', '--defined-only', binary]).decode().splitlines()})
    assert exports[0] == exports[1], 'Public exports changed'
    assert sha(source) == source_hash
    for rel, digest in prior['owningHeaders'].items(): assert sha(tree/rel) == digest
    for p, digest in deps.items(): assert sha(p) == digest
    r.update(passed=True, binary=str(OUT/'Hyprland'), binarySHA256=sha(OUT/'Hyprland'),
             archiveSHA256=sha(target), sourceSHA256=source_hash, originalSourceSHA256=sha(original),
             owningHeaders=prior['owningHeaders'], existingPublicHeadersUnchanged=True,
             existingObjectLayoutsUnchanged=True, unchangedArchiveMembers=432,
             ancestor=dict(report=str(PRIOR/'report.json'), reportSHA256=sha(PRIOR/'report.json')),
             archiveHelperSHA256=sha(HELPER), dependencies=deps, linkDependencies=actual,
             aqLibrary=prior['aqLibrary'], aqLibrarySHA256=prior['aqLibrarySHA256'])
except Exception as error:
    import traceback
    r.update(error=repr(error), traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps(dict(passed=r['passed'], report=str(OUT/'report.json'), error=r.get('error'))))
raise SystemExit(not r['passed'])

I've finished reading the files and am writing up the audit now.

# Warlock contributor plugin: offline checker and scaffolding audit

I only read files: 11 reads covering `warlock.py`, `contract.json`, `SKILL.md`, `README.md`, `test_warlock.py`, `session_hook.py`, the AAR, `INSTRUCTIONS.md`, `loop.py` and the CI workflow. I did not run the tests or the checker, so nothing below claims execution, AT or GUI results.

**Assumptions about the root's concurrent work:** `CONTRIBUTING.md` and `.github/` are untracked in the session's git status, so the CI workflow isn't running on any PR yet. `docs/warlock-build-loop/v2/loop.py` exists in the working tree. I didn't check whether it is committed, or whether its delegate `implementation/elm-build-loop-v1/loop.py` exists.

## Top 3 findings

### 1. Renames hide archive deletions, so the "preserve archived implementation" rule can be bypassed (must fix)

**Scenario:** A PR runs `git mv implementation/warlock-preview-provider-v143/src/X.elm implementation/warlock/src/X.elm`. This is the "merge older prototypes wholesale" move the AAR rejects.

- Git detects renames by default, and `--name-only` then prints only the destination.
- In CI, `check --base-ref` sees only `implementation/warlock/src/X.elm` and passes.
- Locally, the same thing happens if `src/X.elm` is a declared new slice path.
- The comment at `warlock.py:61` ("preserves … both rename endpoints") is wrong.
- `warlock.py:285` also hashes every changed file only to throw the hash away. On a large PR that costs a lot, and any symlink in the diff makes `safe()` stop CI with exit 2.

**Fix at `warlock.py:60-65`:**
```python
def dirty(root):
    # NUL encoding preserves spaces/newlines; --no-renames reports both rename endpoints.
    names = set(git(root, 'diff', '--name-only', '--no-renames', '-z').decode().split('\0'))
    names.update(git(root, 'diff', '--cached', '--name-only', '--no-renames', '-z').decode().split('\0'))
    names.update(git(root, 'ls-files', '--others', '--exclude-standard', '-z', '--', 'implementation/warlock', 'plugins/warlock-contributor').decode().split('\0'))
    return {n: fingerprint(root, n) for n in sorted(names) if n}
```

**Fix at `warlock.py:283-286`** (path names only, no hashing):
```python
            changed = []
            if args.base_ref:
                changed = [n for n in git(root, 'diff', '--name-only', '--no-renames', '-z', args.base_ref, '--').decode().split('\0') if n]
            errors = ['Archival implementation change: ' + n for n in changed if n.startswith('implementation/') and not n.startswith('implementation/warlock/')]
```

**Tests to add in `test_warlock.py`:**
```python
    def test_base_ref_archive_rename_into_candidate_rejected(self):
        base = self.run_git('rev-parse', 'HEAD')
        self.run_git('mv', 'implementation/warlock-preview-provider-v143/frozen.txt', 'implementation/warlock/src/Frozen.elm')
        self.run_git('commit', '-qm', 'move archive into candidate')
        self.cli('check', '--base-ref', base, ok=False)

    def test_staged_archive_rename_to_declared_path_rejected(self):
        self.slice['paths'] += ['src/Frozen.elm']
        self.write('.warlock-contributor/override.json', self.slice)
        self.cli('start', '--owner', 'contributor', '--slice-file', '.warlock-contributor/override.json')
        self.run_git('mv', 'implementation/warlock-preview-provider-v143/frozen.txt', 'implementation/warlock/src/Frozen.elm')
        self.cli('check', ok=False)
```
There is currently no `--base-ref` test at all, even though CI depends on it.

### 2. Record writes are racy and not atomic (must fix)

**Scenario:** Six agents share one worktree.

- `start` checks `path.exists()` at `:263` and writes at `:278`. Two concurrent `start`s both pass the check, and the second silently overwrites the first owner's record.
- `record` reads at `:289` and writes at `:315` with no lock, so two concurrent `record`s lose an iteration.
- `write_text` is not atomic. A crash or timeout mid-write leaves broken JSON, and every later `loop.py check` exits 2.

**Fix:** add near `:37`:
```python
import contextlib, os, tempfile
try:
    import fcntl
except ImportError:  # non-POSIX: best effort, atomic replace still applies
    fcntl = None

@contextlib.contextmanager
def locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_name(path.name + '.lock'), 'a') as lock:
        if fcntl:
            fcntl.flock(lock, fcntl.LOCK_EX)
        yield

def write_record(path, record, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name + '.')
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(json.dumps(record, indent=2) + '\n'); stream.flush(); os.fsync(stream.fileno())
        if exclusive:
            os.link(tmp, path)  # atomic create; FileExistsError if a concurrent start won
        else:
            os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
```

- **At `:277-278`:** replace with `write_record(path, record, exclusive=True)`.
- **At `:288-316`:** wrap the record read-modify-write in a lock:
  ```python
  with (locked(path) if args.command == 'record' else contextlib.nullcontext()):
      record = read(path)
      ...
  ```
  Inside it, `:315` becomes `write_record(path, record)`.

The lock file sits next to the record, which `start` has already confirmed is ignored by Git.

### 3. The mandatory check fails for things the contributor didn't do (must fix)

**Scenario:** `start` snapshots every dirty file into `foreignDirty`, including `AGENTS.md`, `.gitignore`, `docs/...` and untracked `plugins/warlock-contributor/**`. All of these are dirty right now.

- `:153-155` treats any later change to them as an error.
- The root agent is editing `AGENTS.md`, `.gitignore` and `CONTRIBUTING.md` right now, and the plugin agents are writing `reviews/*.jsonl`. So every participant's `loop.py check` returns 1, and `native` campaigns refuse to run.
- Any dirty symlink, or an untracked nested-repo directory, makes `safe()`/`digest()` raise. That turns every `start`/`check` into exit 2.

**Fix at `:153-155`:** keep errors for the product and archive trees; downgrade the rest to warnings:
```python
    for name, old in record['foreignDirty'].items():
        if fingerprint(root, name) != old:
            message = 'Protected foreign-dirty path changed: ' + name
            # Only implementation trees are attributable to a product slice; repository
            # docs/config/plugin files owned by concurrent workers may keep changing.
            (errors if name.startswith('implementation/') else warnings).append(message)
```

**Add `fingerprint` near `:37`.** Git-listed names can't contain `..`, and only the last component can be a symlink:
```python
def fingerprint(root, name):
    p = root / name
    if p.is_symlink():
        return 'symlink:' + hashlib.sha256(os.fsencode(os.readlink(p))).hexdigest()
    if p.is_dir():
        return 'directory'
    return digest(safe(root, name))
```

**Test updates:**
- Change `test_foreign_dirty_preserved_and_mutation_rejected` and `test_adoption_preserves_unrelated_foreign_dirty_file` to use a committed `implementation/warlock/src/Other.elm` instead of `foreign.txt`.
- Add a test asserting that a root-level `foreign.txt` change gives `ok` plus a warning.

## Other small must-fixes

1. **Leftover record blocks doc work** (`:151`, `:263`). Once `STATE.activeSlice` moves on (the commits show UI-007 → UI-004 → UI-005), the leftover default `.warlock-contributor/slice.json` fails every plain `check` with "Live selected slice changed". `start` refuses to replace it, and the hook reports "needs attention" forever. Two fixes:
   - Add `check --project-only`, which takes the no-record branch (`elif args.command == 'check' and (args.project_only or not path.exists()):`). Reject it when combined with `--require-record`.
   - Add `start --supersede`. Inside the lock, move the old record with `os.link` + `os.unlink` to `path.with_name(f"{path.stem}.{re.sub(r'[^A-Za-z0-9._-]', '_', old['slice']['id'])}.{old['startedUTC'].replace(':', '')}.json")`.
2. **Duplicate paths after normalization** (`:106`). `['src/Desktop.elm', 'implementation/warlock/src/Desktop.elm']` passes the uniqueness check. Add `if len(set(normalized)) != len(normalized): raise ValueError('Slice paths must be unique after normalization')` after the loop at `:114`.
3. **Misleading error for a non-ignored record** (`:265`). When the record isn't ignored, `git check-ignore` exits 1, so `git()` raises with an empty "Git operation failed:". Use `subprocess.run([... 'check-ignore', '-q', '--', args.record]).returncode != 0` and raise the existing message.
4. **Accepted `sourceRevision` can be anything** (`:182-184`). Add:
   ```python
   if source_tuple.get('sourceRevision') and subprocess.run(['git', '-C', str(root), 'cat-file', '-e', str(source_tuple['sourceRevision']) + '^{commit}'], capture_output=True).returncode:
       errors.append('Accepted sourceRevision is not a commit in this repository')
   ```
5. **Tests aren't isolated from the developer's environment** (`test_warlock.py:55-66`, `:395`).
   - If the tests run from a pre-commit hook, the inherited `GIT_DIR`/`GIT_INDEX_FILE` would point the fixture `git add` at the **real** repository index.
   - A global `commit.gpgsign`, `core.hooksPath` or `core.excludesFile` makes fixture commits and `check-ignore` results machine-dependent.
   - An inherited `GROK_*` variable makes the hook print nothing, so `json.loads('')` fails.
   - Fix: add the block below and pass `env=ENV` to `run_git`, `cli` and the hook subprocess. The same `GIT_*` scrub belongs in `warlock.py:git()` for the checker.
   ```python
   ENV = {k: v for k, v in os.environ.items() if not k.startswith(('GIT_', 'GROK_'))}
   ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0')
   ```
6. **Performance** (`:156`). `validate` calls `dirty()`, which hashes every dirty file and then uses only the names. `record` validates twice. Add a `dirty_names(root)` for `validate` so the 5-second hook budget isn't spent hashing other workers' files.

## Known limitations (document, don't fix)

- **Records are self-attested.** Someone can hand-edit `historicalAfterSourceChange` onto the latest claim and turn a stale claim into a warning, or fake iteration `sourceHashes` to show progress. Allowing that flag only when a later iteration exists would mean restructuring the pre-append validate at `:295`. The contract already says records are self-attested.
- **Accepted evidence may be untracked, as long as it isn't ignored.** Requiring it to be tracked would break the INSTRUCTIONS order (record at step 5, commit at step 6).
- **A new untracked prototype directory isn't caught locally.** Something like `implementation/warlock-v144/` is outside the `ls-files` pathspec. CI's `--base-ref` catches it once committed. A fix is an extra `ls-files --others --directory -- implementation ':(exclude)implementation/warlock'`.
- **Local `--base-ref` uses a two-dot diff against the working tree.** That's correct for GitHub's PR merge checkout but can blame you for base-branch changes when run locally on a stale branch.
- **Platform:** the tests' `symlink_to` and the `fcntl`/`os.link` above need POSIX. That's acceptable for an Omarchy/Linux project; add `skipUnless(hasattr(os, 'symlink'))` if needed.

## Portability on a fresh clone

The checker uses only the standard library plus the `git` CLI. It needs Python 3.9+ for `Path.is_relative_to`, and CI pins 3.12. The tests copy the real `requirements.json` and ledger from the checkout. That works on a fresh clone only if both are committed; I didn't verify the ledger is tracked. Apart from fix 5 above, the fixtures are hermetic: temporary Git repositories, no network, no credentials.

## Recommended minimal configuration

- **Doc, plugin or support work:** `warlock.py check --project-only` before and after (plain `check` until that flag exists). No slice, no record, no GUI gates.
- **CI:**
  - Keep the three existing steps, with fix 1 applied.
  - Run the unit tests with the isolated `ENV`.
  - Don't expect local ownership records in CI.
- **GUI product slice:**
  - `start --owner X`, with `--supersede` once the active slice has moved on.
  - `loop.py check` at the start and end of each continuation.
  - `record --outcome …` after each iteration.
  - Use `--claim-file` only for scenario verdicts, and mark a claim `accepted` only with an external reviewer and a real commit as `sourceRevision`.
- **Hooks:** keep them advisory only, as they are now. They never replace the explicit calls above.

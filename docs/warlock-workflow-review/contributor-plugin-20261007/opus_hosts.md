# Warlock contributor plugin review: host packaging, hooks and discoverability

The plugin is mostly sound. The hooks only read state, never write records and never start another agent session. I found one bug that can block contributors' prompts, one problem with stale installed copies, and one requirement that the CI and loop wrapper the root is adding can't meet.

**What I read (12 reads):** `scripts/warlock.py`, `scripts/session_hook.py`, `hooks/hooks.json`, `hooks/codex.json`, `README.md`, `skills/warlock-contribute/SKILL.md`, both plugin manifests, the root `.claude-plugin/marketplace.json`, `references/contract.json` and `qa/test_warlock.py`. I also ran one targeted search over the AAR and `INSTRUCTIONS.md`. The search didn't show `INSTRUCTIONS.md:20` or `AAR.md:64` because those lines are too long, so I haven't checked my advice against them.

**What I didn't read:** `references/workflow.md`, `AGENTS.md`, `.agents/`, `.github/` and `CONTRIBUTING.md`. Wherever I describe CI, the loop wrapper or the Codex marketplace below, that's an assumption about integration that doesn't exist yet. I haven't run any tests or used any host, so none of this comes from running the code.

## Recursion and blocking check

- **No recursion.** The hook runs `warlock.py check`, which only runs read-only git commands (`diff`, `ls-files`, `rev-parse`). It never starts `claude`, `codex` or `grok`, and no hook references `reviews/run_opus.py`. If `run_opus.py` launches a child session, that session's hooks just run the same harmless checker once.
- **No writes.** `check` doesn't write anything, and `-B` stops Python writing `__pycache__` into the plugin cache.
- **Python errors are handled.** All expected errors are caught, the checker gets 5 seconds against a hook timeout of 10, and the hook prints nothing outside a Warlock repo.
- **One way to block remains** (finding 1): the hook command line itself, not the Python script.

## Top 3 findings

### 1. MUST-FIX: the hook command can block every prompt

**Where:** `hooks/hooks.json:3-4` and `hooks/codex.json:3-4`.

**How it happens:** Suppose the plugin-root variable is unset or named differently. That could be because Codex doesn't use `${PLUGIN_ROOT}` (I couldn't confirm this), because Grok doesn't set `GROK_PLUGIN_ROOT`, or because the plugin cache was pruned. The command then becomes `python3 -B "/scripts/session_hook.py"`. Python exits with code **2** when it can't open a script. Claude Code treats exit 2 from `UserPromptSubmit` as "block and erase the prompt". Codex's hooks appear to copy that convention, but I haven't confirmed it.

The result is that a doc-only contributor can't send any prompt at all. That breaks the README's promise (line 40) that hooks "never block prompts".

**Fix (shared command shape):**

```json
{
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "python3 -B \"${CLAUDE_PLUGIN_ROOT:-$GROK_PLUGIN_ROOT}/scripts/session_hook.py\" || true", "timeout": 10}]}],
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python3 -B \"${CLAUDE_PLUGIN_ROOT:-$GROK_PLUGIN_ROOT}/scripts/session_hook.py\" || true", "timeout": 10}]}]
  }
}
```

Make the same change in `codex.json`, keeping `${PLUGIN_ROOT}` there. `|| true` keeps the script's output and forces exit code 0.

**Also change `session_hook.py`:**
- **Check for Grok first.** At the moment it runs the checker for up to 5 seconds and then throws the result away (lines 27-40).
- **Catch everything.** Widen the `except` so that no exception can escape.

```python
# session_hook.py, replacing lines 27-45
        if os.environ.get("GROK_HOOK_EVENT") or os.environ.get("GROK_PLUGIN_ROOT"):
            # Grok ignores passive stdout; the skill and repository loop carry policy.
            return
        checker = Path(__file__).resolve().with_name("warlock.py")
        result = subprocess.run([sys.executable, "-B", str(checker), "--repo", str(root),
                                 "--json", "check"], capture_output=True, text=True, timeout=5)
        passed = result.returncode == 0
        if event == "UserPromptSubmit" and passed:
            # SessionStart (startup/resume/compact) already delivered the reminder.
            return
        state = "passed" if passed else "needs attention"
        context = ("Warlock contribution checker " + state + ". For Warlock code use the "
                   "warlock-contribute skill, follow docs/warlock-build-loop/v2/INSTRUCTIONS.md, "
                   "and run `python3 -B plugins/warlock-contributor/scripts/warlock.py --repo . check` "
                   "before implementation and before reporting. Fix findings within the selected "
                   "product slice. Structural compliance does not establish original GUI/native/AT "
                   "acceptance. Unrelated work may continue.")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                                                 "additionalContext": context}}))
    except Exception:
        return
```

**Why only emit on a failing prompt:** this is a recommendation, not a must-fix. Today the same paragraph is added to every prompt, which grows the context over a long session. The constant command string is safe to include: it's fixed text, not checker output.

**Tests to add** to `qa/test_warlock.py` (also add `import os`). The first test fails against the current hooks, which demonstrates the bug.

```python
    def test_hook_commands_fail_open_without_plugin_root(self):
        for name in ('hooks/hooks.json', 'hooks/codex.json'):
            for event, groups in json.loads((PLUGIN/name).read_text())['hooks'].items():
                for hook in (h for g in groups for h in g['hooks']):
                    proc = subprocess.run(['sh', '-c', hook['command']], input='{}',
                                          env={'PATH': os.environ['PATH']}, capture_output=True,
                                          text=True, timeout=20)
                    self.assertEqual(proc.returncode, 0, name + ' ' + event)

    def test_grok_hook_is_silent(self):
        payload = {'hookEventName': 'SessionStart', 'cwd': str(self.repo)}
        proc = subprocess.run([sys.executable, '-B', str(PLUGIN/'scripts/session_hook.py')],
                              input=json.dumps(payload), capture_output=True, text=True,
                              env={**os.environ, 'GROK_PLUGIN_ROOT': str(PLUGIN)})
        self.assertEqual((proc.returncode, proc.stdout), (0, ''))

    def test_packaging_paths_resolve(self):
        claude = json.loads((PLUGIN/'.claude-plugin/plugin.json').read_text())
        codex = json.loads((PLUGIN/'.codex-plugin/plugin.json').read_text())
        market = json.loads((PLUGIN.parents[1]/'.claude-plugin/marketplace.json').read_text())
        self.assertEqual(claude['name'], codex['name'])
        self.assertTrue((PLUGIN/codex['hooks']).is_file())
        self.assertTrue((PLUGIN/'skills/warlock-contribute/SKILL.md').is_file())
        entry = next(p for p in market['plugins'] if p['name'] == claude['name'])
        self.assertEqual((PLUGIN.parents[1]/entry['source']).resolve(), PLUGIN)
```

The existing test `test_hook_is_advisory_and_unrelated_work_is_allowed` should still pass. Its fixture makes the check fail, so the hook still produces output.

### 2. MUST-FIX: installed copies run stale code and look at the wrong repo

**Where:** `SKILL.md:8` ("this installed plugin's `scripts/warlock.py`") and `warlock.py:195` (the `--repo` default, `parents[3]`).

**How it happens:** A contributor installs the plugin through the marketplace, and Claude Code caches a copy at version `0.1.0`. Later the repo fixes the checker or the contract, but the skill keeps sending agents to the old cached copy. If an agent also leaves out `--repo`, `parents[3]` points somewhere inside the cache folder. The agent then gets a confusing exit 2 ("file not found") instead of a check.

The README admits the copies may be cached (line 36), but the skill still tells agents to use them. `INSTRUCTIONS.md:22` says the loop uses the plugin "even without installing", so the repo's own copy should be the one that counts.

**Trust angle:** the hook should keep running its own reviewed copy. If it ran whatever `warlock.py` the current branch contains, it would execute unreviewed repo code on every prompt. So the safer fix is for the checker to detect the mismatch and refuse.

**Fix in `warlock.py`:**

```python
def default_repo():
    cwd = pathlib.Path.cwd().resolve()
    for p in (cwd, *cwd.parents):
        if (p / STATE).is_file() and (p / BASE).is_file():
            return str(p)
    return str(pathlib.Path(__file__).resolve().parents[3])
```

Then:

```python
# line 195
    parser.add_argument('--repo', default=default_repo())
# line 210
    result = {'acceptanceBoundary': BOUNDARY, 'checker': digest(pathlib.Path(__file__).resolve())}
# insert after line 212 (root = ...)
        bundled = root / 'plugins/warlock-contributor/scripts/warlock.py'
        if bundled.is_file() and bundled.resolve() != pathlib.Path(__file__).resolve() and digest(bundled) != result['checker']:
            raise ValueError('Installed checker differs from repository checker; run plugins/warlock-contributor/scripts/warlock.py')
```

**Fix in `SKILL.md:8`:** replace the first sentence with:

> Find the repository root. Inside a Warlock checkout run the repository's `plugins/warlock-contributor/scripts/warlock.py`. An installed plugin may be a stale cached copy, and the checker refuses if it differs. Use this skill's `../../scripts/warlock.py` only when the repository lacks it.

The test fixture repos have no `plugins/` folder, so the existing tests are unaffected.

### 3. INTEGRATION ASSUMPTION: CI can't require the local record, and a fresh clone may not ignore it

**Where:** `warlock.py:223-224`, `contract.json:54`, `README.md:14`, and the root's `.gitignore`.

**Why CI can't use `--require-record`:**
- `contract.json:54` says "mandatory implementation continuations use" `--require-record`.
- The record is deliberately ignored by git, so it never exists in CI or in a fresh clone. If the CI or wrapper the root is adding uses `check --require-record`, every PR fails, including doc-only ones.
- CI's `--base-ref` check also needs the full git history. If the CI checkout is shallow, the `git diff` fails with exit 2.

**Why the ignore may be missing:**
- The README says "this repository supplies the ignore", but `.gitignore` shows as modified and uncommitted in the current status. That claim is only true once the root commits it.
- When the record isn't ignored, `git check-ignore` exits 1. `git()` turns that into the unhelpful "Git operation failed: " message, so the clearer refusal at line 224 never runs.

**Fix for lines 223-224:**

```python
            ignored = subprocess.run(['git', '-C', str(root), 'check-ignore', '-q', '--', args.record])
            if ignored.returncode == 1:
                raise ValueError('Record must be Git-ignored; add ".warlock-contributor/" to .git/info/exclude or choose an ignored --record')
            if ignored.returncode:
                raise ValueError('git check-ignore failed')
```

**Rule for the wrapper and CI** (an assumption about the code being written concurrently):

```sh
# CI (needs the full history, e.g. fetch-depth: 0): never --require-record
python3 -B plugins/warlock-contributor/qa/test_warlock.py
python3 -B plugins/warlock-contributor/scripts/warlock.py --json check --base-ref "$(git merge-base HEAD origin/main)"

# Local v2loop iteration: require the record only when product source is touched
if git status --porcelain -- implementation/warlock | grep -q .; then req=--require-record; else req=; fi
python3 -B plugins/warlock-contributor/scripts/warlock.py --json check $req
```

This keeps simple doc contributions free of slice, release and gate requirements.

## Smaller issues (not must-fix)

- **`--base-ref` is silently ignored when a record exists** (`warlock.py:238-245`). Either apply it in both branches or say so in `contract.json`.
- **The README doesn't mention the Claude marketplace that already exists.** Add `/plugin marketplace add .` followed by `/plugin install warlock-contributor@warlock`.
  - A project `.claude/settings.json` with `extraKnownMarketplaces` and `enabledPlugins` would prompt contributors on a fresh clone. That changes repo configuration, needs user approval, and the exact source schema should be checked with `claude plugin validate` before relying on it.
- **The marketplace description overstates the plugin** (`marketplace.json:4` says "Scaffold, implement and review"). Reuse the plugin's own description.
- **`"skills": "./skills/"` in `.claude-plugin/plugin.json:6` is the default path.** In Claude Code, custom paths add to the defaults, so this risks loading the skill twice. Remove it; keep it in the Codex manifest.
- **`reviews/` ships inside the plugin package.** It contains prompts, stream logs, stderr and `run_opus.py`, which would be copied into every user's plugin cache. Move it to `docs/warlock-workflow-review/`.
- **Trust limits, stated plainly:**
  - Anyone who can commit to the repo can change code that runs on every prompt for anyone who installed the plugin. Pinning the version and refusing on mismatch (finding 2) limits this.
  - The README says Codex requires re-trusting hooks after they change.
  - In Grok the hook delivers nothing.
  - These hooks are reminders. They're not how the rules are enforced.
- **The `${VAR:-$OTHER}` form assumes Claude Code passes `CLAUDE_PLUGIN_ROOT` to the shell as an environment variable,** rather than only replacing the literal token. Check that with `/hooks` and debug output before calling it confirmed. With the finding 1 fix, getting it wrong costs nothing.

## Minimal acceptable configuration

1. **What's actually required:** the repo's own `scripts/warlock.py`, `SKILL.md` and `contract.json`, called directly by `AGENTS.md`, `INSTRUCTIONS.md` and the v2loop wrapper. No client install is needed.
2. **Claude Code (optional):** the root marketplace plus `hooks/hooks.json` with `|| true`. SessionStart always adds the reminder; UserPromptSubmit adds it only when the check fails.
3. **Codex (optional):** `.codex-plugin/plugin.json` plus `hooks/codex.json` with `|| true`. Hooks need manual install and trust, and the skill is also readable straight from the repo.
4. **Grok:** the skill only. The hook does nothing.
5. **CI:** `qa/test_warlock.py` plus `check --base-ref <merge-base>` with full history, and never `--require-record`.
6. **Local loop:** `check --require-record` only when `implementation/warlock/` has changed.

Before the plugin is called usable, three things need to happen: the finding 1 and finding 2 fixes, the new tests, and the root committing the `.warlock-contributor/` ignore. None of this establishes GUI, native or accessibility (AT/IME) acceptance.

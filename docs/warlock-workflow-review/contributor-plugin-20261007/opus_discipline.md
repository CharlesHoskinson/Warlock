I've finished reading the files and am writing up the report.

# Warlock contributor plugin: audit of AAR lessons and contribution-policy semantics

I read 10 targeted files; nothing was executed. The findings are against the current `warlock.py`, compared with the AAR and v2 `INSTRUCTIONS.md`. I have not seen the root's v2loop wrapper, CI or CONTRIBUTING; they are listed as assumptions under §4.

## 1. Top 3 must-fix findings

### F1 — The live slice can't be worked: its own dirty files are frozen as "foreign"
**Scenario (happening now):** `STATE.activeSlice` = persistent-catalog-pins, with paths `src/Desktop.elm`, `src/Surface.elm` and `adapter/daemon.py`. All three are already modified in the working tree. `start` (`warlock.py:217`) saves them in `foreignDirty`. The contributor's first edit then triggers `Protected foreign-dirty path changed` (`:130-132`, exit 1), and `record` refuses (`:232`). The tests don't catch this because the fixture's slice files are clean.

**Second problem:** another agent's ongoing `docs/…build-loop-events` edits also fail this contributor's check. The contributor can't fix or attribute those changes.

**Fix (`:217`):**
```python
            now_dirty = dirty(root)
            adopted = sorted(n for n in now_dirty if n in s['paths'])
            record = {'schema': 1, 'owner': args.owner, 'slice': s, 'explicitSliceOverride': bool(args.slice_file), 'baseline': EXPECTED, 'startedUTC': now(), 'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip(), 'sourceHashes': {n: digest(safe(root,n)) for n in s['paths']}, 'foreignDirty': {n: h for n, h in now_dirty.items() if n not in s['paths']}, 'adoptedDirty': adopted, 'iterations': []}
            ...
            result.update(record=args.record, slice=s, warnings=['Slice path had uncommitted changes at start; you now own them: ' + n for n in adopted])
```
**Fix (`:130-132`):**
```python
    for name, old in record['foreignDirty'].items():
        if name in s['paths']:
            continue  # pre-fix records captured their own slice paths
        if digest(safe(root, name)) != old:
            (errors if name.startswith('implementation/') else warnings).append(
                'Foreign dirty path changed since start (not attributable; do not stage or revert it): ' + name)
```
Foreign changes under `implementation/` stay errors because archives are frozen and the candidate is WIP=1. Changes elsewhere become warnings.

### F2 — A partial verdict locks out the next fix (evidence freshness is treated as a policy violation)
**Scenario:** the contributor records `partial` on `restore-pending`, then fixes `Desktop.elm`. Every past claim is re-hashed on every call (`:156-163`), so `check` exits 1. `record` won't run (`:232`), so the fix that follows the verdict can't be recorded.

The only way out is a new `--record` file, which throws away the no-progress history. With the default path, the hook also reports "needs attention" on every prompt. This contradicts INSTRUCTIONS:24: "Source changes invalidate only relevant evidence."

The same lockout happens when `STATE.activeSlice` moves on (as it just did from launcher-search), because `start` refuses to touch an existing record (`:212-213`).

**Fix:** keep structural errors permanent. Make hash staleness of *historical* claims a warning, except changed evidence behind an `accepted` claim.
```python
def validate(root, record, reqs, state, strict_from=None):
    iterations = record.get('iterations', [])
    strict_from = len(iterations) if strict_from is None else strict_from
    ...
    for index, item in enumerate(iterations):
        for c in item.get('claims', []):
            fresh = errors if index >= strict_from else warnings
            ...
            for e in c['evidence']:
                if not isinstance(e.get('sha256'), str) or len(e['sha256']) != 64 or digest(safe(root, e['path'])) != e['sha256']:
                    (errors if c.get('disposition') == 'accepted' else fresh).append('Missing or changed evidence: ' + e['path'])
            for name, h in c['sourceHashes'].items():
                if not isinstance(h, str) or len(h) != 64 or name not in s['paths']:
                    errors.append('Irrelevant or malformed claim source: ' + name)
                elif digest(safe(root, name)) != h:
                    fresh.append('Stale verdict (source changed; re-adjudicate ' + c['scenario'] + '): ' + name)
```
- **`:248`:** `validate(root, record, reqs, state, strict_from=len(record['iterations']) - 1)`. Only the claim being appended is checked strictly.
- **`:196` / `:212`:** add `start.add_argument('--supersede', action='store_true')`. When the record exists and `--supersede` is set, rename it to `path.with_name(f"{path.stem}.{old['slice']['id']}.{old['startedUTC'].replace(':','')}.json")` instead of raising.
- **Tests:** invert `test_source_changed_after_claim_rejected` and `test_stale_source_evidence_and_exact_oracle` so they expect `ok` plus a stale warning. Add a test with a fix after a partial verdict.

### F3 — Labels alone can bypass the no-progress rule and the "accepted" checks
- **Fake progress (`:167`, `:246`):** `scenario-verdict` counts as progress whenever any claim is present. Re-recording the same `partial` claim with the same evidence every 40 minutes resets the 45-minute trigger forever. That repeats the AAR's root failure of republishing qualifications.
- **Contradictory "accepted" (`:142-148`):** an `accepted` claim with non-empty `missingObservations` passes. A reviewer named the same as the owner passes. Evidence can sit in Git-ignored `.warlock-contributor/`, which can't be published, or be the slice source file itself.
- **Silent "partial" claims:** `partial`, `implemented-unverified` and `blocked` claims pass with an empty `missingObservations`.

**Fix:**
```python
def claim_key(c):
    return (c['requirement'], c['scenario'], c['disposition'], tuple(sorted(e['sha256'] for e in c['evidence'])))
```
- **`:165-170`:**
```python
    previous, seen = record['sourceHashes'], set()
    for item in iterations:
        keys = {claim_key(c) for c in item.get('claims', []) if c.get('disposition') != 'unadjudicated'}
        expected_progress = (item['outcome'] == 'production-fix' and item['sourceHashes'] != previous) or (item['outcome'] == 'scenario-verdict' and bool(keys - seen))
        if item['meaningfulProgress'] != expected_progress:
            errors.append('Iteration progress assertion differs from source hashes/recorded verdict')
        previous, seen = item['sourceHashes'], seen | keys
```
- **`:246`:** compute the same thing. `seen` comes from the existing iterations, and progress is `bool({claim_key(c) for c in claims if c['disposition'] != 'unadjudicated'} - seen)`.
- **After `:141`:**
```python
            d = c.get('disposition')
            if d == 'accepted' and c.get('missingObservations'):
                errors.append('Accepted claim cannot list missing observations')
            if d in ('partial', 'implemented-unverified', 'blocked') and not c.get('missingObservations'):
                errors.append(d + ' claim must name its missing observations')
            for e in c.get('evidence', []):
                if e.get('path') in s['paths']:
                    errors.append('Source file is not evidence: ' + e['path'])
                elif d == 'accepted' and subprocess.run(['git', '-C', str(root), 'check-ignore', '-q', '--', e['path']]).returncode == 0:
                    errors.append('Accepted evidence is Git-ignored scratch: ' + e['path'])
```
- **In the accepted block:** `if isinstance(reviewer, dict) and reviewer.get('name') == record.get('owner'): errors.append('Accepted reviewer must differ from slice owner')`.

## 2. Smaller must-fixes
- **WIP=1 bypass (`:128`):** any `--slice-file` record skips the active-slice check permanently, so two agents can run two slices. INSTRUCTIONS:20 says parallel help addresses *this* slice only.
  ```python
      active = state['activeSlice']
      if record.get('explicitSliceOverride'):
          if not set(s['requirements']) <= set(active['requirements']):
              errors.append('Override must help the active slice (WIP=1); update STATE.activeSlice to change work')
      elif s['id'] != active['id']:
          errors.append('Live selected slice changed; run start --supersede')
  ```
  Change SKILL.md:10 to "`--slice-file` only for a narrower helper slice of the active requirements."
- **Doc contributions vs mandatory `--require-record` (`:221-228`):** if the loop wrapper always passes `--require-record`, every doc, plugin or CI edit is forced into a product slice with an invented product path (`normalize_slice` requires one). Add a conditional flag:
  ```python
      check.add_argument('--require-record-for-product', action='store_true')
      ...
          elif args.command == 'check' and not path.exists():
              changed = set(dirty(root))
              if args.base_ref:
                  changed.update(n for n in git(root, 'diff', '--name-only', '-z', args.base_ref, '--').decode().split('\0') if n)
              product = sorted(n for n in changed if n.startswith('implementation/warlock/') and not n.startswith('implementation/warlock/qa/evidence/'))
              if args.require_record or (args.require_record_for_product and product):
                  raise ValueError('Product source changed without a slice record; run start: ' + ', '.join(product[:5]))
              errors = ['Archival implementation change: ' + n for n in changed if n.startswith('implementation/') and not n.startswith('implementation/warlock/')]
  ```
  This also closes a gap: a plain `check` with no record and no `--base-ref` currently checks nothing about the working tree.
- **Administrative claims (ARC-014/REV-005):** keep them out of slice records. They belong in ledger rows with an external reviewer, reported separately (AAR:40, INSTRUCTIONS:39). Recording them in a slice would wrongly reset the product no-progress timer, so no new outcome type should be added.

## 3. Known limitations (document them, don't build infrastructure)
- **Records are self-attested:** they are local, Git-ignored and hand-editable. The checker catches inconsistency, not fraud. Acceptance authority stays in the ledger plus independent review.
- **No attribution in a shared checkout:** Git can't tell which of several agents dirtied a file. Separate `git worktree`s per agent would solve it; recommend them, don't require them. CI `--base-ref` on a branch is the clean ownership gate.
- **Byte-level progress:** any byte change, including whitespace, counts as a production-fix. Reports must lead with what the user can now see or do.
- **Wall-clock timer:** the 45-minute clock includes time spent waiting in the serialized native queue. It only produces a warning, which is acceptable.
- **Hashes aren't acceptance:** a matching hash proves custody, not that the oracle is true. Grok hooks deliver no context, and the 5-second hook timeout is advisory only.

## 4. Assumptions about the root's in-progress wrapper, CI and CONTRIBUTING
- **CI never has a slice record** (`.warlock-contributor/` is ignored). So CI must run `check --base-ref origin/main --require-record-for-product` only if CI also commits records. Otherwise it should run `check --base-ref origin/main` alone. CI with `--require-record` will always fail.
- **The wrapper should call** `check --require-record-for-product --json` on every iteration, and `record --outcome …` after any product edit. It should not call `--require-record` unconditionally.
- **The current dirty archival directories** (`elm-shared-observation-recovery-v121`, `elm-unsent-operation-disposition-v122`) will fail any `--base-ref` check. The root needs to decide what to do with them; contributors shouldn't revert them.

## 5. Minimum acceptable configuration
1. **Doc, plugin or CI change:** `check` (CI adds `--base-ref`). No slice, no record, no QA gate.
2. **Product change:** `status` → `start` (or `start --supersede` after a slice change) → implement → proportional checks through the protected launcher → `record --outcome production-fix|scenario-verdict|qualification` → `check --require-record-for-product` before reporting.
3. **Acceptance:** written only to ledger rows, by an independent reviewer, with tracked evidence and a source tuple. The plugin record never writes the ledger and never implies release acceptance.
4. **Hooks:** advisory reminders only. The explicit calls are what enforce the contract.
5. **Order of work:** F1 and F2 first, because they block the active slice today. Then F3, then the two smaller fixes. Each comes with the test inversions or additions noted above.

#!/usr/bin/env python3
"""Offline structural contributor checks. Never performs acceptance or executes QA."""
import argparse
import fcntl
import os
import tempfile
import datetime as dt
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

BASE = 'docs/elm-roadmap/requirements.json'
STATE = 'docs/warlock-build-loop/v2/STATE.json'
LEDGER = 'docs/warlock-build-loop/v2/requirement-ledger.json'
EXPECTED = 'a0c2093cc7769e05b70cc81aa3c001dbcbffe936cc17d1c494d7ab2fdc8b3b1b'
BOUNDARY = 'Structural compliance only; physical presentation, native input, AT/IME, scenario and release acceptance require external evidence and independent review.'


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe(root, name):
    p = pathlib.Path(name)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('Expected safe repository-relative path: ' + str(name))
    result = root / p
    cursor = root
    for part in p.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Symlink path is not allowed: ' + str(name))
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path escapes repository: ' + str(name))
    return result


def digest(path):
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError('Expected regular file: ' + str(path))
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text())


def git_run(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_TERMINAL_PROMPT='0')
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, env=env)


def git(root, *args):
    r = git_run(root, *args)
    if r.returncode:
        raise ValueError('Git operation failed: ' + r.stderr.decode(errors='replace').strip())
    return r.stdout


def fingerprint(root, name):
    p = pathlib.Path(name)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('Unsafe foreign path: ' + name)
    cursor = root
    for part in p.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return 'symlink:' + hashlib.sha256(os.fsencode(os.readlink(cursor))).hexdigest()
        if not cursor.exists():
            return None
    if cursor.is_dir():
        return 'directory'
    return digest(cursor)


def dirty_names(root):
    names = set(git(root, 'diff', '--no-renames', '--name-only', '-z').decode().split('\0'))
    names.update(git(root, 'diff', '--cached', '--no-renames', '--name-only', '-z').decode().split('\0'))
    names.update(git(root, 'ls-files', '--others', '--exclude-standard', '-z', '--', 'implementation/warlock', 'plugins/warlock-contributor', '.warlock-contributor').decode().split('\0'))
    return sorted(n for n in names if n)


def dirty(root):
    return {n: fingerprint(root, n) for n in dirty_names(root)}


def write_record(path, value, exclusive=False):
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name + '.')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        if exclusive:
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def discover_repo():
    for parent in (pathlib.Path.cwd(), *pathlib.Path.cwd().parents):
        if (parent / BASE).is_file() and (parent / STATE).is_file():
            return str(parent)
    return str(pathlib.Path(__file__).resolve().parents[3])


def context(root):
    data = read(safe(root, BASE))
    reqs = {r['id']: r for r in data['requirements']}
    if digest(safe(root, BASE)) != EXPECTED or len(reqs) != 242 or sum(len(r['scenarios']) for r in reqs.values()) != 417:
        raise ValueError('Frozen original 242/417 baseline changed')
    ledger = read(safe(root, LEDGER))
    if ledger['baseline']['sha256'] != EXPECTED:
        raise ValueError('Ledger baseline hash differs')
    entries = ledger.get('requirements', [])
    if len(entries) != 242 or {r['id'] for r in entries} != set(reqs):
        raise ValueError('Ledger requirement identities differ from original')
    count = 0
    for row in entries:
        scenarios = row.get('scenarios', [])
        original = {x['name']: x['then'] for x in reqs[row['id']]['scenarios']}
        if len(scenarios) != len(original) or {x['name']: x['oracle'] for x in scenarios} != original:
            raise ValueError('Ledger scenario identities/oracles differ: ' + row['id'])
        count += len(scenarios)
    if count != 417:
        raise ValueError('Ledger must preserve all 417 scenarios')
    return reqs, read(safe(root, STATE))


def normalize_slice(root, s, reqs):
    s = dict(s)
    for k in ('id', 'before', 'after'):
        if not isinstance(s.get(k), str) or not s[k].strip():
            raise ValueError('Slice needs ' + k)
    ids = s.get('requirements', [])
    if not 1 <= len(ids) <= 3 or len(set(ids)) != len(ids) or any(x not in reqs for x in ids):
        raise ValueError('Slice requires 1–3 exact original requirement IDs')
    names = s.get('scenarios', [])
    available = {x['name'] for i in ids for x in reqs[i]['scenarios']}
    if not names or len(set(names)) != len(names) or not set(names) <= available:
        raise ValueError('Slice needs exact original scenario names under selected requirements')
    if any(not any(x['name'] in names for x in reqs[i]['scenarios']) for i in ids):
        raise ValueError('Each requirement needs a selected original scenario')
    paths = s.get('paths', [])
    if not paths or len(set(paths)) != len(paths):
        raise ValueError('Slice needs unique product source paths')
    normalized = []
    for name in paths:
        name = name if name.startswith('implementation/warlock/') else 'implementation/warlock/' + name
        p = safe(root, name)
        if not name.startswith('implementation/warlock/') or name.endswith('/') or p.is_dir():
            raise ValueError('Product paths must be files in incremental implementation/warlock')
        normalized.append(name)
    if len(set(normalized)) != len(normalized):
        raise ValueError('Slice paths must be unique after normalization')
    s['paths'] = normalized
    if not isinstance(s.get('verification'), list) or not s['verification'] or any(not isinstance(x, str) or not x.strip() for x in s['verification']):
        raise ValueError('Slice needs proportional decisive verification')
    return s


def authored(name):
    prefix = 'implementation/warlock/'
    if not name.startswith(prefix):
        return False
    relative = name[len(prefix):]
    return relative.startswith(('src/', 'native/', 'adapter/', 'assets/')) and pathlib.Path(name).suffix in ('.elm', '.c', '.h', '.py', '.css', '.svg')


def product_delta(current, previous):
    return any(authored(n) and current[n] != previous.get(n) for n in current)


def verdict_key(claim):
    return json.dumps([claim.get('requirement'), claim.get('scenario'), claim.get('disposition'), claim.get('scope'), sorted(claim.get('missingObservations', []))], sort_keys=True)


def handoff(root, record, reqs, state):
    """Read-only resume packet. Current hashes never upgrade recorded observations."""
    errors, warnings = validate(root, record, reqs, state)
    s = normalize_slice(root, record['slice'], reqs)
    iterations = record.get('iterations', [])
    last = iterations[-1] if iterations else None
    previous = last['sourceHashes'] if last else record['sourceHashes']
    current = {n: digest(safe(root, n)) for n in s['paths']}
    latest = {}
    for iteration in iterations:
        for claim in iteration.get('claims', []):
            latest[(claim['requirement'], claim['scenario'])] = claim
    observations = []
    for requirement in s['requirements']:
        for scenario in reqs[requirement]['scenarios']:
            if scenario['name'] not in s['scenarios']:
                continue
            claim = latest.get((requirement, scenario['name']))
            observations.append({
                'requirement': requirement, 'scenario': scenario['name'],
                'oracle': scenario['then'], 'verificationScope': reqs[requirement]['verification'],
                'recordedDisposition': claim['disposition'] if claim else None,
                'evidenceMatchesCurrentSources': bool(claim) and not claim.get('historicalAfterSourceChange', False)
                    and claim['sourceHashes'] == current
                    and all(digest(safe(root, e['path'])) == e['sha256'] for e in claim['evidence']),
                'missingObservations': claim['missingObservations'] if claim else
                    ['No observation recorded in this participant record; inspect the original ledger and retained evidence.'],
                'evidence': claim['evidence'] if claim else []})
    return {
        'owner': record['owner'], 'slice': s,
        'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip(),
        'sourceHashes': current,
        'changedSinceLastRecord': [n for n in current if current[n] != previous.get(n)],
        'protectedForeignPaths': sorted(record['foreignDirty']),
        'lastIteration': {k: last[k] for k in ('atUTC', 'outcome', 'summary', 'meaningfulProgress')} if last else None,
        'observations': observations, 'errors': errors, 'warnings': warnings,
        'nextAction': 'Resolve structural errors before claims.' if errors else
            'Read the observations and implement the next source change, or record the decisive original-scenario observation. '
            'Follow any no-progress warning; do not rerun unchanged qualification by default.'}


def doctor(root, record_path):
    """Inspect local availability without running client binaries, builds or installs."""
    plugin = 'plugins/warlock-contributor/'
    required = ['scripts/warlock.py', 'scripts/session_hook.py',
                'skills/warlock-contribute/SKILL.md', '.claude-plugin/plugin.json',
                '.codex-plugin/plugin.json', 'hooks/hooks.json', 'hooks/codex.json']
    missing = [plugin + n for n in required if not safe(root, plugin + n).is_file()]
    ignored = git_run(root, 'check-ignore', '-q', '--', record_path).returncode == 0
    warnings = ['Client executable availability does not establish installation, enabled hooks or trust. '
                'Product toolchain and native runtime are checked by their protected runners.']
    if not ignored:
        warnings.append('Scratch record is not ignored; start will refuse to write it. Add a narrow ignore or select an ignored --record path.')
    return {
        'python': {'version': list(sys.version_info[:3]), 'minimum': '3.9'},
        'git': shutil.which('git'),
        'clientExecutables': {name: shutil.which(name) for name in ('claude', 'codex', 'grok')},
        'recordIgnored': ignored,
        'recordExists': safe(root, record_path).exists(),
        'missingPackageFiles': missing,
        'errors': ['Missing package file: ' + n for n in missing],
        'warnings': warnings}


def validate(root, record, reqs, state):
    errors, warnings = [], []
    if record.get('schema') != 1 or not record.get('owner'):
        raise ValueError('Invalid record schema/owner')
    s = normalize_slice(root, record['slice'], reqs)
    adoption = record.get('adoptedDirty', {'paths': [], 'ownershipNote': None})
    if not isinstance(adoption, dict) or not isinstance(adoption.get('paths'), list):
        raise ValueError('Invalid dirty adoption metadata')
    if adoption['paths'] and (not isinstance(adoption.get('ownershipNote'), str) or not adoption['ownershipNote'].strip()):
        errors.append('Dirty adoption lacks explicit ownership note')
    if any(n not in s['paths'] for n in adoption['paths']):
        errors.append('Dirty adoption exceeds declared product paths')
    if record.get('baseline') != EXPECTED:
        errors.append('Record baseline differs')
    if not record.get('explicitSliceOverride') and s['id'] != state['activeSlice']['id']:
        errors.append('Live selected slice changed; restart deliberately or explicitly select a slice')
    for name, old in record['foreignDirty'].items():
        if fingerprint(root, name) != old:
            errors.append('Protected foreign-dirty path changed: ' + name)
    for name in dirty_names(root):
        if name in record['foreignDirty'] or name in s['paths'] or name.startswith(('plugins/warlock-contributor/', '.warlock-contributor/', 'docs/', 'implementation/warlock/qa/evidence/')):
            continue
        if name.startswith('implementation/'):
            errors.append('Unowned or archival implementation change: ' + name)
    for item in record.get('iterations', []):
        for c in item.get('claims', []):
            if c.get('disposition') not in ('unadjudicated', 'missing', 'implemented-unverified', 'partial', 'failed', 'blocked', 'accepted'):
                errors.append('Unknown scenario disposition')
            if not isinstance(c.get('missingObservations'), list) or any(not isinstance(x, str) or not x.strip() for x in c['missingObservations']):
                errors.append('Missing observations must be an array of nonempty strings')
            if c.get('disposition') in ('partial', 'blocked') and not c.get('missingObservations'):
                errors.append('Partial/blocked verdict requires a missing observation')
            if c.get('disposition') == 'accepted':
                if c.get('missingObservations'):
                    errors.append('Accepted claim contradicts remaining missing observations')
                reviewer = c.get('reviewer')
                if not isinstance(reviewer, dict) or not reviewer.get('name') or reviewer.get('independent') is not True or not reviewer.get('disposition'):
                    errors.append('Accepted claim needs independent external reviewer identity/disposition')
                if isinstance(reviewer, dict) and str(reviewer.get('name', '')).strip().casefold() == str(record['owner']).strip().casefold():
                    errors.append('Accepted external reviewer must differ from contributor owner')
                for evidence in c.get('evidence', []):
                    evidence_path = evidence.get('path', '')
                    ignored = git_run(root, 'check-ignore', '--', evidence_path).returncode == 0
                    if evidence_path in s['paths'] or authored(evidence_path) or evidence_path.startswith('.warlock-contributor/') or ignored:
                        errors.append('Accepted evidence cannot be product source or ignored scratch')
                source_tuple = c.get('sourceTuple', {})
                if not isinstance(source_tuple, dict) or any(not source_tuple.get(k) for k in ('sourceRevision', 'core', 'plugin', 'toolchain')):
                    errors.append('Accepted claim needs reproducible source/core/plugin/toolchain tuple')
                elif git_run(root, 'cat-file', '-e', str(source_tuple['sourceRevision']) + '^{commit}').returncode:
                    errors.append('Accepted sourceRevision is not a commit in this repository')
            if c['requirement'] not in s['requirements'] or c['scenario'] not in s['scenarios']:
                errors.append('Claim outside selected slice')
                continue
            original = reqs[c['requirement']]
            scenarios = {x['name']: x for x in original['scenarios']}
            if c['scenario'] not in scenarios or c['oracle'] != scenarios[c['scenario']]['then'] or c['verificationScope'] != original['verification']:
                errors.append('Claim oracle/verification differs from original')
            for e in c['evidence']:
                if not isinstance(e.get('sha256'), str) or len(e['sha256']) != 64 or digest(safe(root, e['path'])) != e['sha256']:
                    errors.append('Missing or changed evidence: ' + e['path'])
            for name, h in c['sourceHashes'].items():
                if not isinstance(h, str) or len(h) != 64 or name not in s['paths'] or digest(safe(root, name)) != h:
                    if c.get('historicalAfterSourceChange') and isinstance(h, str) and len(h) == 64 and name in s['paths']:
                        warnings.append('Historical evidence source changed; current acceptance invalidated: ' + name)
                    else:
                        errors.append('Stale or irrelevant claim source: ' + name)
            if set(c['sourceHashes']) != set(s['paths']):
                errors.append('Claim must identify all selected relevant sources')
    iterations = record.get('iterations', [])
    previous = record['sourceHashes']
    seen_verdicts = set()
    for item in iterations:
        expected_progress = (item['outcome'] == 'production-fix' and product_delta(item['sourceHashes'], previous)) or (item['outcome'] == 'scenario-verdict' and any(verdict_key(c) not in seen_verdicts for c in item.get('claims', [])))
        if item['meaningfulProgress'] != expected_progress:
            errors.append('Iteration progress assertion differs from source hashes/recorded verdict')
        previous = item['sourceHashes']
        seen_verdicts.update(verdict_key(c) for c in item.get('claims', []))
    qualifying = 0
    for i in reversed(iterations):
        if i['meaningfulProgress']:
            break
        qualifying += 1
    since = record['startedUTC']
    for i in iterations:
        if i['meaningfulProgress']:
            since = i['atUTC']
    elapsed = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(since)).total_seconds()
    if qualifying >= 2 or elapsed >= 2700:
        warnings.append('Stop expanding this investigation; record missing observation and choose another bounded mandatory slice. Independent work remains allowed.')
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default=None)
    parser.add_argument('--record', default='.warlock-contributor/slice.json')
    parser.add_argument('--json', action='store_true')
    subs = parser.add_subparsers(dest='command', required=True)
    inspect = subs.add_parser('inspect')
    inspect.add_argument('--requirement', action='append', required=True)
    subs.add_parser('status'); check = subs.add_parser('check')
    subs.add_parser('doctor')
    subs.add_parser('handoff')
    plan = subs.add_parser('plan', help='Print a start-compatible slice scaffold; does not write or select work')
    plan.add_argument('--id', required=True)
    plan.add_argument('--requirement', action='append', required=True)
    plan.add_argument('--scenario', action='append', required=True)
    plan.add_argument('--path', action='append', required=True)
    plan.add_argument('--before', required=True)
    plan.add_argument('--after', required=True)
    plan.add_argument('--verify', action='append', required=True)
    check.add_argument('--project-only', action='store_true', help='Check project/baseline without reading a participant record')
    check.add_argument('--require-record', action='store_true', help='Fail if the participant slice record is absent')
    check.add_argument('--base-ref', help='Check changed implementation paths since this Git revision')
    start = subs.add_parser('start')
    start.add_argument('--owner', required=True); start.add_argument('--slice-file')
    start.add_argument('--adopt-dirty', action='append', default=[], metavar='PATH', help='Explicitly assert ownership of an already dirty declared product path')
    start.add_argument('--ownership-note', help='Explain authorization/ownership for adopting dirty product paths')
    rec = subs.add_parser('record')
    rec.add_argument('--outcome', choices=['qualification', 'production-fix', 'scenario-verdict'], required=True)
    rec.add_argument('--summary', required=True); rec.add_argument('--claim-file')
    args = parser.parse_args()
    result = {'acceptanceBoundary': BOUNDARY, 'checkerSha256': digest(pathlib.Path(__file__))}
    lock = None
    try:
        root = pathlib.Path(args.repo or discover_repo()).resolve()
        owned_checker = safe(root, 'plugins/warlock-contributor/scripts/warlock.py')
        if digest(owned_checker) != result['checkerSha256']:
            raise ValueError('Installed checker differs from repository-owned checker; use the reviewed repository copy')
        if args.command == 'check' and args.project_only and args.require_record:
            raise ValueError('--project-only is incompatible with --require-record')
        reqs, state = context(root)
        if args.command == 'check' and args.base_ref:
            args.base_ref = git(root, 'rev-parse', '--verify', '--end-of-options', args.base_ref + '^{commit}').decode().strip()
        path = safe(root, args.record)
        if args.command in ('start', 'record'):
            if git_run(root, 'check-ignore', '-q', '--', args.record).returncode != 0:
                raise ValueError('Record must be Git-ignored; add its directory to .gitignore or local .git/info/exclude')
            path.parent.mkdir(parents=True, exist_ok=True)
            lock_path = safe(root, args.record + '.lock')
            lock = os.fdopen(os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600), 'w')
            fcntl.flock(lock, fcntl.LOCK_EX)
        if args.command == 'doctor':
            result.update(doctor(root, args.record))
        elif args.command == 'plan':
            s = normalize_slice(root, {'id': args.id, 'requirements': args.requirement,
                'scenarios': args.scenario, 'paths': args.path, 'before': args.before,
                'after': args.after, 'verification': args.verify}, reqs)
            result.update(planSchema=1, slice=s, originals=[{
                'requirement': i, 'verification': reqs[i]['verification'],
                'scenarios': [x for x in reqs[i]['scenarios'] if x['name'] in s['scenarios']]
            } for i in s['requirements']])
        elif args.command == 'handoff':
            if not path.exists():
                raise ValueError('No participant record to resume; inspect status and start an owned slice first')
            result.update(handoff(root, read(path), reqs, state))
        elif args.command == 'inspect':
            if not 1 <= len(args.requirement) <= 3 or len(set(args.requirement)) != len(args.requirement) or any(i not in reqs for i in args.requirement):
                raise ValueError('Inspect needs 1–3 unique original requirement IDs')
            ledger = read(safe(root, LEDGER))
            rows = {r['id']: r for r in ledger['requirements']}
            result['requirements'] = [{'original': reqs[i], 'ledger': rows[i], 'pointers': {'original': BASE, 'ledger': LEDGER, 'contribution': reqs[i].get('source'), 'openSpec': [str(p.relative_to(root)) for p in (root / 'openspec' / 'changes').glob('*/specs/' + reqs[i]['capability'] + '/spec.md')] if (root / 'openspec' / 'changes').exists() else []}} for i in args.requirement]
        elif args.command == 'status':
            result.update(activeSlice=state['activeSlice'], baseline=EXPECTED, recordExists=path.exists(), releaseAccepted=False)
            if path.exists():
                errors, warnings = validate(root, read(path), reqs, state)
                result.update(errors=errors, warnings=warnings)
        elif args.command == 'start':
            if path.exists():
                raise ValueError('Record already exists; retain it and choose a new --record for a new slice')
            selection = read(safe(root, args.slice_file)) if args.slice_file else state['activeSlice']
            if selection.get('planSchema') == 1:
                selection = selection['slice']
            s = normalize_slice(root, selection, reqs)
            adopted = list(dict.fromkeys(args.adopt_dirty))
            if adopted and (not args.ownership_note or not args.ownership_note.strip()):
                raise ValueError('Dirty adoption requires an explicit --ownership-note')
            if any(n not in s['paths'] for n in adopted):
                raise ValueError('Dirty adoption is restricted to exact declared product paths')
            dirty_snapshot = dirty(root)
            if any(n not in dirty_snapshot for n in adopted):
                raise ValueError('Adopted path is not currently dirty')
            record = {'schema': 1, 'owner': args.owner, 'slice': s, 'explicitSliceOverride': bool(args.slice_file), 'baseline': EXPECTED, 'startedUTC': now(), 'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip(), 'sourceHashes': {n: digest(safe(root,n)) for n in s['paths']}, 'foreignDirty': {n: h for n, h in dirty_snapshot.items() if n not in adopted}, 'adoptedDirty': {'paths': adopted, 'ownershipNote': args.ownership_note}, 'iterations': []}
            path.parent.mkdir(parents=True, exist_ok=True)
            write_record(path, record, exclusive=True)
            result.update(record=args.record, slice=s)
        elif args.command == 'check' and (args.project_only or not path.exists()):
            if args.require_record:
                raise ValueError('Continuation requires a participant slice record; run start first')
            changed = {}
            if args.base_ref:
                changed.update({n: None for n in git(root, 'diff', '--no-renames', '--name-only', '-z', args.base_ref, '--').decode().split('\0') if n})
            errors = ['Archival implementation change: ' + n for n in changed if n.startswith('implementation/') and not n.startswith('implementation/warlock/')]
            result.update(errors=errors, warnings=['No participant slice record; baseline/project checks only. No contributor source ownership or evidence claim checked.'])
        else:
            record = read(path)
            if args.command == 'record':
                for iteration in record.get('iterations', []):
                    for claim in iteration.get('claims', []):
                        if any(digest(safe(root, n)) != h for n, h in claim.get('sourceHashes', {}).items()):
                            claim['historicalAfterSourceChange'] = True
            errors, warnings = validate(root, record, reqs, state)
            if args.command == 'record' and not errors:
                claims = read(safe(root, args.claim_file)) if args.claim_file else []
                if not isinstance(claims, list):
                    raise ValueError('Claim file must contain an array')
                for c in claims:
                    for key in ('requirement','scenario','oracle','verificationScope','scope','evidence','sourceHashes','reviewer','disposition','missingObservations'):
                        if key not in c:
                            raise ValueError('Claim missing ' + key)
                    if not isinstance(c['evidence'], list) or not isinstance(c['sourceHashes'], dict) or not isinstance(c['missingObservations'], list):
                        raise ValueError('Claim evidence/missingObservations must be arrays; sourceHashes must be an object')
                    if not c['evidence'] or not c['reviewer'] or not c['scope'] or not c['disposition']:
                        raise ValueError('Claims require evidence, scope, reviewer and disposition')
                hashes = {n: digest(safe(root,n)) for n in record['slice']['paths']}
                previous = record['iterations'][-1]['sourceHashes'] if record['iterations'] else record['sourceHashes']
                seen_verdicts = {verdict_key(c) for i in record['iterations'] for c in i.get('claims', [])}
                progress = (args.outcome == 'production-fix' and product_delta(hashes, previous)) or (args.outcome == 'scenario-verdict' and any(verdict_key(c) not in seen_verdicts for c in claims))
                record['iterations'].append({'atUTC': now(), 'outcome': args.outcome, 'summary': args.summary, 'sourceHashes': hashes, 'meaningfulProgress': progress, 'claims': claims, 'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip()})
                errors, warnings = validate(root, record, reqs, state)
                if not errors:
                    write_record(path, record)
            result.update(errors=errors, warnings=warnings, record=args.record)
        if args.command == 'check' and args.base_ref and path.exists() and not args.project_only:
            names = git(root, 'diff', '--no-renames', '--name-only', '-z', args.base_ref, '--').decode().split('\0')
            result.setdefault('errors', []).extend('Archival implementation change: ' + n for n in names if n.startswith('implementation/') and not n.startswith('implementation/warlock/'))
        result['ok'] = not result.get('errors')
        code = 0 if result['ok'] else 1
    except (ValueError, OSError, KeyError, TypeError, AttributeError, IndexError) as exc:
        result.update(ok=False, errors=[str(exc)])
        code = 2
    finally:
        if lock is not None:
            lock.close()
    print(json.dumps(result, indent=2) if args.json else '\n'.join([BOUNDARY, json.dumps(result, indent=2)]))
    return code


if __name__ == '__main__':
    sys.exit(main())

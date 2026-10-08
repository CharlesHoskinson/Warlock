#!/usr/bin/env python3
"""Offline contribution checks and explicit plugin regressions; no GUI acceptance/builds."""
import argparse
import fcntl
import os
import tempfile
import datetime as dt
import hashlib
import json
import pathlib
import shutil
import shlex
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
        safe(root, name)  # Reject absolute/escaping inputs before adding the product prefix.
        name = str(pathlib.Path(name))
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


def authored(name, include_cpp=True):
    prefix = 'implementation/warlock/'
    if not name.startswith(prefix):
        return False
    relative = name[len(prefix):]
    extensions = ('.elm', '.c', '.h', '.py', '.css', '.svg') + (('.cpp', '.hpp') if include_cpp else ())
    return relative.startswith(('src/', 'native/', 'adapter/', 'assets/')) and pathlib.Path(name).suffix in extensions


def product_delta(current, previous, include_cpp=True):
    return any(authored(n, include_cpp) and current[n] != previous.get(n) for n in current)


def extension_baseline(record, previous, position):
    """Include new dependencies without presenting their existing bytes as a fix."""
    previous = dict(previous)
    for extension in record.get('pathExtensions', []):
        if extension['afterIteration'] == position:
            previous.update(extension['sourceHashes'])
    return previous


def extend_paths(root, record, reqs, state, args):
    """Explicitly add dependencies to the same behavior, retaining its delivery history."""
    if not args.reason.strip():
        raise ValueError('Extension requires a concrete --reason')
    old = normalize_slice(root, record['slice'], reqs)
    requested = normalize_slice(root, dict(old, paths=args.path), reqs)['paths']
    if any(n in old['paths'] for n in requested):
        raise ValueError('Extension paths must be new to this slice')
    adopted = list(dict.fromkeys(args.adopt_dirty))
    if any(n not in requested for n in adopted):
        raise ValueError('Dirty adoption is restricted to exact new product paths')
    if adopted and (not args.ownership_note or not args.ownership_note.strip()):
        raise ValueError('Dirty adoption requires an explicit --ownership-note')
    snapshot = dirty(root)
    if any(n not in snapshot for n in adopted):
        raise ValueError('Adopted path is not currently dirty')
    if any(n in snapshot and n not in adopted for n in requested):
        raise ValueError('New dirty dependencies require explicit --adopt-dirty and ownership note')
    # Check foreign custody before any adoption; an overwritten draft cannot be repaired here.
    if any(fingerprint(root, n) != h for n, h in record['foreignDirty'].items()):
        raise ValueError('Protected foreign-dirty path changed; extension cannot override custody')
    hashes = {n: digest(safe(root, n)) for n in requested}
    event = {'atUTC': now(), 'afterIteration': len(record['iterations']),
             'reason': args.reason, 'sourceHashes': hashes,
             'adoptedDirty': {'paths': adopted, 'ownershipNote': args.ownership_note}}
    record['slice']['paths'] = old['paths'] + requested
    record.setdefault('pathExtensions', []).append(event)
    for n in adopted:
        record['foreignDirty'].pop(n, None)
    for iteration in record['iterations']:
        for claim in iteration.get('claims', []):
            claim['historicalAfterSliceExtension'] = True
    mark_historical(root, record)
    errors, warnings = validate(root, record, reqs, state)
    if errors:
        raise ValueError('Cannot extend slice: ' + '; '.join(errors))
    return {'extension': event, 'slice': record['slice'], 'warnings': warnings,
            'progress': progress_status(record)}


def verdict_key(claim):
    return json.dumps([claim.get('requirement'), claim.get('scenario'), claim.get('disposition'), claim.get('scope'), sorted(claim.get('missingObservations', []))], sort_keys=True)


def mark_historical(root, record):
    for iteration in record.get('iterations', []):
        for claim in iteration.get('claims', []):
            if any(digest(safe(root, n)) != h for n, h in claim.get('sourceHashes', {}).items()):
                claim['historicalAfterSourceChange'] = True


def scaffold_claim(root, record, reqs, state, args):
    """Print a self-attested observation packet; never write or grant acceptance."""
    mark_historical(root, record)  # Only the in-memory copy; same freshness rules as record.
    errors, warnings = validate(root, record, reqs, state)
    if errors:
        raise ValueError('Cannot scaffold claim: ' + '; '.join(errors))
    s = normalize_slice(root, record['slice'], reqs)
    if args.requirement not in s['requirements'] or args.scenario not in s['scenarios']:
        raise ValueError('Claim outside selected slice')
    original = reqs[args.requirement]
    scenario = next((x for x in original['scenarios'] if x['name'] == args.scenario), None)
    if scenario is None:
        raise ValueError('Scenario does not belong to selected original requirement')
    if not args.scope.strip() or any(not x.strip() for x in args.missing):
        raise ValueError('Evidence scope and missing observations must contain text')
    if args.disposition in ('partial', 'blocked') and not args.missing:
        raise ValueError('Partial/blocked observations require --missing')
    evidence = []
    for name in dict.fromkeys(args.evidence):
        h = digest(safe(root, name))
        if h is None:
            raise ValueError('Missing evidence file: ' + name)
        evidence.append({'path': name, 'sha256': h})
    hashes = {n: digest(safe(root, n)) for n in s['paths']}
    if any(h is None for h in hashes.values()):
        raise ValueError('Every selected source must exist before a claim is scaffolded')
    claim = {'requirement': args.requirement, 'scenario': args.scenario,
             'oracle': scenario['then'], 'verificationScope': original['verification'],
             'scope': args.scope, 'evidence': evidence, 'sourceHashes': hashes,
             'reviewer': record['owner'], 'disposition': args.disposition,
             'missingObservations': args.missing}
    return {'claimSchema': 1, 'claims': [claim],
            'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip(),
            'warnings': warnings + ['Contributor observation only. This scaffold neither reviews evidence contents '
                                    'nor updates the original ledger; accepted claims require external review.']}


def handoff(root, record, reqs, state):
    """Read-only resume packet. Current hashes never upgrade recorded observations."""
    errors, warnings = validate(root, record, reqs, state)
    s = normalize_slice(root, record['slice'], reqs)
    iterations = record.get('iterations', [])
    last = iterations[-1] if iterations else None
    previous = extension_baseline(record, last['sourceHashes'] if last else record['sourceHashes'], len(iterations))
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
                'scope': claim['scope'] if claim else None,
                'evidenceMatchesCurrentSources': bool(claim) and not claim.get('historicalAfterSourceChange', False)
                    and not claim.get('historicalAfterSliceExtension', False)
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
        'pathExtensions': record.get('pathExtensions', []),
        'lastIteration': {k: last[k] for k in ('atUTC', 'outcome', 'summary', 'meaningfulProgress')} if last else None,
        'observations': observations, 'errors': errors, 'warnings': warnings,
        'progress': progress_status(record),
        'nextAction': 'Resolve structural errors before claims.' if errors else
            'Read the observations and implement the next source change, or record the decisive original-scenario observation. '
            'Follow any no-progress warning; do not rerun unchanged qualification by default.'}


def progress_status(record, clock=None):
    """Recorded progress is a self-attestation, never an observed feature count."""
    iterations = record.get('iterations', [])
    qualifying = 0
    for item in reversed(iterations):
        if item['meaningfulProgress']:
            break
        qualifying += 1
    since = record['startedUTC']
    for item in iterations:
        if item['meaningfulProgress']:
            since = item['atUTC']
    clock = clock or dt.datetime.now(dt.timezone.utc)
    elapsed = max(0, (clock - dt.datetime.fromisoformat(since)).total_seconds())
    reasons = []
    if qualifying >= 2:
        reasons.append('two-iterations-without-progress')
    if elapsed >= 2700:
        reasons.append('45-minutes-without-recorded-progress')
    return {'iterationsWithoutProgress': qualifying, 'lastRecordedProgressUTC': since,
            'secondsSinceRecordedProgress': int(elapsed),
            'limits': {'iterations': 2, 'seconds': 2700},
            'investigationNeedsChange': bool(reasons), 'reasons': reasons,
            'action': 'Record the missing observation and select another bounded mandatory slice; '
                      'do not block independent work or bypass safety.' if reasons else
                      'Continue the selected behavior with proportional verification.',
            'basis': 'Participant record; unrecorded work and oracle truth are not inferred.'}


def verification_plan(root, record, reqs, state, selected=False):
    """Suggest existing protected runners. Never run or certify their contents."""
    packet = handoff(root, record, reqs, state)
    paths = packet['slice']['paths'] if selected else packet['changedSinceLastRecord']
    product = [n for n in paths if authored(n)]
    requirements = set(packet['slice']['requirements'])
    scenarios = set(packet['slice']['scenarios'])
    primary = bool(scenarios & {'taskbar-inactive', 'taskbar-active', 'taskbar-minimized'})
    cpu, mapped = [], set()

    def add(name, arguments, sources, reason):
        runner = 'implementation/warlock/qa/' + name
        key = (runner, tuple(arguments))
        for target in cpu:
            if (target['runner'], tuple(target['arguments'])) == key:
                target['triggerPaths'] = sorted(set(target['triggerPaths']) | set(sources))
                return
        exists = safe(root, runner).is_file()
        launcher = pathlib.Path('/home/hoskinson/window-integration-qa/qa_run.py')
        argv = ['/usr/bin/python3', '-B', str(launcher), '--', '/usr/bin/python3',
                '-B', str(safe(root, runner)), *arguments] if exists else None
        cpu.append({'runner': runner, 'runnerSha256': digest(safe(root, runner)),
                    'arguments': arguments, 'triggerPaths': sorted(sources), 'reason': reason,
                    'runnerAvailable': exists, 'protectedLauncherAvailable': launcher.is_file(),
                    'argv': argv, 'command': 'PYTHONDONTWRITEBYTECODE=1 ' + shlex.join(argv) if argv else None})

    for name in product:
        relative = name.removeprefix('implementation/warlock/')
        if relative.startswith('native/core/'):
            if relative == 'native/core/SeatManager.cpp':
                add('check-focus-core.py', [], [name], 'Compile the changed owning core unit and relink the exact archive.')
                add('check-native-authority.py', [], [name], 'After the core build, rebuild authority against the same owning headers/provider.')
            else:
                continue
        elif relative in ('native/host.c', 'native/shared-host.c', 'native/surface.h'):
            add('check-search.py', ['--native-popup'], [name], 'Changed host compile, relink and popup lifecycle self-tests.')
        elif relative.startswith('native/'):
            add('check-native-authority.py', [], [name], 'Compile changed authority units against the owning core tuple.')
        elif relative in ('adapter/taskbar_preferences.py', 'adapter/taskbar_projection.py'):
            add('check-pin-storage.py', [], [name], 'Pin persistence/component behavior; inspect scope for non-pin projection changes.')
        elif relative in ('src/Catalog.elm', 'src/Launch.elm', 'adapter/catalog_authority.py'):
            add('check-search.py', [], [name], 'Compile search views and catalog/launch replays.')
        elif relative in ('src/TaskView.elm', 'src/Taskbar.elm', 'src/TaskbarShell.elm',
                          'src/Surface.elm', 'src/Desktop.elm', 'src/Main.elm',
                          'src/SurfaceRenderer.elm', 'src/Bar.elm', 'src/ActionProjection.elm'):
            if requirements & {'ELM-UI-007'}:
                add('check-feedback.py', [], [name], 'Changed feedback views and state projection.')
            else:
                flags = ['--taskbar-primary'] if primary else \
                        ['--workspace-navigation'] if requirements & {'ELM-UI-002', 'ELM-UX-008'} else \
                        ['--task-view'] if requirements & {'ELM-UI-006', 'ELM-UX-017'} else \
                        ['--pins'] if requirements & {'ELM-UX-004'} else []
                add('check-search.py', flags, [name], 'Compile the affected shell/view route; review the selected runner mode.')
        elif relative in ('src/Effects.elm', 'src/NativeOutcome.elm', 'adapter/effect_endpoint.py'):
            add('check-feedback.py', [], [name], 'Outcome/state projection; select additional replay/model cases for changed invariants.')
        else:
            continue
        mapped.add(name)

    modes = []
    if product:
        if requirements & {'ELM-UI-006', 'ELM-UX-017'}:
            modes += [['--task-view'], ['--task-view-retired-opener']]
        if requirements & {'ELM-UI-002', 'ELM-UX-008'}:
            modes += [['--workspace-navigation']]
        if requirements & {'ELM-UI-005', 'ELM-UX-029'}:
            modes += [['--launcher-search']]
        if requirements & {'ELM-UX-004'}:
            modes += [['--taskbar-pins']]
        if primary:
            modes += [['--taskbar-primary']]
        if 'taskbar-group' in scenarios or requirements & {'ELM-UX-005', 'ELM-UX-024'}:
            modes += [['--taskbar-focus']]
        if requirements & {'ELM-UI-007'}:
            modes += [[]]
    native = []
    runner = 'implementation/warlock/qa/native-window-feedback.py'
    for arguments in modes:
        exists = safe(root, runner).is_file()
        argv = ['python3', '-B', 'docs/warlock-build-loop/v2/loop.py', '--record',
                record.get('_recordPath', '.warlock-contributor/slice.json'),
                'native', '--runner', str(safe(root, runner)), '--', *arguments] if exists else None
        native.append({'runner': runner, 'runnerSha256': digest(safe(root, runner)),
                       'arguments': arguments, 'runnerAvailable': exists,
                       'argv': argv, 'command': shlex.join(argv) if argv else None})
    packet.update(verificationPlanSchema=1, executionPerformed=False, acceptanceInferred=False,
                  mode='selected-paths' if selected else 'changes-since-last-record',
                  consideredPaths=paths, cpuTargets=cpu, nativeCandidates=native,
                  unmappedProductPaths=sorted(set(product) - mapped),
                  supportPaths=[n for n in paths if n not in product],
                  instructions=[
                      'Suggestions only: inspect runners, prerequisites and source tuple before execution; run nothing automatically.',
                      'Choose the smallest decisive behavior plus a meaningful negative/lifecycle case. Native candidates run serially.',
                      'Add Quint/fuzz only for changed reducer, concurrency or authority invariants; this map is not complete coverage.',
                      'Unmapped product/support changes need an explicit proportional check chosen by the contributor.',
                      'Original verification and missing observations below still apply; suggested runner passes do not accept scenarios.',
                      'No changed sources means no default rerun. Use --selected to plan before edits, not to infer new evidence.'])
    return packet


def doctor(root, record_path):
    """Inspect local availability without running client binaries, builds or installs."""
    plugin = 'plugins/warlock-contributor/'
    required = ['scripts/warlock.py', 'scripts/session_hook.py',
                'skills/warlock-contribute/SKILL.md', '.claude-plugin/plugin.json',
                '.codex-plugin/plugin.json', 'hooks/hooks.json', 'hooks/codex.json']
    missing = [plugin + n for n in required if not safe(root, plugin + n).is_file()]
    errors = ['Missing package file: ' + n for n in missing]
    manifests = {}
    for name in ('.claude-plugin/plugin.json', '.codex-plugin/plugin.json'):
        path = safe(root, plugin + name)
        if not path.is_file():
            continue
        try:
            manifest = read(path)
            if not isinstance(manifest, dict) or manifest.get('name') != 'warlock-contributor':
                raise ValueError('Expected warlock-contributor manifest object')
            version = manifest.get('version')
            if not isinstance(version, str) or not version.strip():
                raise ValueError('Missing package version')
            manifests[name] = version
            if name.startswith('.codex-plugin/'):
                for field, directory in (('skills', True), ('hooks', False)):
                    target = manifest.get(field)
                    if not isinstance(target, str) or not target.startswith('./'):
                        raise ValueError(field + ' must be an explicit plugin-relative path')
                    destination = safe(root, plugin + target)
                    if not (destination.is_dir() if directory else destination.is_file()):
                        raise ValueError('Missing ' + field + ' target: ' + target)
        except (ValueError, OSError, TypeError) as exc:
            errors.append('Invalid package metadata ' + name + ': ' + str(exc))
    if len(set(manifests.values())) > 1:
        errors.append('Claude and Codex package versions differ')
    for name in ('hooks/hooks.json', 'hooks/codex.json'):
        path = safe(root, plugin + name)
        if not path.is_file():
            continue
        try:
            data = read(path)
            hooks = data.get('hooks') if isinstance(data, dict) else None
            if not isinstance(hooks, dict):
                raise ValueError('Expected hooks object')
            for event in ('SessionStart', 'UserPromptSubmit'):
                entries = hooks.get(event)
                if not isinstance(entries, list) or not entries:
                    raise ValueError('Missing hook entries for ' + event)
                for entry in entries:
                    commands = entry.get('hooks') if isinstance(entry, dict) else None
                    if not isinstance(commands, list) or not commands:
                        raise ValueError('Missing commands for ' + event)
                    for command in commands:
                        if not isinstance(command, dict) or command.get('type') != 'command' \
                                or not isinstance(command.get('command'), str) or not command['command'].strip():
                            raise ValueError('Expected nonempty command hook for ' + event)
                        timeout = command.get('timeout')
                        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 60:
                            raise ValueError('Expected bounded positive hook timeout for ' + event)
        except (ValueError, OSError, TypeError) as exc:
            errors.append('Invalid package metadata ' + name + ': ' + str(exc))
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
        'manifestVersions': manifests,
        'metadataValidation': 'Local manifest identity, version agreement, referenced paths and reminder-hook shape only; no client loading or trust inferred.',
        'errors': errors,
        'warnings': warnings}


def self_test(root):
    """Explicit plugin-only regression run; no product build or native campaign."""
    qa = safe(root, 'plugins/warlock-contributor/qa')
    tests = sorted(qa.glob('test_*.py'))
    if not tests:
        raise ValueError('Plugin regression tests are missing; use a complete repository checkout')
    for test in tests:
        if not safe(root, str(test.relative_to(root))).is_file():
            raise ValueError('Expected regular plugin test file: ' + test.name)
    argv = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(qa),
            '-t', str(qa), '-p', 'test_*.py']
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(('GIT_', 'GROK_', 'CLAUDE_', 'PLUGIN_'))
           and key not in ('PYTHONPATH', 'PYTHONHOME')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    try:
        result = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                                text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {'selfTestSchema': 1, 'executionPerformed': True, 'acceptanceInferred': False,
                'argv': argv, 'errors': ['Plugin regression suite exceeded its 300-second limit']}
    errors = ['Plugin regression suite failed'] if result.returncode else []
    if '\nRan 0 tests in ' in result.stderr:
        errors = ['Plugin regression suite discovered zero tests']
    return {'selfTestSchema': 1, 'executionPerformed': True, 'acceptanceInferred': False,
            'scope': 'Plugin contribution-policy regressions; no GUI build, native/AT oracle or client installation.',
            'argv': argv, 'returnCode': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr,
            'errors': errors}


def contribution_report(root, record, reqs, state):
    """Prepare a delivery note from recorded observations, without inventing results."""
    packet = handoff(root, record, reqs, state)
    current = packet['sourceHashes']
    selected_dirty = set(dirty_names(root)) & set(current)
    initial = dict(record['sourceHashes'])
    for extension in record.get('pathExtensions', []):
        initial.update(extension['sourceHashes'])
    packet.update(
        reportSchema=1, releaseAccepted=False,
        intendedBehavior=record['slice']['after'],
        observedResult=packet['lastIteration']['summary'] if packet['lastIteration'] else None,
        selectedChanges=[{'path': name, 'initialSha256': initial.get(name),
                         'currentSha256': sha, 'uncommitted': name in selected_dirty}
                        for name, sha in current.items()
                        if sha != initial.get(name) or name in selected_dirty],
        reportBoundary='Contributor self-attestation for review. Intended behavior is not an observation; '
                       'matching hashes do not establish oracle truth, independent review or release acceptance.')
    return packet


def report_markdown(packet):
    # Keep contributor text literal: no HTML, links or injected Markdown headings.
    def literal(value):
        text = ' '.join(str(value).splitlines())
        for character in ('\\', '`', '*', '_', '[', ']', '<', '>', '#', '|'):
            text = text.replace(character, '\\' + character)
        return text

    lines = ['Warlock contribution: ' + literal(packet['slice']['id']), '',
             'Owner: ' + literal(packet['owner']),
             'Source HEAD: ' + literal(packet['sourceRevision']) + ' (see uncommitted paths below).', '',
             'Before: ' + literal(packet['slice']['before']),
             'Intended result: ' + literal(packet['intendedBehavior']),
             'Recorded observation: ' + literal(packet['observedResult'] or 'No iteration recorded.'), '',
             'Recorded progress: ' + str(packet['progress']['iterationsWithoutProgress']) +
             ' consecutive iterations without progress; ' + str(packet['progress']['secondsSinceRecordedProgress']) +
             ' seconds since the recorded progress baseline.',
             'Investigation action: ' + literal(packet['progress']['action']), '',
             packet['reportBoundary'], '', 'Selected source changes:', '']
    for change in packet['selectedChanges']:
        lines.append('- ' + literal(change['path']) +
                     (' — uncommitted' if change['uncommitted'] else ' — committed') +
                     '; current SHA-256: ' + literal(change['currentSha256'] or 'deleted'))
    if not packet['selectedChanges']:
        lines.append('No selected source changes since this record began.')
    lines.extend(['', 'Original scenario observations:', ''])
    for observation in packet['observations']:
        lines.extend(['- ' + literal(observation['requirement']) + ' / ' + literal(observation['scenario']) +
                      ': recorded disposition ' + literal(observation['recordedDisposition'] or 'none') + '.',
                      '  Original oracle: ' + literal(observation['oracle']),
                      '  Verification obligations: ' + literal(observation['verificationScope']),
                      '  Source/evidence hashes: ' + ('current' if observation['evidenceMatchesCurrentSources']
                                                    else 'not current or no observation') + '.'])
        if observation.get('scope'):
            lines.append('  Recorded evidence scope: ' + literal(observation['scope']))
        for evidence in observation['evidence']:
            lines.append('  Evidence: ' + literal(evidence['path']) + '; SHA-256: ' + literal(evidence['sha256']))
        for missing in observation['missingObservations']:
            lines.append('  Remaining observation: ' + literal(missing))
    lines.extend(['', 'Planned verification (execution is not inferred):', ''])
    lines.extend('- ' + literal(item) for item in packet['slice']['verification'])
    if packet['errors'] or packet['warnings']:
        lines.extend(['', 'Structural findings:', ''])
        lines.extend('- Error: ' + literal(item) for item in packet['errors'])
        lines.extend('- Advisory: ' + literal(item) for item in packet['warnings'])
    lines.extend(['', 'Full release acceptance is not established by this report.', ''])
    return '\n'.join(lines)


def remaining(root, reqs, requirements, statuses, summary_only):
    """Report recorded backlog, without inferring implementation or acceptance."""
    if len(set(requirements)) != len(requirements) or any(i not in reqs for i in requirements):
        raise ValueError('Remaining needs unique original requirement IDs')
    ledger = read(safe(root, LEDGER))
    counts, rows = {}, []
    requirement_count = 0
    for requirement in ledger['requirements']:
        identity = requirement['id']
        if requirements and identity not in requirements:
            continue
        requirement_count += 1
        original = reqs[identity]
        scenarios = {s['name']: s for s in original['scenarios']}
        for scenario in requirement['scenarios']:
            status = scenario['status']
            counts[status] = counts.get(status, 0) + 1
            if status not in statuses:
                continue
            rows.append({'requirement': identity, 'capability': original['capability'],
                         'original': scenarios[scenario['name']],
                         'verificationScope': original['verification'], 'ledger': scenario})
    return {'ledgerSha256': digest(safe(root, LEDGER)), 'recordedOnly': True,
            'requirementsConsidered': requirement_count, 'scenarioCountsByRecordedStatus': counts,
            'matchingScenarios': len(rows), 'scenarios': [] if summary_only else rows,
            'summaryOnly': summary_only, 'releaseAccepted': False,
            'warnings': ['Recorded dispositions are not revalidated here. Unadjudicated does not mean unimplemented; '
                         'accepted rows still require current evidence and independent review. '
                         'The frozen 242/417 baseline is only part of the full release scope.']}


def review(root, record, reqs, state, includes):
    """Read-only staging review; explicit support paths do not override foreign ownership."""
    packet = handoff(root, record, reqs, state)
    allowed = set(record['slice']['paths'])
    for name in includes:
        path = safe(root, name)
        if path.is_dir() or name.startswith(('.git/', '.warlock-contributor/')):
            raise ValueError('Review includes must be publishable repository files: ' + name)
        if name.startswith('implementation/') and not name.startswith('implementation/warlock/'):
            raise ValueError('Review cannot include archival implementation: ' + name)
        allowed.add(name)
    for iteration in record['iterations']:
        for claim in iteration.get('claims', []):
            allowed.update(e['path'] for e in claim['evidence'])
    staged = []
    for name in git(root, 'diff', '--cached', '--no-renames', '--name-only', '-z', '--').decode().split('\0'):
        if not name:
            continue
        if name in record['foreignDirty']:
            packet['errors'].append('Staged protected foreign path: ' + name)
        elif name not in allowed:
            packet['errors'].append('Staged path needs explicit contribution scope (--include for owned support files): ' + name)
        path = safe(root, name)
        entries = git(root, 'ls-files', '--stage', '-z', '--', ':(literal)' + name).split(b'\0')
        index_hash = None
        for entry in entries:
            if not entry:
                continue
            metadata, _ = entry.split(b'\t', 1)
            mode, blob, stage = metadata.decode().split()
            if stage != '0' or mode not in ('100644', '100755'):
                raise ValueError('Staged path must be a resolved regular file: ' + name)
            index_hash = hashlib.sha256(git(root, 'cat-file', 'blob', blob)).hexdigest()
        current_hash = digest(path)
        matches = index_hash == current_hash
        if not matches:
            packet['errors'].append('Staged bytes differ from current source/evidence: ' + name)
        staged.append({'path': name, 'stagedSha256': index_hash, 'workingSha256': current_hash,
                       'matchesWorkingTree': matches})
    if not staged:
        packet['warnings'].append('Nothing is staged; this review has no commit contents to check.')
    packet.update(staged=staged, explicitSupportPaths=includes,
                  reviewBoundary='Read-only scope and byte comparison. Does not stage, commit, push, run QA or certify observations.')
    return packet


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
    extensions = record.get('pathExtensions', [])
    known_paths = set(record['sourceHashes'])
    last_position = 0
    for extension in extensions:
        position = extension.get('afterIteration')
        if type(position) is not int or not last_position <= position <= len(record.get('iterations', [])):
            raise ValueError('Invalid extension iteration position')
        last_position = position
        hashes = extension.get('sourceHashes')
        if not isinstance(hashes, dict) or not hashes or known_paths.intersection(hashes):
            raise ValueError('Extension must identify unique new source paths')
        if any(n not in s['paths'] or (h is not None and (not isinstance(h, str) or len(h) != 64)) for n, h in hashes.items()):
            raise ValueError('Invalid extension source baseline')
        if not isinstance(extension.get('reason'), str) or not extension['reason'].strip():
            raise ValueError('Extension needs its reason')
        dt.datetime.fromisoformat(extension['atUTC'])
        adoption = extension.get('adoptedDirty', {})
        if not isinstance(adoption.get('paths'), list) or any(n not in hashes for n in adoption['paths']):
            raise ValueError('Invalid extension dirty adoption')
        if adoption['paths'] and (not isinstance(adoption.get('ownershipNote'), str) or not adoption['ownershipNote'].strip()):
            raise ValueError('Extension dirty adoption needs ownership note')
        known_paths.update(hashes)
    if extensions and known_paths != set(s['paths']):
        errors.append('Extension history does not cover declared source paths')
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
    for index, item in enumerate(record.get('iterations', [])):
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
            later_paths = {n for e in extensions if e['afterIteration'] > index for n in e['sourceHashes']}
            historical_scope = bool(later_paths) and c.get('historicalAfterSliceExtension') is True
            expected_sources = set(s['paths']) - later_paths if historical_scope else set(s['paths'])
            if set(c['sourceHashes']) != expected_sources:
                errors.append('Claim must identify all selected relevant sources')
            if historical_scope:
                warnings.append('Historical evidence predates added dependencies; current acceptance invalidated.')
            elif c.get('historicalAfterSliceExtension'):
                errors.append('Claim extension marker lacks a later source extension')
    iterations = record.get('iterations', [])
    previous = record['sourceHashes']
    seen_verdicts = set()
    for index, item in enumerate(iterations):
        previous = extension_baseline(record, previous, index)
        if item.get('progressPolicy', 1) not in (1, 2):
            errors.append('Unknown iteration progress policy')
        expected_progress = (item['outcome'] == 'production-fix' and product_delta(item['sourceHashes'], previous, item.get('progressPolicy', 1) == 2)) or (item['outcome'] == 'scenario-verdict' and any(verdict_key(c) not in seen_verdicts for c in item.get('claims', [])))
        if item['meaningfulProgress'] != expected_progress:
            errors.append('Iteration progress assertion differs from source hashes/recorded verdict')
        previous = item['sourceHashes']
        seen_verdicts.update(verdict_key(c) for c in item.get('claims', []))
    if progress_status(record)['investigationNeedsChange']:
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
    subs.add_parser('self-test', help='Run plugin regression tests in isolated fixtures; no GUI campaigns')
    subs.add_parser('handoff')
    extension = subs.add_parser('extend', help='Add dependencies to the same owned slice without resetting its history or timer')
    extension.add_argument('--path', action='append', required=True)
    extension.add_argument('--reason', required=True)
    extension.add_argument('--adopt-dirty', action='append', default=[], metavar='PATH')
    extension.add_argument('--ownership-note')
    verification = subs.add_parser('verify-plan', help='Read-only suggestions for proportional protected checks; never executes QA')
    verification.add_argument('--selected', action='store_true', help='Plan declared paths before edits; default considers only changes since last record')
    report = subs.add_parser('report', help='Read-only delivery note from the participant record; no acceptance inferred')
    report.add_argument('--markdown', action='store_true', help='Print a reviewable Markdown note instead of the JSON packet')
    backlog = subs.add_parser('remaining', help='Read-only original scenario checklist from recorded ledger dispositions')
    backlog.add_argument('--requirement', action='append', default=[])
    backlog.add_argument('--status', action='append', choices=['unadjudicated', 'missing', 'implemented-unverified', 'partial', 'failed', 'blocked', 'accepted'])
    backlog.add_argument('--summary', action='store_true', help='Counts only; omit scenario details')
    staging = subs.add_parser('review', help='Read-only participant handoff and staged contribution review')
    staging.add_argument('--include', action='append', default=[], help='Explicitly owned supporting file; cannot override protected foreign paths')
    claim = subs.add_parser('claim', help='Print a record-compatible observation scaffold; does not write or accept')
    claim.add_argument('--requirement', required=True)
    claim.add_argument('--scenario', required=True)
    claim.add_argument('--evidence', action='append', required=True)
    claim.add_argument('--scope', required=True)
    claim.add_argument('--disposition', required=True,
                       choices=['unadjudicated', 'missing', 'implemented-unverified', 'partial', 'failed', 'blocked'])
    claim.add_argument('--missing', action='append', default=[])
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
        if args.command == 'report' and args.markdown and args.json:
            raise ValueError('--markdown is incompatible with --json')
        reqs, state = context(root)
        if args.command == 'check' and args.base_ref:
            args.base_ref = git(root, 'rev-parse', '--verify', '--end-of-options', args.base_ref + '^{commit}').decode().strip()
        path = safe(root, args.record)
        if args.command in ('start', 'record', 'extend'):
            if git_run(root, 'check-ignore', '-q', '--', args.record).returncode != 0:
                raise ValueError('Record must be Git-ignored; add its directory to .gitignore or local .git/info/exclude')
            path.parent.mkdir(parents=True, exist_ok=True)
            lock_path = safe(root, args.record + '.lock')
            lock = os.fdopen(os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600), 'w')
            fcntl.flock(lock, fcntl.LOCK_EX)
        if args.command == 'doctor':
            result.update(doctor(root, args.record))
        elif args.command == 'self-test':
            result.update(self_test(root))
        elif args.command == 'remaining':
            result.update(remaining(root, reqs, args.requirement,
                args.status or ['unadjudicated', 'missing', 'implemented-unverified', 'partial', 'failed', 'blocked'], args.summary))
        elif args.command == 'plan':
            s = normalize_slice(root, {'id': args.id, 'requirements': args.requirement,
                'scenarios': args.scenario, 'paths': args.path, 'before': args.before,
                'after': args.after, 'verification': args.verify}, reqs)
            result.update(planSchema=1, slice=s, originals=[{
                'requirement': i, 'verification': reqs[i]['verification'],
                'scenarios': [x for x in reqs[i]['scenarios'] if x['name'] in s['scenarios']]
            } for i in s['requirements']])
        elif args.command in ('handoff', 'claim', 'review', 'report', 'verify-plan', 'extend'):
            if not path.exists():
                raise ValueError('No participant record to resume; inspect status and start an owned slice first')
            if args.command == 'extend':
                record = read(path)
                result.update(extend_paths(root, record, reqs, state, args))
                write_record(path, record)
                result['record'] = args.record
            elif args.command == 'verify-plan':
                record = read(path)
                record['_recordPath'] = args.record
                result.update(verification_plan(root, record, reqs, state, args.selected))
            elif args.command == 'claim':
                result.update(scaffold_claim(root, read(path), reqs, state, args))
            elif args.command == 'review':
                result.update(review(root, read(path), reqs, state, args.include))
            elif args.command == 'report':
                result.update(contribution_report(root, read(path), reqs, state))
            else:
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
                record = read(path)
                errors, warnings = validate(root, record, reqs, state)
                result.update(errors=errors, warnings=warnings, progress=progress_status(record))
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
                mark_historical(root, record)
            errors, warnings = validate(root, record, reqs, state)
            if args.command == 'record' and not errors:
                claims = read(safe(root, args.claim_file)) if args.claim_file else []
                if isinstance(claims, dict) and claims.get('claimSchema') == 1:
                    claims = claims['claims']
                if not isinstance(claims, list):
                    raise ValueError('Claim file must contain an array or claimSchema=1 packet')
                for c in claims:
                    for key in ('requirement','scenario','oracle','verificationScope','scope','evidence','sourceHashes','reviewer','disposition','missingObservations'):
                        if key not in c:
                            raise ValueError('Claim missing ' + key)
                    if not isinstance(c['evidence'], list) or not isinstance(c['sourceHashes'], dict) or not isinstance(c['missingObservations'], list):
                        raise ValueError('Claim evidence/missingObservations must be arrays; sourceHashes must be an object')
                    if not c['evidence'] or not c['reviewer'] or not c['scope'] or not c['disposition']:
                        raise ValueError('Claims require evidence, scope, reviewer and disposition')
                hashes = {n: digest(safe(root,n)) for n in record['slice']['paths']}
                previous = extension_baseline(record, record['iterations'][-1]['sourceHashes'] if record['iterations'] else record['sourceHashes'], len(record['iterations']))
                seen_verdicts = {verdict_key(c) for i in record['iterations'] for c in i.get('claims', [])}
                progress = (args.outcome == 'production-fix' and product_delta(hashes, previous)) or (args.outcome == 'scenario-verdict' and any(verdict_key(c) not in seen_verdicts for c in claims))
                record['iterations'].append({'atUTC': now(), 'outcome': args.outcome, 'summary': args.summary, 'sourceHashes': hashes, 'meaningfulProgress': progress, 'progressPolicy': 2, 'claims': claims, 'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip()})
                errors, warnings = validate(root, record, reqs, state)
                if not errors:
                    write_record(path, record)
            result.update(errors=errors, warnings=warnings, record=args.record, progress=progress_status(record))
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
    if args.command == 'report' and args.markdown and 'reportSchema' in result:
        print(report_markdown(result))
    else:
        print(json.dumps(result, indent=2) if args.json else '\n'.join([BOUNDARY, json.dumps(result, indent=2)]))
    return code


if __name__ == '__main__':
    sys.exit(main())

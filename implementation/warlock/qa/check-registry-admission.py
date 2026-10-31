#!/usr/bin/env python3
"""ELM-REV-005 actual contributor admission regression; protected root QA only.

Usage: python3 -B implementation/warlock/qa/check-registry-admission.py REPORT.json
Only disposable Git fixture inputs are mutated. No product runtime or native GUI
is launched. Expected rejection failures remain failures in the retained report.
"""
import argparse
import collections
import ctypes
import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parents[3]
CHECKER = 'plugins/warlock-contributor/scripts/warlock.py'
REGISTRY = 'docs/elm-roadmap/requirements.json'
TASKS = 'openspec/changes/elm-desktop-pivot/tasks.md'
TRACE = 'docs/elm-roadmap/TRACEABILITY.md'
COPIED = [
    CHECKER, REGISTRY,
    'docs/elm-roadmap/baselines/requirements-pre-language-20261030.json',
    'docs/elm-roadmap/language-revision.json',
    'docs/elm-roadmap/tools/language_revision.py',
    'docs/warlock-build-loop/v2/requirement-ledger.json',
    'docs/warlock-build-loop/v2/STATE.json', TASKS, TRACE,
]
SEED = 20261031


def sha(data):
    return hashlib.sha256(data).hexdigest()


def hashes(root, names):
    return {name: sha((root / name).read_bytes()) if (root / name).is_file() else None for name in names}


def independent_mapping_errors(document, task_text, trace_text):
    """Original-oracle parser; it imports no implementation validator."""
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    rows = document.get('requirements', [])
    ids = [row.get('id') for row in rows]
    require(len(rows) == 242 and len(set(ids)) == 242, 'registry must contain exactly242 distinct requirements')
    scenarios = []
    expected_tasks = {}
    for row in rows:
        identity = row.get('id')
        for field in ['id', 'phase', 'taskId', 'task', 'verification', 'accountableOwnerRole', 'verifierRole']:
            require(isinstance(row.get(field), str) and bool(row[field].strip()), str(identity) + ': missing nonempty ' + field)
        require(row.get('accountableOwnerRole') != row.get('verifierRole'), str(identity) + ': reviewer must be independent')
        require(row.get('phase') in ['P' + str(n) for n in range(9)], str(identity) + ': invalid phase')
        require(row.get('taskId') == str(row.get('phase')) + '-' + str(identity), str(identity) + ': task/phase identity mismatch')
        require(isinstance(row.get('scenarios'), list) and bool(row.get('scenarios')), str(identity) + ': missing named scenarios')
        for scenario in row.get('scenarios', []):
            for field in ['name', 'given', 'when', 'then']:
                require(isinstance(scenario.get(field), str) and bool(scenario[field].strip()), str(identity) + ': malformed scenario ' + field)
            scenarios.append((identity, scenario.get('name')))
        if isinstance(row.get('taskId'), str):
            expected_tasks[row['taskId']] = row
    require(len(scenarios) == 417 and len(set(scenarios)) == 417, 'registry must contain exactly417 distinct qualified scenarios')

    phase = None
    actual_tasks = []
    for line in task_text.splitlines():
        heading = re.match(r'^## (P[0-8])(?:\s|$)', line)
        if heading:
            phase = heading.group(1)
        match = re.fullmatch(r'- \[[ xX]\] (P[0-8]-ELM-[A-Z]+-\d{3}): (.+)', line)
        if match:
            task, body = match.groups()
            actual_tasks.append(task)
            expected = expected_tasks.get(task)
            require(expected is not None, 'foreign task row: ' + task)
            require(task.split('-')[0] == phase, 'task under wrong phase heading: ' + task)
            if expected is not None:
                require(body == str(expected.get('task')) + ' Verify: ' + str(expected.get('verification')), 'task description/verification mapping differs: ' + task)
        elif line.startswith('- [') and 'ELM-' in line:
            errors.append('malformed requirement task row: ' + line)
    require(collections.Counter(actual_tasks) == collections.Counter(expected_tasks.keys()), 'task rows are not a bijection with registry')

    actual_trace = []
    by_id = {row.get('id'): row for row in rows}
    for line in trace_text.splitlines():
        if not line.startswith('| ELM-'):
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        require(len(cells) == 8, 'trace row does not have8 columns: ' + line[:80])
        if len(cells) != 8:
            continue
        identity, phase, priority, scenario_link, task, roles, verification, legacy = cells
        actual_trace.append(identity)
        expected = by_id.get(identity)
        require(expected is not None, 'foreign trace row: ' + identity)
        if expected is None:
            continue
        require(phase == expected.get('phase') and priority == expected.get('priority'), identity + ': trace phase/priority differs')
        require(task == expected.get('taskId'), identity + ': trace task differs')
        require(roles == str(expected.get('accountableOwnerRole')) + ' / ' + str(expected.get('verifierRole')), identity + ': trace explicit owner/verifier differs')
        require(verification == expected.get('verification') and legacy == expected.get('legacyEvidence'), identity + ': trace verification/evidence mapping differs')
        link = re.fullmatch(r'\[(\d+) scenario\(s\)\]\(([^)]+)\)', scenario_link)
        require(link is not None, identity + ': trace scenario link malformed')
        if link:
            expected_target = '../../openspec/changes/elm-desktop-pivot/specs/' + str(expected.get('capability')) + '/spec.md#requirement-' + identity.lower()
            require(int(link.group(1)) == len(expected.get('scenarios', [])) and link.group(2) == expected_target, identity + ': trace scenario count/capability anchor differs')
    require(collections.Counter(actual_trace) == collections.Counter(ids), 'trace rows are not a bijection with registry')
    return errors


class CreationWatch:
    """Observe attempted participant-directory creation, including create/delete."""
    def __init__(self, directory):
        library = ctypes.CDLL(None, use_errno=True)
        library.inotify_init1.argtypes = [ctypes.c_int]
        library.inotify_init1.restype = ctypes.c_int
        library.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        library.inotify_add_watch.restype = ctypes.c_int
        self.fd = library.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if self.fd < 0:
            raise OSError(ctypes.get_errno(), 'inotify_init1')
        # IN_CREATE / MOVED_TO / DELETE / MOVED_FROM. A refused command must
        # not create and subsequently remove a fresh participant parent either.
        if library.inotify_add_watch(self.fd, os.fsencode(directory), 0x100 | 0x80 | 0x200 | 0x40) < 0:
            error = ctypes.get_errno()
            os.close(self.fd)
            raise OSError(error, 'inotify_add_watch')

    def finish(self):
        events = []
        try:
            while True:
                try:
                    data = os.read(self.fd, 65536)
                except BlockingIOError:
                    break
                if not data:
                    break
                cursor = 0
                while cursor < len(data):
                    descriptor, mask, cookie, length = struct.unpack_from('iIII', data, cursor)
                    name = os.fsdecode(data[cursor + 16:cursor + 16 + length].split(b'\0', 1)[0])
                    events.append({'descriptor': descriptor, 'mask': mask, 'cookie': cookie, 'name': name})
                    cursor += 16 + length
        finally:
            os.close(self.fd)
        return events


def artifact_snapshot(root, parent):
    result = {}
    if not parent.exists():
        return result
    for candidate in [parent, *sorted(parent.rglob('*'))]:
        name = str(candidate.relative_to(root))
        if candidate.is_file() and not candidate.is_symlink():
            data = candidate.read_bytes()
            result[name] = {'type': 'file', 'sha256': sha(data), 'bytes': len(data), 'text': data.decode('utf-8', errors='replace')}
        else:
            result[name] = {'type': 'symlink' if candidate.is_symlink() else 'directory'}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    output = args.report.absolute()
    report = {'schema': 1, 'requirement': 'ELM-REV-005', 'scenario': 'requirement-ownership',
              'oracle': 'every row has explicit role and verifier mapping and missing mappings block admission',
              'verification': 'Registry/task/traceability bijection and explicit nonempty role mapping with separate acceptance reviewer.',
              'scope': 'Actual development contributor CLI admission in disposable Git fixtures; no GUI/product/native behavior',
              'seed': SEED, 'seedGenerator': 'Python random.Random(seed).sample over frozen ordered registry IDs; source and Python version retained',
              'passed': False, 'nativeAcceptance': False, 'releaseAccepted': False,
              'commands': [], 'checks': [], 'cases': [], 'failures': [],
              'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}

    def save():
        output.write_text(json.dumps(report, indent=2) + '\n')

    def check(name, condition, detail=None):
        row = {'name': name, 'passed': bool(condition)}
        if not condition:
            row['detail'] = detail
            report['failures'].append(row)
        report['checks'].append(row)
        return bool(condition)

    try:
        sys.path.insert(0, str(REPO / 'window-integration-qa'))
        from qa_launch import require_qa_scope
        report['protectedScope'] = require_qa_scope()
        original_bytes = {name: (REPO / name).read_bytes() for name in COPIED}
        report['sourceHashes'] = {name: sha(data) for name, data in original_bytes.items()}
        report['sourceHashes'][str(Path(__file__).relative_to(REPO))] = sha(Path(__file__).read_bytes())
        report['sourceHashes']['window-integration-qa/qa_launch.py'] = sha((REPO / 'window-integration-qa/qa_launch.py').read_bytes())
        report['sourceBase'] = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
        python = Path(sys.executable).resolve()
        git = Path(shutil.which('git') or '/missing-git').resolve()
        report['tools'] = {'python': {'path': str(python), 'sha256': sha(python.read_bytes()), 'version': sys.version},
                           'git': {'path': str(git), 'sha256': sha(git.read_bytes())}}
        registry = json.loads(original_bytes[REGISTRY])
        report['independentMappingErrors'] = independent_mapping_errors(registry, original_bytes[TASKS].decode(), original_bytes[TRACE].decode())
        if not check('Original242/417 registry/task/trace/independent-role mapping is complete', not report['independentMappingErrors'], report['independentMappingErrors']):
            raise RuntimeError('Current complete-input precondition failed; no valid admission baseline inferred')
        rows = registry['requirements']
        by_id = {row['id']: row for row in rows}
        selected = by_id['ELM-REV-005']
        report['originalRequirement'] = selected
        env = {key: value for key, value in os.environ.items() if not key.startswith(('GIT_', 'GROK_', 'AGENTBUS_'))}
        env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', PYTHONDONTWRITEBYTECODE='1',
                   GIT_AUTHOR_DATE='2000-01-01T00:00:00Z', GIT_COMMITTER_DATE='2000-01-01T00:00:00Z')
        with tempfile.TemporaryDirectory(prefix='warlock-registry-admission-') as temporary:
            fixture = Path(temporary)
            for name, data in original_bytes.items():
                target = fixture / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            state = json.loads(original_bytes['docs/warlock-build-loop/v2/STATE.json'])
            selected_slice = {'id': 'registry-admission-original-oracle', 'requirements': ['ELM-REV-005'], 'scenarios': ['requirement-ownership'],
                              'paths': ['implementation/warlock/qa/registry-admission-marker.txt'],
                              'before': 'Fixture admission has not been evaluated.', 'after': 'Admission is allowed only with complete original mappings.',
                              'verification': ['Actual contributor start positive and malformed registry/task/trace refusal before any participant artifact.']}
            state['activeSlice'] = selected_slice
            (fixture / 'docs/warlock-build-loop/v2/STATE.json').write_text(json.dumps(state, indent=2) + '\n')
            (fixture / '.gitignore').write_text('/.warlock-contributor/\n')
            (fixture / 'admission-slice.json').write_text(json.dumps(selected_slice, indent=2) + '\n')
            marker = fixture / selected_slice['paths'][0]
            marker.parent.mkdir(parents=True)
            marker.write_text('Data-only owned declaration marker for the original registry admission fixture.\n')
            fixture_inputs = [*COPIED, '.gitignore', 'admission-slice.json', selected_slice['paths'][0]]
            pristine = {name: (fixture / name).read_bytes() for name in fixture_inputs}

            def git_command(*arguments):
                command = [str(git), '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgSign=false', '-c', 'tag.gpgSign=false', '-C', str(fixture), *arguments]
                result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=20)
                report['commands'].append({'argv': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
                if result.returncode:
                    raise RuntimeError('Disposable Git setup failed: ' + result.stderr)
                return result.stdout.strip()

            git_command('init', '-q')
            git_command('config', 'user.name', 'Registry admission fixture')
            git_command('config', 'user.email', 'fixture@example.invalid')
            git_command('config', 'core.hooksPath', '/dev/null')
            git_command('config', 'commit.gpgSign', 'false')
            git_command('config', 'tag.gpgSign', 'false')
            git_command('config', 'core.autocrlf', 'false')
            git_command('config', 'core.safecrlf', 'false')
            attributes = fixture / '.git/info/attributes'
            attributes.write_text('* -text -filter\n')
            report['fixtureGitControls'] = {'localConfig': {'core.hooksPath': '/dev/null', 'commit.gpgSign': 'false', 'tag.gpgSign': 'false', 'core.autocrlf': 'false', 'core.safecrlf': 'false'},
                                          'ownedAttributesSHA256': sha(attributes.read_bytes()),
                                          'limit': 'The contributor checker preserves its existing Git environment cleanup and performs local read-only Git inspection. These fixture controls do not establish a general hostile-Git sandbox.'}
            git_command('add', '.')
            git_command('commit', '-qm', 'Exact source registry admission fixture')
            report['fixtureSourceRevision'] = git_command('rev-parse', 'HEAD')
            report['fixtureInputHashes'] = hashes(fixture, fixture_inputs)
            case_index = 0

            def restore():
                for name in [REGISTRY, TASKS, TRACE]:
                    target = fixture / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(pristine[name])

            def attempt(name, mutation=None, expected_admission=False, seeded=False):
                nonlocal case_index
                restore()
                descriptor = mutation() if mutation else {'kind': 'complete-current-inputs'}
                case_index += 1
                case_name = 'attempt-' + str(case_index).zfill(3)
                record = '.warlock-contributor/' + case_name + '/record.json'
                parent = fixture / '.warlock-contributor' / case_name
                command = [str(python), '-B', str(fixture / CHECKER), '--repo', str(fixture), '--record', record, '--json',
                           'start', '--owner', 'registry-fixture', '--slice-file', 'admission-slice.json']
                entry = {'name': name, 'seeded': seeded, 'mutation': descriptor, 'expectedAdmission': expected_admission,
                         'record': record, 'argv': command, 'inputHashes': hashes(fixture, fixture_inputs)}
                report['cases'].append(entry)
                require_errors = independent_mapping_errors(json.loads((fixture / REGISTRY).read_bytes()),
                                                           (fixture / TASKS).read_text() if (fixture / TASKS).exists() else '',
                                                           (fixture / TRACE).read_text() if (fixture / TRACE).exists() else '')
                entry['independentMappingErrors'] = require_errors
                check(name + ': independent oracle classifies the intended input', (not require_errors) == expected_admission, require_errors)
                check(name + ': unique participant parent does not already exist', not parent.exists())
                watch = CreationWatch(fixture / '.warlock-contributor') if (fixture / '.warlock-contributor').exists() else None
                try:
                    result = subprocess.run(command, cwd=fixture, env=env, capture_output=True, text=True, timeout=30)
                    entry.update(exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
                finally:
                    entry['creationEvents'] = watch.finish() if watch else []
                    entry['artifacts'] = artifact_snapshot(fixture, parent)
                    entry['inputHashesAfter'] = hashes(fixture, fixture_inputs)
                    save()
                try:
                    packet = json.loads(result.stdout)
                except (ValueError, UnboundLocalError):
                    packet = None
                entry['packet'] = packet
                check(name + ': actual copied checker returns its source-bound JSON result', isinstance(packet, dict) and packet.get('checkerSha256') == report['sourceHashes'][CHECKER], packet)
                check(name + ': contributor never rewrites registry/task/trace inputs', entry['inputHashesAfter'] == entry['inputHashes'])
                if expected_admission:
                    admitted = result.returncode == 0 and packet is not None and packet.get('ok') is True and (fixture / record).is_file()
                    check(name + ': actual start admits complete registry inputs', admitted, entry)
                    if not admitted:
                        raise RuntimeError('Positive actual start did not admit; no valid negative admission campaign inferred')
                    created = json.loads((fixture / record).read_text())
                    check(name + ': positive record binds exact selected original and actual fixture revision', created.get('slice', {}).get('requirements') == ['ELM-REV-005'] and created['slice'].get('scenarios') == ['requirement-ownership'] and created.get('sourceRevision') == report['fixtureSourceRevision'], created)
                else:
                    check(name + ': invalid mapping refuses actual implementation admission', result.returncode != 0 and isinstance(packet, dict) and packet.get('ok') is False and bool(packet.get('errors')), packet)
                    check(name + ': refusal creates no participant directory/record/lock even transiently', not parent.exists() and not entry['artifacts'] and not entry['creationEvents'], {'events': entry['creationEvents'], 'artifacts': entry['artifacts']})
                save()

            def mutate_task(kind, row):
                def mutation():
                    lines = pristine[TASKS].decode().splitlines(keepends=True)
                    index = next(index for index, line in enumerate(lines) if re.match(r'- \[[ xX]\] ' + re.escape(row['taskId']) + ':', line))
                    old = lines[index]
                    if kind == 'missing':
                        del lines[index]
                    elif kind == 'duplicate':
                        lines.insert(index + 1, old)
                    elif kind == 'foreign':
                        lines[index] = old.replace(row['taskId'], row['phase'] + '-ELM-FOREIGN-999', 1)
                    elif kind == 'wrong-phase':
                        lines[index] = old.replace(row['taskId'], ('P8' if row['phase'] != 'P8' else 'P0') + '-' + row['id'], 1)
                    elif kind == 'wrong-body':
                        lines[index] = old.split(':', 1)[0] + ': Unrelated task. Verify: Unrelated verification.\n'
                    elif kind == 'missing-file':
                        (fixture / TASKS).unlink()
                        return {'kind': 'task-' + kind, 'requirement': row['id'], 'path': TASKS}
                    else:
                        raise ValueError(kind)
                    (fixture / TASKS).write_text(''.join(lines))
                    return {'kind': 'task-' + kind, 'requirement': row['id'], 'path': TASKS, 'originalRow': old.rstrip('\n'), 'changedRow': None if kind == 'missing' else lines[index].rstrip('\n')}
                return mutation

            def mutate_trace(kind, row):
                def mutation():
                    lines = pristine[TRACE].decode().splitlines(keepends=True)
                    index = next(index for index, line in enumerate(lines) if line.startswith('| ' + row['id'] + ' |'))
                    old = lines[index]
                    cells = [cell.strip() for cell in old.split('|')[1:-1]]
                    if kind == 'missing':
                        del lines[index]
                    elif kind == 'duplicate':
                        lines.insert(index + 1, old)
                    elif kind == 'missing-file':
                        (fixture / TRACE).unlink()
                        return {'kind': 'trace-' + kind, 'requirement': row['id'], 'path': TRACE}
                    else:
                        if kind == 'foreign':
                            cells[0] = 'ELM-FOREIGN-999'
                        elif kind == 'wrong-phase':
                            cells[1] = 'P8' if row['phase'] != 'P8' else 'P0'
                        elif kind == 'wrong-task':
                            cells[4] = row['phase'] + '-ELM-FOREIGN-999'
                        elif kind == 'wrong-owner':
                            cells[5] = 'Unassigned / ' + row['verifierRole']
                        elif kind == 'non-independent-reviewer':
                            cells[5] = row['accountableOwnerRole'] + ' / ' + row['accountableOwnerRole']
                        elif kind == 'wrong-scenario-count':
                            cells[3] = cells[3].replace('[' + str(len(row['scenarios'])) + ' scenario', '[' + str(len(row['scenarios']) + 1) + ' scenario', 1)
                        elif kind == 'wrong-capability':
                            cells[3] = cells[3].replace('/' + row['capability'] + '/', '/foreign-capability/', 1)
                        else:
                            raise ValueError(kind)
                        lines[index] = '| ' + ' | '.join(cells) + ' |\n'
                    (fixture / TRACE).write_text(''.join(lines))
                    return {'kind': 'trace-' + kind, 'requirement': row['id'], 'path': TRACE, 'originalRow': old.rstrip('\n'), 'changedRow': None if kind == 'missing' else lines[index].rstrip('\n')}
                return mutation

            def mutate_registry(field, mode='missing'):
                def mutation():
                    document = json.loads(pristine[REGISTRY])
                    row = next(value for value in document['requirements'] if value['id'] == 'ELM-REV-005')
                    previous = json.loads(json.dumps(row.get(field)))
                    if mode == 'missing':
                        row.pop(field)
                    elif mode == 'whitespace':
                        row[field] = ' '
                    elif mode == 'same-reviewer':
                        row['verifierRole'] = row['accountableOwnerRole']
                    elif mode == 'duplicate':
                        row['scenarios'].append(dict(row['scenarios'][0]))
                    (fixture / REGISTRY).write_text(json.dumps(document, indent=2) + '\n')
                    return {'kind': 'registry-' + mode, 'path': REGISTRY, 'requirement': row['id'], 'field': field, 'originalValue': previous, 'newValue': row.get(field), 'frozenHashGuardRetained': True}
                return mutation

            attempt('positive-complete-current-inputs', expected_admission=True)
            for field in ['accountableOwnerRole', 'verifierRole', 'phase', 'taskId', 'task', 'scenarios']:
                attempt('registry-missing-' + field, mutate_registry(field))
            attempt('registry-whitespace-owner', mutate_registry('accountableOwnerRole', 'whitespace'))
            attempt('registry-non-independent-reviewer', mutate_registry('verifierRole', 'same-reviewer'))
            attempt('registry-duplicate-named-scenario', mutate_registry('scenarios', 'duplicate'))
            for kind in ['missing', 'duplicate', 'foreign', 'wrong-phase', 'wrong-body', 'missing-file']:
                attempt('task-' + kind, mutate_task(kind, selected))
            for kind in ['missing', 'duplicate', 'foreign', 'wrong-phase', 'wrong-task', 'wrong-owner', 'non-independent-reviewer', 'wrong-scenario-count', 'wrong-capability', 'missing-file']:
                attempt('trace-' + kind, mutate_trace(kind, selected))
            seeded_rows = random.Random(SEED).sample(rows, 8)
            report['seededRequirements'] = [row['id'] for row in seeded_rows]
            for index, row in enumerate(seeded_rows):
                functions = [mutate_task('missing', row), mutate_task('duplicate', row), mutate_trace('missing', row), mutate_trace('wrong-owner', row)]
                attempt('seeded-' + str(index) + '-' + row['id'], functions[index % len(functions)], seeded=True)
            attempt('positive-restored-after-all-mutations', expected_admission=True)
            restore()
            check('All copied fixture inputs finish byte-exact after mutation campaign', hashes(fixture, fixture_inputs) == report['fixtureInputHashes'])
        check('Actual repository source inputs remain byte-exact', all((REPO / name).read_bytes() == data for name, data in original_bytes.items()))
        report['passed'] = not report['failures']
    except Exception as error:
        report['error'] = repr(error)
        report['failures'].append({'name': 'QA execution precondition/completion', 'passed': False, 'detail': repr(error)})
    finally:
        save()
    print(json.dumps({'passed': report['passed'], 'cases': len(report['cases']), 'checks': len(report['checks']), 'failures': len(report['failures']), 'report': str(output), 'error': report.get('error')}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

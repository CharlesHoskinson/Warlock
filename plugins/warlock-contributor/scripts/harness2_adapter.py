"""Optional Harness2 comparison boundary; standard library only on Python 3.9+."""
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

UPSTREAM_COMMIT = '6868817518876de8fd170c6a8354daca273b6191'
UPSTREAM_URL = 'https://github.com/google-research/harness2'
ROLES = ('taskFiles', 'sourceFiles', 'oracleFiles', 'guardFiles', 'authorizationFiles', 'pluginBaselineFiles')
EDITABLE = {'prompt', 'toolGuidance', 'taskDecomposition', 'handoff'}
MAX_BYTES = 1048576

# Reviewed credential-free API only. No benchmark CLI, agent executor or model.
# The upstream substrate package defines Codex classes on import; none is called.
PROBE_CODE = r'''
import json, os, sys
from pathlib import Path
root, output = map(Path, sys.argv[1:])
def offline_only(event, args):
    if event.startswith('socket.'):
        raise RuntimeError('network is disabled in the deterministic probe')
    if event == 'subprocess.Popen':
        executable, argv, _cwd, _env = args
        if (os.path.realpath(executable) != os.path.realpath(sys.executable) or len(argv) != 3
                or Path(argv[1]).name != 'summarize.py' or output not in Path(argv[1]).resolve().parents
                or Path(argv[2]).name != 'ledger.csv' or output not in Path(argv[2]).resolve().parents):
            raise RuntimeError('only the fixed private arithmetic subprocess is permitted')
sys.addaudithook(offline_only)
sys.path.insert(0, str(root))
from harness2.core.schedule import run_domain
from harness2.demo import DemoAdapter, DemoProposer
adapter = DemoAdapter(output)
proposer = DemoProposer(adapter.spec.channels['proposer'])
result = run_domain('accounting', adapter.tasks(), 1, adapter=adapter, prop=proposer,
                    runs_root=adapter.spec.runs_root, library_root=output / 'library',
                    modes=('agg', 'seq'), seed=0)
result['execution_count'] = adapter.execution_count
result['editor_calls'] = len(proposer._calls)
(output / 'demo.json').write_text(json.dumps(result, indent=2) + '\n')
if result['failed'] or result['done'] != 2:
    raise SystemExit('deterministic upstream probe failed')
print(json.dumps({'done':result['done'], 'failed':result['failed'],
                  'executionCount':adapter.execution_count, 'editorCalls':len(proposer._calls)}))
'''


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_file_hash(path):
    return hashlib.sha256(_bytes(path)).hexdigest()


def canonical_sha(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def _bytes(path):
    fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_size <= MAX_BYTES, 'not a bounded regular input')
        data = bytearray()
        while len(data) <= MAX_BYTES:
            chunk = os.read(fd, min(65536, MAX_BYTES + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        after = os.fstat(fd)
        require(len(data) <= MAX_BYTES and (before.st_dev, before.st_ino, before.st_size,
                before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns), 'input changed or exceeded bound')
        return bytes(data)
    finally:
        os.close(fd)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def invalid_constant(_value):
        raise ValueError('nonfinite JSON constant')
    return json.loads(_bytes(Path(path)), object_pairs_hook=unique, parse_constant=invalid_constant)


def _root(root):
    path = Path(root).absolute()
    require(not path.is_symlink() and path.is_dir(), 'context root must be a real directory')
    require(path == path.resolve(), 'context root cannot contain symlinks')
    info = path.stat()
    require(info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) & 0o077 == 0,
            'context root must be owned and private')
    return path


def _file(root, name):
    require(isinstance(name, str) and bool(name), 'missing relative input path')
    relative = Path(name)
    require(not relative.is_absolute() and '..' not in relative.parts and str(relative) == name
            and name != '.', 'input path escapes or is not canonical')
    current = root
    for part in relative.parts:
        current = current / part
        require(not current.is_symlink(), 'symlink input refused')
    require(current.is_file(), 'input file is missing')
    return current


def _strings(values):
    return (isinstance(values, list) and 0 < len(values) <= 128
            and all(isinstance(value, str) and 0 < len(value) <= 4096 for value in values)
            and len(set(values)) == len(values))


def _harness(harness):
    require(isinstance(harness, dict) and set(harness) == EDITABLE, 'only four guidance fields are editable')
    for field in EDITABLE - {'taskDecomposition'}:
        require(isinstance(harness[field], str) and 0 < len(harness[field]) <= 65536, 'invalid guidance text')
    require(_strings(harness['taskDecomposition']), 'invalid task decomposition')
    return harness


def _bindings(root, files):
    require(_strings(files), 'invalid file inventory')
    result = {}
    for name in files:
        raw = _bytes(_file(root, name))
        result[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    return result


def freeze(context_root, request, harness):
    root = _root(context_root)
    require(isinstance(request, dict) and set(request) == {'schema', 'taskId', 'checkNames', *ROLES},
            'invalid request fields')
    require(type(request['schema']) is int and request['schema'] == 1, 'unsupported request schema')
    require(isinstance(request['taskId'], str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', request['taskId']),
            'invalid task identity')
    require(_strings(request['checkNames']), 'invalid frozen check inventory')
    fixed, used = {}, set()
    for role in ROLES:
        fixed[role] = _bindings(root, request[role])
        require(not used.intersection(fixed[role]), 'one input cannot occupy two immutable roles')
        used.update(fixed[role])
    guidance = json.loads(json.dumps(_harness(harness), allow_nan=False))
    return {'schema': 1, 'upstreamCommit': UPSTREAM_COMMIT, 'contextRoot': str(root),
            'taskId': request['taskId'], 'checkNames': list(request['checkNames']), 'fixedInputs': fixed,
            'harness': guidance, 'harnessSha256': canonical_sha(guidance),
            'acceptanceAuthority': False}


def _validate_snapshot(snapshot):
    keys = {'schema', 'upstreamCommit', 'contextRoot', 'taskId', 'checkNames', 'fixedInputs',
            'harness', 'harnessSha256', 'acceptanceAuthority'}
    require(isinstance(snapshot, dict) and set(snapshot) == keys, 'invalid snapshot fields')
    require(snapshot['upstreamCommit'] == UPSTREAM_COMMIT and snapshot['acceptanceAuthority'] is False,
            'snapshot pin or authority differs')
    require(isinstance(snapshot['fixedInputs'], dict) and set(snapshot['fixedInputs']) == set(ROLES),
            'invalid immutable input roles')
    request = {'schema': snapshot['schema'], 'taskId': snapshot['taskId'], 'checkNames': snapshot['checkNames']}
    for role in ROLES:
        require(isinstance(snapshot['fixedInputs'][role], dict), 'invalid immutable input map')
        request[role] = list(snapshot['fixedInputs'][role])
    current = freeze(snapshot['contextRoot'], request, snapshot['harness'])
    require(current == snapshot, 'snapshot inputs/guidance changed or were forged')
    return current


def _observation(snapshot, observation):
    require(isinstance(observation, dict) and set(observation) ==
            {'schema', 'taskId', 'snapshotSha256', 'checks', 'reportFiles', 'regressionFiles'}, 'invalid observation fields')
    require(type(observation['schema']) is int and observation['schema'] == 1
            and observation['taskId'] == snapshot['taskId']
            and observation['snapshotSha256'] == canonical_sha(snapshot), 'observation binds a different task/snapshot')
    checks = observation['checks']
    require(isinstance(checks, list) and len(checks) == len(snapshot['checkNames']), 'omitted/injected checks')
    require(all(isinstance(row, dict) and set(row) == {'name', 'passed'} and type(row['passed']) is bool
                for row in checks), 'invalid check result')
    require([row['name'] for row in checks] == snapshot['checkNames'], 'check order/inventory changed')
    reports = _bindings(_root(snapshot['contextRoot']), observation['reportFiles'])
    regressions = _bindings(_root(snapshot['contextRoot']), observation['regressionFiles'])
    return sum(row['passed'] for row in checks), reports, regressions


def compare(baseline, candidate, baseline_observation, candidate_observation, completed_candidate_sha):
    require(isinstance(completed_candidate_sha, str) and re.fullmatch(r"[0-9a-f]{64}", completed_candidate_sha),
            "explicit full core completed-candidate digest required")
    baseline, candidate = _validate_snapshot(baseline), _validate_snapshot(candidate)
    for field in ('schema', 'upstreamCommit', 'taskId', 'checkNames', 'fixedInputs'):
        require(baseline[field] == candidate[field], 'changed task/source/oracle/authorization/guard input')
    before, before_reports, before_regressions = _observation(baseline, baseline_observation)
    after, after_reports, after_regressions = _observation(candidate, candidate_observation)
    return {'schema': 1, 'kind': 'same-task-harness-comparison', 'upstreamCommit': UPSTREAM_COMMIT, 'taskId': baseline['taskId'],
            'baselineSnapshotSha256': canonical_sha(baseline), 'candidateSnapshotSha256': canonical_sha(candidate),
            'changedHarnessFields': sorted(field for field in EDITABLE if baseline['harness'][field] != candidate['harness'][field]),
            'baselinePassedChecks': before, 'candidatePassedChecks': after, 'passedCheckDelta': after - before,
            'checkNames': baseline['checkNames'],
            'observationSha256': {'baseline': canonical_sha(baseline_observation), 'candidate': canonical_sha(candidate_observation)},
            'reportBindings': {'baseline': before_reports, 'candidate': after_reports},
            'completedCandidateSha256': completed_candidate_sha,
            'baselinePluginSha256': canonical_sha({name: row['sha256'] for name, row in baseline['fixedInputs']['pluginBaselineFiles'].items()}),
            'sourceSnapshotSha256': canonical_sha({name: row['sha256'] for name, row in baseline['fixedInputs']['sourceFiles'].items()}),
            'immutableHashes': {role: canonical_sha({name: row['sha256'] for name, row in baseline['fixedInputs'][role].items()}) for role in ROLES},
            'checks': [{'name': left['name'], 'baselinePassed': left['passed'], 'candidatePassed': right['passed']}
                       for left, right in zip(baseline_observation['checks'], candidate_observation['checks'])],
            'regression': {'path': str(Path(candidate['contextRoot']) / next(iter(after_regressions))),
                           'sha256': next(iter(after_regressions.values()))['sha256']},
            'rsi': {
                    'sameTaskProbeRefs': {'baseline': before_reports, 'candidate': after_reports},
                    'regressionRefs': {'baseline': before_regressions, 'candidate': after_regressions},
                    'proposedDisposition': 'deferred-blocker' if after > before else 'no-change',
                    'reason': 'Independent improvement/adoption review required; supplied deltas are not verified adoption.'
                              if after > before else 'No positive supplied check-count delta; retain baseline unless reviewed evidence warrants a change.',
                    'adoptionVerified': False, 'recursiveRsi': False},
            'evidenceScope': 'Supplied report comparisons only; not independently executed or accepted task outcomes.',
            'acceptanceAuthority': False, 'autoAdopt': False, 'originalAcceptance': False,
            'nativeAcceptance': False, 'releaseAccepted': False}


def check_probe_interpreter(version):
    require(tuple(version[:2]) == (3, 12), 'optional upstream probe requires isolated Python 3.12')


def _git_bytes(root, *arguments):
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'GIT_NO_REPLACE_OBJECTS': '1',
           'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null'}
    result = subprocess.run(['git', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null',
                             '-C', str(root), *arguments], env=env,
                            capture_output=True, check=True, timeout=20)
    return result.stdout


def _git(root, *arguments):
    return _git_bytes(root, *arguments).decode('utf-8').strip()


def verify_upstream(upstream):
    require(_git(upstream, 'rev-parse', 'HEAD') == UPSTREAM_COMMIT, 'upstream commit differs')
    require(not _git(upstream, 'status', '--porcelain', '--untracked-files=all', '--ignored'),
            'upstream checkout must have no changed/untracked/ignored inputs')
    require(not os.path.lexists(upstream / '.env'), 'upstream dotenv is not permitted')
    paths = _git(upstream, 'ls-tree', '-r', '--name-only', UPSTREAM_COMMIT, '--', 'harness2').splitlines()
    require(paths and len(paths) <= 256, 'unexpected upstream module inventory')
    bindings = {}
    for name in paths:
        body = _bytes(_file(upstream, name))
        committed = _git_bytes(upstream, 'show', UPSTREAM_COMMIT + ':' + name)
        require(body == committed, 'upstream body differs from pin (including assumed-unchanged files)')
        bindings[name] = hashlib.sha256(body).hexdigest()
    return bindings


def demo_report(output):
    report = read_json(Path(output) / 'demo.json')
    require(isinstance(report, dict) and report.get('done') == 2 and report.get('failed') == 0,
            'upstream deterministic tasks did not complete')
    require(type(report.get('execution_count')) is int and 0 < report['execution_count'] <= 32
            and type(report.get('editor_calls')) is int and 0 < report['editor_calls'] <= 64,
            'upstream deterministic work exceeded its fixed bound')
    return {'done': report['done'], 'failed': report['failed'],
            'executionCount': report['execution_count'], 'editorCalls': report['editor_calls']}


def upstream_probe(upstream_root, output_root):
    """Run only the fixed reviewed deterministic upstream API in a fresh context."""
    check_probe_interpreter(sys.version_info)
    upstream = Path(upstream_root).resolve()
    upstream_bindings = verify_upstream(upstream)
    output = _root(output_root)
    require(not list(output.iterdir()), 'probe output must be a fresh empty private context')
    require(not output.is_relative_to(upstream) if hasattr(output, 'is_relative_to') else upstream not in output.parents,
            'probe output cannot modify upstream checkout')
    env = {'PATH': str(Path(sys.executable).parent) + ':/usr/bin:/bin', 'HOME': str(output),
           'TMPDIR': str(output), 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1'}
    run = subprocess.run([sys.executable, '-I', '-B', '-c', PROBE_CODE, str(upstream), str(output)],
                         cwd=output, env=env, capture_output=True, text=True, timeout=120, check=False)
    _write_new(output / 'adapter-process-output.json', {'stdout': run.stdout, 'stderr': run.stderr, 'exit': run.returncode})
    require(run.returncode == 0, 'upstream deterministic probe failed; retained adapter-process-output.json; no model fallback')
    require(verify_upstream(upstream) == upstream_bindings, 'upstream modules changed during probe')
    result = demo_report(output)
    return {'schema': 1, 'upstreamCommit': UPSTREAM_COMMIT, 'api': 'harness2.core.schedule.run_domain',
            'python': '.'.join(map(str, sys.version_info[:3])), 'result': result,
            'upstreamModuleHashes': upstream_bindings,
            'demoReport': _bindings(output, ['demo.json']),
            'scope': 'Credential-free upstream arithmetic demo only; no Warlock improvement measured.',
            'acceptanceAuthority': False, 'autoAdopt': False, 'originalAcceptance': False, 'nativeAcceptance': False}


def _write_new(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    freezing = commands.add_parser('freeze')
    freezing.add_argument('--context-root', type=Path, required=True)
    freezing.add_argument('--request', required=True)
    freezing.add_argument('--harness', required=True)
    freezing.add_argument('--output', required=True)
    comparison = commands.add_parser('compare')
    for field in ('baseline', 'candidate', 'baseline-observation', 'candidate-observation', 'output'):
        comparison.add_argument('--' + field, type=Path, required=True)
    comparison.add_argument('--completed-candidate-sha', required=True)
    probe = commands.add_parser('upstream-probe')
    probe.add_argument('--upstream-root', type=Path, required=True)
    probe.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'freeze':
            root = _root(args.context_root)
            result = freeze(root, read_json(_file(root, args.request)), read_json(_file(root, args.harness)))
            require(Path(args.output).name == args.output and args.output not in ('.', '..'), 'output must be a new context filename')
            _write_new(root / args.output, result)
        elif args.command == 'compare':
            result = compare(read_json(args.baseline), read_json(args.candidate),
                             read_json(args.baseline_observation), read_json(args.candidate_observation), args.completed_candidate_sha)
            _root(args.output.parent)
            _write_new(args.output, result)
        else:
            result = upstream_probe(args.upstream_root, args.output_root)
            _write_new(args.output_root / 'adapter-probe-receipt.json', result)
        print(json.dumps({'taskId': result.get('taskId'), 'acceptanceAuthority': False, 'status': 'recorded'}))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({'error': str(error), 'acceptanceAuthority': False}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

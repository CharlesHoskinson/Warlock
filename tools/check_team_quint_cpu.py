#!/usr/bin/env python3
"""Five fixed team model pairs, private sampled TypeScript Quint checks only."""
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import time
from pathlib import Path

from qa_cpu import TEAM_QUINT_PAIRS, team_quint_inputs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base  # ty: ignore[import-not-found]

TOOL = ROOT / 'tools/team-quint-toolchain.json'
NODE = Path('/home/hoskinson/.local/share/mise/installs/node/26.13.0/bin/node')
QUINT = NODE.parent.parent / 'lib/node_modules/@informalsystems/quint'
SYSTEM = Path('/home/hoskinson/.local/share/warlock-toolchain/system-build-inputs.json')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_json(path):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('Expected regular model input: ' + str(path))
    return json.loads(path.read_text())


def verify_tools():
    packet = read_json(TOOL)
    files = {str(NODE), str(SYSTEM), '/etc/ld.so.cache', '/etc/passwd', '/etc/group', '/etc/nsswitch.conf'}
    if (packet['schema'] != 1 or packet['profile'] != 'team-quint-arm64-20261105'
            or packet['quint'] != str(QUINT) or packet['node'] != str(NODE)
            or packet['version'] != '0.32.0' or packet['backend'] != 'typescript'
            or set(packet['files']) != files
            or packet['historicalParent'] != {'path': 'tools/quint-toolchain.json',
                'sha256': digest(ROOT / 'tools/quint-toolchain.json')}):
        raise RuntimeError('Unexpected team Quint toolchain')
    for name, sha in packet['files'].items():
        path = Path(name)
        if path.is_symlink() or digest(path) != sha:
            raise RuntimeError('Team Quint external input changed: ' + name)
    rows = {}
    for path in sorted(QUINT.rglob('*')):
        if path.is_symlink():
            if not path.resolve().is_relative_to(QUINT):
                raise RuntimeError('Quint package symlink escapes its locked tree')
            rows[str(path.relative_to(QUINT))] = {'link': os.readlink(path)}
        elif path.is_file():
            rows[str(path.relative_to(QUINT))] = {'sha256': digest(path), 'mode': stat.S_IMODE(path.stat().st_mode)}
        elif not path.is_dir():
            raise RuntimeError('Special file in Quint package')
    tree = {'files': len(rows), 'sha256': hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}
    if tree != packet['tree'] or read_json(QUINT / 'package.json')['version'] != '0.32.0':
        raise RuntimeError('Complete local Quint tree differs')
    for name, expected in read_json(SYSTEM)['files'].items():
        if not name.startswith(('/usr/bin/', '/usr/lib/', '/usr/include/')):
            raise RuntimeError('Unexpected system tool input')
        path = Path(name)
        actual = ({'link': os.readlink(path)} if path.is_symlink() else
                  {'sha256': digest(path), 'mode': stat.S_IMODE(path.stat().st_mode)})
        if actual != expected:
            raise RuntimeError('System model input differs: ' + name)
    return packet


TEST_SELECTOR_LIMIT = 64


def validate_selector_admission(plan, declared_tests=None):
    """Pure selector layer shared by real admission and fixed startup controls."""
    names = [*plan['tests'], *plan['invariants'], *plan['witnesses']]
    if any(not isinstance(name, str) or not re.fullmatch('[A-Za-z][A-Za-z0-9_]*', name) for name in names):
        raise RuntimeError('Model selectors must be simple declared identifiers')
    for key in ('tests', 'invariants', 'witnesses'):
        limit = TEST_SELECTOR_LIMIT if key == 'tests' else 32
        if not 1 <= len(plan[key]) <= limit or len(set(plan[key])) != len(plan[key]):
            raise RuntimeError('Empty, repeated or excessive model selectors')
    if declared_tests is not None and sorted(declared_tests) != sorted(plan['tests']):
        raise RuntimeError('Named model/test declarations do not match the reviewed plan')


def selector_admission_controls():
    """Fixed in-memory admission checks, never synthetic Quint files/runs."""
    def selectors(tests=3, invariants=1, witnesses=1):
        return {'tests': ['Test' + str(n) for n in range(tests)],
                'invariants': ['Invariant' + str(n) for n in range(invariants)],
                'witnesses': ['Witness' + str(n) for n in range(witnesses)]}
    excessive = 'Empty, repeated or excessive model selectors'
    mismatch = 'Named model/test declarations do not match the reviewed plan'
    cases = []
    for count in (49, 40, 36, 64):
        plan = selectors(tests=count)
        cases.append(('complete-' + str(count), plan, list(plan['tests']), None))
    plan = selectors(tests=65)
    cases.append(('tests-65-rejected', plan, list(plan['tests']), excessive))
    for key in ('invariants', 'witnesses'):
        plan = selectors(**{key: 33})
        cases.append((key + '-33-rejected', plan, list(plan['tests']), excessive))
        plan = selectors(**{key: 32})
        cases.append((key + '-32-admitted', plan, list(plan['tests']), None))
    plan = selectors()
    declared = list(plan['tests'])
    plan['tests'].pop()
    cases.append(('omitted-declared-test-rejected', plan, declared, mismatch))
    plan = selectors()
    declared = list(plan['tests'])
    plan['tests'].append(plan['tests'][0])
    cases.append(('duplicate-test-rejected', plan, declared, excessive))
    plan = selectors()
    declared = list(plan['tests'])
    plan['tests'][-1] = 'UndeclaredTest'
    cases.append(('undeclared-test-rejected', plan, declared, mismatch))
    plan = selectors()
    declared = list(plan['tests'])
    plan['tests'][-1] = 'Test2|Injected'
    cases.append(('injected-name-rejected', plan, declared, 'Model selectors must be simple declared identifiers'))
    rows = []
    for label, plan, declared, expected_error in cases:
        observed_error = None
        error_type = None
        try:
            validate_selector_admission(plan, declared)
        except Exception as error:  # Preserve unexpected errors; they cannot count as intended rejection.
            observed_error, error_type = str(error), type(error).__name__
        passed = observed_error == expected_error and (expected_error is None or error_type == 'RuntimeError')
        rows.append({'name': label, 'passed': passed, 'expectedError': expected_error,
                     'observedError': observed_error, 'errorType': error_type,
                     'tests': len(plan['tests']), 'declaredTests': len(declared),
                     'invariants': len(plan['invariants']), 'witnesses': len(plan['witnesses'])})
    return {'schema': 1, 'passed': all(row['passed'] for row in rows), 'controls': rows,
            'limits': {'tests': TEST_SELECTOR_LIMIT, 'invariants': 32, 'witnesses': 32},
            'scope': 'Pure selector admission only; no synthetic models or Quint commands',
            'modelAcceptance': False, 'nativeAcceptance': False}


def validate_plan(plan, pair, inputs):
    if (set(plan) != {'schema', 'pair', 'sourceBase', 'modelModule', 'testModule', 'tests', 'invariants',
                     'witnesses', 'seeds', 'maxSamples', 'maxSteps'}
            or plan['schema'] != 1 or plan['pair'] != pair
            or not re.fullmatch('[0-9a-f]{40}', plan['sourceBase'])
            or plan['seeds'] != [20261105, 20261106]
            or type(plan['maxSamples']) is not int or plan['maxSamples'] != 10000
            or type(plan['maxSteps']) is not int or plan['maxSteps'] not in (30, 50, 80)):
        raise RuntimeError('Unexpected reviewed fixed model plan')
    symbols = [plan['modelModule'], plan['testModule'], *plan['tests'], *plan['invariants'], *plan['witnesses']]
    if any(not isinstance(name, str) or not re.fullmatch('[A-Za-z][A-Za-z0-9_]*', name) for name in symbols):
        raise RuntimeError('Model selectors must be simple declared identifiers')
    validate_selector_admission(plan)
    model = inputs / ('tea004-preview-' + pair + '.qnt')
    tests = inputs / ('tea004-preview-' + pair + '_test.qnt')
    texts = [model.read_text(), tests.read_text()]
    validate_selector_admission(plan, re.findall(r'\brun\s+(\w+)\s*=', texts[1]))
    if (re.findall(r'\bmodule\s+(\w+)\s*\{', texts[0]) != [plan['modelModule']]
            or re.findall(r'\bmodule\s+(\w+)\s*\{', texts[1]) != [plan['testModule']]
            or sorted(re.findall(r'\brun\s+(\w+)\s*=', texts[1])) != sorted(plan['tests'])):
        raise RuntimeError('Named model/test declarations do not match the reviewed plan')
    imports = re.findall(r'\bfrom\s+[\"\x27]([^\"\x27]+)[\"\x27]', '\n'.join(texts))
    if imports != ['./tea004-preview-' + pair]:
        raise RuntimeError('Only this fixed pair may be imported')
    for name in [*plan['invariants'], *plan['witnesses']]:
        if not re.search(r'\bval\s+' + re.escape(name) + r'\b', texts[0]):
            raise RuntimeError('Missing declared model invariant: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for pair in TEAM_QUINT_PAIRS:
        modes.add_argument('--' + pair, action='store_true')
    parser.add_argument('--tests-only', action='store_true')
    parser.add_argument('--inside-private', type=Path)
    args = parser.parse_args()
    pair = next(pair for pair in TEAM_QUINT_PAIRS if getattr(args, pair))
    scope = require_qa_scope()
    if args.inside_private is not None:
        (Path('/run/user') / str(os.getuid())).mkdir(parents=True, mode=0o700)
    runtime_base()
    inputs = ROOT / '.warlock-contributor/team-quint-inputs' / pair
    plan = read_json(inputs / 'plan.json')
    controls = selector_admission_controls()
    tools = verify_tools()
    sources = {name: digest(ROOT / name) for name in sorted(team_quint_inputs(ROOT, pair))}
    if args.inside_private is None:
        output = ROOT / '.warlock-contributor' / ('team-quint-' + pair + '-' + str(time.time_ns()))
        output.mkdir(mode=0o700)
        report = {'schema': 1, 'pair': pair, 'passed': False, 'plan': plan, 'sourceHashes': sources,
                  'protectedScope': scope, 'commands': [], 'phase': 'tests-only' if args.tests_only else 'full',
                  'scope': 'Isolated draft model typecheck, named tests and sampled traces only',
                  'exhaustiveProof': False, 'implementationAcceptance': False, 'nativeAcceptance': False,
                  'originalAcceptance': False, 'releaseAccepted': False, 'toolchainSHA256': digest(TOOL),
                  'selectorAdmissionControls': controls}
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        command = ['/usr/bin/bwrap', '--die-with-parent', '--unshare-net', '--unshare-pid',
                   '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
                   '--symlink', 'usr/lib', '/lib64', '--dir', '/etc', '--proc', '/proc', '--dev', '/dev',
                   '--tmpfs', '/tmp', '--tmpfs', '/run']
        mounts = {str(ROOT / name) for name in sources} | set(tools['files']) | {str(QUINT)}
        for name in sorted(mounts):
            command += ['--ro-bind', name, name]
        command += ['--bind', str(output), str(output), '--chdir', str(inputs), '--', sys.executable, '-B',
                    str(Path(__file__).resolve()), '--' + pair, '--inside-private', str(output)]
        if args.tests_only:
            command.append('--tests-only')
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'NO_COLOR': '1',
               'PYTHONDONTWRITEBYTECODE': '1', 'HOME': str(output / 'home'), 'TMPDIR': '/tmp'}
        try:
            if not controls['passed']:
                raise RuntimeError('Fixed selector admission startup controls failed; no Quint invocation')
            validate_plan(plan, pair, inputs)
            child = subprocess.run(command, cwd=ROOT, env=env, timeout=3500, check=False)
            report = read_json(output / 'report.json')
            verify_tools()
            if any(digest(ROOT / name) != sha for name, sha in sources.items()):
                raise RuntimeError('Reviewed model/tool sources changed during execution')
            if child.returncode or not report['passed']:
                raise RuntimeError('Private team model check failed; retained evidence')
        except Exception as error:  # noqa: BLE001 -- retain failure evidence
            report.update(passed=False, error=str(error))
        finally:
            (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps({'passed': report['passed'], 'report': str(output / 'report.json')}), flush=True)
        return 0 if report['passed'] else 1

    output = args.inside_private
    if output.parent != ROOT / '.warlock-contributor' or not re.fullmatch('team-quint-' + pair + '-[0-9]+', output.name) or output.is_symlink():
        raise RuntimeError('Unexpected private model output')
    report = read_json(output / 'report.json')
    if report['sourceHashes'] != sources or report['plan'] != plan:
        raise RuntimeError('Model source/plan changed before private execution')
    logs = output / 'logs'
    traces = output / 'traces'
    logs.mkdir(mode=0o700)
    traces.mkdir(mode=0o700)
    cli = [str(NODE), str(QUINT / 'dist/src/cli.js')]

    def run(label, arguments, expected, selector=None):
        result_path = logs / (label + '.json')
        command = cli + arguments + ['--out=' + str(result_path)]
        previous_traces = set(traces.glob('*.itf.json'))
        with (logs / (label + '.stdout')).open('wb') as stdout, (logs / (label + '.stderr')).open('wb') as stderr:
            child = subprocess.run(command, cwd=inputs, env=os.environ, stdout=stdout, stderr=stderr,
                                   timeout=180, check=False)
        row = {'label': label, 'argv': command, 'exit': child.returncode, 'expected': expected,
               'json': str(result_path), 'selector': selector}
        report['commands'].append(row)
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        result = read_json(result_path)
        valid = result.get('errors') == [] and child.returncode == (1 if expected == 'reaching-violation' else 0)
        if expected == 'named-test':
            valid = valid and result.get('passed') == [selector] and result.get('failed') == [] and result.get('ignored') == []
        elif expected in ('sampled-safety', 'reaching-violation'):
            valid = valid and result.get('status') == ('violation' if expected == 'reaching-violation' else 'ok')
            valid = valid and isinstance(result.get('trace'), list) and bool(result['trace'])
        row.update(valid=bool(valid), status=result.get('status'), resultSHA256=digest(result_path))
        if expected == 'reaching-violation' and valid:
            generated = set(traces.glob('*.itf.json')) - previous_traces
            if len(generated) != 1:
                raise RuntimeError(label + ' requires exactly one new ITF counterexample')
            trace_file = generated.pop()
            info = trace_file.lstat()
            if (not stat.S_ISREG(info.st_mode) or trace_file.is_symlink()
                    or not 0 < info.st_size <= 16 * 1024 * 1024):
                raise RuntimeError(label + ' has no bounded regular ITF counterexample')
            itf = read_json(trace_file)
            states = itf.get('states')
            variables = itf.get('vars')
            metadata = itf.get('#meta', {})
            if (metadata.get('format') != 'ITF' or metadata.get('status') != 'violation'
                    or metadata.get('source') != 'tea004-preview-' + pair + '.qnt'
                    or not isinstance(states, list) or len(states) != len(result['trace'])
                    or not 1 <= len(states) <= plan['maxSteps'] + 1
                    or not isinstance(variables, list) or not variables
                    or any(not isinstance(name, str) for name in variables)
                    or any(not isinstance(state, dict) or not set(variables).issubset(state)
                           for state in states)):
                raise RuntimeError(label + ' ITF trace does not match the selected result')
            row['classification'] = 'Counterexample to exactly the selected negated reachability predicate'
            row['traceStates'] = len(result['trace'])
            row['itf'] = {'path': str(trace_file), 'sha256': digest(trace_file),
                          'bytes': info.st_size, 'states': len(states), 'predicate': selector}
        if not valid:
            raise RuntimeError(label + ' failed exact result classification; retain trace and diagnostics')

    try:
        report['selectorAdmissionControls'] = controls
        if not controls['passed']:
            raise RuntimeError('Fixed selector admission startup controls failed; no Quint invocation')
        validate_plan(plan, pair, inputs)
        model = 'tea004-preview-' + pair + '.qnt'
        tests = 'tea004-preview-' + pair + '_test.qnt'
        run('typecheck-model', ['typecheck', model], 'typecheck')
        run('typecheck-tests', ['typecheck', tests], 'typecheck')
        for seed in plan['seeds']:
            for name in plan['tests']:
                run('test-' + name + '-' + str(seed), ['test', tests, '--main=' + plan['testModule'],
                    '--match=^' + name + '$', '--seed=' + str(seed), '--max-samples=1',
                    '--backend=typescript', '--verbosity=1', '--out-itf=' +
                    str(traces / ('test-' + str(seed) + '-{test}-{seq}.itf.json'))], 'named-test', name)
        if not args.tests_only:
            for seed in plan['seeds']:
                base = ['run', model, '--main=' + plan['modelModule'], '--seed=' + str(seed),
                        '--max-samples=' + str(plan['maxSamples']), '--max-steps=' + str(plan['maxSteps']),
                        '--backend=typescript', '--verbosity=1']
                run('safety-' + str(seed), base + ['--invariants', *plan['invariants']], 'sampled-safety')
                for name in plan['witnesses']:
                    label = 'witness-' + name + '-' + str(seed)
                    run(label, base + ['--invariant=' + name, '--out-itf=' + str(traces / (label + '-{seq}.itf.json'))],
                        'reaching-violation', name)
        verify_tools()
        if any(digest(ROOT / name) != sha for name, sha in sources.items()):
            raise RuntimeError('Reviewed model/tool source changed during execution')
        report.update(passed=True, fullModelCampaignCompleted=not args.tests_only)
    except Exception as error:  # noqa: BLE001 -- preserve unexpected results without relabeling witness failures
        report.update(passed=False, error=str(error))
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

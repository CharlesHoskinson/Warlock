#!/usr/bin/env python3
"""Protected compiled-worker protocol fixture; not native clock proof."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO = Path('/home/charles/Warlock')
PRODUCT = REPO / 'implementation/warlock'
HELD = REPO / 'implementation/warlock-preview-provider-v143'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope

PINS = {
    'src/PreviewLifecycle.elm': '232ebe2e823a4f9b07444f9afaccd98cdc3de9a592ff220d9975a64952dacf24',
    'src/PreviewIdentity.elm': '262240e59eed37d362f921a4e7e89d0bb23c8b0f84fb39f0fddc29faaa3de3b5',
    'src/UInt64.elm': '0c32ee015c1882d9d754d9dcda5a454e8a1d71f85d3bbd60d9280dd564531baa',
    'src/PreviewVisual.elm': '5c285bd8c6fde00b4e1082edfd10e59e281264a4f45b15cea9b5ce0920dd039a',
    'elm.json': '48651a8950f9d4df5502f541d0262f83c579b54fe0dcd623a186992cb72d8208',
}
MANIFEST_HASH = 'fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv, cwd, env, timeout):
    result = subprocess.run([str(x) for x in argv], cwd=cwd, env=env,
                            text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(json.dumps({'argv': [str(x) for x in argv], 'exit': result.returncode,
                                       'stdout': result.stdout, 'stderr': result.stderr}))
    return result


def main():
    scope_evidence = require_qa_scope()
    assert sha(HELD / 'qa/toolchain.json') == MANIFEST_HASH
    toolchain = json.loads((HELD / 'qa/toolchain.json').read_text())
    assert len(toolchain['heldFiles']) == 111
    def verify_toolchain():
        for name, expected in toolchain['heldFiles'].items():
            path = HELD / name
            assert path.is_file() and path.stat().st_size == expected['size'] and sha(path) == expected['sha256'], name
    verify_toolchain()
    compiler = HELD / toolchain['compiler']
    assert sha(compiler) == toolchain['compilerSHA256']
    node = shutil.which('node')
    if not node:
        raise RuntimeError('node unavailable')
    for name, digest in PINS.items():
        assert sha(PRODUCT / name) == digest, name
    sources = {str(p.relative_to(REPO)): sha(p) for p in sorted((PRODUCT / 'src').rglob('*.elm'))}
    sources.update({str(p): sha(p) for p in (PRODUCT / 'elm.json', HERE / 'DeadlineBridgeReplay.elm',
                                               HERE / 'deadline-bridge-replay.cjs', HERE / 'check-deadline-bridge.py')})
    first, second = '9007199254740993', '9007199254740994'
    now = '9007197254740994'
    binding = {'lifetime': first, 'session': '1', 'frontend': '1'}
    context = {'lifetime': first, 'incarnation': first, 'output': '1', 'privacy': '1',
               'rendering': '1', 'scene': '1', 'content': '1'}
    def packet(deadline, scope_now=now, clock_now=None):
        return {'scope': {'binding': copy.deepcopy(binding), 'context': copy.deepcopy(context),
                          'observation': '1', 'clock': first, 'now': scope_now,
                          'present': True, 'sourceLive': True, 'locked': False, 'gpuReady': True},
                'request': {'kind': 'request', 'trigger': {'binding': copy.deepcopy(binding),
                            'context': copy.deepcopy(context), 'origin': '1', 'clock': first, 'deadline': deadline}},
                'clockEvent': {'kind': 'clock', 'binding': copy.deepcopy(binding), 'clock': first,
                               'now': scope_now if clock_now is None else clock_now}}
    assert int(first) > 2**53 and int(second) == int(first) + 1
    assert int(first) - 9007197254740993 == 2_000_000_000
    assert int(second) - 9007197254740994 == 2_000_000_000
    assert 9007201254740993 - int(first) == 2_000_000_000
    assert 9007201254740994 - int(second) == 2_000_000_000
    cases, expectations = [], []
    def add(name, case, expected, stage=None):
        cases.append(case); expectations.append((name, expected, stage))
    add('adjacent-deadline-first', packet(first, '9007197254740993'), 'acquire')
    add('adjacent-deadline-second', packet(second, '9007197254740994'), 'acquire')
    add('deadline-equal-scope-now', packet(second, second), 'none')
    add('deadline-expired-at-scope-now', packet(first, second), 'none')
    add('clock-reaches-original-deadline', packet(second, now, second), 'cancel')
    # This interval is derived from the current native producer policy; it is fixture data, not a native-clock observation.
    add('native-policy-interval-fixture-first', packet('9007201254740993', first), 'acquire')
    add('native-policy-interval-fixture-second', packet('9007201254740994', second), 'acquire')
    paths = [(['scope', 'now'], 'scope'), (['scope', 'clock'], 'scope'),
             (['scope', 'observation'], 'scope'), (['request', 'trigger', 'deadline'], 'request'),
             (['request', 'trigger', 'clock'], 'request'), (['request', 'trigger', 'origin'], 'request'),
             (['clockEvent', 'now'], 'clockEvent'), (['clockEvent', 'clock'], 'clockEvent')]
    for base, stage in [(['scope', 'binding'], 'scope'), (['request', 'trigger', 'binding'], 'request'),
                        (['clockEvent', 'binding'], 'clockEvent')]:
        paths.extend((base + [key], stage) for key in binding)
    for base, stage in [(['scope', 'context'], 'scope'), (['request', 'trigger', 'context'], 'request')]:
        paths.extend((base + [key], stage) for key in context)
    def numeric_baseline():
        case = packet(second)
        # Keep cross-field lifetime equality valid even under hypothetical numeric coercion.
        for group in (case['scope'], case['request']['trigger']):
            group['binding']['lifetime'] = '1'
            group['context']['lifetime'] = '1'
        case['clockEvent']['binding']['lifetime'] = '1'
        return case
    add('numeric-baseline-valid-control', numeric_baseline(), 'acquire')
    for path, stage in paths:
        case = numeric_baseline()
        target = case
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = int(target[path[-1]])
        add('numeric-' + '.'.join(path), case, 'reject', stage)
    with tempfile.TemporaryDirectory(prefix='warlock-rev007-deadline-') as temp:
        root = Path(temp); workspace = root / 'workspace'; workspace.mkdir()
        (workspace / 'src').symlink_to(PRODUCT / 'src', target_is_directory=True)
        (workspace / 'qa').mkdir()
        shutil.copyfile(HERE / 'DeadlineBridgeReplay.elm', workspace / 'qa/DeadlineBridgeReplay.elm')
        info = json.loads((PRODUCT / 'elm.json').read_text()); info['source-directories'] = ['src', 'qa']
        (workspace / 'elm.json').write_text(json.dumps(info))
        elmhome = root / 'elm-home'; shutil.copytree(HELD / toolchain['elmHome'], elmhome)
        env = {**os.environ, 'ELM_HOME': str(elmhome), 'PYTHONDONTWRITEBYTECODE': '1'}
        compiled = root / 'deadline.js'; cases_path = root / 'cases.json'
        cases_path.write_text(json.dumps(cases, separators=(',', ':')))
        compile_result = run([compiler, 'make', 'qa/DeadlineBridgeReplay.elm', '--output=' + str(compiled)], workspace, env, 240)
        node_result = run([node, HERE / 'deadline-bridge-replay.cjs', compiled, cases_path], workspace, env, 10)
        outputs = json.loads(node_result.stdout)
        assert len(outputs) == len(cases)
        receipts = []
        for case, (name, expected, stage), output in zip(cases, expectations, outputs):
            if expected == 'reject':
                assert output == {'accepted': False, 'stage': stage, 'commands': [], 'clockCommands': []}, (name, output)
            else:
                assert output['accepted'] and output['stage'] == 'decoded', (name, output)
                commands, clock_commands = output['commands'], output['clockCommands']
                if expected == 'none':
                    assert commands == [] and clock_commands == [], (name, output)
                else:
                    assert len(commands) == 1 and commands[0]['kind'] == 'acquire', (name, output)
                    job = commands[0]['job']; trigger = case['request']['trigger']
                    assert job == {'binding': trigger['binding'], 'context': trigger['context'],
                                   'request': '1', 'origin': trigger['origin'], 'clock': trigger['clock'],
                                   'deadline': trigger['deadline']}, (name, job)
                    if expected == 'cancel':
                        assert clock_commands == [{'kind': 'cancel', 'job': job}], (name, output)
                    else:
                        assert clock_commands == [], (name, output)
            receipts.append({'name': name, 'expected': expected, 'passed': True, 'input': case, 'output': output})
        for name, digest in sources.items():
            path = Path(name) if Path(name).is_absolute() else REPO / name
            assert sha(path) == digest, 'source changed: ' + name
        assert sha(HELD / 'qa/toolchain.json') == MANIFEST_HASH
        verify_toolchain()
        result = {'passed': True, 'requirement': 'ELM-REV-007', 'receipts': receipts,
                  'scope': 'Compiled Elm worker ports: production scopeDecoder/eventDecoder, init/open/request/clock/update and encodeCommands; JS JSON serialization. Fixture times are inputs, not native clock observations.',
                  'sourceHashes': sources, 'casesJSONSHA256': sha(cases_path), 'toolchainManifestSHA256': MANIFEST_HASH,
                  'compilerSHA256': sha(compiler), 'node': str(Path(node).resolve()),
                  'nodeSHA256': sha(Path(node).resolve()), 'compiledSHA256': sha(compiled), 'scopeEvidence': scope_evidence,
                  'commands': [{'argv': [str(compiler), 'make', 'qa/DeadlineBridgeReplay.elm', '--output=' + str(compiled)], 'exit': compile_result.returncode, 'stdout': compile_result.stdout, 'stderr': compile_result.stderr},
                               {'argv': [node, str(HERE / 'deadline-bridge-replay.cjs'), str(compiled), str(cases_path)], 'exit': node_result.returncode, 'stderr': node_result.stderr}],
                  'limits': ['No native clock/start-event/producer/wire execution or Main/adapter transport', 'No acceptance; fixture watchdog is not the native absolute deadline']}
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

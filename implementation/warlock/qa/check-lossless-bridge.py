#!/usr/bin/env python3
"""Protected compiled Elm-port / JS / Python protocol fixture for REV-007.

Runs actual product Elm decoders and encoder, not Main's Browser.element or a
native plugin. Native counter correspondence and whole-requirement review are
separate. No production source, cache or deadline is changed.
"""
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
sys.path.insert(0, str(PRODUCT / 'adapter'))
from endpoint import canonical, Refused


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv, cwd, env, timeout):
    p = subprocess.run([str(x) for x in argv], cwd=cwd, env=env,
                       text=True, capture_output=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError(json.dumps({'argv': [str(x) for x in argv],
                                       'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}))
    return p


def main():
    scope = require_qa_scope()
    toolchain = json.loads((HELD / 'qa/toolchain.json').read_text())
    assert len(toolchain['heldFiles']) == 111
    for name, expected in toolchain['heldFiles'].items():
        path = HELD / name
        assert path.is_file() and path.stat().st_size == expected['size'] and sha(path) == expected['sha256'], name
    compiler = HELD / toolchain['compiler']
    assert sha(compiler) == toolchain['compilerSHA256']
    node = shutil.which('node')
    if not node:
        raise RuntimeError('node is unavailable')
    sources = {str(p.relative_to(REPO)): sha(p) for p in sorted((PRODUCT / 'src').rglob('*.elm'))}
    for path in (PRODUCT / 'elm.json', PRODUCT / 'adapter/endpoint.py', HERE / 'LosslessBridgeReplay.elm', HERE / 'lossless-bridge-replay.cjs', HERE / 'check-lossless-bridge.py'):
        sources[str(path)] = sha(path)
    ids = ['9007199254740993', '9007199254740994']
    assert int(ids[0]) > 2**53 and int(ids[1]) == int(ids[0]) + 1
    def scene():
        return {'revision': '1', 'focused': None, 'windows': [
            {'incarnation': value, 'label': 'window-' + value, 'minimized': False,
             'owner': None, 'application': 'fixture', 'available': True} for value in ids]}
    def intent(identity):
        return {'request': '1', 'generation': '1', 'incarnation': identity,
                'operation': 'activate', 'context': {'lifetime': '1', 'epoch': '1', 'output': '1', 'revision': '1'}}
    cases = [{'intent': intent(value), 'scene': scene()} for value in ids]
    names = ['positive-first', 'positive-second']
    # JSON numeric values must be rejected even if JavaScript rounded their bits.
    for field in ('request', 'generation', 'incarnation'):
        row = {'intent': intent(ids[0]), 'scene': scene()}
        row['intent'][field] = int(ids[0])
        cases.append(row); names.append('numeric-intent-' + field)
    for field in ('lifetime', 'epoch', 'output', 'revision'):
        row = {'intent': intent(ids[0]), 'scene': scene()}
        row['intent']['context'][field] = int(ids[0])
        cases.append(row); names.append('numeric-context-' + field)
    row = {'intent': intent(ids[0]), 'scene': scene()}
    row['scene']['windows'][0]['incarnation'] = int(ids[0])
    cases.append(row); names.append('numeric-scene-incarnation')
    row = {'intent': intent(ids[0]), 'scene': scene()}
    row['scene']['revision'] = int(ids[0])
    cases.append(row); names.append('numeric-scene-revision')
    with tempfile.TemporaryDirectory(prefix='warlock-rev007-') as temp:
        root = Path(temp); workspace = root / 'workspace'; workspace.mkdir()
        # Link immutable current source for reading; elm-stuff remains in workspace.
        (workspace / 'src').symlink_to(PRODUCT / 'src', target_is_directory=True)
        (workspace / 'qa').mkdir()
        shutil.copyfile(HERE / 'LosslessBridgeReplay.elm', workspace / 'qa/LosslessBridgeReplay.elm')
        info = json.loads((PRODUCT / 'elm.json').read_text())
        info['source-directories'] = ['src', 'qa']
        (workspace / 'elm.json').write_text(json.dumps(info))
        elmhome = root / 'elm-home'
        shutil.copytree(HELD / toolchain['elmHome'], elmhome)
        env = {**os.environ, 'ELM_HOME': str(elmhome), 'PYTHONDONTWRITEBYTECODE': '1'}
        compiled = root / 'lossless.js'; cases_path = root / 'cases.json'
        cases_path.write_text(json.dumps(cases, separators=(',', ':')))
        compile_result = run([compiler, 'make', 'qa/LosslessBridgeReplay.elm', '--output=' + str(compiled)], workspace, env, 240)
        node_result = run([node, HERE / 'lossless-bridge-replay.cjs', compiled, cases_path], workspace, env, 10)
        outputs = json.loads(node_result.stdout)
        assert len(outputs) == len(cases)
        for i, identity in enumerate(ids):
            value = outputs[i]
            assert value['intentAccepted'] and value['sceneAccepted']
            assert value['intent'] == intent(identity) and value['scene'] == ids
            assert canonical(value['intent']['incarnation']) == identity
        for i, name in enumerate(names[2:], 2):
            value = outputs[i]
            if name in ('numeric-scene-incarnation', 'numeric-scene-revision'):
                assert value['intentAccepted'] and not value['sceneAccepted'] and value['scene'] is None
            else:
                assert not value['intentAccepted'] and value['intent'] is None and value['sceneAccepted']
            try:
                canonical(int(ids[0]))
            except Refused:
                pass
            else:
                raise AssertionError('Python canonical accepted numeric identity')
        for name, digest in sources.items():
            path = Path(name) if Path(name).is_absolute() else REPO / name
            assert sha(path) == digest, 'source changed: ' + name
        for name, expected in toolchain['heldFiles'].items():
            assert sha(HELD / name) == expected['sha256'], 'toolchain changed: ' + name
        result = {'passed': True, 'requirement': 'ELM-REV-007', 'scenario': 'revision-007',
                  'scope': 'Compiled Platform.worker real Elm ports with product ActionProjection and Effects decoders/encoder, Node JSON transport and Python endpoint.canonical. Not production Main/adapter.js or native authority parser.',
                  'ids': ids, 'cases': names, 'outputs': outputs, 'sourceHashes': sources,
                  'toolchainManifestSHA256': sha(HELD / 'qa/toolchain.json'), 'compilerSHA256': sha(compiler),
                  'node': str(Path(node).resolve()), 'nodeSHA256': sha(Path(node).resolve()),
                  'compiledSHA256': sha(compiled), 'scopeEvidence': scope,
                  'commands': [{'argv': [str(compiler), 'make', 'qa/LosslessBridgeReplay.elm', '--output=' + str(compiled)], 'exit': compile_result.returncode, 'stdout': compile_result.stdout, 'stderr': compile_result.stderr},
                               {'argv': [node, str(HERE / 'lossless-bridge-replay.cjs'), str(compiled), str(cases_path)], 'exit': node_result.returncode, 'stderr': node_result.stderr}],
                  'missing': ['Main.nativeEvents / production adapter.js correspondence', 'Native authority counter parser and actual native-generated source identity', 'Absolute deadline field and original native deadline; 3000ms Node watchdog matches existing feedback-replay.js and is only this fixture timeout', 'Independent review and original requirement acceptance']}
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

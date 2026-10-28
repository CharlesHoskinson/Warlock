#!/usr/bin/env python3
"""Compile the current Desktop three-family replay in a new private QA directory."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
HELD = REPO / 'implementation/warlock-preview-provider-v143'
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_directory(value):
    path = Path(value)
    if not path.is_absolute() or '..' in path.parts or path == Path('/'):
        raise ValueError('output must be an absolute new path without ..')
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError('output path contains a symlink')
    if path.exists() or not path.parent.is_dir() or path.parent.stat().st_uid != os.getuid():
        raise ValueError('output must be absent with an owned existing parent')
    resolved = path.resolve()
    protected = (REPO.resolve(), ROOT.resolve(), HELD.resolve(), (ROOT / 'src').resolve())
    if any(resolved == base or resolved.is_relative_to(base) for base in protected):
        raise ValueError('output cannot be in the source or frozen tree')
    path.mkdir(mode=0o700)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-owned', required=True)
    args = parser.parse_args()
    require_qa_scope()
    out = output_directory(args.output_owned)
    toolpath = HELD / 'qa/toolchain.py'
    spec = importlib.util.spec_from_file_location('held_toolchain', toolpath)
    toolchain = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(toolchain)
    pinned = toolchain.verify()
    compiler = HELD / pinned['compiler']
    if digest(compiler) != pinned['compilerSHA256']:
        raise ValueError('compiler hash mismatch')
    sources = sorted((ROOT / 'src').glob('*.elm')) + [ROOT / 'elm.json', ROOT / 'qa/NativePointerFixture.elm', ROOT / 'qa/ThreeGroupReplay.elm', ROOT / 'qa/feedback-replay.js', toolpath, HELD / 'qa/toolchain.json']
    before = {str(p): digest(p) for p in sources}
    workspace = out / 'workspace'
    workspace.mkdir()
    (workspace / 'src').symlink_to(ROOT / 'src', target_is_directory=True)
    (workspace / 'qa').mkdir()
    for name in ('NativePointerFixture.elm', 'ThreeGroupReplay.elm'):
        (workspace / 'qa' / name).symlink_to(ROOT / 'qa' / name)
    project = json.loads((ROOT / 'elm.json').read_text())
    project['source-directories'] = ['src', 'qa']
    (workspace / 'elm.json').write_text(json.dumps(project))
    shutil.copytree(HELD / pinned['elmHome'], out / 'elm-home')
    env = {**os.environ, 'ELM_HOME': str(out / 'elm-home'), 'GHCRTS': '-N1', 'SOURCE_DATE_EPOCH': '0', 'TZ': 'UTC', 'PYTHONDONTWRITEBYTECODE': '1'}
    node = shutil.which('node')
    if not node:
        raise RuntimeError('node executable unavailable')
    runner = (ROOT / 'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay', 'Elm.ThreeGroupReplay')
    (out / 'replay-run.cjs').write_text(runner)
    commands = []
    def run(argv):
        result = subprocess.run([str(x) for x in argv], cwd=workspace, env=env, capture_output=True, text=True, timeout=120)
        commands.append({'argv': [str(x) for x in argv], 'exitCode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        if result.returncode:
            raise RuntimeError('replay subprocess failed; see commands.json')
    run([compiler, 'make', 'qa/ThreeGroupReplay.elm', '--output=' + str(out / 'replay.js')])
    run([node, out / 'replay-run.cjs', out / 'replay.js', out / 'result.json'])
    result = json.loads((out / 'result.json').read_text())
    expected = {'pickerOpensWithoutEffect', 'threeDistinctSelectableRoots', 'staleScopeDoesNotChoose', 'selectionRequestsFreshProjection', 'exactOneSelectedActivation', 'noLaunch', 'noAutomaticReplay'}
    if set(result['checks']) != expected or not all(value is True for value in result['checks'].values()):
        raise AssertionError('replay assertions failed')
    if any(digest(Path(name)) != value for name, value in before.items()):
        raise AssertionError('source changed during replay')
    toolchain.verify()
    report = {'passed': True, 'sourceHashes': before, 'compilerSHA256': pinned['compilerSHA256'], 'resultSHA256': digest(out / 'result.json'), 'checks': result['checks'], 'scope': 'Compiled Desktop/Surface synthetic scene; native GUI, receipt, focus and AT remain separate. noAutomaticReplay does not send a duplicate frame.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Three-group Desktop replay: seven checks passed; native acceptance not inferred.')


if __name__ == '__main__':
    main()

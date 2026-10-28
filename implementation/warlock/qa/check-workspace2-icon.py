#!/usr/bin/env python3
"""Compile the Desktop taskbar workspace-two restore replay under QA scope."""
import argparse
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


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-owned', required=True)
    args = parser.parse_args()
    require_qa_scope()
    helper = module('three_group_check', ROOT / 'qa/check-three-group.py')
    out = helper.output_directory(args.output_owned)
    toolpath = HELD / 'qa/toolchain.py'
    toolchain = module('held_toolchain', toolpath)
    pinned = toolchain.verify()
    compiler = HELD / pinned['compiler']
    if helper.digest(compiler) != pinned['compilerSHA256']:
        raise ValueError('compiler hash mismatch')
    sources = sorted((ROOT / 'src').glob('*.elm')) + [ROOT / 'elm.json', ROOT / 'qa/NativePointerFixture.elm', ROOT / 'qa/Workspace2IconReplay.elm', ROOT / 'qa/feedback-replay.js', ROOT / 'qa/check-three-group.py', toolpath, HELD / 'qa/toolchain.json']
    before = {str(p): helper.digest(p) for p in sources}
    workspace = out / 'workspace'
    workspace.mkdir()
    (workspace / 'src').symlink_to(ROOT / 'src', target_is_directory=True)
    (workspace / 'qa').mkdir()
    for name in ('NativePointerFixture.elm', 'Workspace2IconReplay.elm'):
        (workspace / 'qa' / name).symlink_to(ROOT / 'qa' / name)
    project = json.loads((ROOT / 'elm.json').read_text())
    project['source-directories'] = ['src', 'qa']
    (workspace / 'elm.json').write_text(json.dumps(project))
    shutil.copytree(HELD / pinned['elmHome'], out / 'elm-home')
    env = {**os.environ, 'ELM_HOME': str(out / 'elm-home'), 'GHCRTS': '-N1', 'SOURCE_DATE_EPOCH': '0', 'TZ': 'UTC', 'PYTHONDONTWRITEBYTECODE': '1'}
    node = shutil.which('node')
    if not node:
        raise RuntimeError('node unavailable')
    (out / 'replay-run.cjs').write_text((ROOT / 'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay', 'Elm.Workspace2IconReplay'))
    commands = []
    def run(argv):
        result = subprocess.run([str(x) for x in argv], cwd=workspace, env=env, capture_output=True, text=True, timeout=120)
        commands.append({'argv': [str(x) for x in argv], 'exitCode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        if result.returncode:
            raise RuntimeError('replay subprocess failed; see commands.json')
    run([compiler, 'make', 'qa/Workspace2IconReplay.elm', '--output=' + str(out / 'replay.js')])
    run([node, out / 'replay-run.cjs', out / 'replay.js', out / 'result.json'])
    result = json.loads((out / 'result.json').read_text())
    expected = {'minimizedWorkspaceTwoFixture', 'barIconOpensGroupWithoutMutation', 'stalePublicationRejected', 'selectedMemberWaitsForFreshProjection', 'wrongProjectionCannotSelect', 'exactRestoreOnce', 'localMembershipNotRewritten', 'noTransferOrLaunch', 'duplicateProjectionNoReplay', 'singleIconRestoresExactRoot'}
    if set(result['checks']) != expected or not all(value is True for value in result['checks'].values()):
        raise AssertionError('replay assertions failed: ' + json.dumps(result['checks']))
    if any(helper.digest(Path(name)) != value for name, value in before.items()):
        raise AssertionError('source changed during replay')
    toolchain.verify()
    report = {'passed': True, 'sourceHashes': before, 'compilerSHA256': pinned['compilerSHA256'], 'resultSHA256': helper.digest(out / 'result.json'), 'checks': result['checks'], 'scope': 'Synthetic workspace metadata and projection through actual Desktop/Surface; no native membership, receipt, focus, paint or AT claim.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Workspace-two taskbar icon replay: ten checks passed; native acceptance not inferred.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Compile pinned current Elm roots and optional pure feedback context fixture.

Development-only CPU evidence; no GUI/native process or effect is launched.
"""
import hashlib
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quint_toolchain():
    pin = json.loads((REPO / 'tools/quint-toolchain.json').read_text())
    root = Path(pin['path'])
    rows = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            rows[str(path.relative_to(root))] = {'symlink': os.readlink(path), 'sha256': sha(path) if path.is_file() else None}
        elif path.is_file():
            rows[str(path.relative_to(root))] = {'sha256': sha(path)}
    actual = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if len(rows) != pin['files'] or actual != pin['treeSHA256'] or pin['backend'] != 'typescript':
        raise RuntimeError('Installed Quint toolchain differs from reviewed inventory')
    return pin, root / 'dist/src/cli.js'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--browser', action='store_true', help='Separately reviewed private-network browser component checks')
    modes.add_argument('--authority', action='store_true', help='Original ARC005 owning-route authority tuple bridge checks')
    modes.add_argument('--receipts', action='store_true', help='Original ARC007 actual desktop receipt bridge and model checks')
    args = parser.parse_args()
    scope = require_qa_scope()
    runtime_base()
    root = REPO / 'implementation/warlock'
    held = REPO / 'implementation/warlock-preview-provider-v143'
    output = REPO / '.warlock-contributor' / ('elm-cpu-' + str(time.time_ns()))
    output.mkdir(parents=True)
    report = {'schema': 1, 'passed': False, 'scope': 'Elm compiler and pure production projection only',
              'nativeAcceptance': False, 'releaseAccepted': False, 'protectedScope': scope, 'commands': []}
    node = Path(shutil.which('node') or '/missing-node').resolve()
    report['developmentTools'] = {name: {'path': str(path), 'sha256': sha(path)}
                                  for name, path in [('python', Path(sys.executable).resolve()), ('node', node)]}
    spec = importlib.util.spec_from_file_location('held_toolchain', held / 'qa/toolchain.py')
    toolchain = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(toolchain)
    pinned = toolchain.verify()
    report['compilerSHA256'] = pinned['compilerSHA256']
    sources = {str(p.relative_to(REPO)): sha(p) for p in sorted((root / 'src').rglob('*.elm'))}
    sources['implementation/warlock/elm.json'] = sha(root / 'elm.json')
    report['sources'] = sources
    work = output / 'work'
    work.mkdir()
    shutil.copytree(root / 'src', work / 'src')
    shutil.copytree(held / pinned['elmHome'], output / 'elm-home')
    config = json.loads((root / 'elm.json').read_text())
    config['source-directories'] = ['src', 'qa']
    (work / 'qa').mkdir()
    (work / 'elm.json').write_text(json.dumps(config))
    env = dict(os.environ, ELM_HOME=str(output / 'elm-home'))
    if args.receipts:
        for key in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
            env.pop(key, None)
        env['NO_COLOR'] = '1'

    def run(name, command):
        toolchain.verify()
        result = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=120)
        (output / (name + '.stdout')).write_text(result.stdout)
        (output / (name + '.stderr')).write_text(result.stderr)
        report['commands'].append({'name': name, 'argv': command, 'exit': result.returncode})
        print(name, result.returncode, flush=True)
        toolchain.verify()
        if result.returncode:
            raise RuntimeError(name + ': ' + result.stderr + result.stdout)

    try:
        compiler = str(held / pinned['compiler'])
        run('compiler-version', [compiler, '--version'])
        run('node-version', [str(node), '--version'])
        # Unchanged GUI roots already have source-bound qualification. ARC005
        # compiles its actual production controller/bridge fixture directly.
        if not args.authority:
            for name in ['Main', 'Bar', 'Popup']:
                run('compile-' + name, [compiler, 'make', 'src/' + name + '.elm', '--optimize', '--output=' + str(output / (name + '.js'))])
        fixture_name = 'ReceiptStateReplay' if args.receipts else ('AuthorityTupleReplay' if args.authority else 'FeedbackContextReplay')
        harness_name = 'receipt-state' if args.receipts else ('authority-tuple' if args.authority else 'feedback-context')
        fixture = root / ('qa/' + fixture_name + '.elm')
        harness = root / ('qa/' + harness_name + '.cjs')
        if fixture.exists():
            for source in [fixture, harness]:
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / source.name)
            run('compile-' + harness_name, [compiler, 'make', 'qa/' + fixture_name + '.elm', '--optimize', '--output=' + str(output / (harness_name + '.js'))])
            if not args.receipts:
                run(harness_name, [str(node), 'qa/' + harness_name + '.cjs', str(output / (harness_name + '.js')), str(output / (harness_name + '.json'))])
        elif args.authority or args.receipts:
            raise RuntimeError('Original scenario fixture is required')
        if args.receipts:
            pin, cli = quint_toolchain()
            report['quintToolchain'] = pin
            for name in ['receipt-lifecycle.qnt', 'receipt-lifecycle_test.qnt']:
                source = root / 'qa' / name
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / name)
            sources['tools/quint-toolchain.json'] = sha(REPO / 'tools/quint-toolchain.json')
            run('receipt-model-typecheck', [str(node), str(cli), 'typecheck', 'qa/receipt-lifecycle_test.qnt'])
            run('receipt-model-cancelled-tests', [str(node), str(cli), 'test', 'qa/receipt-lifecycle.qnt', '--main=ReceiptLifecycle', '--match=.*Test', '--backend=typescript', '--verbosity=2'])
            run('receipt-model-original-tests', [str(node), str(cli), 'test', 'qa/receipt-lifecycle_test.qnt', '--main=ReceiptLifecycle_test', '--match=.*Test', '--backend=typescript', '--verbosity=2'])
            run('receipt-model-safety', [str(node), str(cli), 'run', 'qa/receipt-lifecycle.qnt', '--main=ReceiptLifecycle', '--backend=typescript', '--invariant=safety', '--witnesses',
                                        'witnessPending', 'witnessCommitted', 'witnessRefused', 'witnessCancelled', 'witnessUnknown', 'witnessDisconnected', 'witnessNewRequest',
                                        '--max-samples=10000', '--max-steps=50', '--seed=20261031', '--verbosity=1'])
            text = (output / 'receipt-model-safety.stdout').read_text()
            witnesses = {name: int(count) for name, count in re.findall(r'(witness\w+) was witnessed in (\d+) trace', text)}
            report['modelWitnessCounts'] = witnesses
            if len(witnesses) != 7 or any(count == 0 for count in witnesses.values()):
                raise RuntimeError('Model reachability witness missing or zero; inspect retained sampling report')
            quint_toolchain()
            run(harness_name, [str(node), 'qa/' + harness_name + '.cjs', str(output / (harness_name + '.js')), str(output / (harness_name + '.json'))])
        if args.browser:
            # New network/PID namespaces have no host network or desktop sockets.
            # This is browser component evidence, never a native GUI trial.
            for source in [root / 'assets/shell.css', root / 'qa/feedback-context-browser.mjs', REPO / 'tools/check_feedback_browser.py']:
                sources[str(source.relative_to(REPO))] = sha(source)
            env['WARLOCK_CPU_PARENT_NETNS'] = os.readlink('/proc/self/ns/net')
            run('feedback-context-browser', ['bwrap', '--unshare-net', '--unshare-pid', '--bind', '/', '/',
                                            '--dev', '/dev', '--proc', '/proc', '--tmpfs', '/run/user',
                                            '--tmpfs', '/tmp', '--', sys.executable, '-B',
                                            str(REPO / 'tools/check_feedback_browser.py'), str(output)])
        if not all(sha(REPO / p) == digest for p, digest in sources.items()):
            raise RuntimeError('Source changed during protected check')
        if not all(sha(Path(tool['path'])) == tool['sha256'] for tool in report['developmentTools'].values()):
            raise RuntimeError('Development interpreter changed during protected check')
        report['artifacts'] = {p.name: sha(p) for p in output.glob('*.js')}
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'passed': report['passed'], 'report': str(output / 'report.json'), 'error': report.get('error')}), flush=True)
        # Keep reports and compiled artifacts; disposable compiler cache/source copy is not evidence.
        shutil.rmtree(work)
        shutil.rmtree(output / 'elm-home')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

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
import shutil
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--browser', action='store_true', help='Separately reviewed private-network browser component checks')
    modes.add_argument('--authority', action='store_true', help='Original ARC005 owning-route authority tuple bridge checks')
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
        fixture_name = 'AuthorityTupleReplay' if args.authority else 'FeedbackContextReplay'
        harness_name = 'authority-tuple' if args.authority else 'feedback-context'
        fixture = root / ('qa/' + fixture_name + '.elm')
        harness = root / ('qa/' + harness_name + '.cjs')
        if fixture.exists():
            for source in [fixture, harness]:
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / source.name)
            run('compile-' + harness_name, [compiler, 'make', 'qa/' + fixture_name + '.elm', '--optimize', '--output=' + str(output / (harness_name + '.js'))])
            run(harness_name, [str(node), 'qa/' + harness_name + '.cjs', str(output / (harness_name + '.js')), str(output / (harness_name + '.json'))])
        elif args.authority:
            raise RuntimeError('Original authority-tuple fixture is required')
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

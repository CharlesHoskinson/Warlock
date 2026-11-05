#!/usr/bin/env python3
"""Fixed private ARM build profiles, admitted only by hash-reviewed qa_cpu."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from arm64_toolchain import digest, inventory, verify
from qa_cpu import arm64_inputs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base  # ty: ignore[import-not-found]


def image(path):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('Expected regular compiled image')
    status = path.stat()
    return {'path': str(path), 'device': str(status.st_dev), 'inode': str(status.st_ino),
                'size': str(status.st_size), 'sha256': digest(path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ('subscriptions', 'owner-build', 'owner', 'preview-control', 'protocol'):
        modes.add_argument('--' + mode, action='store_true')
    parser.add_argument('--inside-private', type=Path)
    args = parser.parse_args()
    scope = require_qa_scope()
    if args.inside_private is not None:
        private_runtime = Path('/run/user') / str(os.getuid())
        private_runtime.mkdir(parents=True, mode=0o700)
    runtime_base()
    mode = '--subscriptions' if args.subscriptions else ('--owner-build' if args.owner_build else ('--preview-control' if args.preview_control else ('--protocol' if args.protocol else '--owner')))
    if args.inside_private is None:
        output = ROOT / '.warlock-contributor' / ('arm64-cpu-' + str(time.time_ns()))
        output.mkdir(parents=True, mode=0o700)
        sources = {name: digest(ROOT / name) for name in sorted(arm64_inputs(ROOT, args.subscriptions, args.preview_control, args.protocol))}
        packet = verify(full=True)
        report = {'schema': 1, 'passed': False, 'mode': mode, 'protectedScope': scope, 'sourceHashes': sources,
                      'toolchainManifestSHA256': packet['manifestSHA256'], 'commands': [],
                      'scope': 'ARM component build/replay only; no original scenario or native acceptance',
                      'nativeAcceptance': False, 'originalAcceptance': False, 'releaseAccepted': False}
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        # Hide host runtime sockets and network. All compiler writes are confined
        # to the new output; SDK, source, system inputs and caches remain read-only.
        command = ['/usr/bin/bwrap', '--die-with-parent', '--unshare-net', '--unshare-pid',
                   '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin',
                   '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib', '/lib64',
                   '--dir', '/etc']
        for name in ('ld.so.cache', 'passwd', 'group', 'nsswitch.conf'):
            command += ['--ro-bind', '/etc/' + name, '/etc/' + name]
        command += ['--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--tmpfs', '/run',
                    '--ro-bind', str(ROOT), str(ROOT)]
        mounts = set(packet['trees']) | {name for name in packet['files'] if name.startswith('/home/hoskinson/')}
        for name in sorted(mounts):
            command += ['--ro-bind', name, name]
        command += ['--bind', str(output), str(output),
                   '--chdir', str(ROOT), '--', sys.executable, '-B', str(Path(__file__).resolve()),
                   mode, '--inside-private', str(output)]
        clean = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
                 'PYTHONDONTWRITEBYTECODE': '1', 'HOME': str(output / 'home'), 'TMPDIR': '/tmp'}
        # qa_launch reads the systemd scope through /proc, not an environment bypass.
        try:
            child = subprocess.run(command, cwd=ROOT, env=clean, timeout=3500, check=False)
            report = json.loads((output / 'report.json').read_text())
            verify(full=True)
            if set(arm64_inputs(ROOT, args.subscriptions, args.preview_control, args.protocol)) != set(sources) or any(digest(ROOT / name) != sha for name, sha in sources.items()):
                raise RuntimeError('ARM source closure changed during execution')
            if child.returncode or not report['passed']:
                raise RuntimeError('Private ARM profile failed; retained logs')
        except Exception as error:  # noqa: BLE001 -- retain failure evidence before exiting
            report.update(passed=False, error=str(error))
        finally:
            (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps({'passed': report['passed'], 'report': str(output / 'report.json')}), flush=True)
        return 0 if report['passed'] else 1

    output = args.inside_private
    if output.parent != ROOT / '.warlock-contributor' or not re.fullmatch('arm64-cpu-[0-9]+', output.name) or output.is_symlink():
        raise RuntimeError('Unexpected ARM private output')
    report = json.loads((output / 'report.json').read_text())
    packet = verify(full=True)
    env = dict(os.environ, PATH=str(Path(packet['ghcPrefix']) / 'bin') + ':/usr/bin:/bin',
               GHC_ENVIRONMENT='-', CABAL_DIR=str(output / 'cabal-home'), NO_COLOR='1')
    logs = output / 'logs'
    logs.mkdir(mode=0o700)

    def run(name, command, cwd=ROOT, timeout=900, extra_env=None):
        with (logs / (name + '.stdout')).open('wb') as stdout, (logs / (name + '.stderr')).open('wb') as stderr:
            child = subprocess.run([str(arg) for arg in command], cwd=cwd, env=extra_env or env,
                                   stdout=stdout, stderr=stderr, timeout=timeout, check=False)
        report['commands'].append({'name': name, 'argv': [str(arg) for arg in command], 'exit': child.returncode})
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        if child.returncode:
            raise RuntimeError(name + ' failed; see retained logs')
        return (logs / (name + '.stdout')).read_text()

    try:
        if args.preview_control:
            # Fixed source syntax preflight prevents expensive recompilation
            # when a declared QA fixture cannot be parsed by the pinned Node.
            for name in ('http-preview-control-replay.cjs', 'http-preview-control-literals.cjs',
                         'sol-http-root-observer-0535.cjs', 'sol-http-popup-literals-0525.cjs',
                         'tea-contract-cases.cjs'):
                run('syntax-' + name, [packet['node'], '--check',
                    ROOT / 'implementation/warlock/qa' / name], timeout=30)
        if args.subscriptions:
            subscription_output = output / 'subscriptions'
            run('subscriptions', [sys.executable, '-B', ROOT / 'tools/check_elm_cpu.py',
                                  '--subscriptions', '--arm64', '--arm64-output', subscription_output], timeout=3300)
            summary = json.loads((subscription_output / 'report.json').read_text())
            if not summary['passed']:
                raise RuntimeError('ARM subscription replay has no successful report')
            report['subscriptionsReport'] = {'path': str(subscription_output / 'report.json'),
                                                'sha256': digest(subscription_output / 'report.json')}
        else:
            source = ROOT / 'implementation/warlock/haskell'
            before = inventory(source)
            stage = output / 'haskell'
            shutil.copytree(source, stage, ignore=shutil.ignore_patterns('dist-newstyle', '__pycache__'))
            if inventory(stage) != before:
                raise RuntimeError('Haskell stage differs')
            dependencies = output / 'dependencies'
            shutil.copytree(Path(packet['dependencies']), dependencies)
            if inventory(dependencies) != packet['trees'][packet['dependencies']]:
                raise RuntimeError('ARM dependency stage differs')
            manifest = json.loads((ROOT / 'tools/haskell-dependencies.json').read_text())
            for dependency in manifest['packages']:
                metadata = dependencies / dependency['directory'] / (dependency['name'] + '.cabal')
                if digest(metadata) != dependency['metadataSHA256']:
                    raise RuntimeError('Exact Haskell dependency metadata revision differs')
            project = stage / 'cabal.project'
            project.write_text(project.read_text() + '\npackages: ' + ' '.join(
                str(dependencies / p['directory']) for p in manifest['packages']) + '\nactive-repositories: :none\n')
            config = output / 'cabal.config'
            config.write_text('active-repositories: :none\nstore-dir: ' + str(output / 'store') + '\nremote-repo-cache: ' + str(output / 'repo-cache') + '\n')
            ghc = Path(packet['ghcPrefix']) / 'bin'
            common = [packet['cabal'], '--config-file=' + str(config)]
            flags = ['--offline', '--project-file=' + str(project), '--builddir=' + str(output / 'dist'),
                     '--with-compiler=' + str(ghc / 'ghc'), '--with-hc-pkg=' + str(ghc / 'ghc-pkg'),
                     '--with-hsc2hs=' + str(ghc / 'hsc2hs'), '--with-gcc=/usr/bin/gcc',
                     '--with-ar=/usr/bin/ar', '--with-ld=/usr/bin/ld', '--with-pkg-config=/usr/bin/pkg-config', '--jobs=2']
            target = 'warlock-runtime:test:ui-origin-controls'
            protocol = 'warlock-protocol:test:desktop-boundary-controls'
            backend = 'warlock-runtime:exe:warlock-ui-backend'
            run('protocol-build' if args.protocol else 'owner-build', common + ['build'] + flags +
                ([protocol] if args.protocol else [target, protocol, backend]), stage)
            binaries = {}
            selected_targets = ([('desktop-boundary-controls', protocol)] if args.protocol else
                                [('ui-origin-controls', target), ('desktop-boundary-controls', protocol),
                                 ('warlock-ui-backend', backend)])
            for name, selected in selected_targets:
                lines = run('list-' + name, common + ['list-bin'] + flags + [selected], stage).splitlines()
                if len(lines) != 1:
                    raise RuntimeError('Unexpected compiled binary path')
                path = Path(lines[0])
                if not path.is_relative_to(output / 'dist') or path.name != name:
                    raise RuntimeError('Unexpected compiled binary location')
                binaries[name] = image(path)
            documents, plain = {}, {}
            if not args.protocol:
                frontend = output / 'frontend'
                frontend.mkdir(mode=0o700)
                shutil.copytree(ROOT / 'implementation/warlock/src', frontend / 'src')
                shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
                shutil.copyfile(ROOT / 'implementation/warlock/elm.json', frontend / 'elm.json')
                elm_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
                documents, plain = {}, {}
                for role, entry in (('controller', 'HttpMain'), ('bar', 'HttpBar'), ('popup', 'HttpPopup')):
                    html = frontend / (entry + '.html')
                    run('compile-' + entry, [packet['elm'], 'make', 'src/' + entry + '.elm', '--optimize', '--output=' + str(html)], frontend, 180, elm_env)
                    info = image(html)
                    info['ancestors'] = [{'path': str(p), 'device': str(p.stat().st_dev), 'inode': str(p.stat().st_ino)}
                                         for p in reversed(html.parents) if str(p) != '/']
                    documents[role] = info
                    js = frontend / (entry + '.plain.js')
                    run('compile-plain-' + entry, [packet['elm'], 'make', 'src/' + entry + '.elm', '--output=' + str(js)], frontend, 180, elm_env)
                    plain[role] = image(js)
            report.update(executables=binaries, uiDocuments=documents, plainRoots=plain)
            if args.preview_control:
                qa = ROOT / 'implementation/warlock/qa'
                result = json.loads(run('http-preview-control', [packet['node'],
                    qa / 'http-preview-control-replay.cjs', ROOT, plain['popup']['path']], timeout=180))
                expected = [('HttpPopup-native-control-closed-realm-lifetime', 8),
                            ('HttpPopup-matching-quarantine-retains-unconfirmed-reconcile', 4),
                            ('HttpPopup-restart-enrolls-new-realm-without-old-effect-replay', 2)]
                state = 20261105
                for index in range(32):
                    state = (1664525 * state + 1013904223) & 0xffffffff
                    expected.append((f'HttpPopup-control-LCG20261105-{index}-{state}', 7))
                results = result.get('results', [])
                coverage = result.get('coverage', {})
                if (set(result) != {'ok', 'results', 'imageSha256', 'fixtureSha256', 'observerSha256',
                                    'tool', 'fuzz', 'coverage', 'originalAcceptanceClaim'}
                        or result.get('ok') is not True or result.get('originalAcceptanceClaim') is not False
                        or [(row.get('name'), row.get('steps')) for row in results] != expected
                        or any(set(row) != {'name', 'steps', 'freshRuns', 'negative', 'instrumentation'}
                               or row.get('freshRuns') != 2 or row.get('negative') != 'grant-retention-model-altered'
                               for row in results)
                        or result.get('tool') != {'node': 'v26.13.0'}
                        or result.get('fuzz') != {'seed': 20261105, 'cases': 32,
                            'generator': 'LCG32 1664525/1013904223; 32 seven-step realm sequences'}
                        or result.get('imageSha256') != plain['popup']['sha256']
                        or result.get('fixtureSha256') != digest(qa / 'http-preview-control-literals.cjs')
                        or result.get('observerSha256') != digest(qa / 'sol-http-root-observer-0535.cjs')
                        or any(coverage.get(k) is not False for k in ('complete', 'originalAccepted', 'nativeAccepted'))):
                    raise RuntimeError('Fixed preview-control replay report differs')
                report['previewControl'] = result
            if args.owner or args.preview_control or args.protocol:
                runs = output / 'runs'
                runs.mkdir(mode=0o700)
                def wrapped(item):
                    return {'path': item['path'], 'pin': [item[k] for k in ('device', 'inode', 'size', 'sha256')]}
                dispatch = {'suites': {}}
                if not args.protocol:
                    dispatch['suites'][binaries['ui-origin-controls']['path']] = {
                        'suite': 'ui-origin-controls', 'test': wrapped(binaries['ui-origin-controls']),
                        'fixtures': {'warlock-ui-backend': wrapped(binaries['warlock-ui-backend'])},
                        'uiDocuments': documents, 'runRoot': str(runs / 'ui-origin-controls')}
                dispatch['suites'][binaries['desktop-boundary-controls']['path']] = {
                    'suite': 'desktop-boundary-controls', 'test': wrapped(binaries['desktop-boundary-controls']),
                    'fixtures': {}, 'runRoot': str(runs / 'desktop-boundary-controls')}
                dispatch_path = output / 'dispatch.json'
                dispatch_path.write_text(json.dumps(dispatch, indent=2) + '\n')
                test_env = dict(env, WARLOCK_HASKELL_DISPATCH=str(dispatch_path))
                report['suiteReceipts'] = {}
                for suite in (('desktop-boundary-controls',) if args.protocol else
                              ('desktop-boundary-controls', 'ui-origin-controls')):
                    run(suite, [sys.executable, '-B', ROOT / 'tools/haskell_test_wrapper.py',
                                binaries[suite]['path']], stage, 900, test_env)
                    receipt = json.loads((runs / suite / 'results.json').read_text())
                    if len(receipt) != 1 or receipt[0]['exit'] != 0 or receipt[0]['forcedCleanup']:
                        raise RuntimeError(suite + ' lacks successful terminal receipt')
                    report['suiteReceipts'][suite] = receipt
            for item in [*binaries.values(), *documents.values(), *plain.values()]:
                if image(Path(item['path'])) != {k: item[k] for k in ('path', 'device', 'inode', 'size', 'sha256')}:
                    raise RuntimeError('Compiled ARM artifact changed during profile')
        verify(full=True)
        if any(digest(ROOT / name) != sha for name, sha in report['sourceHashes'].items()):
            raise RuntimeError('ARM input source changed')
        report['passed'] = True
    except Exception as error:  # noqa: BLE001 -- retain failure evidence before exiting
        report.update(passed=False, error=str(error))
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

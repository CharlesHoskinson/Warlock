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


def consumption_frontend(output, env, packet, run):
    """Fixed actual Elm component route; original joined HTTP oracles stay open."""
    frontend = output / 'frontend'
    frontend.mkdir(mode=0o700)
    source = ROOT / 'implementation/warlock'
    before = inventory(source / 'src')
    shutil.copytree(source / 'src', frontend / 'src')
    shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
    (frontend / 'qa').mkdir(mode=0o700)
    qa_files = [name for name in arm64_inputs(ROOT, consumption=True)
                if name.startswith('implementation/warlock/qa/')]
    for name in sorted(qa_files):
        shutil.copyfile(ROOT / name, frontend / 'qa' / Path(name).name)
    reviewed_sources = json.loads((output / 'report.json').read_text())['sourceHashes']
    for name in qa_files:
        if digest(frontend / 'qa' / Path(name).name) != reviewed_sources[name]:
            raise RuntimeError('Reviewed consumption QA stage differs: ' + name)
    config = json.loads((source / 'elm.json').read_text())
    config['source-directories'] = ['src', 'qa']
    (frontend / 'elm.json').write_text(json.dumps(config, sort_keys=True) + '\n')
    staged_config = digest(frontend / 'elm.json')
    if inventory(frontend / 'src') != before:
        raise RuntimeError('Consumption frontend source stage differs')
    build_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
    for name in ('preview-consumption.cjs', 'typed-state.cjs'):
        run('syntax-' + name, [packet['node'], '--check', frontend / 'qa' / name], frontend, 30, build_env)
    typed = ('NotificationsReplay', 'JumpListReplay', 'NotificationRelevanceReplay',
             'RetirementProofReplay', 'LocalFieldReplay')
    entries = [('PreviewConsumptionReplay', 'qa'), ('RetainedPreviewPresenterReplay', 'src')]
    entries += [(name, 'qa') for name in typed]
    roots = ('Main', 'Bar', 'Popup', 'HttpMain', 'HttpBar', 'HttpPopup',
             'NativePreviewAdmission', 'NativePreviewRenderer')
    entries += [(name, 'src') for name in roots]
    artifacts = {}
    for name, directory in entries:
        target = frontend / (name + '.js')
        run('compile-' + name, [packet['elm'], 'make', directory + '/' + name + '.elm',
            '--optimize', '--output=' + str(target)], frontend, 180, build_env)
        artifacts[name] = image(target)
    typed_path = frontend / 'typed-state.json'
    run('typed-state', [packet['node'], frontend / 'qa/typed-state.cjs',
                       *[artifacts[name]['path'] for name in typed], typed_path], frontend, 90, build_env)
    observed = json.loads(typed_path.read_text())
    typed_counts = {'NotificationsReplay': 24, 'JumpListReplay': 30, 'NotificationRelevanceReplay': 20,
              'RetirementProofReplay': 20, 'LocalFieldReplay': 43}
    rows = observed.get('fixtures', [])
    if (observed.get('schema') != 1 or observed.get('passed') is not True or observed.get('failures') != []
            or observed.get('runnerSha256') != digest(frontend / 'qa/typed-state.cjs')
            or [row.get('name') for row in rows] != list(typed)
            or len(observed.get('checks', [])) != sum(typed_counts.values())
            or any(row.get('passed') is not True or row.get('failures') != []
                   or row.get('sha256') != artifacts[row['name']]['sha256']
                   or len(row.get('checks', [])) != typed_counts[row['name']]
                   or any(check.get('passed') is not True for check in row.get('checks', [])) for row in rows)):
        raise RuntimeError('Exact existing typed lifecycle/local-field regression report differs')
    budgets: dict = {'cases': {'min': 7, 'max': 7}, 'steps': {'min': 4280, 'max': 4500},
               'assertions': {'min': 5300, 'max': 10000}, 'seeds': {'min': 3, 'max': 3},
               'responseMs': 20000, 'totalMs': 180000}
    fixture_hashes = {'compiled': artifacts['PreviewConsumptionReplay']['sha256'],
                      'oracle': digest(frontend / 'qa/preview-consumption.cjs'),
                      'elmFixture': digest(frontend / 'qa/PreviewConsumptionReplay.elm')}
    receipts = []
    for index in range(2):
        receipt = json.loads(run('preview-consumption-fresh-' + str(index),
            [packet['node'], frontend / 'qa/preview-consumption.cjs', artifacts['PreviewConsumptionReplay']['path']],
            frontend, 210, build_env))
        counts = receipt.get('counts', {})
        if (set(receipt) != {'status', 'counts', 'budgets', 'seeds', 'hashes', 'lastSequence'}
                or receipt.get('status') != 'passed' or receipt.get('budgets') != budgets
                or receipt.get('seeds') != [20261105, 20261106, 20261107]
                or receipt.get('hashes') != fixture_hashes or set(counts) != {'cases', 'steps', 'assertions', 'seeds'}
                or any(type(counts[name]) is not int or not budgets[name]['min'] <= counts[name] <= budgets[name]['max']
                       for name in ('cases', 'steps', 'assertions', 'seeds'))
                or type(receipt.get('lastSequence')) is not int or receipt['lastSequence'] != counts['steps']):
            raise RuntimeError('Consumption fixture terminal receipt is missing, incomplete or mismatched')
        receipts.append(receipt)
    if receipts[0] != receipts[1]:
        raise RuntimeError('Two fresh consumption executions differ')
    for artifact in artifacts.values():
        if image(Path(artifact['path'])) != artifact:
            raise RuntimeError('Compiled consumption/compatibility artifact changed')
    if (inventory(frontend / 'src') != before or inventory(source / 'src') != before
            or digest(frontend / 'elm.json') != staged_config
            or any(digest(frontend / 'qa' / Path(name).name) != reviewed_sources[name] for name in qa_files)):
        raise RuntimeError('Consumption source, staged manifest or fixture changed during execution')
    return {'scope': 'Actual compiled Elm Popup/ingress consumption component and existing typed regressions only',
            'artifacts': artifacts, 'optimizedProductionRoots': list(roots), 'productionRootBehaviorExecuted': False,
            'consumption': {'freshRuns': 2, 'receipts': receipts},
            'typedState': {'path': str(typed_path), 'sha256': digest(typed_path), 'checks': sum(typed_counts.values()),
                           'fixtures': list(typed)},
            'retainedPresenter': {'compiled': True, 'behaviorExecuted': False},
            'originalHttpFiveAndEleven': {'executed': False, 'status': 'Pending separate current-source oracle derivative review'},
            'nativeAcceptance': False, 'originalAcceptance': False, 'releaseAccepted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ('subscriptions', 'owner-build', 'owner', 'preview-control', 'protocol', 'preview-consumption', 'preview-schema', 'held-executable'):
        modes.add_argument('--' + mode, action='store_true')
    parser.add_argument('--inside-private', type=Path)
    args = parser.parse_args()
    protocol_profile = args.protocol or args.preview_schema
    haskell_profile = protocol_profile or args.held_executable
    scope = require_qa_scope()
    if args.inside_private is not None:
        private_runtime = Path('/run/user') / str(os.getuid())
        private_runtime.mkdir(parents=True, mode=0o700)
    runtime_base()
    mode = ('--held-executable' if args.held_executable else ('--preview-schema' if args.preview_schema else ('--preview-consumption' if args.preview_consumption else
            ('--subscriptions' if args.subscriptions else ('--owner-build' if args.owner_build else
             ('--preview-control' if args.preview_control else ('--protocol' if args.protocol else '--owner')))))))
    if args.inside_private is None:
        output = ROOT / '.warlock-contributor' / ('arm64-cpu-' + str(time.time_ns()))
        output.mkdir(parents=True, mode=0o700)
        sources = {name: digest(ROOT / name) for name in sorted(arm64_inputs(
            ROOT, args.subscriptions, args.preview_control, haskell_profile, args.preview_consumption))}
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
            if set(arm64_inputs(ROOT, args.subscriptions, args.preview_control, haskell_profile,
                                args.preview_consumption)) != set(sources) or any(digest(ROOT / name) != sha for name, sha in sources.items()):
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
        if args.preview_consumption:
            report['previewConsumption'] = consumption_frontend(output, env, packet, run)
        elif args.subscriptions:
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
            protocol_suites = (('preview-control', 'desktop-boundary-controls') if args.preview_schema else
                               ('desktop-boundary-controls',))
            protocol_targets = [(suite, 'warlock-protocol:test:' + suite) for suite in protocol_suites]
            backend = 'warlock-runtime:exe:warlock-ui-backend'
            if args.held_executable:
                library_target = 'warlock-held-document-proposal:lib:warlock-held-document-proposal'
                library = (stage / 'held-document/held-document.cabal').read_text().split('\nlibrary\n', 1)[1].split('\ntest-suite ', 1)[0]
                exposed = re.search(r'^  exposed-modules: (.+)$', library, re.M)
                if not exposed or exposed.group(1).replace(',', '').split() != [
                        'Warlock.Platform.Resolver', 'Warlock.Platform.Executable', 'Warlock.Http.Document']:
                    raise RuntimeError('Ordinary held library module opacity differs')
                selected_targets = [('held-executable-controls', 'warlock-held-document-proposal:test:held-executable-controls'),
                                    ('custody-child', 'warlock-process-custody:exe:custody-child')]
                build_targets = [library_target, *[selected for _, selected in selected_targets]]
                build_label = 'held-executable-build'
                protocol_suites = ()
                report['heldExecutableProfile'] = {'ordinaryLibraryTarget': library_target,
                    'declaredOrdinaryInternalModulesExposed': False, 'testsUseHomeModules': True,
                    'publicLinkedTestProof': False, 'externalImportOpacityProbeExecuted': False, 'fixture': 'custody-child',
                    'scope': 'Held executable lease/process fixture only; no native desktop or original acceptance'}
            else:
                build_targets = ([selected for _, selected in protocol_targets] if protocol_profile else
                                 [target, *[selected for _, selected in protocol_targets], backend])
                build_label = 'preview-schema-build' if args.preview_schema else ('protocol-build' if args.protocol else 'owner-build')
                selected_targets = (protocol_targets if protocol_profile else
                                    [('ui-origin-controls', target), *protocol_targets, ('warlock-ui-backend', backend)])
            run(build_label, common + ['build'] + flags + build_targets, stage)
            binaries = {}
            for name, selected in selected_targets:
                lines = run('list-' + name, common + ['list-bin'] + flags + [selected], stage).splitlines()
                if len(lines) != 1:
                    raise RuntimeError('Unexpected compiled binary path')
                path = Path(lines[0])
                if not path.is_relative_to(output / 'dist') or path.name != name:
                    raise RuntimeError('Unexpected compiled binary location')
                binaries[name] = image(path)
            documents, plain = {}, {}
            if not haskell_profile:
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
            if args.owner or args.preview_control or protocol_profile or args.held_executable:
                runs = output / 'runs'
                runs.mkdir(mode=0o700)
                def wrapped(item):
                    return {'path': item['path'], 'pin': [item[k] for k in ('device', 'inode', 'size', 'sha256')]}
                dispatch = {'suites': {}}
                if args.held_executable:
                    dispatch['suites'][binaries['held-executable-controls']['path']] = {
                        'suite': 'held-executable-controls', 'test': wrapped(binaries['held-executable-controls']),
                        'fixtures': {'custody-child': wrapped(binaries['custody-child'])},
                        'runRoot': str(runs / 'held-executable-controls')}
                elif not protocol_profile:
                    dispatch['suites'][binaries['ui-origin-controls']['path']] = {
                        'suite': 'ui-origin-controls', 'test': wrapped(binaries['ui-origin-controls']),
                        'fixtures': {'warlock-ui-backend': wrapped(binaries['warlock-ui-backend'])},
                        'uiDocuments': documents, 'runRoot': str(runs / 'ui-origin-controls')}
                for suite in protocol_suites:
                    dispatch['suites'][binaries[suite]['path']] = {
                        'suite': suite, 'test': wrapped(binaries[suite]),
                        'fixtures': {}, 'runRoot': str(runs / suite)}
                dispatch_path = output / 'dispatch.json'
                dispatch_path.write_text(json.dumps(dispatch, indent=2) + '\n')
                test_env = dict(env, WARLOCK_HASKELL_DISPATCH=str(dispatch_path))
                report['suiteReceipts'] = {}
                suites = (('held-executable-controls',) if args.held_executable else
                          (protocol_suites if protocol_profile else (*protocol_suites, 'ui-origin-controls')))
                for suite in suites:
                    run(suite, [sys.executable, '-B', ROOT / 'tools/haskell_test_wrapper.py',
                                binaries[suite]['path']], stage, 900, test_env)
                    receipt = json.loads((runs / suite / 'results.json').read_text())
                    if len(receipt) != 1 or receipt[0]['exit'] != 0 or receipt[0]['forcedCleanup']:
                        raise RuntimeError(suite + ' lacks successful terminal receipt')
                    if args.held_executable and (receipt[0].get('mode') != 'default' or receipt[0].get('timeout') is not False
                            or receipt[0].get('argv') != [str(runs / suite / 'image'), 'custody-child',
                                                        binaries['custody-child']['size'], binaries['custody-child']['sha256']]):
                        raise RuntimeError('Held executable disposable COPY receipt differs')
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

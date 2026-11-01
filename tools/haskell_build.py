"""Offline, source-copy Haskell build and fixture QA; called only by protected runner.

build(sdk, output, env) returns an auditable dictionary. The caller owns the
network/PID namespace, SDK verification, output directory and final report.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = ROOT / 'tools/haskell-dependencies.json'
WRAPPER = ROOT / 'tools/haskell_test_wrapper.py'
SUITES = {
    'warlock-held-document-proposal': ['held-document-controls', 'held-executable-controls'],
    'warlock-process-custody': ['internal-controls', 'public-controls', 'selected-fd-controls', 'deadline-stop-controls', 'bootstrap-facade-controls'],
    'warlock-protocol': ['boundary-controls', 'ingress-controls', 'owner-sequences', 'credential-guard-controls'],
    'warlock-elf-observation-proposal': ['elf-cases'],
    'warlock-runtime': ['current-session-oracles', 'persistent-bootstrap-controls'],
    'warlock-native-authority': ['native-cancellation-controls', 'durable-storage-controls', 'selection-admission-controls', 'host-guard-controls', 'slot-store-controls', 'pair-store-smoke', 'child-directory-controls', 'independent-admission-shape', 'pair-store-sequences', 'independent-lifetime-owner', 'independent-pairstore'],
}
FIXTURES = {
    'custody-child': 'warlock-process-custody:exe:custody-child',
    'selected-fd-child': 'warlock-process-custody:exe:selected-fd-child',
    'graceful-stop-child': 'warlock-process-custody:exe:graceful-stop-child',
    'bootstrap-facade-child': 'warlock-process-custody:exe:bootstrap-facade-child',
    'credential-peer-child': 'warlock-runtime:exe:credential-peer-child',
}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inventory(root, exclude_builds=False):
    result = {}
    for path in sorted(root.rglob('*')):
        rel = str(path.relative_to(root))
        if exclude_builds and any(part in ('dist', 'dist-newstyle', '.stack-work') for part in path.relative_to(root).parts):
            continue
        if path.is_symlink():
            raise RuntimeError('unexpected symlink in source tree: ' + str(path))
        if path.is_file():
            result[rel] = digest(path)
    return result


def pin(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('expected regular executable: ' + str(path))
    st = path.stat()
    return [str(st.st_dev), str(st.st_ino), str(st.st_size), digest(path)]


def run(argv, cwd, env, logs, name, timeout=900):
    stdout = logs / (name + '.stdout')
    stderr = logs / (name + '.stderr')
    with stdout.open('wb') as out, stderr.open('wb') as err:
        process = subprocess.Popen([str(x) for x in argv], cwd=cwd, env=env, stdout=out,
                                   stderr=err, start_new_session=True)
        timeout_hit = False
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timeout_hit = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                code = process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
        forced = timeout_hit
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            pass
        else:
            forced = True
            os.killpg(process.pid, signal.SIGKILL)
    return {'argv': [str(x) for x in argv], 'exit': code, 'timeout': timeout_hit,
            'forcedCleanup': forced, 'stdout': str(stdout), 'stderr': str(stderr)}


def build(sdk, output, env, profile='common'):
    if profile not in ('common', 'auth'):
        raise RuntimeError('Unknown fixed Haskell verification profile')
    sdk, output = Path(sdk).resolve(), Path(output).resolve()
    result = {'schema': 1, 'passed': False, 'profile': profile, 'commands': [], 'suites': {},
              'nativeAccepted': False, 'releaseAccepted': False}
    work = output / 'haskell-build'
    try:
        work.mkdir(mode=0o700)  # no reuse of previous artifacts
        logs = work / 'logs'
        logs.mkdir(mode=0o700)
        source = ROOT / 'implementation/warlock/haskell'
        copy = work / 'source'
        ignore = shutil.ignore_patterns('dist', 'dist-newstyle', '.stack-work')
        before = inventory(source, exclude_builds=True)
        shutil.copytree(source, copy, symlinks=True, ignore=ignore)
        source_hashes = inventory(copy)
        if before != source_hashes or inventory(source, exclude_builds=True) != before:
            raise RuntimeError('Haskell source changed during staging')
        result['sourceHashes'] = source_hashes
        (work / 'source-hashes.json').write_text(json.dumps(source_hashes, indent=2) + '\n')
        sdk_inventory = json.loads((sdk / 'sdk.json').read_text())['files']
        packages = json.loads(DEPENDENCIES.read_text())['packages']
        depdir = work / 'dependencies'
        depdir.mkdir()
        for package in packages:
            name = package['directory']
            archive = sdk.parent / 'downloads' / (name + '.tar.gz')
            if archive.is_symlink() or not archive.is_file() or digest(archive) != package['archiveSHA256']:
                raise RuntimeError('dependency archive differs: ' + name)
            dest = depdir / name
            if package.get('source') == 'archive':
                with tarfile.open(archive) as contents:
                    contents.extractall(depdir, filter='data')
                inventory(dest)
            else:
                source_dep = sdk / 'sources' / name
                expected = {k[len('sources/' + name + '/'):]: v['sha256'] for k, v in sdk_inventory.items()
                            if k.startswith('sources/' + name + '/') and 'sha256' in v}
                if inventory(source_dep) != expected:
                    raise RuntimeError('SDK dependency source inventory differs: ' + name)
                shutil.copytree(source_dep, dest, symlinks=True)
            metadata = sdk.parent / 'downloads' / package['metadataFile']
            if metadata.is_symlink() or digest(metadata) != package['metadataSHA256']:
                raise RuntimeError('dependency metadata differs: ' + name)
            shutil.copyfile(metadata, dest / (package['name'] + '.cabal'))
        result['dependencyHashes'] = inventory(depdir)
        result['dependenciesManifestSHA256'] = digest(DEPENDENCIES)
        result['wrapperSHA256'] = digest(WRAPPER)
        config = work / 'cabal.config'
        store = work / 'store'
        config.write_text('remote-repo-cache: ' + str(work / 'repo-cache') + '\nstore-dir: ' + str(store) + '\nactive-repositories: :none\n')
        base_project = (copy / 'cabal.project').read_text()
        base_project += '\npackages: ' + ' '.join('../dependencies/' + package['directory'] for package in packages) + '\n'
        base_project += '\nactive-repositories: :none\n'
        for package in packages:
            base_project += 'package ' + package['name'] + '\n  tests: False\n  benchmarks: False\n'
        (copy / 'cabal.project').write_text(base_project)
        test_project = copy / 'test.project'
        test_project.write_text(base_project + ('\npackage warlock-native-authority\n  flags: +slotstore-test-hooks\n' if profile == 'common' else ''))
        build_env = dict(env)
        for key in list(build_env):
            if key.startswith(('GHC_', 'CABAL_', 'PKG_CONFIG_', 'HASKELL_')) or key in ('CPATH', 'LIBRARY_PATH'):
                build_env.pop(key, None)
        sysroot = sdk / 'sysroot/usr'
        build_env.update({'PATH': str(sdk / 'bin') + ':/usr/bin:/bin', 'GHC_ENVIRONMENT': '-',
                          'CABAL_DIR': str(work / 'cabal-home'),
                          'PKG_CONFIG_LIBDIR': str(sysroot / 'lib/x86_64-linux-gnu/pkgconfig'),
                          'LIBRARY_PATH': str(sysroot / 'lib/x86_64-linux-gnu'),
                          'CPATH': str(sysroot / 'include') + ':' + str(sysroot / 'include/x86_64-linux-gnu'),
                          'PYTHONDONTWRITEBYTECODE': '1'})
        common = [str(sdk / 'bin/cabal'), '--config-file=' + str(config)]
        toolargs = ['--offline', '--with-compiler=' + str(sdk / 'bin/ghc'),
                    '--with-hc-pkg=' + str(sdk / 'bin/ghc-pkg'), '--with-hsc2hs=' + str(sdk / 'bin/hsc2hs'),
                    '--with-gcc=/usr/bin/gcc', '--with-ar=/usr/bin/ar', '--with-ld=/usr/bin/ld',
                    '--with-pkg-config=/usr/bin/pkg-config', '--jobs=2']
        def command(name, action, args, test=False, timeout=900, extra_env=None):
            project = test_project if test else copy / 'cabal.project'
            dist = work / ('dist-test' if test else 'dist-production')
            argv = common + [action, '--project-file=' + str(project), '--builddir=' + str(dist)] + toolargs + args
            info = run(argv, copy, extra_env or build_env, logs, name, timeout)
            result['commands'].append(info)
            return info
        def required(info, name):
            if info['exit'] != 0 or info['forcedCleanup']:
                raise RuntimeError(name + ' failed; see retained logs')
        # Authentication changes repeat the existing registration claim for
        # each frame; qualify its unchanged invariants before executing code.
        from check_elm_cpu import quint_toolchain
        model_pin, model_cli = quint_toolchain()
        node = Path(model_pin['node']['path'])
        if digest(node) != model_pin['node']['sha256']:
            raise RuntimeError('Pinned model interpreter differs')
        model_env = dict(build_env, NO_COLOR='1')
        for key in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
            model_env.pop(key, None)
        model = 'runtime/formal/current_registration.qnt'
        tests = 'runtime/formal/current_registration_test.qnt'
        selected_tests = re.findall(r'^\s*run\s+(\w+)\s*=', (copy / tests).read_text(), re.MULTILINE)
        if not selected_tests or len(set(selected_tests)) != len(selected_tests):
            raise RuntimeError('Registration directed test selection is empty or duplicated')
        result['modelDirectedTests'] = selected_tests
        test_match = '^(?:' + '|'.join(selected_tests) + ')$'
        model_commands = [
            ('registration-typecheck', [str(node), str(model_cli), 'typecheck', tests]),
            ('registration-directed', [str(node), str(model_cli), 'test', tests,
                                       '--main=current_registration_test', '--match=' + test_match, '--backend=typescript', '--verbosity=2']),
            ('registration-safety', [str(node), str(model_cli), 'run', model, '--main=current_registration',
                                     '--backend=typescript', '--invariant=safety', '--witnesses',
                                     'witnessReserved', 'witnessBuilt', 'witnessLive', 'witnessChecked', 'witnessClaim',
                                     'witnessDelivered', 'witnessRetired', 'witnessReaped', 'witnessExhausted',
                                     'witnessRefused', 'witnessMixed', 'witnessMultipleFrames',
                                     '--seed=20261031', '--max-samples=10000', '--max-steps=100', '--verbosity=1']),
            ('registration-conversation', [str(node), str(model_cli), 'run', model, '--main=current_registration',
                                           '--backend=typescript', '--invariant=safety', '--step=conversationStep',
                                           '--witnesses', 'witnessLive', 'witnessClaim', 'witnessDelivered', 'witnessMultipleFrames',
                                           '--seed=20261031', '--max-samples=10000', '--max-steps=30', '--verbosity=1'])]
        for name, argv in model_commands:
            info = run(argv, copy, model_env, logs, name, timeout=240)
            result['commands'].append(info)
            required(info, name)
        executed = re.findall(r'\b(\d+) passing\b', (logs / 'registration-directed.stdout').read_text())
        if executed != [str(len(selected_tests))]:
            raise RuntimeError('Registration directed execution count differs from explicit run selection')
        witness_text = (logs / 'registration-safety.stdout').read_text()
        witnesses = {name: int(count) for name, count in re.findall(r'(witness\w+) was witnessed in (\d+) trace', witness_text)}
        result['modelWitnessCounts'] = witnesses
        focus_text = (logs / 'registration-conversation.stdout').read_text()
        focused = {name: int(count) for name, count in re.findall(r'(witness\w+) was witnessed in (\d+) trace', focus_text)}
        result['focusedModelWitnessCounts'] = focused
        if (len(witnesses) != 12 or any(count == 0 for name, count in witnesses.items() if name != 'witnessMultipleFrames')
                or len(focused) != 4 or any(count == 0 for count in focused.values())):
            raise RuntimeError('Registration reachability witness missing or zero in its declared campaign')
        result['modelToolchain'] = model_pin
        quint_toolchain()
        required(command('production-build', 'build', ['all']), 'production build')
        required(command('production-freeze', 'freeze', []), 'production freeze')
        targets = ([p + ':test:' + suite for p, suites in SUITES.items() for suite in suites] if profile == 'common'
                   else ['warlock-runtime:test:persistent-bootstrap-controls'])
        fixtures = FIXTURES if profile == 'common' else {'credential-peer-child': FIXTURES['credential-peer-child']}
        required(command('test-build', 'build', targets + list(fixtures.values()), test=True), 'test build')
        required(command('test-freeze', 'freeze', [], test=True), 'test freeze')
        bins = {}
        for index, target in enumerate(targets + list(fixtures.values())):
            info = command('list-bin-' + str(index), 'list-bin', [target], test=True)
            required(info, 'list-bin ' + target)
            lines = Path(info['stdout']).read_text().splitlines()
            if len(lines) != 1:
                raise RuntimeError('unexpected list-bin output: ' + target)
            path = Path(lines[0])
            if not path.is_absolute() or not path.is_relative_to(work / 'dist-test') or path.name != target.rsplit(':', 1)[1]:
                raise RuntimeError('unexpected executable from list-bin: ' + str(path))
            bins[target] = {'path': str(path), 'pin': pin(path)}
        result['executables'] = bins
        dispatches = {}
        for target in targets:
            suite = target.rsplit(':', 1)[1]
            dispatch = {'suite': suite, 'test': bins[target],
                        'fixtures': {name: bins[t] for name, t in fixtures.items()},
                        'authProfile': profile,
                        'protocolFixtures': str(copy / 'protocol/test/fixtures'),
                        'runRoot': str(work / 'runs' / suite)}
            (work / 'runs').mkdir(exist_ok=True, mode=0o700)
            dispatches[bins[target]['path']] = dispatch
        dispatch_path = work / 'dispatch-all.json'
        dispatch_path.write_text(json.dumps({'suites': dispatches}, indent=2) + '\n')
        test_env = dict(build_env, WARLOCK_HASKELL_DISPATCH=str(dispatch_path))
        info = command('test-all' if profile == 'common' else 'test-public-auth', 'test',
                       (['all'] if profile == 'common' else targets) + ['--keep-going', '--test-show-details=direct', '--test-wrapper=' + str(WRAPPER)],
                       test=True, timeout=900, extra_env=test_env)
        result['testCommandExit'] = info['exit']
        for target in targets:
            suite = target.rsplit(':', 1)[1]
            receipt = work / 'runs' / suite / 'results.json'
            runs = json.loads(receipt.read_text()) if receipt.is_file() else []
            expected = 13 if suite == 'independent-pairstore' else 1
            passed = (not info['forcedCleanup'] and len(runs) == expected
                      and all(r['exit'] == 0 and not r['forcedCleanup'] for r in runs))
            result['suites'][target] = {'passed': passed, 'runs': runs}
        result['passed'] = (info['exit'] == 0 and not info['forcedCleanup'] and len(result['suites']) == len(targets)
                            and all(s['passed'] for s in result['suites'].values()))
        result['crossUserRequired'] = profile == 'auth'
        result['originalAcceptance'] = False
    except Exception as error:
        result['error'] = str(error)
    if work.is_dir():
        (work / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result

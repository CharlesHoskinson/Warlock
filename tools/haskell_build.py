"""Offline, source-copy Haskell build and fixture QA; called only by protected runner.

build(sdk, output, env) returns an auditable dictionary. The caller owns the
network/PID namespace, SDK verification, output directory and final report.
"""
import hashlib
import importlib.util
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
    'warlock-protocol': ['boundary-controls', 'ingress-controls', 'owner-sequences', 'credential-guard-controls', 'desktop-boundary-controls'],
    'warlock-elf-observation-proposal': ['elf-cases'],
    'warlock-runtime': ['current-session-oracles', 'persistent-bootstrap-controls', 'ui-backend-controls', 'ui-origin-controls', 'ui-engine-controls', 'ui-private-network-controls', 'ui-display-controls', 'ui-mvp-controls', 'ui-webkit-controls'],
    'warlock-native-authority': ['native-cancellation-controls', 'durable-storage-controls', 'selection-admission-controls', 'host-guard-controls', 'slot-store-controls', 'pair-store-smoke', 'child-directory-controls', 'independent-admission-shape', 'pair-store-sequences', 'independent-lifetime-owner', 'independent-pairstore'],
}
FIXTURES = {
    'custody-child': 'warlock-process-custody:exe:custody-child',
    'selected-fd-child': 'warlock-process-custody:exe:selected-fd-child',
    'graceful-stop-child': 'warlock-process-custody:exe:graceful-stop-child',
    'bootstrap-facade-child': 'warlock-process-custody:exe:bootstrap-facade-child',
    'credential-peer-child': 'warlock-runtime:exe:credential-peer-child',
    'warlock-ui-backend': 'warlock-runtime:exe:warlock-ui-backend',
    'ui-stream-child': 'warlock-runtime:exe:ui-stream-child',
    'warlock-ui-owner': 'warlock-runtime:exe:warlock-ui-owner',
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


def run_ui_models(copy, source, node, model_cli, model_env, logs, result, required):
        origin_dir = copy / 'runtime/formal'
        origin_model, origin_test = origin_dir / 'ui-origin.qnt', origin_dir / 'ui-origin_test.qnt'
        origin_hashes = {p.name: digest(p) for p in (origin_model, origin_test)}
        names = re.findall(r'^\s*run\s+(\w+)\s*=', origin_test.read_text(), re.M)
        witnesses = re.findall(r'^\s*val\s+(witness\w+)\s*(?::[^=]+)?=', origin_model.read_text(), re.M)
        if not names or len(names) != len(set(names)) or not witnesses or len(witnesses) != len(set(witnesses)):
            raise RuntimeError('Origin model directed/witness selection empty or duplicated')
        selector = '^(?:' + '|'.join(re.escape(n) for n in names) + ')$'
        commands = [
            ('origin-model-typecheck', [str(node), str(model_cli), 'typecheck', str(origin_model)]),
            ('origin-model-test-typecheck', [str(node), str(model_cli), 'typecheck', str(origin_test)]),
            ('origin-model-directed', [str(node), str(model_cli), 'test', str(origin_test), '--main=ui_origin_test',
                                      '--match=' + selector, '--backend=typescript', '--verbosity=2']),
            ('origin-model-safety', [str(node), str(model_cli), 'run', str(origin_model), '--main=ui_origin',
                                    '--backend=typescript', '--invariant=safety', '--witnesses', *witnesses,
                                    '--seed=20261101', '--max-samples=10000', '--max-steps=50', '--verbosity=1'])]
        for name, argv in commands:
            info = run(argv, origin_dir, model_env, logs, name, timeout=240)
            result['commands'].append(info)
            required(info, name)
        counts = {name: int(n) for name, n in re.findall(r'(\w+) was witnessed in (\d+) trace',
                  (logs / 'origin-model-safety.stdout').read_text())}
        result['originModel'] = {'sourceHashes': origin_hashes, 'directed': names, 'witnesses': counts,
                                 'samples': 10000, 'maxSteps': 50, 'seed': 20261101,
                                 'scope': 'Reduced role/queue/provenance abstraction; browser preflight, namespace and engine assumptions are not established'}
        if re.findall(r'\b(\d+) passing\b', (logs / 'origin-model-directed.stdout').read_text()) != [str(len(names))]:
            raise RuntimeError('Origin model exact directed count not executed')
        if set(counts) != set(witnesses) or any(n == 0 for n in counts.values()):
            raise RuntimeError('Origin model witness missing or zero; retain coverage gap')
        for filename, expected in origin_hashes.items():
            if digest(origin_dir / filename) != expected or digest(source / 'runtime/formal' / filename) != expected:
                raise RuntimeError('Origin model changed during execution')
        # Fixed companion models; each selection and reachability witness is
        # taken from its source and must actually execute before any tests.
        formal = copy / 'runtime/formal'
        result['uiCompanionModels'] = {}
        for stem in ('ui-engine-lifetime', 'ui-private-network', 'ui-http-admission', 'ui-frontend-delivery', 'ui-standalone-bootstrap'):
            module = stem.replace('-', '_')
            model_path, test_path = formal / (stem + '.qnt'), formal / (stem + '_test.qnt')
            hashes = {path.name: digest(path) for path in (model_path, test_path)}
            names = re.findall(r'^\s*run\s+(\w+)\s*=', test_path.read_text(), re.M)
            witnesses = re.findall(r'^\s*val\s+(witness\w+)\s*(?::[^=]+)?=', model_path.read_text(), re.M)
            if not names or len(names) != len(set(names)) or not witnesses or len(witnesses) != len(set(witnesses)):
                raise RuntimeError(stem + ' model selection empty or duplicated')
            if stem == 'ui-engine-lifetime' and set(witnesses) != {
                    'witnessReady', 'witnessRefused', 'witnessExternal', 'witnessExit',
                    'witnessCallbackRetired', 'witnessClean', 'witnessQuarantine',
                    'witnessDeadline', 'witnessPartialAsync'}:
                raise RuntimeError('Lifetime broad witness declarations differ from reviewed set')
            selector = '^(?:' + '|'.join(re.escape(n) for n in names) + ')$'
            commands = [
                (stem + '-typecheck', [str(node), str(model_cli), 'typecheck', str(model_path)]),
                (stem + '-test-typecheck', [str(node), str(model_cli), 'typecheck', str(test_path)]),
                (stem + '-directed', [str(node), str(model_cli), 'test', str(test_path), '--main=' + module + '_test',
                                       '--match=' + selector, '--backend=typescript', '--verbosity=2'])]
            campaigns = ('initController', 'initRenderer') if stem == 'ui-frontend-delivery' else (None,)
            role_witnesses = {'initController': ['witnessDelivery', 'witnessReceipt', 'witnessUnknown', 'witnessGateway'],
                              'initRenderer': ['witnessDelivery', 'witnessGateway', 'witnessFocus', 'witnessPreedit']}
            if stem == 'ui-frontend-delivery' and set(witnesses) != set(sum(role_witnesses.values(), [])):
                raise RuntimeError('Frontend witness declaration differs from fixed role obligations')
            samples = 100000 if stem == 'ui-private-network' else 10000
            for init in campaigns:
                selected = role_witnesses[init] if init else witnesses
                label = stem + '-safety' + ('-' + init if init else '')
                args = [str(node), str(model_cli), 'run', str(model_path), '--main=' + module,
                        '--backend=typescript', '--invariant=safety', '--witnesses', *selected,
                        '--seed=20261101', '--max-samples=' + str(samples), '--max-steps=50', '--verbosity=1']
                if init:
                    args.append('--init=' + init)
                commands.append((label, args))
            for name, argv in commands:
                info = run(argv, formal, model_env, logs, name, timeout=240)
                result['commands'].append(info)
                required(info, name)
            if re.findall(r'\b(\d+) passing\b', (logs / (stem + '-directed.stdout')).read_text()) != [str(len(names))]:
                raise RuntimeError(stem + ' directed count differs')
            per_init = {}
            for init in campaigns:
                label = stem + '-safety' + ('-' + init if init else '')
                observed = {name: int(n) for name, n in re.findall(r'(\w+) was witnessed in (\d+) trace',
                            (logs / (label + '.stdout')).read_text())}
                expected = role_witnesses[init] if init else witnesses
                if set(observed) != set(expected):
                    raise RuntimeError(stem + ' witness output incomplete for ' + str(init))
                if any(n == 0 for name, n in observed.items()
                       if not (stem == 'ui-engine-lifetime' and name == 'witnessClean')):
                    raise RuntimeError(stem + ' required broad witness zero for ' + str(init))
                per_init[init or 'default'] = observed
            counts = {name: sum(values.get(name, 0) for values in per_init.values()) for name in witnesses}
            entry = {'sourceHashes': hashes, 'directed': names, 'witnesses': counts,
                     'perInitWitnesses': per_init, 'samplesPerInit': samples, 'maxSteps': 50, 'seed': 20261101}
            result['uiCompanionModels'][stem] = entry
            if stem == 'ui-engine-lifetime':
                if 'witnessClean' not in counts:
                    raise RuntimeError('Lifetime model missing clean witness')
                entry['broadCounts'] = dict(counts)
                entry['broadStep'] = 'step'
                entry['scope'] = ('Broad safety and other witness coverage plus separate guided clean reachability; '
                                  'guided scheduling excludes failures and elapsed time and proves no runtime/native acceptance')
                label = stem + '-guided-clean'
                args = [str(node), str(model_cli), 'run', str(model_path), '--main=' + module,
                        '--backend=typescript', '--step=cleanConversationStep', '--invariant=safety',
                        '--witnesses', 'witnessClean', '--seed=20261101', '--max-samples=10000',
                        '--max-steps=50', '--verbosity=1']
                info = run(args, formal, model_env, logs, label, timeout=240)
                result['commands'].append(info)
                required(info, label)
                guided = {name: int(n) for name, n in re.findall(r'(\w+) was witnessed in (\d+) trace',
                          (logs / (label + '.stdout')).read_text())}
                entry['guidedCounts'] = guided
                entry['guidedStep'] = 'cleanConversationStep'
                entry['guidedSeed'] = 20261101
                if set(guided) != {'witnessClean'} or guided['witnessClean'] == 0:
                    raise RuntimeError('Lifetime guided clean witness missing or zero')
            elif any(n == 0 for n in counts.values()):
                raise RuntimeError(stem + ' witness missing or zero across campaigns')
            for filename, expected in hashes.items():
                if digest(formal / filename) != expected or digest(source / 'runtime/formal' / filename) != expected:
                    raise RuntimeError(stem + ' source changed during execution')


def models_only(output, env):
    result = {'schema': 1, 'passed': False, 'profile': 'ui-models', 'commands': [],
              'nativeAccepted': False, 'releaseAccepted': False, 'originalAcceptance': False,
              'scope': 'Model-only component feedback; no compilation or runtime tests'}
    work = Path(output).resolve() / 'haskell-build'
    try:
        work.mkdir(mode=0o700)
        logs = work / 'logs'
        logs.mkdir(mode=0o700)
        source = ROOT / 'implementation/warlock/haskell'
        copy = work / 'source'
        formal = copy / 'runtime/formal'
        formal.mkdir(parents=True, mode=0o700)
        stems = ('ui-origin', 'ui-engine-lifetime', 'ui-private-network', 'ui-http-admission', 'ui-frontend-delivery', 'ui-standalone-bootstrap')
        paths = [stem + suffix for stem in stems for suffix in ('.qnt', '_test.qnt')]
        hashes = {}
        for name in paths:
            original = source / 'runtime/formal' / name
            if original.is_symlink() or not original.is_file():
                raise RuntimeError('Expected regular model source: ' + name)
            hashes[name] = digest(original)
            shutil.copyfile(original, formal / name)
            if digest(formal / name) != hashes[name] or digest(original) != hashes[name]:
                raise RuntimeError('Model changed during staging: ' + name)
        result['sourceHashes'] = hashes
        from check_elm_cpu import quint_toolchain
        model_pin, model_cli = quint_toolchain()
        node = Path(model_pin['node']['path'])
        if digest(node) != model_pin['node']['sha256']:
            raise RuntimeError('Pinned model interpreter differs')
        model_env = dict(env, NO_COLOR='1')
        for key in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
            model_env.pop(key, None)
        def required(info, name):
            if info['exit'] != 0 or info['forcedCleanup']:
                raise RuntimeError(name + ' failed; see retained logs')
        run_ui_models(copy, source, node, model_cli, model_env, logs, result, required)
        if quint_toolchain()[0] != model_pin:
            raise RuntimeError('Model toolchain changed during execution')
        for name, expected in hashes.items():
            if digest(source / 'runtime/formal' / name) != expected or digest(formal / name) != expected:
                raise RuntimeError('Model changed during execution: ' + name)
        result['modelToolchain'] = model_pin
        result['passed'] = True
    except Exception as error:
        result['passed'] = False
        result['error'] = str(error)
    if work.is_dir():
        (work / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def site_only(output, env):
    result = {'schema': 1, 'passed': False, 'profile': 'site', 'commands': [],
              'nativeAccepted': False, 'releaseAccepted': False, 'originalAcceptance': False,
              'scope': 'Offline standalone site Elm compilation only'}
    work = Path(output).resolve() / 'site-build'
    try:
        work.mkdir(mode=0o700)
        logs = work / 'logs'
        logs.mkdir(mode=0o700)
        source = ROOT / 'site/src'
        config = ROOT / 'site/elm.json'
        if source.is_symlink() or not source.is_dir() or config.is_symlink() or not config.is_file():
            raise RuntimeError('Site inputs must be regular, nonsymlink sources')
        before = inventory(source)
        if 'SiteMain.elm' not in before:
            raise RuntimeError('Missing fixed site entry')
        config_hash = digest(config)
        stage = work / 'source'
        stage.mkdir(mode=0o700)
        shutil.copytree(source, stage / 'src', symlinks=True)
        shutil.copyfile(config, stage / 'elm.json')
        held = ROOT / 'implementation/warlock-preview-provider-v143'
        spec = importlib.util.spec_from_file_location('site_held_toolchain', held / 'qa/toolchain.py')
        toolchain = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(toolchain)
        compiler = toolchain.verify()
        shutil.copytree(held / compiler['elmHome'], work / 'elm-home')
        if inventory(stage / 'src') != before or inventory(source) != before or digest(stage / 'elm.json') != config_hash or digest(config) != config_hash:
            raise RuntimeError('Site source changed during staging')
        compile_env = dict(env, ELM_HOME=str(work / 'elm-home'), NO_COLOR='1')
        for key in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
            compile_env.pop(key, None)
        html = work / 'site.html'
        info = run([held / compiler['compiler'], 'make', 'src/SiteMain.elm', '--optimize', '--output=' + str(html)],
                   stage, compile_env, logs, 'site-compile', timeout=180)
        result['commands'].append(info)
        if info['exit'] != 0 or info['forcedCleanup']:
            raise RuntimeError('Standalone site compilation failed; see retained logs')
        if html.is_symlink() or not html.is_file() or html.stat().st_size == 0:
            raise RuntimeError('Site output missing or empty')
        if toolchain.verify() != compiler or inventory(stage / 'src') != before or inventory(source) != before or digest(config) != config_hash or digest(stage / 'elm.json') != config_hash:
            raise RuntimeError('Site source or compiler changed during execution')
        result.update(passed=True, compiler=compiler, sourceHashes=before, elmJsonSHA256=config_hash,
                      html={'path': str(html), 'sha256': digest(html), 'size': html.stat().st_size})
    except Exception as error:
        result['passed'] = False
        result['error'] = str(error)
    if work.is_dir():
        (work / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def build(sdk, output, env, profile='common'):
    if profile == 'ui-models':
        return models_only(output, env)
    if profile == 'site':
        return site_only(output, env)
    if profile not in ('common', 'auth', 'ui-origin'):
        raise RuntimeError('Unknown fixed Haskell verification profile')
    sdk, output = Path(sdk).resolve(), Path(output).resolve()
    result = {'schema': 1, 'passed': False, 'profile': profile, 'commands': [], 'suites': {},
              'nativeAccepted': False, 'releaseAccepted': False}
    work = output / 'haskell-build'
    try:
        work.mkdir(mode=0o700)  # no reuse of previous artifacts
        from ui_host_toolchain import verify as verify_ui_toolchain
        result['uiToolchain'] = verify_ui_toolchain()
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
        ui_lib = result['uiToolchain']['libraryDirectory']
        base_project += '\npackage warlock-runtime\n  extra-lib-dirs: ' + ui_lib + '\n  ghc-options: -optl-Wl,--disable-new-dtags -optl-Wl,-rpath,' + ui_lib + '\n'
        for package in packages:
            base_project += 'package ' + package['name'] + '\n  tests: False\n  benchmarks: False\n'
        (copy / 'cabal.project').write_text(base_project)
        test_project = copy / 'test.project'
        test_project.write_text(base_project + ('\npackage warlock-native-authority\n  flags: +slotstore-test-hooks\n' if profile == 'common' else ''))
        project_hashes = {str(p): digest(p) for p in (copy / 'cabal.project', test_project)}
        result['generatedProjectHashes'] = project_hashes
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
        # Compile first so syntax/API diagnostics do not repeat unrelated
        # sampled campaigns. Models still qualify the boundary before tests
        # execute any newly built product or fixture executable.
        required(command('production-build', 'build', ['all']), 'production build')
        required(command('production-freeze', 'freeze', []), 'production freeze')
        targets = ([p + ':test:' + suite for p, suites in SUITES.items() for suite in suites] if profile == 'common'
                   else (['warlock-runtime:test:ui-origin-controls', 'warlock-runtime:test:ui-engine-controls', 'warlock-runtime:test:ui-private-network-controls', 'warlock-runtime:test:ui-display-controls', 'warlock-runtime:test:ui-mvp-controls', 'warlock-runtime:test:ui-webkit-controls', 'warlock-protocol:test:desktop-boundary-controls']
                         if profile == 'ui-origin' else ['warlock-runtime:test:persistent-bootstrap-controls']))
        fixtures = (FIXTURES if profile == 'common' else
                    ({'warlock-ui-backend': FIXTURES['warlock-ui-backend'], 'ui-stream-child': FIXTURES['ui-stream-child']} if profile == 'ui-origin'
                     else {'credential-peer-child': FIXTURES['credential-peer-child']}))
        required(command('test-build', 'build', targets + list(fixtures.values()), test=True), 'test build')
        required(command('test-freeze', 'freeze', [], test=True), 'test freeze')
        # Authentication changes repeat the existing registration claim for
        # each frame; qualify its unchanged invariants before behavioral tests.
        from check_elm_cpu import quint_toolchain
        model_pin, model_cli = quint_toolchain()
        node = Path(model_pin['node']['path'])
        if digest(node) != model_pin['node']['sha256']:
            raise RuntimeError('Pinned model interpreter differs')
        model_env = dict(build_env, NO_COLOR='1')
        for key in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
            model_env.pop(key, None)
        if profile != 'ui-origin':
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
        if profile == 'common':
            ui_models = work / 'ui-models'
            ui_models.mkdir(mode=0o700)
            ui_hashes = {}
            for filename in ('ui-native-stream.qnt', 'ui-native-stream_test.qnt'):
                original = ROOT / 'implementation/warlock/qa' / filename
                if original.is_symlink() or not original.is_file():
                    raise RuntimeError('Expected regular UI model source')
                ui_hashes[filename] = digest(original)
                shutil.copyfile(original, ui_models / filename)
                if digest(ui_models / filename) != ui_hashes[filename] or digest(original) != ui_hashes[filename]:
                    raise RuntimeError('UI model changed during staging')
            ui_test = ui_models / 'ui-native-stream_test.qnt'
            ui_model = ui_models / 'ui-native-stream.qnt'
            names = re.findall(r'^\s*run\s+(\w+)\s*=', ui_test.read_text(), re.M)
            reach = [n for n in re.findall(r'^\s*val\s+(\w+)\s*:', ui_model.read_text(), re.M)
                     if n.startswith('witness') or n.endswith('Witness')]
            if not names or len(names) != len(set(names)) or not reach or len(reach) != len(set(reach)):
                raise RuntimeError('UI model directed/reachability selection empty or duplicated')
            selector = '^(?:' + '|'.join(re.escape(n) for n in names) + ')$'
            ui_commands = [
                ('ui-model-typecheck', [str(node), str(model_cli), 'typecheck', str(ui_model)]),
                ('ui-model-test-typecheck', [str(node), str(model_cli), 'typecheck', str(ui_test)]),
                ('ui-model-directed', [str(node), str(model_cli), 'test', str(ui_test), '--main=uiNativeStreamTest',
                                       '--match=' + selector, '--backend=typescript', '--verbosity=2']),
                ('ui-model-safety', [str(node), str(model_cli), 'run', str(ui_model), '--main=uiNativeStream',
                                    '--backend=typescript', '--invariant=safety', '--witnesses', *reach,
                                    '--seed=20261101', '--max-samples=10000', '--max-steps=50', '--verbosity=1'])]
            for name, argv in ui_commands:
                info = run(argv, ui_models, model_env, logs, name, timeout=240)
                result['commands'].append(info)
                required(info, name)
            counts = {name: int(n) for name, n in re.findall(r'(\w+) was witnessed in (\d+) trace',
                      (logs / 'ui-model-safety.stdout').read_text())}
            result['uiModel'] = {'sourceHashes': ui_hashes, 'directed': names, 'witnesses': counts,
                                 'samples': 10000, 'maxSteps': 50, 'seed': 20261101}
            if re.findall(r'\b(\d+) passing\b', (logs / 'ui-model-directed.stdout').read_text()) != [str(len(names))]:
                raise RuntimeError('UI model exact directed count not executed')
            if set(counts) != set(reach) or any(n == 0 for n in counts.values()):
                raise RuntimeError('UI model witness missing or zero; retain coverage gap')
            for filename, expected in ui_hashes.items():
                if (digest(ROOT / 'implementation/warlock/qa' / filename) != expected
                        or digest(ui_models / filename) != expected):
                    raise RuntimeError('UI model changed during execution')
        if profile in ('common', 'ui-origin'):
            run_ui_models(copy, source, node, model_cli, model_env, logs, result, required)
        quint_toolchain()
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
        # Inspect ELF metadata only; never invoke the dynamic loader as a probe.
        # DT_RPATH is needed for the pinned WebKit dependency's own SDK DSOs.
        if profile in ('common', 'ui-origin'):
            readelf = Path('/usr/bin/readelf').resolve()
            readelf_pin = pin(readelf)
            result['readelf'] = {'path': str(readelf), 'pin': readelf_pin}
            target = 'warlock-runtime:test:ui-webkit-controls'
            info = run([str(readelf), '-d', bins[target]['path']], copy, build_env, logs,
                       'ui-webkit-dynamic-tags', timeout=30)
            result['commands'].append(info)
            required(info, 'ui-webkit dynamic metadata')
            tags = Path(info['stdout']).read_text()
            rpaths = re.findall(r'\(RPATH\).*?\[([^\]]*)\]', tags)
            runpaths = re.findall(r'\(RUNPATH\).*?\[([^\]]*)\]', tags)
            if rpaths != [ui_lib] or runpaths:
                raise RuntimeError('UI fixture lacks exact transitive SDK RPATH')
            if pin(readelf) != readelf_pin or pin(bins[target]['path']) != bins[target]['pin']:
                raise RuntimeError('UI fixture or ELF inspector changed during metadata inspection')
            result['uiWebkitRpath'] = {'path': ui_lib, 'fixture': target, 'inspectorPin': readelf_pin,
                                       'scope': 'ELF dynamic tag only; loader execution remains a runtime test'}
        frontend = None
        if profile in ('common', 'ui-origin'):
            from ui_backend_frontend import prepare as prepare_frontend
            frontend, result['uiFrontend'] = prepare_frontend(ROOT, work, build_env, run, digest)
        dispatches = {}
        for target in targets:
            suite = target.rsplit(':', 1)[1]
            dispatch = {'suite': suite, 'test': bins[target],
                        'fixtures': {name: bins[t] for name, t in fixtures.items()},
                        'authProfile': profile,
                        'frontend': frontend if suite == 'ui-backend-controls' else None,
                        'uiDocuments': result.get('uiFrontend', {}).get('documents') if suite == 'ui-origin-controls' else None,
                        'protocolFixtures': str(copy / 'protocol/test/fixtures'),
                        'runRoot': str(work / 'runs' / suite)}
            (work / 'runs').mkdir(exist_ok=True, mode=0o700)
            dispatches[bins[target]['path']] = dispatch
        dispatch_path = work / 'dispatch-all.json'
        dispatch_path.write_text(json.dumps({'suites': dispatches}, indent=2) + '\n')
        test_env = dict(build_env, WARLOCK_HASKELL_DISPATCH=str(dispatch_path))
        info = command('test-all' if profile == 'common' else ('test-ui-origin' if profile == 'ui-origin' else 'test-public-auth'), 'test',
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
        if inventory(source, exclude_builds=True) != before or inventory(copy, exclude_builds=True) != source_hashes:
            # Generated Cabal project files differ by design; compare originals below.
            if inventory(source, exclude_builds=True) != before:
                raise RuntimeError('Haskell source changed during execution')
            staged = inventory(copy, exclude_builds=True)
            for name, expected in source_hashes.items():
                if name != 'cabal.project' and staged.get(name) != expected:
                    raise RuntimeError('Staged Haskell source changed during execution: ' + name)
        if any(digest(path) != expected for path, expected in project_hashes.items()):
            raise RuntimeError('Generated Cabal project changed during execution')
        result['crossUserRequired'] = profile == 'auth'
        result['originalAcceptance'] = False
    except Exception as error:
        result['passed'] = False
        result['error'] = str(error)
    if result.get('uiToolchain'):
        try:
            if verify_ui_toolchain() != result['uiToolchain']:
                raise RuntimeError('UI link inputs changed during verification')
        except Exception as error:
            result['passed'] = False
            result['uiToolchainError'] = str(error)
    if work.is_dir():
        (work / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result

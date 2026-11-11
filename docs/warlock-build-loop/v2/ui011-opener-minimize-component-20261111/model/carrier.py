#!/usr/bin/python3
"""Root-only fixed private RED probe. No managed admission or production overlay."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import time

ROOT = Path('/home/hoskinson/Projects/Warlock')
HERE = Path(__file__).resolve().parent
BUNDLE = HERE
INPUT_SHA = '26d79da54498107b27ddd22903787cfb4e7d082e29be0246ef7a843842af1124'
OUTPUTS = HERE / 'actual-root-runs'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def load(name, relative, pins):
    path = ROOT / relative
    if digest(path) != pins[relative]:
        raise ValueError('Helper source changed: ' + relative)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def input_data():
    if digest(HERE / 'inputs.json') != INPUT_SHA:
        raise ValueError('Fixed inputs changed')
    data = json.loads((HERE / 'inputs.json').read_text())
    for name, expected in {**{str(ROOT / p): h for p, h in data['sourceHashes'].items()}, **data['immutableFiles']}.items():
        path = Path(name)
        if path.is_symlink() or not path.is_file() or digest(path) != expected:
            raise ValueError('Current or immutable source differs: ' + name)
    for suffix, key in (('haskell', 'haskellFiles'), ('src', 'elmFiles')):
        base = ROOT / 'implementation/warlock' / suffix
        names = set()
        for path in base.rglob('*'):
            relative = path.relative_to(base)
            if any(part in ('dist-newstyle', '__pycache__') for part in relative.parts):
                continue
            if path.is_symlink() or (not path.is_file() and not path.is_dir()):
                raise ValueError('Source alias or special file')
            if path.is_file():
                names.add(str(relative))
        if names != set(data[key]):
            raise ValueError('Complete source membership changed: ' + suffix)
    return data


def modules(data):
    sys.path.insert(0, str(ROOT / 'tools'))
    sys.path.insert(0, str(ROOT / 'window-integration-qa'))
    pins = data['sourceHashes']
    qa = load('qa_launch', 'window-integration-qa/qa_launch.py', pins)
    arm = load('arm64_toolchain', 'tools/arm64_toolchain.py', pins)
    build = load('fixed_watch_build', 'tools/run_ux024_menu_focus_build.py', pins)
    elm = load('fixed_watch_elm', 'tools/check_elm_cpu.py', pins)
    return qa, arm, build, elm


def tools_for(profile, data, arm, build, elm):
    # Existing fixed verifier checks the exact current cache correspondence,
    # system inventory, full compiler/dependency trees, and source membership.
    if profile in ('protocol', 'quint'):
        selected = build.verify_inputs(data)
    else:
        selected = elm.verify_menu_tab_toolchain()
    if profile == 'quint':
        # Actual ARM Quint profile. Preserve its old file and use the accepted
        # loader-cache correspondence above, not its obsolete loader cache pin.
        pin = json.loads((ROOT / 'tools/team-quint-toolchain.json').read_text())
        if pin['profile'] != 'team-quint-arm64-20261105' or pin['backend'] != 'typescript' or pin['version'] != '0.32.0':
            raise ValueError('Wrong existing Quint profile')
        if digest(ROOT / pin['historicalParent']['path']) != pin['historicalParent']['sha256']:
            raise ValueError('Quint parent changed')
        for name, expected in pin['files'].items():
            if name != '/etc/ld.so.cache' and digest(name) != expected:
                raise ValueError('Quint external pin differs: ' + name)
        rows = {}
        package = Path(pin['quint'])
        for path in sorted(package.rglob('*')):
            key = str(path.relative_to(package))
            if path.is_symlink():
                if not path.resolve().is_relative_to(package):
                    raise ValueError('Quint symlink escapes package')
                rows[key] = {'link': os.readlink(path)}
            elif path.is_file():
                rows[key] = {'sha256': digest(path), 'mode': stat.S_IMODE(path.stat().st_mode)}
            elif not path.is_dir():
                raise ValueError('Quint special file')
        actual = {'files': len(rows), 'sha256': hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}
        if actual != pin['tree'] or json.loads((package / 'package.json').read_text())['version'] != pin['version']:
            raise ValueError('Complete ARM Quint tree changed')
        menu = elm.verify_menu_tab_toolchain()
        if menu['node'] != pin['node'] or digest(menu['node']) != pin['files'][pin['node']]:
            raise ValueError('Existing ARM menu/Quint selected interpreter differs')
        selected = dict(selected, quintProfile=pin, menuInterpreter=menu)
    return selected


def terminate(child):
    if child.poll() is None:
        os.killpg(child.pid, signal.SIGKILL)
    child.wait(timeout=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('profile', choices=('quint',))
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--inside-private', type=Path)
    args = parser.parse_args()
    if digest(HERE / 'manifest.json') != args.manifest_sha256:
        raise ValueError('Reviewed execution manifest differs')
    frozen = json.loads((HERE / 'manifest.json').read_text())
    for row in frozen['files']:
        if digest(row['path']) != row['sha256']:
            raise ValueError('Frozen execution source differs')
    data = input_data()
    qa, arm, build, elm = modules(data)
    scope = qa.require_qa_scope()
    selected = tools_for(args.profile, data, arm, build, elm)
    expires = datetime.datetime.fromisoformat(data['authorizationLimitUTC'].replace('Z', '+00:00')).timestamp()
    if time.time() >= expires:
        raise ValueError('Renewed operational limit expired; Root must re-authorize a successor')
    if args.inside_private is None:
        # Root independently checks the effective record/goal under lock at spawn.
        # This private invocation is not a fabricated canonical managed job.
        OUTPUTS.mkdir(mode=0o700, exist_ok=True)
        output = OUTPUTS / (args.profile + '-' + str(time.time_ns()))
        output.mkdir(mode=0o700)
        deadline = min(time.monotonic() + data['profiles'][args.profile], time.monotonic() + expires - time.time())
        save(output / 'limits.json', {'profile': args.profile, 'deadline': deadline, 'expires': expires, 'scope': scope})
        save(output / 'record-at-spawn.json', {'path': str(ROOT / data['record']), 'sha256': digest(ROOT / data['record']), 'authorityValidation': 'Root performs actual goal/effective-authorization check under record lock; this file is provenance only'})
        argv = ['/usr/bin/bwrap', '--die-with-parent', '--unshare-net', '--unshare-pid', '--ro-bind', '/', '/', '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--tmpfs', '/run', '--bind', str(output), str(output), '--chdir', str(output), '--', '/usr/bin/python3', '-B', str(Path(__file__).resolve()), args.profile, '--manifest-sha256', args.manifest_sha256, '--inside-private', str(output)]
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'HOME': str(output / 'home'), 'TMPDIR': '/tmp', 'PYTHONDONTWRITEBYTECODE': '1'}
        forced = False
        with (output / 'outer.stdout').open('xb') as stdout, (output / 'outer.stderr').open('xb') as stderr:
            child = subprocess.Popen(argv, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=max(0.001, deadline - time.monotonic()) + 2)
            except BaseException:
                forced = True
                terminate(child)
                raise
            finally:
                save(output / 'outer-terminal.json', {'exit': child.returncode, 'forced': forced, 'argv': argv})
        build.require_group_absent(child)
        input_data()
        tools_for(args.profile, data, arm, build, elm)
        print(json.dumps({'profile': args.profile, 'exit': code, 'output': str(output), 'privateEvidenceOnly': True}))
        return code
    output = args.inside_private
    if output.parent != OUTPUTS or output.resolve() != output or not re.fullmatch(args.profile + r'-[0-9]+', output.name):
        raise ValueError('Unrecognized private output')
    limits = json.loads((output / 'limits.json').read_text())
    if limits['profile'] != args.profile or limits['expires'] != expires or limits['deadline'] - time.monotonic() > data['profiles'][args.profile]:
        raise ValueError('Original profile deadline differs')
    deadline = limits['deadline']
    report = {'schema': 1, 'profile': args.profile, 'passed': False, 'classification': 'setup-or-compile-failed', 'privateEvidenceOnly': True, 'managedAdmissionClaimed': False, 'nativeAcceptance': False, 'originalAcceptance': False, 'integrationClaimed': False, 'sourceHashes': data['sourceHashes'], 'bundle': data['bundle'], 'commands': [], 'scope': scope, 'toolchain': selected, 'cleanupQualified': False}
    logs = output / 'logs'
    logs.mkdir(mode=0o700)
    env = dict(os.environ, NO_COLOR='1', GHC_ENVIRONMENT='-', CABAL_DIR=str(output / 'cabal-home'))
    for key in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
        env.pop(key, None)
    def run(label, argv, cwd=output, allow_failure=False):
        input_data()
        remaining = min(120, deadline - time.monotonic(), expires - time.time())
        if remaining <= 0:
            raise TimeoutError('Original private profile deadline exhausted')
        row = {'name': label, 'argv': [str(x) for x in argv], 'exit': None}
        report['commands'].append(row)
        with (logs / (label + '.stdout')).open('xb') as stdout, (logs / (label + '.stderr')).open('xb') as stderr:
            child = subprocess.Popen(row['argv'], cwd=cwd, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                row['exit'] = child.wait(timeout=remaining)
            except BaseException:
                row['forced'] = True
                terminate(child)
                raise
        build.require_group_absent(child)
        input_data()
        if row['exit'] and not allow_failure:
            raise RuntimeError(label + ': exit ' + str(row['exit']))
        return row['exit'], (logs / (label + '.stdout')).read_text()
    def copy(source, target):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if digest(source) != digest(target):
            raise ValueError('Staged body changed')
    try:
        if args.profile == 'elm':
            work = output / 'elm'
            for name in data['elmFiles']:
                copy(ROOT / 'implementation/warlock/src' / name, work / 'src' / name)
            copy(ROOT / 'implementation/warlock/qa/OutputRetirementReplay.elm', work / 'qa/OutputRetirementReplay.elm')
            copy(BUNDLE / 'tests-first/Ui011AutomaticWindowWatchReplay.elm', work / 'qa/Ui011AutomaticWindowWatchReplay.elm')
            config = json.loads((ROOT / 'implementation/warlock/elm.json').read_text())
            config['source-directories'] = ['src', 'qa']
            save(work / 'elm.json', config)
            # Same small Elm package-cache staging as run_menu_tab_dom; no SDK copy.
            shutil.copytree(selected['elmHome'], output / 'elm-home')
            if arm.inventory(output / 'elm-home') != selected['trees'][selected['elmHome']]:
                raise ValueError('Private Elm cache differs')
            env['ELM_HOME'] = str(output / 'elm-home')
            report['currentHtml'] = {}
            for entry in ('HttpMain', 'HttpBar', 'HttpPopup'):
                image = output / (entry + '.html')
                run('compile-' + entry, [selected['elm'], 'make', 'src/' + entry + '.elm', '--optimize', '--output=' + str(image)], work)
                report['currentHtml'][entry] = {'path': str(image), 'sha256': digest(image)}
            image = output / 'Ui011AutomaticWindowWatchReplay.js'
            run('compile-watch-replay', [selected['elm'], 'make', 'qa/Ui011AutomaticWindowWatchReplay.elm', '--optimize', '--output=' + str(image)], work)
            target = output / 'window-watch.json'
            fixture = BUNDLE / 'tests-first/ui011-automatic-window-watch.cjs'
            code, _ = run('watch-replay', [selected['node'], fixture, image, target], work, True)
            value = json.loads(target.read_text())
            if (value.get('imageSha256') != digest(image) or value.get('fixtureSha256') != digest(fixture) or value.get('caseCount') != 27 or value.get('seedSampleCount') != 32 or [x['name'] for x in value.get('checks', [])] != data['elm']['caseNames'] or value.get('observed', {}).get('preconditions') != {name: True for name in data['elm']['preconditionNames']} or value.get('observed', {}).get('seeded', {}).get('seeds') != list(range(32)) or len(value.get('observed', {}).get('seeded', {}).get('samples', [])) != 32):
                raise ValueError('All27 cases/3setup/32 sequences not observed')
            if value.get('classification') not in ('watch-capability-or-scheduling-red', 'semantic-red', 'component-pass') or (code == 0) != (value.get('passed') is True):
                raise ValueError('Execution status differs from literal report')
            report.update(classification=value['classification'], passed=value['passed'], result={'path': str(target), 'sha256': digest(target)})
        elif args.profile == 'protocol':
            work = output / 'haskell'
            packages = ('held-document', 'process-custody', 'protocol')
            for name in data['haskellFiles']:
                if Path(name).parts[0] in packages:
                    copy(ROOT / 'implementation/warlock/haskell' / name, work / name)
            copy(BUNDLE / 'tests-first/WindowWatchProtocolControls.hs', work / 'protocol/test-window-watch/Main.hs')
            cabal = work / 'protocol/protocol.cabal'
            # StrictJson is private in the installed library. Copy its exact pinned
            # source into the TEST component only to construct literal bytes.
            # All observed accept/refuse decisions still call the public library.
            copy(ROOT / 'implementation/warlock/haskell/protocol/src/Warlock/Protocol/StrictJson.hs', work / 'protocol/test-window-watch/Warlock/Protocol/StrictJson.hs')
            stanza = (BUNDLE / 'tests-first/protocol-test-stanza.fragment').read_text()
            stanza = stanza.replace('  main-is: Main.hs', '  main-is: Main.hs\n  other-modules: Warlock.Protocol.StrictJson').replace('bytestring, text, warlock-protocol', 'bytestring, containers, text, warlock-protocol')
            cabal.write_text(cabal.read_text() + '\n' + stanza)
            dependencies = output / 'dependencies'
            shutil.copytree(selected['dependencies'], dependencies)
            if arm.inventory(dependencies) != selected['trees'][selected['dependencies']]:
                raise ValueError('Selected dependency source staging differs')
            dependency_manifest = json.loads((ROOT / 'tools/haskell-dependencies.json').read_text())
            for item in dependency_manifest['packages']:
                if digest(dependencies / item['directory'] / (item['name'] + '.cabal')) != item['metadataSHA256']:
                    raise ValueError('Dependency metadata changed')
            (work / 'cabal.project').write_text('packages: ' + ' '.join(packages) + '\npackages: ' + ' '.join(str(dependencies / item['directory']) for item in dependency_manifest['packages']) + '\nactive-repositories: :none\n')
            (output / 'cabal.config').write_text('active-repositories: :none\nstore-dir: ' + str(output / 'store') + '\nremote-repo-cache: ' + str(output / 'repo-cache') + '\n')
            env['PATH'] = selected['ghcPrefix'] + '/bin:/usr/bin:/bin'
            plan = build.command_plan(selected, output, work, (('window-watch-boundary-controls', 'warlock-protocol:test:window-watch-boundary-controls'),))
            run(*plan[0], cwd=work)
            _, image_text = run(*plan[1], cwd=work)
            image = Path(image_text.strip())
            if not image.is_relative_to(output / 'dist') or not image.is_file():
                raise ValueError('Fresh fixed test image missing')
            code, observed = run('window-watch-boundary-controls', [image], work, True)
            cases = re.findall(r'^([a-z0-9-]+):(PASS|FAIL)$', observed, flags=re.M)
            if [name for name, _ in cases] != data['haskellNames']:
                raise ValueError('All29 ordered protocol cases not observed')
            all_pass = all(result == 'PASS' for _, result in cases)
            if (code == 0) != all_pass or (all_pass and 'window-watch-protocol:29-controls:PASS' not in observed):
                raise ValueError('Protocol exit differs from literal cases')
            report.update(classification='component-pass' if all_pass else 'semantic-red', passed=all_pass, checks=[{'name': n, 'passed': s == 'PASS'} for n, s in cases], compiledImage={'path': str(image), 'sha256': digest(image)})
        else:
            pin = selected['quintProfile']
            prefix = [pin['node'], str(Path(pin['quint']) / 'dist/src/cli.js')]
            model = BUNDLE / 'tests-first/window-watch-retirement.qnt'
            run('quint-typecheck', prefix + ['typecheck', str(model)])
            traces = []
            for index, name in enumerate(data['quintNames']):
                code, observed = run('trace-' + str(index), prefix + ['test', str(model), '--main=window_watch_retirement', '--backend=typescript', '--match=^' + name + '$', '--verbosity=2'], allow_failure=True)
                if not re.search(r'\b1 passing\b', observed) and code == 0:
                    raise ValueError('Selected trace did not execute exactly once: ' + name)
                traces.append({'name': name, 'exit': code, 'passed': code == 0})
            safety, _ = run('quint-safety', prefix + ['run', str(model), '--main=window_watch_retirement', '--backend=typescript', '--invariant=safety', '--max-samples=1000', '--max-steps=30', '--seed=11011'], allow_failure=True)
            passed = safety == 0 and all(row['passed'] for row in traces)
            report.update(passed=passed, classification='sampled-model-pass' if passed else 'model-failed', traces=traces, sampledOnly=True, exhaustiveProof=False)
        input_data()
        tools_for(args.profile, data, arm, build, elm)
        report['sourceInputsUnchanged'] = True
        report['cleanupQualified'] = True
    except Exception as error:
        report.update(passed=False, classification='setup-compile-or-verification-failed', error=str(error))
    finally:
        save(output / 'report.json', report)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

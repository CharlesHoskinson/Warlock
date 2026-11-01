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
    modes.add_argument('--standalone-mvp', action='store_true', help='Fixed actual standalone MVP replay and six production roots')
    modes.add_argument('--status-scroll', action='store_true', help='Fixed UI007 status scroll replay and model')
    modes.add_argument('--tea-contract', action='store_true', help='Original TEA001/002 complete-model and typed-effect component fixture')
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
    from elm_http_dependencies import stage as stage_http_dependencies
    report['httpDependencies'] = stage_http_dependencies(output / 'elm-home')
    config = json.loads((root / 'elm.json').read_text())
    config['source-directories'] = ['src', 'qa']
    (work / 'qa').mkdir()
    (work / 'elm.json').write_text(json.dumps(config))
    env = dict(os.environ, ELM_HOME=str(output / 'elm-home'))
    if args.receipts or args.status_scroll or args.tea_contract:
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
            for name in ['Main', 'Bar', 'Popup', 'HttpMain', 'HttpBar', 'HttpPopup']:
                run('compile-' + name, [compiler, 'make', 'src/' + name + '.elm', '--optimize', '--output=' + str(output / (name + '.js'))])
        if args.tea_contract:
            run('compile-NativePreviewRenderer', [compiler, 'make', 'src/NativePreviewRenderer.elm', '--optimize',
                                                   '--output=' + str(output / 'NativePreviewRenderer.js')])
            # Fixed official compiler HTML outputs for the existing HTTP roots.
            # These are additional artifacts, not an alternate runner or policy.
            report['httpDocuments'] = {}
            for role, name in (('controller', 'HttpMain'), ('bar', 'HttpBar'), ('popup', 'HttpPopup')):
                document = output / (name + '.html')
                run('compile-html-' + name, [compiler, 'make', 'src/' + name + '.elm', '--optimize',
                                             '--output=' + str(document)])
                if document.is_symlink() or not document.is_file():
                    raise RuntimeError('Expected regular compiler HTML artifact: ' + name)
                source_path = 'implementation/warlock/src/' + name + '.elm'
                report['httpDocuments'][role] = {'path': document.name, 'sha256': sha(document),
                    'sourcePath': source_path, 'sourceSha256': sources[source_path]}
        fixture_name = 'ReceiptStateReplay' if args.receipts else ('AuthorityTupleReplay' if args.authority else 'FeedbackContextReplay')
        harness_name = 'receipt-state' if args.receipts else ('authority-tuple' if args.authority else 'feedback-context')
        fixture = root / ('qa/' + fixture_name + '.elm')
        harness = root / ('qa/' + harness_name + '.cjs')
        if fixture.exists():
            if any(source.is_symlink() or not source.is_file() for source in (fixture, harness)):
                raise RuntimeError('Expected regular replay and harness')
            for source in [fixture, harness]:
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / source.name)
            run('compile-' + harness_name, [compiler, 'make', 'qa/' + fixture_name + '.elm', '--optimize', '--output=' + str(output / (harness_name + '.js'))])
            if not args.receipts:
                run(harness_name, [str(node), 'qa/' + harness_name + '.cjs', str(output / (harness_name + '.js')), str(output / (harness_name + '.json'))])
        elif args.authority or args.receipts or args.standalone_mvp or args.status_scroll or args.tea_contract:
            raise RuntimeError('Original scenario fixture is required')
        if not (args.authority or args.receipts or args.browser):
            for filename in ('UiHttpReplay.elm', 'ui-http.cjs'):
                source = root / 'qa' / filename
                if source.is_symlink() or not source.is_file():
                    raise RuntimeError('Actual HTTP transport fixture is required')
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / filename)
            run('compile-ui-http-replay', [compiler, 'make', 'qa/UiHttpReplay.elm', '--optimize',
                                         '--output=' + str(output / 'UiHttpReplay.js')])
            run('ui-http', [str(node), 'qa/ui-http.cjs', *[str(output / (name + '.js'))
                           for name in ('HttpMain', 'HttpBar', 'HttpPopup', 'UiHttpReplay')],
                           str(output / 'ui-http.json')])
        if args.standalone_mvp:
            for filename in ('StandaloneMvpReplay.elm', 'standalone-mvp.cjs'):
                source = root / 'qa' / filename
                if source.is_symlink() or not source.is_file():
                    raise RuntimeError('Standalone MVP fixture is required')
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / filename)
            run('compile-standalone-mvp', [compiler, 'make', 'qa/StandaloneMvpReplay.elm', '--optimize',
                                           '--output=' + str(output / 'standalone-mvp.js')])
            run('standalone-mvp', [str(node), 'qa/standalone-mvp.cjs', str(output / 'standalone-mvp.js'),
                                   str(output / 'standalone-mvp.json')])
            replay_result = json.loads((output / 'standalone-mvp.json').read_text())
            if (replay_result.get('passed') is not True or not replay_result.get('checks')
                    or replay_result.get('failures') or any(row.get('passed') is not True for row in replay_result['checks'])):
                raise RuntimeError('Standalone MVP replay incomplete or failed')
            report['standaloneMvp'] = {'checks': len(replay_result['checks']), 'seed': replay_result.get('seed'),
                                       'resultSHA256': sha(output / 'standalone-mvp.json')}
        if args.tea_contract:
            typed_fixtures = ('NotificationsReplay', 'JumpListReplay',
                              'NotificationRelevanceReplay', 'RetirementProofReplay', 'LocalFieldReplay')
            for filename in (*(name + '.elm' for name in typed_fixtures),
                             'NativePointerFixture.elm', 'typed-state.cjs'):
                source = root / 'qa' / filename
                if source.is_symlink() or not source.is_file():
                    raise RuntimeError('Typed lifecycle/operation/retirement fixture is required')
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / filename)
                if sha(work / 'qa' / filename) != sources[str(source.relative_to(REPO))]:
                    raise RuntimeError('Typed-state input changed during staging')
            for name in typed_fixtures:
                run('compile-' + name, [compiler, 'make', 'qa/' + name + '.elm', '--optimize',
                                        '--output=' + str(output / (name + '.js'))])
            run('typed-state', [str(node), 'qa/typed-state.cjs',
                                *[str(output / (name + '.js')) for name in typed_fixtures],
                                str(output / 'typed-state.json')])
            typed = json.loads((output / 'typed-state.json').read_text())
            if (typed.get('passed') is not True
                    or [row.get('name') for row in typed.get('fixtures', [])] != list(typed_fixtures)
                    or any(row.get('passed') is not True or row.get('sha256') != sha(output / (name + '.js'))
                           for name, row in zip(typed_fixtures, typed.get('fixtures', [])))
                    or typed.get('runnerSha256') != sha(work / 'qa/typed-state.cjs')
                    or not typed.get('checks') or typed.get('failures')
                    or any(row.get('passed') is not True for row in typed['checks'])):
                raise RuntimeError('Typed-state lifecycle/operation/proof controls incomplete or failed')
            report['typedState'] = {'fixtures': list(typed_fixtures), 'checks': len(typed['checks']),
                                     'resultSHA256': sha(output / 'typed-state.json'),
                                     'nativeAccepted': False, 'originalAccepted': False}
            for filename in ('TeaContractReplay.elm', 'tea-contract.cjs', 'tea-contract-cases.cjs'):
                source = root / 'qa' / filename
                if source.is_symlink() or not source.is_file():
                    raise RuntimeError('Complete TEA contract fixture/oracle/runner are required')
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / filename)
                if sha(work / 'qa' / filename) != sources[str(source.relative_to(REPO))]:
                    raise RuntimeError('TEA contract input changed during staging')
            # Production roots above remain optimized. This QA-only fixture
            # retains Debug.log so the read-only runner can observe the entire
            # unmodified reducer tuple without exposing opaque constructors.
            run('compile-tea-contract', [compiler, 'make', 'qa/TeaContractReplay.elm',
                                         '--output=' + str(output / 'tea-contract.js')])
            run('tea-contract', [str(node), 'qa/tea-contract.cjs', str(output / 'tea-contract.js'),
                                 str(work / 'qa/tea-contract-cases.cjs')])
            contract = json.loads((output / 'tea-contract.stdout').read_text())
            if (contract.get('passed') is not True or contract.get('reversiblePatch') is not True
                    or not contract.get('cases') or contract.get('transitions', 0) <= 0
                    or contract.get('runsPerCase') != 2
                    or contract.get('originalFixtureSha256') != sha(output / 'tea-contract.js')
                    or contract.get('oracleSha256') != sha(work / 'qa/tea-contract-cases.cjs')):
                raise RuntimeError('Complete-model replay receipt incomplete or mismatched')
            report['teaContract'] = dict(contract,
                originalAccepted=False, nativeAccepted=False, releaseAccepted=False,
                acceptanceLimit='Named complete-model/effect fixture only; whole original clauses require independent review and adequate positive/lifecycle coverage')
            # The canonical local-field model accompanies the fixed typed/HTTP
            # replays; it is not a separate caller-selected model or CLI mode.
            source = root / 'qa/local-field-publication.qnt'
            model = work / 'qa/local-field-publication.qnt'
            pin_path = REPO / 'tools/quint-toolchain.json'
            if source.is_symlink() or not source.is_file() or pin_path.is_symlink() or not pin_path.is_file():
                raise RuntimeError('Expected regular local-field model and toolchain pin')
            model_key = str(source.relative_to(REPO))
            sources[model_key] = sha(source)
            sources['tools/quint-toolchain.json'] = sha(pin_path)
            shutil.copy2(source, model)
            if model.is_symlink() or sha(model) != sources[model_key]:
                raise RuntimeError('Local-field model changed during staging')
            pin, cli = quint_toolchain()
            if str(node) != pin['node']['path'] or sha(node) != pin['node']['sha256']:
                raise RuntimeError('Pinned local-field model interpreter differs')
            names = re.findall(r'^\s*run\s+(\w+)\s*=', model.read_text(), re.M)
            original_names = ('localPaintGapPreservesDraftTest', 'staleExternalEditRejectedTest',
                              'staleLocalButtonRejectedTest', 'retiredFieldCannotEditTest',
                              'futureFieldCannotEditTest', 'localFifoKeepsLatestDraftTest',
                              'currentActionStillWorksTest')
            witnesses = ('witnessDependent', 'witnessSafeWhilePending')
            declared_witnesses = re.findall(r'^\s*val\s+(witness\w+)\s*(?::[^=]+)?=', model.read_text(), re.M)
            if (not names or len(names) != len(set(names)) or not set(original_names).issubset(names)
                    or sorted(declared_witnesses) != sorted(witnesses)):
                raise RuntimeError('Local-field original tests or positive witnesses missing/duplicated')
            selector = '^(?:' + '|'.join(re.escape(name) for name in names) + ')$'
            run('local-field-model-typecheck', [str(node), str(cli), 'typecheck', str(model)])
            run('local-field-model-directed', [str(node), str(cli), 'test', str(model),
                                              '--main=local_field_publication', '--match=' + selector,
                                              '--backend=typescript', '--verbosity=2'])
            if re.findall(r'\b(\d+) passing\b', (output / 'local-field-model-directed.stdout').read_text()) != [str(len(names))]:
                raise RuntimeError('Local-field exact named test count differs')
            run('local-field-model-safety', [str(node), str(cli), 'run', str(model),
                                            '--main=local_field_publication', '--backend=typescript',
                                            '--invariant=safety', '--witnesses', *witnesses,
                                            '--max-samples=10000', '--max-steps=50', '--seed=20261101', '--verbosity=1'])
            observed = re.findall(r'(\w+) was witnessed in (\d+) trace',
                                  (output / 'local-field-model-safety.stdout').read_text())
            counts = {name: int(count) for name, count in observed}
            if len(observed) != len(witnesses) or set(counts) != set(witnesses) or any(count == 0 for count in counts.values()):
                raise RuntimeError('Local-field positive witness missing, duplicated or zero')
            if (source.is_symlink() or not source.is_file() or model.is_symlink() or not model.is_file()
                    or sha(source) != sources[model_key] or sha(model) != sources[model_key]
                    or pin_path.is_symlink() or not pin_path.is_file()
                    or sha(pin_path) != sources['tools/quint-toolchain.json']
                    or quint_toolchain()[0] != pin or sha(node) != pin['node']['sha256']):
                raise RuntimeError('Local-field model or pinned toolchain changed during execution')
            report['localFieldModel'] = {'directed': names, 'witnesses': counts, 'samples': 10000,
                'maxSteps': 50, 'seed': 20261101, 'modelSHA256': sources[model_key],
                'stagedModelSHA256': sha(model), 'toolchainFileSHA256': sources['tools/quint-toolchain.json'],
                'toolchain': pin, 'nativeAccepted': False, 'originalAccepted': False}
        if args.status_scroll:
            for filename in ('StatusScrollReplay.elm', 'status-scroll.cjs', 'status-scroll.qnt', 'status-scroll_test.qnt'):
                source = root / 'qa' / filename
                if source.is_symlink() or not source.is_file():
                    raise RuntimeError('Status scroll fixture and model are required')
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / filename)
                if sha(work / 'qa' / filename) != sources[str(source.relative_to(REPO))]:
                    raise RuntimeError('Status scroll source changed during staging')
            run('compile-status-scroll', [compiler, 'make', 'qa/StatusScrollReplay.elm', '--optimize',
                                           '--output=' + str(output / 'status-scroll.js')])
            run('status-scroll', [str(node), 'qa/status-scroll.cjs', str(output / 'status-scroll.js'),
                                  str(output / 'status-scroll.json')])
            replay = json.loads((output / 'status-scroll.json').read_text())
            if (replay.get('passed') is not True or not replay.get('checks') or replay.get('failures')
                    or any(row.get('passed') is not True for row in replay['checks'])):
                raise RuntimeError('Status scroll replay incomplete or failed')
            report['statusScrollReplay'] = {'checks': len(replay['checks']), 'seed': replay.get('seed'),
                                             'resultSHA256': sha(output / 'status-scroll.json')}
            restore_files = ('RestoreAnnouncementReplay.elm', 'restore-announcement.cjs',
                             'SnapReplay.elm', 'NativePointerFixture.elm')
            for filename in restore_files:
                source = root / 'qa' / filename
                if source.is_symlink() or not source.is_file():
                    raise RuntimeError('Restore announcement replay and helpers are required')
                sources[str(source.relative_to(REPO))] = sha(source)
                shutil.copy2(source, work / 'qa' / filename)
                if sha(work / 'qa' / filename) != sources[str(source.relative_to(REPO))]:
                    raise RuntimeError('Restore announcement source changed during staging')
            run('compile-restore-announcement', [compiler, 'make', 'qa/RestoreAnnouncementReplay.elm', '--optimize',
                                                  '--output=' + str(output / 'restore-announcement.js')])
            run('restore-announcement', [str(node), 'qa/restore-announcement.cjs',
                                          str(output / 'restore-announcement.js'),
                                          str(output / 'restore-announcement.json')])
            restore = json.loads((output / 'restore-announcement.json').read_text())
            if (restore.get('passed') is not True or not restore.get('checks') or restore.get('failures')
                    or any(row.get('passed') is not True for row in restore['checks'])):
                raise RuntimeError('Restore announcement replay incomplete or failed')
            for filename in restore_files:
                source = root / 'qa' / filename
                expected = sources[str(source.relative_to(REPO))]
                staged = work / 'qa' / filename
                if (source.is_symlink() or not source.is_file() or staged.is_symlink() or not staged.is_file()
                        or sha(source) != expected or sha(staged) != expected):
                    raise RuntimeError('Restore announcement source changed during execution')
            report['restoreAnnouncementReplay'] = {'checks': len(restore['checks']),
                                                   'resultSHA256': sha(output / 'restore-announcement.json')}
            pin, cli = quint_toolchain()
            if str(node) != pin['node']['path'] or sha(node) != pin['node']['sha256']:
                raise RuntimeError('Pinned model interpreter differs')
            sources['tools/quint-toolchain.json'] = sha(REPO / 'tools/quint-toolchain.json')
            model = work / 'qa/status-scroll.qnt'
            tests = work / 'qa/status-scroll_test.qnt'
            names = re.findall(r'^\s*run\s+(\w+)\s*=', tests.read_text(), re.M)
            witnesses = re.findall(r'^\s*val\s+(witness\w+)\s*(?::[^=]+)?=', model.read_text(), re.M)
            if not names or len(names) != len(set(names)) or not witnesses or len(witnesses) != len(set(witnesses)):
                raise RuntimeError('Status scroll named test or witness selection empty or duplicated')
            selector = '^(?:' + '|'.join(re.escape(name) for name in names) + ')$'
            run('status-model-typecheck', [str(node), str(cli), 'typecheck', str(model)])
            run('status-model-test-typecheck', [str(node), str(cli), 'typecheck', str(tests)])
            run('status-model-directed', [str(node), str(cli), 'test', str(tests), '--main=status_scroll_test',
                                           '--match=' + selector, '--backend=typescript', '--verbosity=2'])
            if re.findall(r'\b(\d+) passing\b', (output / 'status-model-directed.stdout').read_text()) != [str(len(names))]:
                raise RuntimeError('Status scroll exact named test count differs')
            run('status-model-safety', [str(node), str(cli), 'run', str(model), '--main=status_scroll',
                                        '--backend=typescript', '--invariant=safety', '--witnesses', *witnesses,
                                        '--max-samples=10000', '--max-steps=50', '--seed=20261101', '--verbosity=1'])
            counts = {name: int(n) for name, n in re.findall(r'(\w+) was witnessed in (\d+) trace',
                      (output / 'status-model-safety.stdout').read_text())}
            if set(counts) != set(witnesses) or any(n == 0 for n in counts.values()):
                raise RuntimeError('Status scroll model witness missing or zero')
            if quint_toolchain()[0] != pin or sha(node) != pin['node']['sha256']:
                raise RuntimeError('Status scroll model toolchain changed')
            report['statusScrollModel'] = {'directed': names, 'witnesses': counts, 'samples': 10000,
                                           'maxSteps': 50, 'seed': 20261101, 'toolchain': pin}
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
        if args.tea_contract:
            for document in report['httpDocuments'].values():
                artifact = output / document['path']
                if (artifact.is_symlink() or not artifact.is_file()
                        or sha(artifact) != document['sha256']):
                    raise RuntimeError('Compiler HTML artifact changed during protected check')
                report['artifacts'][document['path']] = document['sha256']
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

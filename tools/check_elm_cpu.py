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
# Exact previously exercised case names plus selected source-bound Motion cases.
TEA001_POLICY_CASES = frozenset(['empty-topology-publishes-complete-frame', 'topology-full-width-9007199254740993', 'topology-maximum-then-overflow', 'one-view-topology-assigns-owner', 'pending-catalog-disposition-mismatch-scope', 'pending-catalog-disposition-mismatch-revision', 'pending-catalog-disposition-mismatch-publication', 'pending-catalog-disposition-mismatch-lease', 'pending-catalog-disposition-mismatch-binding', 'pending-catalog-disposition-mismatch-wire', 'pending-catalog-mismatched-domain-receipt', 'catalog-preflight-refusal-no-replay', 'catalog-matched-read-then-stale-receipt', 'catalog-pending-disconnect-rejects-late-receipt', 'outer-not-object', 'outer-missing-version', 'outer-version-string', 'outer-wrong-version', 'outer-unknown-kind', 'outer-missing-payload', 'outer-extra-field', 'topology-zero-revision', 'topology-leading-zero', 'topology-counter-overflow', 'topology-negative-counter', 'topology-numeric-counter', 'pin-wrong-request-retains-pending', 'pin-refused-retains-observed-order', 'pin-unknown-retains-reservation-no-replay', 'pin-saved-receipt-confirms-exact-new-order', 'pin-unknown-then-correlated-refused', 'pin-unknown-then-correlated-saved', 'catalog-rebind-new-frontend-no-old-replay', 'pin-pending-invalid-status-Stored', 'pin-pending-invalid-status-Bogus', 'pin-pending-invalid-status-saved', 'pin-pending-invalid-status-empty', 'window-minimize-committed-duplicate-and-stale', 'window-minimize-refused-duplicate-and-stale', 'window-pending-disconnect-rebind-historical-receipt', 'launch-delay-exact-timeout-and-stale-token', 'launch-delay-stale-after-matching-submitted', 'settings-pending-malformed-status-noop-then-unknown-and-refused', 'settings-pending-malformed-status-noop-then-saved', 'motion-pending-malformed-status-noop-then-unknown-and-refused', 'motion-pending-malformed-status-noop-then-saved-syncs-profile', 'shortcut-pending-malformed-status-noop-then-unknown-and-refused', 'shortcut-pending-malformed-status-noop-then-stored', 'shortcut-pending-malformed-status-noop-then-saved', 'ux-pending-settings-malformed-unsupported-name', 'ux-pending-settings-malformed-wrong-case', 'ux-pending-settings-malformed-empty-status', 'ux-pending-settings-malformed-wrong-domain-stored', 'ux-pending-settings-malformed-null-status', 'ux-pending-settings-malformed-numeric-status', 'ux-pending-settings-malformed-missing-status', 'ux-pending-settings-malformed-extra-field', 'ux-pending-settings-valid-unknown-is-distinct', 'motion-pending-stale-saved-unconfirmed-then-refused', 'motion-source-portal-gtk-stale-invalid-complete-policy', 'motion-source-gtk-uint64-max-stale-complete-policy'])
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quint_toolchain():
    from toolchain_derivative import selected
    _, pin, identity = selected()
    pin['derivative'] = identity
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



def run_receipt_models(node, pin, cli, run):
    if str(node) != pin['node']['path'] or sha(node) != pin['node']['sha256']:
        raise RuntimeError('Pinned model interpreter differs')
    run('receipt-model-typecheck', [str(node), str(cli), 'typecheck', 'qa/receipt-lifecycle_test.qnt'])
    run('receipt-model-cancelled-tests', [str(node), str(cli), 'test', 'qa/receipt-lifecycle.qnt', '--main=ReceiptLifecycle', '--match=.*Test', '--backend=typescript', '--verbosity=2'])
    run('receipt-model-original-tests', [str(node), str(cli), 'test', 'qa/receipt-lifecycle_test.qnt', '--main=ReceiptLifecycle_test', '--match=.*Test', '--backend=typescript', '--verbosity=2'])
    run('receipt-model-safety', [str(node), str(cli), 'run', 'qa/receipt-lifecycle.qnt', '--main=ReceiptLifecycle', '--backend=typescript', '--invariant=safety', '--witnesses',
                                'witnessPending', 'witnessCommitted', 'witnessRefused', 'witnessCancelled', 'witnessUnknown', 'witnessDisconnected', 'witnessNewRequest',
                                '--max-samples=10000', '--max-steps=50', '--seed=20261031', '--verbosity=1'])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--browser', action='store_true', help='Separately reviewed private-network browser component checks')
    modes.add_argument('--authority', action='store_true', help='Original ARC005 owning-route authority tuple bridge checks')
    modes.add_argument('--receipts', action='store_true', help='Original ARC007 actual desktop receipt bridge and model checks')
    modes.add_argument('--standalone-mvp', action='store_true', help='Fixed actual standalone MVP replay and six production roots')
    modes.add_argument('--status-scroll', action='store_true', help='Fixed UI007 status scroll replay and model')
    modes.add_argument('--tea-contract', action='store_true', help='Original TEA001/002 complete-model and typed-effect component fixture')
    modes.add_argument('--subscriptions', action='store_true', help='Fixed eight-root subscription component replay; original coverage remains incomplete')
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
    staged_tea_sources = {}
    selected_artifacts = {}
    shutil.copytree(held / pinned['elmHome'], output / 'elm-home')
    from elm_http_dependencies import stage as stage_http_dependencies
    report['httpDependencies'] = stage_http_dependencies(output / 'elm-home')
    config = json.loads((root / 'elm.json').read_text())
    config['source-directories'] = ['src', 'qa']
    (work / 'qa').mkdir()
    (work / 'elm.json').write_text(json.dumps(config))
    staged_elm_manifest_sha = sha(work / 'elm.json')
    env = dict(os.environ, ELM_HOME=str(output / 'elm-home'))
    if args.receipts or args.status_scroll or args.tea_contract or args.subscriptions:
        for key in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
            env.pop(key, None)
        env['NO_COLOR'] = '1'

    def run(name, command, cwd=work):
        toolchain.verify()
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
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
        if args.subscriptions:
            for name in ('NativePreviewAdmission', 'NativePreviewRenderer'):
                run('compile-' + name, [compiler, 'make', 'src/' + name + '.elm', '--optimize',
                                       '--output=' + str(output / (name + '.js'))])
        if args.tea_contract:
            run('compile-NativePreviewRenderer', [compiler, 'make', 'src/NativePreviewRenderer.elm', '--optimize',
                                                   '--output=' + str(output / 'NativePreviewRenderer.js')])
        if args.tea_contract or args.standalone_mvp or args.subscriptions:
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
        if fixture.exists() and not args.subscriptions:
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
        if not (args.authority or args.receipts or args.browser or args.subscriptions):
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
        if args.subscriptions:
            roots = ('Main', 'Bar', 'Popup', 'HttpMain', 'HttpBar', 'HttpPopup',
                     'NativePreviewAdmission', 'NativePreviewRenderer')
            workers = {'popup': 'TeaPopupSubscriptionsReplay', 'bar': 'TeaBarSubscriptionsReplay',
                       'admission': 'TeaAdmissionSubscriptionsReplay', 'renderer': 'TeaRendererSubscriptionsReplay'}
            qa_files = tuple(name + '.elm' for name in workers.values()) + (
                'tea-subscriptions-cases.cjs', 'tea-subscriptions.cjs', 'tea-contract-cases.cjs',
                'sol-http-root-observer-0535.cjs', 'sol-http-popup-literals-0525.cjs',
                'httpbar-literals.cjs', 'http-root-cases-manifest.json',
                'http-root-cases-guard.cjs', 'http-root-cases-negative.cjs',
                'sitemain-root-literals.cjs', 'sitemain-root-observer.cjs',
                'sitemain-root-manifest.json', 'sitemain-root-negative.cjs')
            # Keep the harness's optional three-parent SiteMain probe inside a fresh owned tree.
            subscription_qa = output / 'subscription-source' / 'implementation/warlock/qa'
            subscription_qa.mkdir(parents=True)
            for filename in qa_files:
                source = root / 'qa' / filename
                if source.is_symlink() or not source.is_file():
                    raise RuntimeError('Required subscription QA input missing: ' + filename)
                key = str(source.relative_to(REPO))
                sources[key] = staged_tea_sources[key] = sha(source)
                shutil.copy2(source, work / 'qa' / filename)
                shutil.copy2(source, subscription_qa / filename)
            reviewed_http_inputs = {
                'sol-http-root-observer-0535.cjs': 'ccd93b17d5126e2be411b2f9d42a57770e5cdffa8f1654ad7b01a42f80bef7cf',
                'sol-http-popup-literals-0525.cjs': 'ab7af2abe53a36eae18c90762001a7f3647b47ed400b15bdd5aaba56f49f21f1',
                'httpbar-literals.cjs': '6f645e235c119e2a8069d9a6d7542c1f45cd95d667ddbe5e3f6129f83a255173',
                'http-root-cases-manifest.json': '2a00fc7fbabac6f3a228847d945f703a4d9dcade3b060a9a27034ea1b31e6064',
                'http-root-cases-guard.cjs': '1943800f421da64c4f11a80359d200e142c5dd36839c386aec19afba5754b7f1',
                'http-root-cases-negative.cjs': 'd04b96e8983525dfb675428bcdcbe3f4fef7730aba0672378d3aa228b4958782',
                'tea-contract-cases.cjs': '41e3ccabc5843153b604205dd937c56890f659e294929788a959951d39b7bcb7',
            }
            for name, digest in reviewed_http_inputs.items():
                key = 'implementation/warlock/qa/' + name
                if (sources[key] != digest or sha(work / 'qa' / name) != digest
                        or sha(subscription_qa / name) != digest):
                    raise RuntimeError('Reviewed HTTP fixture or stage differs: ' + name)
            manifest = json.loads((subscription_qa / 'http-root-cases-manifest.json').read_text())
            if (manifest.get('schema') != 1 or manifest.get('requirement') != 'ELM-TEA-004'
                    or manifest.get('scenario') != 'tea-subscriptions'
                    or manifest.get('coverageComplete') is not False
                    or manifest.get('originalAcceptanceClaim') is not False):
                raise RuntimeError('Reviewed HTTP fixture manifest identity differs')
            reviewed_sitemain_inputs = {
                'sitemain-root-literals.cjs': '04151053b079b4dba16656d71680d8eec9ebed709285c695e8270f3e57478cb3',
                'sitemain-root-manifest.json': '35c43b1af218669b033eacb6f754efcf28982f21a1c6a7215f288231f12fcac5',
                'sitemain-root-negative.cjs': '0bb0d6b118b258aa56d5fa764d392968f4be03219f96d220e3ef77d49dbaa7b2',
                'sitemain-root-observer.cjs': '0a0ec6efc3c14bee29b055532775ecc567f2e96f1b0d43d2d6c7f2306b5bc643',
            }
            for name, digest in reviewed_sitemain_inputs.items():
                key = 'implementation/warlock/qa/' + name
                if (sources[key] != digest or sha(work / 'qa' / name) != digest
                        or sha(subscription_qa / name) != digest):
                    raise RuntimeError('Reviewed SiteMain fixture or stage differs: ' + name)
            site_manifest = json.loads((subscription_qa / 'sitemain-root-manifest.json').read_text())
            if (site_manifest.get('schema') != 1 or site_manifest.get('requirement') != 'ELM-TEA-004'
                    or site_manifest.get('scenario') != 'tea-subscriptions'
                    or site_manifest.get('fixtures', {}).get('siteMain') != {
                        'file': 'site/src/SiteMain.elm',
                        'sha256': 'f05a3768eb4573161544099917ce009f8df7eb57b8c9408f5266001980cafcfb'}
                    or site_manifest.get('fixtures', {}).get('siteElmJson') != {
                        'file': 'site/elm.json',
                        'sha256': 'ffe9bc4f6811166a7bbafca49540bf7b8af214118dd9aff2f4707890eb9824dc'}
                    or site_manifest.get('coverageComplete') is not False
                    or site_manifest.get('originalAcceptanceClaim') is not False):
                raise RuntimeError('Reviewed SiteMain fixture manifest identity differs')
            # Bind and compile the ninth production root from its own staged site/
            # package closure while preserving desktop eight-root profile honesty.
            site_key = 'site/src/SiteMain.elm'
            site_manifest_key = 'site/elm.json'
            site_source = REPO / site_key
            site_manifest_source = REPO / site_manifest_key
            if (site_source.is_symlink() or not site_source.is_file()
                    or site_manifest_source.is_symlink() or not site_manifest_source.is_file()):
                raise RuntimeError('Required SiteMain source or elm.json missing')
            sources[site_key] = sha(site_source)
            sources[site_manifest_key] = sha(site_manifest_source)
            if (sources[site_key] != site_manifest['fixtures']['siteMain']['sha256']
                    or sources[site_manifest_key] != site_manifest['fixtures']['siteElmJson']['sha256']):
                raise RuntimeError('SiteMain source or elm.json hash differs from reviewed manifest')
            staged_site = output / 'subscription-source' / site_key
            staged_site_manifest = output / 'subscription-source' / site_manifest_key
            staged_site.parent.mkdir(parents=True)
            shutil.copy2(site_source, staged_site)
            shutil.copy2(site_manifest_source, staged_site_manifest)
            if (staged_site.is_symlink() or sha(staged_site) != sources[site_key]
                    or staged_site_manifest.is_symlink() or sha(staged_site_manifest) != sources[site_manifest_key]):
                raise RuntimeError('Staged SiteMain source or elm.json differs')
            plain_roots = ('HttpMain', 'HttpBar', 'HttpPopup')
            for name in plain_roots:
                run('compile-plain-' + name, [compiler, 'make', 'src/' + name + '.elm',
                    '--output=' + str(output / (name + '.plain.js'))])
            run('compile-plain-SiteMain', [compiler, 'make', 'src/SiteMain.elm',
                '--output=' + str(output / 'SiteMain.plain.js')], cwd=staged_site_manifest.parent)
            plain_hashes = {name: sha(output / (name + '.plain.js')) for name in plain_roots}
            site_plain_hash = sha(output / 'SiteMain.plain.js')
            for name in workers.values():
                # Debug.log exposes the actual tuple before formatting; never optimize these disjoint workers.
                run('compile-' + name, [compiler, 'make', 'qa/' + name + '.elm',
                                       '--output=' + str(output / (name + '.js'))])
            selected_artifacts.update({name: sha(output / (name + '.js')) for name in (*roots, *workers.values())})
            run('http-root-cases-negative', [str(node), str(subscription_qa / 'http-root-cases-negative.cjs'),
                str(output / 'subscription-source')])
            negative_path = output / 'http-root-cases-negative.stdout'
            negative = json.loads(negative_path.read_text())
            if (negative.get('ok') is not True or negative.get('originalAcceptanceClaim') is not False
                    or negative.get('controls') != ['absent-peer', 'empty-peer', 'altered-peer',
                        'removed-peer-cases', 'removed-case', 'duplicate-case']):
                raise RuntimeError('HTTP fixture negative controls incomplete')
            report['httpRootNegative'] = {'resultPath': negative_path.name, 'resultSHA256': sha(negative_path),
                'result': negative}
            run('http-root-observer', [str(node), str(subscription_qa / 'sol-http-root-observer-0535.cjs'),
                str(output / 'subscription-source'),
                *[str(output / (name + '.plain.js')) for name in plain_roots],
                str(subscription_qa / 'httpbar-literals.cjs')])
            observer_path = output / 'http-root-observer.stdout'
            observed_http = json.loads(observer_path.read_text())
            cases = observed_http.get('cases', [])
            if (observed_http.get('ok') is not True
                    or observed_http.get('originalAcceptanceClaim') is not False
                    or observed_http.get('coverage', {}).get('complete') is not False
                    or observed_http.get('manifestHash') != reviewed_http_inputs['http-root-cases-manifest.json']
                    or observed_http.get('observerHash') != sha(subscription_qa / 'sol-http-root-observer-0535.cjs')
                    or observed_http.get('oracleHash') != sha(subscription_qa / 'sol-http-popup-literals-0525.cjs')
                    or observed_http.get('policyLiteralSource', {}).get('sha256') != sha(subscription_qa / 'tea-contract-cases.cjs')
                    or len(observed_http.get('peerSources', [])) != 1
                    or observed_http['peerSources'][0].get('sha256') != sha(subscription_qa / 'httpbar-literals.cjs')
                    or not isinstance(cases, list) or not cases
                    or [{'name': case.get('name'), 'root': case.get('root'),
                         'steps': case.get('assertedStepsPerRun')} for case in cases] != manifest.get('cases')
                    or len({case.get('name') for case in cases}) != len(cases)
                    or any(case.get('freshRuns') != 2 or type(case.get('assertedStepsPerRun')) is not int
                           or case['assertedStepsPerRun'] <= 0
                           or case.get('compiledOriginal') != plain_hashes.get(case.get('root'))
                           for case in cases)):
                raise RuntimeError('HTTP owning-root observer result incomplete or mismatched')
            report['httpRootObserver'] = {'resultPath': observer_path.name, 'resultSHA256': sha(observer_path),
                'plainRootHashes': plain_hashes, 'result': observed_http}
            run('sitemain-root-negative', [str(node), str(subscription_qa / 'sitemain-root-negative.cjs'),
                str(output / 'subscription-source'), str(output / 'SiteMain.plain.js')])
            site_negative_path = output / 'sitemain-root-negative.stdout'
            site_negative = json.loads(site_negative_path.read_text())
            if (site_negative.get('ok') is not True or site_negative.get('originalAcceptanceClaim') is not False
                    or site_negative.get('controls') != [
                        'missing-sitemain-source', 'empty-sitemain-source', 'altered-sitemain-source',
                        'missing-site-elm-json', 'altered-site-elm-json', 'altered-literals',
                        'removed-case', 'duplicate-case', 'injected-animated-subscription-bundle']):
                raise RuntimeError('SiteMain fixture negative controls incomplete')
            report['siteMainRootNegative'] = {'resultPath': site_negative_path.name,
                'resultSHA256': sha(site_negative_path), 'result': site_negative}
            run('sitemain-root-observer', [str(node), str(subscription_qa / 'sitemain-root-observer.cjs'),
                str(output / 'subscription-source'), str(output / 'SiteMain.plain.js')])
            site_observer_path = output / 'sitemain-root-observer.stdout'
            observed_site = json.loads(site_observer_path.read_text())
            site_cases = observed_site.get('cases', [])
            site_dom = observed_site.get('fakeDomLifecycle', {})
            if (observed_site.get('ok') is not True
                    or observed_site.get('originalAcceptanceClaim') is not False
                    or observed_site.get('coverage', {}).get('complete') is not False
                    or observed_site.get('manifestHash') != reviewed_sitemain_inputs['sitemain-root-manifest.json']
                    or observed_site.get('observerHash') != sha(subscription_qa / 'sitemain-root-observer.cjs')
                    or observed_site.get('literalsHash') != sha(subscription_qa / 'sitemain-root-literals.cjs')
                    or observed_site.get('sourcePins', {}).get('siteMain') != {
                        'path': site_key, 'sha256': sources[site_key]}
                    or observed_site.get('sourcePins', {}).get('siteElmJson') != {
                        'path': site_manifest_key, 'sha256': sources[site_manifest_key]}
                    or not isinstance(site_cases, list) or not site_cases
                    or [{'name': case.get('name'), 'root': case.get('root'),
                         'steps': case.get('assertedStepsPerRun')} for case in site_cases] != site_manifest.get('cases')
                    or len({case.get('name') for case in site_cases}) != len(site_cases)
                    or any(case.get('freshRuns') != 2 or type(case.get('assertedStepsPerRun')) is not int
                           or case['assertedStepsPerRun'] <= 0
                           or case.get('compiledOriginal') != site_plain_hash
                           for case in site_cases)
                    or site_dom.get('transitions') != site_manifest.get('fakeDomExpectedTransitions')
                    or site_dom.get('freshRuns') != 2
                    or site_dom.get('compiledOriginal') != site_plain_hash
                    or site_dom.get('activeTimersAfterIdleAdvance') != 0):
                raise RuntimeError('SiteMain owning-root observer result incomplete or mismatched')
            report['siteMainRootObserver'] = {'resultPath': site_observer_path.name,
                'resultSHA256': sha(site_observer_path), 'plainRootHash': site_plain_hash,
                'result': observed_site}
            result_path = output / 'tea-subscriptions.json'
            run('tea-subscriptions', [str(node), str(subscription_qa / 'tea-subscriptions.cjs'), '--workers',
                                     *[str(output / (name + '.js')) for name in workers.values()], '--roots',
                                     *[str(output / (name + '.js')) for name in roots], '--out', str(result_path)])
            summary = json.loads(result_path.read_text())
            expected_cases = [
                {'name': 'bar-consumer-subscriptions', 'worker': 'bar'},
                {'name': 'popup-overlay-and-paint-gate-subscriptions', 'worker': 'popup'},
                {'name': 'popup-realm-ingress-and-closed-revocation', 'worker': 'popup'},
                {'name': 'popup-realm-close-while-closed-preserves-retirement-ledger', 'worker': 'popup'},
                {'name': 'admission-consumer-subscriptions', 'worker': 'admission'},
                {'name': 'renderer-grant-and-poison-subscriptions', 'worker': 'renderer'}]
            coverage = summary.get('coverageDeclaration', {})
            if (summary.get('schema') != 2 or summary.get('passed') is not True
                    or summary.get('requirement') != 'ELM-TEA-004' or summary.get('scenario') != 'tea-subscriptions'
                    or summary.get('marker') != 'TEA_SUBSCRIPTIONS_OBSERVE_V1'
                    or summary.get('cases') != expected_cases or summary.get('runsPerCase') != 2
                    or type(summary.get('transitions')) is not int or summary['transitions'] <= 0
                    or summary.get('scope') != 'QA single-root replay + eight compiled Browser.element roots for port/XHR/timer verification + static SiteMain source inventory; native behavior qualified separately'
                    or summary.get('completeRuntimeBoundary') is not False
                    or summary.get('siteMainSha256') != sources[site_key]
                    or summary.get('siteMainBytePreserved') is not True
                    or summary.get('optimizedRootsVerified') is not True
                    or summary.get('optimizedRootHashes') != {name: selected_artifacts[name] for name in roots}
                    or summary.get('oracleSha256') != sha(work / 'qa/tea-subscriptions-cases.cjs')
                    or summary.get('runnerSha256') != sha(work / 'qa/tea-subscriptions.cjs')
                    or set(summary.get('workers', {})) != set(workers)
                    or coverage.get('complete') is not False or not coverage.get('missing')
                    or summary.get('nativeAccepted') is not False or summary.get('releaseAccepted') is not False):
                raise RuntimeError('Subscription component result incomplete, changed or overclaimed')
            for key, name in workers.items():
                observed = summary['workers'][key]
                if (observed.get('moduleName') != name
                        or observed.get('fixtureElmSha256') != sha(work / 'qa' / (name + '.elm'))
                        or observed.get('originalFixtureSha256') != selected_artifacts[name]
                        or observed.get('reversiblePatch') is not True
                        or not re.fullmatch(r'[0-9a-f]{64}', observed.get('instrumentedFixtureSha256', ''))
                        or type(observed.get('patchOffset')) is not int or observed['patchOffset'] < 0
                        or type(observed.get('patchInsertedBytes')) is not int or observed['patchInsertedBytes'] <= 0):
                    raise RuntimeError('Subscription worker observation/hash binding differs: ' + key)
            report['scope'] = 'Eight optimized production roots and four disjoint debug subscription workers; component evidence only'
            report['subscriptions'] = dict(summary, resultPath=result_path.name, resultSHA256=sha(result_path))
            report['compiledSubscriptionRoots'] = list(roots)
            report['wholeTea004Accepted'] = False
            report['subscriptionQaStage'] = {'path': str(subscription_qa.relative_to(output)),
                                               'hashes': {name: sha(subscription_qa / name) for name in qa_files}}
            report['subscriptionLimits'] = [
                'coverage.complete=false retained; HTTP wrapper Model/effect AST gaps remain in the raw coverage declaration',
                'Eight desktop roots use the optimized runtime harness; SiteMain has a separate ordinary-compiled fake-DOM component check, without browser/native or whole-scenario acceptance',
                'sitemain-root-observer.cjs observes compiled ordinary SiteMain.plain.js (Sub.none + Dom.focus spotlight lifecycle); product EARS ELM-TEA-004 remains open',
                'No live native host ordering, GUI, provider, AT/IME or release acceptance']
        if args.standalone_mvp:
            for filename in ('NativePointerFixture.elm', 'StandaloneMvpReplay.elm', 'standalone-mvp.cjs'):
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
            # Fixed TEA001 core workers. Existing 7 JS / 3 HTML roots,
            # typed-state, complete policy and local model continue unchanged.
            extra_workers = (
                'FilesReplay', 'SolFilesRebind2214',
                'SystemMenuReplay', 'SolSystemMenuIntegratedReplay2114',
                'MotionReplay', 'LiveMotionReplay', 'MotionReadRecoveryReplay',
                'UiHttpFailureReplay',
                'ShortcutPreferencesReplay', 'ShortcutDraftProperties',
                'SnapReplay', 'GeometryCapabilitySequences', 'TransferReplay',
                'AnnouncementReplay', 'TaskViewReplay', 'PinMaxReplay',
                'FullscreenExitReplay',
            )
            extra_runners = (
                'files-typed-state.cjs', 'sol-files-rebind-result-2214.cjs',
                'system-menu-typed-state.cjs', 'motion-typed-state.cjs',
                'motion-read-recovery.cjs', 'tea001-extra-typed.cjs',
                'shortcut-draft-strict.cjs',
                'ui-http-failure-typed.cjs',
            )
            for filename in (*(worker + '.elm' for worker in extra_workers), *extra_runners):
                source = root / 'qa' / filename
                if source.is_symlink() or not source.is_file():
                    raise RuntimeError('Fixed TEA001 worker/runner missing: ' + filename)
                key = str(source.relative_to(REPO))
                digest = sha(source)
                sources[key] = digest
                staged = work / 'qa' / filename
                shutil.copy2(source, staged)
                if staged.is_symlink() or not staged.is_file() or sha(staged) != digest:
                    raise RuntimeError('TEA001 staged input mismatch: ' + filename)
                staged_tea_sources[key] = digest
            for worker in extra_workers:
                compiled = output / (worker + '.js')
                run('compile-tea001-' + worker,
                    [compiler, 'make', 'qa/' + worker + '.elm', '--optimize', '--output=' + str(compiled)])
                if compiled.is_symlink() or not compiled.is_file() or compiled.stat().st_size == 0:
                    raise RuntimeError('TEA001 compiled worker missing: ' + worker)
                selected_artifacts[worker] = sha(compiled)

            def run_fixed_component(label, runner, workers, counts):
                result_path = output / (label + '.json')
                if result_path.exists() or result_path.is_symlink():
                    raise RuntimeError('TEA001 output already exists: ' + label)
                args = [str(node), 'qa/' + runner]
                args.extend(str(output / (worker + '.js')) for worker in workers)
                args.append(str(result_path))
                run(label, args)
                if result_path.is_symlink() or not result_path.is_file():
                    raise RuntimeError('TEA001 result missing: ' + label)
                result = json.loads(result_path.read_text())
                rows = result.get('fixtures')
                if rows is None and len(workers) == 1:
                    rows = [result.get('result')]
                if (result.get('passed') is not True or not isinstance(rows, list)
                        or len(rows) != len(workers)
                        or ('failures' in result and result['failures'] != [])
                        or (label in ('tea001-motion', 'tea001-extra-typed')
                            and result.get('failures') != [])
                        or [row.get('name') for row in rows] != list(workers)):
                    raise RuntimeError('TEA001 result identity/integrity failed: ' + label)
                for worker, count, row in zip(workers, counts, rows):
                    checks = row.get('checks')
                    if (row.get('passed') is not True or row.get('sha256') != selected_artifacts[worker]
                            or not isinstance(checks, list) or len(checks) != count
                            or any(check.get('passed') is not True for check in checks)
                            or len({check.get('name') for check in checks}) != count):
                        raise RuntimeError('TEA001 exact worker witness failed: ' + worker)
                recorded_runner = result.get('runnerSha256', result.get('runnerPathSha256AtReport'))
                if recorded_runner != staged_tea_sources['implementation/warlock/qa/' + runner]:
                    raise RuntimeError('TEA001 runner changed: ' + runner)
                if (label == 'tea001-http-failure'
                        and result.get('sourceReplaySha256Expected')
                        != staged_tea_sources['implementation/warlock/qa/UiHttpFailureReplay.elm']):
                    raise RuntimeError('TEA001 UiHttp failure fixture pin mismatch')
                report.setdefault('tea001Workers', {})[label] = {
                    'fixtures': list(workers), 'counts': list(counts),
                    'resultSHA256': sha(result_path), 'nativeAccepted': False,
                    'originalAccepted': False}

            run_fixed_component('tea001-files', 'files-typed-state.cjs', ('FilesReplay',), (31,))
            run_fixed_component('tea001-http-failure', 'ui-http-failure-typed.cjs',
                                ('UiHttpFailureReplay',), (14,))
            run_fixed_component('tea001-files-rebind', 'sol-files-rebind-result-2214.cjs',
                                ('SolFilesRebind2214',), (176,))
            run_fixed_component('tea001-system-menu', 'system-menu-typed-state.cjs',
                                ('SystemMenuReplay', 'SolSystemMenuIntegratedReplay2114'), (28, 650))
            run_fixed_component('tea001-motion', 'motion-typed-state.cjs',
                                ('MotionReplay', 'LiveMotionReplay'), (18, 31))
            # Fixed selected geometry/shortcut suite; runner carries exact
            # per-fixture names and reports them, never a dynamic all-values pass.
            extra_names = ('ShortcutPreferencesReplay', 'SnapReplay', 'GeometryCapabilitySequences',
                           'TransferReplay', 'AnnouncementReplay', 'TaskViewReplay',
                           'PinMaxReplay', 'FullscreenExitReplay')
            extra_counts = (26, 45, 16, 16, 12, 78, 28, 17)
            run_fixed_component('tea001-extra-typed', 'tea001-extra-typed.cjs', extra_names, extra_counts)
            run('tea001-motion-recovery', [str(node), 'qa/motion-read-recovery.cjs',
                                           str(output / 'MotionReadRecoveryReplay.js')])
            recovery = json.loads((output / 'tea001-motion-recovery.stdout').read_text())
            if (recovery.get('cases') != 16 or recovery.get('checksPerCase') != 8
                    or recovery.get('failures') != []):
                raise RuntimeError('TEA001 motion read recovery incomplete')
            report['tea001MotionRecovery'] = {'cases': 16, 'checksPerCase': 8,
                'resultSHA256': sha(output / 'tea001-motion-recovery.stdout')}
            run('tea001-shortcut-properties', [str(node), 'qa/shortcut-draft-strict.cjs',
                                                str(output / 'ShortcutDraftProperties.js')])
            properties = json.loads((output / 'tea001-shortcut-properties.stdout').read_text())
            if (properties.get('seed') != 0x5eeda405 or properties.get('algorithm') != 'xorshift32'
                    or properties.get('sequences') != 200 or properties.get('failureCount') != 0
                    or properties.get('failures') != []
                    or properties.get('hashes') != {
                        'harness': sha(work / 'qa/shortcut-draft-strict.cjs'),
                        'artifact': selected_artifacts['ShortcutDraftProperties'],
                        'fixture': sha(work / 'qa/ShortcutDraftProperties.elm'),
                        'preferences': sha(work / 'src/ShortcutPreferences.elm'),
                        'counter': sha(work / 'src/UInt64.elm'),
                        'elmManifest': staged_elm_manifest_sha}):
                raise RuntimeError('TEA001 seeded shortcut properties incomplete')
            report['tea001ShortcutProperties'] = {'seed': 0x5eeda405, 'sequences': 200,
                'resultSHA256': sha(output / 'tea001-shortcut-properties.stdout')}
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
                    or not isinstance(contract.get('cases'), list)
                    or len(contract['cases']) != len(TEA001_POLICY_CASES)
                    or set(contract['cases']) != TEA001_POLICY_CASES
                    or contract.get('transitions', 0) < 134 or contract.get('preludes', 0) < 31
                    or contract.get('runsPerCase') != 2
                    or contract.get('originalFixtureSha256') != sha(output / 'tea-contract.js')
                    or contract.get('oracleSha256') != sha(work / 'qa/tea-contract-cases.cjs')
                    or contract.get('runnerSha256') != sha(work / 'qa/tea-contract.cjs')
                    or contract.get('fixtureElmSha256') != sha(work / 'qa/TeaContractReplay.elm')):
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
            run_receipt_models(node, pin, cli, run)
            text = (output / 'receipt-model-safety.stdout').read_text()
            witnesses = {name: int(count) for name, count in re.findall(r'(witness\w+) was witnessed in (\d+) trace', text)}
            report['modelWitnessCounts'] = witnesses
            if len(witnesses) != 7 or any(count == 0 for count in witnesses.values()):
                raise RuntimeError('Model reachability witness missing or zero; inspect retained sampling report')
            if quint_toolchain()[0] != pin or sha(node) != pin['node']['sha256']:
                raise RuntimeError('Receipt model toolchain changed')
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
        if args.subscriptions:
            if (staged_site.is_symlink() or not staged_site.is_file() or sha(staged_site) != sources[site_key]
                    or staged_site_manifest.is_symlink() or not staged_site_manifest.is_file()
                    or sha(staged_site_manifest) != sources[site_manifest_key]):
                raise RuntimeError('SiteMain inventory or elm.json stage changed')
            site_artifact = output / 'SiteMain.plain.js'
            if site_artifact.is_symlink() or not site_artifact.is_file() or sha(site_artifact) != site_plain_hash:
                raise RuntimeError('SiteMain plain root artifact changed')
            for name, digest in plain_hashes.items():
                artifact = output / (name + '.plain.js')
                if artifact.is_symlink() or not artifact.is_file() or sha(artifact) != digest:
                    raise RuntimeError('HTTP plain root artifact changed: ' + name)
            for filename in qa_files:
                staged = subscription_qa / filename
                if (staged.is_symlink() or not staged.is_file()
                        or sha(staged) != sources['implementation/warlock/qa/' + filename]):
                    raise RuntimeError('Subscription harness/source stage changed: ' + filename)
        if args.tea_contract or args.subscriptions:
            if (work / 'elm.json').is_symlink() or sha(work / 'elm.json') != staged_elm_manifest_sha:
                raise RuntimeError('Staged Elm manifest changed during execution')
            report['stagedElmManifestSHA256'] = staged_elm_manifest_sha
            for key, digest in staged_tea_sources.items():
                staged = work / 'qa' / Path(key).name
                if staged.is_symlink() or not staged.is_file() or sha(staged) != digest:
                    raise RuntimeError('TEA001 staged input changed during execution: ' + key)
            for worker, digest in selected_artifacts.items():
                artifact = output / (worker + '.js')
                if artifact.is_symlink() or not artifact.is_file() or sha(artifact) != digest:
                    raise RuntimeError('TEA001 compiled worker changed during execution: ' + worker)
            for key, digest in sources.items():
                qa_prefix = 'implementation/warlock/qa/'
                if key.startswith(qa_prefix):
                    staged_qa = work / 'qa' / key[len(qa_prefix):]
                    if staged_qa.is_symlink() or not staged_qa.is_file() or sha(staged_qa) != digest:
                        raise RuntimeError('Staged QA input changed: ' + key)
                prefix = 'implementation/warlock/src/'
                if key.startswith(prefix):
                    staged = work / 'src' / key[len(prefix):]
                    if staged.is_symlink() or not staged.is_file() or sha(staged) != digest:
                        raise RuntimeError('Staged Elm source changed: ' + key)
        if not all(sha(REPO / p) == digest for p, digest in sources.items()):
            raise RuntimeError('Source changed during protected check')
        if not all(sha(Path(tool['path'])) == tool['sha256'] for tool in report['developmentTools'].values()):
            raise RuntimeError('Development interpreter changed during protected check')
        report['artifacts'] = {p.name: sha(p) for p in output.glob('*.js')}
        if args.tea_contract or args.standalone_mvp or args.subscriptions:
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

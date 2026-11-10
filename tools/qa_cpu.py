#!/usr/bin/env python3
"""Reviewed CPU-only QA for development hosts without a native DRM provider.

No arbitrary command interface: a hash-bound review permits fixed development runners only.
Native campaigns must still use the unchanged qa_run.py and loop.py native.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import uuid

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reviewed(path, expected):
    if path.is_symlink() or not path.is_file() or digest(path) != expected:
        raise RuntimeError('Reviewed input missing or changed: ' + str(path))



def reviewed_inputs(packet):
    for name, sha in packet['inputs'].items():
        candidate = Path(name)
        if candidate.is_absolute() or '..' in candidate.parts:
            raise RuntimeError('Review input must be repository-relative')
        reviewed(REPO / candidate, sha)


def registry_inputs(root, self_test=False):
    names = {'tools/qa_cpu.py', 'tools/check_registry_cpu.py', 'window-integration-qa/qa_launch.py',
             'implementation/warlock/qa/check-registry-admission.py',
             'plugins/warlock-contributor/scripts/warlock.py',
             'docs/elm-roadmap/requirements.json',
             'docs/elm-roadmap/baselines/requirements-pre-language-20261030.json',
             'docs/elm-roadmap/language-revision.json', 'docs/elm-roadmap/tools/language_revision.py',
             'docs/elm-roadmap/TRACEABILITY.md', 'openspec/changes/elm-desktop-pivot/tasks.md',
             'docs/warlock-build-loop/v2/STATE.json', 'docs/warlock-build-loop/v2/requirement-ledger.json'}
    if self_test:
        names.update({'tools/warlock_continuity.py', 'tools/test_warlock_continuity.py'})
        names.update(str(path.relative_to(root)) for path in (root / 'plugins/warlock-contributor').rglob('*')
                     if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc')
        names.update(['docs/warlock-build-loop/v2/loop.py', 'implementation/elm-build-loop-v1/loop.py',
                      'window-integration-qa/qa_run.py'])
    return names


def haskell_inputs(root, prepare=False, site=False):
    names = {'tools/qa_cpu.py', 'tools/check_haskell_cpu.py', 'tools/haskell-toolchain.json',
             'window-integration-qa/qa_launch.py'}
    if site:
        # The fixed site profile invokes site_only, not the Haskell build or
        # application compiler. Bind its actual complete inputs so unrelated
        # application edits do not invalidate this independent compilation.
        names.update({'tools/haskell_build.py', 'site/elm.json',
                      'implementation/warlock-preview-provider-v143/qa/toolchain.py',
                      'implementation/warlock-preview-provider-v143/qa/toolchain.json'})
        names.update(str(path.relative_to(root)) for path in (root / 'site/src').rglob('*')
                     if path.is_file() and '__pycache__' not in path.parts)
        return names
    if not prepare:
        names.update({'tools/haskell_build.py', 'tools/haskell_test_wrapper.py', 'tools/haskell-dependencies.json',
                      'tools/elm_http_dependencies.py', 'tools/elm-http-dependencies.json',
                      'tools/ui_host_toolchain.py', 'tools/ui-host-toolchain.json',
                      'tools/check_elm_cpu.py', 'tools/quint-toolchain.json', 'tools/ui_backend_frontend.py',
                      'implementation/warlock-preview-provider-v143/qa/toolchain.py',
                      'implementation/warlock-preview-provider-v143/qa/toolchain.json',
                      'implementation/warlock/elm.json', 'implementation/warlock/qa/ui-backend-port.cjs',
                      'implementation/warlock/qa/ui-native-stream.qnt',
                      'implementation/warlock/qa/ui-native-stream_test.qnt'})
        names.update(str(path.relative_to(root)) for path in (root / 'implementation/warlock/src').rglob('*.elm'))
        names.update(str(path.relative_to(root)) for path in (root / 'implementation/warlock/haskell').rglob('*')
                     if path.is_file() and not any(part in ('dist-newstyle', '__pycache__') for part in path.parts))
    if 'tools/quint-toolchain.json' in names:
        names.update({'tools/toolchain_derivative.py', 'tools/host-toolchain-derivative.json'})
    return names


def continuity_inputs(root):
    return {'tools/qa_cpu.py', 'tools/check_continuity_cpu.py',
            'tools/warlock_continuity.py', 'tools/test_warlock_continuity.py',
            'window-integration-qa/qa_launch.py'}


TEAM_QUINT_PAIRS = ('schema', 'authority', 'transport', 'http', 'consumption')


def team_quint_inputs(root, pair):
    if pair not in TEAM_QUINT_PAIRS:
        raise RuntimeError('Unknown fixed team model pair')
    prefix = '.warlock-contributor/team-quint-inputs/' + pair + '/'
    return {'tools/qa_cpu.py', 'tools/check_team_quint_cpu.py', 'tools/team-quint-toolchain.json',
            'tools/quint-toolchain.json', 'window-integration-qa/qa_launch.py',
            prefix + 'request.json', prefix + 'plan.json', prefix + 'snapshot.json',
            prefix + 'tea004-preview-' + pair + '.qnt',
            prefix + 'tea004-preview-' + pair + '_test.qnt'}


def arm64_inputs(root, subscriptions=False, preview_control=False, protocol_only=False, consumption=False, successor_focus=False, workspace_owner_baseline=False, workspace_owner_component=False, workspace_owner_component_red=False, workspace_original=False, workspace_dom=False, daemon_only=False, application_availability=False, native_stage_build=False, provider_probe_build=False, provider_callback_build=False, physical_context_owner_build=False, physical_context_owner_bridge=False, physical_context_owner_backing=False, virtual_pointer_build=False, ux003_journey_build=False, aquamarine_build=False):
    if aquamarine_build:
        manifest_name = '.warlock-contributor/evidence/nextloop-20261106/aquamarine-build-inputs/inputs.json'
        manifest_path = root / manifest_name
        if manifest_path.is_symlink() or digest(manifest_path) != '9e7347b8903b162c9042b5be6d3b6f52b3caac962fcb3d9b194c4d444ba9feb6':
            raise RuntimeError('Aquamarine supplemental manifest changed')
        manifest = json.loads(manifest_path.read_text())
        names = {'tools/qa_cpu.py', 'tools/check_arm64_cpu.py', 'tools/arm64_toolchain.py',
                 'tools/aquamarine_build.py', 'tools/test_aquamarine_build.py',
                 'tools/run_arm_nested_foundation.py', 'tools/test_arm_nested_foundation.py',
                 'tools/run_arm_gl_foundation.py', 'tools/test_arm_gl_foundation.py',
                 'tools/arm64-toolchain.json', 'tools/haskell-toolchain.json',
                 'tools/ui-host-toolchain.json', 'tools/elm-http-dependencies.json',
                 'tools/haskell-dependencies.json',
                 'window-integration-qa/qa_launch.py', manifest_name}
        names.update(name for name, entry in manifest['files'].items() if 'sha256' in entry)
        if any(Path(name).is_absolute() or '..' in Path(name).parts for name in names):
            raise RuntimeError('Aquamarine supplemental input escaped repository')
        return names
    if ux003_journey_build:
        names = arm64_inputs(root, physical_context_owner_backing=True)
        names.update({'implementation/warlock/haskell/runtime/fixture-ux003-native-observer/Main.hs',
                      'implementation/warlock/haskell/runtime/src/Warlock/Backend.hs',
                      'implementation/warlock/haskell/runtime/test-application-owner-route/Main.hs',
                      'tools/run_ux003_native_journey.py', 'tools/test_ux003_native_journey.py'})
        return names
    if virtual_pointer_build:
        return {'tools/haskell-toolchain.json', 'tools/check_arm64_cpu.py', 'implementation/warlock/qa/native-runtime-helpers/wlr-virtual-pointer-unstable-v1.xml', 'implementation/warlock/qa/native-runtime-helpers/virtual-pointer-protocol-provenance.json', 'tools/ui-host-toolchain.json', 'tools/provider_callback_build.py', 'tools/qa_cpu.py', 'tools/elm-http-dependencies.json', 'implementation/warlock/qa/native-runtime-helpers/LICENSE.wlr-virtual-pointer.txt', 'implementation/warlock/qa/native-runtime-helpers/virtual_pointer.c', 'tools/haskell-dependencies.json', 'window-integration-qa/qa_launch.py', 'tools/arm64-toolchain.json', 'tools/arm64_toolchain.py', 'tools/virtual_pointer_build.py', 'tools/test_virtual_pointer_build.py'}
    if physical_context_owner_backing:
        names = arm64_inputs(root, physical_context_owner_bridge=True)
        names.update({'implementation/warlock/haskell/runtime/ui/Warlock/Ui/FilterBackingRoot.hsc',
                      'implementation/warlock/haskell/runtime/test-filter-backing-root/Main.hs'})
        return names
    if physical_context_owner_bridge:
        names = arm64_inputs(root, physical_context_owner_build=True)
        names.update({'tools/haskell_test_wrapper.py', 'implementation/warlock/haskell/runtime/src/Warlock/Ui/EngineProtocol.hs','implementation/warlock/haskell/runtime/src/Warlock/Ui/EngineBroker.hs','implementation/warlock/haskell/runtime/src/Warlock/Ui/EngineAdapter.hs','implementation/warlock/haskell/runtime/ui/Warlock/Ui/EngineEntrypoint.hs','implementation/warlock/haskell/runtime/test-ui-engine-protocol/Main.hs','implementation/warlock/haskell/runtime/test-ui-engine-broker/Main.hs','implementation/warlock/haskell/runtime/ui/Main.hs','implementation/warlock/haskell/runtime/ui/Warlock/Ui/EngineCustody.hsc','implementation/warlock/haskell/runtime/test-ui-engine-protocol/ProtocolBoundary.hs','implementation/warlock/haskell/runtime/test-ui-engine-protocol/DesktopIdleControls.hs'})
        return names
    if physical_context_owner_build:
        # Finite compile/link-only extension; all original callback mode guards remain.
        names = arm64_inputs(root, provider_callback_build=True)
        names.update({'tools/physical_context_build.py', 'tools/test_physical_context_build.py',
                      'implementation/warlock/haskell/runtime/ui/Warlock/Ui/DefaultContextOwner.hs',
                      'implementation/warlock/haskell/runtime/ui/Warlock/Ui/CallbackRetirement.hs',
                      'implementation/warlock/haskell/runtime/ui/Warlock/Ui/ProcessSignalOwner.hs',
                      'implementation/warlock/haskell/runtime/test-ui-webkit/Main.hs',
                      'implementation/warlock/haskell/runtime/test-default-context-owner/Main.hs'})
        return names
    if provider_callback_build:
        # Fixed compile/link-only closure. No Elm frontend or native-stage campaigns.
        names = {'tools/qa_cpu.py', 'tools/check_arm64_cpu.py', 'tools/arm64_toolchain.py',
                 'tools/arm64-toolchain.json', 'tools/haskell-toolchain.json',
                 'tools/ui-host-toolchain.json', 'tools/elm-http-dependencies.json',
                 'tools/haskell-dependencies.json', 'window-integration-qa/qa_launch.py',
                 'tools/provider_callback_build.py', 'tools/test_provider_callback_build.py',
                 'implementation/warlock/haskell/runtime/test-webkit-callback-capi/callback-invoke.c'}
        names.update(str(p.relative_to(root)) for p in (root / 'implementation/warlock/haskell').rglob('*')
                     if p.is_file() and not any(part in ('dist-newstyle', '__pycache__') for part in p.parts))
        return names
    if daemon_only:
        return {'tools/qa_cpu.py', 'tools/check_arm64_cpu.py', 'tools/arm64_toolchain.py',
                'tools/arm64-toolchain.json', 'tools/ux031_daemon_only.py',
                'tools/ux031-private-bus.conf', 'window-integration-qa/qa_launch.py'}
    names = {'tools/qa_cpu.py', 'tools/check_arm64_cpu.py', 'tools/arm64_toolchain.py',
             'tools/arm64-toolchain.json', 'tools/haskell-toolchain.json',
             'tools/ui-host-toolchain.json', 'tools/elm-http-dependencies.json',
             'tools/haskell-dependencies.json', 'window-integration-qa/qa_launch.py',
             'implementation/warlock/elm.json'}
    names.update(str(p.relative_to(root)) for p in (root / 'implementation/warlock/src').rglob('*.elm'))
    if native_stage_build or provider_probe_build:
        names.update({'tools/arm64_native_stage.py', 'tools/test_arm64_native_stage.py',
                      'tools/omarchy_ui_mvp.py',
                      'implementation/warlock/qa/omarchy_trial/test_application_staging.py'})
    if provider_probe_build:
        names.update({'tools/run_webkit_provider_probe.py', 'tools/test_webkit_provider_probe_runner.py'})
    if application_availability:
        names.add('tools/check_elm_cpu.py')
        names.add('tools/elm_http_dependencies.py')
        names.update('implementation/warlock/qa/' + name for name in ('ApplicationAvailabilityReplay.elm', 'application-availability.cjs', 'NativePointerFixture.elm', 'StandaloneMvpReplay.elm', 'standalone-mvp.cjs'))
    elif workspace_original:
        names.update({'docs/elm-roadmap/INTERACTION.md', 'docs/elm-roadmap/requirements.json',
                      'openspec/changes/elm-desktop-pivot/specs/elm-shell-experience/spec.md'})
        names.update('implementation/warlock/qa/' + name for name in (
            'TaskViewReplay.elm', 'TaskViewEscapeReplay.elm', 'WorkspaceNavigationReplay.elm',
            'OutputRetirementReplay.elm', 'NativePointerFixture.elm', 'task-view-original-fixed.cjs'))
    elif workspace_dom:
        names.update({'docs/elm-roadmap/INTERACTION.md', 'docs/elm-roadmap/requirements.json',
                      'openspec/changes/elm-desktop-pivot/specs/elm-shell-experience/spec.md'})
        names.update('implementation/warlock/qa/' + name for name in (
            'WorkspaceUnsupportedDomReplay.elm', 'workspace-unsupported-dom-fixed.cjs',
            'ui006-dom-guard.js', 'ui006-dom-guard.html',
            'OutputRetirementReplay.elm', 'NativePointerFixture.elm'))
    elif workspace_owner_component_red:
        names.update({'docs/elm-roadmap/INTERACTION.md', 'docs/elm-roadmap/requirements.json',
                      'openspec/changes/elm-desktop-pivot/specs/elm-shell-experience/spec.md'})
        names.update('implementation/warlock/qa/' + name for name in (
            'WorkspaceOwnerComponentReplay.elm', 'Desktop-test-observer.txt',
            'workspace-owner-component-red-fixed.cjs', 'OutputRetirementReplay.elm', 'NativePointerFixture.elm'))
    elif workspace_owner_component:
        names.update({'docs/elm-roadmap/INTERACTION.md', 'docs/elm-roadmap/requirements.json',
                      'openspec/changes/elm-desktop-pivot/specs/elm-shell-experience/spec.md'})
        names.update('implementation/warlock/qa/' + name for name in (
            'WorkspaceOwnerComponentReplay.elm', 'Desktop-test-observer.txt',
            'workspace-owner-component-fixed.cjs', 'OutputRetirementReplay.elm', 'NativePointerFixture.elm'))
    elif workspace_owner_baseline:
        names.update({'docs/elm-roadmap/INTERACTION.md', 'docs/elm-roadmap/requirements.json',
                      'openspec/changes/elm-desktop-pivot/specs/elm-shell-experience/spec.md'})
        names.update('implementation/warlock/qa/' + name for name in (
            'WorkspaceOwnerLiteralReplay.elm', 'Desktop-test-observer.txt',
            'workspace-owner-literal-fixed.cjs', 'workspace-owner-baseline-fixed.cjs',
            'OutputRetirementReplay.elm', 'NativePointerFixture.elm'))
    elif successor_focus:
        names.update('implementation/warlock/qa/' + name for name in (
            'SystemMenuReplay.elm', 'SolSystemMenuIntegratedReplay2114.elm',
            'SystemMenuFocusPipeline.elm', 'SuccessorFocusReplay.elm', 'SystemMenuFocusExtended.elm',
            'NativePointerFixture.elm', 'system-menu-typed-state.cjs', 'successor-focus-harness.cjs',
            'check-search.py'))
    elif consumption:
        names.update('implementation/warlock/qa/' + name for name in (
            'PreviewConsumptionReplay.elm', 'preview-consumption.cjs', 'LocalFieldReplay.elm',
            'NotificationsReplay.elm', 'JumpListReplay.elm', 'NotificationRelevanceReplay.elm',
            'RetirementProofReplay.elm', 'NativePointerFixture.elm', 'typed-state.cjs'))
    elif subscriptions:
        # Preserve the entire existing subscription profile's oracle/source
        # closure while using only the new ARM compiler/cache selection.
        names.add('tools/check_elm_cpu.py')
        names.add('tools/elm_http_dependencies.py')
        names.add('tools/check_http_reachable_cpu.py')
        names.update(str(p.relative_to(root)) for p in (root / 'implementation/warlock/qa').rglob('*')
                     if p.is_file() and p.suffix in ('.elm', '.cjs', '.json'))
        names.update({'site/src/SiteMain.elm', 'site/elm.json',
                      'implementation/warlock/haskell/runtime/src/Warlock/Ui/Owner.hs'})
    else:
        names.add('tools/haskell_test_wrapper.py')
        names.update(str(p.relative_to(root)) for p in (root / 'implementation/warlock/haskell').rglob('*')
                     if p.is_file() and not any(part in ('dist-newstyle', '__pycache__') for part in p.parts))
    if protocol_only:
        names.discard('implementation/warlock/elm.json')
        names.difference_update(str(p.relative_to(root)) for p in (root / 'implementation/warlock/src').rglob('*.elm'))
    if preview_control:
        names.update('implementation/warlock/qa/' + name for name in (
            'http-preview-control-replay.cjs', 'http-preview-control-literals.cjs',
            'sol-http-root-observer-0535.cjs', 'sol-http-popup-literals-0525.cjs',
            'tea-contract-cases.cjs'))
    return names


def tea_inputs(root):
    names = {'tools/toolchain_derivative.py', 'tools/host-toolchain-derivative.json',
             'tools/ui-host-toolchain.json', 'tools/qa_cpu.py', 'tools/check_tea_cpu.py', 'tools/check_elm_cpu.py',
             'tools/elm_http_dependencies.py', 'tools/elm-http-dependencies.json',
             'tools/quint-toolchain.json', 'window-integration-qa/qa_launch.py',
             'implementation/warlock-preview-provider-v143/qa/toolchain.py',
             'implementation/warlock-preview-provider-v143/qa/toolchain.json',
             'implementation/warlock/elm.json'}
    names.update(str(p.relative_to(root)) for p in (root / 'implementation/warlock/src').rglob('*.elm'))
    names.update('implementation/warlock/qa/' + name for name in (
        'PinsPendingReplay.elm', 'pins-pending.cjs', 'PinsReplay.elm',
        'NativePointerFixture.elm', 'PreviewPaintReplay.elm',
        'AuthorityTupleReplay.elm', 'authority-tuple.cjs',
        'ReceiptStateReplay.elm', 'receipt-state.cjs',
        'StreamCapacityReplay.elm',
        'pins-save-lifecycle.qnt', 'pins-save-lifecycle_test.qnt',
        'receipt-lifecycle.qnt', 'receipt-lifecycle_test.qnt'))
    return names


def capi_invocation_controls_inputs(root):
    # Only pure unittest/mocked-runner code; no compiler, SDK build or native target.
    return {'tools/qa_cpu.py', 'tools/run_capi_invocation_probe.py',
            'tools/test_capi_invocation_probe.py', 'window-integration-qa/qa_launch.py'}


def menu_tab_dom_mode(runner, arguments):
    return runner == REPO / 'tools/check_elm_cpu.py' and arguments == ['--menu-tab-dom', '--arm64']


def menu_tab_dom_inputs(root):
    names = {'tools/qa_cpu.py', 'tools/check_elm_cpu.py', 'window-integration-qa/qa_launch.py',
             'tools/arm64_toolchain.py', 'tools/arm64-toolchain.json', 'tools/menu-tab-elm-toolchain.json',
             'implementation/warlock/elm.json', 'implementation/warlock/qa/ux024-menu-dom.cjs',
             'implementation/warlock/qa/MenuEscapeReplay.elm', 'implementation/warlock/qa/menu-escape.cjs',
             'implementation/warlock/qa/OutputRetirementReplay.elm',
             'implementation/warlock/qa/ux024-bar-context-dom.cjs',
             'implementation/warlock/qa/MenuInitialFocusReplay.elm', 'implementation/warlock/qa/menu-initial-focus.cjs'}
    names.update(str(p.relative_to(root)) for p in (root / 'implementation/warlock/src').rglob('*.elm'))
    return names



MENU_FOCUS_BUILD_PACKET = '.warlock-contributor/evidence/nextloop-20261106/ux024-menu-focus-build-v1-20261109/packet.json'
MENU_FOCUS_BUILD_RECORD = '.warlock-contributor/ux024-menu-tab-focus-root-20261109.json'
MENU_FOCUS_BUILD_IDENTITY = '60fc89b0b68fd5f48614e08c0b203a765442483ac57d5e2c59a1771ace553fa4'
MENU_FOCUS_BUILD_TARGETS = ('warlock-runtime:exe:warlock-ui-owner', 'warlock-runtime:test:ui-webkit-controls')
MENU_FOCUS_BUILD_SUPPORT = {'tools/qa_cpu.py', 'tools/run_ux024_menu_focus_build.py',
    'tools/test_ux024_menu_focus_build.py', 'plugins/warlock-contributor/scripts/warlock.py',
    'tools/arm64-toolchain.json', 'tools/arm64_toolchain.py', 'tools/haskell-dependencies.json',
    'tools/haskell_test_wrapper.py', 'tools/provider_callback_build.py',
    'window-integration-qa/qa_launch.py', 'window-integration-qa/qa_run.py'}


def menu_focus_build_mode(runner, arguments, packet_sha):
    return runner == REPO / 'tools/run_ux024_menu_focus_build.py' and arguments == ['--sha256', packet_sha]


def menu_focus_build_spec(root):
    import re
    path = root / MENU_FOCUS_BUILD_PACKET
    fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > 4 * 1024 * 1024:
            raise RuntimeError('Fixed menu focus packet must be bounded regular JSON')
        body = stream.read(4 * 1024 * 1024 + 1)
        after = os.fstat(stream.fileno())
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if identity(before) != identity(after) or len(body) != before.st_size:
        raise RuntimeError('Fixed menu focus packet changed while reading')
    packet = json.loads(body)
    fields = {'schema', 'kind', 'recordPath', 'recordIdentitySha256', 'selectionGeneration',
              'authorizationExpiresUTC', 'coreSha256', 'targets', 'behaviorSuites',
              'sourceHashes', 'haskellFiles', 'toolchainManifest', 'cacheCorrespondence'}
    if (not isinstance(packet, dict) or set(packet) != fields or packet['schema'] != 1
            or packet['kind'] != 'ux024-fixed-menu-focus-build'
            or packet['recordPath'] != MENU_FOCUS_BUILD_RECORD
            or packet['recordIdentitySha256'] != MENU_FOCUS_BUILD_IDENTITY
            or type(packet['selectionGeneration']) is not int or packet['selectionGeneration'] < 1
            or packet['targets'] != list(MENU_FOCUS_BUILD_TARGETS) or packet['behaviorSuites'] not in (['ui-webkit-controls'], ['ui-webkit-controls', 'foreign-endpoint-refusal-controls'])):
        raise RuntimeError('Fixed menu focus build scope differs')
    hs = root / 'implementation/warlock/haskell'
    current = set()
    for p in hs.rglob('*'):
        if any(part in ('dist-newstyle', '__pycache__') for part in p.relative_to(hs).parts):
            continue
        if p.is_symlink():
            raise RuntimeError('Haskell build source alias refused')
        if p.is_file():
            current.add(str(p.relative_to(hs)))
        elif not p.is_dir():
            raise RuntimeError('Haskell build source special file refused')
    files, sources = packet['haskellFiles'], packet['sourceHashes']
    if (not isinstance(files, dict) or not isinstance(sources, dict) or set(files) != current
            or set(sources) != MENU_FOCUS_BUILD_SUPPORT | {'implementation/warlock/haskell/' + n for n in current}
            or any(not isinstance(h, str) or re.fullmatch('[0-9a-f]{64}', h) is None for h in sources.values())
            or any(sources['implementation/warlock/haskell/' + n] != h for n, h in files.items())
            or packet['coreSha256'] != sources['plugins/warlock-contributor/scripts/warlock.py']):
        raise RuntimeError('Fixed menu focus build source closure differs')
    names = set(sources) | {MENU_FOCUS_BUILD_PACKET}
    for key in ('toolchainManifest', 'cacheCorrespondence'):
        ref = packet[key]
        if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'} or not isinstance(ref['sha256'], str) or re.fullmatch('[0-9a-f]{64}', ref['sha256']) is None:
            raise RuntimeError('Fixed menu focus metadata reference differs')
        p = Path(ref['path'])
        try:
            rel = p.relative_to(root) if p.is_absolute() else p
        except ValueError as error:
            raise RuntimeError('Fixed menu focus metadata must be inside repo') from error
        if '..' in rel.parts or str(rel) in ('', '.'):
            raise RuntimeError('Fixed menu focus metadata escape refused')
        if key == 'toolchainManifest' and (str(rel) != 'tools/arm64-toolchain.json' or ref['sha256'] != sources[str(rel)]):
            raise RuntimeError('Fixed menu focus SDK reference differs')
        names.add(str(rel))
    return {'inputs': names, 'packetSha256': hashlib.sha256(body).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--inside-scope', action='store_true')
    args = parser.parse_args()
    review = args.review.absolute()
    try:
        fd = os.open(review, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise RuntimeError('Expected regular CPU review packet')
            review_bytes = stream.read()
            after = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise RuntimeError('CPU review packet changed while reading')
    except OSError as error:
        raise RuntimeError('Expected regular CPU review packet') from error
    if hashlib.sha256(review_bytes).hexdigest() != args.sha256:
        raise RuntimeError('Reviewed packet missing or changed: ' + str(review))
    packet = json.loads(review_bytes)
    if set(packet) != {'schema', 'runner', 'arguments', 'inputs'} or packet['schema'] != 1:
        raise RuntimeError('Unknown CPU review shape')
    runner = Path(packet['runner'])
    registry = runner == REPO / 'tools/check_registry_cpu.py'
    haskell = runner == REPO / 'tools/check_haskell_cpu.py'
    tea = runner == REPO / 'tools/check_tea_cpu.py'
    continuity = runner == REPO / 'tools/check_continuity_cpu.py'
    arm64 = runner == REPO / 'tools/check_arm64_cpu.py'
    capi_controls = runner == REPO / 'tools/test_capi_invocation_probe.py'
    team_quint = runner == REPO / 'tools/check_team_quint_cpu.py'
    menu_focus_build = runner == REPO / 'tools/run_ux024_menu_focus_build.py'
    menu_focus_spec = menu_focus_build_spec(REPO) if menu_focus_build else None
    allowed = ([[], ['--capacity']] if tea else ([['--prepare'], ['--build'], ['--ui-origin'], ['--ui-models'], ['--site'], ['--custody'], ['--backend'], ['--persistent']] if haskell else
               ([[], ['--self-test']] if registry else [[], ['--browser'], ['--authority'], ['--receipts'], ['--standalone-mvp'], ['--status-scroll'], ['--tea-contract'], ['--subscriptions']])))
    if menu_tab_dom_mode(runner, packet['arguments']):
        allowed = [['--menu-tab-dom', '--arm64']]
    if menu_focus_build:
        if packet['inputs'].get(MENU_FOCUS_BUILD_PACKET) != menu_focus_spec['packetSha256']:
            raise RuntimeError('Fixed build packet hash differs from reviewed CPU inputs')
        allowed = [['--sha256', menu_focus_spec['packetSha256']]]
    if continuity:
        allowed = [[]]
    if arm64:
        allowed = [['--subscriptions'], ['--owner-build'], ['--owner'], ['--preview-control'], ['--protocol'],
                   ['--preview-consumption'], ['--preview-schema'], ['--held-executable'], ['--peer-role'], ['--successor-focus'], ['--workspace-owner-baseline'], ['--workspace-owner-component'], ['--workspace-owner-component-red'], ['--workspace-original'], ['--workspace-dom'], ['--workspace-navigation-protocol'], ['--ux031-daemon-only'], ['--notification-config'], ['--notification-issuer'], ['--catalog-nodisplay'], ['--catalog-source-revision'], ['--catalog-publication'], ['--application-owner-route'], ['--application-availability'], ['--native-stage-build'], ['--provider-probe-build'], ['--provider-callback-build'], ['--physical-context-owner-build'], ['--physical-context-owner-bridge'], ['--physical-context-owner-backing'], ['--virtual-pointer-build'], ['--ux003-journey-build'], ['--aquamarine-build']]
    if team_quint:
        allowed = [[flag] + tail for flag in ('--' + pair for pair in TEAM_QUINT_PAIRS)
                   for tail in ([], ['--tests-only'])]
    if capi_controls:
        allowed = [[]]
    if (not registry and not haskell and not tea and not continuity and not arm64 and not team_quint and not capi_controls and not menu_focus_build and runner != REPO / 'tools/check_elm_cpu.py') or packet['arguments'] not in allowed:
        raise RuntimeError('Only a fixed reviewed development runner and mode is supported')
    mandatory = {'tools/qa_cpu.py', 'tools/check_elm_cpu.py', 'window-integration-qa/qa_launch.py',
                 'tools/elm_http_dependencies.py', 'tools/elm-http-dependencies.json',
                 'implementation/warlock-preview-provider-v143/qa/toolchain.py',
                 'implementation/warlock-preview-provider-v143/qa/toolchain.json',
                 'implementation/warlock/elm.json'}
    mandatory.update(str(p.relative_to(REPO)) for p in (REPO / 'implementation/warlock/src').rglob('*.elm'))
    if packet['arguments'] == []:
        mandatory.update({'implementation/warlock/qa/UiHttpReplay.elm', 'implementation/warlock/qa/ui-http.cjs'})
    if packet['arguments'] == ['--standalone-mvp']:
        mandatory.update({'implementation/warlock/qa/UiHttpReplay.elm', 'implementation/warlock/qa/ui-http.cjs',
                          'implementation/warlock/qa/NativePointerFixture.elm',
                          'implementation/warlock/qa/StandaloneMvpReplay.elm', 'implementation/warlock/qa/standalone-mvp.cjs'})
    if packet['arguments'] == ['--subscriptions']:
        mandatory.update('implementation/warlock/qa/' + name for name in (
            'TeaPopupSubscriptionsReplay.elm', 'TeaBarSubscriptionsReplay.elm',
            'TeaAdmissionSubscriptionsReplay.elm', 'TeaRendererSubscriptionsReplay.elm',
            'tea-subscriptions-cases.cjs', 'tea-subscriptions.cjs', 'tea-contract-cases.cjs',
            'sol-http-root-observer-0535.cjs', 'sol-http-popup-literals-0525.cjs',
            'httpbar-literals.cjs', 'joined-control-literals.cjs', 'closed-topology-after-dismiss-literals.cjs', 'http-popup-control-literals.cjs', 'http-root-cases-manifest.json',
            'http-root-cases-guard.cjs', 'http-root-cases-negative.cjs',
            'sitemain-root-literals.cjs', 'sitemain-root-observer.cjs',
            'sitemain-root-manifest.json', 'sitemain-root-negative.cjs'))
        mandatory.update({'site/src/SiteMain.elm', 'site/elm.json',
                          'implementation/warlock/haskell/runtime/src/Warlock/Ui/Owner.hs'})
    if packet['arguments'] == ['--tea-contract']:
        mandatory.update({'implementation/warlock/qa/UiHttpReplay.elm', 'implementation/warlock/qa/ui-http.cjs',
                          'implementation/warlock/qa/TeaContractReplay.elm',
                          'implementation/warlock/qa/tea-contract.cjs',
                          'implementation/warlock/qa/tea-contract-cases.cjs',
                          'implementation/warlock/qa/FeedbackContextReplay.elm',
                          'implementation/warlock/qa/feedback-context.cjs',
                          'implementation/warlock/qa/NotificationsReplay.elm',
                          'implementation/warlock/qa/JumpListReplay.elm',
                          'implementation/warlock/qa/NotificationRelevanceReplay.elm',
                          'implementation/warlock/qa/RetirementProofReplay.elm',
                          'implementation/warlock/qa/LocalFieldReplay.elm',
                          'implementation/warlock/qa/local-field-publication.qnt',
                          'tools/quint-toolchain.json',
                          'implementation/warlock/qa/NativePointerFixture.elm',
                          'implementation/warlock/qa/typed-state.cjs',
                          'implementation/warlock/qa/FilesReplay.elm',
                          'implementation/warlock/qa/files-typed-state.cjs',
                          'implementation/warlock/qa/SolFilesRebind2214.elm',
                          'implementation/warlock/qa/sol-files-rebind-result-2214.cjs',
                          'implementation/warlock/qa/SystemMenuReplay.elm',
                          'implementation/warlock/qa/SolSystemMenuIntegratedReplay2114.elm',
                          'implementation/warlock/qa/system-menu-typed-state.cjs',
                          'implementation/warlock/qa/MotionReplay.elm',
                          'implementation/warlock/qa/LiveMotionReplay.elm',
                          'implementation/warlock/qa/MotionReadRecoveryReplay.elm',
                          'implementation/warlock/qa/motion-typed-state.cjs',
                          'implementation/warlock/qa/motion-read-recovery.cjs',
                          'implementation/warlock/qa/ShortcutPreferencesReplay.elm',
                          'implementation/warlock/qa/ShortcutDraftProperties.elm',
                          'implementation/warlock/qa/SnapReplay.elm',
                          'implementation/warlock/qa/GeometryCapabilitySequences.elm',
                          'implementation/warlock/qa/TransferReplay.elm',
                          'implementation/warlock/qa/AnnouncementReplay.elm',
                          'implementation/warlock/qa/TaskViewReplay.elm',
                          'implementation/warlock/qa/PinMaxReplay.elm',
                          'implementation/warlock/qa/FullscreenExitReplay.elm',
                          'implementation/warlock/qa/tea001-extra-typed.cjs',
                          'implementation/warlock/qa/shortcut-draft-strict.cjs',
                          'implementation/warlock/qa/UiHttpFailureReplay.elm',
                          'implementation/warlock/qa/ui-http-failure-typed.cjs'})
    if packet['arguments'] == ['--status-scroll']:
        mandatory.update({'implementation/warlock/qa/UiHttpReplay.elm', 'implementation/warlock/qa/ui-http.cjs',
                          'implementation/warlock/qa/StatusScrollReplay.elm', 'implementation/warlock/qa/status-scroll.cjs',
                          'implementation/warlock/qa/status-scroll.qnt', 'implementation/warlock/qa/status-scroll_test.qnt',
                          'implementation/warlock/qa/RestoreAnnouncementReplay.elm', 'implementation/warlock/qa/restore-announcement.cjs',
                          'implementation/warlock/qa/SnapReplay.elm', 'implementation/warlock/qa/NativePointerFixture.elm',
                          'tools/quint-toolchain.json'})
    fixture = REPO / 'implementation/warlock/qa/FeedbackContextReplay.elm'
    if packet['arguments'] == ['--authority']:
        mandatory.update(['implementation/warlock/qa/AuthorityTupleReplay.elm',
                          'implementation/warlock/qa/authority-tuple.cjs'])
    elif packet['arguments'] == ['--receipts']:
        mandatory.update(['implementation/warlock/qa/ReceiptStateReplay.elm',
                          'implementation/warlock/qa/receipt-state.cjs',
                          'implementation/warlock/qa/receipt-lifecycle.qnt',
                          'implementation/warlock/qa/receipt-lifecycle_test.qnt', 'tools/quint-toolchain.json'])
    elif fixture.exists() and packet['arguments'] != ['--subscriptions']:
        mandatory.update(['implementation/warlock/qa/FeedbackContextReplay.elm',
                          'implementation/warlock/qa/feedback-context.cjs'])
    if packet['arguments'] == ['--browser']:
        mandatory.update(['tools/check_feedback_browser.py',
                          'implementation/warlock/qa/feedback-context-browser.mjs',
                          'implementation/warlock/assets/shell.css'])
    if registry:
        mandatory = registry_inputs(REPO, packet['arguments'] == ['--self-test'])
    if tea:
        mandatory = tea_inputs(REPO)
    if haskell:
        mandatory = haskell_inputs(REPO, packet['arguments'] == ['--prepare'], site=packet['arguments'] == ['--site'])
    if 'tools/quint-toolchain.json' in mandatory or 'tools/ui-host-toolchain.json' in mandatory:
        mandatory.update({'tools/toolchain_derivative.py', 'tools/host-toolchain-derivative.json',
                          'tools/ui-host-toolchain.json', 'tools/quint-toolchain.json'})
    if continuity:
        mandatory = continuity_inputs(REPO)
    if arm64:
        mandatory = arm64_inputs(REPO, aquamarine_build=packet['arguments'] == ['--aquamarine-build'], ux003_journey_build=packet['arguments'] == ['--ux003-journey-build'], virtual_pointer_build=packet['arguments'] == ['--virtual-pointer-build'], physical_context_owner_backing=packet['arguments'] == ['--physical-context-owner-backing'], physical_context_owner_bridge=packet['arguments'] == ['--physical-context-owner-bridge'], physical_context_owner_build=packet['arguments'] == ['--physical-context-owner-build'], provider_callback_build=packet['arguments'] == ['--provider-callback-build'], provider_probe_build=packet['arguments'] == ['--provider-probe-build'], native_stage_build=packet['arguments'] == ['--native-stage-build'], application_availability=packet['arguments'] == ['--application-availability'], subscriptions=packet['arguments'] == ['--subscriptions'],
                                 preview_control=packet['arguments'] == ['--preview-control'],
                                 protocol_only=packet['arguments'] in (['--protocol'], ['--preview-schema'], ['--held-executable'], ['--peer-role'], ['--workspace-navigation-protocol'], ['--notification-config'], ['--notification-issuer'], ['--catalog-nodisplay'], ['--catalog-source-revision'], ['--catalog-publication'], ['--application-owner-route']),
                                 consumption=packet['arguments'] == ['--preview-consumption'],
                                 successor_focus=packet['arguments'] == ['--successor-focus'],
                                 workspace_owner_baseline=packet['arguments'] == ['--workspace-owner-baseline'],
                                 workspace_owner_component=packet['arguments'] == ['--workspace-owner-component'],
                                 workspace_owner_component_red=packet['arguments'] == ['--workspace-owner-component-red'],
                                 workspace_original=packet['arguments'] == ['--workspace-original'],
                                 workspace_dom=packet['arguments'] == ['--workspace-dom'],
                                 daemon_only=packet['arguments'] == ['--ux031-daemon-only'])
    if team_quint:
        mandatory = team_quint_inputs(REPO, packet['arguments'][0][2:])
    if capi_controls:
        mandatory = capi_invocation_controls_inputs(REPO)
    if menu_tab_dom_mode(runner, packet['arguments']):
        mandatory = menu_tab_dom_inputs(REPO)
    if menu_focus_build:
        mandatory = menu_focus_spec['inputs']
    if set(packet['inputs']) != mandatory:
        raise RuntimeError('CPU review does not match the complete current source/fixture/toolchain closure')
    reviewed_inputs(packet)
    if not args.inside_scope:
        command = ['systemd-run', '--user', '--scope', '--slice=qa-harness.slice',
                   '--unit=qa-harness-' + uuid.uuid4().hex, '-p', 'MemoryMax=3G', '--',
                   'prlimit', '--core=1:1', '--', sys.executable, '-B', str(Path(__file__).resolve()),
                   '--inside-scope', '--review', str(review), '--sha256', args.sha256]
        os.execvp(command[0], command)
    require_qa_scope()
    base = runtime_base()
    # Serialize this host's CPU equivalent. The lock is never unlinked.
    fd = os.open(base / 'cpu-check.lock', os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as lock:
        info = os.fstat(lock.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600:
            raise RuntimeError('Unsafe CPU lock')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        current = (base / 'cpu-check.lock').lstat()
        if (current.st_dev, current.st_ino) != (info.st_dev, info.st_ino):
            raise RuntimeError('CPU lock path replaced')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for name in ('DISPLAY', 'WAYLAND_DISPLAY', 'WAYLAND_SOCKET', 'XAUTHORITY',
                     'HYPRLAND_INSTANCE_SIGNATURE', 'AQ_DRM_DEVICES', 'AQ_BACKENDS', 'AT_SPI_BUS_ADDRESS'):
            env.pop(name, None)
        if capi_controls:
            env.pop('WARLOCK_CAPI_RUNNER_UNDER_TEST', None)
        reviewed(review, args.sha256)
        reviewed_inputs(packet)
        child = subprocess.Popen([sys.executable, '-B', str(runner), *packet['arguments']], cwd=REPO, env=env, start_new_session=True)
        try:
            return child.wait(timeout=902 if menu_focus_build else (3600 if haskell or arm64 or team_quint else (600 if tea else 240)))
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            raise
        finally:
            prior = sys.exception()
            try:
                reviewed(review, args.sha256)
                reviewed_inputs(packet)
            except Exception as post_error:
                if prior is not None:
                    prior.add_note('Post-run review check also failed: ' + str(post_error))
                else:
                    raise RuntimeError('Post-run review check failed; child status: ' + str(child.returncode)) from post_error


if __name__ == '__main__':
    raise SystemExit(main())

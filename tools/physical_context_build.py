#!/usr/bin/env python3
"""Fixed physical-context compile/link profile. Never executes a compiled image."""
import hashlib
import json
from pathlib import Path
import re
import shutil

from arm64_toolchain import digest, inventory
from provider_callback_build import command_plan as callback_command_plan, pin_image

TARGETS = (
    ('warlock-ui-owner', 'warlock-runtime:exe:warlock-ui-owner'),
    ('ui-webkit-controls', 'warlock-runtime:test:ui-webkit-controls'),
    ('physical-context-owner-controls', 'warlock-runtime:test:physical-context-owner-controls'),
    ('physical-context-owner-threaded-controls', 'warlock-runtime:test:physical-context-owner-threaded-controls'),
)
# Exact composed ownership/provider source; independent product review and
# Root adoption/qualification remain required. These hashes grant no authority.
CABAL_SHA256 = '307eaf327e5d0319efe734b960d1de833d9e656c0c49cffdf822b5ea712da9e3'
SOURCE_HASHES = {'ui/Warlock/Ui/DefaultContextOwner.hs': '7dbe4fb93a6c7bc98078c75819e43b046e1ef53c63b0946a23b3b6ef30413743', 'test-default-context-owner/Main.hs': 'a03e015ee86c7f581e86fc103ecf0853bd8241add9fbae98d04c9ada4184e197', 'ui/Warlock/Ui/WebKit.hs': '00de662b6b93ea2b17592feabcc3c9433bfc742e655593c93fff97655da00f02', 'ui/Warlock/Ui/Mvp.hsc': '54f22a62eb9ef59d2bc25710ad11dc79265c4a2ab44b2ac147ffb9799015723d', 'ui/Warlock/Ui/CallbackRetirement.hs': '76dace5cb34d05a4e13f587615a824f73ac29297074897f065fc935ce73d25f4', 'ui/Warlock/Ui/ProcessSignalOwner.hs': '01378b006b4de137fd1bd14ec172585e5559139af653280de6c145ddbde30170', 'test-ui-webkit/Main.hs': 'f057132baf7ecc1bcd70c485430dd973298ed6e2ae4a3d521107edc300f213c9'}
COMPONENT_STANZAS = {'executable warlock-ui-owner': 'executable warlock-ui-owner\n  hs-source-dirs: ui\n  main-is: Main.hs\n  other-modules: Warlock.Ui.EngineEntrypoint, Warlock.Ui.WebKit, Warlock.Ui.WebKitABI, Warlock.Ui.EngineCustody, Warlock.Ui.Mvp, Warlock.Ui.DefaultContextOwner, Warlock.Ui.CallbackRetirement, Warlock.Ui.ProcessSignalOwner, Warlock.Ui.FilterBackingRoot\n  pkgconfig-depends: gobject-2.0\n  extra-libraries: webkitgtk-6.0, gtk-4, gobject-2.0, gio-2.0, glib-2.0, soup-3.0\n  build-depends: base >=4.18 && <5, bytestring, text, unix, directory, filepath, warlock-runtime, warlock-protocol, warlock-process-custody, network ==3.2.0.0, cryptohash-sha256 ==0.11.102.1\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0\n', 'test-suite ui-webkit-controls': 'test-suite ui-webkit-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-ui-webkit, ui\n  main-is: Main.hs\n  other-modules: Warlock.Ui.WebKit, Warlock.Ui.WebKitABI, Warlock.Ui.EngineCustody, Warlock.Ui.Mvp, Warlock.Ui.DefaultContextOwner, Warlock.Ui.CallbackRetirement, Warlock.Ui.ProcessSignalOwner\n  pkgconfig-depends: gobject-2.0\n  extra-libraries: webkitgtk-6.0, gtk-4, gobject-2.0, gio-2.0, glib-2.0, soup-3.0\n  build-depends: base >=4.18 && <5, bytestring, text, unix, directory, filepath, process ==1.6.19.0, warlock-runtime, warlock-protocol, warlock-process-custody, network ==3.2.0.0, cryptohash-sha256 ==0.11.102.1\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0\n', 'test-suite physical-context-owner-controls': 'test-suite physical-context-owner-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-default-context-owner, ui\n  main-is: Main.hs\n  other-modules: Warlock.Ui.DefaultContextOwner, Warlock.Ui.CallbackRetirement, Warlock.Ui.ProcessSignalOwner\n  pkgconfig-depends: gobject-2.0, gio-2.0\n  build-depends: base >=4.18 && <5, unix, warlock-runtime\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0\n', 'test-suite physical-context-owner-threaded-controls': 'test-suite physical-context-owner-threaded-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-default-context-owner, ui\n  main-is: Main.hs\n  other-modules: Warlock.Ui.DefaultContextOwner, Warlock.Ui.CallbackRetirement, Warlock.Ui.ProcessSignalOwner\n  pkgconfig-depends: gobject-2.0, gio-2.0\n  build-depends: base >=4.18 && <5, unix, warlock-runtime\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -threaded -with-rtsopts=-V0\n'}


BRIDGE_TARGETS = TARGETS + (
    ('ui-engine-protocol-controls', 'warlock-runtime:test:ui-engine-protocol-controls'),
    ('ui-engine-broker-controls', 'warlock-runtime:test:ui-engine-broker-controls'),
)
BRIDGE_BEHAVIOR_SUITES = ('ui-engine-protocol-controls', 'ui-engine-broker-controls')
BRIDGE_SOURCE_HASHES = {'src/Warlock/Ui/EngineProtocol.hs': 'c65efea15a5a9adba80bd6f10462f9ebf4bd685b7726b343f427576f30b97191', 'src/Warlock/Ui/EngineBroker.hs': '4818a8094e42b61521995583544f5eb02b1a162c674d57918c2e4ff26ab5f515', 'src/Warlock/Ui/EngineAdapter.hs': 'dda839d4a8bb6d618b1ac6132bf84097d8d858e18d7bee2877b27e4a21388ca5', 'ui/Warlock/Ui/EngineEntrypoint.hs': '50b13ce201401779d135957052c5479b495148fbc482e3a34da5f121ba1d36e8', 'test-ui-engine-protocol/Main.hs': '1db41be2a723c8996481d31ff4a0a85e721a580c7f13b6466543b13e80f58a26', 'test-ui-engine-broker/Main.hs': 'dd27d93061fa60490b3f4c1f6f28f639e652cec4aafc8614be3db91968532c0e', 'ui/Main.hs': '1efe1ec3625abbaabe0ba237166b2990bd2f82b034a01abd033ae8cbb9bbf497', 'ui/Warlock/Ui/EngineCustody.hsc': '5e7175ba4d90cfe622b0b382c37440bbe51496dc3b550c59fde20f840a833f8f', 'test-ui-engine-protocol/ProtocolBoundary.hs': '3e294c7a095bf5b67c5396b3f2377affb02882d7136a814d95838552dbb07759', 'test-ui-engine-protocol/DesktopIdleControls.hs': 'b5741ca909729a17c529c24e41e47359e7b2dc02b6cbd5b506fb4fb48c1ef74a'}
BRIDGE_COMPONENT_STANZAS = {'test-suite ui-engine-protocol-controls': 'test-suite ui-engine-protocol-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-ui-engine-protocol\n  main-is: Main.hs\n  other-modules: ProtocolBoundary, DesktopIdleControls\n  build-depends: base >=4.18 && <5, bytestring, text, unix, network ==3.2.0.0, warlock-runtime, warlock-protocol\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0\n', 'test-suite ui-engine-broker-controls': 'test-suite ui-engine-broker-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-ui-engine-broker\n  main-is: Main.hs\n  build-depends: base >=4.18 && <5, bytestring, text, unix, network ==3.2.0.0, warlock-runtime, warlock-protocol, warlock-process-custody\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0\n\n-- Ordinary-linked optional notification startup data controls.'}

BACKING_TARGETS = BRIDGE_TARGETS + (('filter-backing-root-controls', 'warlock-runtime:test:filter-backing-root-controls'),)
BACKING_BEHAVIOR_SUITES = BRIDGE_BEHAVIOR_SUITES + ('filter-backing-root-controls',)
BACKING_SOURCE_HASHES = {'ui/Warlock/Ui/FilterBackingRoot.hsc': 'bbc92b60813532408c686f20e694f544d5c801a8ba75e5a3dd6821826d7f1ca4', 'test-filter-backing-root/Main.hs': '1be7797f62e9db90b0056c1531ca61155080d6deadd10a345936a10b9dd8ddbd'}
BACKING_COMPONENT_STANZA = 'test-suite filter-backing-root-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-filter-backing-root, ui\n  main-is: Main.hs\n  other-modules: Warlock.Ui.FilterBackingRoot, Warlock.Ui.EngineCustody\n  build-depends: base >=4.18 && <5, bytestring, text, unix, directory, filepath, process ==1.6.19.0, warlock-runtime, warlock-protocol, warlock-process-custody, network ==3.2.0.0, cryptohash-sha256 ==0.11.102.1\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0\n'

JOURNEY_TARGETS = BACKING_TARGETS + (('ux003-native-observer', 'warlock-runtime:exe:ux003-native-observer'),
    ('application-owner-route-controls', 'warlock-runtime:test:application-owner-route-controls'))
JOURNEY_SOURCE_HASHES = {'fixture-ux003-native-observer/Main.hs': 'd3d76201c5b49062cd15cef26c3d9bf9a3f217ed00930c455facd1462fe2c652', 'src/Warlock/Backend.hs': 'aa6f6dd5306350328a846b812916aaaa0e2a061c566025b9462add873af7874a', 'test-application-owner-route/Main.hs': '55588e0366247dd44ec3ac886bf4207189a84203e06ae984a79de2ff346a9e90'}
JOURNEY_COMPONENT_STANZAS = {'executable ux003-native-observer': 'executable ux003-native-observer\n  hs-source-dirs: fixture-ux003-native-observer\n  main-is: Main.hs\n  build-depends: base >=4.18 && <5, bytestring, text, warlock-runtime, warlock-protocol, warlock-process-custody\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -threaded\n', 'test-suite application-owner-route-controls': 'test-suite application-owner-route-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-application-owner-route\n  main-is: Main.hs\n  build-depends: base >=4.18 && <5, bytestring, text, directory, filepath, unix, cryptohash-sha256 ==0.11.102.1, warlock-runtime, warlock-process-custody, warlock-protocol\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0\n\n-- Preparation-only fixed native metadata observation. Never a GUI/provider grant.'}


def _plain_file(runtime, relative):
    file = runtime / relative
    cursor = file
    while cursor != runtime:
        if cursor.is_symlink():
            raise RuntimeError('Physical build source contains a symlink')
        cursor = cursor.parent
    if runtime.is_symlink() or not file.is_file():
        raise RuntimeError('Physical build source is missing or not a regular file')
    return file


def validate_runtime(runtime):
    runtime = Path(runtime)
    if (not isinstance(CABAL_SHA256, str) or re.fullmatch('[0-9a-f]{64}', CABAL_SHA256) is None
            or set(SOURCE_HASHES) != {'ui/Warlock/Ui/DefaultContextOwner.hs',
                                     'ui/Warlock/Ui/CallbackRetirement.hs',
                                     'ui/Warlock/Ui/ProcessSignalOwner.hs',
                                     'test-ui-webkit/Main.hs',
                                     'ui/Warlock/Ui/WebKit.hs', 'ui/Warlock/Ui/Mvp.hsc',
                                     'test-default-context-owner/Main.hs'}
            or set(COMPONENT_STANZAS) != {'executable warlock-ui-owner',
                                         'test-suite ui-webkit-controls',
                                         'test-suite physical-context-owner-controls',
                                         'test-suite physical-context-owner-threaded-controls'}):
        raise RuntimeError('Physical build source bindings are incomplete')
    metadata = _plain_file(runtime, 'runtime.cabal')
    if digest(metadata) != CABAL_SHA256:
        raise RuntimeError('Fixed physical-context Cabal postimage differs')
    text = metadata.read_text()
    for heading, expected in COMPONENT_STANZAS.items():
        pieces = text.split(heading + '\n')
        if len(pieces) != 2:
            raise RuntimeError('Physical build component absent or repeated: ' + heading)
        actual = heading + '\n' + re.split(r'\n(?:test-suite|executable|library|common|flag)\b',
                                           pieces[1], maxsplit=1)[0]
        if actual.rstrip('\n') != expected.rstrip('\n'):
            raise RuntimeError('Fixed physical-context component fields differ: ' + heading)
    for relative, expected in SOURCE_HASHES.items():
        if re.fullmatch('[0-9a-f]{64}', expected) is None:
            raise RuntimeError('Invalid physical-context source binding')
        if digest(_plain_file(runtime, relative)) != expected:
            raise RuntimeError('Fixed physical-context source differs: ' + relative)
    directory = runtime / 'test-default-context-owner'
    entries = list(directory.rglob('*'))
    if (directory.is_symlink() or any(file.is_symlink() or not file.is_file() for file in entries)
            or {str(file.relative_to(directory)) for file in entries} != {'Main.hs'}):
        raise RuntimeError('Unexpected physical-context fixture or home module')


def command_plan(packet, output, stage):
    # Reuse the existing reviewed offline compiler/package-tool flags exactly.
    # Only the finite target tails and retained-log labels differ.
    original = callback_command_plan(packet, output, stage)
    build = original[0][1][:-2] + [target for _, target in TARGETS]
    listing = original[1][1][:-1]
    return [('physical-context-owner-build', build),
            *[('list-' + name, listing + [target]) for name, target in TARGETS]]


def validate_bridge_runtime(runtime):
    runtime = Path(runtime)
    validate_runtime(runtime)
    if set(BRIDGE_SOURCE_HASHES) != {'src/Warlock/Ui/EngineBroker.hs', 'ui/Warlock/Ui/EngineEntrypoint.hs', 'src/Warlock/Ui/EngineProtocol.hs', 'test-ui-engine-broker/Main.hs', 'test-ui-engine-protocol/Main.hs', 'src/Warlock/Ui/EngineAdapter.hs', 'test-ui-engine-protocol/DesktopIdleControls.hs', 'ui/Main.hs', 'test-ui-engine-protocol/ProtocolBoundary.hs', 'ui/Warlock/Ui/EngineCustody.hsc'}:
        raise RuntimeError('Bridge source bindings incomplete')
    for relative, expected in BRIDGE_SOURCE_HASHES.items():
        if (not isinstance(expected, str) or re.fullmatch('[0-9a-f]{64}', expected) is None
                or digest(_plain_file(runtime, relative)) != expected):
            raise RuntimeError('Fixed GUI bridge source differs: ' + relative)
    metadata = (runtime / 'runtime.cabal').read_text()
    for heading, expected in BRIDGE_COMPONENT_STANZAS.items():
        pieces = metadata.split(heading + '\n')
        if len(pieces) != 2:
            raise RuntimeError('Bridge component absent or repeated')
        actual = heading + '\n' + re.split(r'\n(?:test-suite|executable|library|common|flag)\b',
                                            pieces[1], maxsplit=1)[0]
        if actual.rstrip('\n') != expected.rstrip('\n'):
            raise RuntimeError('Bridge ordinary component differs')
    for directory, expected in {
            'test-ui-engine-protocol': {'Main.hs', 'ProtocolBoundary.hs', 'DesktopIdleControls.hs'},
            'test-ui-engine-broker': {'Main.hs'}}.items():
        base = runtime / directory
        entries = list(base.rglob('*'))
        if (base.is_symlink() or any(p.is_symlink() or not p.is_file() for p in entries)
                or {str(p.relative_to(base)) for p in entries} != expected):
            raise RuntimeError('Unexpected bridge fixture/home module')


def bridge_command_plan(packet, output, stage):
    original = command_plan(packet, output, stage)
    build = original[0][1][:-4] + [target for _, target in BRIDGE_TARGETS]
    listing = original[1][1][:-1]
    return [('physical-context-owner-bridge-build', build),
            *[('list-' + name, listing + [target]) for name, target in BRIDGE_TARGETS]]



def validate_backing_runtime(runtime):
    validate_bridge_runtime(runtime)
    runtime = Path(runtime)
    if set(BACKING_SOURCE_HASHES) != {'ui/Warlock/Ui/FilterBackingRoot.hsc', 'test-filter-backing-root/Main.hs'}:
        raise RuntimeError('Backing source bindings incomplete')
    for name, expected in BACKING_SOURCE_HASHES.items():
        if (not isinstance(expected, str) or re.fullmatch('[0-9a-f]{64}', expected) is None
                or digest(_plain_file(runtime, name)) != expected):
            raise RuntimeError('Fixed backing source differs: ' + name)
    text = (runtime / 'runtime.cabal').read_text()
    heading = 'test-suite filter-backing-root-controls'
    pieces = text.split(heading + '\n')
    if len(pieces) != 2:
        raise RuntimeError('Backing fixture stanza absent or repeated')
    actual = heading + '\n' + re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
    if actual.rstrip('\n') != BACKING_COMPONENT_STANZA.rstrip('\n'):
        raise RuntimeError('Backing ordinary fixture fields differ')
    directory = runtime / 'test-filter-backing-root'
    entries = list(directory.rglob('*'))
    if (directory.is_symlink() or any(p.is_symlink() or not p.is_file() for p in entries)
            or {str(p.relative_to(directory)) for p in entries} != {'Main.hs'}):
        raise RuntimeError('Unexpected backing fixture/home module')


def backing_command_plan(packet, output, stage):
    original = bridge_command_plan(packet, output, stage)
    build = original[0][1][:-6] + [target for _, target in BACKING_TARGETS]
    listing = original[1][1][:-1]
    return [('physical-context-owner-backing-build', build),
            *[('list-' + name, listing + [target]) for name, target in BACKING_TARGETS]]


def validate_journey_runtime(runtime):
    validate_backing_runtime(runtime)
    runtime = Path(runtime)
    if set(JOURNEY_SOURCE_HASHES) != {'fixture-ux003-native-observer/Main.hs', 'src/Warlock/Backend.hs',
                                      'test-application-owner-route/Main.hs'}:
        raise RuntimeError('Journey compile source bindings incomplete')
    for name, expected in JOURNEY_SOURCE_HASHES.items():
        if (not isinstance(expected, str) or re.fullmatch('[0-9a-f]{64}', expected) is None
                or digest(_plain_file(runtime, name)) != expected):
            raise RuntimeError('Fixed journey compile source differs: ' + name)
    text = (runtime / 'runtime.cabal').read_text()
    for heading, expected in JOURNEY_COMPONENT_STANZAS.items():
        pieces = text.split(heading + '\n')
        if len(pieces) != 2:
            raise RuntimeError('Journey ordinary component absent or repeated')
        actual = heading + '\n' + re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
        if actual.rstrip('\n') != expected.rstrip('\n'):
            raise RuntimeError('Journey ordinary component differs')
    for name in ('fixture-ux003-native-observer', 'test-application-owner-route'):
        directory = runtime / name
        entries = list(directory.rglob('*'))
        if (directory.is_symlink() or any(p.is_symlink() or not p.is_file() for p in entries)
                or {str(p.relative_to(directory)) for p in entries} != {'Main.hs'}):
            raise RuntimeError('Unexpected journey fixture/home module')


def journey_command_plan(packet, output, stage):
    original = backing_command_plan(packet, output, stage)
    build = original[0][1][:-7] + [target for _, target in JOURNEY_TARGETS]
    listing = original[1][1][:-1]
    return [('ux003-journey-build', build),
            *[('list-' + name, listing + [target]) for name, target in JOURNEY_TARGETS]]


def run_profile(root, output, packet, run, *, bridge=False, backing=False, journey=False, execute=None):
    """Called only by the reviewed protected ARM mode; run retains command receipts."""
    if journey and not backing:
        raise RuntimeError('Journey compile profile requires the fixed backing mode')
    if backing and not bridge:
        raise RuntimeError('Backing behavior requires the fixed bridge mode')
    if bridge and not callable(execute):
        raise RuntimeError('Bridge behavior requires the fixed protected callback')
    root, output = Path(root), Path(output)
    validate = validate_journey_runtime if journey else (validate_backing_runtime if backing else (validate_bridge_runtime if bridge else validate_runtime))
    source = root / 'implementation/warlock/haskell'
    validate(source / 'runtime')
    before = inventory(source)
    stage = output / 'haskell'
    shutil.copytree(source, stage, ignore=shutil.ignore_patterns('dist-newstyle', '__pycache__'))
    if inventory(stage) != before:
        raise RuntimeError('Physical-context Haskell staging differs')
    validate(stage / 'runtime')
    dependencies = output / 'dependencies'
    shutil.copytree(Path(packet['dependencies']), dependencies)
    if inventory(dependencies) != packet['trees'][packet['dependencies']]:
        raise RuntimeError('Physical-context dependency staging differs')
    manifest = json.loads((root / 'tools/haskell-dependencies.json').read_text())
    for dependency in manifest['packages']:
        metadata = dependencies / dependency['directory'] / (dependency['name'] + '.cabal')
        if digest(metadata) != dependency['metadataSHA256']:
            raise RuntimeError('Exact Haskell dependency metadata revision differs')
    project = stage / 'cabal.project'
    original_project = project.read_text()
    suffix = '\npackages: ' + ' '.join(str(dependencies / p['directory']) for p in manifest['packages']) + '\nactive-repositories: :none\n'
    project.write_text(original_project + suffix)
    config = output / 'cabal.config'
    config.write_text('active-repositories: :none\nstore-dir: ' + str(output / 'store') + '\nremote-repo-cache: ' + str(output / 'repo-cache') + '\n')
    plan = (journey_command_plan if journey else (backing_command_plan if backing else (bridge_command_plan if bridge else command_plan)))(packet, output, stage)
    targets = JOURNEY_TARGETS if journey else (BACKING_TARGETS if backing else (BRIDGE_TARGETS if bridge else TARGETS))
    run(*plan[0], stage)
    binaries = {}
    for (name, _), (label, argv) in zip(targets, plan[1:], strict=True):
        lines = run(label, argv, stage).splitlines()
        if len(lines) != 1:
            raise RuntimeError('Unexpected physical-context list-bin output')
        binaries[name] = pin_image(Path(lines[0]), output / 'dist', name)
    for name, pin in binaries.items():
        if pin_image(Path(pin['path']), output / 'dist', name) != pin:
            raise RuntimeError('Physical-context compiled image changed')
    behavior = {}
    if bridge:
        for name in (BACKING_BEHAVIOR_SUITES if backing else BRIDGE_BEHAVIOR_SUITES):
            pin = binaries[name]
            if pin_image(Path(pin['path']), output / 'dist', name) != pin:
                raise RuntimeError('Bridge image drift before behavior')
            behavior[name] = execute(name, pin, stage)
            if pin_image(Path(pin['path']), output / 'dist', name) != pin:
                raise RuntimeError('Bridge image drift after behavior')
    return {'scope': ('Nine fixed targets compiled; observer and application route are build/list only; only three existing CPU fixtures run' if journey
                      else 'Seven fixed targets compiled; only two codec/socket and one owned-filesystem fixture run' if backing
                      else 'Six fixed targets compiled; only two ordinary protocol/socket fixtures run' if bridge
                      else 'Four fixed targets compiled/linked only; no fixture Main invocation'),
            'targets': [target for _, target in targets], 'compiledImages': binaries,
            'haskellSourceTree': before,
            'originalProjectSHA256': hashlib.sha256(original_project.encode()).hexdigest(),
            'derivedProjectSHA256': digest(project),
            'projectAppendSHA256': hashlib.sha256(suffix.encode()).hexdigest(),
            'fixtureMainExecutions': len(behavior), 'cpuBehaviorReceipts': behavior, 'callbackExecutionObserved': False,
            'gtkExecutionObserved': False, 'physicalThreadOwnershipObserved': False,
            'nativeExecutionAcceptance': False, 'providerQualified': False,
            'inputQualified': False, 'cleanupQualified': False,
            'nativeAcceptance': False, 'originalAcceptance': False, 'releaseAccepted': False}

#!/usr/bin/env python3
"""Fixed two-target ARM compile/link support; never executes fixture Main."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import struct

from arm64_toolchain import digest, inventory

TARGETS = (
    ('webkit-callback-capi-controls', 'warlock-runtime:test:webkit-callback-capi-controls'),
    ('owned-signal-lifecycle-controls', 'warlock-runtime:test:owned-signal-lifecycle-controls'),
)
BASE_CABAL_SHA256 = 'f11bfb0e2bf6b5480ffe5759465dce5d06569d579b50c84691fbb3cd5574c695'
POST_CABAL_SHA256 = '9650b5504e22c09ac68dafb87fc0fd4443f18ebbfd3773ccdfd33b99257408a6'
ADDED_SUFFIX = '\ntest-suite webkit-callback-capi-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-webkit-callback-capi\n  main-is: Main.hs\n  build-depends: base >=4.18 && <5\n  pkgconfig-depends: gobject-2.0\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates\n\ntest-suite owned-signal-lifecycle-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-owned-signal, ui\n  main-is: Main.hs\n  other-modules: Warlock.Ui.WebKit, Warlock.Ui.WebKitABI, Warlock.Ui.EngineCustody, Warlock.Ui.Mvp\n  pkgconfig-depends: gobject-2.0\n  extra-libraries: webkitgtk-6.0, gtk-4, gobject-2.0, gio-2.0, glib-2.0, soup-3.0\n  build-depends: base >=4.18 && <5, bytestring, text, unix, directory, filepath, process ==1.6.19.0, warlock-runtime, warlock-protocol, warlock-process-custody, network ==3.2.0.0, cryptohash-sha256 ==0.11.102.1\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -threaded -with-rtsopts=-V0\n'
SUITE_STANZAS = {'webkit-callback-capi-controls': 'test-suite webkit-callback-capi-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-webkit-callback-capi\n  main-is: Main.hs\n  build-depends: base >=4.18 && <5\n  pkgconfig-depends: gobject-2.0\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates\n', 'owned-signal-lifecycle-controls': 'test-suite owned-signal-lifecycle-controls\n  type: exitcode-stdio-1.0\n  hs-source-dirs: test-owned-signal, ui\n  main-is: Main.hs\n  other-modules: Warlock.Ui.WebKit, Warlock.Ui.WebKitABI, Warlock.Ui.EngineCustody, Warlock.Ui.Mvp\n  pkgconfig-depends: gobject-2.0\n  extra-libraries: webkitgtk-6.0, gtk-4, gobject-2.0, gio-2.0, glib-2.0, soup-3.0\n  build-depends: base >=4.18 && <5, bytestring, text, unix, directory, filepath, process ==1.6.19.0, warlock-runtime, warlock-protocol, warlock-process-custody, network ==3.2.0.0, cryptohash-sha256 ==0.11.102.1\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -threaded -with-rtsopts=-V0\n'}
FIXTURE_HASHES = {'test-webkit-callback-capi': '2d5a72f20348a9961cc28e96d0ca6cc634e60050bddce072e92d4e830fcd4c42', 'test-owned-signal': '7269e40e32790f296a7d31d443b4881004fd1ace0c219b67530f335606a9f607'}


def validate_runtime(runtime):
    runtime = Path(runtime)
    metadata = runtime / 'runtime.cabal'
    if metadata.is_symlink() or not metadata.is_file() or digest(metadata) != POST_CABAL_SHA256:
        raise RuntimeError('Fixed callback Cabal postimage differs')
    text = metadata.read_text()
    if not text.endswith(ADDED_SUFFIX):
        raise RuntimeError('Expected exactly two callback suite appends')
    original = text[:-len(ADDED_SUFFIX)]
    if hashlib.sha256(original.encode()).hexdigest() != BASE_CABAL_SHA256:
        raise RuntimeError('Existing runtime metadata changed')
    for suite, expected in SUITE_STANZAS.items():
        pieces = text.split('test-suite ' + suite + '\n')
        if len(pieces) != 2:
            raise RuntimeError('Callback suite is absent or repeated: ' + suite)
        actual = 'test-suite ' + suite + '\n' + re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
        if actual.rstrip('\n') != expected.rstrip('\n'):
            raise RuntimeError('Fixed callback suite fields differ: ' + suite)
    for directory, expected_sha in FIXTURE_HASHES.items():
        root = runtime / directory
        if root.is_symlink() or not root.is_dir():
            raise RuntimeError('Callback fixture directory differs')
        entries = list(root.rglob('*'))
        if any(p.is_symlink() or not p.is_file() for p in entries) or {str(p.relative_to(root)) for p in entries} != {'Main.hs'}:
            raise RuntimeError('Unexpected callback fixture/home-module source')
        if digest(root / 'Main.hs') != expected_sha:
            raise RuntimeError('Fixed callback fixture source differs: ' + directory)


def command_plan(packet, output, stage):
    output, stage = Path(output), Path(stage)
    ghc = Path(packet['ghcPrefix']) / 'bin'
    common = [packet['cabal'], '--config-file=' + str(output / 'cabal.config')]
    flags = ['--offline', '--project-file=' + str(stage / 'cabal.project'),
             '--builddir=' + str(output / 'dist'), '--with-compiler=' + str(ghc / 'ghc'),
             '--with-hc-pkg=' + str(ghc / 'ghc-pkg'), '--with-hsc2hs=' + str(ghc / 'hsc2hs'),
             '--with-gcc=/usr/bin/gcc', '--with-ar=/usr/bin/ar', '--with-ld=/usr/bin/ld',
             '--with-pkg-config=/usr/bin/pkg-config', '--jobs=2']
    return [('provider-callback-build', common + ['build'] + flags + [target for _, target in TARGETS]),
            *[('list-' + name, common + ['list-bin'] + flags + [target]) for name, target in TARGETS]]


def pin_image(path, dist, expected_name):
    path, dist = Path(path), Path(dist)
    if (not path.is_absolute() or path.name != expected_name or path.is_symlink()
            or path.resolve() != path or not path.is_relative_to(dist.resolve())):
        raise RuntimeError('Unexpected callback compiled-image path')
    fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid()
                or before.st_mode & (stat.S_ISUID | stat.S_ISGID) or not before.st_mode & stat.S_IXUSR):
            raise RuntimeError('Unsafe callback compiled image')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            header = stream.read(64)
            stream.seek(0)
            result_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
        after = os.fstat(fd)
        fields = ('st_dev', 'st_ino', 'st_size', 'st_mode', 'st_uid', 'st_mtime_ns', 'st_ctime_ns')
        if any(getattr(before, key) != getattr(after, key) for key in fields):
            raise RuntimeError('Callback image changed while pinned')
    finally:
        os.close(fd)
    if (len(header) != 64 or header[:7] != b'\x7fELF\x02\x01\x01'
            or struct.unpack_from('<H', header, 16)[0] not in (2, 3)
            or struct.unpack_from('<H', header, 18)[0] != 183
            or struct.unpack_from('<I', header, 20)[0] != 1):
        raise RuntimeError('Callback image is not ELF64 little-endian AArch64')
    return {'path': str(path), 'device': str(before.st_dev), 'inode': str(before.st_ino),
            'size': str(before.st_size), 'sha256': result_sha, 'executed': False}


def run_profile(root, output, packet, run):
    """Only caller is the fixed reviewed private ARM mode; run is its retained-log command adapter."""
    root, output = Path(root), Path(output)
    source = root / 'implementation/warlock/haskell'
    validate_runtime(source / 'runtime')
    before = inventory(source)
    stage = output / 'haskell'
    shutil.copytree(source, stage, ignore=shutil.ignore_patterns('dist-newstyle', '__pycache__'))
    if inventory(stage) != before:
        raise RuntimeError('Callback Haskell staging differs')
    validate_runtime(stage / 'runtime')
    dependencies = output / 'dependencies'
    shutil.copytree(Path(packet['dependencies']), dependencies)
    if inventory(dependencies) != packet['trees'][packet['dependencies']]:
        raise RuntimeError('Callback dependency staging differs')
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
    plan = command_plan(packet, output, stage)
    run(*plan[0], stage)
    binaries = {}
    for (name, _), (label, argv) in zip(TARGETS, plan[1:], strict=True):
        lines = run(label, argv, stage).splitlines()
        if len(lines) != 1:
            raise RuntimeError('Unexpected callback list-bin output')
        binaries[name] = pin_image(Path(lines[0]), output / 'dist', name)
    for name, pin in binaries.items():
        if pin_image(Path(pin['path']), output / 'dist', name) != pin:
            raise RuntimeError('Callback compiled image changed')
    return {'scope': 'Two new fixed suite images compiled/linked only; no fixture Main invocation',
            'targets': [target for _, target in TARGETS], 'compiledImages': binaries,
            'haskellSourceTree': before, 'signalOrdinaryRuntimeLibraryDependency': True,
            'originalProjectSHA256': hashlib.sha256(original_project.encode()).hexdigest(),
            'derivedProjectSHA256': digest(project), 'projectAppendSHA256': hashlib.sha256(suffix.encode()).hexdigest(),
            'fixtureMainExecutions': 0, 'callbackExecutionObserved': False,
            'gtkExecutionObserved': False, 'nativeExecutionAcceptance': False,
            'providerQualified': False, 'inputQualified': False, 'cleanupQualified': False,
            'nativeAcceptance': False, 'originalAcceptance': False, 'releaseAccepted': False}

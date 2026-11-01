#!/usr/bin/env python3
"""Fixed, offline Haskell SDK preparation and Cabal checks; never native QA."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base

CACHE = Path('/home/charl/.cache/warlock-haskell')
MANIFEST = ROOT / 'tools/haskell-toolchain.json'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def regular(path):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('Expected regular input: ' + str(path))


def directory(path):
    if path.is_symlink() or not path.is_dir() or path.stat().st_uid != os.getuid() or path.resolve() != path:
        raise RuntimeError('Expected owned nonsymlink directory: ' + str(path))


def artifacts(packet):
    for artifact in packet['artifacts']:
        path = CACHE / 'downloads' / artifact['file']
        regular(path)
        if digest(path) != artifact['sha256']:
            raise RuntimeError('Pinned artifact differs: ' + artifact['file'])


def system_inputs():
    tools = {name: str(Path(shutil.which(name) or '/missing-' + name).resolve())
             for name in ('gcc', 'make', 'ld', 'ar', 'ranlib', 'as', 'strip', 'pkg-config', 'dpkg-deb', 'bwrap', 'sh')}
    tools['python'] = str(Path(sys.executable).resolve())
    tools.update({name: str((Path('/usr/lib/x86_64-linux-gnu') / name).resolve())
                  for name in ('libgmp.so.10', 'libffi.so.8', 'libglib-2.0.so.0')})
    return {name: {'path': path, 'sha256': digest(Path(path))} for name, path in tools.items()}


def command(argv, output, name, env, cwd, timeout=600):
    with (output / (name + '.stdout')).open('w') as stdout, (output / (name + '.stderr')).open('w') as stderr:
        child = subprocess.run(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr, timeout=timeout)
    print(json.dumps({'command': name, 'exit': child.returncode}), flush=True)
    if child.returncode:
        raise RuntimeError(name + ' failed; see retained stdout/stderr')


def extract(archive, target):
    with tarfile.open(archive) as contents:
        contents.extractall(target, filter='data')


def tree_hashes(directory):
    result = {}
    for path in sorted(directory.rglob('*')):
        key = str(path.relative_to(directory))
        if path.is_symlink():
            result[key] = {'symlink': os.readlink(path), 'resolvedSHA256': digest(path) if path.is_file() else None}
        elif path.is_file():
            result[key] = {'sha256': digest(path)}
    return result


def prepare(packet, output, env):
    sdk = CACHE / packet['sdkDirectory']
    if sdk.exists():
        directory(sdk)
        receipt = sdk / 'sdk.json'
        regular(receipt)
        old = json.loads(receipt.read_text())
        if old['manifestSHA256'] != digest(MANIFEST) or old['files'] != tree_hashes_without_receipt(sdk):
            raise RuntimeError('Existing SDK differs; preserve and reconcile it before preparation')
        return old
    sdk.mkdir()
    source = output / 'bindist'
    source.mkdir()
    sysroot = sdk / 'sysroot'
    sysroot.mkdir()
    for artifact in packet['artifacts']:
        archive = CACHE / 'downloads' / artifact['file']
        regular(archive)
        if digest(archive) != artifact['sha256']:
            raise RuntimeError('Pinned artifact changed before extraction: ' + artifact['file'])
        if artifact['role'] == 'sysroot':
            command(['/usr/bin/dpkg-deb', '-x', str(archive), str(sysroot)], output,
                    'unpack-' + artifact['file'], env, output)
        elif artifact['role'] == 'ghc':
            extract(archive, source)
        elif artifact['role'] == 'cabal':
            (sdk / 'bin').mkdir(exist_ok=True)
            extract(archive, sdk / 'bin')
        elif artifact['role'] == 'dependency':
            (sdk / 'sources').mkdir(exist_ok=True)
            extract(archive, sdk / 'sources')
    # Relocate development metadata only; the installed host DSOs stay unchanged.
    for pc in sysroot.rglob('*.pc'):
        pc.write_text(pc.read_text().replace('prefix=/usr\n', 'prefix=' + str(sysroot / 'usr') + '\n'))
    lib = sysroot / 'usr/lib/x86_64-linux-gnu'
    for name, soname in (('gmp', 'libgmp.so.10'), ('ffi', 'libffi.so.8'), ('glib-2.0', 'libglib-2.0.so.0')):
        link = lib / ('lib' + name + '.so')
        if link.is_symlink():
            link.unlink()
        selected = Path('/usr/lib/x86_64-linux-gnu') / soname
        if not selected.is_file():
            raise RuntimeError('Missing installed system DSO: ' + name)
        link.symlink_to(selected.resolve())
    bindist = source / packet['ghcArchiveRoot']
    includes = sysroot / 'usr/include/x86_64-linux-gnu'
    command([str(bindist / 'configure'), '--prefix=' + str(sdk),
             '--with-gmp-includes=' + str(includes), '--with-gmp-libraries=' + str(lib)],
            output, 'configure-ghc', env, bindist)
    command(['/usr/bin/make', 'install'], output, 'install-ghc', env, bindist)
    command([str(sdk / 'bin/ghc'), '--numeric-version'], output, 'ghc-version', env, output)
    command([str(sdk / 'bin/cabal'), '--numeric-version'], output, 'cabal-version', env, output)
    if (output / 'ghc-version.stdout').read_text().strip() != packet['ghc']:
        raise RuntimeError('Compiler version differs')
    if (output / 'cabal-version.stdout').read_text().strip() != packet['cabal']:
        raise RuntimeError('Cabal version differs')
    result = {'manifestSHA256': digest(MANIFEST), 'files': tree_hashes_without_receipt(sdk)}
    (sdk / 'sdk.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def tree_hashes_without_receipt(sdk):
    return {key: value for key, value in tree_hashes(sdk).items() if key != 'sdk.json'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--build', action='store_true')
    modes.add_argument('--ui-origin', action='store_true')
    modes.add_argument('--ui-models', action='store_true')
    modes.add_argument('--site', action='store_true')
    parser.add_argument('--inside-private', type=Path)
    args = parser.parse_args()
    scope = require_qa_scope()
    if args.inside_private is None:
        runtime_base()
    packet = json.loads(MANIFEST.read_text())
    if args.inside_private is None:
        output = ROOT / '.warlock-contributor' / ('haskell-cpu-' + str(time.time_ns()))
        output.mkdir(mode=0o700)
        CACHE.mkdir(parents=True, exist_ok=True)
        for cache_directory in (CACHE, CACHE / 'downloads'):
            directory(cache_directory)
        artifacts(packet)
        private = ['/usr/bin/bwrap', '--die-with-parent', '--unshare-net', '--unshare-pid',
                   '--ro-bind', '/', '/', '--proc', '/proc', '--dev', '/dev',
                   # Keep the display fixture's entire runtime ancestry private;
                   # the outer qa_cpu process retains the host lock independently.
                   '--tmpfs', '/tmp', '--tmpfs', '/run', '--dir', '/run/user',
                   '--tmpfs', '/home', '--ro-bind', '/home/charl', '/home/charl',
                   '--dir', '/home/charles', '--ro-bind', str(ROOT), '/home/charles/Warlock',
                   '--bind' if args.prepare else '--ro-bind', str(CACHE), str(CACHE), '--bind', str(output), str(output),
                   '--chdir', str(ROOT), '--', sys.executable, '-B', str(Path(__file__).resolve()),
                   '--inside-private', str(output)] + (['--prepare'] if args.prepare else (['--ui-origin'] if args.ui_origin else (['--ui-models'] if args.ui_models else (['--site'] if args.site else ['--build']))))
        report = {'schema': 1, 'protectedScope': scope, 'passed': False, 'prepare': args.prepare,
                  'nativeAccepted': False, 'releaseAccepted': False,
                  'parentNetworkNamespace': os.readlink('/proc/self/ns/net'),
                  'manifestSHA256': digest(MANIFEST), 'commands': []}
        report['scope'] = 'Offline SDK bootstrap inventory only; not backend build/test, native provider, or original EARS acceptance'
        report['systemInputs'] = system_inputs()
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        from qa_cpu import haskell_inputs
        sources = {name: digest(ROOT / name) for name in sorted(haskell_inputs(ROOT, args.prepare, site=args.site))}
        report['sourceHashes'] = sources
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        result = subprocess.run(private, cwd=ROOT, timeout=3500)
        if (set(haskell_inputs(ROOT, args.prepare, site=args.site)) != set(sources)
                or any(not (ROOT / name).is_file() or (ROOT / name).is_symlink()
                       or digest(ROOT / name) != sha for name, sha in sources.items())):
            report = json.loads((output / 'report.json').read_text())
            report.update(passed=False, error='Reviewed source changed during execution')
            (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            return 1
        print(json.dumps({'exit': result.returncode, 'report': str(output / 'report.json')}), flush=True)
        return result.returncode
    output = args.inside_private
    if output.parent != ROOT / '.warlock-contributor' or not re.fullmatch(r'haskell-cpu-[0-9]+', output.name):
        raise RuntimeError('Unexpected private output path')
    directory(output)
    directory(CACHE)
    directory(CACHE / 'downloads')
    report_path = output / 'report.json'
    report = json.loads(report_path.read_text())
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
           'PYTHONDONTWRITEBYTECODE': '1', 'GHC_ENVIRONMENT': '-',
           'TMPDIR': '/tmp', 'CABAL_DIR': str(output / 'cabal-home')}
    try:
        artifacts(packet)
        if system_inputs() != report['systemInputs']:
            raise RuntimeError('System inputs changed before preparation')
        network = os.readlink('/proc/self/ns/net')
        report['networkNamespace'] = network
        interfaces = {line.split(':', 1)[0].strip() for line in Path('/proc/net/dev').read_text().splitlines() if ':' in line}
        if network == report['parentNetworkNamespace'] or interfaces != {'lo'}:
            raise RuntimeError('Expected a private network with loopback only')
        if args.prepare:
            receipt = prepare(packet, output, env)
            report['sdkReceiptSHA256'] = digest(CACHE / packet['sdkDirectory'] / 'sdk.json')
            report['sdkFiles'] = len(receipt['files'])
        else:
            sdk = CACHE / packet['sdkDirectory']
            directory(sdk)
            receipt = sdk / 'sdk.json'
            regular(receipt)
            saved = json.loads(receipt.read_text())
            if saved['manifestSHA256'] != digest(MANIFEST) or saved['files'] != tree_hashes_without_receipt(sdk):
                raise RuntimeError('Installed SDK inventory differs before build')
            from haskell_build import build
            report['scope'] = ('Offline site Elm compilation only; no runtime or original acceptance' if args.site else
                               'UI model-only component feedback; compilation and runtime tests omitted; no original acceptance' if args.ui_models else
                               'Actual offline Haskell package build and controlled component tests; no native GUI/provider or original scenario acceptance')
            report['build'] = build(sdk, output, env, profile='site' if args.site else ('ui-models' if args.ui_models else ('ui-origin' if args.ui_origin else 'common')))
            if not report['build']['passed']:
                raise RuntimeError(report['build'].get('error', 'Haskell component tests failed; see retained suite reports'))
            if saved['files'] != tree_hashes_without_receipt(sdk):
                raise RuntimeError('Installed SDK inventory changed during build')
        artifacts(packet)
        if system_inputs() != report['systemInputs']:
            raise RuntimeError('System inputs changed during preparation')
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
    finally:
        report_path.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'passed': report['passed'], 'error': report.get('error')}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

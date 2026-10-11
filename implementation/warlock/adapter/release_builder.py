#!/usr/bin/env python3
"""Hash-pinned local release inputs and a fixed Elm/native-host build recipe.

ELM-DEL-003. This builder retains the separately qualified core/plugin artifacts;
it does not infer native acceptance, compiler-source provenance or redistribution
permission from hashes. Build commands must use the protected QA launcher.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tarfile

PACKAGES = ('gtk+-3.0', 'webkit2gtk-4.1', 'gtk-layer-shell-0',
            'json-glib-1.0', 'gio-unix-2.0')
UNITS = ('preview_uri.cpp', 'preview_icons.cpp', 'preview-uri-webkit.cpp',
         'preview-provider-bootstrap.cpp', 'client-producer.cpp',
         'imported-clients.cpp', 'preview-uri-router.cpp',
         'elm-preview-policy.cpp', 'preview-visual-channel.cpp', 'preview-policy-driver.cpp')
TOOLS = ('cc', 'g++', 'pkg-config', 'node', 'python3', 'quint', 'as', 'ld', 'ar', 'ldd', 'bash', 'env', 'bwrap')
ENV_KEYS = ('PATH', 'LD_LIBRARY_PATH', 'LD_PRELOAD', 'CPATH', 'C_INCLUDE_PATH',
            'CPLUS_INCLUDE_PATH', 'LIBRARY_PATH', 'COMPILER_PATH',
            'GCC_EXEC_PREFIX', 'PKG_CONFIG_PATH', 'PKG_CONFIG_LIBDIR',
            'LANG', 'LC_ALL', 'LC_CTYPE', 'TZ')


def require_scope():
    sys.path.insert(0, '/home/hoskinson/window-integration-qa')
    from qa_launch import require_qa_scope
    return require_qa_scope()


class ChangedInput(RuntimeError):
    pass


def sha(path):
    with Path(path).open('rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ChangedInput('Input is not a regular file: ' + str(path))
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ChangedInput('Duplicate manifest key: ' + key)
        result[key] = value
    return result


def read(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def run(argv, cwd=None, env=None):
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=240)
    if result.returncode:
        raise ChangedInput('Command failed: ' + repr(argv) + '\n' + result.stdout + result.stderr)
    return result.stdout


def native_dependencies(candidate, tools, flags, spellings=False):
    result = set()
    for source, compiler, standard in [('shared-host.c', 'cc', 'c11')] + [
            (name, 'g++', 'c++20') for name in UNITS]:
        body = run([tools[compiler]['path'], '-std=' + standard, '-M', '-MT',
                    'locked-object', 'native/' + source, *flags], cwd=candidate)
        dependencies = shlex.split(body.replace('\\\n', ' ').split(':', 1)[1])
        for name in dependencies:
            path = candidate / name if not Path(name).is_absolute() else Path(name)
            result.add(str(path.absolute() if spellings else path.resolve()))
    return sorted(result)


def path_links(paths):
    """Retain directory/leaf link chains needed to resolve locked file names."""
    links = {}
    checked = set()
    def inspect(path):
        for prefix in reversed([path, *path.parents]):
            key = str(prefix)
            if key in checked:
                continue
            checked.add(key)
            if prefix.is_symlink():
                target = os.readlink(prefix)
                location = str(prefix.parent.resolve() / prefix.name)
                links[location] = target
                inspect(Path(target) if Path(target).is_absolute() else prefix.parent / target)
    for name in paths:
        inspect(Path(name))
    return dict(sorted(links.items()))


def add(files, path, role, expected=None):
    path = Path(path).absolute()
    actual = sha(path)
    if expected is not None and actual != expected:
        raise ChangedInput('Recorded artifact changed: ' + str(path))
    name = str(path)
    row = {'sha256': actual, 'resolved': str(path.resolve()),
           'size': path.stat().st_size, 'roles': [role]}
    if name in files:
        if files[name]['sha256'] != actual:
            raise ChangedInput('Input changed during capture: ' + name)
        row['roles'] = sorted(set(files[name]['roles']) | {role})
    files[name] = row


def add_dynamic(files, path):
    # ldd can print a canonical /usr/lib64 loader path even when PT_INTERP
    # actually requests /lib64. Retain the executable's real lookup spelling.
    with Path(path).open('rb') as stream:
        header = stream.read(64)
        if header[:4] == b'\x7fELF':
            if header[4:6] != b'\x02\x01':
                raise ChangedInput('Unsupported ELF class/encoding: ' + str(path))
            offset = int.from_bytes(header[32:40], 'little')
            size = int.from_bytes(header[54:56], 'little')
            count = int.from_bytes(header[56:58], 'little')
            for index in range(count):
                stream.seek(offset + index * size)
                program = stream.read(size)
                if int.from_bytes(program[:4], 'little') == 3:  # PT_INTERP
                    stream.seek(int.from_bytes(program[8:16], 'little'))
                    loader = stream.read(int.from_bytes(program[32:40], 'little'))
                    add(files, loader.rstrip(b'\0').decode(), 'elf-interpreter')
    result = subprocess.run(['/usr/bin/ldd', str(path)], text=True, capture_output=True)
    if result.returncode and ('not a dynamic executable' in result.stderr + result.stdout
                              or 'statically linked' in result.stdout):
        return
    if result.returncode or 'not found' in result.stdout:
        raise ChangedInput('Unresolved dynamic dependency: ' + str(path))
    for name in re.findall(r'(?:=>\s+|^\s*)(/\S+)\s+\(', result.stdout, re.MULTILINE):
        add(files, name, 'dynamic-library')


def capture(repo):
    require_scope()
    # Exercise CLI initialization before collecting Python's lazy dependencies;
    # QA may call capture() directly while an isolated build enters main().
    argparse.ArgumentParser(description=__doc__).parse_args([])
    repo = Path(repo).resolve()
    candidate = repo / 'implementation/warlock'
    held = repo / 'implementation/warlock-preview-provider-v143'
    files = {}
    sources = []
    for folder in ('src', 'native', 'adapter', 'assets', 'qa'):
        iterator = (candidate / folder).rglob('*') if folder != 'qa' else (candidate / folder).iterdir()
        for path in sorted(iterator):
            if path.is_file() and '__pycache__' not in path.parts:
                add(files, path, 'candidate-source')
                sources.append(str(path.relative_to(candidate)))
    add(files, candidate / 'elm.json', 'candidate-source')
    sources.append('elm.json')
    toolchain_path = held / 'qa/toolchain.json'
    toolchain = read(toolchain_path)
    add(files, toolchain_path, 'elm-toolchain-manifest')
    for name, row in toolchain['heldFiles'].items():
        add(files, held / name, 'elm-package-or-compiler', row['sha256'])
    compiler = held / toolchain['compiler']
    if sha(compiler) != toolchain['compilerSHA256']:
        raise ChangedInput('Elm compiler changed')
    tools = {}
    for name in TOOLS:
        executable = shutil.which(name)
        if executable is None:
            raise ChangedInput('Missing build/test tool: ' + name)
        add(files, executable, 'build-or-test-tool')
        tools[name] = {'path': str(Path(executable).absolute()), 'version': None}
    for name in ('cc', 'g++', 'pkg-config', 'node', 'python3', 'quint', 'as', 'ld', 'ar', 'bwrap'):
        tools[name]['version'] = run([tools[name]['path'], '--version']).strip()
    tools['elm'] = {'path': str(compiler), 'version': run([str(compiler), '--version']).strip()}
    # Pin the installed Quint distribution and its Node dependencies, not only its
    # small shebang entry. The build's decisive replay uses the pinned Node tool.
    quint_modules = Path(tools['quint']['path']).parent.parent
    for path in sorted(quint_modules.rglob('*')):
        if path.is_file() and not path.is_symlink():
            add(files, path, 'quint-distribution')
    for name in ('cc1', 'cc1plus', 'collect2', 'as', 'ld'):
        path = run([tools['g++']['path'], '-print-prog-name=' + name]).strip()
        executable = path if Path(path).is_absolute() else shutil.which(path)
        if executable is None:
            raise ChangedInput('Unresolved compiler helper: ' + name)
        add(files, executable, 'compiler-helper')
        add_dynamic(files, executable)
    flags = shlex.split(run([tools['pkg-config']['path'], '--cflags', '--libs', *PACKAGES]))
    pkg_versions = {name: run([tools['pkg-config']['path'], '--modversion', name]).strip()
                    for name in PACKAGES}
    for folder in ('/usr/lib/pkgconfig', '/usr/share/pkgconfig', '/usr/local/lib/pkgconfig'):
        for path in sorted(Path(folder).glob('*.pc')):
            add(files, path, 'pkg-config-source')
    dependencies = native_dependencies(candidate, tools, flags)
    for path in dependencies:
        add(files, path, 'host-compile-dependency')
    for path in native_dependencies(candidate, tools, flags, spellings=True):
        add(files, path, 'host-header-path-spelling')
    for name in ('crtbeginS.o', 'crtendS.o', 'libgcc.a', 'libgcc_s.so',
                 'libstdc++.so', 'libatomic.so', 'libc.so', 'libm.so', 'liblto_plugin.so',
                 'Scrt1.o', 'crti.o', 'crtn.o'):
        path = run([tools['g++']['path'], '-print-file-name=' + name]).strip()
        if not Path(path).is_absolute():
            raise ChangedInput('Unresolved link input: ' + name)
        add(files, path, 'host-link-input')
        if name == 'libatomic.so':
            add_dynamic(files, path)
    pair_path = candidate / 'qa/current-native-pair.json'
    pair_meta = read(pair_path)
    add(files, pair_path, 'native-pair-manifest')
    reports = [pair_meta['authorityReport'], pair_meta['sceneCoreReport']['report'],
               pair_meta['outputTransportReport']['report']]
    report_hashes = [pair_meta['authorityReportSHA256'], pair_meta['sceneCoreReport']['reportSHA256'],
                     pair_meta['outputTransportReport']['reportSHA256']]
    loader_aliases = {}
    for name, expected in zip(reports, report_hashes):
        path = repo / name
        add(files, path, 'native-build-provenance', expected)
        report = read(path)
        if not report['passed']:
            raise ChangedInput('Native input has a failed build: ' + name)
        for field in ('dependencies', 'linkDependencies', 'retainedObjects', 'linkLibraries'):
            for artifact, expected_hash in report.get(field, {}).items():
                add(files, artifact, 'native-source-or-artifact', expected_hash)
        if 'loaderSymlink' in report:
            link = report['loaderSymlink']
            loader_aliases[Path(link['path']).name] = Path(pair_meta['pair']['aquamarine']['path']).name
    for row in pair_meta['pair'].values():
        add(files, row['path'], 'retained-native-pair', row['sha256'])
        add_dynamic(files, row['path'])
    for row in tools.values():
        add_dynamic(files, row['path'])
    # Explicit -l inputs resolve through the captured link dependency set; name
    # aliases are recorded as well so a changed linker script/symlink refuses.
    for flag in flags:
        if flag.startswith('-l'):
            name = 'lib' + flag[2:] + '.so'
            path = run([tools['g++']['path'], '-print-file-name=' + name]).strip()
            if not Path(path).is_absolute():
                raise ChangedInput('Unresolved host library: ' + name)
            add(files, path, 'host-link-library')
            add_dynamic(files, path)
    for module in list(sys.modules.values()):
        for attribute in ('__file__', '__cached__'):
            filename = getattr(module, attribute, None)
            if filename and Path(filename).is_file():
                add(files, filename, 'python-build-or-check-module')
    for path in (Path('/etc/ld.so.cache'), Path('/etc/ld.so.conf'),
                 Path('/usr/lib/locale/locale-archive'), Path('/usr/share/zoneinfo/UTC')):
        if path.is_file():
            add(files, path, 'build-runtime-data')
    for path in Path('/etc/ld.so.conf.d').glob('*.conf'):
        add(files, path, 'build-runtime-data')
    for path in (Path('/home/hoskinson/window-integration-qa/qa_launch.py'),
                 Path('/home/hoskinson/window-integration-qa/qa_run.py')):
        add(files, path, 'protected-launcher')
    return {'schema': 1, 'candidate': str(candidate), 'sources': sorted(sources),
            'tools': tools, 'elmHome': str(held / toolchain['elmHome']),
            'elmPackages': toolchain['elmDependencies'], 'nativePackages': pkg_versions,
            'flags': flags, 'hostDependencies': dependencies, 'nativePair': pair_meta['pair'],
            'loaderAliases': loader_aliases,
            'environment': {key: os.environ.get(key) for key in ENV_KEYS}, 'inputs': dict(sorted(files.items())),
            'symlinks': path_links(files),
            'scope': 'Fixed Elm assets/native host rebuild with retained exact core/plugin/Aquamarine artifacts.',
            'nativeAcceptance': False, 'fullReleaseAccepted': False,
            'missingObservations': ['Complete compiler/build-tool upstream source provenance and redistribution disposition.',
                'Two clean isolated offline builds and distributable comparison.',
                'Native acceptance of a newly compiled host and full main-session deployment.']}


def verify(manifest):
    require_scope()
    if manifest.get('schema') != 1 or not manifest.get('inputs'):
        raise ChangedInput('Unsupported or empty release input lock')
    if manifest['environment'] != {key: os.environ.get(key) for key in ENV_KEYS}:
        raise ChangedInput('Build search environment changed')
    for name, row in manifest['inputs'].items():
        if str(Path(name).resolve()) != row['resolved'] or sha(name) != row['sha256']:
            raise ChangedInput('Locked input changed: ' + name)
    for name, target in manifest.get('symlinks', {}).items():
        if not Path(name).is_symlink() or os.readlink(name) != target:
            raise ChangedInput('Locked filesystem link changed: ' + name)
    candidate = Path(manifest['candidate'])
    if native_dependencies(candidate, manifest['tools'], manifest['flags']) != manifest['hostDependencies']:
        raise ChangedInput('Native header resolution changed')
    return len(manifest['inputs'])


def build(manifest, output):
    count = verify(manifest)  # Fail before creating any build/output files.
    output = Path(output).absolute()
    output.mkdir(mode=0o700)
    workspace = output / 'workspace'; workspace.mkdir(mode=0o700)
    candidate = Path(manifest['candidate'])
    for name in manifest['sources']:
        target = workspace / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate / name, target)
        if sha(target) != manifest['inputs'][str(candidate / name)]['sha256']:
            raise ChangedInput('Source changed while copying: ' + name)
    elm_home = output / 'elm-home'
    for name, row in manifest['inputs'].items():
        if name.startswith(manifest['elmHome'] + '/'):
            target = elm_home / Path(name).relative_to(manifest['elmHome'])
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(name, target)
            if sha(target) != row['sha256']:
                raise ChangedInput('Elm package changed while copying: ' + name)
    env = {**os.environ, 'ELM_HOME': str(elm_home), 'SOURCE_DATE_EPOCH': '0', 'TZ': 'UTC'}
    tools = manifest['tools']; commands = []
    def execute(name, argv):
        result = subprocess.run(argv, cwd=workspace, env=env, text=True,
                                capture_output=True, timeout=240)
        (output / (name + '.stdout')).write_text(result.stdout)
        (output / (name + '.stderr')).write_text(result.stderr)
        commands.append({'name': name, 'argv': argv, 'exitCode': result.returncode})
        if result.returncode:
            raise ChangedInput('Build failed: ' + name + '\n' + result.stdout + result.stderr)
    for module, asset in [('Main', 'elm'), ('Bar', 'bar'), ('Popup', 'popup')]:
        execute('compile-' + module, [tools['elm']['path'], 'make', 'src/' + module + '.elm',
                                     '--optimize', '--output=assets/' + asset + '.js'])
    flags = manifest['flags']; objects = []
    for name, compiler, standard in [('shared-host.c', 'cc', 'c11')] + [(name, 'g++', 'c++20') for name in UNITS]:
        obj = output / (name + '.o'); objects.append(str(obj))
        execute('compile-' + name, [tools[compiler]['path'], '-std=' + standard, '-O2',
            '-Wall', '-Wextra', '-Werror', '-Wno-deprecated-declarations', '-MD',
            '-MF', str(output / (name + '.d')), '-c', 'native/' + name, '-o', str(obj), *flags])
    execute('link-host', [tools['g++']['path'], *objects, '-o', str(output / 'elm-host'), *flags])
    execute('host-self-test', [str(output / 'elm-host'), '--self-test'])
    # Keep a real typed reducer regression in the release build, using the same
    # pinned source/compiler/Node tuple rather than only syntax-checking assets.
    elm_info = read(workspace / 'elm.json'); elm_info['source-directories'] = ['src', 'qa']
    (workspace / 'elm.json').write_text(json.dumps(elm_info))
    execute('compile-NewInstanceReplay', [tools['elm']['path'], 'make', 'qa/NewInstanceReplay.elm',
        '--output=' + str(output / 'new-instance.js')])
    replay = (workspace / 'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay', 'Elm.NewInstanceReplay')
    (output / 'new-instance-replay.js').write_text(replay)
    execute('typed-NewInstanceReplay', [tools['node']['path'], str(output / 'new-instance-replay.js'),
        str(output / 'new-instance.js'), str(output / 'new-instance.json')])
    if not all(read(output / 'new-instance.json')['checks'].values()):
        raise ChangedInput('Compiled release reducer regression failed')
    verify(manifest)
    payload = output / 'package'; payload.mkdir()
    shutil.copytree(workspace / 'assets', payload / 'assets')
    shutil.copytree(workspace / 'adapter', payload / 'adapter')
    shutil.copyfile(output / 'elm-host', payload / 'elm-host')
    (payload / 'elm-host').chmod(0o755)
    (payload / 'native').mkdir()
    packaged_pair = {}
    for role, row in manifest['nativePair'].items():
        name = Path(row['path']).name
        target = payload / 'native' / name
        shutil.copyfile(row['path'], target)
        target.chmod(0o755 if role == 'core' else 0o644)
        packaged_pair[role] = {'path': 'native/' + name, 'sha256': row['sha256']}
        if sha(target) != row['sha256']:
            raise ChangedInput('Native pair changed during packaging: ' + role)
    for alias, target in manifest['loaderAliases'].items():
        (payload / 'native' / alias).symlink_to(target)
    input_identity = sorted((row['sha256'], row['size'], row['roles']) for row in manifest['inputs'].values())
    package_manifest = {'schema': 1, 'nativePair': packaged_pair,
        'inputContentSHA256': hashlib.sha256(json.dumps(input_identity, separators=(',', ':')).encode()).hexdigest(),
        'files': {str(p.relative_to(payload)): {'sha256': sha(p),
            'symlink': os.readlink(p) if p.is_symlink() else None}
            for p in sorted(payload.rglob('*')) if p.is_file()},
        'target': 'Arch Linux with Omarchy, x86_64', 'installable': False,
        'nativeAcceptance': False, 'fullReleaseAccepted': False}
    (payload / 'MANIFEST.json').write_text(json.dumps(package_manifest, indent=2) + '\n')
    # Deterministic transport: no build directory paths, clocks, UIDs or raw build
    # logs enter the archive. Provenance/input-location records remain alongside.
    archive = output / 'warlock-candidate.tar'
    with tarfile.open(archive, 'w', format=tarfile.PAX_FORMAT) as stream:
        for path in sorted(payload.rglob('*')):
            item = stream.gettarinfo(str(path), arcname='warlock/' + str(path.relative_to(payload)))
            item.mtime = 0; item.uid = 0; item.gid = 0; item.uname = ''; item.gname = ''
            item.mode = 0o755 if path.is_dir() or path.name in ('elm-host', 'Hyprland') else 0o644
            if item.isfile():
                with path.open('rb') as body:
                    stream.addfile(item, body)
            else:
                stream.addfile(item)
    report = {'passed': True, 'inputCount': count, 'commands': commands,
              'compiledAssets': {name: sha(payload / 'assets' / name) for name in ('elm.js', 'bar.js', 'popup.js')},
              'hostSHA256': sha(payload / 'elm-host'),
              'nativePair': manifest['nativePair'], 'typedChecks': read(output / 'new-instance.json')['checks'],
              'packageManifest': package_manifest, 'archiveSHA256': sha(archive),
              'payload': {str(p.relative_to(payload)): sha(p) for p in sorted(payload.rglob('*')) if p.is_file()},
              'installable': False, 'nativeAcceptance': False, 'fullReleaseAccepted': False,
              'missingObservations': manifest['missingObservations']}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    cap = sub.add_parser('capture'); cap.add_argument('--repo', required=True); cap.add_argument('--output', required=True)
    for name in ('verify', 'build'):
        item = sub.add_parser(name); item.add_argument('--lock', required=True); item.add_argument('--sha256', required=True)
        if name == 'build':
            item.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        if args.operation == 'capture':
            value = capture(args.repo)
            with Path(args.output).open('x') as stream:
                stream.write(json.dumps(value, indent=2) + '\n')
            print(json.dumps({'passed': True, 'inputs': len(value['inputs']), 'lockSHA256': sha(args.output)}))
        else:
            if sha(args.lock) != args.sha256:
                raise ChangedInput('Release lock identity changed')
            manifest = read(args.lock)
            if args.operation == 'verify':
                print(json.dumps({'passed': True, 'inputs': verify(manifest)}))
            else:
                result = build(manifest, args.output)
                print(json.dumps({'passed': result['passed'], 'report': str(Path(args.output) / 'report.json')}))
        return 0
    except (ChangedInput, OSError, ValueError) as error:
        print(json.dumps({'passed': False, 'error': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

"""Protected CPU build of the actual xdg-shell SHM subsurface client fixture."""
import hashlib
import json
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = Path('/usr/share/wayland-protocols/stable/xdg-shell/xdg-shell.xml')
DIALOG = Path('/usr/share/wayland-protocols/staging/xdg-dialog/xdg-dialog-v1.xml')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    sys.path.insert(0, '/home/hoskinson/window-integration-qa')
    from qa_launch import require_qa_scope
    qa_scope = require_qa_scope()
    out = ROOT / 'qa' / ('client-build-' + str(time.time_ns()))
    out.mkdir(mode=0o700)
    inputs = out / 'inputs'
    inputs.mkdir(mode=0o700)
    paths = [ROOT / 'native/child-client.c', Path(__file__).resolve(), PROTOCOL, DIALOG]
    hashes = {str(path): digest(path) for path in paths}
    for path in paths:
        target = inputs / path.name
        shutil.copy2(path, target)
        target.chmod(0o400)
    scanner = Path('/usr/bin/wayland-scanner').resolve()
    compiler = Path('/usr/bin/cc').resolve()
    report = {'passed': False, 'scope': 'real bounded Wayland/xdg-shell/subsurface client compile only; no server/GUI/native child claim',
              'qaScope': qa_scope, 'inputs': hashes, 'commands': [],
              'tools': {str(path): digest(path) for path in [scanner, compiler, Path('/usr/bin/pkg-config').resolve(),Path('/usr/bin/as').resolve(),Path('/usr/bin/ld').resolve(),Path('/usr/bin/ldd').resolve(),Path(subprocess.check_output([str(compiler),'-print-prog-name=cc1'],text=True).strip()).resolve()]}}
    generated = out / 'generated'
    generated.mkdir(mode=0o700)
    def run(name, command):
        result = subprocess.run(command, capture_output=True, text=True, cwd=out, timeout=60)
        (out / (name + '.stdout')).write_text(result.stdout)
        (out / (name + '.stderr')).write_text(result.stderr)
        report['commands'].append({'name': name, 'command': list(map(str, command)), 'exitCode': result.returncode})
        if result.returncode:
            raise RuntimeError(name + ' failed')
        return result.stdout
    try:
        run('scanner-version', [str(scanner), '--version'])
        run('compiler-version', [str(compiler), '--version'])
        run('client-header', [str(scanner), 'client-header', str(inputs / PROTOCOL.name), str(generated / 'xdg-shell-client.h')])
        run('protocol-code', [str(scanner), 'private-code', str(inputs / PROTOCOL.name), str(generated / 'xdg-shell-protocol.c')])
        run('dialog-header', [str(scanner), 'client-header', str(inputs / DIALOG.name), str(generated / 'xdg-dialog-client.h')])
        run('dialog-code', [str(scanner), 'private-code', str(inputs / DIALOG.name), str(generated / 'xdg-dialog-protocol.c')])
        flags = shlex.split(run('client-flags', ['/usr/bin/pkg-config', '--cflags', '--libs', 'wayland-client']))
        binary = out / 'child-client'
        run('client-build', [str(compiler), '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-Wl,-z,defs',
                            '-I' + str(generated), '-MD', '-MF', str(out / 'client.d'),
                            str(inputs / 'child-client.c'), str(generated / 'xdg-shell-protocol.c'), str(generated / 'xdg-dialog-protocol.c'), *flags, '-o', str(binary)])
        # Separate compile dependencies for both translation units; combined -MF
        # reports only the final unit on GCC, so obtain each exact dependency set.
        dependency_files = []
        for name, source in [('client', inputs / 'child-client.c'), ('protocol', generated / 'xdg-shell-protocol.c'), ('dialog', generated / 'xdg-dialog-protocol.c')]:
            target = out / (name + '-dependencies.d')
            run(name + '-dependencies', [str(compiler), '-std=c11', '-I' + str(generated), '-M', '-MF', str(target), str(source), *[flag for flag in flags if flag.startswith('-I')]])
            dependency_files.append(target)
        dependencies = set()
        for path in dependency_files:
            text = path.read_text().replace('\\\n', ' ')
            dependencies.update(text.split(':', 1)[1].split())
        report['dependencies'] = {str(Path(path).resolve()): digest(path) for path in sorted(dependencies)}
        linked = run('linked-libraries', ['/usr/bin/ldd', str(binary)])
        libraries = []
        for line in linked.splitlines():
            for word in line.split():
                if word.startswith('/') and Path(word).is_file():
                    libraries.append(Path(word).resolve())
        report['linkedLibraries'] = {str(path): digest(path) for path in sorted(set(libraries))}
        for path, expected in hashes.items():
            if digest(path) != expected:
                raise RuntimeError('Live fixture source changed during build: ' + path)
        report.update(client=str(binary), clientSHA256=digest(binary), generated={str(path.relative_to(out)): digest(path) for path in generated.iterdir()}, passed=True)
    except Exception as error:
        report['error'] = repr(error)
    report['artifacts'] = {str(path.relative_to(out)): digest(path) for path in sorted(out.rglob('*')) if path.is_file()}
    target = out / 'report.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'report': str(target), 'client': report.get('client'), 'error': report.get('error')}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

import hashlib, json, os, resource, shlex, socket, subprocess, tempfile, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
o = r / 'qa' / ('corrected-' + str(time.time_ns()))
o.mkdir()
sources = {
    'gtk': r.parent / 'elm-gtk-role-canonical-runtime-v244/native/gtk-role-client.c',
    'observer': r.parent / 'elm-toolkit-popup-canonical-observer-v246/native/observer.cpp',
}
binaries = {}
for name, p in sources.items():
    t = p.read_text()
    if name == 'gtk':
        body = t[t.index('static gboolean canonical_runtime('):t.index('\nint main(')]
        prefix = '#define _XOPEN_SOURCE 700\n#include <glib.h>\n#include <sys/stat.h>\n#include <unistd.h>\n#include <string.h>\n#include <stdio.h>\n#include <stdlib.h>\nstatic gboolean protected_scope(void){return TRUE;}\n'
        suffix = '\nint main(void){printf("%d\\n",private_environment());return 0;}\n'
        compiler = ['/usr/bin/cc', '-std=c11']
        flags = shlex.split(subprocess.check_output(['/usr/bin/pkg-config', '--cflags', '--libs', 'glib-2.0']).decode())
    else:
        body = t[t.index('bool privateSession()'):t.index('std::string surfaceIdentity(')]
        prefix = '#include <filesystem>\n#include <format>\n#include <cstdlib>\n#include <string>\n#include <sys/stat.h>\n#include <unistd.h>\n#include <cstdio>\n'
        suffix = '\nint main(){printf("%d\\n",privateSession());return 0;}\n'
        compiler = ['/usr/bin/c++', '-std=c++23']
        flags = []
    (o / (name + '-actual.txt')).write_text(body)
    q = o / (name + ('.c' if name == 'gtk' else '.cpp'))
    q.write_text(prefix + body + suffix)
    a = subprocess.run(compiler + ['-Wall', '-Wextra', '-Werror', str(q), *flags, '-o', str(o / name)], capture_output=True, timeout=30)
    (o / (name + '-compile.stderr')).write_bytes(a.stderr)
    assert a.returncode == 0, a.stderr
    binaries[name] = o / name
rows = []
base = Path('/run/user') / str(os.getuid()) / 'wqa'
with tempfile.TemporaryDirectory(prefix='guard-', dir=base) as tmp:
    leaf = Path(tmp)
    os.chmod(leaf, 0o700)
    sock = socket.socket(socket.AF_UNIX)
    sock.bind(str(leaf / 'wayland-owned'))
    alias = base / (leaf.name + '-alias')
    alias.symlink_to(leaf)
    try:
        cases = [('canonical', str(leaf), True), ('dot', str(base / '.') + '/.', False), ('dotdot', str(base) + '/..', False), ('leaf-dot', str(leaf) + '/.', False), ('symlink', str(alias), False), ('main', str(base.parent), False)]
        for name, binary in binaries.items():
            for label, runtime, expected in cases:
                env = dict(os.environ, XDG_RUNTIME_DIR=runtime, WAYLAND_DISPLAY='wayland-owned', ELM_GTK_ROLE_QA='1', GDK_BACKEND='wayland', WAYLAND_DEBUG='client', AQ_BACKENDS='wayland')
                a = subprocess.run([str(binary)], env=env, capture_output=True, timeout=5)
                actual = a.stdout.strip() == b'1'
                assert a.returncode == 0 and actual == expected, (name, label, a.stdout, a.stderr)
                rows.append({'guard': name, 'case': label, 'accepted': actual, 'expected': expected})
        os.chmod(leaf, 0o755)
        for name, binary in binaries.items():
            env = dict(os.environ, XDG_RUNTIME_DIR=str(leaf), WAYLAND_DISPLAY='wayland-owned', ELM_GTK_ROLE_QA='1', GDK_BACKEND='wayland', WAYLAND_DEBUG='client', AQ_BACKENDS='wayland')
            a = subprocess.run([str(binary)], env=env, capture_output=True, timeout=5)
            assert a.returncode == 0 and a.stdout.strip() == b'0'
            rows.append({'guard': name, 'case': 'wrong-mode', 'accepted': False, 'expected': False})
    finally:
        alias.unlink()
        sock.close()
        (leaf / 'wayland-owned').unlink()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = {'passed': True, 'nativeAcceptance': False, 'scope': 'Actual guard functions with real canonical paths, private temp directories and unconnected local socket; GTK protected_scope mocked true, no GUI/display connection', 'checks': rows, 'sources': {str(p): sha(p) for p in sources.values()}, 'scriptSHA256': sha(Path(__file__))}
(o / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(str(o / 'report.json'))

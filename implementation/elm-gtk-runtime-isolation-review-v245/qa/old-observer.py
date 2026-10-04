import hashlib, json, os, resource, subprocess, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
p = r.parent / 'elm-toolkit-popup-owned-observer-v240/native/observer.cpp'
t = p.read_text()
body = t[t.index('bool privateSession()'):t.index('std::string surfaceIdentity(')]
o = r / 'qa' / ('old-observer-' + str(time.time_ns()))
o.mkdir()
(o / 'actual-function.txt').write_text(body)
q = o / 'test.cpp'
q.write_text('#include <filesystem>\n#include <format>\n#include <cstdlib>\n#include <string>\n#include <sys/stat.h>\n#include <unistd.h>\n#include <cstdio>\n' + body + '\nint main(){printf("%d\\n",privateSession());return 0;}\n')
a = subprocess.run(['/usr/bin/c++', '-std=c++23', '-Wall', '-Wextra', '-Werror', str(q), '-o', str(o / 'guard')], capture_output=True, timeout=30)
(o / 'compile.stderr').write_bytes(a.stderr)
assert a.returncode == 0, a.stderr
runtime = f'/run/user/{os.getuid()}/wqa/..'
a = subprocess.run([str(o / 'guard')], env=dict(os.environ, XDG_RUNTIME_DIR=runtime, AQ_BACKENDS='wayland'), capture_output=True, timeout=5)
(o / 'actual.stdout').write_bytes(a.stdout)
assert a.returncode == 0 and a.stdout.strip() == b'1'
report = {'diagnosisConfirmed': True, 'nativeAcceptance': False, 'sourceSHA256': hashlib.sha256(p.read_bytes()).hexdigest(), 'runtime': runtime, 'actualAccepted': True, 'scope': 'Actual old observer guard; real filesystem canonical alias resolves main runtime, no display connection'}
(o / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(str(o / 'report.json'))

"""Build the private Weston pointer probe against the exact private Weston 15 pair."""
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
WESTON = Path('/home/hoskinson/window-integration-qa/private-weston-host-v2')
PREFIX = WESTON / 'prefix/usr'
SOURCE = WESTON / 'primary/weston-15.0.1'
OUT = ROOT / 'qa' / ('build-' + str(time.time_ns()))
OUT.mkdir(mode=0o700)
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
inputs = {}
for source in [ROOT/'native/parent-input.xml', ROOT/'native/parent-input-module.c',
               ROOT/'native/parent-input-client.c', ROOT/'native/SOURCE-API.md',
               ROOT/'fixture.py', ROOT/'qa/fixture-inspection.py', Path(__file__),
               WESTON/'host-stage-report.json', WESTON/'weston_host.py',
               PREFIX/'include/libweston-15/libweston/libweston.h',
               SOURCE/'libweston/backend.h', PREFIX/'lib/libweston-15.so.0.0.1']:
    inputs[str(source)] = hashlib.sha256(source.read_bytes()).hexdigest()
    if source.is_relative_to(ROOT):
        target = OUT/'inputs'/source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
generated = OUT/'generated'
generated.mkdir()
steps = []
def run(name, command):
    proc = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=180)
    (OUT/(name+'.stdout')).write_text(proc.stdout)
    (OUT/(name+'.stderr')).write_text(proc.stderr)
    steps.append({'name':name, 'command':list(map(str,command)), 'exitCode':proc.returncode})
    if proc.returncode:
        raise RuntimeError(name + ': ' + proc.stderr)

report = {'passed':False, 'scope':'Exact private Weston parent injection build; no delivery claim',
          'inputs':inputs, 'steps':steps}
try:
    xml = ROOT/'native/parent-input.xml'
    run('server-header', ['wayland-scanner','server-header',xml,generated/'parent-input-server.h'])
    run('client-header', ['wayland-scanner','client-header',xml,generated/'parent-input-client.h'])
    run('protocol-code', ['wayland-scanner','private-code',xml,generated/'parent-input-protocol.c'])
    flags = subprocess.check_output(['pkg-config','--cflags','--libs','wayland-server','pixman-1','xkbcommon'], text=True).split()
    run('module', ['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fPIC','-shared',
                   ROOT/'native/parent-input-module.c',generated/'parent-input-protocol.c',
                   '-I'+str(generated),'-I'+str(PREFIX/'include/libweston-15'),'-I'+str(SOURCE),
                   *flags,'-L'+str(PREFIX/'lib'),'-lweston-15','-o',OUT/'parent-input.so'])
    flags = subprocess.check_output(['pkg-config','--cflags','--libs','wayland-client'], text=True).split()
    run('client', ['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',
                   ROOT/'native/parent-input-client.c',generated/'parent-input-protocol.c',
                   '-I'+str(generated),*flags,'-o',OUT/'parent-input-client'])
    for path, digest in inputs.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
    report['binaries'] = {name:hashlib.sha256((OUT/name).read_bytes()).hexdigest()
                          for name in ('parent-input.so','parent-input-client')}
    report['passed'] = True
except Exception as error:
    report['error'] = repr(error)
(OUT/'report.json').write_text(json.dumps(report, indent=2)+'\n')
print(OUT/'report.json', flush=True)
raise SystemExit(not report['passed'])

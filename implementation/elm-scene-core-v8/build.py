"""Compile one renderer derivative and link a fresh core without changing ancestors."""
import hashlib
import json
from pathlib import Path
import resource
import shlex
import shutil
import subprocess
import time

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
PREVIOUS = REPO / 'implementation/maximized-stack-v2'
OWNER = REPO / 'implementation/maximized-stack-v1/native-core-v2'
OUT = ROOT / ('build-' + str(time.time_ns()))
OUT.mkdir()

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

source = ROOT / 'candidate/src/render/Renderer.cpp'
shutil.copy2(source, OUT / 'Renderer.cpp')
shutil.copy2(__file__, OUT / 'build.py')
prior = json.loads((PREVIOUS / 'native-build-report.json').read_text())
report = {'passed': False, 'installed': False, 'scope': 'Renderer exclusion derivative build only; no native acceptance',
          'sourceSHA256': digest(source), 'priorReportSHA256': digest(PREVIOUS / 'native-build-report.json'), 'commands': []}
try:
    assert prior['result'] == 'pass' and digest(prior['binary']) == prior['sha256']
    archive = PREVIOUS / 'native-build/libhyprland_lib.a'
    archive_hash = digest(archive)
    command = list(prior['commands'][0])
    for index, arg in enumerate(command):
        if index and command[index - 1] == '-c':
            command[index] = str(OUT / 'Renderer.cpp')
        elif index and command[index - 1] == '-o':
            command[index] = str(OUT / 'Renderer.cpp.o')
        elif index and command[index - 1] == '-MF':
            command[index] = str(OUT / 'Renderer.d')
    def run(name, command):
        process = subprocess.run(command, cwd=OWNER / 'build', capture_output=True, timeout=180)
        (OUT / (name + '.stdout')).write_bytes(process.stdout)
        (OUT / (name + '.stderr')).write_bytes(process.stderr)
        report['commands'].append({'name': name, 'command': command, 'exitCode': process.returncode})
        print(name, process.returncode, flush=True)
        assert process.returncode == 0, process.stderr.decode(errors='replace')
    run('compile', command)
    dependencies = shlex.split((OUT / 'Renderer.d').read_text().replace('\\\n', ' ').split(':', 1)[1])
    report['dependencies'] = {str(Path(path).resolve()): digest(path) for path in dependencies}
    assert not any(path.startswith('/usr/include/hyprland') for path in report['dependencies'])
    shutil.copy2(archive, OUT / 'libhyprland_lib.a')
    run('archive', ['/usr/bin/ar', 'r', str(OUT / 'libhyprland_lib.a'), str(OUT / 'Renderer.cpp.o')])
    link = list(prior['commands'][-1])
    for index, arg in enumerate(link):
        if index and link[index - 1] == '-o':
            link[index] = str(OUT / 'Hyprland')
        elif arg == str(archive):
            link[index] = str(OUT / 'libhyprland_lib.a')
        elif arg.startswith('-Wl,--dependency-file='):
            link[index] = '-Wl,--dependency-file=' + str(OUT / 'link.d')
    run('link', link)
    assert digest(archive) == archive_hash and digest(prior['binary']) == prior['sha256']
    report.update(passed=True, binary=str(OUT / 'Hyprland'), binarySHA256=digest(OUT / 'Hyprland'),
                  ancestorBinaryPreserved=True, ancestorArchivePreserved=True,
                  owningVersionHeaderSHA256=digest(OWNER / 'src/version.h'))
except Exception as error:
    report['error'] = repr(error)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(str(OUT / 'report.json'), flush=True)
raise SystemExit(not report['passed'])

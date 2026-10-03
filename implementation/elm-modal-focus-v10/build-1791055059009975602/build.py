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
PREVIOUS = REPO / 'implementation/elm-scene-core-v8'
OWNER = REPO / 'implementation/maximized-stack-v1/native-core-v2'
OUT = ROOT / ('build-' + str(time.time_ns()))
OUT.mkdir()

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

source = ROOT / 'candidate/src/desktop/state/FocusState.cpp'
shutil.copy2(source, OUT / 'FocusState.cpp')
shutil.copy2(__file__, OUT / 'build.py')
prior_path = PREVIOUS / 'build-1791053548003608844/report.json'
prior = json.loads(prior_path.read_text())
report = {'passed': False, 'installed': False, 'scope': 'Native modal focus redirection derivative build only; no native acceptance',
          'sourceSHA256': digest(source), 'priorReportSHA256': digest(prior_path), 'commands': []}
try:
    assert prior['passed'] and digest(prior['binary']) == prior['binarySHA256']
    archive = Path(prior['binary']).parent / 'libhyprland_lib.a'
    archive_hash = digest(archive)
    command = list(prior['commands'][0]['command'])
    command = [arg.replace('/src/render', '/src/desktop/state') if arg.startswith('-I') and arg.endswith('/src/render') else arg for arg in command]
    for index, arg in enumerate(command):
        if index and command[index - 1] == '-c':
            command[index] = str(OUT / 'FocusState.cpp')
        elif index and command[index - 1] == '-o':
            command[index] = str(OUT / 'FocusState.cpp.o')
        elif index and command[index - 1] == '-MF':
            command[index] = str(OUT / 'FocusState.d')
    def run(name, command):
        process = subprocess.run(command, cwd=OWNER / 'build', capture_output=True, timeout=180)
        (OUT / (name + '.stdout')).write_bytes(process.stdout)
        (OUT / (name + '.stderr')).write_bytes(process.stderr)
        report['commands'].append({'name': name, 'command': command, 'exitCode': process.returncode})
        print(name, process.returncode, flush=True)
        assert process.returncode == 0, process.stderr.decode(errors='replace')
    run('compile', command)
    dependencies = shlex.split((OUT / 'FocusState.d').read_text().replace('\\\n', ' ').split(':', 1)[1])
    report['dependencies'] = {str(Path(path).resolve()): digest(path) for path in dependencies}
    assert not any(path.startswith('/usr/include/hyprland') for path in report['dependencies'])
    shutil.copy2(archive, OUT / 'libhyprland_lib.a')
    run('archive', ['/usr/bin/ar', 'r', str(OUT / 'libhyprland_lib.a'), str(OUT / 'FocusState.cpp.o')])
    link = list(prior['commands'][-1]['command'])
    for index, arg in enumerate(link):
        if index and link[index - 1] == '-o':
            link[index] = str(OUT / 'Hyprland')
        elif arg == str(archive):
            link[index] = str(OUT / 'libhyprland_lib.a')
        elif arg.startswith('-Wl,--dependency-file='):
            link[index] = '-Wl,--dependency-file=' + str(OUT / 'link.d')
    run('link', link)
    assert digest(archive) == archive_hash and digest(prior['binary']) == prior['binarySHA256']
    report.update(passed=True, binary=str(OUT / 'Hyprland'), binarySHA256=digest(OUT / 'Hyprland'),
                  ancestorBinaryPreserved=True, ancestorArchivePreserved=True,
                  owningVersionHeaderSHA256=digest(OWNER / 'src/version.h'))
except Exception as error:
    report['error'] = repr(error)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(str(OUT / 'report.json'), flush=True)
raise SystemExit(not report['passed'])

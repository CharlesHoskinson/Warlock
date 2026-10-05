"""Review sealed current runtime and preserve the original renderer fault oracle."""
import ast, hashlib, json, os, resource, stat, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs = {}
def check(path, digest):
    path = Path(path)
    assert path.is_file() and sha(path) == digest, str(path)
    inputs[str(path)] = digest
def hold(path, digest):
    check(path, digest)
    manifest = json.loads(path.read_text())
    assert manifest['passed']
    for row in manifest['files']:
        p = REPO / row['path']
        assert stat.S_IMODE(p.lstat().st_mode) == row['mode'], str(p)
        if 'symlink' in row:
            assert p.is_symlink() and os.readlink(p) == row['symlink']
        else:
            assert not p.is_symlink() and p.stat().st_size == row['size'], str(p)
            check(p, row['sha256'])
    return manifest
parent = hold(REPO / 'implementation/elm-focus-recovery-coherent-reviewed-v350/acceptance-manifest.json', '966470b215087c9ff13db6f8a009acb3d4359cdd7443098ffb26316f0d2b550b')
responsive = hold(REPO / 'implementation/elm-focus-recovery-responsive-held-v353/acceptance-manifest.json', '52578b0f5a9afb2fe8093b350aa602bfa3c9f607ef1dbbd0d73e8bf00bff35d3')
assert parent['currentNativeScopedChecks'] == 626 and responsive['responsiveNativeChecks'] == 893 and responsive['pair'] == parent['pair']
sys.path.insert(0, str(ROOT / 'qa'))
from closure import verify_current
inputs.update(verify_current(ROOT))
source = ROOT / 'qa/native.py'
previous = REPO / 'implementation/elm-responsive-cohort-native-v297/qa/native.py'
expected = previous.read_text()
for before, after in json.loads((ROOT / 'qa/source-amendments.json').read_text()):
    assert expected.count(before) == 1
    expected = expected.replace(before, after)
assert expected == source.read_text(), 'Only reviewed source selection and private-bus policy may change'
calls = lambda p: [ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'check']
original = REPO / 'implementation/elm-cohort-native-v183/qa/native.py'
assert calls(source) == calls(previous) == calls(original)
code = source.read_text()
assert code.count('signal.pidfd_send_signal(renderer_fd,signal.SIGKILL,None,0)') == 2
assert 'def wait(fn,seconds=6):' in code and "wait(lambda:s.data('clients')==[])" in code
assert "if time.monotonic()>=until:raise RuntimeError('Unchanged observation deadline')" in code
for name in ('inspection.py', 'sampling.py'):
    p = ROOT / 'qa' / name
    prior = previous.parent / name
    assert p.read_bytes() == prior.read_bytes()
    check(prior, sha(prior))
assert (ROOT / 'fixture.py').read_bytes() == (previous.parent.parent / 'fixture.py').read_bytes()
bus = REPO / 'implementation/elm-focus-recovery-responsive-bounds-v352/qa/bus_policy.py'
assert bus.read_bytes() == (ROOT / 'qa/bus_policy.py').read_bytes()
check(bus, sha(bus))
runtime = REPO / 'implementation/elm-grant-retirement-runtime-v595'
pair_path = runtime / 'qa/build-pair-manifest.json'
pair = json.loads(pair_path.read_text())
assert pair['passed'] and pair['nativePair'] == parent['pair']
for name, digest in pair['files'].items():
    check(runtime / name, digest)
meta = json.loads((runtime / 'native-build-report.json').read_text())
check(meta['pluginBuildReport'], meta['pluginBuildReportSHA256'])
build = json.loads(Path(meta['pluginBuildReport']).read_text())
assert build['passed'] and not build['missingSymbols']
for section in ('inputs', 'dependencies', 'tools', 'linkedLibraries'):
    for name, digest in build[section].items():
        p = Path(name)
        check(p if p.is_absolute() else Path(meta['pluginBuildReport']).parents[2] / p, digest)
for name, digest in build['owningHeaders'].items():
    check(Path(meta['pluginBuildReport']).parent / 'owning-headers' / name, digest)
for name, digest in build['artifacts'].items():
    check(Path(meta['pluginBuildReport']).parent / name, digest)
producer = REPO / 'implementation/elm-focus-recovery-pinned-toolchain-v349'
report_path = producer / 'qa/build-1791156669069885164/report.json'
build = json.loads(report_path.read_text())
assert build['passed'] and len(build['commands']) == 21 and all(c['exitCode'] == 0 for c in build['commands'])
check(report_path, sha(report_path))
for name, digest in build['inputs'].items():
    check(producer / name, digest)
    check(report_path.parent / 'inputs' / name, build['artifacts'].get('inputs/' + name, digest))
for name, digest in build['artifacts'].items():
    check(report_path.parent / name, digest)
for section in ('compilerDependencies', 'tools', 'linkedLibraries'):
    for name, row in build[section].items():
        check(name, row['sha256'] if isinstance(row, dict) else row)
supervisor = REPO / 'implementation/elm-focus-recovery-renderer-cohort-v354'
for name in ('cohort.py', 'supervisor.py'):
    prior = REPO / 'implementation/elm-responsive-cohort-v296' / name
    assert prior.read_bytes() == (supervisor / name).read_bytes()
    check(prior, sha(prior))
capsule = json.loads((supervisor / 'runtime-manifest.json').read_text())
assert capsule['host'] == str(report_path.parent / 'elm-host') and capsule['backend'] == str(report_path.parent / 'inputs/adapter/daemon.py') and capsule['assets'] == str(report_path.parent / 'inputs/assets') and capsule['coreSHA256'] == pair['nativePair']['core']['sha256']
sealed = {str(report_path.parent / 'elm-host')}
for directory in ('assets', 'adapter'):
    for path in (report_path.parent / 'inputs' / directory).iterdir():
        assert path.is_file() and not path.is_symlink()
        sealed.add(str(path))
assert set(capsule['files']) == sealed
for name, digest in capsule['files'].items():
    check(name, digest)
for path in [*supervisor.iterdir(), source, previous, original, ROOT / 'fixture.py', ROOT / 'SPEC.md', ROOT / 'lineage.json', Path(__file__), *sorted((ROOT / 'qa').glob('*.py')), ROOT / 'qa/source-amendments.json']:
    check(path, sha(path))
result = {'passed': True, 'sourceHeld': True, 'nativeAcceptance': False, 'fullReleaseAccepted': False, 'pair': pair['nativePair'], 'inputs': inputs, 'originalStaticCheckCalls': len(calls(source)), 'scope': 'Original183/297 full bounded renderer/cohort restart/cancel oracle on sealed354 actual349(same333), owning205/594/AQ155. Two verified PIDFD fault signals, original six-second waits and normal ordered teardown remain exact. Private bus excludes automatic activation. No native result yet.'}
with (ROOT / 'qa/preflight.json').open('x') as stream:
    stream.write(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': True, 'inputs': len(inputs), 'originalStaticCheckCalls': result['originalStaticCheckCalls']}))

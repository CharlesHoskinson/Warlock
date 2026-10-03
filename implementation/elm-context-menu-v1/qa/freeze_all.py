"""Freeze separate CPU, build, native and sampled model claims; protected only."""
import hashlib
import json
import resource
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def latest(pattern):
    path = sorted((ROOT/'qa').glob(pattern))[-1]
    value = json.loads(path.read_text())
    assert value['passed'] and not value.get('error'), str(path)
    return path, value

replay_path, replay = latest('replay-*/report.json')
build_path, build = latest('host-build-*/report.json')
native_path, native = latest('native-*/report.json')
model_path, model = latest('model-*/report.json')
assert model['stage'] == 'final'
assert native['cleanupPassed'] and not native['mainDesktopActions']
assert Path(native['buildReport']) == build_path
assert sha(build_path) == native['buildReportSHA256']
assert sha(build_path.parent/'elm-host') == build['binarySHA256']
for name, report, frozen in [
    ('replay', replay, replay_path.parent/'inputs'),
    ('build', build, build_path.parent/'inputs'),
    ('model', model, model_path.parent),
]:
    for relative, digest in report['inputs'].items():
        assert sha(ROOT/relative) == digest, name+': '+relative
        assert sha(frozen/relative) == digest, 'Frozen '+name+': '+relative
for absolute, digest in native['inputs'].items():
    assert sha(absolute) == digest, absolute
manifest_path = ROOT/'qa/implementation-manifest.json'
assert not manifest_path.exists(), 'Preserve a frozen manifest; use a new derivative'
files = {}
links = {}
for path in sorted(ROOT.rglob('*')):
    if path == manifest_path:
        continue
    relative = str(path.relative_to(ROOT))
    if path.is_symlink():
        links[relative] = str(path.readlink())
    elif path.is_file():
        files[relative] = sha(path)
claims = {}
for name, path, report in [('elmReplay', replay_path, replay),
                           ('hostBuild', build_path, build),
                           ('nativeMenu', native_path, native),
                           ('sampledModel', model_path, model)]:
    claims[name] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                    'scope': report['scope']}
manifest = {'passed': True, 'observedUTC': datetime.now(timezone.utc).isoformat(),
            'wholeFeatureAccepted': False, 'completedRequirementIds': [],
            'installedChanges': False, 'boundedNativeMenuPassed': True,
            'claims': claims, 'elmChecks': replay['checks'],
            'nativeChecks': len(native['checks']),
            'modelNamedScenarios': model['namedScenarios'],
            'modelSamples': model['invariantSamples'],
            'modelMaxSteps': model['maxSteps'],
            'nativePair': native['pair'], 'files': files, 'symlinks': links}
manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
print(json.dumps({'passed': True, 'files': len(files), 'manifest': str(manifest_path)}))

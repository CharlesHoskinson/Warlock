import copy, hashlib, importlib.util, json, resource, sys, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-gtk-role-native-v238/qa'
sys.path.insert(0, str(owner))
def load(name):
    spec = importlib.util.spec_from_file_location('review_' + name, owner / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
geometry, pixels = load('geometry'), load('pixels')
selected = {'marker': {'global': [80, 100]}, 'native': {'at': [40, 70], 'size': [320, 180]}}
other = {'native': {'at': [420, 70]}, 'wire': {'windowGeometry': [10, 20, 320, 180]}, 'gtk': {'surfaceWidth': 340, 'surfaceHeight': 220}}
checks = []
expected = {'selectedSampleRect': [79, 99, 3, 3], 'selectedRealRect': [40, 70, 320, 180], 'excludedOtherSurfaceRect': [410, 50, 340, 220]}
assert geometry.attribution(selected, other) == expected
checks.append('independent-disjoint-surface-oracle')
overlap = copy.deepcopy(other)
overlap['native']['at'] = [90, 70]
overlap['wire']['windowGeometry'][0] = 30
# The other native geometry begins at90, but its actual surface starts at60.
assert selected['marker']['global'][0] < overlap['native']['at'][0]
try:
    geometry.attribution(selected, overlap)
    raise AssertionError('CSD overlap accepted')
except geometry.Refused:
    checks.append('other-CSD-overlap-outside-other-native-rect-refused')
outside = copy.deepcopy(selected)
outside['marker']['global'] = [40, 100]
try:
    geometry.attribution(outside, other)
    raise AssertionError('sample outside selected rectangle accepted')
except geometry.Refused:
    checks.append('whole-nine-pixel-selected-containment')
image = bytearray(bytes([255, 255, 0]) * (800 * 600))
offset = (99 * 800 + 79) * 3
image[offset:offset + 3] = b'\0\0\0'
actual = pixels.yellow_marker(bytes(image), [80, 100])
assert actual['passed'] is False and len(actual['samples']) == 9
assert actual['samples'][0] == {'point': [79, 99], 'rgb': [0, 0, 0]}
assert actual['samples'][-1] == {'point': [81, 101], 'rgb': [255, 255, 0]}
checks.append('failed-first-sample-retains-all-nine-measurements')
out = r / 'qa' / ('corrected-' + str(time.time_ns()))
out.mkdir()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = {'passed': True, 'nativeAcceptance': False, 'scope': 'Actual corrected helper functions with independent synthetic coordinates/RGB; no GUI or subprocess launch', 'checks': checks, 'sources': {str(owner / (name + '.py')): sha(owner / (name + '.py')) for name in ('geometry', 'pixels')}, 'measurements': actual}
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(str(out / 'report.json'))

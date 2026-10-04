"""Bind held-cancellation source, negative controls, and owning native evidence."""
import hashlib
import json
import os
import resource
from pathlib import Path

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
IMPL = ROOT.parent
REPO = IMPL.parent

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

component = IMPL / 'elm-parent-held-cancellation-v120/component-manifest.json'
packet = json.loads(component.read_text())
assert packet['passed'] and not packet['nativeAcceptance'] and not packet['releaseAcceptance']
for entry in packet['files']:
    path = component.parent / entry['path']
    if 'symlink' in entry:
        assert path.is_symlink() and os.readlink(path) == entry['symlink']
    else:
        assert sha(path) == entry['sha256'], str(path)
tuple_path = IMPL / 'elm-parent-held-cancellation-native-v121/aq-tuple.json'
aq = json.loads(tuple_path.read_text())
assert aq['manifest'] == str(component) and aq['manifestSHA256'] == sha(component)
assert sha(aq['library']) == aq['librarySHA256']
native = []

def verify_native(path, count, mask=None):
    data = json.loads(path.read_text())
    assert data['passed'] and data['cleanupPassed']
    assert not data['mainDesktopActions']
    assert len(data['checks']) == count and all(c['passed'] for c in data['checks'])
    for name, value in data['inputs'].items():
        assert sha(name) == value, name
    for name, value in data['artifacts'].items():
        assert sha(path.parent / name) == value, name
    selected = json.loads((path.parent.parent.parent / 'aq-tuple.json').read_text())
    assert selected == aq
    private = data['privateHost']['privateAquamarine']
    assert private['sha256'] == aq['librarySHA256']
    assert private['contractManifestSHA256'] == aq['manifestSHA256']
    assert private['mappedVerified'] is True
    assert private['mappedFiles'][str(Path(aq['library']).resolve())] == aq['librarySHA256']
    if mask is not None:
        assert data['heldMask'] == mask
        assert data['heldStateAfterLoss']['held'] is False
    native.append({'path': str(path), 'sha256': sha(path), 'checks': count,
                   'heldMask': mask})

def latest(root, prefix='native'):
    return sorted((IMPL / root / 'qa').glob(prefix + '-*/report.json'))[-1]

originals = [
    ('elm-parent-held-cancellation-native-v121', 'native', 34),
    ('elm-held-cancellation-input-v122', 'native', 159),
    ('elm-held-cancellation-multi-v123', 'native', 51),
    ('elm-held-cancellation-burst-v124', 'native', 35),
    ('elm-held-cancellation-geometry-v125', 'native', 96),
    ('elm-held-cancellation-menu-v126', 'menu', 68),
    ('elm-held-cancellation-menu-v126', 'native', 195),
    ('elm-held-cancellation-unheld-v127', 'native', 26),
]
for root, prefix, count in originals:
    verify_native(latest(root, prefix), count)
for mask in range(1, 8):
    path = sorted((IMPL / 'elm-held-cancellation-masks-v128' / ('mask-' + str(mask))
                   / 'qa').glob('native-*/report.json'))[-1]
    verify_native(path, 35, mask)
assert sum(row['checks'] for row in native) == 909

negative = []
for root, phase, count in [
    ('elm-parent-held-transport-native-v115', 'physicalPressHeldInActualChild', 0),
    ('elm-parent-held-transport-native-v116', 'actualChildHeldButtonsCancelled', 0),
]:
    path = latest(root)
    data = json.loads(path.read_text())
    assert not data['passed'] and data['cleanupPassed'] and phase in data['error']
    if root.endswith('v116'):
        assert data['heldStateAfterLoss']['held'] is True
        assert data['heldStateAfterLoss']['mousePresent'] is False
    negative.append({'path': str(path), 'sha256': sha(path), 'failure': phase})

owned = [
    'elm-parent-held-transport-fixture-v113', 'elm-held-state-observer-v114',
    'elm-parent-held-transport-native-v115', 'elm-parent-held-transport-native-v116',
    'elm-parent-held-cancellation-v117', 'elm-parent-held-cancellation-v118',
    'elm-held-cancellation-model-v119', 'elm-parent-held-cancellation-v120',
    'elm-parent-held-cancellation-native-v121', 'elm-held-cancellation-input-v122',
    'elm-held-cancellation-multi-v123', 'elm-held-cancellation-burst-v124',
    'elm-held-cancellation-geometry-v125', 'elm-held-cancellation-menu-v126',
    'elm-held-cancellation-unheld-v127', 'elm-held-cancellation-masks-v128',
    ROOT.name,
]
files = {}
symlinks = {}
for name in owned:
    for path in sorted((IMPL / name).rglob('*')):
        if path == ROOT / 'acceptance-manifest.json':
            continue
        relative = str(path.relative_to(REPO))
        if path.is_symlink():
            symlinks[relative] = os.readlink(path)
        elif path.is_file():
            files[relative] = {'sha256': sha(path), 'size': path.stat().st_size}
manifest = {
    'schema': 1, 'passed': True, 'nativeAcceptance': True, 'releaseAcceptance': False,
    'component': 'Admitted pointer-button cancellation on parent transport loss',
    'scope': '909 native check executions, not unique scenarios or roadmap completion. '
             'One private parent seat, all seven nonempty left/right/middle masks; '
             'Core89/plugin90 where applicable/AQ120. Original normal oracles retain '
             'historical baseline scope strings; AQ descriptors and actual mapped '
             'library evidence identify the tested candidate. No installed changes.',
    'sourceComponent': {'path': str(component), 'sha256': sha(component)},
    'aquamarine': aq, 'native': native, 'negativeControls': negative,
    'remaining': ['Held-key cancellation and device/hardware qualification',
                  'Coherent shared GUI release, full S01-S16 and applicable C00-C06 gates',
                  'Accessibility/IME, performance budgets, user journeys and deployment/rollback'],
    'files': files, 'symlinks': symlinks,
}
destination = ROOT / 'acceptance-manifest.json'
assert not destination.exists()
destination.write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'passed': True, 'nativeCheckExecutions': 909,
                  'manifest': str(destination), 'sha256': sha(destination),
                  'files': len(files), 'symlinks': len(symlinks)}))

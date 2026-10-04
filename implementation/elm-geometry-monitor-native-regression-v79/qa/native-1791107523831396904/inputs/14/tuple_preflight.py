"""Read-only frozen input verification; no native process or socket is opened."""
import hashlib
import json
from pathlib import Path

def verify_frozen_tuple(repo, auth, descriptor):
    def sha(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    def verify(path, wanted):
        path = Path(path)
        assert path.is_file() and not path.is_symlink() and sha(path) == wanted, str(path)
    review_root = repo / 'implementation/elm-geometry-monitor-pair-review-v76'
    manifest_path = review_root / 'qa/held-source-manifest.json'
    verify(manifest_path, '7119b6b63fbb60a39b9eae19d67b87746c00b75096f063dee0d5bf82c124a5a0')
    manifest = json.loads(manifest_path.read_text())
    assert manifest['sourceHeld'] and manifest['evidenceIntegrityPassed']
    assert manifest['nativeAcceptance'] is False
    assert Path(manifest['pairRoot']) == auth
    for relative, row in manifest['files'].items():
        verify(review_root / relative, row['sha256'])
    for relative, row in manifest['pairFiles'].items():
        path = auth / relative
        verify(path, row['sha256'])
        assert path.stat().st_size == row['size'], relative
    review_path = Path(manifest['report'])
    verify(review_path, manifest['reportSHA256'])
    review = json.loads(review_path.read_text())
    assert review['passed']
    for path, wanted in review['verified'].items():
        verify(path, wanted)
    assert review['descriptorSHA256'] == sha(auth / 'native-build-report.json')
    core_component = Path(descriptor['coreComponentManifest'])
    verify(core_component, descriptor['coreComponentManifestSHA256'])
    component = json.loads(core_component.read_text())
    assert component['sourceHeld'] and component['evidenceIntegrityPassed']
    assert component['nativeAcceptance'] is False
    for relative, row in component['files'].items():
        path = core_component.parent / relative
        verify(path, row['sha256'])
        assert path.stat().st_size == row['size'], relative
    ancestor = repo / 'implementation/elm-geometry-effect-native-v55'
    old_manifest_path = ancestor / 'component-manifest.json'
    verify(old_manifest_path, '3b1f68d711718c62011a32fd64d6ae70d14bda76489f1b5deb3d6904a2fbccc9')
    old = json.loads(old_manifest_path.read_text())
    assert old['passed'] and old['nativeQualification']['nativeChecks'] == 96
    assert old['nativeQualification']['pixelChecks'] == 7
    for row in old['files']:
        path = ancestor / row['path']
        verify(path, row['sha256'])
        assert path.stat().st_size == row['size'], row['path']
    return manifest_path, core_component, old_manifest_path

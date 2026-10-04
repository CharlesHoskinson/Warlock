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
    review_root = repo / 'implementation/elm-parent-first-anchor-acceptance-v96'
    manifest_path = review_root / 'acceptance-manifest.json'
    verify(manifest_path, 'd50be687e5776faa25f1465ad43363339c7e7d84f91d0ade868d3728efd61e68')
    manifest = json.loads(manifest_path.read_text())
    assert manifest['passed'] and manifest['releaseAcceptance'] is False
    assert manifest['tuple']['core']=={'path':descriptor['binary'],'sha256':descriptor['sha256']}
    assert manifest['tuple']['plugin']==descriptor['plugin']
    for row in manifest['files']:
        path=repo/row['path']
        if 'symlink' in row:
            assert path.is_symlink() and str(path.readlink())==row['symlink'],str(path)
        else:
            verify(path,row['sha256'])
            assert path.stat().st_size==row['size'],str(path)
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

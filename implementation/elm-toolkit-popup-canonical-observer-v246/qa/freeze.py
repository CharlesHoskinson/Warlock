"""Freeze compiled read-only popup diagnostics, without native acceptance."""
import hashlib, json, resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'qa/build-1791139221615888759/report.json'
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    r = json.loads(BUILD.read_text())
    assert r['passed'] is True and not r['missingSymbols']
    for name, digest in r['artifacts'].items():
        assert sha(BUILD.parent / name) == digest, name
    for name, digest in r['inputs'].items():
        assert sha(ROOT / name) == digest, name
    for name, digest in r['owningHeaders'].items():
        assert sha(BUILD.parent / 'owning-headers' / name) == digest, name
    external = {}
    for section in ('dependencies', 'linkedLibraries', 'tools'):
        for name, digest in r[section].items():
            assert sha(name) == digest, name
            external[name] = {'sha256': digest, 'size': Path(name).stat().st_size}
    for key in ('path', 'buildReport', 'componentManifest'):
        expected = r['core'][{'path': 'sha256', 'buildReport': 'buildReportSHA256', 'componentManifest': 'componentManifestSHA256'}[key]]
        name = r['core'][key]
        assert sha(name) == expected
        external[name] = {'sha256': expected, 'size': Path(name).stat().st_size}
    source = (ROOT / 'native/observer.cpp').read_text()
    parent = json.loads((ROOT / 'origin.json').read_text())
    old = Path(parent['parent']) / 'native/observer.cpp'
    assert sha(old) == parent['files']['native/observer.cpp']
    legacy = old.read_text().split('std::string observe(', 1)[1].split('\n}\n}\nAPICALL', 1)[0]
    current = source.split('std::string observe(', 1)[1].split('\n}\n}\nAPICALL', 1)[0]
    assert legacy == current, 'Original held-state query must remain byte-identical'
    assert old.read_text().split('std::string observeRoles(', 1)[1].split('std::string observe(', 1)[0] == source.split('std::string observeRoles(', 1)[1].split('std::string observe(', 1)[0], 'Original role query must remain byte-identical'
    external[str(old)] = {'sha256': sha(old), 'size': old.stat().st_size}
    files = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'size': p.stat().st_size}
             for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p.name != 'component-manifest.json'}
    result = {'sourceHeld': True, 'compiled': True, 'nativeAcceptance': False,
              'fullRoadmapAccepted': False, 'scope': 'Read-only canonical-private-runtime role and strongly owned window-popup observer on exact470 ABI; no GUI run',
              'buildReport': str(BUILD), 'buildReportSHA256': sha(BUILD), 'files': files, 'externalFiles': external}
    (ROOT / 'component-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'held': True, 'files': len(files), 'external': len(external)}))
if __name__ == '__main__':
    main()

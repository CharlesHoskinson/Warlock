import hashlib, json, resource, stat, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
reports = [r / 'qa' / x for x in ['witness-1791139327241351105/report.json', 'parent-1791139401575564500/report.json', 'corrected-1791139567202455330/report.json', 'old-observer-1791139600376674684/report.json']]
for p in reports:
    v = json.loads(p.read_text())
    assert v.get('passed', v.get('diagnosisConfirmed')) is True
    assert v['nativeAcceptance'] is False
external = {}
for lane, source in [('elm-gtk-role-journal-fixture-v233', 'native/gtk-role-client.c'), ('elm-parent-keyboard-surface-observer-v239', 'native/parent-input-client.c'), ('elm-parent-keyboard-surface-observer-v239', 'native/parent-input-module.c'), ('elm-toolkit-popup-owned-observer-v240', 'native/observer.cpp'), ('elm-gtk-role-canonical-runtime-v244', 'native/gtk-role-client.c'), ('elm-toolkit-popup-canonical-observer-v246', 'native/observer.cpp')]:
    p = r.parent / lane / source
    external[str(p)] = {'sha256': sha(p), 'size': p.stat().st_size}
corrected = json.loads(reports[2].read_text())
for p, digest in corrected['sources'].items():
    assert external[p]['sha256'] == digest
assert sha(r.parent / 'elm-gtk-role-journal-fixture-v233/component-manifest.json') == '58d33306a1234548059ff9ec36975f1c8c0cbd8d1fe5c676f735ed379739bc1d'
assert sha(r.parent / 'elm-parent-keyboard-surface-observer-v239/component-manifest.json') == 'e125cb7cf93b3dc8e5e41889e6db07bea7e46a3fcb5955bbeae416ab3f46344a'
files = {}
for p in sorted(r.rglob('*')):
    if not p.is_file() or p.name == 'component-manifest.json':
        continue
    assert not p.is_symlink()
    files[str(p.relative_to(r))] = {'sha256': sha(p), 'size': p.stat().st_size, 'mode': stat.S_IMODE(p.stat().st_mode)}
manifest = {'schema': 1, 'sourceHeld': True, 'nativeAcceptance': False, 'completion': False, 'scope': 'Compiled exact guard diagnosis and corrected guard filesystem tests only', 'files': files, 'externalSources': external, 'reports': [str(p.relative_to(r)) for p in reports]}
(r / 'component-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'passed': True, 'files': len(files), 'manifestSHA256': sha(r / 'component-manifest.json')}))

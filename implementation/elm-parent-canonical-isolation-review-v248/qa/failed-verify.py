import hashlib, json, resource, stat, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-parent-keyboard-canonical-observer-v247'
old = r.parent / 'elm-parent-keyboard-surface-observer-v239'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = r / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
report = {'passed': False, 'nativeAcceptance': False, 'checks': []}
try:
    manifest = json.loads((owner / 'component-manifest.json').read_text())
    assert manifest['sourceHeld'] is True
    rows = manifest['files']
    for name, entry in rows.items():
        p = owner / name
        assert not p.is_symlink() and p.is_file(), name
        assert sha(p) == entry['sha256'] and p.stat().st_size == entry['size'], name
        if 'mode' in entry:
            assert stat.S_IMODE(p.stat().st_mode) == entry['mode'], name
    for name in ['parent-input.xml', 'surface-observer.h']:
        assert (owner / 'native' / name).read_bytes() == (old / 'native' / name).read_bytes(), name
    a = (old / 'native/parent-input-module.c').read_text()
    b = (owner / 'native/parent-input-module.c').read_text()
    restored = b.replace('#include "private-runtime.h"\n', '').replace(' || !canonical_private_runtime(getenv("XDG_RUNTIME_DIR"))', '')
    assert restored == a
    a = (old / 'native/parent-input-client.c').read_text()
    b = (owner / 'native/parent-input-client.c').read_text()
    assert a[a.index('static bool send_request('):] == b[b.index('static bool send_request('):]
    before_a = a[:a.index('static bool private_socket(')]
    before_b = b[:b.index('static bool private_socket(')]
    before_b = before_b.replace('#ifndef _GNU_SOURCE\n#define _GNU_SOURCE\n#endif\n', '').replace('#ifndef _POSIX_C_SOURCE\n#define _POSIX_C_SOURCE 200809L\n#endif', '#define _POSIX_C_SOURCE 200809L').replace('#include <sys/socket.h>\n', '').replace('#include <sys/un.h>\n', '').replace('#include "private-runtime.h"\n', '')
    assert before_a == before_b
    guards = sorted((owner / 'qa').glob('guard-*/report.json'))
    v = json.loads(guards[-1].read_text())
    assert v['passed'] and not v['nativeAcceptance']
    assert v['guardSourceSHA256'] == sha(owner / 'native/private-runtime.h')
    assert v['clientSourceSHA256'] == sha(owner / 'native/parent-input-client.c')
    assert all(x['passed'] for x in v['checks'])
    report.update(passed=True, verifiedRows=len(rows), guardChecks=len(v['checks']), ownerManifestSHA256=sha(owner / 'component-manifest.json'), guardReport=str(guards[-1]), guardReportSHA256=sha(guards[-1]), checks=['all-owning-held-files', 'observer-XML-byteexact', 'module-only-preglobal-guard-change', 'all-client-handlers-byteexact', 'client-prehandler-only-macros-includes-guard', 'actual-guard-report-current-sources'])
except Exception as e:
    report['error'] = repr(e)
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
if not report['passed']:
    raise SystemExit(1)
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size, 'mode': stat.S_IMODE(p.stat().st_mode)} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'completion': False, 'ownerManifestSHA256': report['ownerManifestSHA256'], 'files': files, 'verificationReport': str((out / 'report.json').relative_to(r))}, indent=2) + '\n')
print('reviewManifestSHA256=' + sha(r / 'component-manifest.json'))

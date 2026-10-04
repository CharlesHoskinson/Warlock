import hashlib, json, resource, stat, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-gtk-sibling-role-fixture-v253'
old = r.parent / 'elm-gtk-role-canonical-runtime-v244'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(owner / 'component-manifest.json') == '32f0cc1aff70793ef9cc2d1bc76508806500a5be34df386696d5db4aa5cc4758'
m = json.loads((owner / 'component-manifest.json').read_text())
count = 0
for section, base in [('files', owner), ('externalFiles', None)]:
    for name, row in m[section].items():
        p = base / name if base is not None else Path(name)
        row = row if isinstance(row, dict) else {'sha256': row}
        assert sha(p) == row['sha256'], str(p)
        if 'size' in row: assert p.stat().st_size == row['size'], str(p)
        if 'mode' in row:
            assert stat.S_IMODE(p.stat().st_mode) == row['mode'], str(p)
        count += 1
a = (old / 'native/gtk-role-client.c').read_text()
b = (owner / 'native/gtk-role-client.c').read_text()
def function(text, name):
    at = text.index(name + '(')
    start = text.index('{', at)
    depth = 1
    end = start + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[at:end]
unchanged = ['surface_id', 'record', 'emit', 'state_changed', 'mapped', 'unmapped', 'input_record', 'current_controller', 'pressed', 'released', 'key_pressed', 'key_released', 'motion', 'attach', 'close_role', 'close_requested', 'popover_clicked', 'draw', 'window_new', 'stdin_ready', 'own_start', 'protected_scope', 'canonical_runtime', 'private_environment']
for name in unchanged:
    assert function(a, name) == function(b, name), name
reports = []
for relative in ['qa/test-1791142248825783858/report.json', 'qa/callbacks-1791142201726339518/report.json', 'qa/lifecycle-1791142248827346211/report.json']:
    p = owner / relative
    v = json.loads(p.read_text())
    assert v['passed'], relative
    reports.append({'path': str(p), 'sha256': sha(p)})
out = r / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
report = {'passed': True, 'nativeAcceptance': False, 'verifiedRows': count, 'unchangedFunctions': unchanged, 'ownerManifestSHA256': sha(owner / 'component-manifest.json'), 'ownerSourceSHA256': sha(owner / 'native/gtk-role-client.c'), 'reports': reports}
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'fullCampaignPassed': False, 'files': files, 'ownerManifestSHA256': report['ownerManifestSHA256'], 'verificationReport': str((out / 'report.json').relative_to(r))}, indent=2) + '\n')
print(json.dumps({'passed': True, 'rows': count, 'unchangedFunctions': len(unchanged), 'manifestSHA256': sha(r / 'component-manifest.json')}))

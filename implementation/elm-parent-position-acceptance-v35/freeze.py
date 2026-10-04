"""Freeze bounded parent-position qualification without changing ancestor evidence."""
import hashlib
import json
import os
from pathlib import Path
import resource

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
IMPL = REPO / 'implementation'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def verify_files(base, files):
    if isinstance(files, dict):
        for rel, digest in files.items():
            assert sha(base / rel) == digest, rel
    else:
        for row in files:
            path = base / row['path']
            if 'symlink' in row:
                assert path.is_symlink() and os.readlink(path) == row['symlink'], path
            else:
                assert sha(path) == row['sha256'], path


pair_path = IMPL / 'elm-parent-position-pair-v32/qa/build-pair-manifest.json'
pair = read(pair_path)
assert pair['passed']
verify_files(pair_path.parent.parent, pair['files'])
core = pair['nativePair']['core']
plugin = pair['nativePair']['plugin']
assert sha(core['path']) == core['sha256']
assert sha(plugin['path']) == plugin['sha256']
assert sha(core['componentManifest']) == core['componentManifestSHA256']
core_manifest = read(core['componentManifest'])
verify_files(Path(core['componentManifest']).parent, core_manifest['files'])

aq_path = IMPL / 'elm-nested-input-status-v30/component-manifest.json'
aq_manifest = read(aq_path)
assert aq_manifest['passed']
verify_files(aq_path.parent, aq_manifest['files'])
aq_tuple = read(IMPL / 'elm-parent-stationary-click-v33/aq-tuple.json')
assert aq_tuple['manifestSHA256'] == sha(aq_path)
assert sha(aq_tuple['library']) == aq_tuple['librarySHA256']

native_reports = [
    ('elm-parent-stationary-click-v33/qa/native-1791098397418492152/report.json', 195),
    ('elm-parent-stationary-click-v33/qa/menu-1791098610460993839/report.json', 68),
    ('elm-parent-button-position-v34/qa/native-1791098659787486590/report.json', 105),
]
qualified = []
for relative, count in native_reports:
    path = IMPL / relative
    report = read(path)
    assert report['passed'] and report['cleanupPassed'] and not report['mainDesktopActions']
    assert len(report['checks']) == count and all(c['passed'] for c in report['checks'])
    for key in ['inputs', 'sourceInputs']:
        verify_files(Path('/'), report.get(key, {}))
    verify_files(path.parent, report['artifacts'])
    host = report['privateHost']
    assert host['hyprlandMaps']['files'][str(Path(core['path']).resolve())] == core['sha256']
    assert host['privateAquamarine']['mappedFiles'][str(Path(aq_tuple['library']).resolve())] == aq_tuple['librarySHA256']
    assert host['runtimeGone'] and not host['cleanupErrors'] and not host['remainingDescendants']
    assert host['xwaylandEnabled'] is False
    if '/menu-' in relative:
        assert report['pluginMapsAfterLoad']['files'][str(Path(plugin['path']).resolve())] == plugin['sha256']
    qualified.append({'path': str(path), 'sha256': sha(path), 'checks': count,
                      'passed': True, 'cleanupPassed': True, 'scope': report['scope']})

query_path = IMPL / 'elm-parent-focus-query-v27/qa/query-1791098138757795492/report.json'
query = read(query_path)
assert query['passed'] and not query['nativeAcceptance'] and query['checks'] == 25
verify_files(Path('/'), query['inputs'])

# Preserve earlier failure claims and distinguish them from corrected tuple evidence.
failed_path = IMPL / 'elm-core-parent-position-v29/build-1791097910600715193/report.json'
assert read(failed_path)['passed'] is False
old_path = IMPL / 'elm-parent-stationary-click-v26/qa/native-1791097090711114043/report.json'
assert read(old_path)['passed'] is False

owned = ['elm-parent-focus-query-v27', 'elm-nested-input-focus-v28',
         'elm-core-parent-position-v29', 'elm-nested-input-status-v30',
         'elm-core-parent-position-v31', 'elm-parent-position-pair-v32',
         'elm-parent-stationary-click-v33', 'elm-parent-button-position-v34',
         ROOT.name]
files = []
for name in owned:
    for path in sorted((IMPL / name).rglob('*')):
        if path == ROOT / 'acceptance-manifest.json':
            continue
        if path.is_symlink():
            files.append({'path': str(path.relative_to(IMPL)), 'symlink': os.readlink(path)})
        elif path.is_file():
            files.append({'path': str(path.relative_to(IMPL)), 'sha256': sha(path), 'size': path.stat().st_size})

out = ROOT / 'acceptance-manifest.json'
assert not out.exists()
out.write_text(json.dumps({
    'schema': 1, 'passed': True, 'scope': 'Bounded stationary input/cursor and original menu/held-button native campaigns',
    'releaseAcceptance': False, 'mainDesktopActions': False, 'quintQualification': False,
    'pairManifest': str(pair_path), 'pairManifestSHA256': sha(pair_path),
    'aqManifest': str(aq_path), 'aqManifestSHA256': sha(aq_path), 'aqTuple': aq_tuple,
    'nativeReports': qualified,
    'cpuFocusQuery': {'path': str(query_path), 'sha256': sha(query_path), 'checks': 25, 'nativeAcceptance': False},
    'retainedFailures': [{'path': str(p), 'sha256': sha(p)} for p in [failed_path, old_path]],
    'remaining': ['Native focus/configure/capability loss and device retirement fencing',
                  'Dedicated Quint parent-position contract and implementation trace comparison',
                  'Multiple outputs/rotation, shell integration, physical devices, AT/IME, budgets and full release'],
    'files': files,
}, indent=2) + '\n')
print(json.dumps({'passed': True, 'manifest': str(out), 'files': len(files), 'nativeChecks': 368}))

"""Independently hold responsive GUI evidence without broadening release claims."""
import ast, hashlib, json, os, resource, stat, sys, time, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
OUT = ROOT / 'qa' / ('review-' + str(time.time_ns()))
OUT.mkdir()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
result = {'passed': False, 'fullReleaseAccepted': False}
try:
    references = {}
    def pin(path, digest=None):
        path = Path(path)
        actual = sha(path)
        assert digest is None or actual == digest, str(path)
        references[str(path.relative_to(REPO))] = actual
        return json.loads(path.read_text())
    def verify_report(path):
        report = pin(path)
        for name, digest in report.get('inputs', {}).items():
            assert sha(name) == digest, name
        for name, digest in report.get('artifacts', {}).items():
            assert sha(path.parent / name) == digest, name
        return report
    parent_path = REPO / 'implementation/elm-focus-recovery-coherent-reviewed-v350/acceptance-manifest.json'
    parent = pin(parent_path, '966470b215087c9ff13db6f8a009acb3d4359cdd7443098ffb26316f0d2b550b')
    assert parent['passed'] and parent['currentNativeScopedChecks'] == 626
    assert not parent['fullReleaseAccepted'] and not parent['allGeometryContractScenariosAccepted']
    for row in parent['files']:
        path = REPO / row['path']
        assert stat.S_IMODE(path.lstat().st_mode) == row['mode'], str(path)
        if 'symlink' in row:
            assert path.is_symlink() and os.readlink(path) == row['symlink']
        else:
            assert not path.is_symlink() and sha(path) == row['sha256'] and path.stat().st_size == row['size'], str(path)
    current = REPO / 'implementation/elm-focus-recovery-responsive-bounds-v352'
    original = REPO / 'implementation/elm-gui-bounds-native-v279/qa'
    assert (current / 'profiles.json').read_bytes() == (REPO / 'implementation/elm-keyboardless-bounds-regression-v215/profiles.json').read_bytes()
    profiles = json.loads((current / 'profiles.json').read_text())['profiles']
    table = {row['id']: row for row in profiles}
    assert len(table) == len(profiles) == 22
    for name in ('gui.py', 'inspection.py'):
        expected = (original / name).read_text()
        if name == 'gui.py':
            for before, after in json.loads((current / 'qa/observation-amendment.json').read_text()):
                assert expected.count(before) == 1
                expected = expected.replace(before, after)
        assert expected == (current / 'qa' / name).read_text()
    run = lambda p: next(n for n in ast.parse(p.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    previous = run(original / 'native.py')
    for node in ast.walk(previous):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            node.value = node.value.replace('on278/Core205/206/AQ155', 'on349(same333)/Core205/594/AQ155')
    assert ast.dump(previous, include_attributes=False) == ast.dump(run(current / 'qa/native.py'), include_attributes=False)
    preflight = verify_report(current / 'qa/preflight.json')
    assert preflight['passed'] and preflight['profileCount'] == 22 and len(preflight['inputs']) == 6205
    controls_path = next((current / 'qa').glob('observations-*/report.json'))
    controls = verify_report(controls_path)
    assert controls['passed'] and len(controls['checks']) == 16 and all(c['passed'] for c in controls['checks']) and controls['productionChanged'] is False
    failure_path = REPO / 'implementation/elm-focus-recovery-responsive-bounds-v351/qa/native-1791157538587667379/report.json'
    failure = verify_report(failure_path)
    assert not failure['passed'] and len(failure['checks']) == 293 and failure['cleanupPassed']
    assert "'NoneType' object is not subscriptable" in failure['error'] and not failure['profileCleanupErrors'] and not failure['finalCleanupErrors']
    reports = []
    seen = set()
    outputs = set()
    count = 0
    report_paths = sorted((current / 'qa').glob('native-*/report.json'))
    assert len(report_paths) == 3
    for path in report_paths:
        report = verify_report(path)
        assert report['passed'] and all(c['passed'] for c in report['checks']) and report['cleanupPassed']
        assert not report['profileCleanupErrors'] and not report['finalCleanupErrors']
        cleanup = report['cleanup']
        assert not cleanup['mainDisplayUsed'] and cleanup['runtimeGone'] and cleanup['privateAquamarine']['mappedVerified']
        assert not any(cleanup.get(k) for k in ('cleanupErrors', 'remainingDescendants', 'unexpectedInnerDescendants'))
        pair = parent['pair']
        assert cleanup['hyprlandMaps']['files'][str(Path(pair['core']['path']).resolve())] == pair['core']['sha256']
        assert report['pluginMaps']['files'][str(Path(pair['plugin']['path']).resolve())] == pair['plugin']['sha256']
        output = report['requestedOutput']
        outputs.add((tuple(output['physicalMode']), output['monitorScale']))
        for record in report['profiles']:
            requested = record['requestedProfile']
            assert requested == table[requested['id']]
            assert requested['physicalMode'] == output['physicalMode'] and requested['monitorScale'] == output['monitorScale']
            seen.add(requested['id'])
        count += len(report['checks'])
        reports.append({'path': str(path.relative_to(REPO)), 'sha256': sha(path), 'checks': len(report['checks']), 'passed': True, 'normalCleanupPassed': True})
    assert count == 893 and seen == set(table)
    assert outputs == {((800, 600), 1), ((1600, 1200), 2), ((800, 600), 2)}
    roots = ['implementation/elm-focus-recovery-responsive-bounds-v351', str(current.relative_to(REPO)), str(ROOT.relative_to(REPO))]
    files = []
    for name in roots:
        for path in sorted((REPO / name).rglob('*')):
            if path in (ROOT / 'acceptance-manifest.json', OUT / 'report.json'):
                continue
            info = path.lstat()
            row = {'path': str(path.relative_to(REPO)), 'mode': stat.S_IMODE(info.st_mode)}
            if path.is_symlink():
                row['symlink'] = os.readlink(path)
            elif path.is_file():
                row.update(sha256=sha(path), size=info.st_size)
            elif path.is_dir():
                continue
            else:
                raise RuntimeError('Owned special file: ' + str(path))
            files.append(row)
    manifest = {'passed': True, 'component': ROOT.name, 'sourceHeld': True, 'selectedNativeProduction': parent['selectedNativeProduction'], 'freshSameProgramProducer': parent['freshSameProgramProducer'], 'pair': parent['pair'], 'parentManifest': str(parent_path.relative_to(REPO)), 'parentManifestSHA256': sha(parent_path), 'parentScopedNativeChecks': 626, 'responsiveNativeChecks': 893, 'responsiveProfileCount': 22, 'pollingObservationControls': 16, 'failedAttemptPreserved': {'path': str(failure_path.relative_to(REPO)), 'sha256': sha(failure_path), 'checksReached': 293, 'cleanupPassed': True}, 'nativeReports': reports, 'references': references, 'ownedRoots': roots, 'files': files, 'allGeometryContractScenariosAccepted': False, 'currentRendererCohortAccepted': False, 'nativeMixedMultiOriginLossAccepted': False, 'nativeATIMEHardwareBudgetsAccepted': False, 'fullUIUXAccepted': False, 'fullReleaseAccepted': False, 'scope': 'Original22 responsive profiles and893 actual GUI/receipt/ACK/RGB checks on fresh349 byte-identical333. Four single-observation QA predicates only; original production, check identities and deadlines retained. Repeated observation records are not additional profiles. Parent626 and broader release gates remain separate.'}
    with (ROOT / 'acceptance-manifest.json').open('x') as stream:
        stream.write(json.dumps(manifest, indent=2) + '\n')
    result.update(passed=True, files=len(files), responsiveNativeChecks=count, profiles=len(seen), manifestSHA256=sha(ROOT / 'acceptance-manifest.json'))
except Exception as error:
    result.update(error=repr(error), traceback=traceback.format_exc())
(OUT / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'report': str(OUT / 'report.json'), **result}))
raise SystemExit(not result['passed'])

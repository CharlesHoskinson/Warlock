"""Hold actual current renderer recovery, including its original bounded scope."""
import hashlib, json, os, resource, stat, sys, time, traceback
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
    parent = REPO / 'implementation/elm-focus-recovery-responsive-held-v353/acceptance-manifest.json'
    assert sha(parent) == '52578b0f5a9afb2fe8093b350aa602bfa3c9f607ef1dbbd0d73e8bf00bff35d3'
    held = json.loads(parent.read_text())
    assert held['passed'] and held['responsiveNativeChecks'] == 893 and not held['fullReleaseAccepted']
    for row in held['files']:
        path = REPO / row['path']
        assert stat.S_IMODE(path.lstat().st_mode) == row['mode']
        if 'symlink' in row:
            assert path.is_symlink() and os.readlink(path) == row['symlink']
        else:
            assert not path.is_symlink() and sha(path) == row['sha256'] and path.stat().st_size == row['size'], str(path)
    runner = REPO / 'implementation/elm-focus-recovery-renderer-native-v355'
    preflight_path = runner / 'qa/preflight.json'
    preflight = json.loads(preflight_path.read_text())
    assert preflight['passed'] and preflight['originalStaticCheckCalls'] == 33 and preflight['pair'] == held['pair']
    report_path = runner / 'qa/native-1791158504005288650/report.json'
    report = json.loads(report_path.read_text())
    assert report['passed'] and report['cleanupPassed'] and not report['inputChanges']
    assert report['pair'] == held['pair'] and len(report['checks']) == 40 and all(c['passed'] for c in report['checks'])
    assert report['inputs'][str(preflight_path)] == sha(preflight_path)
    for path, digest in {**preflight['inputs'], **report['inputs']}.items():
        assert sha(path) == digest, path
    for name, digest in report['artifacts'].items():
        assert sha(report_path.parent / name) == digest, name
    host = report['privateHost']
    assert not host['mainDisplayUsed'] and host['runtimeGone']
    assert not any(host.get(k) for k in ('cleanupErrors', 'unexpectedInnerDescendants', 'remainingDescendants'))
    starts = report['supervisorEvents']['starts']
    exits = report['supervisorEvents']['exits']
    assert len(starts) == len(exits) == 2 and starts[0]['pid'] != starts[1]['pid']
    assert exits[0]['exitCode'] == 3 and not exits[0]['forced'] and not exits[0]['stopping']
    assert exits[1]['exitCode'] == 1 and not exits[1]['forced'] and exits[1]['stopping']
    assert report['cohortCleanup'][-1]['remaining'] == []
    producer = REPO / 'implementation/elm-focus-recovery-pinned-toolchain-v349'
    build = producer / 'qa/build-1791156669069885164/report.json'
    assert report['buildReport'] == str(build) and report['buildReportSHA256'] == sha(build)
    cohort = REPO / 'implementation/elm-focus-recovery-renderer-cohort-v354'
    for name in ('cohort.py', 'supervisor.py'):
        assert (cohort / name).read_bytes() == (REPO / 'implementation/elm-responsive-cohort-v296' / name).read_bytes()
    roots = [str(cohort.relative_to(REPO)), str(runner.relative_to(REPO)), str(ROOT.relative_to(REPO))]
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
    manifest = {'passed': True, 'component': ROOT.name, 'sourceHeld': True, 'selectedNativeProduction': held['selectedNativeProduction'], 'freshSameProgramProducer': held['freshSameProgramProducer'], 'pair': held['pair'], 'parentManifest': str(parent.relative_to(REPO)), 'parentManifestSHA256': sha(parent), 'parentScopedNativeChecks': 626, 'responsiveNativeChecks': 893, 'responsiveProfileCount': 22, 'currentRendererCohortNativeChecks': 40, 'currentRendererCohortAccepted': True, 'nativeReport': {'path': str(report_path.relative_to(REPO)), 'sha256': sha(report_path), 'checks': 40, 'normalCleanupPassed': True}, 'ownedRoots': roots, 'files': files, 'allGeometryContractScenariosAccepted': False, 'nativeMixedMultiOriginLossAccepted': False, 'nativeArchiveScalingAccepted': False, 'nativeATIMEHardwareBudgetsAccepted': False, 'fullUIUXAccepted': False, 'fullReleaseAccepted': False, 'scope': 'Original183/297 bounded40 renderer/cohort fault-restart-cancel campaign on actual349 byte-identical333 and owning205/594/AQ155. Real applications/input/geometry preserved, explicit native Restart and second failure cancellation. Old packet refusal is local endpoint binding evidence; server grant retirement and uncertain-operation proofs remain separately held in350. Counts are separate scoped campaigns, not a full release score.'}
    with (ROOT / 'acceptance-manifest.json').open('x') as stream:
        stream.write(json.dumps(manifest, indent=2) + '\n')
    result.update(passed=True, files=len(files), rendererCohortNativeChecks=40, manifestSHA256=sha(ROOT / 'acceptance-manifest.json'))
except Exception as error:
    result.update(error=repr(error), traceback=traceback.format_exc())
(OUT / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'report': str(OUT / 'report.json'), **result}))
raise SystemExit(not result['passed'])

"""Verify actual native lost-result journeys and their durable source closure."""
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
encoded = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
result = {'passed': False, 'fullReleaseAccepted': False}
try:
    parent = REPO / 'implementation/elm-focus-recovery-lost-actions-held-v359/acceptance-manifest.json'
    assert sha(parent) == '201084c3347018c31e6cf84546e9ab649f216909f2da9281e2c9574df24a4694'
    held = json.loads(parent.read_text())
    assert held['passed'] and held['lostMinimizeNativeChecks'] == 61 and held['lostRestoreNativeChecks'] == 63 and not held['fullReleaseAccepted']
    for row in held['files']:
        path = REPO / row['path']
        assert stat.S_IMODE(path.lstat().st_mode) == row['mode']
        if 'symlink' in row:
            assert path.is_symlink() and os.readlink(path) == row['symlink']
        else:
            assert not path.is_symlink() and sha(path) == row['sha256'] and path.stat().st_size == row['size'], str(path)
    campaigns = []
    roots = []
    for number, operation, checks in [(360, 'minimize', 61), (361, 'restore', 63)]:
        root = REPO / 'implementation' / ('elm-focus-recovery-' + operation + '-unread-v' + str(number))
        roots.append(str(root.relative_to(REPO)))
        paths = list((root / 'qa').glob('native-*/report.json'))
        assert len(paths) == 1
        path = paths[0]
        report = json.loads(path.read_text())
        preflight_path = root / 'qa/preflight.json'
        preflight = json.loads(preflight_path.read_text())
        assert preflight['passed'] and preflight['originalStaticCheckCalls'] == 52 and preflight['additiveStaticCheckCalls'] == 2
        assert report['passed'] and report['cleanupPassed'] and report['pair'] == held['pair'] and report['operation'] == operation and report['faultBoundary'] == 'unread'
        assert len(report['checks']) == checks and all(c['passed'] for c in report['checks'])
        assert report['inputs'][str(preflight_path)] == sha(preflight_path)
        for name, digest in {**preflight['inputs'], **report['inputs']}.items():
            assert sha(name) == digest, name
        for name, digest in report['artifacts'].items():
            assert sha(path.parent / name) == digest, name
        host = report['privateHost']
        assert not host['mainDisplayUsed'] and host['runtimeGone'] and not any(host.get(k) for k in ('cleanupErrors', 'remainingDescendants', 'unexpectedInnerDescendants'))
        marker = report['operationFaultMarker']
        assert marker['stage'] == 'after-durable-admission-and-publication-before-broker-write' and marker['request']['kind'] == 'window-effect'
        assert marker['hostPID'] == report['supervisorEvents']['starts'][0]['pid']
        release = report['retirementRelease']
        wire, historical, certificate = release['wire'], release['historical'], release['certificate']
        assert wire['record'] == historical['record'] == certificate['record']
        record = wire['record']
        assert record['status'] == 'Unknown' and record['intent'] == marker['request']['intent'] and record['binding'] == marker['request']['binding'] and record['intent']['operation'] == operation
        assert historical['phase'] == 'Released' and certificate['anchorId'] == historical['id']
        assert wire['release'] == {k: certificate[k] for k in ('id', 'proof', 'observation')}
        payload = {k: historical[k] for k in ('record', 'proof', 'observation')}
        assert historical['id'] == hashlib.sha256(encoded(payload)).hexdigest()
        payload = {k: certificate[k] for k in ('record', 'proof', 'observation', 'anchorId')}
        assert certificate['id'] == hashlib.sha256(encoded(payload)).hexdigest()
        recovery = report['recovery']
        assert certificate['proof']['binding'] == recovery['freshBinding'] and certificate['proof']['queriedBinding'] == recovery['oldBinding'] == record['binding']
        assert certificate['proof']['grantState'] == 'Retired' and recovery['oldHostExit'] == 3
        starts, exits = report['supervisorEvents']['starts'], report['supervisorEvents']['exits']
        assert len(starts) == len(exits) == 2 and starts[0]['pid'] != starts[1]['pid']
        assert exits[0]['exitCode'] == 3 and not exits[0]['forced'] and not exits[0]['stopping']
        assert exits[1]['exitCode'] == 1 and not exits[1]['forced'] and exits[1]['stopping']
        assert report['cohortCleanup'][-1]['remaining'] == []
        build = REPO / 'implementation/elm-focus-recovery-pinned-toolchain-v349/qa/build-1791156669069885164/report.json'
        assert report['buildReport'] == str(build) and report['buildReportSHA256'] == sha(build)
        pixel_checks = [c for c in report['checks'] if c['name'].endswith('ActualApplicationPixelsMatchNativeMinimized')]
        assert len(pixel_checks) == 6 and all(c['passed'] for c in pixel_checks)
        initial_minimized = operation == 'restore'
        assert all(c['minimized'] == initial_minimized for c in pixel_checks if c['name'].split('ActualApplicationPixels')[0] in ['beforeFault', 'atInterruption', 'nativeFallback', 'replacementUnknown'])
        assert all(c['minimized'] != initial_minimized for c in pixel_checks if c['name'].split('ActualApplicationPixels')[0] in ['explicitAction', 'finalFallback'])
        campaigns.append({'path': str(path.relative_to(REPO)), 'sha256': sha(path), 'operation': operation, 'checks': checks, 'actualPixelStages': len(pixel_checks), 'passed': True, 'normalCleanupPassed': True})
    roots.append(str(ROOT.relative_to(REPO)))
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
    manifest = {'passed': True, 'component': ROOT.name, 'sourceHeld': True, 'selectedNativeProduction': held['selectedNativeProduction'], 'freshSameProgramProducer': held['freshSameProgramProducer'], 'pair': held['pair'], 'parentManifest': str(parent.relative_to(REPO)), 'parentManifestSHA256': sha(parent), 'parentScopedNativeChecks': 626, 'responsiveNativeChecks': 893, 'responsiveProfileCount': 22, 'parentRendererCohortNativeChecks': 40, 'parentLostMinimizeNativeChecks': 61, 'parentLostRestoreNativeChecks': 63, 'unreadMinimizeNativeChecks': 61, 'unreadRestoreNativeChecks': 63, 'singleOriginUnreadAdmissionRendererRestartAccepted': True, 'nativeCampaigns': campaigns, 'ownedRoots': roots, 'files': files, 'allGeometryContractScenariosAccepted': False, 'nativeMixedMultiOriginLossAccepted': False, 'nativeArchiveScalingAccepted': False, 'fullPreviewRestoreTimingAccepted': False, 'nativeATIMEHardwareBudgetsAccepted': False, 'fullUIUXAccepted': False, 'fullReleaseAccepted': False, 'scope': 'Original243/244 actual C-admitted minimize/restore held before broker write/read and renderer restart journeys on current349(same333)/owning205594AQ155: actual pixels/native minimized state/input stay unchanged until fresh explicit action; six pixel/input stages per campaign, historical Unknown retained, native retirement/read/durable release, no replay, normal second-failure cancellation. Single origin only; previews, canonical atomic motion/restore timing and broader release gates remain open.'}
    with (ROOT / 'acceptance-manifest.json').open('x') as stream:
        stream.write(json.dumps(manifest, indent=2) + '\n')
    result.update(passed=True, files=len(files), unreadAdmissionNativeChecks=124, actualPixelStages=12, manifestSHA256=sha(ROOT / 'acceptance-manifest.json'))
except Exception as error:
    result.update(error=repr(error), traceback=traceback.format_exc())
(OUT / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'report': str(OUT / 'report.json'), **result}))
raise SystemExit(not result['passed'])

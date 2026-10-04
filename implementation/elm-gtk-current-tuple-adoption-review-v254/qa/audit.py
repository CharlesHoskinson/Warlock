import hashlib, json, resource, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
repo = r.parents[1]
b = r.parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
external = {}
def read(p):
    p = Path(p)
    external[str(p)] = {'sha256': sha(p), 'size': p.stat().st_size}
    return json.loads(p.read_text())
current = read(b / 'elm-keyboardless-current-acceptance-v222/acceptance-manifest.json')
assert current['acceptedGuiNativeCheckCount'] == 473 and current['boundedNativeAcceptance'] and not current['toolkitNativeAcceptance']
assert current['gui'] == 'implementation/elm-stable-surface-publication-v521'
checks = 0
for row in current['reports']:
    p = repo / row['path']
    assert sha(p) == row['sha256']
    v = read(p)
    assert v['passed'] and len(v['checks']) == row['checks']
    checks += len(v['checks'])
assert checks == 473
des = read(b / 'elm-keyboardless-focus-owning-pair-v206/native-build-report.json')
core = read(des['buildReport'])
assert des['sha256'] == sha(des['binary']) == current['nativePair']['core']['sha256']
external[des['binary']] = {'sha256': des['sha256'], 'size': Path(des['binary']).stat().st_size}
assert core['unchangedArchiveMembers'] == 432 and list(core['rebuiltArchiveMembers']) == ['SeatManager.cpp.o']
assert core['existingPublicHeadersUnchanged'] and core['geometryAndReloadArchivePayloadsPreserved']
assert core['exportClosure']['candidateCount'] == core['exportClosure']['ancestorCount'] == 13412 and core['exportClosure']['missingSymbols'] == []
new = read(b / 'elm-keyboardless-toolkit-owning-observer-v223/component-manifest.json')
old = read(b / 'elm-toolkit-popup-canonical-observer-v246/component-manifest.json')
newbuild, oldbuild = read(new['buildReport']), read(old['buildReport'])
assert newbuild['core']['sha256'] == des['sha256']
assert len(newbuild['owningHeaders']) == 694 and newbuild['owningHeaders'] == oldbuild['owningHeaders']
assert newbuild['missingSymbols'] == [] and newbuild['strongUndefinedCount'] == 121
assert newbuild['binarySHA256'] == oldbuild['binarySHA256'] == sha(newbuild['binary']) == sha(oldbuild['binary'])
for name in ['elm-keyboardless-toolkit-owning-observer-v223', 'elm-toolkit-popup-canonical-observer-v246']:
    p = b / name / 'native/observer.cpp'
    external[str(p)] = {'sha256': sha(p), 'size': p.stat().st_size}
assert (b / 'elm-keyboardless-toolkit-owning-observer-v223/native/observer.cpp').read_bytes() == (b / 'elm-toolkit-popup-canonical-observer-v246/native/observer.cpp').read_bytes()
for name in ['elm-gtk-role-canonical-runtime-v244', 'elm-parent-keyboard-canonical-observer-v247']:
    v = read(b / name / 'component-manifest.json')
    assert v['sourceHeld']
parent = read(b / 'elm-keyboardless-current-runtime-v216/parent-probe-build.json')
assert 'elm-shared-held-context-fixture-v170' in parent['buildReport']
gtkparent = read(b / 'elm-parent-keyboard-canonical-observer-v247/parent-probe-build-report.json')
assert parent['buildReport'] != gtkparent['buildReport']
for p in [b / 'elm-keyboardless-current-runtime-v216/candidate_host.py', b / 'elm-gtk-role-native-v238/runtime/candidate_host.py']:
    external[str(p)] = {'sha256': sha(p), 'size': p.stat().st_size}
assert (b / 'elm-keyboardless-current-runtime-v216/candidate_host.py').read_bytes() == (b / 'elm-gtk-role-native-v238/runtime/candidate_host.py').read_bytes()
loop = repo / 'docs/elm-roadmap/delivery/loop-state.json'
(r / 'observed-loop-state.json').write_bytes(loop.read_bytes())
out = r / 'qa' / ('audit-' + str(time.time_ns()))
out.mkdir()
v = {'passed': True, 'nativeAcceptance': False, 'scope': 'Current tuple adoption compatibility and retained evidence audit only', 'currentGuiChecks': checks, 'owningObserverAlreadyRebuilt': True, 'owningHeaders': 694, 'observerStrongSymbols': 121, 'observerBinaryByteIdentical': True, 'coreUnchangedMembers': 432, 'coreExportCount': 13412, 'currentParentFixtureDiffersFromGtk247': True, 'externalFiles': external}
(out / 'report.json').write_text(json.dumps(v, indent=2) + '\n')
print(str(out / 'report.json'))

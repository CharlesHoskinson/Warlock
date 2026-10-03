#!/usr/bin/python3
"""Review the applied restore candidate and complete recorded proof coverage."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, os, re, stat
QA=Path('/home/hoskinson/window-integration-qa')
H=QA/'restore-focus-v28-source-handoff-v1.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(H)=='1044bb960dabd193ee4b5144df104e463400ac7ba5fbe0afa8d1cd32efe08dc6'
h=json.loads(H.read_bytes());B=Path(h['candidate']);ready=Path(h['sourceReady'])
assert sha(ready)==h['sourceReadySHA256']=='42244ab87cc002e8e60eb5f26f4f505c47ca93a40554b8c0d48fe576a7824d95'
spec=importlib.util.spec_from_file_location('reviewed_v28_freezer',h['freezer']);freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
packet=json.loads(ready.read_bytes());freezer.verify(packet)
for path,key in [(freezer.BASE,'links'),(freezer.B13,'symlinks')]:
    ancestor=json.loads(path.read_bytes())
    for field in ['inputs','inputModes']:assert all(packet[field].get(k)==v for k,v in ancestor[field].items())
    assert all(packet['links'].get(k)==v for k,v in ancestor[key].items())
proof=json.loads(Path(h['proof']).read_bytes());assert sha(h['proof'])==h['proofSHA256']=='4dd9122a3618037d8246289354352989da99a324af32f141ec5dc7e8f2009a65'
for mapping in [proof['sources'],proof['inputs']]:
    for path,w in mapping.items():assert sha(path)==w['sha256'] and stat.S_IMODE(Path(path).stat().st_mode)==w['mode'],path
text=Path(proof['CPULog']).read_text();actual={name+'.'+method:status for method,name,status in re.findall(r'^(test\S+) \(([^)]+)\) \.\.\. (.*)$',text,re.M)}
assert actual==proof['perTestResults'] and len(actual)==444 and all(v=='ok' for v in actual.values())
assert 'Ran 444 tests' in text and text.rstrip().endswith('OK')
# The reviewed driver creates check001 only after subprocess.run returned zero
# and the CPU-log error predicate passed. Whole scope later exits143, retained.
assert (Path(proof['CPULog']).parent/'check-001.log').exists()
for old,w in proof['formalDependencyMap'].items():
    current=Path(w['selectedCurrent']);assert sha(old)==sha(current)==w['sha256']
    assert stat.S_IMODE(current.stat().st_mode)==w['mode']
for row in proof['formalChecks']:assert row['exitCode']==0 and sha(row['log'])==row['sha256']
assert (proof['originalPythonTests'],proof['newActualCandidateTransactionTests'],proof['retainedOriginalQuintNamedScenarios'],proof['retainedOriginalQuintModels'],proof['newFinalTransactionQuintNamedScenarios'])==(424,20,435,37,45)
assert proof['allModelsNewlyRun'] is False and proof['stoppedSupersededDriver']['exitCode']==143
old=B.with_name('service-restore-planning-v27')
for name in ['native_desktop.py','owned_commands.py','scene_controller.py']:
    assert (B/name).read_bytes()==(QA/'restore-focus-transaction-design-v6/intended'/(name+'.proposed')).read_bytes()
fixture=(B/'fixture_restore_planning.py').read_text()
selection='    # Explicit legacy CPU route retains six real jobs and three refreshes.\n    apply_destinations=None\n    refresh_destinations=None\n'
assert fixture.count(selection)==1 and fixture.replace(selection,'')==(old/'fixture_restore_planning.py').read_text()
assert (B/'test_restore_planning.py').read_bytes()==(old/'test_restore_planning.py').read_bytes()
out=QA/'restore-focus-v28-root-source-review-v1.json'
row=dict(schema='root-restore-focus-v28-source-review-v1',observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    handoffSHA256=sha(H),sourceReadySHA256=sha(ready),files=len(packet['inputs']),links=len(packet['links']),
    completeV27AndB13AncestorsConserved=True,exactApprovedThreeProductFiles=True,legacyFixtureWholeInverse=True,
    actualCPUTests=444,originalCPUTests=424,newCurrentModuleTests=20,CPUZeroReturnInferredFromReviewedDriverNextLog=True,
    supersededDriverExitCode=143,retainedOriginalModelProofs=37,retainedOriginalNamed=435,newModelNamed=45,newModelSamples=2000,
    allModelsNewlyRun=False,reviewed='Complete applied source/durable chain, source freezer, proof composer/driver, original fixture inverse and actual CPU/model dependency records.',
    approved='Freeze exact source-ready then mechanically prepare unprofiled original38 baseline collector for root review.',nativeExecuted=False,baseline38Accepted=False,recovery34Accepted=False,mainChanged=False)
raw=(json.dumps(row,indent=2)+'\n').encode();fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
print(json.dumps(dict(result='pass',reviewSHA256=hashlib.sha256(raw).hexdigest(),files=len(packet['inputs']),links=len(packet['links']),cpu=444)))

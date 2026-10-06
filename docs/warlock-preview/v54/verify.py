"""Preserve original S09 identities and pin concrete next fallback defects."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2];OUT=ROOT/('verify-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
oldPath=REPO/'docs/warlock-preview/v52/S09-EVIDENCE-PLAN.json';old=json.loads(oldPath.read_text());planPath=ROOT/'S09-EVIDENCE-PLAN.json';p=json.loads(planPath.read_text())
assert [x['scenarioId'] for x in p['scenarios']]==[x['scenarioId'] for x in old['scenarios']] and len(p['scenarios'])==13
assert all(x['status']=='partial-unaccepted' for x in p['scenarios']) and not p['S09Accepted'] and not p['fullReleaseAccepted']
for key in ['originalRequirements','originalScenarioCount']:assert p[key]==old[key]
reqPath=REPO/'docs/elm-roadmap/requirements.json';requirements=json.loads(reqPath.read_text())['requirements'];assert len(requirements)==242 and sum(len(x['scenarios']) for x in requirements)==417
packetPath=REPO/'docs/warlock-preview/v53/report.json';packet=json.loads(packetPath.read_text());assert packet['passed'] and packet['nativeAddressReuseFullGUIQualified'] and not packet['S09Accepted']
nativePath=REPO/'implementation/warlock-client-provider-native-v92/qa/native-1791288138505615354/report.json';native=json.loads(nativePath.read_text());assert native['passed'] and native['cleanupPassed'] and native['nativeAddressReuseFullGUIQualified'] and len(native['checks'])==2363 and all(x['exitCode']==0 for x in native['ownedExitCodes'])
row=next(x for x in p['scenarios'] if x['scenarioId']=='ELM-REN-004 ren-004')
for name in row['boundedPassingNativeControls']:assert any(x['name']==name and x['passed'] for x in native['checks']),name
findingsPath=ROOT/'FALLBACK-SOURCE-FINDINGS.json';f=json.loads(findingsPath.read_text());assert f['scenarioId']=='ELM-UX-007 ux-007' and not f['actualIconURIHandlerImplemented']
inputs={str(x):sha(x) for x in [Path(__file__),oldPath,planPath,packetPath,nativePath,findingsPath,reqPath]}
for x in f['findings']:
 file=REPO/x['path'];assert sha(file)==x['sha256'];lines=file.read_text().splitlines();assert all(x['finding'] in lines[i-1] for i in x['lines']);inputs[str(file)]=sha(file)
report={'passed':True,'scope':scope,'inputs':inputs,'originalRequirements':9,'originalS09ScenarioIds':13,'frozenBaseline':[242,417],'actualNativeAddressReuseMapped':True,'fallbackDefectsSourceVerified':4,'nativeAcceptance':False,'S09Accepted':False,'fullReleaseAccepted':False,'nextExecutableSlice':p['nextExecutableSlice']}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')

"""Rebind retained 1011 controls to compiled popup observer and selected projections."""
import hashlib,json,pathlib,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('prepare-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 parent=REPO/'implementation/warlock-client-provider-native-v31';old=parent/'qa/preflight.json';pre=json.loads(old.read_text());assert pre['passed']
 for p,h in pre['inputs'].items():assert sha(p)==h,p
 inputs=dict(pre['inputs']);inputs[str(old)]=sha(old)
 baseline=parent/'qa/native-1791256379960337558/report.json';accepted=json.loads(baseline.read_text());assert accepted['passed'] and accepted['cleanupPassed'] and len(accepted['checks'])==1160 and len(accepted['ownedExitCodes'])==122 and all(row['exitCode']==0 for row in accepted['ownedExitCodes'])
 for rel,h in accepted['artifacts'].items():assert sha(baseline.parent/rel)==h,rel
 inputs[str(baseline)]=sha(baseline);pre['retainedPopupCaptureReport']=str(baseline)
 owner=REPO/'implementation/warlock-popup-capture-v1';descriptor=owner/'native-build-report.json';pair=json.loads(descriptor.read_text());assert pair['result']=='pass' and sha(pair['binary'])==pair['sha256'] and sha(pair['plugin']['path'])==pair['plugin']['sha256']
 assert pair['sha256']==pre['pair']['core']['sha256'] and sha(ROOT/'native-build-report.json')==sha(descriptor)
 build=pathlib.Path(pair['pluginBuildReport']);assert sha(build)==pair['pluginBuildReportSHA256'];compiled=json.loads(build.read_text());assert compiled['passed']
 closure=pathlib.Path(pair['linkClosureReport']);assert sha(closure)==pair['linkClosureReportSHA256'];linked=json.loads(closure.read_text());assert not linked['missingSymbols']
 for rel,h in compiled['inputs'].items():assert sha(owner/rel)==h,rel;inputs[str(owner/rel)]=h
 for p in [descriptor,build,closure,pathlib.Path(pair['plugin']['path']),*owner.joinpath('native').glob('*'),*owner.joinpath('candidate').glob('*'),*ROOT.glob('*'),*ROOT.joinpath('qa').glob('*.py')]:
  if p.is_file():inputs[str(p)]=sha(p)
 model=REPO/'implementation/warlock-popup-revision-model-v2';pointer=model/'qa/model-report.json';mp=json.loads(pointer.read_text());report=pathlib.Path(mp['path']);assert sha(report)==mp['sha256'];proof=json.loads(report.read_text());assert proof['passed'] and len(proof['traces'])==5 and len(proof['implementationReplay'])==5
 for p,h in proof['inputs'].items():assert sha(p)==h,p;inputs[p]=h
 for rel,h in proof['artifacts'].items():assert sha(report.parent/rel)==h,rel;inputs[str(report.parent/rel)]=h
 inputs[str(pointer)]=sha(pointer);inputs[str(report)]=sha(report)
 pre['popupTraces']={p:h for p,h in proof['traces'].items() if 'malformedRefusalTest' not in p};assert len(pre['popupTraces'])==4
 fd=REPO/'implementation/warlock-popup-fd-qualification-v1';fp=fd/'qa/test-report.json';fdPointer=json.loads(fp.read_text());fr=pathlib.Path(fdPointer['path']);assert sha(fr)==fdPointer['sha256'];fdProof=json.loads(fr.read_text());assert fdProof['passed'] and fdProof['evidence']['physicalFDClosed'] and fdProof['evidence']['physicalMappingClosed']
 for p,h in fdProof['inputs'].items():assert sha(p)==h,p;inputs[p]=h
 for rel,h in fdProof['artifacts'].items():assert sha(fr.parent/rel)==h,rel;inputs[str(fr.parent/rel)]=h
 inputs[str(fp)]=sha(fp);inputs[str(fr)]=sha(fr);pre['popupFDReport']=str(fr)
 fixture=REPO/'implementation/warlock-family-modal-fixture-v1';reports=list(fixture.glob('qa/client-build-*/report.json'));assert len(reports)==1;fixtureReport=reports[0];fb=json.loads(fixtureReport.read_text());assert fb['passed'] and sha(fb['client'])==fb['clientSHA256']
 for key in ['inputs','tools','dependencies','linkedLibraries']:
  for p,h in fb[key].items():assert sha(p)==h,p;inputs[p]=h
 for rel,h in fb['artifacts'].items():assert sha(fixtureReport.parent/rel)==h,rel;inputs[str(fixtureReport.parent/rel)]=h
 inputs[str(fixtureReport)]=sha(fixtureReport);pre['fixtureClient']=fb['client'];pre['modalFixtureReport']=str(fixtureReport)
 import shlex,subprocess
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','libpng'],text=True));argv=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(ROOT/'modal-pixels.cpp'),*flags,'-o',str(OUT/'modal-pixels')];p=subprocess.run(argv,capture_output=True,text=True,timeout=180);(OUT/'modal-compile.stdout').write_text(p.stdout);(OUT/'modal-compile.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
 inputs[str(ROOT/'modal-pixels.cpp')]=sha(ROOT/'modal-pixels.cpp');inputs[str(OUT/'modal-pixels')]=sha(OUT/'modal-pixels');pre['modalPixelOracle']=str(OUT/'modal-pixels')
 pre['popupModelReport']=str(report);pre['pair']['plugin']=pair['plugin'];pre['inputs']=inputs
 assert all(sha(p)==h for p,h in inputs.items())
 (ROOT/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n');r.update(passed=True,inputs=inputs,pair=pre['pair'],popupTraces=pre['popupTraces'])
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}),flush=True)
raise SystemExit(not r['passed'])

"""Complete selective V28 union; root alone freezes and launches native baseline."""
import argparse,hashlib,importlib.util,json,os,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-focus-transaction-v28')
BASE=B.with_name('service-restore-planning-v27')/'manifest-restore-planning-v27.json'
BASE_SHA='54857ba311e2862e37037195283cf98b6fba8bb286cb33d32e92685671304e40'
B13=QA/'family-preparation-thumbnail-v13/frozen-inputs.json'
B13_SHA='68a1996ac38b01635b0e91af59cf6c4214f6e4fe165446826f3f076e4b7662bf'
DESIGN=QA/'restore-focus-transaction-design-v6/source-handoff.json'
DESIGN_SHA='0dfcf7ff6c2d94f2b5d2499ef6d8919c7e49b224ad2b63244ea9c7ab46b59f5a'
GRANT=QA/'restore-focus-v6-root-source-application-grant-v1.json'
GRANT_SHA='dafa374ccd6b786d833b45dcf4669f2fcd2ba47ebfc0a15105e62f2d49f4aff3'
PROOF=QA/'restore-focus-v28-complete-proof-v1/report.json'
READY=B/'source-ready-v28.json'
MANIFEST=B/'manifest-restore-focus-transaction-v28.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def closure():
 p=QA/'family-preparation-thumbnail-v10/collector_v9_closure.py'
 if sha(p)!='3ef9b46881587023d642cee353ed84b4bf8de6eb9e264bfbaf1448980e1c0742':raise ValueError('accepted alias guard changed')
 spec=importlib.util.spec_from_file_location('v28_retained_alias',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def verify(p):
 if set(p['inputs'])!=set(p['inputModes']):raise ValueError('byte/mode coverage differs')
 c=closure();c.verify_links(p['links'])
 for name,digest in p['inputs'].items():c.retained_file(name,digest,p['inputModes'][name],p['inputs'],p['inputModes'],p['links'])
 c.verify_links(p['links'])
def inventory():
 inputs={};modes={};links={}
 def merge(name,digest,mode):
  if name in inputs and (inputs[name]!=digest or modes[name]!=mode):raise ValueError('source declaration conflict: '+name)
  inputs[name]=digest;modes[name]=mode
 def add(p,digest=None,mode=None):
  p=Path(p).absolute();actual=sha(p);permissions=stat.S_IMODE(p.stat().st_mode)
  if digest is not None and actual!=digest or mode is not None and permissions!=mode:raise ValueError('selected source changed: '+str(p))
  for alias in (p,*p.parents):
   if alias.is_symlink():
    name=str(alias);target=os.readlink(alias)
    if name in links and links[name]!=target:raise ValueError('source link conflict')
    links[name]=target
  merge(str(p.resolve(strict=True)),actual,permissions);merge(str(p),actual,permissions)
 for path,digest,key in [(BASE,BASE_SHA,'links'),(B13,B13_SHA,'symlinks')]:
  if path.is_symlink() or sha(path)!=digest:raise ValueError('frozen predecessor changed')
  row=json.loads(path.read_text());packet={**row,'links':row[key]};verify(packet)
  for name,target in packet['links'].items():
   if name in links and links[name]!=target:raise ValueError('retained link conflict')
   links[name]=target
  for name,digest in packet['inputs'].items():merge(name,digest,packet['inputModes'][name])
  add(path)
 add(DESIGN,DESIGN_SHA);design=json.loads(DESIGN.read_text())
 if design['runtimeApplied'] or design['nativeAcceptance']:raise ValueError('design authority misclassified')
 for path,row in design['inputs'].items():add(path,row['sha256'],row['mode'])
 add(GRANT,GRANT_SHA)
 proof=json.loads(PROOF.read_text())
 if (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['original112CommandCoverage'],proof['allModelsNewlyRun'])!=('pass',444,480,38,True,False):raise ValueError('complete proof absent')
 if len(proof['perTestResults'])!=444 or any(s!='ok' for s in proof['perTestResults'].values()):raise ValueError('actual CPU completion absent')
 for path,row in proof['sources'].items():add(path,row['sha256'],row['mode'])
 for path,row in proof['inputs'].items():add(path,row['sha256'],row['mode'])
 for row in proof['formalChecks']:
  if row['exitCode']:raise ValueError('formal completion failed')
  add(row['log'],row['sha256'])
 add(PROOF)
 provenance=json.loads((Path(__file__).parent/'v27-copy-application.json').read_text());changed=[]
 for name,row in provenance['copied'].items():
  add(BASE.parent/name,row['sha256'],row['mode'])
  if stat.S_IMODE((B/name).stat().st_mode)!=row['mode']:raise ValueError('inherited mode changed')
  if sha(B/name)!=row['sha256']:changed.append(name)
 if sorted(changed)!=['fixture_restore_planning.py','native_desktop.py','owned_commands.py','scene_controller.py']:raise ValueError('unreviewed inherited changes')
 for name in ('native_desktop.py','owned_commands.py','scene_controller.py'):
  proposed=DESIGN.parent/'intended'/(name+'.proposed');add(B/name,sha(proposed));add(proposed)
 for folder in [B,Path(__file__).parent,PROOF.parent,QA/'restore-focus-v28-full-proof-v1',QA/'restore-focus-v28-full-proof-v2',B13.parent/'attempt-baseline-1']:
  for path in folder.rglob('*'):
   if path.is_file() and '__pycache__' not in path.parts and path not in (READY,MANIFEST):add(path)
 for path,digest in [(QA/'thumbnail-v13-root-failure-audit-v1.json','8ab7589677086d9a51830f556a99ac168bb09311dbf0849c9cb5eafb369d562a'),(QA/'thumbnail-v13-agent-causal-replay-v1/report.json','56684adcebe6f8d25dd326c93f34abe28523386514987bf8adc733ca0af7a469')]:add(path,digest)
 row={'version':'restore-focus-transaction-v28-source','baseManifest':str(BASE),'baseManifestSHA256':BASE_SHA,'retainedProfiledB13Manifest':str(B13),'retainedProfiledB13ManifestSHA256':B13_SHA,'sourceDesign':str(DESIGN),'sourceDesignSHA256':DESIGN_SHA,'rootSourceApplicationGrant':str(GRANT),'rootSourceApplicationGrantSHA256':GRANT_SHA,'proof':str(PROOF),'proofSHA256':sha(PROOF),'changedInheritedSources':sorted(changed),'newActualCandidateTests':20,'pythonTests':444,'originalPythonTests':424,'originalModelProofsRetained':37,'newTransactionModelProofs':1,'quintNamedScenarioCoverage':480,'allModelsNewlyRun':False,'legacyFixtureCreditOnly':True,'original38BaselineAccepted':False,'original34FaultsAccepted':False,'nativePerformanceAccepted':False,'nativeAccepted':False,'mainChanged':False,'requestDeadlineSeconds':2,'focusCommandLimitSeconds':2,'thumbnailDeadlineSeconds':1,'housekeepDeadlineSeconds':.6,'futureBaselineObserver':'original-unprofiled','inputs':dict(sorted(inputs.items())),'inputModes':dict(sorted(modes.items())),'links':dict(sorted(links.items()))}
 verify(row);return row
def write(p,row):
 with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True)
 for flag in ('collect','freeze','verify'):g.add_argument('--'+flag,action='store_true')
 args=parser.parse_args()
 if args.verify:row=json.loads(MANIFEST.read_text());verify(row)
 elif args.collect:row=inventory();write(READY,row)
 else:
  ready=json.loads(READY.read_text());verify(ready);row=inventory()
  if row!=ready:raise ValueError('reviewed ready changed')
  row={**row,'sourceReady':str(READY),'sourceReadySHA256':sha(READY)};write(MANIFEST,row)
 print(json.dumps({'result':'pass','inputs':len(row['inputs']),'modes':len(row['inputModes']),'links':len(row['links']),'sourceReady':str(READY),'sourceReadySHA256':sha(READY),'manifest':str(MANIFEST),'nativeAccepted':False}))
if __name__=='__main__':main()

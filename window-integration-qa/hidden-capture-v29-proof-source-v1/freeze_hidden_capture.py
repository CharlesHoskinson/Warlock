"""Selective full union. Agent collects; root alone freezes and launches."""
import argparse,hashlib,importlib.util,json,os,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-hidden-capture-fusion-v29')
BASE=B.with_name('service-restore-focus-transaction-v28')/'manifest-restore-focus-transaction-v28.json'
BASE_SHA='30303eb8b2dac6f3407155d5619e2a828e134b410ce70c141488ed2493e94eb3'
B14=QA/'family-preparation-thumbnail-v14/frozen-inputs.json'
B14_SHA='d0bb8b6e3fc5478509194046667366ca04a6aa96e93ea6018b1c7bed80f5efa6'
DESIGN=QA/'hidden-capture-fusion-design-v2/source-handoff.json'
DESIGN_SHA='b48d14140883f46e40b176f195c2e6ab02b5179956a75079250cf9386bf81cc9'
GRANT=QA/'hidden-capture-fusion-v3-root-application-grant-v1.json'
GRANT_SHA='1d25c005dfc4d82b994f135d521057b124ba393324ed0b6183242b23bfa3451b'
PROOF=QA/'hidden-capture-v29-full-proof-v1/report.json'
READY=B/'source-ready-v29.json';MANIFEST=B/'manifest-hidden-capture-fusion-v29.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def closure():
 path=QA/'family-preparation-thumbnail-v10/collector_v9_closure.py'
 if sha(path)!='3ef9b46881587023d642cee353ed84b4bf8de6eb9e264bfbaf1448980e1c0742':raise ValueError('retained alias verifier changed')
 spec=importlib.util.spec_from_file_location('v29_retained_alias',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def verify(packet):
 if set(packet['inputs'])!=set(packet['inputModes']):raise ValueError('byte/mode inputs differ')
 c=closure();c.verify_links(packet['links'])
 for name,digest in packet['inputs'].items():c.retained_file(name,digest,packet['inputModes'][name],packet['inputs'],packet['inputModes'],packet['links'])
 c.verify_links(packet['links'])
def inventory():
 inputs={};modes={};links={}
 def merge(name,digest,mode):
  if name in inputs and (inputs[name]!=digest or modes[name]!=mode):raise ValueError('conflicting selected source: '+name)
  inputs[name]=digest;modes[name]=mode
 def add(path,digest=None,mode=None):
  path=Path(path).absolute();actual=sha(path);permission=stat.S_IMODE(path.stat().st_mode)
  if digest is not None and digest!=actual or mode is not None and mode!=permission:raise ValueError('selected source changed: '+str(path))
  for alias in (path,*path.parents):
   if alias.is_symlink():
    name=str(alias);target=os.readlink(alias)
    if name in links and links[name]!=target:raise ValueError('link conflict')
    links[name]=target
  merge(str(path),actual,permission);merge(str(path.resolve(strict=True)),actual,permission)
 for path,digest,key in ((BASE,BASE_SHA,'links'),(B14,B14_SHA,'symlinks')):
  if path.is_symlink() or sha(path)!=digest:raise ValueError('frozen predecessor changed')
  packet=json.loads(path.read_text());packet={**packet,'links':packet[key]};verify(packet)
  for name,target in packet['links'].items():
   if name in links and links[name]!=target:raise ValueError('retained link conflict')
   links[name]=target
  for name,digest in packet['inputs'].items():merge(name,digest,packet['inputModes'][name])
  add(path)
 add(DESIGN,DESIGN_SHA);design=json.loads(DESIGN.read_text())
 if design['runtimeApplied'] or design['nativeAccepted']:raise ValueError('proposal authority differs')
 for path,row in design['sources'].items():add(path,row['sha256'],row['mode'])
 add(GRANT,GRANT_SHA);grant=json.loads(GRANT.read_text())
 add(grant['correctedProposedSource'],grant['correctedProposedSourceSHA256'])
 add(QA/'review_hidden_fusion_root_v3.py',grant['rootReviewToolSHA256'])
 add(B/'native_desktop.py',grant['correctedProposedSourceSHA256'])
 correctedpath=QA/'restore-v6-actual-named-correction-v1/report.json';add(correctedpath,'a70e9c06c9f3b455ff8c92b8663cfeedc0460df1a207c930be3591d87e19479b')
 corrected=json.loads(correctedpath.read_text());assert corrected['result']=='pass' and corrected['actualNamedScenarios']==45 and corrected['sourceStable']
 for path,row in corrected['sourceBefore'].items():add(path,row['sha256'],row['mode'])
 add(corrected['log'],corrected['logSHA256']);add(QA/'run_restore_v6_named_correction_v1.py')
 proof=json.loads(PROOF.read_text())
 if (proof['result'],proof['pythonTests'],proof['originalPythonTests'],proof['quintNamedScenarios'],proof['quintModels'])!=('pass',462,444,503,39):raise ValueError('required actual proof absent')
 if not proof['originalAllTestIdentitiesExact'] or not proof['sourceUnchanged'] or not proof['formalChecksRetainedNoRerun']:raise ValueError('required source/coverage proof differs')
 if len(proof['perTestResults'])!=462 or any(row!='ok'for row in proof['perTestResults'].values()):raise ValueError('actual CPU completion differs')
 for mapping in ('sources','inputs'):
  for path,row in proof[mapping].items():add(path,row['sha256'],row['mode'])
 add(proof['log'],proof['logSHA256']);add(PROOF)
 focusedpath=QA/'hidden-capture-v29-focused-proof-v2/report.json';focused=json.loads(focusedpath.read_text())
 assert focused['result']=='pass' and focused['pythonTests']==18 and focused['sourceUnchanged']
 for path,row in focused['sources'].items():add(path,row['sha256'],row['mode'])
 add(focused['log'],focused['logSHA256']);add(focusedpath)
 conservation=json.loads((Path(__file__).parent/'conservation.json').read_text())
 if conservation['result']!='pass' or not conservation['wholeProductInverseExact'] or not conservation['wholeFixtureLiteralInverseExact']:raise ValueError('source conservation absent')
 for row in conservation['rows']:
  add(BASE.parent/row['name'],row['old']['sha256'],row['old']['mode']);add(B/row['name'],row['new']['sha256'],row['new']['mode'])
 for folder in (B,Path(__file__).parent,PROOF.parent,focusedpath.parent,QA/'hidden-capture-v29-focused-proof-v1',QA/'hidden-capture-v29-fixture-schema-epoch-v1',B14.parent/'attempt-baseline-1'):
  for path in folder.rglob('*'):
   if path.is_file() and '__pycache__'not in path.parts and path not in (READY,MANIFEST):add(path)
 for path,digest in ((QA/'thumbnail-v14-root-failure-audit-v1.json','e01aee0d6c5f57f1e4ed80932fb739922cf50eddeeb0e4031864617daa1f5a6e'),(QA/'hidden-capture-fusion-formal-selection-epochs-v1.json','6506002c55fb28ac3633274105f2ea399e7f5873dd471a9135bcb7bfd8b7a349'),(QA/'thumbnail-v14-agent-formal-selection-audit-v1/report.json','4a205f42abeb732677608d895101ca10f3462d394cadc4bdceb2b4feb135c4dd')):add(path,digest)
 row={'version':'hidden-capture-fusion-v29-source','baseManifest':str(BASE),'baseManifestSHA256':BASE_SHA,
  'retainedB14FailedManifest':str(B14),'retainedB14FailedManifestSHA256':B14_SHA,'sourceDesign':str(DESIGN),'sourceDesignSHA256':DESIGN_SHA,
  'rootApplicationGrant':str(GRANT),'rootApplicationGrantSHA256':GRANT_SHA,'proof':str(PROOF),'proofSHA256':sha(PROOF),
  'productChanged':['native_desktop.py'],'fixtureChanged':['test_focus_transaction.py'],'pythonTests':462,'originalPythonTests':444,'newAppliedTests':18,
  'quintNamedScenarios':503,'quintModels':39,'allModelsNewlyRun':False,'originalFalseNamedClaimsRetainedAndCorrected':True,
  'original38BaselineAccepted':False,'original34FaultsAccepted':False,'nativePerformanceAccepted':False,'nativeAccepted':False,'mainChanged':False,
  'requestDeadlineSeconds':2,'focusCommandLimitSeconds':2,'thumbnailDeadlineSeconds':1,'grimDeadlineSeconds':.65,'housekeepDeadlineSeconds':.6,
  'futureBaselineObserver':'original-unprofiled','inputs':dict(sorted(inputs.items())),'inputModes':dict(sorted(modes.items())),'links':dict(sorted(links.items()))}
 verify(row);return row
def write(path,row):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
 for flag in ('collect','freeze','verify'):group.add_argument('--'+flag,action='store_true')
 args=parser.parse_args()
 if args.verify:row=json.loads(MANIFEST.read_text());verify(row)
 elif args.collect:row=inventory();write(READY,row)
 else:
  ready=json.loads(READY.read_text());verify(ready);row=inventory()
  if row!=ready:raise ValueError('reviewed ready changed')
  row={**row,'sourceReady':str(READY),'sourceReadySHA256':sha(READY)};write(MANIFEST,row)
 print(json.dumps({'result':'pass','inputs':len(row['inputs']),'modes':len(row['inputModes']),'links':len(row['links']),'sourceReady':str(READY),'sourceReadySHA256':sha(READY),'manifest':str(MANIFEST),'nativeAccepted':False}))
if __name__=='__main__':main()

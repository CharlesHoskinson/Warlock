"""Freeze exact current GUI521 and corrected compositor composition."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_packet(path,base):
 m=json.loads(path.read_text());assert m['sourceHeld'] and m['evidenceIntegrityPassed']
 files=m['files']
 if isinstance(files,dict):files=[{'path':k,**v} for k,v in files.items()]
 for r in files:
  p=base/r['path'];target=r.get('symlink',r.get('target'))
  if target is not None:assert p.is_symlink() and os.readlink(p)==target
  else:assert sha(p)==r['sha256'],str(p)
 links=m.get('symlinks',[])
 if isinstance(links,dict):links=[{'path':k,'target':v} for k,v in links.items()]
 for r in links:assert (base/r['path']).is_symlink() and os.readlink(base/r['path'])==r['target']
 return m
runtime=REPO/'implementation/elm-keyboardless-current-runtime-v216';pair=json.loads((runtime/'qa/build-pair-manifest.json').read_text());assert pair['passed']
for name,digest in pair['files'].items():assert sha(runtime/name)==digest
parent=REPO/'implementation/elm-keyboardless-focus-bounded-acceptance-v213/acceptance-manifest.json';assert sha(parent)=='83ee65c509e22ca748c1c0cdb4d8804b8b4e9fe332dcd966ddda9393b45fde9c';p=verify_packet(parent,REPO);assert p['nativePair']==pair['nativePair'] and p['acceptedGuiNativeCheckCount']==473
producer=Path(pair['producerEvidence']);assert sha(producer)==pair['producerEvidenceSHA256'];g=verify_packet(producer,REPO);assert g['source']=='implementation/elm-stable-surface-publication-v521' and not g['fullReleaseAccepted'] and not g['pointerRaceCausallyResolved']
source_gate=Path(g['parentManifest']);assert sha(source_gate)==g['parentManifestSHA256'];gate=verify_packet(source_gate,REPO);assert gate['quintNamedScenarios']==8 and gate['quintSamples']==1000 and gate['quintMutantsRejected']==5 and gate['typedCompiledCases']==9 and gate['compiledMutantsRejected']==4
fixture=REPO/'implementation/elm-stable-publication-broker-fixture-v528/component-manifest.json';f=verify_packet(fixture,fixture.parent);assert f['backendRoot']==str(REPO/'implementation/elm-stable-surface-publication-v521/qa/build-1791138800386580258/inputs/adapter')
observer=REPO/'implementation/elm-keyboardless-toolkit-owning-observer-v223/component-manifest.json';o=verify_packet(observer,observer.parent);assert o['compiled'] and not o['nativeAcceptance'];assert sha(o['buildReport'])==o['buildReportSHA256'];ob=json.loads(Path(o['buildReport']).read_text());assert ob['passed'] and not ob['missingSymbols'] and len(ob['owningHeaders'])==694 and ob['core']['sha256']==pair['nativePair']['core']['sha256']
for path,row in o['externalFiles'].items():assert sha(path)==row['sha256']
reports=[]
for name,count in [('elm-keyboardless-current-capability-v217',83),('elm-keyboardless-current-focus-v218',83),('elm-keyboardless-current-geometry-v219',161),('elm-keyboardless-current-reconnect-v220',57),('elm-keyboardless-current-full-menu-v221',89)]:
 paths=list((REPO/'implementation'/name/'qa').glob('native-*/report.json'));assert len(paths)==1
 path=paths[0];m=json.loads(path.read_text());assert m['passed'] and m['cleanupPassed'] and len(m['checks'])==count and all(r['passed'] for r in m['checks']) and not m['mainDesktopActions'] and m['pair']==pair['nativePair']
 assert m['buildReport']==str(REPO/'implementation/elm-stable-surface-publication-v521/qa/build-1791138800386580258/report.json')
 for rel,digest in m['artifacts'].items():assert sha(path.parent/rel)==digest
 reports.append({'path':str(path.relative_to(REPO)),'sha256':sha(path),'passed':True,'checks':count})
files=[]
names=['elm-keyboardless-current-runtime-v216','elm-keyboardless-current-capability-v217','elm-keyboardless-current-focus-v218','elm-keyboardless-current-geometry-v219','elm-keyboardless-current-reconnect-v220','elm-keyboardless-current-full-menu-v221','elm-keyboardless-current-acceptance-v222','elm-keyboardless-toolkit-owning-observer-v223']
for name in names:
 for path in sorted((REPO/'implementation'/name).rglob('*')):
  if path==ROOT/'acceptance-manifest.json':continue
  st=path.lstat();r={'path':str(path.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if path.is_symlink():r['symlink']=os.readlink(path)
  elif path.is_file():r.update(sha256=sha(path),size=st.st_size)
  elif path.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(path))
  files.append(r)
result={'schema':1,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'boundedNativeAcceptance':True,'acceptedGuiNativeCheckCount':473,'nativePair':pair['nativePair'],'gui':'implementation/elm-stable-surface-publication-v521','fixture':'implementation/elm-stable-publication-broker-fixture-v528','observer':'implementation/elm-keyboardless-focus-owning-observer-v207','toolkitObserverCompiled':str(observer),'toolkitObserverCompiledSHA256':sha(observer),'toolkitNativeAcceptance':False,'parentManifest':str(parent),'parentManifestSHA256':sha(parent),'producerManifest':str(producer),'producerManifestSHA256':sha(producer),'reports':reports,'files':files,'pointerRaceCausallyResolved':False,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[],'scope':'Exact Core205/plugin206/AQ155/observer207/GUI521/broker528 original473 actual native checks; observer223 owning toolkit compile only, standalone bounds604 retained in213, full release and GTK01-08 remain open.'}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'actualGuiChecks':473,'manifestSHA256':sha(ROOT/'acceptance-manifest.json')}))

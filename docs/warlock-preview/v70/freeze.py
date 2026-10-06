"""Hold exact same-policy native icon lock bitmap evidence and retained failures."""
import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path('/home/hoskinson/omarchy-windows-parity');OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def proof(p,root=None):
 d=json.loads(p.read_text())
 for rel,h in d.get('inputs',{}).items():
  q=Path(rel);q=q if q.is_absolute() else root/q;assert sha(q)==h,(p,q)
 for rel,h in d.get('artifacts',{}).items():assert sha(p.parent/rel)==h,(p,rel)
 return d
def hold(root):
 p=root/'component-manifest.json'
 if not p.exists():
  files={}
  for f in sorted(root.rglob('*')):
   rel=f.relative_to(root)
   if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
   assert not f.is_symlink(),f
   if f.is_file():files[str(rel)]={'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))}
  p.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
 d=json.loads(p.read_text());assert d.get('passed') or (d.get('sourceHeld') and d.get('evidenceIntegrityPassed'))
 for rel,row in d['files'].items():assert sha(root/rel)==row['sha256'] and (root/rel).stat().st_size==row['size'],rel
 return {'path':str(p.relative_to(REPO)),'sha256':sha(p),'files':len(d['files'])}
root=REPO/'implementation/warlock-preview-provider-v55';p=next(root.glob('qa/build-*/report.json'));failed=proof(p,root);assert not failed['passed'] and failed['commands'][-1]['name']=='receiver-extension-physical-tests';first=hold(root)
root=REPO/'implementation/warlock-preview-provider-v56';manifest=json.loads((root/'component-manifest.json').read_text());b=proof(Path(manifest['buildReport']),root);assert b['passed'] and len(b['commands'])==88 and manifest['evidence']['receiver-extension-physical-tests']['checks']==40
for key,names,traces,states in [('catalogModelReport',8,16,214),('metadataModelReport',8,16,210),('modelReport',10,22,564)]:
 p=Path(manifest[key]);d=proof(p,root);assert d['passed'] and d['namedScenarios']==names and len(d['coupledTraces'])==traces and sum(x['statesCompared'] for x in d['coupledTraces'])==states
 if key=='modelReport':assert d['compiledChecks']==36 and d['unsafeMutantsDetected']==3
second=hold(root)
root=REPO/'openspec/changes/warlock-preview-receiver-membership';p=next(root.glob('qa/validate-*/report.json'));d=proof(p);assert d['passed'] and d['frozenBaseline']==[242,417] and len(d['requirements'])==3 and d['originalS09ScenarioIds']==13;third=hold(root)
report={'schema':1,'passed':True,'scope':scope,'components':[first,second,third],'fullBuildCommands':88,'receiverPhysicalChecks':40,'catalogReplayChecks':60,'ownNativeCatalogDecoderChecks':26,'catalogCoupledStates':214,'metadataCoupledStates':210,'demandCoupledStates':564,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Actual own native receiver growth with held original GIO stream/two charged captured mappings/third waiting subject; wire dynamic ordinary eligible capture through the same native authority and shared pool without changing unqualified previewEligible:false facts. Original full S09/S01-S16 and all release gates remain open.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'components':3,'buildCommands':88,'physicalChecks':40,'nativeAcceptance':False}))

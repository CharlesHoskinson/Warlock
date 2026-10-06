"""Preserve a model typecheck failure and derive a corrected source."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v57';target=repo/'implementation/warlock-preview-provider-v58'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports=list(parent.glob('qa/*-*/report.json'));assert len(reports)==5
for p in reports:
 d=json.loads(p.read_text())
 for rel,h in d['inputs'].items():assert sha(parent/rel)==h,rel
 for rel,h in d.get('artifacts',{}).items():assert sha(p.parent/rel)==h,rel
 if p.parent.name.startswith('delivery-check-'):assert not d['passed'] and d['commands'][-1]['name']=='quint-typecheck'
 else:assert d['passed'],p
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent)
 if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'passed':False,'files':files,'failure':'New Quint projection function omitted annotated return type. Full actual GUI90/physical49/original demand/catalog/metadata passes preserved; model parsing failure retained. Correct in fresh58 with explicit Projection record type. No production guards or native oracles/deadlines change.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not target.exists();shutil.copytree(parent,target,ignore=shutil.ignore_patterns('build-*','check-*','metadata-check-*','catalog-check-*','delivery-check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json','current-build.json'))
p=target/'spec/delivery.qnt';text=p.read_text();old=' pure def projection(st:State)=';assert text.count(old)==1;text=text.replace(old,' type Projection={receiver:bool,readers:int,charge:int,records:int,oldReceipts:int,newReceipts:int}\n pure def projection(st:State):Projection=',1);p.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Preserve failed57 Quint parser evidence. Annotate new receipt projection record return type; no production receiver/job/physical rule, original scenario or deadline changes. Full native acceptance remains pending.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS actual57 fullGUI90/physical49/originaldemand10/catalog8/metadata8 passed; newcoupleddelivery modeltypecheck failed missing return annotation, retained held57. Fresh58 fixes only explicit Projection type; rerun actualfullcompile and selected coupled new/old models, then native owning tuple dynamicgrowth. All prior handles terminal; release/ordinaryeligible stillopen.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))])
print(json.dumps({'heldFiles':len(files),'source':str(target),'checkpoint':str(event)}))

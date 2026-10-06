"""Preserve GUI63 passing build and retained fixture/dependency failures; own GUI64."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v63';target=repo/'implementation/warlock-preview-provider-v64';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bp=next(parent.glob('qa/build-*/report.json'));b=json.loads(bp.read_text());assert b['passed'] and len(b['commands'])==94 and all(x['exitCode']==0 for x in b['commands'])
failed=next(parent.glob('qa/enrollment-check-*/report.json'));f=json.loads(failed.read_text());assert not f['passed'] and f['commands'][-1]['name']=='quint-typecheck' and f['commands'][-1]['exitCode']==1 and 'Trying to infer effect' in f['error']
dependent=list(parent.glob('qa/metadata-check-*/report.json'))+list(parent.glob('qa/catalog-check-*/report.json'));assert len(dependent)==2 and all(not json.loads(p.read_text())['passed'] and 'IndexError' in json.loads(p.read_text())['error'] for p in dependent)
for report in [bp,failed,*dependent]:
 data=json.loads(report.read_text())
 for rel,h in data.get('inputs',{}).items():assert sha(parent/rel)==h,rel
 for rel,h in data.get('artifacts',{}).items():assert sha(report.parent/rel)==h,rel
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent)
 if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':False,'sourceHeld':True,'evidenceIntegrityPassed':True,'buildReport':str(bp),'failedEnrollmentReport':str(failed),'files':files,'scope':'Full94 production/C build passes along with actual intent6/demand10/delivery6 checks. New enrollment model typecheck fails on action all inside assert; metadata/catalog launched before required build report existed and refuse IndexError. Preserve all63 failures; fresh64 changes only model Boolean expressions and schedules dependent tests after compiled build. No original oracle/deadline/production guards changed. No native63 qualification or full release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not target.exists()
shutil.copytree(parent,target,ignore=shutil.ignore_patterns('build-*','check-*','metadata-check-*','catalog-check-*','delivery-check-*','intent-check-*','enrollment-check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json','current-build.json'))
p=target/'spec/enrollment_tests.qnt';s=p.read_text();import re
s,n=re.subn(r'assert\(all\{([^}]*)\}\)',lambda m:'assert('+m.group(1).replace(',', ' and ')+')',s);assert n==8;p.write_text(s)
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Preserve63 full94/actual intent6/demand10/delivery6 evidence and failed enrollment model action-effect assertion plus premature metadata/catalog execution. Correct pure Boolean conjunction in eight named model asserts; native production code unchanged. Build-dependent catalog/metadata checks run only after full build terminal. No scenario/oracle/deadline weakening; native acceptance pending.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS63 full94/C controls and old intent6/demand10/delivery6 pass; new8 model typecheck fails action all assertion, and prematurely launched metadata/catalog correctly refuse missing required build report. Preserve held63 and fresh64 model Boolean conjunction fix; production same atomic nativeDemandView/reserveImportedIntent/growingC. Run fullbuild/new8/oldintent+demand+delivery independent, then dependent metadata/catalog only when build report exists. Freeze actual unchanged production tuple, serial native dynamicC same bootstrap/3realwindows/two physicalitems/originaldeadline/physicalcleanup/pixels. Original fullreleaseopen/desktopdraftspreserved''],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]);print(json.dumps({'held':str(manifest),'files':len(files),'source':str(target),'checkpoint':str(event)}))

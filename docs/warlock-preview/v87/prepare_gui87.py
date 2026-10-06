"""Fresh GUI87 for Elm settlement, exact typed facts and ordered retirement controls."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v86';t=r/'implementation/warlock-preview-provider-v87';assert not t.exists()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
build=next(p.glob('qa/build-*/report.json'));b=json.loads(build.read_text());assert b['passed'] and len(b['commands'])==95
actor=next(p.glob('qa/actor-retirement-check-v3-*/report.json'));a=json.loads(actor.read_text());assert a['passed'] and a['evidence'][1]['sequentialSubjects']>256
for data in [b,a]:
 for rel,value in data['inputs'].items():assert sha(p/rel)==value,rel
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentBuild':str(build),'parentBuildSHA256':sha(build),'parentActorChecks':str(actor),'parentActorChecksSHA256':sha(actor),'purpose':'Keep the qualified actual aggregate-native transaction; add exact immutable Elm retirement settlement and explicit per-original-receiver control continuity before host activation. Native and full release remain unaccepted.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),
 ['PROGRESS PUBLIC61 b78826a/receipt72ee067; actualGUI86 full95 and C/native aggregate short+turnover >256 synthetic subjects pass ASan/UBSan with exact producer proof/final journal ACK and live neighbor. Original12/typedC96/selected decoder running63783/72131/64045. Fresh GUI87 implements Elm resource settlement and ordered-control barrier; real compositor/Elm turnover and all original full release gates remain required.'],
 'progress',[str((t/'ANCESTRY.json').relative_to(r))]))

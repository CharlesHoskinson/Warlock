"""Retain75 and its direct-native proofs; correct typed terminal event in fresh76."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v75';t=r/'implementation/warlock-preview-provider-v76';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
build=next(p.glob('qa/build-*/report.json'));assert json.loads(build.read_text())['passed'] and not t.exists()
nativeReports={}
for key,pat in [('modelReport','qa/check-*/report.json'),('deliveryModelReport','qa/delivery-check-*/report.json'),('resumeModelReport','qa/resume-model-check-*/report.json'),('intentModelReport','qa/intent-check-*/report.json'),('enrollmentModelReport','qa/enrollment-check-*/report.json')]:
 q=next(p.glob(pat));d=json.loads(q.read_text());assert d['passed'];nativeReports[key]=str(q)
files={str(f.relative_to(p)):{'sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))} for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
assert not (p/'component-manifest.json').exists()
(p/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'passed':False,'files':files,**nativeReports,'nativeAcceptance':False,'fullReleaseAccepted':False,'buildReport':str(build),'failure':'Preliminary selected feedback trace incorrectly supplied Refused after an actual Close/Cancel. Elm preserves the cancelling job until a Cancelled receipt. Scratch correction passed all21 selected/sampled traces; fresh76 fixes fixture terminal kind only. Native demand/delivery/resume/intent/enrollment model traces newly passed on exact current production75.'},indent=2)+'\n')
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if n.startswith(('build-','check-','delivery-check-','resume-model-check-','intent-check-','enrollment-check-')) or n=='__pycache__']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
f=t/'qa/feedback-replay.js';s=f.read_text();old="event:{kind:'refused',job:known}";assert s.count(old)==1;s=s.replace(old,"event:{kind:state(result).cancelling.length?'cancelled':'refused',job:known}");f.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(p/'component-manifest.json'),'purpose':'Unchanged72–75 fullfeedback production, typed Cancelled proof for original cancellation in newfixture. Retain all failure evidence and exact current direct-native75 model proofs. Current76 fullbuild/feedback/C/Elm then native113 qualification; all original release gates open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS75 full95/newlycurrentnativeModelsdemand10delivery6resume8intent6enrollment8 pass. FeedbacktracecorrecttypedCancelledafterClose passesall21inscratch; fresh76 applyfixonlytoQA. Production72–76native/Elmunchangedandcompiled; full76currentqualificationthenserializednative113. Original fullreleasegatespreserved.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]);print(json.dumps({'source':str(t),'checkpoint':str(e)}))

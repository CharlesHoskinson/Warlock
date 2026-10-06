"""Preserve74 trace mismatch; align close with real monotonic presentation stamps."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v74';t=r/'implementation/warlock-preview-provider-v75';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
failure=next(p.glob('qa/feedback-check-*/report.json'));assert not json.loads(failure.read_text())['passed'] and not t.exists()
for prefix in ['build','resume-check','receipt-check','metadata-check','catalog-check']:
 d=json.loads(next(p.glob('qa/'+prefix+'-*/report.json')).read_text());assert d['passed'],prefix
files={str(f.relative_to(p)):{'sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))} for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
assert not (p/'component-manifest.json').exists()
(p/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'passed':False,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'feedbackReport':str(failure),'failure':'Feedback traces sent a close presentation with unchanged publication/lease; the real Presentation reducer correctly refused contradictory same-stamp body. Fresh75 advances close stamps in projection and fixture; production policy and monotonicity remain unchanged. Full95, guard controls and actual C/Elm capacity/expiry pass, original resume79/receipt/metadata/catalog pass.'},indent=2)+'\n')
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if n.startswith(('build-','feedback-check-','resume-check-','receipt-check-','metadata-check-','catalog-check-')) or n=='__pycache__']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
f=t/'qa/feedback-replay.js';s=f.read_text();old="if(event==='Close'){active=false;result=";assert s.count(old)==1;s=s.replace(old,"if(event==='Close'){active=false;publication++;result=");f.write_text(s)
f=t/'spec/feedback.qnt';s=f.read_text();old='|Close=>{...st,active:false,outcome:"",';assert s.count(old)==1;s=s.replace(old,'|Close=>{...st,active:false,publication:st.publication+1,outcome:"",');f.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(p/'component-manifest.json'),'purpose':'Unchanged native/Elm full feedback production; correct new close trace to real strictly monotonic presentation protocol. Preserve all original tests, deadlines and failures; qualify new native GUI only after current component checks.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS74 full95/feedbackguardactualCElmcapacityexpiry and originalresume79/receipt8metadata8catalog8 passed; new close trace sent contradicting same presentation stamp, preservedfailed74; fresh75 correctmonotonicClose projection/fixture only. NativeGUI111notlaunched, preparatoryscriptreplacefailurepreserved; nextcurrent75checks + fresh112 nativeGUI. All original fullrelease gates active.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]);print(json.dumps({'source':str(t),'checkpoint':str(e)}))

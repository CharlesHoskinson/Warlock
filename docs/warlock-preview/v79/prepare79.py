"""Preserve compiled78 and fix the reviewed new QA artifact-key typo only."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v78';t=r/'implementation/warlock-preview-provider-v79';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
bp=next(p.glob('qa/build-*/report.json'));b=json.loads(bp.read_text());assert b['passed'] and len(b['commands'])==95 and not t.exists()
for rel,h in b['inputs'].items():assert sha(p/rel)==h,rel
assert 'inputs/assets/feedback-replay.js' in b['artifacts'] and 'assets/feedback-replay.js' not in b['artifacts']
files={str(f.relative_to(p)):{'sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))} for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
assert not (p/'component-manifest.json').exists()
(p/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'passed':False,'buildReport':str(bp),'buildPassed':True,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'remaining':'Review found new next-intent-check.py indexes compiled asset as assets/feedback-replay.js while build report uses inputs/assets/feedback-replay.js. That harness has not run. Fresh79 corrects artifact lookup only; native/fullhost/Elm production unchanged.'},indent=2)+'\n')
def ignore(path,names):
 if pathlib.Path(path)==p:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==p/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(p,t,ignore=ignore)
f=t/'qa/next-intent-check.py';s=f.read_text();old="build['artifacts']['assets/feedback-replay.js']";assert s.count(old)==1;s=s.replace(old,"build['artifacts']['inputs/assets/feedback-replay.js']")
s=s.replace(' traces=[]\n',' traces=[];traceInputs={}\n')
old="traces.append({'trace':path.name,'statesCompared':len(actual)})";assert s.count(old)==1
s=s.replace(old,old+";traceInputs[path.name]=('\\n'.join(events)+'\\n',wanted)")
marker=' assert len(traces)==22\n';assert s.count(marker)==1
mutants=""" original=(OUT/'inputs/native/imported_admission.hpp').read_text();caught=[]
 for name,old,new,witness in [('pending-replaced','old.deadline>nativeNow ||','false ||','pendingCannotAdvance'),('lease-replayed','intent.lease<=old.lease)','false)','partialStampRefused')]:
  assert original.count(old)==1;folder=OUT/name;shutil.copytree(OUT/'inputs/native',folder);(folder/'imported_admission.hpp').write_text(original.replace(old,new,1))
  run(name+'-compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-I'+str(folder),str(source),'-o',str(folder/'checks')])
  matches=[key for key in traceInputs if witness in key];assert len(matches)==1;stdin,wanted=traceInputs[matches[0]]
  actual=[json.loads(line) for line in run(name+'-replay',[str(folder/'checks')],input=stdin).splitlines()]
  assert actual!=wanted,'Unsafe successor mutation escaped';caught.append({'name':name,'trace':matches[0],'differentObservableState':True})
 report['mutants']=caught;report['unsafeMutantsDetected']=len(caught)
"""
s=s.replace(marker,marker+mutants);f.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(p/'component-manifest.json'),'purpose':'Unchanged full78 successor production, reviewed QA compiled asset key corrected before first selected successor test. Original full95 and failed77 cache preparation retained. Native/fullrelease acceptance remain open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS78 currentfull95 passed; reviewnewQAartifactkeytypo foundbeforefirstsuccessortest. Fresh79 correctlookup only, preservecompiled78 unchangedproduction. Next current79fullbuild/nativeCElm10modelcases and originalregressions then serializednative qualification; fulloriginalgatesactive.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]))

import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('warp-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def body(t,marker):
 start=t.index(marker);a=t.index('{',start);b=a+1;depth=1
 while depth:depth+=(t[b]=='{')-(t[b]=='}');b+=1
 return t[start:b]
source=ROOT/'candidate/src/pointer/PointerManager.cpp';old=ROOT.parent/'elm-core-parent-hit-test-v72/candidate/src/pointer/PointerManager.cpp';template=ROOT/'qa/warp-template.cpp'
r={'passed':False,'nativeAcceptance':False,'scope':'Actual new parent warp helper and prior listener body, real Hyprutils weak/shared pointers with typed normal InputManager floor-dedup/policy fixture; native transport separate','inputs':{str(p):sha(p) for p in [source,old,template,Path(__file__),ROOT/'candidate/src/pointer/ParentNormalizedPosition.hpp']},'commands':[]}
def run(name,cmd,expected):
 p=subprocess.run(cmd,capture_output=True,timeout=90);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,p.stderr.decode(errors='replace');return p
try:
 t=source.read_text();state=body(t,'struct ParentPointerPosition {')+';';helper=body(t,'bool dispatchParentWarp(');assert 'if (!dispatchParentWarp(weak, parentPosition, event)) return;' in t
 original=old.read_text();start=original.index('            const auto device = weak.lock();',original.index('listener->motionAbsolute = aqPointer->events.warp.listen'));end=original.index('            PROTO::idle->onActivity();',start)
 prior='bool dispatchParentWarp(const WP<IPointer>& weak, const std::shared_ptr<ParentPointerPosition>& parentPosition, const Aquamarine::IPointer::SWarpEvent& event) {\n'+original[start:end].replace('clear(); return;','clear(); return false;')+'\nreturn true;\n}'
 mutations=[('missing-refresh',helper.replace('if (newSource)','if (newSource && false)')),('ordinary-focus-steal',helper.replace('if (newSource)','if (newSource || true)')),('output-identity',helper.replace(' || parentPosition->output != output','')),('inactive-parent',helper.replace('Aquamarine::parentPointerInputStatus(source.get(), output.get()) != Aquamarine::ParentInputStatus::Ready','false')),('shutdown',helper.replace('g_pCompositor->m_isShuttingDown || ',''))]
 flags=['/usr/bin/c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-I'+str(ROOT/'candidate/src/pointer')]
 for name,h in [('original',prior),('candidate',helper),*mutations]:
  assert name=='original' or name=='candidate' or h!=helper
  cpp=OUT/(name+'.cpp');cpp.write_text(template.read_text().replace('@@STATE@@',state).replace('@@HELPER@@',h));exe=OUT/name
  run(name+'-compile',[*flags,str(cpp),'-lhyprutils','-o',str(exe)],0);p=run(name+'-run',[str(exe)],0 if name=='candidate' else 1)
  if name=='original':assert b'FAIL stationary first source gets focus' in p.stderr
  if name=='candidate':r['checks']=int(p.stdout.decode().split('checks: ')[1])
 r.update(passed=True,mutantsRejected=len(mutations),originalStationaryFailureReproduced=True)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

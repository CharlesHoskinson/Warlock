import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir()
source=ROOT/'candidate/src/pointer/PointerManager.cpp';template=ROOT/'qa/template2.cpp'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def body(text,marker):
 start=text.index(marker);a=text.index('{',start);b=a+1;depth=1
 while depth:depth+=(text[b]=='{')-(text[b]=='}');b+=1
 return text[start:b]
r={'passed':False,'nativeAcceptance':False,'scope':'Actual deferred hit-test helper with typed weak ownership, event-loop, monitor/query and InputManager mocks; native routing excluded','inputs':{str(p):sha(p) for p in [source,template,Path(__file__),ROOT/'candidate/src/desktop/view/Window.cpp',ROOT/'candidate/src/pointer/ParentPointerFocus.hpp']},'commands':[]}
def run(name,cmd,expected=0):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=60);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'command':cmd,'exitCode':p.returncode,'expected':expected});assert p.returncode==expected,p.stderr or p.stdout;return p.stdout
try:
 shutil.copy2(__file__,OUT/'test.py');text=source.read_text();helper=body(text,'void scheduleParentHitTest(')
 layout=body(text,'void CPointerManager::onMonitorLayoutChange()');assert layout.rstrip().endswith('scheduleParentHitTest(this);\n}')
 (OUT/'extracted-helper.cpp').write_text(helper)
 wrapper=body(text,'void Pointer::refreshParentHitTest()');window=body((ROOT/'candidate/src/desktop/view/Window.cpp').read_text(),'void CWindow::commitWindow()');assert window.rstrip().endswith('Pointer::refreshParentHitTest();\n}')
 cpp=template.read_text().replace('// PRODUCTION_HELPER',helper+'\n'+wrapper);(OUT/'test.cpp').write_text(cpp)
 flags=['c++','-I'+str(ROOT/'candidate/src/pointer'),'-std=c++23','-O2','-Wall','-Wextra','-Werror']
 run('compile',[*flags,str(OUT/'test.cpp'),'-o',str(OUT/'test')]);r['checks']=int(run('test',[str(OUT/'test')]).split('checks: ')[1])
 mutants=[('superseding','!position->normalized.point || position->dispatching','position->dispatching'),
          ('ownership','if (!manager || parentPositionFor(manager.get()) != position)','if (!manager)'),
          ('readiness','Aquamarine::parentPointerInputStatus(source.get(), output.get()) != Aquamarine::ParentInputStatus::Ready','false'),
          ('geometry','if (monitor == monitors.end() || (*monitor)->logicalBox() != position->appliedBox)','if (monitor == monitors.end())')]
 for name,before,after in mutants:
  assert cpp.count(before)==1
  mutated=cpp.replace(before,after)
  if name=='readiness':mutated=mutated.replace('static ParentInputStatus parentPointerInputStatus','[[maybe_unused]] static ParentInputStatus parentPointerInputStatus')
  p=OUT/(name+'.cpp');p.write_text(mutated)
  run(name+'-compile',[*flags,str(p),'-o',str(OUT/name)]);run(name+'-rejected',[str(OUT/name)],expected=1)
 for p,digest in r['inputs'].items():assert sha(p)==digest,p
 r.update(passed=True,mutantsRejected=len(mutants),callerSchedulesAfterLayoutBookkeeping=True)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

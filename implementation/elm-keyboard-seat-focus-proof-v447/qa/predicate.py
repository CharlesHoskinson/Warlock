import hashlib,json,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('predicate-'+str(time.time_ns()));OUT.mkdir()
old=REPO/'implementation/maximized-stack-v1/native-core-v2/src/managers/input/InputManager.cpp';new=REPO/'implementation/elm-keyboard-seat-focus-policy-v446/candidate/src/managers/input/InputManager.cpp'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=old.read_text();b=new.read_text();before='if (m_keyboards.size() == 1 && Desktop::focusState()->surface())';after='if (m_keyboards.size() == 1 && g_pSeatManager->m_state.keyboardFocus.expired() && Desktop::focusState()->surface())';assert a.replace(before,after)==b and a.count(before)==1
wrapper = r"""
#include <vector>
#include <iostream>
struct Weak { bool alive; bool expired() const { return !alive; } };
struct Seat { struct State { Weak keyboardFocus; } m_state; } seat;
Seat* g_pSeatManager = &seat;
namespace Desktop { struct Focus { int target; int surface() const { return target; } } focus; Focus* focusState() { return &focus; } }
std::vector<int> m_keyboards;
int decide(int count, int current, int desktop) {
 m_keyboards.assign(count,0);seat.m_state.keyboardFocus.alive=current!=0;Desktop::focus.target=desktop;
 int chosen=current;
 PREDICATE chosen=Desktop::focusState()->surface();
 return chosen;
}
int main() { int checks=0; for(int count=0;count<4;++count) for(int current=0;current<3;++current) for(int target=0;target<3;++target) {
 int expected=(count==1 && current==0 && target!=0)?target:current;
 if(decide(count,current,target)!=expected) return 1; ++checks;
 } std::cout<<checks<<"\n"; }
"""
report={'passed':False,'scope':'Actual owning setupKeyboard predicate extracted against typed adapter and independent36-case focus oracle; no full compositor/native acceptance','inputs':{str(old):sha(old),str(new):sha(new)},'controls':[]}
try:
 for name,predicate,exitCode in [('candidate',after,0),('old-overwrite',before,1),('no-fallback','if (false)',1)]:
  src=OUT/(name+'.cpp');src.write_text(wrapper.replace('PREDICATE',predicate));binary=OUT/name
  cp=subprocess.run(['/usr/bin/c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',str(src),'-o',str(binary)],capture_output=True,text=True,timeout=30);(OUT/(name+'-compile.stderr')).write_text(cp.stderr);assert cp.returncode==0
  rp=subprocess.run([str(binary)],capture_output=True,text=True,timeout=5);(OUT/(name+'.stdout')).write_text(rp.stdout);assert rp.returncode==exitCode
  report['controls'].append({'name':name,'exitCode':rp.returncode,'expectedExitCode':exitCode})
 report.update(passed=True,checks=36)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.iterdir() if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])

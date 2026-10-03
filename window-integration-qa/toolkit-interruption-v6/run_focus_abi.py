"""Exact extracted focus guard, actual Hyprutils shared/weak ABI; no GUI/native load."""
from pathlib import Path
import hashlib,json,shlex,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent));from qa_launch import require_qa_scope
from run_retirement_ownership import block
B=Path(__file__).resolve().parent
SHIM=r'''
#include <hyprutils/memory/SharedPtr.hpp>
#include <hyprutils/memory/WeakPtr.hpp>
#include <hyprutils/memory/UniquePtr.hpp>
#include <optional>
#include <iostream>
#include <stdexcept>
#include <cstdint>
template<class T>using SP=Hyprutils::Memory::CSharedPointer<T>;
template<class T>using WP=Hyprutils::Memory::CWeakPointer<T>;
using Hyprutils::Memory::makeShared;using Hyprutils::Memory::makeUnique;
struct Owner{uint64_t m_stableID;bool mapped=true,hidden=false,m_isFloating=true;explicit Owner(uint64_t id):m_stableID(id){}bool isHidden(){return hidden;}};
using PHLWINDOW=SP<Owner>;using PHLWINDOWREF=WP<Owner>;
bool validMapped(const PHLWINDOW& owner){return owner&&owner->mapped;}
struct CBox{};enum eMouseBindMode{MBIND_INVALID,MBIND_MOVE,MBIND_RESIZE,MBIND_RESIZE_FORCE_RATIO,MBIND_RESIZE_BLOCK_RATIO};
constexpr uint32_t BTN_LEFT=272;
namespace Desktop{enum eFocusReason:uint8_t{FOCUS_REASON_UNKNOWN,FOCUS_REASON_FFM,FOCUS_REASON_KEYBIND,FOCUS_REASON_DISPATCH_FOCUSWINDOW,FOCUS_REASON_DISPATCH_MOVEWINDOWINTOGROUP,FOCUS_REASON_CLICK,FOCUS_REASON_OTHER,FOCUS_REASON_DESKTOP_STATE_CHANGE};}
namespace Layout{struct ITarget{PHLWINDOW owner;explicit ITarget(PHLWINDOW w):owner(w){}PHLWINDOW window(){return owner;}};}
struct Controller{SP<Layout::ITarget> current;eMouseBindMode activeMode=MBIND_MOVE;SP<Layout::ITarget> target(){return current;}eMouseBindMode mode(){return activeMode;}};
struct Manager{Controller controller;Controller* dragController(){return &controller;}};auto g_layoutManager=makeUnique<Manager>();
struct BoolValue{bool active=true;bool value(){return active;}};auto enabled=makeShared<BoolValue>();
unsigned checks=0;void check(bool yes){if(!yes)throw std::runtime_error("focus requirement "+std::to_string(checks+1));++checks;}
'''
CASES=r'''
int main(){
 auto owner=makeShared<Owner>(0xa),peer=makeShared<Owner>(0xb),foreign=makeShared<Owner>(0xc);auto target=makeShared<Layout::ITarget>(owner);g_layoutManager->controller.current=target;
 gesture=GestureCapture{owner,target,owner->m_stableID,{},MBIND_MOVE,BTN_LEFT};
 check(preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));
 for(auto reason:{Desktop::FOCUS_REASON_UNKNOWN,Desktop::FOCUS_REASON_KEYBIND,Desktop::FOCUS_REASON_DISPATCH_FOCUSWINDOW,Desktop::FOCUS_REASON_DISPATCH_MOVEWINDOWINTOGROUP,Desktop::FOCUS_REASON_CLICK,Desktop::FOCUS_REASON_OTHER,Desktop::FOCUS_REASON_DESKTOP_STATE_CHANGE})check(!preserveCapturedGestureFocus(owner,peer,reason));
 check(!preserveCapturedGestureFocus(owner,owner,Desktop::FOCUS_REASON_FFM));check(!preserveCapturedGestureFocus(foreign,peer,Desktop::FOCUS_REASON_FFM));
 check(!preserveCapturedGestureFocus({},peer,Desktop::FOCUS_REASON_FFM));check(!preserveCapturedGestureFocus(owner,{},Desktop::FOCUS_REASON_FFM));
 owner->mapped=false;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));owner->mapped=true;
 peer->mapped=false;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));peer->mapped=true;
 owner->hidden=true;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));owner->hidden=false;
 peer->hidden=true;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));peer->hidden=false;
 owner->m_isFloating=false;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));owner->m_isFloating=true;
 enabled->active=false;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));enabled->active=true;
 owner->m_stableID++;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));owner->m_stableID--;
 auto replacement=makeShared<Layout::ITarget>(owner);g_layoutManager->controller.current=replacement;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));g_layoutManager->controller.current=target;
 auto prior=gesture;gesture.reset();check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));gesture=prior;
 g_layoutManager->controller.activeMode=MBIND_INVALID;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));
 for(auto mode:{MBIND_MOVE,MBIND_RESIZE,MBIND_RESIZE_FORCE_RATIO,MBIND_RESIZE_BLOCK_RATIO}){g_layoutManager->controller.activeMode=mode;gesture->mode=mode;check(preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));}
 // An expired shared target does not adopt a same-owner replacement target.
 prior.reset();target.reset();g_layoutManager->controller.current=replacement;check(!preserveCapturedGestureFocus(owner,peer,Desktop::FOCUS_REASON_FFM));
 std::cout<<checks<<" exact focus guard ABI assertions PASS\n";
}
'''
def main():
 scope=require_qa_scope();source=B/'native-candidate/dragBridge.cpp';text=source.read_text();exact=block(text,'struct GestureCapture')+';\nstd::optional<GestureCapture> gesture;\n'+block(text,'bool sameGesture')+'\n'+block(text,'bool preserveCapturedGestureFocus')
 out=B/'focus-build';out.mkdir(mode=0o700);cpp=out/'test.cpp';cpp.write_text(SHIM+exact+CASES);binary=out/'test';flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','hyprutils'],text=True));command=['g++','-std=c++23','-O1','-MD','-MF',str(out/'test.d'),str(cpp),'-o',str(binary),*flags];built=subprocess.run(command,capture_output=True,text=True);run=subprocess.run([str(binary)],capture_output=True,text=True) if built.returncode==0 else None;deps={}
 if (out/'test.d').exists():
  for name in (out/'test.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(name)
   if p.is_file():deps[str(p.resolve())]=hashlib.sha256(p.read_bytes()).hexdigest()
 report=dict(result='pass' if built.returncode==0 and run.returncode==0 else 'fail',scope=scope,command=command,compileReturnCode=built.returncode,compileStdout=built.stdout,compileStderr=built.stderr,execute=None if run is None else dict(exitCode=run.returncode,stdout=run.stdout,stderr=run.stderr),dependencies=deps,extractedSourceSHA256=hashlib.sha256(exact.encode()).hexdigest(),candidateSourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),nativeGUIExecuted=False,mainChanged=False,boundary='Actual Hyprutils ABI with exact extracted guard; mocked core/window lifecycle, actual native focus acceptance pending')
 with (B/'focus-abi-report.json').open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
 print(json.dumps(dict(result=report['result'],execute=report['execute'],nativeGUIExecuted=False)));return int(report['result']!='pass')
if __name__=='__main__':raise SystemExit(main())

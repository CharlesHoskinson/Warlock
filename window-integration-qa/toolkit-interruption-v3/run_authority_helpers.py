"""Compile and execute exact staged native guard functions with weak-lifetime mocks.
This exercises the production function text, not a separate reimplementation;
it cannot establish actual compositor callback ordering or toolkit input.
"""
from pathlib import Path
import hashlib,json,resource,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent

def block(source,prefix):
 start=source.index(prefix);brace=source.index('{',start);depth=1;end=brace+1
 while depth:
  depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]

def main():
 scope=require_qa_scope();out=B/'authority-build-2';out.mkdir(exist_ok=False)
 source=B/'native-candidate/dragBridge.cpp';text=source.read_text();digest=hashlib.sha256(source.read_bytes()).hexdigest()
 captionSource=(B/'native-candidate/barDeco.cpp').read_text()
 actual=block(text,'struct GestureCapture')+';\nstd::optional<GestureCapture> gesture;\n'+block(text,'bool sameGesture')+'\n'+block(text,'void retireCapturedGesture')
 shim=r'''
#include <cassert>
#include <any>
#include <cstdint>
#include <memory>
#include <optional>
#include <stdexcept>
#include <iostream>
static unsigned passedAssertions=0;
#undef assert
#define assert(condition) do { if (!(condition)) throw std::runtime_error("Assertion failed: " #condition); ++passedAssertions; } while(0)
template<class T>using SP=std::shared_ptr<T>;
template<class T>using WP=std::weak_ptr<T>;
struct Owner{uint64_t m_stableID;bool mapped=true;};
using PHLWINDOW=SP<Owner>;
bool validMapped(const PHLWINDOW& owner){return owner&&owner->mapped;}
struct Vector2D{double x=0,y=0;};
struct CWLSurfaceResource{};
enum eInputType{INPUT_TYPE_DRAG_END,INPUT_TYPE_OTHER};
namespace Desktop{
 enum eFocusReason{FOCUS_REASON_DESKTOP_STATE_CHANGE,FOCUS_REASON_CLICK};
 struct CFocusState{PHLWINDOW current;PHLWINDOW window(){return current;}};
 namespace View{using CWindow=Owner;struct CGroup{};}
}
using DecoInputFn=bool(*)(Desktop::View::CWindow*,eInputType,const Vector2D&,std::any);
using GroupAddFn=void(*)(Desktop::View::CGroup*,PHLWINDOW,std::optional<size_t>);
using FullFocusFn=void(*)(Desktop::CFocusState*,PHLWINDOW,Desktop::eFocusReason,SP<CWLSurfaceResource>,bool);
struct Hook{void* m_original;};
int decoCalls=0,groupCalls=0,focusCalls=0;
bool originalDeco(Desktop::View::CWindow*,eInputType,const Vector2D&,std::any){++decoCalls;return true;}
void originalGroup(Desktop::View::CGroup*,PHLWINDOW,std::optional<size_t>){++groupCalls;}
void originalFocus(Desktop::CFocusState* state,PHLWINDOW owner,Desktop::eFocusReason,SP<CWLSurfaceResource>,bool){++focusCalls;state->current=owner;}
Hook decoImpl{reinterpret_cast<void*>(originalDeco)},groupImpl{reinterpret_cast<void*>(originalGroup)},focusImpl{reinterpret_cast<void*>(originalFocus)};
Hook *decoInputHook=&decoImpl,*groupAddHook=&groupImpl,*fullFocusHook=&focusImpl;
using PHLWINDOWREF=WP<Owner>;
struct CBox{double x=0,y=0,w=0,h=0;};
enum eMouseBindMode{MBIND_INVALID,MBIND_MOVE,MBIND_RESIZE};
constexpr uint32_t BTN_LEFT=272;
namespace Layout{struct ITarget{SP<Owner> owner;SP<Owner> window(){return owner;}};}
struct Controller{SP<Layout::ITarget> current;SP<Layout::ITarget> target(){return current;}};
bool keepCurrentGeometry=false;
uint32_t releasedButton=BTN_LEFT;
struct Manager{
 std::unique_ptr<Controller> c=std::make_unique<Controller>();int ends=0;bool keepObserved=false;bool throws=false;
 const std::unique_ptr<Controller>& dragController(){return c;}
 void endDragTarget(){++ends;keepObserved=keepCurrentGeometry;if(throws)throw std::runtime_error("core end failed");c->current.reset();}
};
auto g_layoutManager=std::make_unique<Manager>();
struct CHyprBar {bool m_bDragPending=false,m_bDraggingThis=false,m_bTouchEv=false,m_bCancelledDown=true;int m_touchId=0;CBox m_captionPress;bool retireCaptionIntent();};
'''
 actual+='\nstd::optional<GestureCapture> cancellation;\n'+block(text,'struct CancellationScope')+';\n'+block(text,'bool cancelledOwner')+'\n'+block(text,'bool hookedDecoInput')+'\n'+block(text,'void hookedGroupAdd')+'\n'+block(text,'void hookedFullFocus')
 actual+='\n'+block(captionSource,'bool CHyprBar::retireCaptionIntent')
 cases=r'''
int main(){
 auto owner=std::make_shared<Owner>(Owner{11});
 auto target=std::make_shared<Layout::ITarget>(Layout::ITarget{owner});
 auto bind=[&]{gesture=GestureCapture{owner,target,11,{},MBIND_MOVE,BTN_LEFT};g_layoutManager->c->current=target;};
 bind();assert(sameGesture(target));
 assert(!sameGesture(nullptr));
 auto other=std::make_shared<Layout::ITarget>(Layout::ITarget{owner});assert(!sameGesture(other));
 auto replacement=std::make_shared<Owner>(Owner{11});target->owner=replacement;assert(!sameGesture(target));target->owner=owner;
 owner->m_stableID=12;assert(!sameGesture(target));owner->m_stableID=11;
 bind();retireCapturedGesture();assert(g_layoutManager->ends==1&&!g_layoutManager->keepObserved&&!gesture&&!g_layoutManager->c->current&&releasedButton==0);
 bind();retireCapturedGesture(true);assert(g_layoutManager->ends==2&&g_layoutManager->keepObserved&&!keepCurrentGeometry);
 bind();g_layoutManager->c->current=other;retireCapturedGesture();assert(g_layoutManager->ends==2&&g_layoutManager->c->current==other&&!gesture);
 bind();g_layoutManager->throws=true;try{retireCapturedGesture(true);assert(false);}catch(const std::runtime_error&){}assert(!keepCurrentGeometry&&gesture&&g_layoutManager->c->current==target);g_layoutManager->throws=false;
 bind();target->owner.reset();owner.reset();assert(!sameGesture(target));retireCapturedGesture();assert(g_layoutManager->ends==3&&g_layoutManager->c->current==target);
 // Capture a weak target then destroy that target: no replacement adoption.
 gesture.reset();target.reset();g_layoutManager->c->current.reset();assert(!sameGesture(other));
 CHyprBar bar;bar.m_bDragPending=true;assert(bar.retireCaptionIntent()&&!bar.m_bDragPending&&bar.m_bCancelledDown);
 bar.m_bDraggingThis=true;bar.m_bTouchEv=true;bar.m_touchId=5;assert(bar.retireCaptionIntent()&&!bar.m_bDraggingThis&&!bar.m_bTouchEv&&bar.m_touchId==0&&bar.m_bCancelledDown);
 assert(!bar.retireCaptionIntent()&&bar.m_bCancelledDown);
 owner=std::make_shared<Owner>(Owner{31});target=std::make_shared<Layout::ITarget>(Layout::ITarget{owner});
 auto peer=std::make_shared<Owner>(Owner{32});GestureCapture cap{owner,target,31,{},MBIND_MOVE,BTN_LEFT};
 Desktop::View::CGroup group;Desktop::CFocusState focus;focus.current=peer;
 assert(!cancelledOwner(owner));
 {CancellationScope outer(cap);assert(cancelledOwner(owner));
  assert(!hookedDecoInput(peer.get(),INPUT_TYPE_DRAG_END,{},std::any(owner))&&decoCalls==0);
  hookedGroupAdd(&group,owner,{});assert(groupCalls==0);
  hookedFullFocus(&focus,owner,Desktop::FOCUS_REASON_DESKTOP_STATE_CHANGE,{},false);assert(focus.current==peer&&focusCalls==0);
  assert(hookedDecoInput(peer.get(),INPUT_TYPE_OTHER,{},std::any(owner))&&decoCalls==1);
  hookedGroupAdd(&group,peer,{});assert(groupCalls==1);
  hookedFullFocus(&focus,owner,Desktop::FOCUS_REASON_CLICK,{},false);assert(focus.current==owner&&focusCalls==1);
  {CancellationScope nested(std::nullopt);assert(!cancelledOwner(owner));hookedGroupAdd(&group,owner,{});assert(groupCalls==2);}assert(cancelledOwner(owner));
  try{CancellationScope nested(std::nullopt);throw std::runtime_error("reentrant");}catch(const std::runtime_error&){}assert(cancelledOwner(owner));
  owner->m_stableID=99;assert(!cancelledOwner(owner));owner->m_stableID=31;
  target->owner=peer;assert(!cancelledOwner(owner));target->owner=owner;
  owner->mapped=false;assert(!cancelledOwner(owner));owner->mapped=true;
 }assert(!cancellation);
 // Real release executes without cancellation scope and preserves native drop.
 assert(hookedDecoInput(peer.get(),INPUT_TYPE_DRAG_END,{},std::any(owner))&&decoCalls==2);hookedGroupAdd(&group,owner,{});assert(groupCalls==3);
 std::cout<<passedAssertions<<" exact-function assertions PASS\n";
}
'''
 (out/'test.cpp').write_text(shim+actual+cases)
 compile_cmd=['g++','-std=c++23','-O1','-g','-MMD','-MF',str(out/'test.d'),str(out/'test.cpp'),'-o',str(out/'test')]
 compiled=subprocess.run(compile_cmd,text=True,capture_output=True)
 run=subprocess.run([str(out/'test')],text=True,capture_output=True) if compiled.returncode==0 else None
 assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
 report={'result':'pass' if run and run.returncode==0 else 'fail','passedAssertions':int(run.stdout.split()[0]) if run and run.returncode==0 else None,'scope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'command':compile_cmd,'sourceSHA256':digest,'extractedSHA256':hashlib.sha256(actual.encode()).hexdigest(),'compile':{'exitCode':compiled.returncode,'stdout':compiled.stdout,'stderr':compiled.stderr},'execute':None if not run else {'exitCode':run.returncode,'stdout':run.stdout,'stderr':run.stderr},'boundary':'Exact function text, mocked core/lifetimes; no native/toolkit acceptance','nativeExecuted':False}
 (B/'authority-report-2.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('result','passedAssertions','scope','boundary')}));return 0 if report['result']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())

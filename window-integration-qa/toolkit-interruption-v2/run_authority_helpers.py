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
#include <cstdint>
#include <memory>
#include <optional>
#include <stdexcept>
#include <iostream>
template<class T>using SP=std::shared_ptr<T>;
template<class T>using WP=std::weak_ptr<T>;
struct Owner{uint64_t m_stableID;};
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
 std::cout<<"14 exact-function authority cases PASS\n";
}
'''
 (out/'test.cpp').write_text(shim+actual+cases)
 compile_cmd=['g++','-std=c++23','-O1','-g','-MMD','-MF',str(out/'test.d'),str(out/'test.cpp'),'-o',str(out/'test')]
 compiled=subprocess.run(compile_cmd,text=True,capture_output=True)
 run=subprocess.run([str(out/'test')],text=True,capture_output=True) if compiled.returncode==0 else None
 assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
 report={'result':'pass' if run and run.returncode==0 else 'fail','caseCount':14,'scope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'command':compile_cmd,'sourceSHA256':digest,'extractedSHA256':hashlib.sha256(actual.encode()).hexdigest(),'compile':{'exitCode':compiled.returncode,'stdout':compiled.stdout,'stderr':compiled.stderr},'execute':None if not run else {'exitCode':run.returncode,'stdout':run.stdout,'stderr':run.stderr},'boundary':'Exact function text, mocked core/lifetimes; no native/toolkit acceptance','nativeExecuted':False}
 (B/'authority-report-2.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('result','caseCount','scope','boundary')}));return 0 if report['result']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())

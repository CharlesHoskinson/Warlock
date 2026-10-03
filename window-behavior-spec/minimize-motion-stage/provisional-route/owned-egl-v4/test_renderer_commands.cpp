// Exercise actual consumer commands with a blocked submitted frame. No display,
// surface, texture or GUI application is created in this executable.
#define OWNED_EGL_OFFLINE_TEST
#include "Renderer.cpp"
#include <cassert>
struct OfflineCommands {
 static int run(){
  int checks=0;auto check=[&](bool yes){assert(yes);++checks;};
  Renderer r;r.ledger.configure({{"left",1}});r.routeIdentity={"ff01",42};
  r.ledger.seed(r.routeIdentity,"0123456789ab-1",std::string(64,'a'));
  r.atlasRect={10,20,380,240};r.iconRect={20,600,28,28};
  auto pending=r.ledger.prepare("left",1,r.atlasRect,.2,false,100);assert(pending);
  auto action=[&](QString command,QString token,QString operation="restore"){
   return QJsonObject{{"command",command},{"stableId","ff01"},{"pid",42},{"token",token},{"operation",operation},{"target",rectangleJson(operation=="restore"?r.atlasRect:r.iconRect)},{"durationMs",400}};
  };
  auto rejects=[&](QJsonObject command){try{r.command(command);return false;}catch(const std::exception&){return true;}};
  r.command(action("retarget","0123456789ab-2"));
  check(r.waitingRetarget["token"]=="0123456789ab-2");check(r.ledger.hasPending());check(!r.ledger.nativeReady());
  check(rejects(action("validate","0123456789ab-1")));
  r.command(action("validate","0123456789ab-2"));check(r.waitingRetarget["promoted"].toBool());check(!r.ledger.nativeReady());
  r.command(action("retarget","0123456789ab-3","minimize"));check(!r.waitingRetarget["promoted"].toBool());
  check(rejects(action("validate","0123456789ab-2")));
  r.command(action("cancel","0123456789ab-1"));check(r.ledger.isActive());check(r.waitingRetarget["token"]=="0123456789ab-3");
  auto reused=action("cancel","0123456789ab-3");reused["pid"]=43;r.command(reused);check(r.ledger.isActive());
  check(rejects(action("retarget","0123456789ab-4\n")));check(rejects(action("retarget","0123456789ab-4\r\n")));check(rejects(action("retarget","0123456789ab-4-extra")));
  check(rejects(action("start","0123456789ab-1")));
  auto wrong=action("retarget","0123456789ab-4");wrong["target"]=rectangleJson({900,500,1,1});check(rejects(wrong));
  auto huge=action("retarget","0123456789ab-4");huge["pid"]=1e100;check(rejects(huge));
  r.command(action("cancel","0123456789ab-3"));check(!r.ledger.isActive());check(r.waitingRetarget.isEmpty());
  check(r.ledger.present(pending->sequence,200,1)==Result::Rejected);
  Renderer::Output idle;idle.configured=true;
  check(r.needsDraw(idle));idle.clearCommitted=true;check(!r.needsDraw(idle));
  r.ledger.seed(r.routeIdentity,"0123456789ab-4",std::string(64,'a'));r.required.push_back(&idle);
  check(r.needsDraw(idle));idle.frameReady=false;check(!r.needsDraw(idle));
  idle.frameReady=true;idle.outstanding=1;check(!r.needsDraw(idle));
  idle.outstanding=0;idle.endpointPresented=true;check(!r.needsDraw(idle));
  idle.endpointPresented=false;r.ledger.cancel();check(!r.needsDraw(idle));
  idle.clearCommitted=false;check(r.needsDraw(idle));r.required.clear();
  std::cout<<checks<<" actual owned-renderer pending-command checks PASS\n";return 0;
 }
};
int main(){return OfflineCommands::run();}

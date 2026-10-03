#define OWNED_EGL_OFFLINE_TEST
#include "Renderer.cpp"
#include <cassert>
struct OfflineCommands {
 static int run(){
  int checks=0;auto check=[&](bool ok){if(!ok)throw std::runtime_error("family check "+std::to_string(checks+1)+" failed");++checks;};
  std::vector<Source> sources{{{"aa01",41},std::string(64,'a'),{104,130,380,240},{100,100,388,274},{20,700,28,28}},{{"bb02",42},std::string(64,'b'),{154,180,280,180},{150,150,288,214},{20,700,28,28}},{{"cc03",43},std::string(64,'c'),{204,230,180,100},{200,200,188,134},{20,700,28,28}}};
  std::vector<Identity> ids;for(const auto& s:sources)ids.push_back(s.identity);
  CommitLedger l;l.configure({{"left",1},{"right",2}});l.seedFamily(sources,"0123456789ab-1",std::string(64,'d'),"minimize");
  check(l.familyMatches(ids));check(!l.nativeReady());check(!l.promoteFamily({ids[0]},"0123456789ab-1"));check(!l.promoteFamily({ids[0],ids[2],ids[1]},"0123456789ab-1"));
  auto a=l.prepareFamily("left",1,.3,100),b=l.prepareFamily("right",2,.2,100);check(a&&b);check(a->members.size()==3&&b->members.size()==3);
  check(a->members[2].source==sources[2]);check(a->members[2].rectangle==mix(sources[2].atlasRect,sources[2].iconRect,.3));
  check(l.swapReturned(a->sequence,true)==Result::Deferred);check(l.present(a->sequence,200,1)==Result::RecordedCurrent);
  check(!l.nativeReady());check(l.swapReturned(b->sequence,true)==Result::Deferred);check(l.present(b->sequence,210,1)==Result::RecordedCurrent);
  check(!l.nativeReady());check(l.promoteFamily(ids,"0123456789ab-1"));check(l.nativeReady());check(!l.nativeEndpoint());
  check(l.retargetFamily(ids,"0123456789ab-2","restore"));check(!l.nativeReady());
  auto leftOrigin=l.sceneRectangles("left",0),rightOrigin=l.sceneRectangles("right",0);
  check(leftOrigin==a->members);check(rightOrigin==b->members);check(leftOrigin[1].rectangle!=rightOrigin[1].rectangle);
  auto c=l.prepareFamily("left",1,.2,220),d=l.prepareFamily("right",2,.2,220);check(c&&d);check(c->progress==d->progress);
  check(c->members[0].rectangle==mix(a->members[0].rectangle,sources[0].atlasRect,.2));
  check(!l.retargetFamily(ids,"0123456789ab-3","minimize"));
  check(l.present(c->sequence,300,2)==Result::Deferred);check(l.swapReturned(c->sequence,true)==Result::RecordedCurrent);
  check(l.swapReturned(d->sequence,true)==Result::Deferred);check(l.present(d->sequence,310,2)==Result::RecordedCurrent);
  check(l.retargetFamily(ids,"0123456789ab-3","minimize"));check(!l.promoteFamily(ids,"0123456789ab-2"));
  check(l.sceneRectangles("left",0)==c->members);check(l.sceneRectangles("right",0)==d->members);
  auto endL=l.prepareFamily("left",1,1,320),endR=l.prepareFamily("right",2,1,320);check(endL&&endR);
  for(size_t i=0;i<3;i++)check(endL->members[i].rectangle==sources[i].iconRect);
  l.swapReturned(endL->sequence,true);l.present(endL->sequence,400,3);l.swapReturned(endR->sequence,true);l.present(endR->sequence,410,3);
  check(!l.nativeEndpoint());auto reused=ids;reused[1].pid++;check(!l.promoteFamily(reused,"0123456789ab-3"));
  check(l.promoteFamily(ids,"0123456789ab-3"));check(l.nativeEndpoint());
  l.outputRemoved("right",2);check(!l.nativeEndpoint());check(!l.isActive());
  auto dup=sources;dup[2].identity.stable=dup[1].identity.stable;bool rejected=false;try{l.seedFamily(dup,"0123456789ab-4",std::string(64,'d'),"minimize");}catch(...){rejected=true;}check(rejected);
  l.seedFamily(sources,"0123456789ab-4",std::string(64,'d'),"restore");
  auto incomplete=l.prepare("left",1,{20,700,28,28},0,false,420);l.swapReturned(incomplete->sequence,true);check(l.present(incomplete->sequence,500,4)==Result::Rejected);
  l.cancel();check(l.present(incomplete->sequence,510,4)==Result::Rejected);
  Renderer r;r.ledger.configure({{"left",1},{"right",2}});r.ledger.seedFamily(sources,"0123456789ab-1",std::string(64,'d'),"minimize");r.familyIdentities=ids;r.routeIdentity=ids[0];
  auto outstanding=r.ledger.prepareFamily("left",1,.2,100);check(bool(outstanding));
  auto command=[&](QString action,QString token,QString op="restore"){return QJsonObject{{"command",action},{"token",token},{"identities",identityJson(ids)},{"operation",op},{"durationMs",400}};};
  auto rejects=[&](QJsonObject j){try{r.command(j);return false;}catch(...){return true;}};
  r.command(command("retarget","0123456789ab-2"));check(r.waitingRetarget["token"]=="0123456789ab-2");check(!r.ledger.nativeReady());
  r.command(command("validate","0123456789ab-2"));check(r.waitingRetarget["promoted"].toBool());
  r.command(command("retarget","0123456789ab-3","minimize"));check(!r.waitingRetarget["promoted"].toBool());check(rejects(command("validate","0123456789ab-2")));
  auto partial=command("validate","0123456789ab-3");partial["identities"]=identityJson({ids[0]});check(rejects(partial));
  auto wrong=command("retarget","0123456789ab-4");wrong["identities"]=identityJson(reused);check(rejects(wrong));
  check(rejects(command("retarget","0123456789ab-4\n")));check(rejects(command("retarget","0123456789ab-4\r\n")));check(rejects(command("retarget","0123456789ab-4-extra")));
  r.command(command("cancel","0123456789ab-1"));check(r.ledger.isActive());check(r.waitingRetarget["token"]=="0123456789ab-3");
  r.command(command("cancel","0123456789ab-3"));check(!r.ledger.isActive());check(r.waitingRetarget.empty());
  check(r.ledger.present(outstanding->sequence,200,1)==Result::Rejected);
  Renderer diagnostic(true);diagnostic.ledger.configure({{"left",1}});diagnostic.ledger.seedFamily(sources,"0123456789ab-1",std::string(64,'d'),"minimize");diagnostic.familyIdentities=ids;diagnostic.routeIdentity=ids[0];
  auto sample=command("sample","0123456789ab-1");sample["progress"]=.45;diagnostic.command(sample);check(diagnostic.sampleProgress==.45);check(!diagnostic.ledger.nativeReady());
  auto diagReject=[&](QJsonObject j){try{diagnostic.command(j);return false;}catch(...){return true;}};
  check(diagReject(command("validate","0123456789ab-1")));check(diagReject(command("start","0123456789ab-1")));
  check(rejects(sample));sample["progress"]=2;check(diagReject(sample));sample["progress"]=-.1;check(diagReject(sample));
  sample["progress"]="0.4";check(diagReject(sample));sample["progress"]=.4;sample["token"]="0123456789ab-2";check(diagReject(sample));
  sample["token"]="0123456789ab-1";sample["identities"]=identityJson(reused);check(diagReject(sample));
  std::cout<<checks<<" composite family ledger/actual consumer checks PASS\n";return 0;
 }
};
int main(){return OfflineCommands::run();}

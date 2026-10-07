#include "capture-intent-source-fixture.hpp"
#include "preview_bootstrap_lifetime.hpp"
using namespace preview;
static std::string take(char*& text){require(text,"Actual realm C output");std::string result(text);g_free(text);text=nullptr;return result;}
static JsonObject* row(Json& wrapper){auto rows=json_object_get_array_member(wrapper.object(),"rows");require(rows && json_array_get_length(rows)==1,"One actual realm row");return json_array_get_object_element(rows,0);}
int main(int argc,char** argv){try{
 const bool coreDead=argc>1 && std::string_view(argv[1])=="core-dead";
 const bool exhausted=argc>1 && std::string_view(argv[1])=="exhaustion";
 Server server;Server foreign;GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);
 check(bootstrap && !error,"Realm original authenticated bootstrap");
 auto foreignBootstrap=warlock_preview_bootstrap_open(foreign.config().c_str(),&error);check(foreignBootstrap && !error,"Independent actual foreign native Bootstrap");auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);
 auto& native=*static_cast<Native*>(transport);const auto binding=native.binding();auto popup=reinterpret_cast<gpointer>(uintptr_t(77));
 char* text=nullptr;char* grantText=nullptr;void* raw=nullptr;std::string previousTicket;uint64_t previousEpoch=0;
 auto open=[&](uint64_t subject,bool accepted){auto owner=warlock_imported_clients_open_controlled(transport,popup,subject,1,1,&text,&grantText,&raw,&error);
  check(bool(owner)==accepted && (accepted?!error:bool(error)),"Actual realm C factory result");
  if(!accepted){check(!text && !grantText && !raw,"Rejected realm publishes no receiver or grant");g_clear_error(&error);}return owner;};
 auto finish=[&](uint64_t subject,uint64_t expectedEpoch){
  auto owner=open(subject,true);check(text && grantText && raw && native.previewControlClaimed(),"Actual published realm owns exclusive native namespace");take(text);Json grant(take(grantText));const auto epoch=grant.counter("receiverEpoch");
  check(epoch==expectedEpoch && epoch>previousEpoch,"Native realm epoch survives endpoint replacement and failed construction");
  auto& endpoint=*static_cast<uri::Endpoint*>(raw);check(endpoint.registeredView(77)->epoch==epoch,"Actual Endpoint carries Native realm identity");
  check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Actual Bootstrap attaches original realm receipt");
  auto delivery=static_cast<ReceiptDelivery*>(warlock_preview_bootstrap_delivery(bootstrap,popup,&error));check(delivery && !error,"Actual original Bootstrap borrowed capability");const auto identity="family:"+std::to_string(subject);
  struct Ticket{uint64_t ordinal;std::string wire;};
  auto propose=[&](const std::string& command){check(warlock_imported_clients_propose_control(owner,delivery,popup,identity.c_str(),command.c_str(),&text,&error) && !error,"Actual realm original purpose proposal");Json p(take(text));return Ticket{p.counter("controlOrdinal"),Json::text(p.object(),"wire")};};
  auto dispatch=[&](const Ticket& ticket){char* receipt=nullptr;check(warlock_imported_clients_dispatch_control(owner,delivery,popup,ticket.wire.c_str(),&text,&receipt,&error) && !error && text && receipt,"Actual realm original ticket dispatch");take(text);take(receipt);};
  auto confirm=[&](uint64_t ordinal){const auto wire=Wire().integer("previewProtocol",3).text("kind","preview-control-confirmed").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).counter("controlOrdinal",ordinal).finish();check(warlock_imported_clients_confirm_control(owner,popup,wire.c_str(),&text,&error) && !error,"Actual original realm confirmation");take(text);};
  auto closeRefused=[&]{check(!warlock_imported_clients_close_bootstrap(owner,bootstrap,&error) && error && native.previewControlClaimed(),"Published realm claim survives refused original close");g_clear_error(&error);check(warlock_preview_bootstrap_delivery(bootstrap,popup,&error)==delivery && !error,"Refused original close preserves borrowed receipt channel");};
  auto poll=[&]{check(warlock_imported_clients_retirement_poll(owner,delivery,popup,&text,&error) && !error,"Actual realm borrowed retirement polling");take(text);};
  closeRefused();open(subject+2,false);check(native.previewControlClaimed(),"Concurrent refused factory cannot release another original realm");
  const auto reconcile=Wire().text("kind","reconcile").begin("binding").binding(binding).end().finish();auto original=propose(reconcile);check(original.ordinal==1,"Fresh realm has independent native control prefix");
  if(!previousTicket.empty()) {
   check(previousTicket!=original.wire,"Canonical same-binding purpose differs across Native realm epochs");
   char* receipt=nullptr;check(!warlock_imported_clients_dispatch_control(owner,delivery,popup,previousTicket.c_str(),&text,&receipt,&error) && error && !text && !receipt,"Old exact native ticket rejected before replacement handler");g_clear_error(&error);
   poll();check(endpoint.native([](auto& b){return b.recordCount()==1 && b.charge()==4096 && !b.inspect().front().terminal;}),"Old realm ticket cannot quarantine or settle replacement job");
  }
  dispatch(original);confirm(original.ordinal);poll();const auto terminal=endpoint.native([](auto& b){return b.inspect().front();});
  check(terminal.terminal && terminal.proofs.size()==2 && !terminal.bytes,"Actual original unattempted job obtains terminal proofs");closeRefused();
  auto ack=propose(Wire().text("kind","acknowledge").begin("job").job(terminal.job).end().counter("sequence",terminal.proofs.back().sequence.value).finish());dispatch(ack);confirm(ack.ordinal);closeRefused();
  std::ofstream(server.root/"retired-through")<<subject;
  check(warlock_imported_clients_retirement_observe(owner,popup,identity.c_str(),&text,&error) && !error,"Actual original realm permanent incarnation observation");Json facts("{\"rows\":"+take(text)+"}");auto fact=row(facts);
  auto ready=propose(Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",subject).text("observationRequest",Json::text(fact,"request")).text("observationSequence",Json::text(fact,"sequence")).finish());dispatch(ready);confirm(ready.ordinal);poll();
  check(warlock_imported_clients_retirement_pending(owner,delivery,popup,&text,&error) && !error,"Actual original realm final actor delivery");Json final("{\"rows\":"+take(text)+"}");fact=row(final);
  auto processed=propose(Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end().text("deliveryOrdinal",Json::text(fact,"deliveryOrdinal")).finish());dispatch(processed);closeRefused();confirm(processed.ordinal);
  check(warlock_imported_clients_empty(owner) && native.previewControlClaimed(),"Original complete closure alone does not silently release published realm");
  check(!warlock_imported_clients_close_bootstrap(owner,foreignBootstrap,&error) && error && native.previewControlClaimed() && warlock_imported_clients_empty(owner),"Foreign Bootstrap refuses before settled original owner mutation");g_clear_error(&error);
  check(warlock_preview_bootstrap_delivery(bootstrap,popup,&error)==delivery && !error,"Foreign Bootstrap refusal preserves exact original channel");
  previousTicket=original.wire;previousEpoch=epoch;
  if(coreDead)server.finish();
  check(warlock_imported_clients_close_bootstrap(owner,bootstrap,&error) && !error && !native.previewControlClaimed(),"Actual strict C close releases only settled original realm");
  const bool stale=bootstrapHasImportedDelivery(bootstrap);
  if(stale){warlock_preview_bootstrap_free(bootstrap);warlock_preview_bootstrap_free(foreignBootstrap);server.finish();foreign.finish();check(!stale,"Settled C close releases borrowed Bootstrap before Endpoint destruction");}
  check(!stale,"Settled C close releases borrowed Bootstrap before Endpoint destruction");
  check(!warlock_preview_bootstrap_delivery(bootstrap,popup,&error) && error,"Closed Bootstrap delivery lookup refuses safely");g_clear_error(&error);
  check(!warlock_preview_bootstrap_pending(bootstrap,popup,&text,&error) && error && !text,"Closed Bootstrap polling refuses without old Endpoint access");g_clear_error(&error);
  if(!coreDead)check(native.binding()==binding,"Preview realm closure never resets shared Native grant");
  if(!coreDead){bool refused=false;try{Native::LegacyPreviewClaim invalid(native);}catch(const std::exception&){refused=true;}
  check(refused,"Closed controlled realm cannot downgrade to legacy ownership");}
 };
 finish(21,exhausted?UINT64_MAX:1);
 if(exhausted){open(23,false);check(!native.previewControlClaimed() && native.binding()==binding,"Realm exhaustion refuses before admission without replacing grant");}
 else if(coreDead){open(23,false);check(!native.previewControlClaimed(),"Core death cannot admit another realm after original settled Bootstrap close");}
 else {open(21,false);check(!native.previewControlClaimed() && native.binding()==binding,"Unpublished source-refused constructor releases only its own claim");finish(23,3);}
 warlock_preview_bootstrap_free(bootstrap);warlock_preview_bootstrap_free(foreignBootstrap);server.finish();foreign.finish();
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"nativeRealmEpochThrough\":\""<<previousEpoch<<"\",\"failedConstructionEpochConsumed\":"<<(!exhausted && !coreDead?"true":"false")<<",\"coreExitedBeforeStrictClose\":"<<(coreDead?"true":"false")<<",\"exhaustion\":"<<(exhausted?"true":"false")<<",\"normalOwnedExit\":true,\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}

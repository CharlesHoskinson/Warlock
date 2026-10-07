#include "capture-resource-source-fixture.hpp"
using namespace preview;
static std::string take(char*& text){require(text,"Actual C resource output");std::string value(text);g_free(text);text=nullptr;return value;}
static uint64_t count(const fs::path& path){uint64_t value=0;std::ifstream(path)>>value;return value;}
int main(){try{
 for(const char* mode:{"capture-refused","capture-malformed","capture-fd-missing","resource-lost-release","resource-lost-retire","resource-bad-reply"}) {
  Server server(mode);GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);
  check(bootstrap && !error,"Actual original C resource bootstrap");auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);
  auto& native=*static_cast<Native*>(transport);const auto binding=native.binding();auto popup=reinterpret_cast<gpointer>(uintptr_t(77));
  char* text=nullptr;char* grantText=nullptr;void* raw=nullptr;
  auto owner=warlock_imported_clients_open_controlled(transport,popup,21,1,1,&text,&grantText,&raw,&error);
  check(owner && text && grantText && raw && !error,"Actual controlled C resource owner");take(text);Json grant(take(grantText));const auto epoch=grant.counter("receiverEpoch");
  auto& endpoint=*static_cast<uri::Endpoint*>(raw);
  check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Same original actual C resource receipt endpoint");
  auto delivery=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);check(delivery && !error,"Original resource receipt capability");
  WarlockImportedAdmission admission=WARLOCK_IMPORTED_INVALID;
  check(warlock_imported_clients_enroll(owner,popup,23,1,1,&admission,&text,&error) && !error && admission==WARLOCK_IMPORTED_STARTED,"Independent original neighbor job");take(text);
  check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Original neighbor receipt enrollment");
  auto refuse=[&](bool value){check(!value && error,"Actual resource C refusal");g_clear_error(&error);};
  struct Ticket{uint64_t ordinal;std::string wire;};
  auto propose=[&](const std::string& identity,const std::string& command){
   check(warlock_imported_clients_propose_control(owner,delivery,popup,identity.c_str(),command.c_str(),&text,&error) && !error,"Actual C resource purpose proposal");
   Json result(take(text));return Ticket{result.counter("controlOrdinal"),Json::text(result.object(),"wire")};
  };
  auto dispatch=[&](const Ticket& ticket,bool expected=true){
   char* receipt=nullptr;auto result=warlock_imported_clients_dispatch_control(owner,delivery,popup,ticket.wire.c_str(),&text,&receipt,&error);
   check(bool(result)==expected && (expected?!error:bool(error)) && text && receipt,"Original C effect return and independent transport receipt");
   g_clear_error(&error);take(text);Json delivered(take(receipt));check(delivered.counter("controlOrdinal")==ticket.ordinal,"Exact original C resource delivered prefix");
  };
  auto confirm=[&](uint64_t ordinal){
   auto wire=Wire().integer("previewProtocol",3).text("kind","preview-control-confirmed").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).counter("controlOrdinal",ordinal).finish();
   check(warlock_imported_clients_confirm_control(owner,popup,wire.c_str(),&text,&error) && !error,"Original resource transport confirmation");take(text);
  };
  const auto first=endpoint.native([](auto& broker){return broker.inspect().front().job;});
  const auto acquire=Wire().text("kind","acquire").begin("job").job(first).end().finish();auto acquired=propose("family:21",acquire);
  dispatch(acquired,false);confirm(acquired.ordinal);
  check(count(server.root/"capture-count")==1 && endpoint.native([](auto& broker){return broker.charge()==8192 && !broker.inspect().front().terminal;}),"Original capture Unknown retains charge before reconciliation");
  const auto reconcile=Wire().text("kind","reconcile").begin("binding").binding(binding).end().finish();
  auto ticket=propose("family:21",reconcile);const auto neighbor=propose("family:23",std::string("  ")+reconcile+"\n");
  check(ticket.ordinal==acquired.ordinal+1 && neighbor.ordinal==ticket.ordinal && neighbor.wire==ticket.wire,"Different families reuse one canonical binding reconciliation ticket");
  refuse(warlock_imported_clients_command(owner,"family:21",reconcile.c_str(),&text,&error));
  check(warlock_imported_clients_retirement_poll(owner,delivery,popup,&text,&error) && !error,"Undispatched reconciliation cannot enter cleanup");take(text);
  check(count(server.root/"resource-count")==0 && endpoint.native([](auto& broker){return broker.charge()==8192;}),"Native issued ticket alone cannot authorize cleanup");
  dispatch(ticket);dispatch(ticket);
  check(count(server.root/"resource-count")==0 && count(server.root/"capture-count")==1,"Exact reconciliation retry does not replay capture or cleanup handler");
  refuse(warlock_imported_clients_enroll(owner,popup,30,1,1,&admission,&text,&error));
  check(!text && endpoint.native([](auto& broker){return broker.actorCount()==2;}),"Original reconciliation quarantines new source admission");
  const bool owned=std::string_view(mode)!="capture-refused";
  if(owned)std::ofstream(server.root/"locked")<<1;
  if(std::string_view(mode)=="resource-bad-reply")std::ofstream(server.root/"bad-resource-reply")<<1;
  auto poll=[&](bool expected=true){auto result=warlock_imported_clients_retirement_poll(owner,delivery,popup,&text,&error);
   check(bool(result)==expected && (expected?!error:bool(error)),"Actual C native resource poll disposition");g_clear_error(&error);if(text)take(text);};
  poll(std::string_view(mode)!="resource-lost-release" && std::string_view(mode)!="resource-bad-reply");
  if(owned)check(endpoint.native([](auto& broker){const auto rows=broker.inspect();return !rows.front().terminal && rows.front().proofs.empty() && rows.front().bytes==4096;}),"Locked or malformed native evidence retains original charge without final proof");
  poll();check(endpoint.native([](auto& broker){const auto rows=broker.inspect();return rows.size()==2 && rows.back().terminal && rows.back().bytes==0;}),"Fair native polling settles independent unattempted neighbor despite pending original job");
  if(owned) {
   if(std::string_view(mode)=="resource-bad-reply")fs::remove(server.root/"bad-resource-reply");
   poll();check(count(server.root/"producer-count")==1 && count(server.root/"export-count")==0,"Lost export ACK recovers by fresh native observation while locked producer remains owned");
   check(endpoint.native([](auto& broker){const auto rows=broker.inspect();return !rows.front().terminal && rows.front().bytes==4096;}),"Native export zero cannot grant producer or local reservation retirement");
   fs::remove(server.root/"locked");poll(std::string_view(mode)!="resource-lost-retire");
   if(std::string_view(mode)=="resource-lost-retire") {
    check(count(server.root/"producer-count")==0 && endpoint.native([](auto& broker){return !broker.inspect().front().terminal;}),"Lost producer ACK preserves Unknown until original native observation");poll();
   }
  }
  check(endpoint.native([](auto& broker){const auto rows=broker.inspect();return rows.size()==2 && rows.front().terminal && rows.front().proofs.size()==2 && !broker.charge();}),"Original unoffered capture settles only after native backend zero and actual no adopted local storage");
  check(!warlock_imported_clients_empty(owner),"Backend settlement cannot retire live window actors or unconfirmed controls");
  char* oldReceipt=nullptr;
  refuse(warlock_imported_clients_dispatch_control(owner,delivery,popup,acquired.wire.c_str(),&text,&oldReceipt,&error));
  check(!text && !oldReceipt && count(server.root/"capture-count")==1,"Unknown original acquisition remains unreplayed after backend settlement");
  confirm(ticket.ordinal);
  const auto records=endpoint.native([](auto& broker){return broker.inspect();});
  for(const auto& record:records) {
   const auto subject=record.job.context.incarnation.value;const auto identity="family:"+std::to_string(subject);
   const auto ack=Wire().text("kind","acknowledge").begin("job").job(record.job).end().counter("sequence",record.proofs.back().sequence.value).finish();
   auto terminal=propose(identity,ack);dispatch(terminal);confirm(terminal.ordinal);
   check(warlock_imported_clients_retirement_observe(owner,popup,identity.c_str(),&text,&error) && !error,"Actual live window retirement query before permanent fact");
   check(take(text)=="[]" && !warlock_imported_clients_empty(owner),"Backend zero and terminal ACK do not fabricate permanent window retirement");
   std::ofstream(server.root/"retired-through")<<subject;
   check(warlock_imported_clients_retirement_observe(owner,popup,identity.c_str(),&text,&error) && !error,"Actual permanent native incarnation fact");
   Json observed("{\"rows\":"+take(text)+"}");auto rows=json_object_get_array_member(observed.object(),"rows");
   check(rows && json_array_get_length(rows)==1,"One actual retained retirement observation");auto fact=json_array_get_object_element(rows,0);
   const auto ready=Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",subject)
       .text("observationRequest",Json::text(fact,"request")).text("observationSequence",Json::text(fact,"sequence")).finish();
   auto readiness=propose(identity,ready);dispatch(readiness);confirm(readiness.ordinal);
   check(warlock_imported_clients_retirement_poll(owner,delivery,popup,&text,&error) && !error,"Original retained completion after actual all-map retirement");
   Json completed("{\"rows\":"+take(text)+"}");rows=json_object_get_array_member(completed.object(),"rows");
   check(rows && json_array_get_length(rows)==1,"Original final actor delivery remains owned");fact=json_array_get_object_element(rows,0);
   const auto finalAck=Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end()
       .text("deliveryOrdinal",Json::text(fact,"deliveryOrdinal")).finish();auto final=propose(identity,finalAck);dispatch(final);
   check(!warlock_imported_clients_empty(owner),"Final actor processing ACK still requires original control confirmation");confirm(final.ordinal);
  }
  check(count(server.root/"capture-count")==1 && !count(server.root/"producer-count") && !count(server.root/"export-count"),"Every original native resource settled without capture replay");
  check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Strict binding close retains all independent native resource, proof, actor and control barriers");
  warlock_preview_bootstrap_free(bootstrap);server.finish();
 }
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"resourceCases\":6,\"normalOwnedExit\":true,\"nativeAcceptance\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}

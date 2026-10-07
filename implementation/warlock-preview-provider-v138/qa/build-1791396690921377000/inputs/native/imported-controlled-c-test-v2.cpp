#define main retained_original_channel_fixture
#include "actor-retirement-channel-test-v2.cpp"
#undef main
using namespace preview;
static std::string take(char*& text){require(text,"Actual C output");std::string result(text);g_free(text);text=nullptr;return result;}
static JsonObject* onlyRow(Json& wrapper){auto rows=json_object_get_array_member(wrapper.object(),"rows");require(rows && json_array_get_length(rows)==1,"One original native row");return json_node_get_object(json_array_get_element(rows,0));}
int main(){try {
 Server server("turnover");GError* error=nullptr;
 auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Actual native C bootstrap");
 auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);check(transport && !error,"Original borrowed Native transport");
 auto& native=*static_cast<Native*>(transport);auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* text=nullptr;char* grantText=nullptr;void* raw=nullptr;
 auto refusal=[&](bool result){check(!result && error,"Actual C refusal reported");g_clear_error(&error);};
 {
  Native::LegacyPreviewClaim liveLegacy(native);const auto before=native.next();
  auto deniedOwner=warlock_imported_clients_open_controlled(transport,popup,21,1,1,&text,&grantText,&raw,&error);
  refusal(deniedOwner);check(!text && !grantText && !raw && native.next()==before+1,"Live legacy owner blocks controlled namespace before native effects");
 }
 auto owner=warlock_imported_clients_open_controlled(transport,popup,21,1,1,&text,&grantText,&raw,&error);
 check(owner && text && grantText && raw && !error,"Actual controlled C factory");take(text);const auto grantWire=take(grantText);Json grant(grantWire);
 const auto binding=native.binding();const auto epoch=grant.counter("receiverEpoch");auto& endpoint=*static_cast<uri::Endpoint*>(raw);
 check(decodeBinding(Json::child(grant.object(),"binding"))==binding && Json::integer(grant.object(),"capacity")==1065 &&
  endpoint.registeredView(77)->epoch==epoch && native.previewControlClaimed(),"Actual original receiver/native namespace and reserved capacity");
 const auto beforeLegacy=native.next();void* other=nullptr;
 refusal(warlock_imported_clients_open_dynamic(transport,popup,22,1,1,&text,&other,&error));
 check(!text && !other && native.next()==beforeLegacy+1,"Legacy C provider cannot enter controlled transport");
 refusal(warlock_imported_clients_open_controlled(transport,popup,22,1,1,&text,&grantText,&other,&error));
 check(!text && !grantText && !other && native.next()==beforeLegacy+2,"Second controlled owner cannot reset grant or namespace");
 check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Same original borrowed receipt endpoint");
 auto delivery=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);check(delivery && !error,"Original C receipt capability");
 auto readReceipt=[&]{check(warlock_imported_clients_control_receipt(owner,popup,&text,&error) && !error,"Original cached native control receipt");return take(text);};
 check(readReceipt()=="[]","No fabricated original delivered prefix");
 std::thread foreignThread([&]{GError* foreignError=nullptr;char* foreignText=nullptr;check(!warlock_imported_clients_control_receipt(owner,popup,&foreignText,&foreignError) && foreignError && !foreignText,"Foreign thread cannot read or mutate owner");g_clear_error(&foreignError);});foreignThread.join();
 auto confirm=[&](uint64_t ordinal){
  auto wire=Wire().integer("previewProtocol",3).text("kind","preview-control-confirmed").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).counter("controlOrdinal",ordinal).finish();
  check(warlock_imported_clients_confirm_control(owner,popup,wire.c_str(),&text,&error) && !error,"Actual original C receipt confirmation");take(text);
 };
 struct Ticket{uint64_t ordinal;bool alreadyDelivered;std::string wire;};
 auto propose=[&](const std::string& identity,const std::string& command){
  check(warlock_imported_clients_propose_control(owner,delivery,popup,identity.c_str(),command.c_str(),&text,&error) && !error,"Actual C native purpose proposal");
  Json proposal(take(text));auto object=proposal.object();
  check(decodeBinding(Json::child(object,"binding"))==binding && proposal.counter("receiverEpoch")==epoch,"Original native proposal grant");
  return Ticket{proposal.counter("controlOrdinal"),Json::boolean(object,"alreadyDelivered"),Json::text(object,"wire")};
 };
 auto dispatch=[&](const Ticket& ticket,bool expected=true){
  char* receipt=nullptr;auto result=warlock_imported_clients_dispatch_control(owner,delivery,popup,ticket.wire.c_str(),&text,&receipt,&error);
  check(bool(result)==expected && (expected?!error:bool(error)) && text && receipt,"Actual native C dispatcher return and independent receipt");
  g_clear_error(&error);auto events=take(text);Json delivered(take(receipt));check(delivered.counter("controlOrdinal")==ticket.ordinal,"Original native delivered prefix exact");return events;
 };
 const auto firstJob=endpoint.native([](auto& broker){return broker.inspect().front().job;});
 const auto firstCancel=Wire().text("kind","cancel").begin("job").job(firstJob).end().finish();
 refusal(warlock_imported_clients_command(owner,"family:21",firstCancel.c_str(),&text,&error));check(!text,"Raw job command cannot bypass native ticket");
 gboolean retired=FALSE;refusal(warlock_imported_clients_retire_native(owner,delivery,popup,"family:21",&retired,&text,&error));check(!retired && !text,"Raw retirement cannot bypass ticket");
 refusal(warlock_imported_clients_retirement_control(owner,delivery,popup,"family:21","{}",&text,&error));
 refusal(warlock_preview_bootstrap_acknowledge(bootstrap,popup,"family:21","{}",&error));
 check(!warlock_imported_clients_empty(owner),"Active actor and reserved cleanup prevent empty result");refusal(warlock_imported_clients_close(owner,&error));
 uint64_t issued=0;std::string lastWire;
 for(uint64_t index=1;index<=260;++index){
  const uint64_t subject=index==1?21:100+index;const auto identity="family:"+std::to_string(subject);
  if(index>1){WarlockImportedAdmission admission=WARLOCK_IMPORTED_INVALID;
   check(warlock_imported_clients_enroll(owner,popup,subject,index,index,&admission,&text,&error) && !error && admission==WARLOCK_IMPORTED_STARTED,"Actual next C actor under reclaimed reservations");take(text);
   check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Original journal grows without new epoch");}
  const auto records=endpoint.native([](auto& broker){return broker.inspect();});check(records.size()==1,"One actual original job");const auto job=records.front().job;
  const auto cancel=Wire().text("kind","cancel").begin("job").job(job).end().finish();auto ticket=propose(identity,cancel);
  check(!ticket.alreadyDelivered && ticket.ordinal==++issued,"Native assigns uninterrupted original control ordinals");
  if(index==1){
   auto altered=ticket.wire;replace(altered,"\"cancel\"","\"acquire\"");char* receipt=nullptr;
   refusal(warlock_imported_clients_dispatch_control(owner,delivery,popup,altered.c_str(),&text,&receipt,&error));check(!text && !receipt && readReceipt()=="[]","Changed valid command cannot invoke native-owned ordinal");
   auto foreign=ticket.wire;replace(foreign,"\"receiverEpoch\":\""+std::to_string(epoch)+"\"","\"receiverEpoch\":\""+std::to_string(epoch+1)+"\"");
   refusal(warlock_imported_clients_dispatch_control(owner,delivery,popup,foreign.c_str(),&text,&receipt,&error));
   refusal(warlock_imported_clients_dispatch_control(owner,delivery,reinterpret_cast<gpointer>(uintptr_t(78)),ticket.wire.c_str(),&text,&receipt,&error));
   auto future=ticket.wire;replace(future,"\"controlOrdinal\":\"1\"","\"controlOrdinal\":\"2\"");refusal(warlock_imported_clients_dispatch_control(owner,delivery,popup,future.c_str(),&text,&receipt,&error));
   check(!text && !receipt && endpoint.native([](auto& broker){return !broker.inspect().front().terminal;}),"Foreign/gap ticket refusals preserve native job");
  }
  dispatch(ticket);check(propose(identity,cancel).wire==ticket.wire && dispatch(ticket)=="[]","Exact C proposal and dispatch retries never replay handler");confirm(ticket.ordinal);
  const auto terminal=endpoint.native([](auto& broker){return broker.inspect();});check(terminal.size()==1 && terminal.front().proofs.size()==2,"Actual native two terminal proofs");
  if(index==1){
   const auto partial=Wire().text("kind","acknowledge").begin("job").job(job).end().counter("sequence",terminal.front().proofs.front().sequence.value).finish();auto partialTicket=propose(identity,partial);check(partialTicket.ordinal==++issued,"Original nonfinal proof retains native slot");
   dispatch(partialTicket,false);check(endpoint.native([](auto& broker){return broker.recordCount()==1;}),"Handler refusal receipt does not settle terminal ownership");
   check(dispatch(partialTicket)=="[]" && propose(identity,partial).wire==partialTicket.wire,"Returned failed handler only echoes exact original receipt");confirm(partialTicket.ordinal);
  }
  const auto ack=Wire().text("kind","acknowledge").begin("job").job(job).end().counter("sequence",terminal.front().proofs.back().sequence.value).finish();auto acknowledged=propose(identity,ack);check(acknowledged.ordinal==++issued,"Actual native final proof ticket");dispatch(acknowledged);
  check(endpoint.native([](auto& broker){return !broker.recordCount();}) && !warlock_imported_clients_empty(owner),"Broker proof drain alone cannot close native actor/control ownership");
  std::ofstream(server.root/"retired-through")<<subject;
  check(warlock_imported_clients_retirement_observe(owner,popup,identity.c_str(),&text,&error) && !error,"Actual native C retirement observation");Json observed("{\"rows\":"+take(text)+"}");auto original=onlyRow(observed);
  const auto ready=std::string("  ")+Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",subject).text("observationRequest",Json::text(original,"request")).text("observationSequence",Json::text(original,"sequence")).finish()+"\n";
  auto readiness=propose(identity,ready);check(readiness.ordinal==++issued && dispatch(readiness)=="[]","Unconfirmed proof ticket retains exact readiness bytes");
  confirm(acknowledged.ordinal);
  check(warlock_imported_clients_retirement_poll(owner,delivery,popup,&text,&error) && !error,"Actual C polling resumes exact accepted readiness");Json complete("{\"rows\":"+take(text)+"}");auto final=onlyRow(complete);const auto finalOrdinal=decimal(Json::text(final,"deliveryOrdinal"));
  if(index==1){auto predecessor=propose(identity,cancel);check(predecessor.alreadyDelivered && predecessor.wire==ticket.wire,"Confirmed native predecessor suppresses stale proposal after effect erasure");
   char* receipt=nullptr;refusal(warlock_imported_clients_dispatch_control(owner,delivery,popup,ticket.wire.c_str(),&text,&receipt,&error));check(!text && !receipt,"Released old ticket cannot invoke or fabricate latest receipt");}
  const auto finalAck=Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end().counter("deliveryOrdinal",finalOrdinal).finish();auto accepted=propose(identity,finalAck);check(accepted.ordinal==++issued,"Actual final ACK ticket resolves retained actor after C subject erasure");
  dispatch(accepted);check(propose(identity,finalAck).wire==accepted.wire && !warlock_imported_clients_empty(owner),"Final processing effect retains quotas until frontend receipt confirmation");
  if(index==260){lastWire=accepted.wire;server.finish();check(dispatch(accepted)=="[]","Latest original receipt remains readable after actual core process exits");}
  confirm(accepted.ordinal);check(endpoint.registeredView(77)->epoch==epoch && endpoint.native([](auto& broker){return !broker.actorCount() && !broker.recordCount() && !broker.charge();}),"Original actor/proof barriers and epoch survive C turnover");
 }
 check(issued==1041 && !lastWire.empty() && warlock_imported_clients_empty(owner),"260 actual C metadata actors settle without serial/ordinal reset");
 check(warlock_imported_clients_close(owner,&error) && !error,"Strict completed actor/control binding closes after actual confirmations");warlock_preview_bootstrap_free(bootstrap);
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"actorsTurnedOver\":260,\"nativeIssuedPrefix\":1041,\"normalOwnedExit\":true,\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& exception){std::cerr<<exception.what()<<'\n';return 1;}}

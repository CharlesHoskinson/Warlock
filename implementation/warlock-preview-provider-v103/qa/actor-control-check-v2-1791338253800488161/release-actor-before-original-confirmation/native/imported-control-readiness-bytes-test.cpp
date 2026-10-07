#define main retained_original_channel_fixture
#include "actor-retirement-channel-test-v2.cpp"
#undef main
using namespace preview;
int main(){try {
 Server server("turnover");auto native=server.open();ImportedClients value(*native,256);auto& endpoint=value.endpoint();const auto binding=native->binding();
 check(endpoint.registerControlView(77,binding),"Actual original empty control receiver");
 PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,77,endpoint.registeredView(77)->epoch};
 PreviewControlDelivery channel{};check(preview_control_delivery_init(&channel,grant),"Original native grant");ControlReservations bank(channel,1065);
 std::unique_ptr<ImportedControlAdmission> controls;endpoint.native([&](auto& broker){controls=std::make_unique<ImportedControlAdmission>(bank,grant,broker,256);});value.attachControlAdmission(*controls,grant);
 ImportedSubjects subjects(256,{});std::unique_ptr<ReceiptDelivery> delivery;RetirementJournal journal(binding,77,grant.epoch);
 for(uint64_t index=1;index<=260;++index) {
  const uint64_t subject=index==1?21:100+index;const auto identity="family:"+std::to_string(subject);auto staged=subjects.stage({subject});const auto entry=staged.entry;
  auto started=value.tryStartAtReceiver(77,grant.epoch,entry,{subject},index,index);
  check(started.native.job && started.native.job->request.value==1,"Actual native new serial starts with original request floor");subjects.commit(std::move(staged));const auto job=*started.native.job;
  if(!delivery)delivery=std::make_unique<ReceiptDelivery>(endpoint,binding,77);else check(delivery->extendSubjects(77),"Original delivery extends without receiver reset");
  check(controls->actorCount()==1 && controls->jobCount()==1 && bank.reserved()==8,"Reclaimed native cleanup quotas fund next actor without resetting counters");
  auto cancel=Wire().text("kind","cancel").begin("job").job(job).end().finish();auto ticket=value.proposeJobControl(grant,entry,identity,cancel);
  check(ticket && bank.ownsTicket(grant,ticket->ticket.ordinal,ticket->ticket.wire),"Actual owning native cancel ticket");
  check(preview_control_delivery_receive(&channel,grant,ticket->ticket.ordinal,ticket->ticket.wire.c_str(),ticket->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Original contiguous native cancel invocation");
  value.command(entry,identity,cancel);check(preview_control_delivery_complete(&channel,ticket->ticket.ordinal) && preview_control_delivery_confirm(&channel,grant,ticket->ticket.ordinal),"Native cancel delivery confirmation remains independent");
  const auto terminal=endpoint.native([](auto& broker){return broker.inspect();});check(terminal.size()==1 && terminal[0].proofs.size()==2,"Actual native cancellation/refusal terminal proofs");
  const auto ack=Wire().text("kind","acknowledge").begin("job").job(job).end().counter("sequence",terminal[0].proofs.back().sequence.value).finish();
  auto acknowledged=value.proposeJobControl(grant,entry,identity,ack);
  check(acknowledged && preview_control_delivery_receive(&channel,grant,acknowledged->ticket.ordinal,acknowledged->ticket.wire.c_str(),acknowledged->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Actual original native terminal ACK ticket");
  check(delivery->acknowledge(77,identity,ack) && preview_control_delivery_complete(&channel,acknowledged->ticket.ordinal),"Actual terminal ACK drains original Broker before transport confirmation");
  std::ofstream(server.root/"retired-through")<<subject;
  const auto observed=value.observeRetirementForDelivery(77,grant.epoch,entry,journal);check(observed.has_value(),"Actual authenticated synthetic source retirement observation retained");
  const auto* original=journal.observation(77,grant.epoch,binding,entry);require(original,"Original observation cache");
  const auto ready=std::string("  ")+Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",subject).counter("observationRequest",original->request).counter("observationSequence",original->sequence).finish()+"\n";
  if(index==1) {
   const auto before=native->next();
   check(denied([&]{value.retireAtReceiver(77,grant.epoch,entry,*delivery,subjects,&journal,ready);}) && native->next()==before+1,
      "Raw undispatched readiness cannot mutate or query original native actor");
   auto changed=ready;replace(changed,"\"subject\":\"21\"","\"subject\":\"22\"");
   check(denied([&]{value.proposeActorControl(grant,entry,identity,changed,journal);}) && bank.issued()==2,"Different original subject cannot consume actor quota");
  }
  auto readiness=value.proposeActorControl(grant,entry,identity,ready,journal);
  check(readiness && readiness->ticket.ordinal==index*4-1 && !readiness->alreadyDelivered,"Native readiness derives reserved actor slot");
  check(preview_control_delivery_receive(&channel,grant,readiness->ticket.ordinal,readiness->ticket.wire.c_str(),readiness->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Original readiness delivery invocation");
  const auto before=native->next();auto blocked=value.retireAtReceiver(77,grant.epoch,entry,*delivery,subjects,&journal,ready);
  check(!blocked && native->next()==before+1 && subjects.size()==1 && controls->jobCount()==1,"Unconfirmed terminal control blocks all-map removal before fresh native query");
  check(preview_control_delivery_complete(&channel,readiness->ticket.ordinal),"Accepted readiness is retained for native polling after handler return");
  check(preview_control_delivery_confirm(&channel,grant,acknowledged->ticket.ordinal),"Old terminal control confirmation opens original job credit release");
  const auto complete=value.pollRetirementDelivery(77,grant.epoch,*delivery,subjects,journal);
  check(complete!="[]" && !subjects.size() && controls->jobCount()==0 && controls->actorRetired(entry),"Actual native all-map transaction marks original control actor retired");
  check(controls->confirmedJobCount()==1 && bank.reserved()==2 && bank.ticketCount()==1,"Old job credits reclaimed but readiness and actor obligations retained");
  check(value.actorCounts(77,*delivery,subjects).find("\"frames\":0")!=std::string::npos &&
    endpoint.nativeDemand([](auto& queue){return !queue.slotCount() && !queue.nativeBroker().actorCount() && !queue.nativeBroker().recordCount() && !queue.nativeBroker().charge();}),"Actual original actor/frame/intent/slot/Broker retirement transaction");
  check(!value.closeControlBinding(grant),"Outstanding actor final-delivery credits prevent binding close");
  Json wrapped("{\"rows\":"+complete+"}");auto rows=json_object_get_array_member(wrapped.object(),"rows");require(rows && json_array_get_length(rows)==1,"Original native completion envelope");
  auto final=json_node_get_object(json_array_get_element(rows,0));const auto finalOrdinal=decimal(Json::text(final,"deliveryOrdinal"));
  const auto finalAck=Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end().counter("deliveryOrdinal",finalOrdinal).finish();
  auto accepted=value.proposeActorControl(grant,entry,identity,finalAck,journal);
  check(accepted && accepted->ticket.ordinal==index*4 && !accepted->alreadyDelivered,"Native completed actor determines final processing ACK slot");
  if(index==1) {
   check(denied([&]{value.acknowledgeRetirementDelivery(77,grant.epoch,*delivery,journal,finalAck);}) && journal.size()==1,
      "Uninvoked actor ACK cannot advance native processing prefix");
   auto foreign=grant;foreign.epoch++;
   check(denied([&]{value.proposeActorControl(foreign,entry,identity,finalAck,journal);}),"Another receiver cannot consume original final actor delivery");
  }
  check(value.settleConfirmedActorControls(grant)==0 && controls->actorCount()==1,"Original final processing effect is required before quota release");
  check(preview_control_delivery_receive(&channel,grant,accepted->ticket.ordinal,accepted->ticket.wire.c_str(),accepted->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Original final actor ACK invocation");
  check(value.acknowledgeRetirementDelivery(77,grant.epoch,*delivery,journal,finalAck) && !journal.size(),"Actual native final delivery acknowledgment removes original completion");
  check(value.settleConfirmedActorControls(grant)==0 && controls->actorCount()==1,"Final ACK handler in flight does not establish frontend confirmation");
  check(preview_control_delivery_complete(&channel,accepted->ticket.ordinal),"Final actor ACK returns separately from frontend confirmation");
  check(value.settleConfirmedActorControls(grant)==0 && controls->actorCount()==1,"Unconfirmed final ACK retains actor cleanup credits");
  const auto retry=value.proposeActorControl(grant,entry,identity,finalAck,journal);
  check(retry && retry->ticket.wire==accepted->ticket.wire && bank.issued()==index*4,"Exact post-effect actor ACK retains native ticket after journal erasure");
  check(preview_control_delivery_confirm(&channel,grant,accepted->ticket.ordinal),"Actual original final actor delivery receipt confirmed");
  check(value.settleConfirmedActorControls(grant)==1 && !controls->actorCount() && !controls->confirmedJobCount() && bank.reserved()==1 && !bank.ticketCount(),"Only actual retirement plus final effect and frontend confirmation reclaim actor credits");
  check(bank.issued()==index*4 && endpoint.registeredView(77)->epoch==grant.epoch && subjects.issuedThrough()==index,"Original issuance and receiver epochs never reset during native metadata turnover");
  if(index==1)check(denied([&]{value.tryStartAtReceiver(77,grant.epoch,entry,{subject},2,2);}),"Closed original native serial cannot be reopened after quota collection");
 }
 check(value.empty() && value.closeControlBinding(grant) && bank.transportEmpty(),"Original physical/proof/actor/final frontend barriers permit transport binding close");
 check(value.closeControlBinding(grant) && bank.issued()==1040 && preview_control_delivery_confirmed(&channel),"Repeated close cannot reset original native namespace");
 auto attempted=subjects.stage({999});check(denied([&]{value.tryStartAtReceiver(77,grant.epoch,attempted.entry,attempted.subject,261,261);}) && !value.hasJob(attempted.entry),"Closed controlled binding cannot admit another original job");
 server.finish();std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"actorsTurnedOver\":260,\"nativeIssuedPrefix\":1040,\"normalOwnedExit\":true,\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}

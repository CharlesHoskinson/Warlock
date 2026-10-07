#define main retained_original_channel_fixture
#include "actor-retirement-channel-test-v2.cpp"
#undef main
using namespace preview;
int main(){try {
 Server server("turnover");auto native=server.open();ImportedClients value(*native,256);auto& endpoint=value.endpoint();const auto binding=native->binding();
 require(endpoint.registerControlView(77,binding),"Actual native receiver before actor admission");
 PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,77,endpoint.registeredView(77)->epoch};
 PreviewControlDelivery channel{};require(preview_control_delivery_init(&channel,grant),"Original native control grant");ControlReservations bank(channel,1065);
 std::unique_ptr<ImportedControlAdmission> controls;endpoint.native([&](auto& broker){controls=std::make_unique<ImportedControlAdmission>(bank,grant,broker,256);});value.attachControlAdmission(*controls,grant);
 ImportedSubjects subjects(256,{{21}});auto started=value.tryStartAtReceiver(77,grant.epoch,1,{21},1,1);require(started.native.job.has_value(),"Actual original job");const auto job=*started.native.job;
 ReceiptDelivery delivery(endpoint,binding,77);RetirementJournal journal(binding,77,grant.epoch);
 const auto cancel=Wire().text("kind","cancel").begin("job").job(job).end().finish();auto first=value.proposeJobControl(grant,1,"family:21",cancel);require(first.has_value(),"Actual original cancel slot");
 require(preview_control_delivery_receive(&channel,grant,first->ticket.ordinal,first->ticket.wire.c_str(),first->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Original first invocation");value.command(1,"family:21",cancel);
 require(preview_control_delivery_complete(&channel,1) && preview_control_delivery_confirm(&channel,grant,1),"Original first receipt confirmation");
 const auto terminal=endpoint.native([](auto& broker){return broker.inspect();});const auto ack=Wire().text("kind","acknowledge").begin("job").job(job).end().counter("sequence",terminal[0].proofs.back().sequence.value).finish();auto second=value.proposeJobControl(grant,1,"family:21",ack);
 require(second && preview_control_delivery_receive(&channel,grant,2,second->ticket.wire.c_str(),second->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Actual original terminal ACK invocation");
 require(delivery.acknowledge(77,"family:21",ack) && preview_control_delivery_complete(&channel,2),"Actual physical/proof settlement, frontend receipt unconfirmed");
 std::ofstream(server.root/"retired-through")<<21;
 require(value.observeRetirementForDelivery(77,grant.epoch,1,journal).has_value(),"Actual cached native retirement observation");
 const auto* observation=journal.observation(77,grant.epoch,binding,1);require(observation,"Actual original observation");
 const auto observationSequence=observation->sequence;
 const auto ready=Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",21).counter("observationRequest",observation->request).counter("observationSequence",observation->sequence).finish();
 const auto finalAck=Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end().counter("deliveryOrdinal",1).finish();
 std::optional<ImportedControlAdmission::Proposal> readiness,final;
 bool accepted=false,acked=false,unknown=false,closed=false;int last=0;std::string event;
 auto dispatch=[&](const std::optional<ImportedControlAdmission::Proposal>& proposal,auto effect){
  if(!proposal)return 0;
  const auto& ticket=proposal->ticket;
  // Original latest wire remains native-approved receipt identity even after
  // its quota was confirmed and released. No effect is granted by that echo.
  if(ticket.ordinal==channel.prefix.delivered && ticket.wire==channel.latest)return 2;
  if(!bank.ownsTicket(grant,ticket.ordinal,ticket.wire))return 0;
  auto decision=preview_control_delivery_receive(&channel,grant,ticket.ordinal,ticket.wire.c_str(),ticket.wire.size());
  if(decision!=PREVIEW_CONTROL_INVOKE)return decision==PREVIEW_CONTROL_REPEAT_RECEIPT?2:0;
  effect();require(preview_control_delivery_complete(&channel,ticket.ordinal),"Native dispatcher returned once");return 1;
 };
 while(std::getline(std::cin,event)) {
  try {
   if(event=="Ready") {readiness=value.proposeActorControl(grant,1,"family:21",ready,journal);last=readiness?1:0;}
   else if(event=="DeliverReady")last=dispatch(readiness,[&]{value.retireAtReceiver(77,grant.epoch,1,delivery,subjects,&journal,ready);accepted=true;});
   else if(event=="ConfirmJob")last=preview_control_delivery_confirm(&channel,grant,2)?1:0;
   else if(event=="Poll")last=value.pollRetirementDelivery(77,grant.epoch,delivery,subjects,journal)!="[]"?1:0;
   else if(event=="FinalAck") {final=value.proposeActorControl(grant,1,"family:21",finalAck,journal);last=final?1:0;}
   else if(event=="DeliverFinal" || event=="UnknownFinal")last=dispatch(final,[&]{
    if(event=="UnknownFinal")unknown=true;
    else {require(value.acknowledgeRetirementDelivery(77,grant.epoch,delivery,journal,finalAck),"Actual original final processing effect");acked=true;}
   });
   else if(event=="ConfirmAll")last=preview_control_delivery_confirm(&channel,grant,channel.prefix.delivered)?1:0;
   else if(event=="Collect")last=value.settleConfirmedActorControls(grant)?1:0;
   else if(event=="Close") {last=value.closeControlBinding(grant)?1:0;if(last)closed=true;}
   else if(event=="RawReady") {value.retireAtReceiver(77,grant.epoch,1,delivery,subjects,&journal,ready);last=1;}
   else if(event=="RawFinal") {last=value.acknowledgeRetirementDelivery(77,grant.epoch,delivery,journal,finalAck)?1:0;}
   else if(event=="WrongObservation") {auto changed=ready;replace(changed,"\"observationSequence\":\""+std::to_string(observationSequence)+"\"","\"observationSequence\":\"999999\"");last=value.proposeActorControl(grant,1,"family:21",changed,journal)?1:0;}
   else if(event=="FutureFinal") {const auto future=Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end().counter("deliveryOrdinal",2).finish();last=value.proposeActorControl(grant,1,"family:21",future,journal)?1:0;}
   else {require(event=="ForeignReceiver","Known actor control event");auto foreign=grant;foreign.epoch++;last=value.proposeActorControl(foreign,1,"family:21",ready,journal)?1:0;}
  }catch(const std::exception&){last=-1;}
  // No real captured buffers/backend resources in this metadata fixture. A
  // confirmed Unknown handler deliberately leaves its actual native journal
  // and actor credits retained; process teardown is not host-close acceptance.
  Json inventory(value.actorCounts(77,delivery,subjects));const auto frames=Json::integer(inventory.object(),"frames");
  std::cout<<"{\"issued\":"<<bank.issued()<<",\"delivered\":"<<channel.prefix.delivered<<",\"confirmed\":"<<channel.confirmed<<",\"reserved\":"<<bank.reserved()<<",\"tickets\":"<<bank.ticketCount()
   <<",\"ready\":"<<(readiness?"true":"false")<<",\"accepted\":"<<(accepted?"true":"false")<<",\"removed\":"<<(!subjects.size()?"true":"false")<<",\"final\":"<<(final?"true":"false")
   <<",\"acked\":"<<(acked?"true":"false")<<",\"unknown\":"<<(unknown?"true":"false")<<",\"actor\":"<<(controls->actorCount()?"true":"false")<<",\"closed\":"<<(closed?"true":"false")
   <<",\"journal\":"<<journal.size()<<",\"frames\":"<<frames<<",\"jobs\":"<<controls->jobCount()<<",\"previous\":"<<controls->confirmedJobCount()<<",\"last\":"<<last<<"}\n";
 }
 server.finish();return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}

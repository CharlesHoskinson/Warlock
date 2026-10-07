#define main retained_original_channel_fixture
#include "actor-retirement-channel-test-v2.cpp"
#undef main
using namespace preview;
int main(){try {
 Server server("turnover");auto native=server.open();ImportedClients value(*native,256);auto& endpoint=value.endpoint();const auto binding=native->binding();
 require(endpoint.registerControlView(77,binding),"Actual native original control receiver");
 PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,77,endpoint.registeredView(77)->epoch};
 PreviewControlDelivery channel{};require(preview_control_delivery_init(&channel,grant),"Actual original grant");ControlReservations bank(channel,1065);
 std::unique_ptr<ImportedControlAdmission> controls;endpoint.native([&](auto& broker){controls=std::make_unique<ImportedControlAdmission>(bank,grant,broker,256);});value.attachControlAdmission(*controls,grant);
 auto started=value.tryStartAtReceiver(77,grant.epoch,1,{21},1,1);require(started.native.job.has_value(),"Actual native first job");Job current=*started.native.job;
 ReceiptDelivery delivery(endpoint,binding,77);uint64_t request=1,phase=0,invocations=0;int last=0;
 std::optional<ImportedControlAdmission::Proposal> cancel,ack;
 std::string currentAck,previousAck;
 auto cancelWire=[](const Job& job){return Wire().text("kind","cancel").begin("job").job(job).end().finish();};
 auto ackWire=[](const Job& job,uint64_t seq){return Wire().text("kind","acknowledge").begin("job").job(job).end().counter("sequence",seq).finish();};
 std::string event;
 while(std::getline(std::cin,event)) {
  try {
   if(event=="Cancel") {cancel=value.proposeJobControl(grant,1,"family:21",cancelWire(current));last=cancel?1:0;}
   else if(event=="Ack" || event=="ChangedAck") {
    if(currentAck.empty()) {
     auto records=endpoint.native([](auto& broker){return broker.inspect();});
     currentAck=ackWire(current,records.size()==1 && !records[0].proofs.empty()?records[0].proofs.back().sequence.value:1);
    }
    if(event=="ChangedAck") {auto changed=(previousAck.empty()?currentAck:previousAck)+" ";auto ignored=value.proposeJobControl(grant,1,"family:21",changed);last=ignored?1:0;}
    else {ack=value.proposeJobControl(grant,1,"family:21",currentAck);last=ack?1:0;}
   }else if(event=="DeliverCancel" || event=="DeliverAck") {
    const auto& proposal=event=="DeliverCancel"?cancel:ack;
    if(!proposal)last=0;
    else {
     require(!proposal->alreadyDelivered && bank.ownsTicket(grant,proposal->ticket.ordinal,proposal->ticket.wire),"Original native owned ticket before dispatch");
     const auto& ticket=proposal->ticket;auto decision=preview_control_delivery_receive(&channel,grant,ticket.ordinal,ticket.wire.c_str(),ticket.wire.size());
     if(decision==PREVIEW_CONTROL_INVOKE) {
      if(event=="DeliverCancel") {value.command(1,"family:21",cancelWire(current));phase=1;currentAck.clear();}
      else {require(delivery.acknowledge(77,"family:21",currentAck),"Actual native final proof acknowledgment");phase=2;}
      ++invocations;require(preview_control_delivery_complete(&channel,ticket.ordinal),"Original handler returned");last=1;
     }else last=decision==PREVIEW_CONTROL_REPEAT_RECEIPT?2:0;
    }
   }else if(event=="Confirm")last=preview_control_delivery_confirm(&channel,grant,channel.prefix.delivered)?1:0;
   else if(event=="Resume") {
    auto next=value.resumeAtReceiver(77,grant.epoch,1,request+1,request+1);last=next.native.job?1:0;
    if(next.native.job){previousAck=currentAck;current=*next.native.job;request=current.request.value;phase=0;cancel.reset();ack.reset();currentAck.clear();}
   }else if(event=="OldAck") {auto prior=value.proposeJobControl(grant,1,"family:21",previousAck.empty()?ackWire(current,1):previousAck);last=prior && prior->alreadyDelivered?2:0;}
   else if(event=="WrongJob") {auto wrong=current;wrong.request.value+=100;auto ignored=value.proposeJobControl(grant,1,"family:21",cancelWire(wrong));last=ignored?1:0;}
   else if(event=="WrongFamily") {auto ignored=value.proposeJobControl(grant,1,"family:22",cancelWire(current));last=ignored?1:0;}
   else if(event=="ForeignReceiver") {auto foreign=grant;foreign.receiver++;auto ignored=value.proposeJobControl(foreign,1,"family:21",cancelWire(current));last=ignored?1:0;}
   else {require(event=="Malformed","Known job control event");auto ignored=value.proposeJobControl(grant,1,"family:21","{\"kind\":\"cancel\",\"kind\":\"acquire\"}");last=ignored?1:0;}
  }catch(const std::exception&){last=-1;}
  auto records=endpoint.native([](auto& broker){return broker.inspect();});
  require(value.job(1)==current && current.request.value==request && endpoint.registeredView(77)->epoch==grant.epoch,"Original native job request/epoch preserved");
  std::cout<<"{\"job\":"<<request<<",\"phase\":"<<phase<<",\"cancel\":"<<(cancel?cancel->ticket.ordinal:0)<<",\"ack\":"<<(ack?ack->ticket.ordinal:0)
   <<",\"issued\":"<<bank.issued()<<",\"delivered\":"<<channel.prefix.delivered<<",\"confirmed\":"<<channel.confirmed<<",\"tickets\":"<<bank.ticketCount()<<",\"reserved\":"<<bank.reserved()
   <<",\"previous\":"<<(controls->confirmedJobCount()?request-1:0)<<",\"records\":"<<records.size()<<",\"charge\":"<<endpoint.native([](auto& broker){return broker.charge();})<<",\"invocations\":"<<invocations<<",\"last\":"<<last<<"}\n";
 }
 server.finish();return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}

#define main retained_original_channel_fixture
#include "actor-retirement-channel-test-v2.cpp"
#undef main
int main(){try {
    Server server("turnover");
    {
        auto native=server.open();ImportedClients value(*native,256);auto& endpoint=value.endpoint();const auto binding=native->binding();
        check(endpoint.registerControlView(77,binding),"Empty owning receiver before actual admission");
        PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,77,endpoint.registeredView(77)->epoch};
        PreviewControlDelivery channel{};check(preview_control_delivery_init(&channel,grant),"Actual original native control grant");
        ControlReservations bank(channel,1065);std::unique_ptr<ImportedControlAdmission> controls;
        endpoint.native([&](auto& broker){controls=std::make_unique<ImportedControlAdmission>(bank,grant,broker,256);});
        value.attachControlAdmission(*controls,grant);auto started=value.tryStartAtReceiver(77,grant.epoch,1,{21},1,1);
        check(started.native.job.has_value(),"Actual original native reservation");const auto job=*started.native.job;
        ReceiptDelivery delivery(endpoint,binding,77);
        auto cancel=[&](const preview::Job& original){return Wire().text("kind","cancel").begin("job").job(original).end().finish();};
        auto ack=[&](const preview::Job& original,uint64_t sequence){return Wire().text("kind","acknowledge").begin("job").job(original).end().counter("sequence",sequence).finish();};
        auto propose=[&](const std::string& raw){return value.proposeJobControl(grant,1,"family:21",raw);};
        auto deniedWithoutMutation=[&](auto call,const char* name){const auto issued=bank.issued(),reserved=bank.reserved();check(denied(call) && issued==bank.issued() && reserved==bank.reserved(),name);};
        auto foreign=grant;foreign.epoch++;
        deniedWithoutMutation([&]{value.proposeJobControl(foreign,1,"family:21","invalid");},"Foreign receiver refused before malformed command decoding");
        foreign=grant;foreign.receiver++;
        deniedWithoutMutation([&]{value.proposeJobControl(foreign,1,"family:21",cancel(job));},"Actual wrong target receiver refused");
        foreign=grant;foreign.frontend++;
        deniedWithoutMutation([&]{value.proposeJobControl(foreign,1,"family:21",cancel(job));},"Actual stale frontend grant refused");
        auto other=job;other.request.value++;
        deniedWithoutMutation([&]{propose(cancel(other));},"Wrong original job cannot obtain reserved cleanup ticket");
        deniedWithoutMutation([&]{value.proposeJobControl(grant,1,"family:22",cancel(job));},"Foreign family cannot consume native credit");
        deniedWithoutMutation([&]{propose("{\"kind\":\"cancel\",\"kind\":\"acquire\"}");},"Duplicate command discriminant refused");
        deniedWithoutMutation([&]{propose(ack(job,1));},"Invented terminal proof refused before ordinal issuance");
        deniedWithoutMutation([&]{propose("{\"kind\":\"reconcile\"}");},"Different native control domain refused by job issuer");
        auto ticket=propose(cancel(job));check(ticket && !ticket->alreadyDelivered && ticket->ticket.ordinal==1,"Native purpose selects original cancel slot and ordinal");
        check(bank.issued()==1 && bank.reserved()==7 && bank.ticketCount()==1,"One reserved job slot consumed without effect invocation");
        check(endpoint.native([&](auto& broker){return broker.recordCount()==1 && broker.charge()==4096 && !broker.inspect()[0].terminal;}),"Issuing transport ticket does not claim or perform cleanup");
        auto duplicate=propose(cancel(job));check(duplicate && !duplicate->alreadyDelivered && duplicate->ticket.wire==ticket->ticket.wire && bank.issued()==1,"Exact cancel proposal reuses original immutable ticket");
        const auto changed=cancel(job)+" ";
        deniedWithoutMutation([&]{propose(changed);},"Changed bytes cannot replace original native purpose slot");
        check(bank.ownsTicket(grant,1,ticket->ticket.wire),"Native original wire must be owned before C invocation");
        check(preview_control_delivery_receive(&channel,grant,1,ticket->ticket.wire.c_str(),ticket->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Original C prefix admits one native ticket");
        check(value.command(1,"family:21",cancel(job))=="[]" && preview_control_delivery_complete(&channel,1),"Actual native cancel and producer refusal return separately from receipt");
        check(preview_control_delivery_confirm(&channel,grant,1),"Original frontend confirms cancel receipt");
        const auto records=endpoint.native([](auto& broker){return broker.inspect();});check(records.size()==1 && records[0].terminal && records[0].proofs.size()==2,"Actual native two-proof cancellation/refusal");
        const auto final=ack(job,records[0].proofs.back().sequence.value);
        deniedWithoutMutation([&]{propose(ack(job,records[0].proofs.back().sequence.value+1));},"Future terminal sequence cannot consume cleanup credit");
        auto acknowledged=propose(final);check(acknowledged && acknowledged->ticket.ordinal==2 && !acknowledged->alreadyDelivered,"Actual native final proof determines stable ACK slot");
        check(preview_control_delivery_receive(&channel,grant,2,acknowledged->ticket.wire.c_str(),acknowledged->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Original C prefix admits final ACK ticket");
        check(delivery.acknowledge(77,"family:21",final) && preview_control_delivery_complete(&channel,2),"Actual native journal acknowledgment removes original record");
        check(endpoint.native([](auto& broker){return !broker.recordCount() && !broker.charge();}),"Actual record and bytes settled without a transport inference");
        for(unsigned i=0;i<25;++i){auto repeated=propose(final);check(repeated && !repeated->alreadyDelivered && repeated->ticket.wire==acknowledged->ticket.wire && bank.issued()==2,"Exact post-effect ACK proposal reuses original ticket despite absent Broker record");}
        auto blocked=value.resumeAtReceiver(77,grant.epoch,1,2,2);
        check(!blocked.native.job && controls->confirmedJobCount()==0 && controls->jobCount()==1,"Unconfirmed original ACK cannot become a tombstone or free job credits");
        check(preview_control_delivery_confirm(&channel,grant,2),"Original frontend separately confirms final ACK");
        auto resumed=value.resumeAtReceiver(77,grant.epoch,1,2,2);check(resumed.native.job && resumed.native.job->request.value==2,"Actual resume reserves a new job after original settlement");
        check(controls->confirmedJobCount()==1 && controls->jobCount()==1 && bank.issued()==2 && bank.ticketCount()==0,"One bounded confirmed predecessor retains exact old transport identity");
        auto old=propose(final);check(old && old->alreadyDelivered && old->ticket.wire==acknowledged->ticket.wire && bank.issued()==2,"Confirmed exact old ACK is delivered disposition without new issuance");
        check(!bank.ownsTicket(grant,old->ticket.ordinal,old->ticket.wire),"Confirmed predecessor cannot authorize another effect invocation");
        auto oldCancel=propose(cancel(job));check(oldCancel && oldCancel->alreadyDelivered && oldCancel->ticket.wire==ticket->ticket.wire,"Confirmed old cancel can only report original delivered identity");
        deniedWithoutMutation([&]{propose(final+" ");},"Changed stale ACK bytes cannot assert delivered disposition");
        foreign=grant;foreign.epoch++;
        deniedWithoutMutation([&]{value.proposeJobControl(foreign,1,"family:21",final);},"Confirmed history does not admit another receiver epoch");
        const auto current=*resumed.native.job;auto currentCancel=propose(cancel(current));
        check(currentCancel && currentCancel->ticket.ordinal==3 && !currentCancel->alreadyDelivered,"Fresh original job gets next native ordinal without resetting namespace");
        check(preview_control_delivery_receive(&channel,grant,3,currentCancel->ticket.wire.c_str(),currentCancel->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Current original cancel invocation");
        value.command(1,"family:21",cancel(current));check(preview_control_delivery_complete(&channel,3) && preview_control_delivery_confirm(&channel,grant,3),"Current original cancel receipt confirmation");
        const auto nextRecords=endpoint.native([](auto& broker){return broker.inspect();});const auto nextAck=ack(current,nextRecords[0].proofs.back().sequence.value);
        auto nextTicket=propose(nextAck);check(nextTicket && nextTicket->ticket.ordinal==4,"Actual next proof chooses its own immutable slot");
        check(preview_control_delivery_receive(&channel,grant,4,nextTicket->ticket.wire.c_str(),nextTicket->ticket.wire.size())==PREVIEW_CONTROL_INVOKE && delivery.acknowledge(77,"family:21",nextAck),"Actual next job terminal ACK settles record");
        check(preview_control_delivery_complete(&channel,4) && preview_control_delivery_confirm(&channel,grant,4),"Actual next terminal receipt confirmed");
        auto third=value.resumeAtReceiver(77,grant.epoch,1,3,3);check(third.native.job && controls->confirmedJobCount()==1,"Confirmed predecessor cache stays one per retained native actor");
        deniedWithoutMutation([&]{propose(final);},"Older-than-retained job cannot invent delivered history");
        check(propose(nextAck)->alreadyDelivered && bank.issued()==4,"Exact immediate predecessor remains usable without ordinal issuance");
        // Pure metadata fixture teardown. Unused actor/reconciliation credits
        // remain; no real native actor/host close qualification is asserted.
        endpoint.native([&](auto& broker){broker.cancel(1,binding,*third.native.job);broker.producerRefused(1,*third.native.job);});
        const auto ended=endpoint.native([](auto& broker){return broker.inspect();});
        check(delivery.acknowledge(77,"family:21",ack(*third.native.job,ended[0].proofs.back().sequence.value)),"Normal fixture terminal settlement without capture");
    }
    server.finish();std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"normalOwnedExit\":true,\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}

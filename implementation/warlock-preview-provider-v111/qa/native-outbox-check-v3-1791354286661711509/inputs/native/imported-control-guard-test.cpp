#define main retained_original_channel_fixture
#include "actor-retirement-channel-test-v2.cpp"
#undef main
int main(){try {
    Server server("turnover");
    {
        auto native=server.open();ImportedClients value(*native,256);auto& endpoint=value.endpoint();const auto binding=native->binding();
        check(endpoint.registerControlView(77,binding),"Original actual empty receiver before any job");
        auto view=endpoint.registeredView(77);check(view && view->entries.empty(),"No fabricated native subject");
        PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,77,view->epoch};
        PreviewControlDelivery channel{};check(preview_control_delivery_init(&channel,grant),"Actual endpoint grant/epoch");
        ControlReservations bank(channel,1);std::unique_ptr<ImportedControlAdmission> controls;
        endpoint.native([&](auto& broker){controls=std::make_unique<ImportedControlAdmission>(bank,grant,broker,256);});
        value.attachControlAdmission(*controls,grant);
        const auto before=native->next();auto result=value.tryStartAtReceiver(77,grant.epoch,1,{21},1,1);
        check(result.intent==ImportedIntentLedger::Admission::Capacity && !result.native.job && result.events=="[]","Actual ImportedClients refuses before job/intent issuance");
        check(native->next()==before+2,"Only original source observation, no physical capture query");
        check(!value.originalIntent(1) && !value.hasJob(1) && endpoint.registeredView(77)->entries.empty(),"Capacity preserves intent/frame/receiver membership");
        check(endpoint.nativeDemand([](auto& queue){return !queue.slotCount() && !queue.nativeBroker().actorCount() && !queue.nativeBroker().recordCount() && !queue.nativeBroker().charge();}),"All actual native actor/job/physical owners remain empty");
        check(bank.reserved()==1 && bank.issued()==0 && bank.reservationCount()==1,"Binding credit untouched by insufficient actor/job capacity");
        const auto receiverless=native->next();
        check(denied([&]{value.tryStart(1,{21},1,1,0);}) && native->next()==receiverless+1,"Controlled legacy receiverless start refuses before source query");
        check(denied([&]{value.attachControlAdmission(*controls,grant);}),"Repeated attachment cannot reset controlled ownership");
    }
    {
        auto native=server.open();ImportedClients value(*native,256);auto& endpoint=value.endpoint();const auto binding=native->binding();
        check(endpoint.registerControlView(77,binding),"Fresh original actual receiver");const auto epoch=endpoint.registeredView(77)->epoch;
        PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,77,epoch};PreviewControlDelivery channel{};
        check(preview_control_delivery_init(&channel,grant),"Fresh endpoint original epoch");ControlReservations bank(channel,1065);
        std::unique_ptr<ImportedControlAdmission> controls;
        endpoint.native([&](auto& broker){controls=std::make_unique<ImportedControlAdmission>(bank,grant,broker,256);});
        value.attachControlAdmission(*controls,grant);
        auto started=value.tryStartAtReceiver(77,epoch,1,{21},1,1);
        check(started.native.job && started.native.status==preview::demand::Attempt::Status::Started && value.hasJob(1),"Actual native start under pre-admission reservation");
        const auto original=*started.native.job;
        check(controls->retainedJob(1)==started.native.job && bank.reserved()==8 && bank.reservationCount()==3,"Original job has native actor/job/reconciliation credits");
        check(value.originalIntent(1)->deadline==original.deadline && endpoint.native([&](auto& broker){return broker.requestFloor(1)==1;}),"Original issued request and deadline retained");
        check(endpoint.registeredView(77)->epoch==epoch && endpoint.registeredView(77)->entries==std::set<uint64_t>{1},"Native membership extends original epoch");
        endpoint.native([&](auto& broker){check(denied([&]{ImportedControlAdmission duplicate(bank,grant,broker,256);}),"Second obligation manager refuses");});
        check(bank.reserved()==8 && bank.reservationCount()==3,"Duplicate manager consumes no speculative credit");
        ReceiptDelivery delivery(endpoint,binding,77);
        auto body=[&](std::string command){return std::string("{\"identity\":\"family:21\",\"commands\":[")+command+"]}";};
        const auto cancel=Wire().text("kind","cancel").begin("job").job(original).end().finish();
        auto ticket=bank.issue(grant,controls->jobReservation(1),2,body(cancel));check(ticket && ticket->ordinal==1,"Native reserved cancel ticket");
        check(preview_control_delivery_receive(&channel,grant,ticket->ordinal,ticket->wire.c_str(),ticket->wire.size())==PREVIEW_CONTROL_INVOKE,"Original C prefix accepts one cancel");
        check(value.command(1,"family:21",cancel)=="[]","Actual ImportedClients cancel without replaying capture");
        check(preview_control_delivery_complete(&channel,1) && preview_control_delivery_confirm(&channel,grant,1),"Original cancel delivery separately confirmed");
        const auto terminal=endpoint.native([](auto& broker){return broker.inspect();});
        check(terminal.size()==1 && terminal[0].terminal && terminal[0].proofs.size()==2 && !terminal[0].bytes,"Actual cancelled/refused terminal proof bound");
        const auto sequence=terminal[0].proofs.back().sequence.value;
        const auto ack=Wire().text("kind","acknowledge").begin("job").job(original).end().counter("sequence",sequence).finish();
        auto acknowledged=bank.issue(grant,controls->jobReservation(1),5,body(ack));check(acknowledged && acknowledged->ordinal==2,"Native reserved final proof ACK ticket");
        check(preview_control_delivery_receive(&channel,grant,2,acknowledged->wire.c_str(),acknowledged->wire.size())==PREVIEW_CONTROL_INVOKE,"Original C ACK invocation");
        check(delivery.acknowledge(77,"family:21",ack),"Actual original terminal proof ACK drains physical Broker");
        check(preview_control_delivery_complete(&channel,2),"Original ACK dispatcher returned but receipt not confirmed");
        const auto blocked=native->next();auto refused=value.resumeAtReceiver(77,epoch,1,2,2);
        check(refused.intent==ImportedIntentLedger::Admission::Capacity && !refused.native.job && native->next()==blocked+1,"Unconfirmed old control blocks actual resume before new source query");
        check(value.job(1)==original && value.lease(1)==1 && value.originalIntent(1)->deadline==original.deadline && bank.issued()==2,"Blocked resume preserves original job/deadline/lease and namespace");
        check(preview_control_delivery_confirm(&channel,grant,2),"Original final ACK frontend confirmation");
        auto resumed=value.resumeAtReceiver(77,epoch,1,2,2);
        check(resumed.native.job && resumed.native.status==preview::demand::Attempt::Status::Started && resumed.native.job->request.value==2,"Confirmed actual native resume preserves request floor");
        check(controls->retainedJob(1)==resumed.native.job && bank.issued()==2 && bank.reserved()==8 && bank.reservationThrough()==4,"New native cleanup reserved without control prefix reset");
        check(!bank.ownsTicket(grant,1,ticket->wire) && !bank.ownsTicket(grant,2,acknowledged->wire),"Released confirmed original tickets cannot grant another invocation");
        check(value.lease(1)==2 && endpoint.registeredView(77)->epoch==epoch,"Actual receiver and new picker lease preserved");
        const auto old=native->next();
        check(denied([&]{value.resume(1,3,3);}) && native->next()==old+1,"Controlled legacy receiverless resume refuses before source query");
        const auto current=value.job(1);endpoint.native([&](auto& broker){broker.cancel(1,binding,current);broker.producerRefused(1,current);});
        const auto ended=endpoint.native([](auto& broker){return broker.inspect();});
        check(delivery.acknowledge(77,"family:21",Wire().text("kind","acknowledge").begin("job").job(current).end().counter("sequence",ended[0].proofs.back().sequence.value).finish()),"Owned fixture terminal teardown without capture");
    }
    {
        auto native=server.open();ImportedClients value(*native,256);auto& endpoint=value.endpoint();const auto binding=native->binding();
        check(endpoint.registerControlView(77,binding),"Fresh receiver for wrong-Broker witness");
        PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,77,endpoint.registeredView(77)->epoch};
        PreviewControlDelivery channel{};check(preview_control_delivery_init(&channel,grant),"Original mismatch-test channel");ControlReservations bank(channel,1065);
        preview::Broker foreign(ImportedClients::allocationLimits(256));ImportedControlAdmission wrong(bank,grant,foreign,256);
        check(denied([&]{value.attachControlAdmission(wrong,grant);}),"Another Broker cannot attach to original receiver");
        check(!value.hasJob(1) && !value.originalIntent(1) && endpoint.registeredView(77)->entries.empty(),"Foreign attachment cannot change native ownership");
    }
    server.finish();std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"normalOwnedExit\":true,\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}

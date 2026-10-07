#include "imported_clients.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static unsigned checks=0;
static void check(bool value,const char* message){require(value,message);++checks;}
static fd::Header header(const ClientCapture& c) {
    fd::Header h{};h[fd::Magic]=fd::MAGIC;h[fd::Version]=1;
    h[fd::Lifetime]=c.binding.lifetime.value;h[fd::Session]=c.binding.session.value;h[fd::Frontend]=c.binding.frontend.value;
    h[fd::Request]=c.request+1;h[fd::Capture]=c.request;h[fd::Subject]=c.context.incarnation.value;h[fd::Output]=c.context.output.value;
    h[fd::Completed]=c.completed;h[fd::Now]=c.completed+1;h[fd::Width]=c.width;h[fd::Height]=c.height;h[fd::Bytes]=c.bytes;h[fd::Charge]=4096;
    h[fd::Transfer]=c.request+2;h[fd::CRC]=c.crc;h[fd::Privacy]=c.context.privacy.value;h[fd::Rendering]=c.context.rendering.value;
    h[fd::Scene]=c.context.scene.value;h[fd::Content]=c.context.content.value;h[fd::Flags]=11;h[fd::Deadline]=c.deadline;h[fd::Expires]=500;
    return h;
}
int main(){try {
    SourceObservation source{{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},{1},102,true,true,false,true},1,4096,1,SourceObservation::Kind::UnqualifiedClientMain,false};
    Job job{source.scope.binding,source.scope.context,{1},{1},source.scope.clock,200};
    ClientCapture capture{job.binding,job.context,10,100,job.deadline,320,240,16,4096,0};const auto h=header(capture);
    check(importedClientTime(h,capture,job,source).has_value(),"Current own native imported authority");
    auto stopped=source;stopped.scope.sourceLive=false;stopped.scope.context.scene.value++;stopped.scope.context.content.value++;
    check(importedClientTime(h,capture,job,stopped).has_value(),"Source stop preserves independently owned Historical pixels");
    for(unsigned mutation=0;mutation<23;++mutation) {
        auto bad=source;
        switch(mutation) {
            case 0:bad.scope.binding.lifetime.value++;break;
            case 1:bad.scope.binding.session.value++;break;
            case 2:bad.scope.binding.frontend.value++;break;
            case 3:bad.scope.context.lifetime.value++;break;
            case 4:bad.scope.context.incarnation.value++;break;
            case 5:bad.scope.clock.value++;break;
            case 6:bad.scope.context.output.value++;break;
            case 7:bad.scope.context.privacy.value++;break;
            case 8:bad.scope.context.rendering.value++;break;
            case 9:bad.scope.context.scene.value--;break;
            case 10:bad.scope.context.content.value--;break;
            case 11:bad.scope.present=false;break;
            case 12:bad.scope.locked=true;break;
            case 13:bad.scope.gpuReady=false;break;
            case 14:bad.scope.now=h[fd::Now]-1;break;
            case 15:bad.scope.now=h[fd::Expires];break;
            case 16:bad.kind=SourceObservation::Kind::UnqualifiedRootMonitorPlane;break;
            case 17:bad.previewEligible=true;break;
            case 18:bad.observation=0;break;
            case 19:bad.request=0;break;
            case 20:bad.maximumTransferBytes=0;break;
            case 21:bad.maximumTransferBytes=4095;break;
            case 22:bad.maximumTransferBytes=8;break;
        }
        check(!importedClientTime(h,capture,job,bad),"Foreign/incoherent/locked/expired source cannot serve imported bytes");
    }
    for(auto word:{fd::Magic,fd::Version,fd::Status,fd::Lifetime,fd::Session,fd::Frontend,fd::Capture,fd::Subject,fd::Output,fd::Completed,fd::Width,fd::Height,fd::Bytes,fd::Charge,fd::CRC,fd::Privacy,fd::Rendering,fd::Scene,fd::Content,fd::Deadline}) {
        auto bad=h;++bad[word];check(!importedClientTime(bad,capture,job,source),"Original frame identity and captured revisions remain exact");
    }
    for(auto flags:{0ULL,3ULL,4ULL,7ULL,8ULL,9ULL,10ULL,15ULL,27ULL}) {
        auto bad=h;bad[fd::Flags]=flags;check(!importedClientTime(bad,capture,job,source),"Unknown/foreign frame planes refused");
    }
    {auto bad=job;bad.deadline++;check(!importedClientTime(h,capture,bad,source),"Original issued deadline cannot renew");}
    {auto bad=job;bad.context.content.value++;check(!importedClientTime(h,capture,bad,source),"Original captured content cannot relabel");}
    {auto bad=job;bad.clock.value++;check(!importedClientTime(h,capture,bad,source),"Original native clock cannot substitute");}
    ImportedNativeOwnership ownership(capture,h);unsigned releases=0,retirements=0;bool releaseOK=false;ClientRetirement result=ClientRetirement::PendingLock;
    auto release=[&](const ClientCapture& c,uint64_t transfer){++releases;check(c.binding==capture.binding && c.request==capture.request && transfer==h[fd::Transfer],"Exact original native release correlation");return releaseOK;};
    auto retire=[&]{++retirements;return result;};
    check(!ownership.settle(release,retire) && releases==1 && retirements==0 && !ownership.exportReleased(),"Failed export release imputes no retirement");
    releaseOK=true;
    check(!ownership.settle(release,retire) && releases==2 && retirements==1 && ownership.exportReleased() && ownership.pendingLock() && !ownership.producerRetired(),"Locked retirement remains a retained backend obligation");
    check(!ownership.settle(release,retire) && releases==2 && retirements==2,"Retry does not release an already acknowledged export");
    result=ClientRetirement::Retired;
    check(ownership.settle(release,retire) && releases==2 && retirements==3 && ownership.producerRetired() && !ownership.pendingLock(),"Only exact native retirement settles producer");
    check(ownership.settle(release,retire) && releases==2 && retirements==3,"Settled native ownership is idempotent");
    {
        ImportedNativeOwnership unknown(capture,h);bool rejected=false;
        try{unknown.settle([](const auto&,auto){return true;},[]{return static_cast<ClientRetirement>(2);});}catch(const std::exception&){rejected=true;}
        check(rejected && unknown.exportReleased() && !unknown.producerRetired(),"Unknown retirement never becomes physical completion");
    }
    // Actual sealed mappings, one physical Broker, two subjects and held GIO
    // readers. Native acknowledgments below are synthetic; native IPC is a
    // separate campaign using ImportedClients, not claimed by this control.
    std::map<uint64_t,SourceObservation> scopes{{1,source},{2,source}};scopes[2].scope.context.incarnation.value=14;
    std::map<uint64_t,ClientCapture> captures;std::map<uint64_t,fd::Header> headers;std::map<uint64_t,Job> jobs;
    uri::Endpoint endpoint({2,8,2,8192},4,1,[&](uint64_t entry){return importedClientTime(headers.at(entry),captures.at(entry),jobs.at(entry),scopes.at(entry));});
    check(endpoint.enableDemand({{2,8,2,8192},{1},{1},1}),"One shared physical Broker for two imported families");
    std::map<uint64_t,Packet> packets;std::map<uint64_t,fd::Mapped*> mappings;
    for(uint64_t entry=1;entry<=2;++entry) {
        auto& s=scopes.at(entry);s.scope.now=90+entry;
        endpoint.nativeDemand([&](auto& q){check(q.observe({entry,1,s.scope,{1},4096,true}).accepted,"Own distinct family demand");const auto attempt=q.start(entry,200);check(attempt.job.has_value(),"Original native-scoped reservation");jobs[entry]=*attempt.job;});
        auto c=capture;c.context=jobs[entry].context;c.request=10*entry;captures[entry]=c;headers[entry]=header(c);s.scope.now=102;
        const std::array<uint8_t,16> png{137,80,78,71,13,10,26,10,static_cast<uint8_t>(entry),2,3,4,5,6,7,8};
        auto mapping=std::make_unique<fd::Mapped>(fd::seal(png),headers[entry],4096,fd::SourcePlane::ClientMain);mappings[entry]=mapping.get();std::unique_ptr<const Buffer> payload=std::move(mapping);
        endpoint.native([&](auto& b){check(b.allocate(entry,jobs[entry],payload,500).receipts.size()==1 && !payload,"Sealed FD and mapping physically adopted");packets[entry]=*b.producerComplete(entry,jobs[entry]).receipts.at(0).packet;});
        ImportedNativeOwnership nativeOwnership(c,headers[entry]);
        check(nativeOwnership.settle([](const auto&,auto){return true;},[]{return ClientRetirement::Retired;}),"Synthetic exact backend acknowledgments");
        endpoint.native([&](auto& b){check(b.charge()==4096*entry && b.recordCount()==entry && b.nextProofSequence()==2*entry+1 && !b.consumerComplete(entry,jobs[entry]) && !mappings[entry]->png().empty(),"Native handoff does not erase local storage, charge or journal");});
    }
    check(packets[1].token!=packets[2].token,"Distinct images have distinct opaque native tokens");
    check(endpoint.registerView(77,job.binding,{1,2}),"One admitted receiver for both families");ReceiptDelivery delivery(endpoint,job.binding,77);
    std::map<uint64_t,GInputStream*> held;
    for(uint64_t entry=1;entry<=2;++entry) {
        GError* error=nullptr;gsize size{};held[entry]=endpoint.open(77,uri::encode(packets[entry].token),&size,&error);
        check(held[entry] && !error && size==16,"Actual imported URI after backend retirement");
        std::array<uint8_t,9> bytes{};check(g_input_stream_read(held[entry],bytes.data(),bytes.size(),nullptr,&error)==9 && !error && bytes[8]==entry,"Distinct independently mapped family bytes readable");
    }
    scopes[1].scope.sourceLive=false;scopes[1].scope.context.scene.value++;
    {GError* error=nullptr;uint8_t byte{};check(g_input_stream_read(held[1],&byte,1,nullptr,&error)==1 && !error,"Held immutable Historical storage after actual read guard source stop");}
    scopes[2].scope.locked=true;
    {GError* error=nullptr;uint8_t byte{};check(g_input_stream_read(held[2],&byte,1,nullptr,&error)==-1 && error && error->code==G_IO_ERROR_PERMISSION_DENIED,"Native lock guard denies held reader before cached policy updates");g_clear_error(&error);gsize size{};auto denied=endpoint.open(77,uri::encode(packets[2].token),&size,&error);check(!denied && error,"Native lock guard denies new URI before cached policy updates");g_clear_error(&error);}
    for(uint64_t entry=1;entry<=2;++entry) {
        endpoint.native([&](auto& b){b.release(entry,jobs[entry].binding,jobs[entry],packets[entry].token);check(!b.consumerComplete(entry,jobs[entry]) && b.charge()==(3-entry)*4096,"Held readers retain physical charge after native backend handoff");});
        GError* error=nullptr;check(g_input_stream_close(held[entry],nullptr,&error) && !error,"Actual imported GIO reader closes");g_object_unref(held[entry]);
        endpoint.native([&](auto& b){check(b.consumerComplete(entry,jobs[entry]),"Only actual reader drain admits local consumer completion");check(mappings[entry]->close() && mappings[entry]->png().empty(),"Actual imported mmap and FD close");auto terminal=b.destroy(entry,jobs[entry]);check(terminal.status==Result::Status::Complete && terminal.receipts.back().sequence.value==4+entry && b.recordCount()==3-entry,"Local terminal proof remains until exact final ACK");});
        check(!delivery.pending(77).empty(),"Original terminal delivery retained");
        Wire ack;check(delivery.acknowledge(77,"family:"+std::to_string(jobs[entry].context.incarnation.value),ack.text("kind","acknowledge").begin("job").job(jobs[entry]).end().counter("sequence",4+entry).finish()),"Exact shared original terminal ACK");
    }
    check(endpoint.readers()==0 && endpoint.native([](auto& b){return b.charge()==0 && b.recordCount()==0;}),"Both physical images and journals finally empty");
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"scope\":\"Imported frame authority and backend ownership controls; actual sealed-FD/Broker/GIO/two-family terminal delivery with synthetic native scope and acknowledgments\"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

#include "imported_lifecycle.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
struct PNG final:uri::Payload {
    std::array<uint8_t,16> bytes{137,80,78,71,13,10,26,10,1,2,3,4,5,6,7,8};
    uint64_t charge()const noexcept override{return 32;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
struct Frame {
    SourceObservation source;
    Job job{},original{};
    uint64_t lease{1};
    std::optional<Packet> packet,originalPacket;
    std::weak_ptr<const Buffer> storage;
    GInputStream* held{};
};
int main(){try {
    Frame first{},second{};
    first.source={{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},{1},1,true,true,false,true},1,32,1,SourceObservation::Kind::UnqualifiedClientMain,false};
    second.source=first.source;second.source.scope.context.incarnation.value=10;second.source.scope.now=2;second.source.observation=2;second.source.request=2;
    uint64_t now=2;uri::Endpoint endpoint({2,8,2,64},4,2,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{1},now};});
    require(endpoint.enableDemand({{2,8,2,64},{1},{1},1}),"One shared two-entry demand authority");
    endpoint.native([&](auto& b){require(b.enroll(1,first.source.scope,32) && b.enroll(2,second.source.scope,32),"Native fixture actors independently enrolled");});
    require(endpoint.registerView(77,first.source.scope.binding,{1,2}),"One own URI reader view");ReceiptDelivery delivery(endpoint,first.source.scope.binding,77);
    auto readable=[&](Frame& f){
        if(!f.packet || f.storage.expired())return false;
        GError* error=nullptr;gsize length{};auto stream=endpoint.open(77,uri::encode(f.packet->token),&length,&error);
        if(!stream){require(error && error->code==G_IO_ERROR_PERMISSION_DENIED,"Exact actual URI refusal");g_clear_error(&error);return false;}
        uint8_t byte{};require(length==16 && g_input_stream_read(stream,&byte,1,nullptr,&error)==1 && !error && byte==137,"Actual immutable storage byte read");
        require(g_input_stream_close(stream,nullptr,&error) && !error,"Actual projection stream closed");g_object_unref(stream);return true;
    };
    auto project=[&](uint64_t entry,Frame& f){
        const bool read=readable(f);
        return endpoint.native([&](auto& b){
            unsigned records=0;bool charged=false,cleanup=false,terminal=false;
            for(const auto& row:b.inspect())if(row.entry==entry){require(row.job==f.job,"Exact own current model job");records++;charged=row.bytes>0;cleanup=row.cleanup;terminal=row.terminal;
                if(row.packet)require(f.packet && row.packet->token==f.packet->token && row.packet->expires==f.packet->expires,"Exact retained packet, not a renewed lease");}
            if(f.originalPacket)require(f.original.request.value==1 && f.original.deadline==(entry==1?2000000001ULL:2000000002ULL) && f.originalPacket->expires==f.original.deadline+3000000000ULL,"Original job/deadline/expiry never renewed");
            Wire w;return w.integer("job",f.job.request.value).integer("floor",b.requestFloor(entry)).integer("deadline",f.job.deadline).integer("expires",f.packet?f.packet->expires:0).integer("lease",f.lease)
                .integer("records",records).boolean("charged",charged).boolean("mapped",!f.storage.expired()).boolean("held",f.held).boolean("cleanup",cleanup).boolean("terminal",terminal).boolean("live",f.source.scope.sourceLive).boolean("readable",read).finish();
        });
    };
    auto finalAck=[&](uint64_t entry,Frame& f){
        const auto sequence=endpoint.native([&](auto& b){for(const auto& row:b.inspect())if(row.entry==entry && row.terminal)return row.proofs.back().sequence.value;return uint64_t{0};});
        require(sequence,"Exact final proof retained until acknowledgement");Wire ack;
        require(delivery.acknowledge(77,"family:"+std::to_string(f.job.context.incarnation.value),ack.text("kind","acknowledge").begin("job").job(f.job).end().counter("sequence",sequence).finish()),"Actual exact per-entry terminal ACK");
    };
    std::string event;
    while(std::getline(std::cin,event)) {
        bool accepted=false;const uint64_t entry=event.ends_with('2')?2:1;auto& f=entry==1?first:second;
        if(event=="Init"){}
        else if(event.starts_with("Reserve")) {
            endpoint.nativeDemand([&](auto& q){require(q.observe({entry,1,f.source.scope,{1},32,true}).accepted,"Own original demand");const auto a=q.start(entry,f.source.scope.now+2000000000ULL);require(a.job.has_value(),"Own original job reservation");f.job=*a.job;f.original=f.job;});
        }else if(event.starts_with("Capture")) {
            endpoint.native([&](auto& b){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();require(b.allocate(entry,f.job,payload,f.job.deadline+3000000000ULL).receipts.size()==1 && !payload,"Actual immutable buffer adoption");f.packet=*b.producerComplete(entry,f.job).receipts.at(0).packet;f.storage=b.fetch(entry,f.job.binding,f.packet->token);
                require(!f.storage.expired(),"Actual own retained storage");if(!f.originalPacket)f.originalPacket=f.packet;else require(f.packet->token!=f.originalPacket->token,"New token does not alias old frame");});
        }else if(event.starts_with("Hold")) {
            GError* error=nullptr;gsize length{};require(!f.held && f.packet,"Own one held reader");f.held=endpoint.open(77,uri::encode(f.packet->token),&length,&error);require(f.held && !error,"Actual held original stream");
        }else if(event.starts_with("Close")) {
            require(f.held,"Held actual reader to drain");GError* error=nullptr;require(g_input_stream_close(f.held,nullptr,&error) && !error,"Actual reader closure");g_object_unref(f.held);f.held=nullptr;
        }else if(event.starts_with("Release"))endpoint.native([&](auto& b){b.release(entry,f.job.binding,f.job,f.packet->token);});
        else if(event.starts_with("Drain"))endpoint.native([&](auto& b){if(b.consumerComplete(entry,f.job))require(b.destroy(entry,f.job).status==Result::Status::Complete,"Actual local storage destruction and terminal proof");});
        else if(event.starts_with("Ack"))finalAck(entry,f);
        else if(event=="Stop2") {
            second.source.scope.sourceLive=false;second.source.scope.context.scene.value++;second.source.scope.now=3;second.source.observation++;second.source.request++;now=3;
            require(endpoint.native([&](auto& b){return b.observe(2,second.source.scope,32);}),"Actual coherent stopped source admission");
        }else if(event.starts_with("Present")) {
            auto current=second.source;if(event=="PresentForeign2")current.scope.binding.frontend.value++;
            bool rejected=false;
            try {accepted=endpoint.native([&](auto& b){return admitRetainedImportedPresentation(b,2,second.job,current,*second.packet,second.lease,2,event=="PresentOld2"?1:2);});}
            catch(const std::exception&){rejected=true;}
            require(rejected==(event=="PresentForeign2"),"Only exact foreign presentation scope rejected");if(accepted)second.lease=2;
        }else if(event.starts_with("Resume")) {
            auto fresh=first.source;fresh.scope.now=4;fresh.observation=4;fresh.request=4;
            if(event=="ResumeForeign1")fresh.scope.binding.frontend.value++;
            if(event=="ResumeStopped1"){fresh.scope.sourceLive=false;fresh.scope.context.scene.value++;}
            if(event=="ResumeCostly1")fresh.maximumTransferBytes=65;
            const auto publication=event=="ResumeMissing1"?0:2,lease=event=="ResumeOld1"?1:2;
            std::optional<Job> next;bool rejected=false;
            try {next=endpoint.nativeDemand([&](auto& q){return reserveImportedResume(q,1,first.job,first.source,first.lease,fresh,publication,lease);});}
            catch(const std::exception&){rejected=true;}
            require(rejected==(event=="ResumeForeign1"),"Only exact foreign new-demand scope rejected");
            if(next){require(first.storage.expired() && !first.held,"Actual own storage must retire before next job");first.source=fresh;first.job=*next;first.lease=2;first.packet.reset();now=4;accepted=true;}
        }else if(event=="OldAck1") {
            Wire ack;require(!delivery.acknowledge(77,"family:4",ack.text("kind","acknowledge").begin("job").job(first.original).end().counter("sequence",5).finish()),"Old final ACK cannot erase resumed resource");
        }else require(false,"Explicitly selected shared lifecycle event");
        std::cout<<"{\"first\":"<<project(1,first)<<",\"second\":"<<project(2,second)<<",\"nextProof\":"<<endpoint.native([](auto& b){return b.nextProofSequence();})<<",\"accepted\":"<<(accepted?"true":"false")<<"}\n";
    }
    require(!first.held && !second.held && first.storage.expired() && second.storage.expired() && endpoint.readers()==0 && endpoint.native([](auto& b){return b.recordCount()==0 && b.charge()==0;}),"Every selected trace drains actual physical/journal/reader ownership");
    endpoint.unregisterView(77);return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

#include "imported_clients.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
struct OwnedFrame {
    SourceObservation source;
    Job job{};
    std::optional<ClientCapture> capture;
    fd::Header header{};
    std::optional<ImportedNativeOwnership> ownership;
    std::optional<Packet> packet;
    fd::Mapped* mapping{};
    GInputStream* held{};
};
static fd::Header header(const ClientCapture& c) {
    fd::Header h{};h[fd::Magic]=fd::MAGIC;h[fd::Version]=1;h[fd::Lifetime]=c.binding.lifetime.value;h[fd::Session]=c.binding.session.value;h[fd::Frontend]=c.binding.frontend.value;
    h[fd::Request]=c.request+1;h[fd::Capture]=c.request;h[fd::Subject]=c.context.incarnation.value;h[fd::Output]=c.context.output.value;
    h[fd::Completed]=c.completed;h[fd::Now]=c.completed+1;h[fd::Width]=320;h[fd::Height]=240;h[fd::Bytes]=16;h[fd::Charge]=4096;h[fd::Transfer]=c.request+2;
    h[fd::Privacy]=c.context.privacy.value;h[fd::Rendering]=c.context.rendering.value;h[fd::Scene]=c.context.scene.value;h[fd::Content]=c.context.content.value;
    h[fd::Flags]=11;h[fd::Deadline]=c.deadline;h[fd::Expires]=500;return h;
}
int main(){try {
    std::map<uint64_t,OwnedFrame> frames;
    for(uint64_t id=1;id<=2;++id) {
        OwnedFrame f{};f.source={{{{1},{2},{3}},{{1},{id+3},{5},{6},{7},{8},{9}},{1},90+id,true,true,false,true},1,4096,1,SourceObservation::Kind::UnqualifiedClientMain,false};frames.emplace(id,std::move(f));
    }
    uri::Endpoint endpoint({2,8,2,8192},4,1,[&](uint64_t id)->std::optional<uri::NativeTime>{auto& f=frames.at(id);return f.capture?importedClientTime(f.header,*f.capture,f.job,f.source):std::nullopt;});
    require(endpoint.enableDemand({{2,8,2,8192},{1},{1},1}),"One imported model physical broker");
    // The view is enrolled after both subjects have their actual native actor
    // slots. No job or physical allocation is invented by view enrollment.
    endpoint.native([&](auto& b){for(auto& [id,f]:frames)require(b.enroll(id,f.source.scope,4096),"Distinct native model subjects");});
    require(endpoint.registerView(77,frames.at(1).source.scope.binding,{1,2}),"One exact model URI receiver");
    ReceiptDelivery delivery(endpoint,frames.at(1).source.scope.binding,77);
    auto probe=[&](uint64_t id) {
        auto& f=frames.at(id);if(!f.packet || !f.mapping)return false;
        GError* error=nullptr;gsize size{};auto stream=endpoint.open(77,uri::encode(f.packet->token),&size,&error);
        if(!stream){require(error && error->code==G_IO_ERROR_PERMISSION_DENIED,"Only actual authority refusal is modeled");g_clear_error(&error);return false;}
        std::array<uint8_t,9> bytes{};require(size==16 && g_input_stream_read(stream,bytes.data(),bytes.size(),nullptr,&error)==9 && !error && bytes[8]==id,"Actual distinct immutable imported pixels");
        require(g_input_stream_close(stream,nullptr,&error) && !error,"Probe actual GIO closure");g_object_unref(stream);return true;
    };
    auto project=[&](uint64_t id) {
        const bool readable=probe(id);auto& f=frames.at(id);
        return endpoint.native([&](auto& b) {
            bool charged=false,cleanup=false,terminal=false;unsigned records=0;
            for(const auto& row:b.inspect())if(row.entry==id){require(row.job==f.job,"Original exact imported model job retained");charged=row.bytes>0;cleanup=row.cleanup;terminal=row.terminal;++records;if(row.packet)require(f.packet && row.packet->token==f.packet->token && row.packet->expires==500,"Original exact native token and expiry retained");}
            const unsigned nativeSlots=f.ownership?unsigned(!f.ownership->exportReleased())+unsigned(!f.ownership->producerRetired()):0;
            Wire w;return w.integer("nativeSlots",nativeSlots).boolean("charged",charged).boolean("mapped",f.mapping && !f.mapping->png().empty()).boolean("held",f.held)
                .boolean("cleanup",cleanup).boolean("terminal",terminal).integer("records",records).boolean("readable",readable).finish();
        });
    };
    std::string event;
    while(std::getline(std::cin,event)) {
        if(event=="Init"){}
        else {
            const uint64_t id=event.back()=='2'?2:1;auto& f=frames.at(id);
            if(event.starts_with("Capture")) {
                const auto& first=frames.at(1);
                if(id==1 || first.ownership->producerRetired()) {
                    require(!f.capture,"One actual imported model capture");
                    endpoint.nativeDemand([&](auto& q){require(q.observe({id,1,f.source.scope,{1},4096,true}).accepted,"Original model native demand");auto attempt=q.start(id,200);require(attempt.job.has_value(),"Separately issued original model job");f.job=*attempt.job;});
                    f.capture=ClientCapture{f.job.binding,f.job.context,10*id,100,200,320,240,16,4096,0};f.header=header(*f.capture);
                    const std::array<uint8_t,16> bytes{137,80,78,71,13,10,26,10,static_cast<uint8_t>(id),2,3,4,5,6,7,8};
                    auto mapping=std::make_unique<fd::Mapped>(fd::seal(bytes),f.header,4096,fd::SourcePlane::ClientMain);f.mapping=mapping.get();std::unique_ptr<const Buffer> payload=std::move(mapping);
                    endpoint.native([&](auto& b){require(b.allocate(id,f.job,payload,500).receipts.size()==1 && !payload,"Actual model mapping and FD adopted");f.packet=*b.producerComplete(id,f.job).receipts.at(0).packet;});
                    f.ownership.emplace(*f.capture,f.header);f.source.scope.now=102;
                }
            }else if(event.starts_with("Transfer") || event=="Pending1" || event=="Fail1" || event=="Unknown1") {
                require(f.ownership.has_value(),"Actual imported native obligation");
                bool rejected=false;
                try {f.ownership->settle([&](const ClientCapture& capture,uint64_t transfer){require(capture.request==f.capture->request && transfer==f.header[fd::Transfer],"Exact original release callback");return event!="Fail1";},
                    [&]{return event=="Pending1"?ClientRetirement::PendingLock:event=="Unknown1"?static_cast<ClientRetirement>(2):ClientRetirement::Retired;});}
                catch(const std::exception&){rejected=true;}
                require(rejected==(event=="Unknown1"),"Only unknown retirement is rejected");
            }else if(event.starts_with("Hold")) {
                require(!f.held && f.packet,"Exact one held original stream");GError* error=nullptr;gsize size{};f.held=endpoint.open(77,uri::encode(f.packet->token),&size,&error);require(f.held && !error && size==16,"Actual owned imported held reader");
            }else if(event.starts_with("Close")) {
                require(f.held,"Actual held reader to close");GError* error=nullptr;require(g_input_stream_close(f.held,nullptr,&error) && !error,"Actual held reader drained");g_object_unref(f.held);f.held=nullptr;
            }else if(event.starts_with("Release")) {
                endpoint.native([&](auto& b){b.release(id,f.job.binding,f.job,f.packet->token);});
            }else if(event.starts_with("Drain")) {
                endpoint.native([&](auto& b){
                    if(f.ownership->producerRetired() && b.consumerComplete(id,f.job)) {
                        require(f.mapping && f.mapping->close(),"Actual local mmap/FD closure before terminal proof");
                        require(b.destroy(id,f.job).status==Result::Status::Complete,"Physical local imported terminal proof");f.mapping=nullptr;
                    }
                });
            }else if(event.starts_with("Ack")) {
                uint64_t sequence=endpoint.native([&](auto& b){for(const auto& row:b.inspect())if(row.entry==id && row.terminal)return row.proofs.back().sequence.value;return uint64_t{0};});
                require(sequence,"Actual retained final receipt");Wire ack;require(delivery.acknowledge(77,"family:"+std::to_string(f.job.context.incarnation.value),ack.text("kind","acknowledge").begin("job").job(f.job).end().counter("sequence",sequence).finish()),"Actual exact final original ACK");
            }else if(event=="Stop1") {f.source.scope.sourceLive=false;f.source.scope.context.scene.value++;}
            else if(event=="Lock1")f.source.scope.locked=true;
            else if(event=="Expire1")f.source.scope.now=500;
            else if(event=="Foreign1")f.source.scope.binding.frontend.value++;
            else require(false,"Explicit selected imported model event");
            if((event=="Lock1" || event=="Expire1") && f.held) {
                GError* error=nullptr;uint8_t byte{};require(g_input_stream_read(f.held,&byte,1,nullptr,&error)==-1 && error && error->code==G_IO_ERROR_PERMISSION_DENIED,"Actual held native guard refuses before cached policy updates");g_clear_error(&error);
            }
        }
        std::cout<<"{\"first\":"<<project(1)<<",\"second\":"<<project(2)<<"}\n";
    }
    require(!frames.at(1).held && !frames.at(2).held && endpoint.readers()==0 && endpoint.native([](auto& b){return b.recordCount()==0 && b.charge()==0;}),"Selected imported traces finish actual storage, readers and receipts");
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

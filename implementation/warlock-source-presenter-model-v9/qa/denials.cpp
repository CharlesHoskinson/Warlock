#include "client_producer.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    uint64_t charge()const noexcept override{return 4096;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
int main(int argc,char** argv){try {
    require(argc==2,"Concrete native fixture argument");std::ifstream input(argv[1]);std::string text((std::istreambuf_iterator<char>(input)),{});Json fixture(text);
    auto source=Json::child(fixture.object(),"clientScope"),raw=Json::child(source,"scope");
    SourceObservation observed{{decodeBinding(Json::child(raw,"binding")),decodeContext(Json::child(raw,"context")),{decimal(Json::text(raw,"clock"))},decimal(Json::text(raw,"now")),Json::boolean(raw,"present"),Json::boolean(raw,"sourceLive"),Json::boolean(raw,"locked"),Json::boolean(raw,"gpuReady")},decimal(Json::text(raw,"observation")),decimal(Json::text(source,"maximumTransferBytes")),decimal(Json::text(source,"requestId")),SourceObservation::Kind::UnqualifiedClientMain,false};
    auto receipts=json_object_get_array_member(fixture.object(),"terminalReceipts");auto proof=json_node_get_object(json_array_get_element(receipts,0));auto frame=Json::child(Json::child(Json::child(proof,"event"),"event"),"frame");
    const auto job=decodeJob(Json::child(frame,"job"));const auto expires=decimal(Json::text(frame,"expires"));
    uri::Endpoint endpoint({1,4,1,observed.maximumTransferBytes},1,1,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{observed.scope.clock,observed.scope.now};});
    endpoint.native([&](auto& b){require(b.enroll(1,observed.scope,observed.maximumTransferBytes),"Concrete native scope enrolled");});
    require(endpoint.registerView(77,job.binding,{1}),"Concrete URI view enrolled");ReceiptDelivery delivery(endpoint,job.binding,77);
    bool open=true,pending=false;std::optional<Packet> packet;std::string event;
    while(std::getline(std::cin,event)) {
        std::vector<std::string> wires;
        if(event=="Init"){}
        else if(event=="Seed")wires.push_back(clientSeed(observed,1,1));
        else if(event=="Request") {
            endpoint.native([&](auto& b){if(b.recordCount()==0)require(b.acquire(1,job.binding,job).status==Result::Status::Admitted,"Exact original reservation");});
            Wire w;w.text("kind","event").text("identity","family:"+std::to_string(job.context.incarnation.value)).begin("event").text("kind","request").begin("trigger").begin("binding").binding(job.binding).end().begin("context").context(job.context).end().counter("origin",job.origin.value).counter("clock",job.clock.value).counter("deadline",job.deadline).end().end();wires.push_back(w.finish());
        } else if(event=="Capture") {
            auto offered=endpoint.native([&](auto& b){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();return b.allocate(1,job,payload,expires);});
            require(offered.receipts.size()==1 && offered.receipts.front().packet.has_value(),"Actual concrete Offer");wires.push_back(frameEvent("offer",*offered.receipts.front().packet));
            auto ready=endpoint.native([&](auto& b){return b.producerComplete(1,job);});packet=ready.receipts.at(0).packet;wires.push_back(frameEvent("fence",*packet));
        } else if(event=="Close")open=false;
        else if(event=="Drain") {
            pending=false;
            require(packet.has_value(),"Concrete owned packet");endpoint.native([&](auto& b){b.release(1,job.binding,job,packet->token);require(b.consumerComplete(1,job),"Concrete physical consumer drain");require(b.destroy(1,job).status==Result::Status::Complete,"Concrete physical destruction");});
            wires=delivery.pending(77);require(wires.size()==1,"Exact retained terminal proof");
        } else if(event=="Ack") {
            auto sequence=endpoint.native([](auto& b){return b.inspect().at(0).proofs.back().sequence.value;});Wire w;const auto ack=w.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",sequence).finish();
            require(delivery.acknowledge(77,"family:"+std::to_string(job.context.incarnation.value),ack),"Actual exact terminal acknowledgment");
        } else if(event=="DenyLocked" || event=="DenyGone" || event=="DenyOutput" || event=="DenyLayout" || event=="RepeatDenied") {
            const auto reason=(event=="DenyGone")?SourceDenial::SourceUnavailable:(event=="DenyOutput")?SourceDenial::OutputUnavailable:(event=="DenyLayout")?SourceDenial::LayoutUnsupported:SourceDenial::Locked;
            require(packet.has_value(),"Original owned denial packet");
            wires.push_back(endpoint.native([&](auto& b){return clientDenied(b,job,*packet,ScopeDenied(job.binding,job.context.incarnation,observed.request,reason));}));
        } else if(event=="ForeignDenied" || event=="StaleDenied") {
            auto foreign=job;auto denied=ScopeDenied(job.binding,job.context.incarnation,observed.request,SourceDenial::Locked);
            if(event=="ForeignDenied"){foreign.binding.session.value++;denied.binding=foreign.binding;}else{foreign.request.value++;denied.subject.value++;}
            bool rejected=false;try{endpoint.native([&](auto& b){clientDenied(b,job,*packet,denied);});}catch(const std::exception&){rejected=true;}require(rejected,"Actual foreign source denial rejected");
            Wire w;w.text("kind","event").text("identity","family:"+std::to_string(job.context.incarnation.value)).begin("event").text("kind","source-denied").begin("job").job(foreign).end().text("reason","locked").end();wires.push_back(w.finish());
        } else if(event=="UnknownDenial") {
            Json reply("{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"transport-error\"}");require(!decodeSourceDenial(reply),"Unknown reply is not typed source denial");
        } else if(event=="PendingRetire") {
            endpoint.native([&](auto& b){require(b.consumerComplete(1,job),"Actual synthetic consumer drain");});
            Json reply("{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-client-locked\"}");require(decodeClientRetirement(reply,job.binding,observed.request)==ClientRetirement::PendingLock,"Actual known pending decoder");pending=true;
        } else if(event=="Resume") {
            auto current=observed;current.scope.now++;current.observation++;current.request++;
            endpoint.native([&](auto& b){require(admitClientObservation(b,job,current),"Actual fresh admitted resume scope");});observed=current;wires.push_back(clientObservation(observed));
        } else if(event=="StaleScope") {
            auto stale=observed;stale.observation--;wires.push_back(clientObservation(stale));
        } else if(event=="Unknown") {
            endpoint.native([&](auto& b){b.release(1,job.binding,job,packet->token);});
            Wire w;w.text("kind","event").text("identity","family:"+std::to_string(job.context.incarnation.value)).begin("event").text("kind","exhausted").begin("binding").binding(job.binding).end().end();wires.push_back(w.finish());
        } else {
            auto current=observed;current.scope.now++;current.observation++;current.request++;
            if(event=="Content")current.scope.context.content.value++;
            else if(event=="Scene")current.scope.context.scene.value++;
            else if(event=="Stopped"){current.scope.sourceLive=false;current.scope.context.scene.value++;}
            else if(event=="Output")current.scope.context.output.value++;
            else if(event=="Privacy")current.scope.context.privacy.value++;
            else if(event=="Rendering")current.scope.context.rendering.value++;
            else if(event=="Locked")current.scope.locked=true;
            else if(event=="Absent")current.scope.present=false;
            else if(event=="Gpu")current.scope.gpuReady=false;
            else if(event=="Expire")current.scope.now=expires;
            else require(event=="ClockOnly","Selected observation event");
            endpoint.native([&](auto& b){require(admitClientObservation(b,job,current),"Actual changed provider observation admission");});
            if(clientFactsChanged(observed,current))wires.push_back(open?clientSeed(current,1,1):clientObservation(current));
            if(event=="Expire") {wires.push_back(frameEvent("expired",*packet));}
            observed=current;
        }
        auto projection=endpoint.native([&](auto& b){Wire w;const auto rows=b.inspect();return w.boolean("readable",packet && static_cast<bool>(b.fetch(1,job.binding,packet->token))).boolean("charged",b.charge()!=0).integer("records",b.recordCount()).boolean("cleanup",!rows.empty() && rows.front().cleanup).boolean("pending",pending).finish();});
        std::cout<<"{\"broker\":"<<projection<<",\"wire\":[";for(size_t i=0;i<wires.size();++i){if(i)std::cout<<',';std::cout<<wires[i];}std::cout<<"]}\n";
    }
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

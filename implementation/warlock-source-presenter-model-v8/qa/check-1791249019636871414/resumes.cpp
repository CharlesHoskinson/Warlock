#include "client_producer.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    uint64_t charge()const noexcept override{return 4096;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
int main(int argc,char** argv){try {
    require(argc==2,"Concrete retained fixture argument");std::ifstream input(argv[1]);std::string text((std::istreambuf_iterator<char>(input)),{});Json fixture(text);
    auto source=Json::child(fixture.object(),"clientScope"),raw=Json::child(source,"scope");
    SourceObservation observed{{decodeBinding(Json::child(raw,"binding")),decodeContext(Json::child(raw,"context")),{decimal(Json::text(raw,"clock"))},decimal(Json::text(raw,"now")),Json::boolean(raw,"present"),Json::boolean(raw,"sourceLive"),Json::boolean(raw,"locked"),Json::boolean(raw,"gpuReady")},decimal(Json::text(raw,"observation")),decimal(Json::text(source,"maximumTransferBytes")),decimal(Json::text(source,"requestId")),SourceObservation::Kind::UnqualifiedClientMain,false};
    auto receipts=json_object_get_array_member(fixture.object(),"terminalReceipts");auto proof=json_node_get_object(json_array_get_element(receipts,0));auto frame=Json::child(Json::child(Json::child(proof,"event"),"event"),"frame");
    const auto original=decodeJob(Json::child(frame,"job"));const auto originalExpires=decimal(Json::text(frame,"expires"));
    const Limits limits{1,4,1,observed.maximumTransferBytes};
    uri::Endpoint endpoint(limits,1,1,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{observed.scope.clock,observed.scope.now};});
    require(endpoint.enableDemand({limits,original.binding.lifetime,original.clock,1}),"One retained native demand authority");
    endpoint.nativeDemand([&](auto& q){require(q.observe({1,1,observed.scope,{1},observed.maximumTransferBytes,true}).accepted,"Original native scope admitted");});
    require(endpoint.registerView(77,original.binding,{1}),"Exact retained URI view");ReceiptDelivery delivery(endpoint,original.binding,77);
    Job current=original;uint64_t lease=1;std::optional<Packet> packet,oldPacket;std::string oldTerminal,event;
    auto acknowledge=[&](const Job& job,uint64_t sequence){Wire w;return delivery.acknowledge(77,"family:"+std::to_string(job.context.incarnation.value),w.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",sequence).finish());};
    while(std::getline(std::cin,event)) {
        std::vector<std::string> wires;
        if(event=="Init" || event=="Reopen"){}
        else if(event=="Seed")wires.push_back(clientSeed(observed,1,1));
        else if(event=="Request") {
            endpoint.nativeDemand([&](auto& q){const auto start=q.start(1,original.deadline);require(start.job && *start.job==original,"Actual native original reservation preserves fixture job/deadline");});wires.push_back(clientRequest(original));
        } else if(event=="Capture" || event=="Recapture") {
            const auto expires=current.request.value==1?originalExpires:current.deadline+3000000000ULL;
            auto offered=endpoint.native([&](auto& b){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();return b.allocate(1,current,payload,expires);});
            require(offered.receipts.size()==1 && offered.receipts.front().packet,"Actual owned synthetic storage Offer");wires.push_back(frameEvent("offer",*offered.receipts.front().packet));
            packet=endpoint.native([&](auto& b){return *b.producerComplete(1,current).receipts.at(0).packet;});wires.push_back(frameEvent("fence",*packet));
            if(current.request.value==1)oldPacket=packet;
        } else if(event=="DenyLocked") {
            require(packet.has_value(),"Exact old owned denial packet");wires.push_back(endpoint.native([&](auto& b){return clientDenied(b,current,*packet,ScopeDenied(current.binding,current.context.incarnation,observed.request,SourceDenial::Locked));}));
        } else if(event=="Drain") {
            require(packet.has_value(),"Owned packet required for drain");endpoint.native([&](auto& b){b.release(1,current.binding,current,packet->token);require(b.consumerComplete(1,current),"Actual synthetic physical consumer drain");require(b.destroy(1,current).status==Result::Status::Complete,"Actual synthetic storage destruction");});
            wires=delivery.pending(77);require(wires.size()==1,"One retained exact terminal proof");if(current.request.value==1)oldTerminal=wires.front();
        } else if(event=="Ack") {
            const auto sequence=endpoint.native([](auto& b){return b.inspect().at(0).proofs.back().sequence.value;});require(sequence==(current.request.value==1?3:6),"Same Broker receipt sequence continuous across both jobs");require(acknowledge(current,sequence),"Actual exact terminal ACK");
        } else if(event=="Reserve" || event=="OldLease" || event=="StaleScope" || event=="ForeignScope" || event=="TooCostly") {
            auto fresh=observed;fresh.observation++;fresh.request++;fresh.scope.now=original.deadline+1;fresh.scope.context.privacy.value++;fresh.scope.context.content.value++;
            if(event=="StaleScope")fresh.observation=observed.observation;
            if(event=="ForeignScope")fresh.scope.binding.session.value++;
            if(event=="TooCostly")fresh.maximumTransferBytes=limits.bytes+1;
            std::optional<Job> next;bool rejected=false;
            try{next=endpoint.nativeDemand([&](auto& q){return reserveClientResume(q,current,observed,lease,fresh,2,event=="OldLease"?1:2);});}catch(const std::exception&){rejected=true;}
            require(rejected==(event=="StaleScope" || event=="ForeignScope"),"Only actual stale/foreign authority rejection is caught");
            if(next){require(event=="Reserve" && next->request.value==2 && next->origin.value==2 && next->deadline==fresh.scope.now+2000000000ULL,"Actual new native job/counter/origin/issued deadline");current=*next;observed=fresh;lease=2;packet.reset();wires={clientSeed(observed,2,2),clientRequest(current)};}
            else require(event!="Reserve" || endpoint.native([](auto& b){return b.recordCount()!=0;}),"Valid reserve only waits for original ownership/journal");
        } else if(event=="Expire") {
            require(packet && current.request.value==2,"Only new frame expiry");auto fresh=observed;fresh.scope.now=packet->expires;fresh.observation++;fresh.request++;
            endpoint.native([&](auto& b){require(admitClientObservation(b,current,fresh),"Actual native clock observation");});observed=fresh;
            wires={clientObservation(observed),frameEvent("expired",*packet)};
        } else if(event=="LateDenied") {
            require(oldPacket && current.request.value==2,"Old exact denied job preserved");bool rejected=false;try{endpoint.native([&](auto& b){clientDenied(b,original,*oldPacket,ScopeDenied(original.binding,original.context.incarnation,1,SourceDenial::Locked));});}catch(const std::exception&){rejected=true;}require(rejected,"Old native denied owner no longer registered");
            Wire w;wires.push_back(w.text("kind","event").text("identity","family:"+std::to_string(original.context.incarnation.value)).begin("event").text("kind","source-denied").begin("job").job(original).end().text("reason","locked").end().finish());
        } else if(event=="LateAck") {
            require(current.request.value==2 && !oldTerminal.empty(),"Retained old proof negative stimulus");require(!acknowledge(original,3),"Actual old ACK cannot erase new owner");wires.push_back(oldTerminal);
        } else require(false,"Explicit selected resumption event");
        auto projection=endpoint.native([&](auto& b){const auto rows=b.inspect();Wire w;return w.boolean("readable",packet && static_cast<bool>(b.fetch(1,current.binding,packet->token))).boolean("charged",b.charge()!=0).integer("records",b.recordCount()).boolean("cleanup",!rows.empty() && rows.front().cleanup).integer("floor",b.requestFloor(1)).finish();});
        std::cout<<"{\"broker\":"<<projection<<",\"wire\":[";for(size_t i=0;i<wires.size();++i){if(i)std::cout<<',';std::cout<<wires[i];}std::cout<<"]}\n";
    }
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

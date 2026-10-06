#include "client_producer.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    uint64_t charge()const noexcept override{return 4096;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
int main(int argc,char** argv){try {
    require(argc==2,"Concrete original native fixture argument");std::ifstream input(argv[1]);std::string text((std::istreambuf_iterator<char>(input)),{});Json fixture(text);
    auto source=Json::child(fixture.object(),"clientScope"),raw=Json::child(source,"scope");
    SourceObservation observed{{decodeBinding(Json::child(raw,"binding")),decodeContext(Json::child(raw,"context")),{decimal(Json::text(raw,"clock"))},decimal(Json::text(raw,"now")),Json::boolean(raw,"present"),Json::boolean(raw,"sourceLive"),Json::boolean(raw,"locked"),Json::boolean(raw,"gpuReady")},decimal(Json::text(raw,"observation")),decimal(Json::text(source,"maximumTransferBytes")),decimal(Json::text(source,"requestId")),SourceObservation::Kind::UnqualifiedClientMain,false};
    auto receipts=json_object_get_array_member(fixture.object(),"terminalReceipts");auto proof=json_node_get_object(json_array_get_element(receipts,0));auto frame=Json::child(Json::child(Json::child(proof,"event"),"event"),"frame");
    const auto original=decodeJob(Json::child(frame,"job"));const auto expires=decimal(Json::text(frame,"expires"));const Limits limits{1,4,1,observed.maximumTransferBytes};
    uri::Endpoint endpoint(limits,1,1,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{observed.scope.clock,observed.scope.now};});
    require(endpoint.enableDemand({limits,original.binding.lifetime,original.clock,1}),"Same native demand authority");endpoint.nativeDemand([&](auto& q){require(q.observe({1,1,observed.scope,{1},observed.maximumTransferBytes,true}).accepted,"Original native demand admission");});
    require(endpoint.registerView(77,original.binding,{1}),"Same URI receiver");ReceiptDelivery delivery(endpoint,original.binding,77);
    uint64_t lease=1;std::optional<Packet> packet;GInputStream* held=nullptr;std::string event;
    while(std::getline(std::cin,event)) {
        std::vector<std::string> wires;
        if(event=="Init" || event=="Close" || event=="Reopen"){}
        else if(event=="Seed")wires.push_back(clientSeed(observed,1,1));
        else if(event=="Request") {
            endpoint.nativeDemand([&](auto& q){auto started=q.start(1,original.deadline);require(started.job && *started.job==original,"Original exact native reservation and issued deadline");});wires.push_back(clientRequest(original));
        } else if(event=="Capture") {
            auto offered=endpoint.native([&](auto& b){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();return b.allocate(1,original,payload,expires);});require(offered.receipts.size()==1 && offered.receipts.front().packet,"Actual original owned storage Offer");wires.push_back(frameEvent("offer",*offered.receipts.front().packet));
            packet=endpoint.native([&](auto& b){return *b.producerComplete(1,original).receipts.at(0).packet;});wires.push_back(frameEvent("fence",*packet));
        } else if(event=="Stop" || event=="Expire") {
            auto fresh=observed;fresh.scope.now++;fresh.observation++;fresh.request++;
            if(event=="Stop"){fresh.scope.sourceLive=false;fresh.scope.context.scene.value++;fresh.scope.context.content.value++;}else fresh.scope.now=expires;
            endpoint.native([&](auto& b){require(admitClientObservation(b,original,fresh),"Actual coherent stopped/expiry native observation admission");});observed=fresh;wires.push_back(clientObservation(observed));if(event=="Expire")wires.push_back(frameEvent("expired",*packet));
        } else if(event=="Retain" || event=="OldLease" || event=="MissingPublication" || event=="ForeignScope" || event=="ChangedExpiry") {
            auto candidate=observed;auto owned=*packet;if(event=="ForeignScope")candidate.scope.binding.session.value++;if(event=="ChangedExpiry")owned.expires++;
            bool accepted=false,rejected=false;try{accepted=endpoint.native([&](auto& b){return admitRetainedClientPresentation(b,original,candidate,owned,lease,event=="MissingPublication"?0:3,event=="OldLease"?1:2);});}catch(const std::exception&){rejected=true;}
            require(rejected==(event=="ForeignScope"),"Only selected foreign authority rejection is caught");
            if(accepted){require(event=="Retain","Only unchanged own packet under new admitted lease may present");lease=2;wires.push_back(clientSeed(observed,3,2));}
            endpoint.native([&](auto& b){require(b.requestFloor(1)==1,"Retained presentation does not reserve another native job");const auto rows=b.inspect();for(const auto& row:rows)require(row.job==original && row.packet && row.packet->token==packet->token && row.packet->expires==expires,"Immutable original job/token/expiry retained");});
        } else if(event=="Unknown") {
            endpoint.native([&](auto& b){b.release(1,original.binding,original,packet->token);});Wire w;wires.push_back(w.text("kind","event").text("identity","family:"+std::to_string(original.context.incarnation.value)).begin("event").text("kind","exhausted").begin("binding").binding(original.binding).end().end().finish());
        } else if(event=="Hold") {
            require(!held,"One actual held GIO reader");GError* error=nullptr;gsize length{};held=endpoint.open(77,uri::encode(packet->token),&length,&error);require(held && !error,"Actual same Historical URI readable");std::array<uint8_t,4> bytes{};require(g_input_stream_read(held,bytes.data(),bytes.size(),nullptr,&error)==4 && !error,"Actual immutable Historical storage readable");
        } else if(event=="CloseReader") {
            require(held,"Actual reader to close");GError* error=nullptr;require(g_input_stream_close(held,nullptr,&error) && !error,"Actual reader closure");g_object_unref(held);held=nullptr;
        } else if(event=="Drain") {
            endpoint.native([&](auto& b){b.release(1,original.binding,original,packet->token);const auto drained=b.consumerComplete(1,original);require(drained==!static_cast<bool>(held),"Held reader physically blocks retirement");if(drained)require(b.destroy(1,original).status==Result::Status::Complete,"Actual synthetic physical storage destruction");});
            if(!held){wires=delivery.pending(77);require(wires.size()==1,"Exact retained terminal proof");}
        } else if(event=="Ack") {
            Wire w;require(delivery.acknowledge(77,"family:"+std::to_string(original.context.incarnation.value),w.text("kind","acknowledge").begin("job").job(original).end().counter("sequence",3).finish()),"Exact unrenewed original terminal ACK3");
        } else require(false,"Explicit selected Historical event");
        auto projection=endpoint.native([&](auto& b){const auto rows=b.inspect();Wire w;return w.boolean("readable",packet && static_cast<bool>(b.fetch(1,original.binding,packet->token))).boolean("charged",b.charge()!=0).integer("records",b.recordCount()).boolean("cleanup",!rows.empty() && rows.front().cleanup).integer("floor",b.requestFloor(1)).boolean("held",held!=nullptr).finish();});
        std::cout<<"{\"broker\":"<<projection<<",\"wire\":[";for(size_t i=0;i<wires.size();++i){if(i)std::cout<<',';std::cout<<wires[i];}std::cout<<"]}\n";
    }
    require(!held,"Selected traces finish actual held readers");return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

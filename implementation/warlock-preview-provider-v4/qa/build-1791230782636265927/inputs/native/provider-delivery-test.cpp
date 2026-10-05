#include "preview_delivery.hpp"
#include <iostream>
using namespace preview;
using namespace preview::bridge;
static unsigned checks=0,frees=0;
static void check(bool value,const char* name){require(value,name);++checks;}
template<class F> static bool denied(F f){try{f();return false;}catch(const std::exception&){return true;}}
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    ~PNG(){++frees;}
    uint64_t charge()const noexcept override{return 32;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
static Scope source(){return {{{UINT64_MAX},{9007199254740993ULL},{9007199254740994ULL}},{{UINT64_MAX},{UINT64_MAX},{3},{4},{5},{6},{7}},{UINT64_MAX},9007199254740993ULL,true,true,false,true};}
static Job job(const Scope& s,uint64_t request=1){return {s.binding,s.context,{request},{9007199254740995ULL},s.clock,9007199254741093ULL};}
static std::string ack(const Job& j,uint64_t sequence){Wire w;return w.text("kind","acknowledge").begin("job").job(j).end().counter("sequence",sequence).finish();}
static std::string packet(const Packet& p){Wire w;w.begin("job").job(p.job).end().text("handle",uri::encode(p.token).substr(20)).boolean("owned",true).boolean("signaled",p.signaled).text("fidelity",p.fidelity==Packet::Fidelity::Family?"family":"client").array("coverage");for(auto name:{"client","decoration","modal","popup"})w.element(name);return w.endArray().counter("expires",p.expires).finish();}
static std::string scopeWire(const Scope& s){Wire w;return w.begin("binding").binding(s.binding).end().begin("context").context(s.context).end().counter("observation",1).counter("clock",s.clock.value).counter("now",s.now).boolean("present",true).boolean("sourceLive",true).boolean("locked",false).boolean("gpuReady",true).finish();}
static int bridge(bool released){
    // Live native CPU fixture; it claims no compositor capture eligibility.
    auto s=source();auto j=job(s);uri::Endpoint endpoint({2,8,2,64},2,2,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{s.clock,s.now};});
    endpoint.native([&](auto& b){require(b.enroll(1,s,32),"Fixture enrollment");require(b.acquire(1,s.binding,j).status==Result::Status::Admitted,"Fixture acquire");});
    require(endpoint.registerView(77,s.binding,{1}),"Fixture view");ReceiptDelivery delivery(endpoint,s.binding,77);
    std::optional<Packet> offered,fenced;
    endpoint.native([&](auto& b){
        if(released){std::unique_ptr<const Buffer> bytes=std::make_unique<const PNG>();auto r=b.allocate(1,j,bytes,UINT64_MAX,Packet::Fidelity::Family,15);offered=r.receipts.at(0).packet;fenced=b.producerComplete(1,j).receipts.at(0).packet;b.release(1,s.binding,j,fenced->token);require(b.consumerComplete(1,j),"Fixture native consumer complete");b.destroy(1,j);}
        else {b.cancel(1,s.binding,j);b.producerRefused(1,j);}
    });
    auto wires=delivery.pending(77);Wire initial;initial.text("kind",released?"released":"refused").text("identity","family:"+std::to_string(s.context.incarnation.value)).text("scopeJSON",scopeWire(s));
    if(offered)initial.text("offerJSON",packet(*offered)).text("fenceJSON",packet(*fenced));
    auto header=initial.finish();header.pop_back();header+=",\"receipts\":[";for(const auto& wire:wires){if(header.back()!= '[')header+=",";header+=wire;}header+="]}";std::cout<<header<<std::endl;
    std::string line;while(std::getline(std::cin,line)){
        bool accepted=false;try{accepted=delivery.acknowledge(77,"family:"+std::to_string(s.context.incarnation.value),line);}catch(const std::exception&){}
        std::cout<<"{\"accepted\":"<<(accepted?"true":"false")<<",\"records\":"<<endpoint.native([](auto& b){return b.recordCount();})<<",\"pending\":"<<delivery.pending(77).size()<<",\"frees\":"<<frees<<"}"<<std::endl;
    }
    require(endpoint.native([](auto& b){return b.recordCount();})==0,"Actual Elm final ACK retired journal");return 0;
}
int main(int argc,char** argv){try{
    if(argc==2)return bridge(std::string_view(argv[1])=="--bridge-released");
    auto s=source();auto j=job(s);uri::Endpoint endpoint({3,8,3,96},3,3,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{s.clock,s.now};});
    endpoint.native([&](auto& b){check(b.enroll(1,s,32),"Own subject enrolled");auto other=s;other.context.incarnation={2};check(b.enroll(2,other,32),"Independent subject enrolled");check(b.acquire(1,s.binding,j).status==Result::Status::Admitted,"Actual broker admits job");});
    check(endpoint.registerView(77,s.binding,{1}),"Native receiver registered");check(endpoint.registerView(88,s.binding,{2}),"Foreign popup registered");
    ReceiptDelivery delivery(endpoint,s.binding,77);
    check(denied([&]{ReceiptDelivery invalid(endpoint,s.binding,99);}),"Missing native view refused");auto foreign=s.binding;foreign.frontend={1};check(denied([&]{ReceiptDelivery invalid(endpoint,foreign,77);}),"Foreign provider binding refused");
    check(delivery.pending(77).empty(),"Reserved operation has no fabricated terminal receipt");check(denied([&]{delivery.pending(88);}),"Foreign popup delivery denied");
    auto offered=endpoint.native([&](auto& b){std::unique_ptr<const Buffer> bytes=std::make_unique<const PNG>();return b.allocate(1,j,bytes,UINT64_MAX,Packet::Fidelity::Family,15);});auto token=offered.receipts.at(0).packet->token;
    check(delivery.pending(77).empty(),"Offer is not a cleanup proof");endpoint.native([&](auto& b){b.producerComplete(1,j);});GError* error=nullptr;gsize length=0;auto stream=endpoint.open(77,uri::encode(token),&length,&error);check(stream && !error && length==12,"Actual URI stream holds physical bytes");
    endpoint.native([&](auto& b){b.cancel(1,s.binding,j);});
    check(!endpoint.native([&](auto& b){return b.consumerComplete(1,j);}),"Reader prevents native consumer completion");check(endpoint.native([&](auto& b){return b.destroy(1,j).receipts.empty();}) && frees==0,"Retained stream prevents physical release");check(delivery.pending(77).empty(),"UI cancellation does not invent terminal proof");
    check(g_input_stream_close(stream,nullptr,&error) && !error,"Actual stream closes");g_object_unref(stream);
    check(delivery.pending(77).empty() && frees==0 && endpoint.native([](auto& b){return b.charge();})==32,"Stream close neither frees broker charge nor creates receipt");
    check(endpoint.native([&](auto& b){return b.destroy(1,j).receipts.empty();}),"Consumer fence still required after stream close");
    check(endpoint.native([&](auto& b){return b.consumerComplete(1,j);}),"Actual consumer completion after reader drain");auto retired=endpoint.native([&](auto& b){return b.destroy(1,j);});
    check(frees==1 && endpoint.native([](auto& b){return b.charge();})==0 && retired.receipts.size()==2,"Physical buffer destroyed before released and cancelled receipts");
    auto pending=delivery.pending(77);check(pending.size()==2 && delivery.pending(77)==pending && endpoint.native([](auto& b){return b.recordCount();})==1,"Repeated delivery retains exact native journal");
    {Json json(pending.front());auto envelope=json.object();auto receipt=Json::child(envelope,"event");auto frame=Json::child(Json::child(receipt,"event"),"frame");check(std::string_view(Json::text(envelope,"identity"))=="family:18446744073709551615" && decodeJob(Json::child(frame,"job"))==j && decimal(Json::text(frame,"expires"))==UINT64_MAX && Json::boolean(frame,"signaled") && std::string_view(Json::text(frame,"fidelity"))=="family" && json_array_get_length(json_node_get_array(json_object_get_member(frame,"coverage")))==4,"Terminal wire preserves job, uint64, native signal, fidelity and coverage");check(std::string_view(Json::text(frame,"handle"))==uri::encode(token).substr(20),"Terminal handle is the original opaque broker token");}
    const auto final=retired.receipts.back().sequence.value;const auto identity="family:"+std::to_string(j.context.incarnation.value);
    check(!delivery.acknowledge(77,identity,ack(j,retired.receipts.front().sequence.value)),"Earlier receipt cannot reclaim journal");check(denied([&]{delivery.acknowledge(88,identity,ack(j,final));}),"Foreign native view cannot acknowledge");check(denied([&]{delivery.acknowledge(77,"family:2",ack(j,final));}),"Foreign family identity cannot acknowledge");auto wrong=j;wrong.binding.frontend={1};check(denied([&]{delivery.acknowledge(77,identity,ack(wrong,final));}),"Foreign binding cannot acknowledge");wrong=j;wrong.request={2};check(!delivery.acknowledge(77,identity,ack(wrong,final)),"Wrong job cannot acknowledge");check(!delivery.acknowledge(77,identity,ack(j,final+1)),"Wrong final sequence cannot acknowledge");
    auto malformed=ack(j,final);malformed.insert(1,"\"kind\":\"acknowledge\",");check(denied([&]{delivery.acknowledge(77,identity,malformed);}),"Duplicate acknowledgment fields rejected");
    check(delivery.pending(77)==pending,"Rejected acknowledgments preserve cleanup proof");check(delivery.acknowledge(77,identity,ack(j,final)),"Exact final acknowledgment reclaims journal");check(delivery.pending(77).empty() && endpoint.native([](auto& b){return b.recordCount();})==0,"Journal removed only after final ACK");check(!delivery.acknowledge(77,identity,ack(j,final)),"Duplicate final ACK is idempotent rejection");check(endpoint.native([&](auto& b){return b.acquire(1,s.binding,j).status==Result::Status::Ignored;}),"Retired request floor rejects replay");
    j.request={2};endpoint.native([&](auto& b){b.acquire(1,s.binding,j);b.cancel(1,s.binding,j);});check(delivery.pending(77).empty(),"Cancellation awaits actual producer refusal");auto refused=endpoint.native([&](auto& b){return b.producerRefused(1,j);});check(refused.receipts.size()==2 && delivery.pending(77).size()==2,"Actual producer refusal retains raced cancellation proofs");
    endpoint.unregisterView(77);check(denied([&]{delivery.pending(77);}),"Closed popup cannot receive receipts");check(endpoint.registerView(77,s.binding,{1}),"Reused native view identity gets new epoch");check(denied([&]{delivery.acknowledge(77,identity,ack(j,refused.receipts.back().sequence.value));}),"Old enrollment cannot acknowledge reused view identity");check(endpoint.native([](auto& b){return b.recordCount();})==1,"Closed and reused receiver retain native journal");
    ReceiptDelivery fresh(endpoint,s.binding,77);check(fresh.pending(77).size()==2 && fresh.acknowledge(77,identity,ack(j,refused.receipts.back().sequence.value)),"Fresh native enrollment delivers and acknowledges retained proofs");
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}

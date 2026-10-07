#include "preview_delivery.hpp"
#include <iostream>
using namespace preview;
using namespace preview::bridge;
static unsigned checks=0,frees=0;
static void check(bool ok,const char* name){require(ok,name);++checks;}
template<class F>static bool denied(F f){try{f();return false;}catch(const std::exception&){return true;}}
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    ~PNG(){++frees;}
    uint64_t charge()const noexcept override{return 32;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
static Scope scope(uint64_t entry){return {{{1},{2},{3}},{{1},{entry+10},{5},{6},{7},{8},{1}},{10},1,true,true,false,true};}
static Job job(const Scope& s){return {s.binding,s.context,{1},{1},s.clock,100};}
static std::string ack(const Job& j,uint64_t sequence){Wire w;return w.text("kind","acknowledge").begin("job").job(j).end().counter("sequence",sequence).finish();}
static std::string identity(const Job& j){return "family:"+std::to_string(j.context.incarnation.value);}
int main(){try {
    auto first=scope(1),second=scope(2);auto old=job(first),fresh=job(second);
    uri::Endpoint endpoint({4,8,2,64},4,2,[](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{10},1};});
    endpoint.native([&](auto& b){check(b.enroll(1,first,32),"Original own native subject");check(b.acquire(1,first.binding,old).status==Result::Status::Admitted,"Original exact job");});
    check(endpoint.registerView(77,first.binding,{1}),"One original native receiver");const auto epoch=endpoint.registeredView(77)->epoch;
    ReceiptDelivery delivery(endpoint,first.binding,77);
    const auto allocate=[&](uint64_t entry,const Job& j){return endpoint.native([&](auto& b){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();auto r=b.allocate(entry,j,payload,120);b.producerComplete(entry,j);return *r.receipts.at(0).packet;});};
    const auto originalPacket=allocate(1,old);GError* error=nullptr;gsize length=0;
    auto original=endpoint.open(77,uri::encode(originalPacket.token),&length,&error);check(original && !error && length==12,"Original actual GIO stream retained");
    std::array<uint8_t,4> bytes{};check(g_input_stream_read(original,bytes.data(),4,nullptr,&error)==4 && bytes[0]==137,"Original stream begins with actual payload");
    endpoint.native([&](auto& b){check(b.enroll(2,second,32),"New exact own native subject");check(b.acquire(2,second.binding,fresh).status==Result::Status::Admitted,"New job has original independent request");});
    check(endpoint.extendView(77,first.binding,{2}),"Pixel membership extends without journal side effect");const auto newPacket=allocate(2,fresh);
    auto newer=endpoint.open(77,uri::encode(newPacket.token),&length,&error);check(newer && !error && endpoint.readers()==2,"New actual physical reader shares original pool");
    endpoint.native([&](auto& b){b.release(2,fresh.binding,fresh,newPacket.token);b.cancel(2,fresh.binding,fresh);});
    check(delivery.pending(77).empty(),"No terminal receipts before actual physical retirement");
    check(!endpoint.native([&](auto& b){return b.consumerComplete(2,fresh);}) && endpoint.native([](auto& b){return b.charge();})==64,"Held new reader retains both charges");
    check(g_input_stream_close(newer,nullptr,&error) && !error,"New GIO stream closes normally");g_object_unref(newer);
    check(endpoint.native([&](auto& b){return b.destroy(2,fresh).receipts.empty();}),"Stream close cannot manufacture native fence");
    check(endpoint.native([&](auto& b){return b.consumerComplete(2,fresh);}),"Actual new native consumer completion");
    auto terminal=endpoint.native([&](auto& b){return b.destroy(2,fresh);});check(terminal.receipts.size()==2 && frees==1,"Physical destruction precedes released and cancelled proofs");
    check(delivery.pending(77).empty() && !delivery.acknowledge(77,identity(fresh),ack(fresh,terminal.receipts.back().sequence.value)),"View growth alone cannot deliver or acknowledge new subjects");
    check(endpoint.native([](auto& b){return b.recordCount()==2 && b.charge()==32;}),"Unadmitted terminal remains in original broker journal");
    check(delivery.extendSubjects(77),"Explicit own native receipt subject extension");
    auto pending=delivery.pending(77);check(pending.size()==2 && delivery.pending(77)==pending,"New original terminal proofs delivered repeatedly without consumption");
    check(g_input_stream_read(original,bytes.data(),4,nullptr,&error)==4 && !error && bytes==std::array<uint8_t,4>{13,10,26,10},"Held original stream survives both view and journal growth");
    check(endpoint.registeredView(77)->epoch==epoch && endpoint.native([](auto& b){return b.requestFloor(1)==1 && b.requestFloor(2)==1;}),"Growth retains old epoch and per-actor request floors");
    check(!delivery.acknowledge(77,identity(fresh),ack(fresh,terminal.receipts.front().sequence.value)),"Earlier new receipt cannot discharge final proof");
    auto wrong=fresh;wrong.deadline++;check(!delivery.acknowledge(77,identity(fresh),ack(wrong,terminal.receipts.back().sequence.value)),"Changed original deadline cannot acknowledge");
    check(delivery.extendSubjects(77) && delivery.pending(77)==pending,"Duplicate extension keeps original sequence and journal");
    check(delivery.acknowledge(77,identity(fresh),ack(fresh,terminal.receipts.back().sequence.value)),"Exact new final ACK uses retained delivery path");
    check(!delivery.acknowledge(77,identity(fresh),ack(fresh,terminal.receipts.back().sequence.value)) && endpoint.native([](auto& b){return b.recordCount();})==1,"Replayed ACK cannot recreate a cleared record");
    endpoint.native([&](auto& b){b.cancel(1,old.binding,old);});
    check(g_input_stream_read(original,bytes.data(),4,nullptr,&error)==-1 && error,"Journal growth cannot bypass original pixel revocation");g_clear_error(&error);
    check(g_input_stream_close(original,nullptr,&error) && !error,"Original GIO stream closes normally");g_object_unref(original);
    check(endpoint.native([&](auto& b){return b.consumerComplete(1,old);}),"Original native consumer completes after actual drain");
    auto retired=endpoint.native([&](auto& b){return b.destroy(1,old);});check(frees==2 && delivery.pending(77).size()==2,"Original physical destruction and journal survive growth");
    check(delivery.acknowledge(77,identity(old),ack(old,retired.receipts.back().sequence.value)),"Original exact final ACK retains original authority");
    // A valid prefix and invalid final scope must never partially admit subjects.
    auto third=scope(3),fourth=scope(4);auto thirdJob=job(third);
    endpoint.native([&](auto& b){check(b.enroll(3,third,32) && b.enroll(4,fourth,32),"Actual two additional native actors");});
    check(endpoint.extendView(77,first.binding,{3,4}),"Actual native view grows atomically");
    auto foreign=fourth;foreign.binding.session={999};endpoint.native([&](auto& b){check(b.enroll(4,foreign,32),"Controlled later foreign native binding");check(b.acquire(3,third.binding,thirdJob).status==Result::Status::Admitted,"Valid prefix has actual own job");b.producerRefused(3,thirdJob);});
    check(denied([&]{delivery.extendSubjects(77);}),"Foreign final scope rejects entire journal extension");
    check(delivery.pending(77).empty() && endpoint.native([](auto& b){return b.recordCount();})==1,"Valid prefix cannot become visible on atomic refusal");
    const auto thirdReceipt=endpoint.native([](auto& b){return b.inspect().front().proofs.back();});
    check(!delivery.acknowledge(77,identity(thirdJob),ack(thirdJob,thirdReceipt.sequence.value)),"Unadmitted valid prefix cannot bypass atomic refusal via ACK");
    endpoint.native([&](auto& b){check(b.enroll(4,fourth,32),"Controlled own native binding restored");});
    auto changed=first;changed.context.incarnation={99};endpoint.native([&](auto& b){check(b.enroll(1,changed,32),"Controlled old entry incarnation changed");});
    check(denied([&]{delivery.extendSubjects(77);}) && delivery.pending(77).empty(),"Existing subject incarnation is immutable across extension");
    endpoint.native([&](auto& b){check(b.enroll(1,first,32),"Controlled exact original incarnation restored");});
    check(delivery.extendSubjects(77) && delivery.pending(77).size()==1,"Fresh valid extension delivers retained original third receipt");
    check(denied([&]{delivery.extendSubjects(88);}),"Foreign popup cannot extend journal membership");
    endpoint.unregisterView(77);check(denied([&]{delivery.extendSubjects(77);}),"Closed native receiver cannot extend journal");
    check(endpoint.registerView(77,first.binding,{1,2,3,4}),"Reused native address has new epoch");
    check(denied([&]{delivery.extendSubjects(77);}) && denied([&]{delivery.acknowledge(77,identity(thirdJob),ack(thirdJob,thirdReceipt.sequence.value));}),"Old journal receiver cannot cross reused native epoch");
    ReceiptDelivery replacement(endpoint,first.binding,77);
    check(replacement.pending(77).size()==1 && replacement.acknowledge(77,identity(thirdJob),ack(thirdJob,thirdReceipt.sequence.value)),"Explicit new receiver adopts retained broker proofs without new journal");
    check(endpoint.native([](auto& b){return b.recordCount()==0 && b.charge()==0 && b.requestFloor(1)==1 && b.requestFloor(2)==1 && b.requestFloor(3)==1;}) && endpoint.readers()==0,"All physical resources drain and historical floors survive");
    endpoint.unregisterView(77);
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}

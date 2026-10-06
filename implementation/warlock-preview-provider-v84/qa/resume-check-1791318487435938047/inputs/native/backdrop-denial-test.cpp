#include "family_producer.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static unsigned checks=0;
static void check(bool ok,const char* message){require(ok,message);++checks;}
template<class F>static void rejects(F f){bool failed=false;try{f();}catch(const std::exception&){failed=true;}check(failed,"Malformed or foreign denial rejected");}
struct PNG final:uri::Payload {
    std::array<uint8_t,12> bytes{137,80,78,71,13,10,26,10,1,2,3,4};
    uint64_t charge()const noexcept override{return 32;}
    std::span<const uint8_t> png()const noexcept override{return bytes;}
};
int main(){try {
    for(const auto& [native,reason]:std::array<std::pair<const char*,SourceDenial>,4>{{
        {"preview-client-locked",SourceDenial::Locked},{"preview-client-scope-source-unavailable",SourceDenial::SourceUnavailable},
        {"preview-client-scope-output-unavailable",SourceDenial::OutputUnavailable},{"preview-client-layout-unsupported",SourceDenial::LayoutUnsupported}}}) {
        Json reply(std::string("{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"")+native+"\"}");
        check(decodeFamilySourceDenial(reply,FamilyPlane::GeneratedBackdrop)==reason,"Exact native reason decoded");
    }
    for(const auto* raw:{"{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"transport-error\"}","{\"kind\":\"preview-client-scope\"}"}) {
        Json reply(raw);check(!decodeFamilySourceDenial(reply,FamilyPlane::GeneratedBackdrop),"Unknown failure does not become source denial");
    }
    for(const auto* raw:{"{\"protocolVersion\":2,\"kind\":\"refused\",\"reason\":\"preview-client-locked\"}",
        "{\"protocolVersion\":3.0,\"kind\":\"refused\",\"reason\":\"preview-client-locked\"}",
        "{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-client-locked\",\"extra\":true}",
        "{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":false}",
        "{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-client-locked\",\"reason\":\"preview-client-locked\"}"}) {
        rejects([&]{Json reply(raw);decodeFamilySourceDenial(reply,FamilyPlane::GeneratedBackdrop);});
    }
    for(const auto& [reason,expected]:std::array<std::pair<const char*,SourceDenial>,3>{{
        {"preview-family-backdrop-source-unavailable",SourceDenial::SourceUnavailable},
        {"preview-family-style-source-unavailable",SourceDenial::SourceUnavailable},
        {"preview-family-style-crop-unavailable",SourceDenial::LayoutUnsupported}}}) {
        Json reply(std::string("{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"")+reason+"\"}");
        check(decodeFamilySourceDenial(reply,FamilyPlane::GeneratedBackdrop)==expected,"Exact native family source denial decoded");
    }
    {Json reply("{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-family-backdrop-source-unavailable\"}");check(!decodeFamilySourceDenial(reply,FamilyPlane::Transparent),"Generated source refusal cannot settle transparent plane");}
    {Json reply("{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-family-backdrop-crop-unavailable\"}");check(!decodeFamilySourceDenial(reply,FamilyPlane::GeneratedBackdrop),"Undeclared generated crop alias remains unknown");}
    const Binding owner{{1},{2},{3}};
    {Json locked("{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-client-locked\"}");check(decodeClientRetirement(locked,owner,12)==ClientRetirement::PendingLock,"Known lock is pending, never retired");}
    const std::string completed="{\"protocolVersion\":3,\"kind\":\"preview-client-retired\",\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"requestId\":\"12\",\"ownedBytes\":\"0\"}";
    {Json reply(completed);check(decodeClientRetirement(reply,owner,12)==ClientRetirement::Retired,"Exact native retirement decoded");}
    for(const auto& raw:std::array<std::string,7>{
        "{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-client-scope-source-unavailable\"}",
        "{\"protocolVersion\":2,\"kind\":\"refused\",\"reason\":\"preview-client-locked\"}",
        "{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-client-locked\",\"ownedBytes\":\"0\"}",
        completed.substr(0,completed.size()-1)+",\"extra\":true}",
        [&]{auto v=completed;v.replace(v.find("\"ownedBytes\":\"0\""),16,"\"ownedBytes\":\"1\"");return v;}(),
        [&]{auto v=completed;v.replace(v.find("\"requestId\":\"12\""),16,"\"requestId\":\"13\"");return v;}(),
        [&]{auto v=completed;v.replace(v.find("\"session\":\"2\""),13,"\"session\":\"9\"");return v;}()}) {
        rejects([&]{Json reply(raw);decodeClientRetirement(reply,owner,12);});
    }
    for(const auto reason:{SourceDenial::Locked,SourceDenial::SourceUnavailable,SourceDenial::OutputUnavailable,SourceDenial::LayoutUnsupported}) {
        Scope scope{owner,{{1},{4},{5},{6},{7},{8},{9}},{10},1,true,true,false,true};
        const Job job{owner,scope.context,{1},{11},scope.clock,20};
        uri::Endpoint endpoint({1,4,1,32},1,1,[&](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{scope.clock,scope.now};});
        endpoint.native([&](auto& b){check(b.enroll(1,scope,32),"Own original scope enrolled");check(b.acquire(1,owner,job).status==Result::Status::Admitted,"Original job retained");});
        auto allocation=endpoint.native([&](auto& b){std::unique_ptr<const Buffer> payload=std::make_unique<const PNG>();return b.allocate(1,job,payload,50,Packet::Fidelity::Family,15);});
        auto packet=*allocation.receipts.at(0).packet;endpoint.native([&](auto& b){b.producerComplete(1,job);});
        check(endpoint.registerView(77,owner,{1}),"Own actual URI view");GError* error=nullptr;gsize size{};
        auto stream=endpoint.open(77,uri::encode(packet.token),&size,&error);check(stream && !error,"Actual held GIO reader before denial");
        for(const auto mutation:{0,1,2,3}) {
            auto denied=ScopeDenied(owner,{4},12,reason);auto wrong=packet;
            if(mutation==0)denied.binding.session.value++;
            if(mutation==1)denied.subject.value++;
            if(mutation==2)denied.request=0;
            if(mutation==3)wrong.token.sequence++;
            rejects([&]{endpoint.native([&](auto& b){familyDenied(b,job,wrong,denied);});});
            endpoint.native([&](auto& b){check(static_cast<bool>(b.fetch(1,owner,packet.token)) && b.charge()==32 && !b.inspect().at(0).cleanup,"Foreign denial preserves exact readable owner");});
        }
        auto wire=endpoint.native([&](auto& b){return familyDenied(b,job,packet,ScopeDenied(owner,{4},12,reason));});
        Json denial(wire);auto event=Json::child(denial.object(),"event");
        check(decodeJob(Json::child(event,"job"))==job && std::string_view(Json::text(event,"reason"))==denialName(reason),"Typed denial carries original job without scope or clock");
        std::array<uint8_t,4> bytes{};check(g_input_stream_read(stream,bytes.data(),bytes.size(),nullptr,&error)==-1 && error,"Held read independently denied");g_clear_error(&error);
        auto extra=endpoint.open(77,uri::encode(packet.token),&size,&error);check(!extra && error,"New read independently denied");g_clear_error(&error);
        endpoint.native([&](auto& b){check(b.charge()==32 && b.recordCount()==1 && b.inspect().at(0).job==job && !b.inspect().at(0).terminal,"Denial preserves charge, journal, original deadline and no terminal proof");check(!b.consumerComplete(1,job),"Held stream blocks physical drain");});
        check(g_input_stream_close(stream,nullptr,&error) && !error,"Exact held stream closes");g_object_unref(stream);
        endpoint.native([&](auto& b){check(b.consumerComplete(1,job) && b.charge()==32 && b.recordCount()==1,"Drained consumers alone do not retire producer");auto retired=b.destroy(1,job);check(retired.status==Result::Status::Complete && b.charge()==0 && b.recordCount()==1,"Component destruction retains terminal proof");check(b.acknowledge(1,owner,job,retired.receipts.at(0).sequence) && b.recordCount()==0,"Exact terminal ACK clears component journal");});
    }
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"scope\":\"Strict denial and retirement decoding; actual shared Broker and held/new GIO denial. Synthetic PNG; no native session lock or producer retirement claim\"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

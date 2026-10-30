#include "../native/effect_cancellation.hpp"
#include <json-glib/json-glib.h>
#include <cstdio>
#include <cstring>
#include <limits>
#include <stdexcept>
namespace Cancellation=warlock::cancellation;
// No untrusted strings are interpolated. Full intent is canonical typed data.
static bool cancellationIdentityJson(char* output,std::size_t capacity,const Cancellation::Key& key) noexcept {
    const auto& o=key.owner;const auto& i=key.intent;
    const int n=std::snprintf(output,capacity,
        "\"binding\":{\"lifetime\":\"%llu\",\"session\":\"%llu\",\"frontend\":\"%llu\"},\"intent\":{\"request\":\"%llu\",\"generation\":\"%llu\",\"incarnation\":\"%llu\",\"operation\":\"restore\",\"context\":{\"lifetime\":\"%llu\",\"epoch\":\"%llu\",\"output\":\"%llu\",\"revision\":\"%llu\"}}",
        (unsigned long long)o.lifetime,(unsigned long long)o.session,(unsigned long long)o.frontend,
        (unsigned long long)i.request,(unsigned long long)i.generation,(unsigned long long)i.incarnation,
        (unsigned long long)i.lifetime,(unsigned long long)i.epoch,(unsigned long long)i.output,(unsigned long long)i.revision);
    return n>0 && static_cast<std::size_t>(n)<capacity;
}
static const char* cancellationReason(Cancellation::Facts facts) noexcept {
    switch(facts.reason) {
        case Cancellation::Reason::Cancelled:return "cancelled-before-commit";
        case Cancellation::Reason::Deadline:return "original-deadline-expired";
        case Cancellation::Reason::Applied:return "applied";
        case Cancellation::Reason::Unproven:return "effect-unproven";
        case Cancellation::Reason::NativeRefusal:return facts.detail;
    }
    return nullptr;
}
static bool formatCancellation(Cancellation::Buffer& buffer,const Cancellation::Key& key,uint64_t id,uint64_t deadline,Cancellation::Phase phase,Cancellation::Facts facts) noexcept {
    char identity[1024];if(!id || !deadline || !cancellationIdentityJson(identity,sizeof identity,key))return false;
    int n=-1;
    if(phase==Cancellation::Phase::Prepared) {
        n=std::snprintf(buffer.data.data(),buffer.data.size(),"{\"protocolVersion\":3,\"kind\":\"effect-prepared\",\"cancellationProtocol\":1,\"effectProtocol\":1,%s,\"preparedId\":\"%llu\",\"deadlineMonotonicNs\":\"%llu\"}",identity,(unsigned long long)id,(unsigned long long)deadline);
    } else {
        const char* status=phase==Cancellation::Phase::Cancelled?"Cancelled":phase==Cancellation::Phase::Committed?"Committed":phase==Cancellation::Phase::Refused?"Refused":"Unknown";
        const auto* reason=cancellationReason(facts);if(!reason || !facts.revision || !facts.outputGeneration)return false;
        const auto size=std::strlen(reason);if(!size || size>128)return false;
        for(std::size_t j=0;j<size;++j)if(!((reason[j]>='a' && reason[j]<='z') || reason[j]=='-'))return false;
        n=std::snprintf(buffer.data.data(),buffer.data.size(),"{\"protocolVersion\":3,\"kind\":\"effect-outcome\",\"cancellationProtocol\":1,\"effectProtocol\":1,%s,\"preparedId\":\"%llu\",\"deadlineMonotonicNs\":\"%llu\",\"status\":\"%s\",\"reason\":\"%s\",\"revision\":\"%llu\",\"outputGeneration\":\"%llu\"}",identity,(unsigned long long)id,(unsigned long long)deadline,status,reason,(unsigned long long)facts.revision,(unsigned long long)facts.outputGeneration);
    }
    if(n<0 || static_cast<std::size_t>(n)>=buffer.data.size())return false;
    buffer.size=static_cast<std::size_t>(n);return true;
}

int main(){try {
    using namespace Cancellation;
    Key k{{1,101,1,1,3},1,{1,1,4,1,3,5,6,Intent::Operation::Restore}};
    unsigned checks=0;
    auto ensure=[&](bool v){++checks;if(!v)throw std::runtime_error("real formatter assertion");};
    for(auto phase:{Phase::Prepared,Phase::Cancelled,Phase::Committed,Phase::Refused,Phase::ExecutionUnknown}) {
        Buffer b{};ensure(formatCancellation(b,k,17,100,phase,{8,9,phase==Phase::Cancelled?Reason::Cancelled:Reason::Applied,nullptr}));
        JsonParser* p=json_parser_new();GError* e=nullptr;ensure(json_parser_load_from_data(p,b.data.data(),b.size,&e));
        auto* o=json_node_get_object(json_parser_get_root(p));ensure(json_object_get_int_member(o,"cancellationProtocol")==1 && json_object_get_int_member(o,"effectProtocol")==1);
        ensure(!std::strcmp(json_object_get_string_member(o,"preparedId"),"17") && !std::strcmp(json_object_get_string_member(o,"deadlineMonotonicNs"),"100"));
        auto* binding=json_object_get_object_member(o,"binding");ensure(!std::strcmp(json_object_get_string_member(binding,"frontend"),"3"));
        auto* intent=json_object_get_object_member(o,"intent");ensure(!std::strcmp(json_object_get_string_member(intent,"operation"),"restore"));
        if(phase!=Phase::Prepared) {const char* expected=phase==Phase::Cancelled?"Cancelled":phase==Phase::Committed?"Committed":phase==Phase::Refused?"Refused":"Unknown";ensure(!std::strcmp(json_object_get_string_member(o,"status"),expected));ensure(!std::strcmp(json_object_get_string_member(o,"revision"),"8"));}
        g_object_unref(p);
    }
    Buffer b{};ensure(!formatCancellation(b,k,0,100,Phase::Prepared,{}));ensure(!formatCancellation(b,k,17,0,Phase::Prepared,{}));ensure(!formatCancellation(b,k,17,100,Phase::Committed,{}));
    ensure(!formatCancellation(b,k,17,100,Phase::Refused,{8,9,Reason::NativeRefusal,"bad\"reason"}));
    ensure(!formatCancellation(b,k,17,100,Phase::Refused,{8,9,Reason::NativeRefusal,nullptr}));
    k.owner.lifetime=k.intent.lifetime=k.owner.session=k.owner.frontend=k.intent.epoch=k.intent.request=k.intent.generation=k.intent.incarnation=k.intent.output=k.intent.revision=std::numeric_limits<U>::max();
    ensure(formatCancellation(b,k,std::numeric_limits<U>::max(),std::numeric_limits<U>::max(),Phase::Committed,{std::numeric_limits<U>::max(),std::numeric_limits<U>::max(),Reason::Applied,nullptr}));
    ensure(b.size<b.data.size());
    std::printf("{\"passed\":true,\"checks\":%u}\n",checks);return 0;
} catch(const std::exception& e) {std::fprintf(stderr,"%s\n",e.what());return 1;}}

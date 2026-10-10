#pragma once
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>

namespace preview::resources {
struct Binding {uint64_t lifetime,session,frontend;};
struct Target {uint64_t capture,subject;};
enum class Operation {Observe,ReleaseExport,RetireProducer};
enum class Status {Observed,Settled,PendingExport,PendingLock};
struct Result {
    Binding binding;Target target;uint64_t request,sequence,clock,now;
    Operation operation;Status status;
    uint64_t producerBytes{},exportTransfer{},exportBytes{};
    bool locked{};
};
inline const char* name(Operation value){switch(value){case Operation::Observe:return "observe";case Operation::ReleaseExport:return "release-export";case Operation::RetireProducer:return "retire-producer";}throw std::invalid_argument("Native resource operation");}
inline const char* name(Status value){switch(value){case Status::Observed:return "Observed";case Status::Settled:return "Settled";case Status::PendingExport:return "PendingExport";case Status::PendingLock:return "PendingLock";}throw std::invalid_argument("Native resource status");}
inline void require(bool ok,const char* message){if(!ok)throw std::invalid_argument(message);}
inline std::string wire(const Result& result) {
    auto counter=[](uint64_t value){return "\""+std::to_string(value)+"\"";};
    return "{\"protocolVersion\":3,\"kind\":\"preview-client-resources\",\"resourceProtocol\":1,\"operation\":\""+std::string(name(result.operation))+
        "\",\"binding\":{\"lifetime\":"+counter(result.binding.lifetime)+",\"session\":"+counter(result.binding.session)+",\"frontend\":"+counter(result.binding.frontend)+
        "},\"requestId\":"+counter(result.request)+",\"captureRequest\":"+counter(result.target.capture)+",\"subjectIncarnation\":"+counter(result.target.subject)+
        ",\"sequence\":"+counter(result.sequence)+",\"clock\":"+counter(result.clock)+",\"now\":"+counter(result.now)+
        ",\"status\":\""+name(result.status)+"\",\"producerState\":\""+(result.producerBytes?"Owned":"Retired")+
        "\",\"producerBytes\":"+counter(result.producerBytes)+",\"exportState\":\""+(result.exportTransfer?"Live":"Released")+
        "\",\"exportTransfer\":"+counter(result.exportTransfer)+",\"exportBytes\":"+counter(result.exportBytes)+
        ",\"locked\":"+(result.locked?"true":"false")+"}";
}
// Caller binding and peer MUST come from the actual kernel-authenticated native
// registry. This operates on the real single capture slot, not UI declarations.
// Build the complete returned value before destroying any resource. A failed
// response allocation preserves both resources and the original sequence.
template<class Map,class Peer,class Prepare>
auto execute(Map& captures,Peer peer,Binding caller,Target target,uint64_t request,
        uint64_t now,bool locked,Operation operation,uint64_t transfer,uint64_t& sequence,Prepare&& prepare) {
    require(caller.lifetime && caller.session && caller.frontend && target.capture && target.subject &&
        request>target.capture && now,"Original native capture resource correlation");
    require(sequence<std::numeric_limits<uint64_t>::max(),"Native resource sequence exhausted");
    require(operation==Operation::Observe || operation==Operation::ReleaseExport || operation==Operation::RetireProducer,"Closed native resource operation");
    require(operation==Operation::ReleaseExport?transfer>0:transfer==0,"Original native export operation transfer");
    Result result{caller,target,request,sequence+1,caller.lifetime,now,operation,
        operation==Operation::Observe?Status::Observed:Status::Settled,0,0,0,locked};
    auto found=captures.find(peer);bool matching=false;
    if(found!=captures.end()) {
        const auto& probe=found->second;
        require(probe.session==caller.session && probe.frontend==caller.frontend,"Original native capture slot binding");
        if(probe.request==target.capture) {
            require(probe.incarnation==target.subject && probe.client && !probe.popup && !probe.family && !probe.crop &&
                !probe.styled && !probe.backdrop && probe.image && probe.image->charge(),"Exact original native client resource target");
            matching=true;result.producerBytes=probe.image->charge();
            if(probe.exported) {
                require(probe.exported->transfer && probe.exported->reservation && probe.exported->reservation->bytes(),"Actual original native export reservation");
                result.exportTransfer=probe.exported->transfer;result.exportBytes=probe.exported->reservation->bytes();
            }
        }
    }
    bool release=false,retire=false;
    if(matching && operation==Operation::ReleaseExport && result.exportTransfer) {
        require(transfer==result.exportTransfer,"Exact original native resource transfer");
        release=true;result.exportTransfer=result.exportBytes=0;
    }
    if(matching && operation==Operation::RetireProducer) {
        if(result.exportTransfer)result.status=Status::PendingExport;
        else if(locked)result.status=Status::PendingLock;
        else {retire=true;result.producerBytes=0;}
    }
    auto output=std::forward<Prepare>(prepare)(result);
    static_assert(std::is_nothrow_move_constructible_v<decltype(output)>,"Native resource response must move without failure after commit");
    // No fallible result construction occurs after the actual resource commit.
    if(release)found->second.exported.reset();
    if(retire)captures.erase(found);
    ++sequence;return output;
}
}

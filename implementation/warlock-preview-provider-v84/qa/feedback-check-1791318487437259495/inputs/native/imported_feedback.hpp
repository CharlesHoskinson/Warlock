#pragma once
#include "imported_admission.hpp"
#include "client_producer.hpp"

namespace preview::bridge {
inline std::string importedLocalFeedback(const ImportedStartAttempt& attempt,
        const SourceObservation& observed,uint64_t publication,uint64_t lease,
        uint64_t deadline,bool initial) {
    if(attempt.native.job || !publication || !lease || !deadline || !observed.request)return "[]";
    std::string outcome;
    switch(attempt.intent) {
        case ImportedIntentLedger::Admission::Invalid:return "[]";
        case ImportedIntentLedger::Admission::Capacity:outcome="capacity";break;
        case ImportedIntentLedger::Admission::Conflict:outcome="conflict";break;
        case ImportedIntentLedger::Admission::Expired:outcome="expired";break;
        case ImportedIntentLedger::Admission::Admitted:
            switch(attempt.native.status) {
                case demand::Attempt::Status::Capacity:outcome="capacity";break;
                case demand::Attempt::Status::NotReady:outcome="waiting";break;
                case demand::Attempt::Status::Exhausted:outcome="exhausted";break;
                case demand::Attempt::Status::Started:
                case demand::Attempt::Status::NativeRejected:return "[]";
            }
    }
    const auto& s=observed.scope;Wire out;
    const auto message=out.text("kind","demand-feedback").text("identity","family:"+std::to_string(s.context.incarnation.value))
        .begin("binding").binding(s.binding).end().counter("subject",s.context.incarnation.value)
        .counter("clock",s.clock.value).counter("publication",publication).counter("lease",lease)
        .counter("sequence",observed.request).counter("deadline",deadline).text("outcome",outcome).finish();
    if(!initial)return "["+message+"]";
    // A local source observation is not an issued demand. The distinct seed
    // establishes idle scope without opening capture or consuming its sequence.
    Wire seed;auto source=seed.text("kind","demand-seed").counter("publication",publication).counter("lease",lease)
        .text("identity","family:"+std::to_string(s.context.incarnation.value)).text("title","Client content").text("application","Native client").finish();
    source.pop_back();return "["+source+",\"source\":"+sourceJSON(observed)+"},"+message+"]";
}
}

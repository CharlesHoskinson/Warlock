#pragma once
#include "client_producer.hpp"

namespace preview::bridge {
inline bool importedEntryRetired(const Broker& broker,uint64_t entry) {
    const auto rows=broker.inspect();
    return std::none_of(rows.begin(),rows.end(),[&](const auto& row){return row.entry==entry;});
}
inline bool admitRetainedImportedPresentation(Broker& broker,uint64_t entry,const Job& original,const SourceObservation& current,const Packet& packet,uint64_t oldLease,uint64_t publication,uint64_t lease) {
    if(!entry || !publication || lease<=oldLease || packet.job!=original || !packet.signaled)return false;
    const auto& s=current.scope;const auto& admitted=broker.nativeScope(entry);
    require(current.kind==SourceObservation::Kind::UnqualifiedClientMain && !current.previewEligible &&
        s.binding==original.binding && s.context.lifetime==original.context.lifetime && s.context.incarnation==original.context.incarnation && s.clock==original.clock &&
        admitted.binding==s.binding && admitted.context==s.context && admitted.clock==s.clock && admitted.now==s.now &&
        admitted.present==s.present && admitted.sourceLive==s.sourceLive && admitted.locked==s.locked && admitted.gpuReady==s.gpuReady,
        "Retained imported presentation uses current admitted own native scope");
    if(!s.present || s.locked || !s.gpuReady || s.now>=packet.expires)return false;
    const auto rows=broker.inspect();const auto retained=std::find_if(rows.begin(),rows.end(),[&](const auto& row){return row.entry==entry && row.job==original;});
    if(retained==rows.end() || retained->cleanup || retained->terminal || !retained->packet)return false;
    const auto& owned=*retained->packet;
    return owned.job==packet.job && owned.token==packet.token && owned.signaled==packet.signaled && owned.expires==packet.expires && owned.fidelity==packet.fidelity && owned.coverage==packet.coverage && static_cast<bool>(broker.fetch(entry,original.binding,packet.token));
}
inline std::optional<Job> reserveImportedResume(demand::Coordinator& queue,uint64_t entry,const Job& prior,const SourceObservation& previous,uint64_t oldLease,const SourceObservation& fresh,uint64_t publication,uint64_t lease) {
    auto& broker=queue.nativeBroker();
    if(!entry || !publication || lease<=oldLease || !importedEntryRetired(broker,entry))return {};
    const auto& s=fresh.scope;const auto& old=previous.scope;
    require(fresh.kind==SourceObservation::Kind::UnqualifiedClientMain && !fresh.previewEligible &&
        s.binding==prior.binding && s.context.lifetime==prior.context.lifetime && s.context.incarnation==prior.context.incarnation && s.clock==prior.clock &&
        fresh.observation>previous.observation && fresh.request>previous.request && s.now>=old.now &&
        s.context.output>=old.context.output && s.context.privacy>=old.context.privacy && s.context.rendering>=old.context.rendering &&
        s.context.scene>=old.context.scene && s.context.content>=old.context.content &&
        (s.sourceLive==old.sourceLive || s.context.scene>old.context.scene),"Fresh own coherent imported resume observation");
    if(!s.present || !s.sourceLive || s.locked || !s.gpuReady || fresh.maximumTransferBytes>broker.limits().bytes)return {};
    require(s.now<=UINT64_MAX-2000000000ULL && broker.requestFloor(entry)==prior.request.value,"Original native imported deadline and own retained request floor");
    require(queue.observe({entry,lease,s,{lease},fresh.maximumTransferBytes,true}).accepted,"Own imported resume demand admission");
    const auto attempt=queue.start(entry,s.now+2000000000ULL);
    if(attempt.status==demand::Attempt::Status::NotReady || attempt.status==demand::Attempt::Status::Capacity)return {};
    require(attempt.status==demand::Attempt::Status::Started && attempt.job,"Exact new imported resume reservation");return attempt.job;
}
}

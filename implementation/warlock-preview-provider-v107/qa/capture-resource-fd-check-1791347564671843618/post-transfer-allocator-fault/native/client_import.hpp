#pragma once
#include "client_frame.hpp"
#include "client_resources.hpp"

namespace preview::bridge {
extern thread_local int mappedResourceAllocationFault;extern bool mappedResourceFaultEnabled;
// Publish only actual Broker adoption. A result allocation can throw after the
// Broker moved the buffer; keep its exact native mapping even on that exception.
// A refused adoption leaves the caller owning storage and no retained pointer.
inline Result allocateImportedMapping(Broker& broker,uint64_t entry,const Job& job,
        std::unique_ptr<const Buffer>& payload,fd::Mapped* candidate,fd::Mapped*& retained,uint64_t expires) {
    require(candidate && payload.get()==candidate && !retained,"Original unadopted imported mapping");
    try {
        if(mappedResourceFaultEnabled)mappedResourceAllocationFault=2;
        auto result=broker.allocate(entry,job,payload,expires);
        if(!payload)retained=candidate;
        return result;
    }catch(...) {
        if(!payload)retained=candidate;
        throw;
    }
}
// Imported storage has an independent lifetime. This admits only a fresh,
// authenticated client-scope observation, never a frontend timestamp or a
// surviving capture-registry record. Captured content/expiry remain unchanged.
inline std::optional<uri::NativeTime> importedClientTime(const fd::Header& frame,
        const ClientCapture& capture,const Job& job,const SourceObservation& current) {
    const auto& s=current.scope;
    if(!clientFrameMatches(frame,capture) || frame[fd::Magic]!=fd::MAGIC || frame[fd::Version]!=1 ||
       frame[fd::Status]!=0 || capture.binding!=job.binding || capture.context!=job.context ||
       capture.deadline!=job.deadline || job.clock.value!=job.binding.lifetime.value ||
       current.kind!=SourceObservation::Kind::UnqualifiedClientMain || current.previewEligible ||
       !current.observation || !current.request || !current.maximumTransferBytes ||
       current.maximumTransferBytes%4096 || frame[fd::Bytes]>current.maximumTransferBytes ||
       s.binding!=job.binding || s.context.lifetime!=job.context.lifetime ||
       s.context.incarnation!=job.context.incarnation || s.clock!=job.clock ||
       s.context.output!=job.context.output || s.context.privacy!=job.context.privacy ||
       s.context.rendering!=job.context.rendering || s.context.scene<job.context.scene ||
       s.context.content<job.context.content || !s.present || s.locked || !s.gpuReady ||
       s.now<frame[fd::Now] || s.now>=frame[fd::Expires])return {};
    return uri::NativeTime{s.clock,s.now};
}

// A native release/retirement acknowledgment settles only these backend
// obligations. It does not consume a local mmap, drain GIO readers, erase a
// Broker charge, generate a terminal receipt, or acknowledge the Elm journal.
class ImportedNativeOwnership {
    ClientCapture capture_;
    fd::Header frame_;
    bool exportReleased_{},producerRetired_{},pendingLock_{};
public:
    ImportedNativeOwnership(ClientCapture capture,fd::Header frame):capture_(capture),frame_(frame) {
        require(clientFrameMatches(frame_,capture_),"Exact sealed imported client ownership");
    }
    template<class Release,class Retire> bool settle(Release&& release,Retire&& retire) {
        if(!exportReleased_) {
            if(!std::invoke(std::forward<Release>(release),capture_,frame_[fd::Transfer]))return false;
            exportReleased_=true;
        }
        if(!producerRetired_) {
            const auto result=std::invoke(std::forward<Retire>(retire));
            require(result==ClientRetirement::Retired || result==ClientRetirement::PendingLock,"Typed native import retirement result");
            pendingLock_=result==ClientRetirement::PendingLock;
            if(pendingLock_)return false;
            producerRetired_=true;
        }
        return true;
    }
    bool settle(Native& native) {
        require(native.binding()==capture_.binding,"Same own native import retirement authority");
        return settle([&](const ClientCapture& capture,uint64_t transfer){return releaseClient(native,capture,transfer);},
                      [&]{return retireClientState(native);});
    }
    void observeResources(const ClientResourceSnapshot& fact) {
        require(fact.binding==capture_.binding && fact.capture==capture_.request &&
            fact.subject==capture_.context.incarnation && (!fact.exportTransfer || fact.exportTransfer==frame_[fd::Transfer]),
            "Exact original imported export before resource settlement");
        // Only the native resource decoder supplies this metadata. It cannot
        // establish local mapping or reader completion.
        if(!fact.exportTransfer)exportReleased_=true;
        if(!fact.producerBytes)producerRetired_=true;
        pendingLock_=fact.status==ClientResourceStatus::PendingLock;
    }
    bool exportReleased()const{return exportReleased_;}
    bool producerRetired()const{return producerRetired_;}
    bool pendingLock()const{return pendingLock_;}
};
}

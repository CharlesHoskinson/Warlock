#pragma once
#include "client_import.hpp"
#include "client_producer.hpp"

namespace preview::bridge {
// Shared native allocator for two imported subjects. Selection and visibility
// stay with the existing Elm owner. This route is explicit and does not alter
// the qualified legacy ClientProducer late-retirement path.
class ImportedClients {
    struct Frame {
        Job job;
        SourceObservation latest;
        SourceObservation admitted;
        std::optional<ClientCapture> capture;
        fd::Header header{};
        std::optional<ImportedNativeOwnership> nativeOwnership;
        std::optional<Packet> packet;
        fd::Mapped* mapping{};
        bool attempted{},cleanup{},mappingClosed{},denied{};
    };
    struct Authority {
        Native& native;
        std::map<uint64_t,Frame> frames;
        explicit Authority(Native& owner):native(owner){}
        std::optional<uri::NativeTime> time(uint64_t entry) noexcept {
            try {
                auto found=frames.find(entry);if(found==frames.end())return {};
                auto& f=found->second;if(!f.capture || !f.packet || f.cleanup || f.denied)return {};
                const auto current=native.clientScope(f.job.context.incarnation);
                const auto& a=f.latest;const auto& b=current;
                if(b.observation<=a.observation || b.request<=a.request || b.scope.now<a.scope.now ||
                   b.scope.context.scene<a.scope.context.scene || b.scope.context.content<a.scope.context.content ||
                   (b.scope.sourceLive!=a.scope.sourceLive && b.scope.context.scene<=a.scope.context.scene))return {};
                auto admitted=importedClientTime(f.header,*f.capture,f.job,current);
                if(admitted)f.latest=current;
                return admitted;
            }catch(...){return {};}
        }
    };
    std::shared_ptr<Authority> authority_;
    uri::Endpoint endpoint_;
    Frame& frame(uint64_t entry) {auto found=authority_->frames.find(entry);require(found!=authority_->frames.end(),"Enrolled imported source");return found->second;}
    bool drain(Broker& broker,uint64_t entry,Frame& f) {
        if(!f.cleanup || !f.mapping || !broker.consumerComplete(entry,f.job))return false;
        require(f.nativeOwnership.has_value(),"Retained backend retirement obligation");
        if(!f.nativeOwnership->settle(authority_->native))return false;
        require(f.mapping->close(),"Actual local imported mapping and FD close");f.mappingClosed=true;
        auto terminal=broker.destroy(entry,f.job);
        require(terminal.status==Result::Status::Complete && !terminal.receipts.empty(),"Physical imported terminal proof");f.mapping=nullptr;return true;
    }
public:
    static constexpr uint64_t byteLimit=128ULL*1024*1024;
    explicit ImportedClients(Native& native):authority_(std::make_shared<Authority>(native)),
        endpoint_({2,8,2,byteLimit},4,2,[authority=authority_](uint64_t entry){return authority->time(entry);}) {
        const auto binding=native.binding();
        require(endpoint_.enableDemand({{2,8,2,byteLimit},binding.lifetime,{binding.lifetime.value},1}),"One shared imported demand and physical Broker");
    }
    ImportedClients(const ImportedClients&)=delete;ImportedClients& operator=(const ImportedClients&)=delete;
    uri::Endpoint& endpoint(){return endpoint_;}
    std::string start(uint64_t entry,Id<Incarnation> subject,uint64_t publication,uint64_t lease) {
        require(entry && subject.value && publication && lease,"Trusted imported subject and presentation stamp");
        return endpoint_.nativeDemand([&](auto& queue) {
            require(authority_->frames.size()<2 && !authority_->frames.contains(entry),"Bounded distinct imported entries");
            for(const auto& [id,f]:authority_->frames) { (void)id;require(f.job.context.incarnation!=subject,"Distinct native imported subjects"); }
            const auto observed=authority_->native.clientScope(subject);const auto& s=observed.scope;
            require(observed.kind==SourceObservation::Kind::UnqualifiedClientMain && !observed.previewEligible &&
                s.binding==authority_->native.binding() && s.present && s.sourceLive && !s.locked && s.gpuReady &&
                s.now<=UINT64_MAX-2000000000ULL,"Current own live native imported demand");
            require(queue.observe({entry,lease,s,{lease},observed.maximumTransferBytes,true}).accepted,"Actual imported demand admission");
            const auto attempt=queue.start(entry,s.now+2000000000ULL);
            require(attempt.status==demand::Attempt::Status::Started && attempt.job,"Original imported job reservation");
            Frame f{};f.job=*attempt.job;f.latest=observed;f.admitted=observed;authority_->frames.emplace(entry,std::move(f));
            return "["+clientSeed(observed,publication,lease)+","+clientRequest(*attempt.job)+"]";
        });
    }
    Job job(uint64_t entry){return endpoint_.native([&](auto&){return frame(entry).job;});}
    std::string command(uint64_t entry,const std::string& identity,const std::string& text) {
        return endpoint_.native([&](Broker& broker) {
            auto& f=frame(entry);const auto command=decodeClientCommand(identity,text,f.job,f.packet);
            if(command==ClientCommand::Acquire) {
                require(!f.attempted && !f.cleanup,"Single original imported capture");
                // Native producer retirement is binding-wide. Never let a new
                // capture overwrite an unresolved earlier backend obligation.
                for(const auto& [id,other]:authority_->frames) {
                    if(id!=entry && other.attempted)require(other.nativeOwnership && other.nativeOwnership->producerRetired(),"Previous native producer retirement before another capture");
                }
                f.attempted=true;f.capture=captureClient(authority_->native,f.latest,f.job.deadline);
                auto received=authority_->native.query(fd::Get,f.capture->request,f.job.context.incarnation.value);
                require(received && received->rights.size()==1 && clientFrameMatches(received->words,*f.capture),"Exact imported native FD envelope");f.header=received->words;
                auto mapping=std::make_unique<fd::Mapped>(std::move(received->rights.front()),f.header,f.latest.maximumTransferBytes,fd::SourcePlane::ClientMain);
                f.mapping=mapping.get();std::unique_ptr<const Buffer> payload=std::move(mapping);
                auto allocated=broker.allocate(entry,f.job,payload,f.header[fd::Expires]);
                require(allocated.receipts.size()==1 && allocated.receipts.front().packet && !payload,"Shared Broker owns sealed local FD and mapping");
                const auto before=*allocated.receipts.front().packet;
                f.nativeOwnership.emplace(*f.capture,f.header);
                // Readiness means immutable local encoded bytes; backend
                // retirement remains independently recorded even under lock.
                auto ready=broker.producerComplete(entry,f.job);
                require(ready.receipts.size()==1 && ready.receipts.front().packet,"Imported encoded bytes complete");f.packet=*ready.receipts.front().packet;
                f.nativeOwnership->settle(authority_->native);
                return "["+frameEvent("offer",before)+","+frameEvent("fence",*f.packet)+"]";
            }
            if(command==ClientCommand::Cancel) {
                broker.cancel(entry,f.job.binding,f.job);f.cleanup=true;
                if(!f.attempted)broker.producerRefused(entry,f.job);
            }else {broker.release(entry,f.job.binding,f.job,f.packet->token);f.cleanup=true;}
            drain(broker,entry,f);return std::string("[]");
        });
    }
    bool pollRetirement(uint64_t entry) {
        return endpoint_.native([&](Broker& broker) {
            auto& f=frame(entry);
            if(f.nativeOwnership && !f.nativeOwnership->producerRetired())f.nativeOwnership->settle(authority_->native);
            return drain(broker,entry,f);
        });
    }
    std::string poll(uint64_t entry) {
        return endpoint_.native([&](Broker& broker) {
            auto& f=frame(entry);drain(broker,entry,f);
            if(!f.packet || f.cleanup || f.denied)return std::string("[]");
            try {
                auto current=authority_->native.clientScope(f.job.context.incarnation);
                require(current.kind==SourceObservation::Kind::UnqualifiedClientMain && !current.previewEligible &&
                    current.scope.binding==f.job.binding && current.scope.context.incarnation==f.job.context.incarnation &&
                    current.scope.context.lifetime==f.job.context.lifetime && current.scope.clock==f.job.clock,
                    "Actual own imported observation authority");
                require(broker.observe(entry,current.scope,current.maximumTransferBytes),"Coherent imported policy observation");
                const bool changed=clientFactsChanged(f.admitted,current);f.admitted=current;f.latest=current;
                std::string events=changed?clientObservation(current):"";
                if(current.scope.now>=f.packet->expires) {if(!events.empty())events+=",";events+=frameEvent("expired",*f.packet);}
                return events.empty()?std::string("[]"):"["+events+"]";
            }catch(const ScopeDenied& denied) {
                require(denied.binding==f.job.binding && denied.subject==f.job.context.incarnation && denied.request,"Exact imported native source denial");
                broker.release(entry,f.job.binding,f.job,f.packet->token);f.denied=true;
                Wire wire;
                return "["+wire.text("kind","event").text("identity","family:"+std::to_string(f.job.context.incarnation.value))
                    .begin("event").text("kind","source-denied").begin("job").job(f.job).end().text("reason",denialName(denied.reason)).end().finish()+"]";
            }
        });
    }
    std::optional<Packet> packet(uint64_t entry){return endpoint_.native([&](auto&){return frame(entry).packet;});}
    std::string status(uint64_t entry) {
        return endpoint_.native([&](auto& broker) {
            auto& f=frame(entry);Wire wire;
            return wire.begin("job").job(f.job).end().text("charge",std::to_string(broker.charge())).integer("records",broker.recordCount())
                .boolean("mappedFDClosed",f.mappingClosed).boolean("exportReleased",f.nativeOwnership && f.nativeOwnership->exportReleased())
                .boolean("producerRetired",f.nativeOwnership && f.nativeOwnership->producerRetired())
                .boolean("retirementPending",f.nativeOwnership && f.nativeOwnership->pendingLock()).finish();
        });
    }
    bool empty(){return endpoint_.readers()==0 && endpoint_.native([](auto& broker){return broker.recordCount()==0 && broker.charge()==0;});}
};
}

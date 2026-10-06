#pragma once
#include "client_import.hpp"
#include "client_producer.hpp"
#include "imported_lifecycle.hpp"
#include "imported_enrollment.hpp"
#include "imported_feedback.hpp"
#include "preview_retirement.hpp"
#include "retirement_journal.hpp"
#include "preview_delivery.hpp"
#include "imported_subjects.hpp"

namespace preview::bridge {
// Shared native allocator with two physical items and bounded subject actors.
// The legacy two-subject qualification keeps its original default. Selection and visibility
// stay with the existing Elm owner. This route is explicit and does not alter
// the qualified legacy ClientProducer late-retirement path.
class ImportedClients {
    struct Frame {
        Job job;
        uint64_t lease{};
        SourceObservation latest;
        SourceObservation admitted;
        std::optional<ClientCapture> capture;
        fd::Header header{};
        std::optional<ImportedNativeOwnership> nativeOwnership;
        std::optional<Packet> packet;
        std::optional<NativeStartIdentity> resumeIntent;
        std::optional<NativeStartIdentity> resumePredecessor;
        fd::Mapped* mapping{};
        bool attempted{},cleanup{},mappingClosed{},denied{},rejected{};
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
    const size_t subjectLimit_;
    std::shared_ptr<Authority> authority_;
    ImportedIntentLedger intents_;
    RetirementCursor retirementCursor_;
    uint64_t issuedEntryThrough_{};
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
    ImportedStartAttempt startObserved(demand::Coordinator& queue,uint64_t entry,Id<Incarnation> subject,
            uint64_t publication,uint64_t lease,uint64_t originalDeadline,uri::View* view=nullptr,bool laterIntent=false) {
        require(entry && subject.value && publication && lease,"Trusted imported subject and presentation stamp");
        require(entry>issuedEntryThrough_ || intents_.find(entry).has_value(),"Previously issued absent imported serial is permanently refused");
        require(authority_->frames.size()<subjectLimit_ && !authority_->frames.contains(entry),"Bounded distinct imported entries");
        for(const auto& [id,f]:authority_->frames) { (void)id;require(f.job.context.incarnation!=subject,"Distinct native imported subjects"); }
        const auto observed=authority_->native.clientScope(subject);const auto& s=observed.scope;
        require(observed.kind==SourceObservation::Kind::UnqualifiedClientMain && !observed.previewEligible &&
            s.binding==authority_->native.binding() && s.present && s.sourceLive && !s.locked && s.gpuReady &&
            s.now<=UINT64_MAX-2000000000ULL,"Current own live native imported demand");
        // A zero deadline uses retained history on a retry. Only the first
        // native issuance derives a cutoff from the original two-second bound.
        const auto previous=intents_.find(entry);
        const bool newStamp=laterIntent && previous &&
            (previous->publication!=publication || previous->lease!=lease);
        const auto deadline=newStamp?s.now+2000000000ULL:
            (originalDeadline?originalDeadline:(previous?previous->deadline:s.now+2000000000ULL));
        require(deadline<=s.now+2000000000ULL,"Original imported native two-second deadline bound");
        if(newStamp) {
            const auto decision=intents_.advance(entry,{s.binding,s.context.incarnation,s.clock,publication,lease,deadline},s.now);
            if(decision!=ImportedIntentLedger::Admission::Admitted) {
                ImportedStartAttempt refused{decision,{},"[]"};
                refused.feedback=importedLocalFeedback(refused,observed,publication,lease,previous->deadline,true);
                return refused;
            }
        }
        auto result=reserveImportedIntent(queue,intents_,entry,s,observed.maximumTransferBytes,publication,lease,deadline,view);
        if(intents_.find(entry) && entry>issuedEntryThrough_)issuedEntryThrough_=entry;
        if(result.native.job && queue.nativeBroker().owningEntry(*result.native.job)) {
            Frame f{};f.job=*result.native.job;f.lease=lease;f.latest=observed;f.admitted=observed;
            f.rejected=result.native.status!=demand::Attempt::Status::Started;
            authority_->frames.emplace(entry,std::move(f));
            // Elm registers the exact known job before seeing its real terminal
            // proof. A terminal native rejection never replays actual capture.
            result.events="["+clientSeed(observed,publication,lease)+","+clientRequest(*result.native.job)+"]";
        }
        const auto retained=intents_.find(entry);
        result.feedback=importedLocalFeedback(result,observed,publication,lease,retained?retained->deadline:deadline,true);
        return result;
    }
    ImportedStartAttempt resumeObserved(demand::Coordinator& queue,uint64_t entry,uint64_t publication,uint64_t lease,bool nextIntent=false) {
        auto& f=frame(entry);
        if(!publication || lease<=f.lease || !importedEntryRetired(queue.nativeBroker(),entry))return {};
        require(!f.mapping && (!f.attempted || (f.mappingClosed && f.nativeOwnership && f.nativeOwnership->exportReleased() && f.nativeOwnership->producerRetired() && !f.nativeOwnership->pendingLock())),"Own imported physical/backend retirement before new source query");
        SourceObservation fresh;
        try {fresh=authority_->native.clientScope(f.job.context.incarnation);}
        catch(const ScopeDenied&){return {};}
        auto result=reserveImportedResumeAttempt(queue,entry,f.job,f.latest,f.lease,fresh,publication,lease,f.resumeIntent,nextIntent,&f.resumePredecessor);
        if(f.resumeIntent)result.feedback=importedLocalFeedback(result,fresh,publication,lease,f.resumeIntent->deadline,false);
        if(result.native.job && queue.nativeBroker().owningEntry(*result.native.job)) {
            Frame replacement{};replacement.job=*result.native.job;replacement.lease=lease;replacement.latest=fresh;replacement.admitted=fresh;
            replacement.rejected=result.native.status!=demand::Attempt::Status::Started;
            f=std::move(replacement);
            result.events="["+clientSeed(fresh,publication,lease)+","+clientRequest(*result.native.job)+"]";
        }
        return result;
    }
public:
    static constexpr uint64_t byteLimit=128ULL*1024*1024;
    static Limits allocationLimits(size_t subjects) {
        require(subjects>0 && subjects<=256,"Bounded native imported subject actors");
        return {subjects,8,2,byteLimit};
    }
    explicit ImportedClients(Native& native,size_t subjects=2):subjectLimit_(subjects),authority_(std::make_shared<Authority>(native)),intents_(native.binding(),subjects),
        endpoint_(allocationLimits(subjects),4,2,[authority=authority_](uint64_t entry){return authority->time(entry);}) {
        const auto binding=native.binding();
        require(endpoint_.enableDemand({allocationLimits(subjectLimit_),binding.lifetime,{binding.lifetime.value},1}),"One shared imported demand and physical Broker");
        require(endpoint_.native([](auto& broker){return broker.enableMonotonicEntries();}),"Fresh imported native serial frontier");
    }
    ImportedClients(const ImportedClients&)=delete;ImportedClients& operator=(const ImportedClients&)=delete;
    uri::Endpoint& endpoint(){return endpoint_;}
    ImportedStartAttempt tryStart(uint64_t entry,Id<Incarnation> subject,uint64_t publication,uint64_t lease,uint64_t originalDeadline) {
        return endpoint_.nativeDemand([&](auto& queue) {
            return startObserved(queue,entry,subject,publication,lease,originalDeadline);
        });
    }
    ImportedStartAttempt tryStartAtReceiver(uint64_t popup,uint64_t epoch,uint64_t entry,Id<Incarnation> subject,uint64_t publication,uint64_t lease,uint64_t originalDeadline=0) {
        return endpoint_.nativeDemandView(popup,[&](auto& queue,uri::View* view) {
            require(importedReceiver(view,authority_->native.binding(),epoch),"Original imported receiver before native admission");
            return startObserved(queue,entry,subject,publication,lease,originalDeadline,view);
        });
    }
    std::optional<NativeStartIdentity> originalIntent(uint64_t entry) {
        return endpoint_.native([&](auto&){return intents_.find(entry);});
    }
    ImportedStartAttempt tryNextUnissuedAtReceiver(uint64_t popup,uint64_t epoch,uint64_t entry,Id<Incarnation> subject,uint64_t publication,uint64_t lease) {
        return endpoint_.nativeDemandView(popup,[&](auto& queue,uri::View* view) {
            require(importedReceiver(view,authority_->native.binding(),epoch),"Original imported receiver before explicit later intent");
            return startObserved(queue,entry,subject,publication,lease,0,view,true);
        });
    }
    bool hasJob(uint64_t entry) {return endpoint_.native([&](auto&){return authority_->frames.contains(entry);});}
    IncarnationRetirement retirementAtReceiver(uint64_t popup,uint64_t epoch,uint64_t entry) {
        return endpoint_.nativeDemandView(popup,[&](auto&,uri::View* view) {
            require(importedReceiver(view,authority_->native.binding(),epoch),"Original receiver before native retirement query");
            const auto original=intents_.find(entry);
            const auto found=authority_->frames.find(entry);
            require(original.has_value() || found!=authority_->frames.end(),"Known own imported retirement subject");
            const auto subject=found!=authority_->frames.end()?found->second.job.context.incarnation:original->subject;
            return observeIncarnationRetirement(authority_->native,subject,retirementCursor_);
        });
    }
    // Native ownership transaction only. The host must additionally establish
    // the Elm settlement/control barrier before making this operation visible
    // through its renderer channel. No JSON field can assert physical cleanup.
    std::optional<std::string> retireAtReceiver(uint64_t popup,uint64_t epoch,uint64_t entry,
            ReceiptDelivery& delivery,ImportedSubjects& subjects,
            RetirementJournal* journal=nullptr,std::string_view readiness={}) {
        return endpoint_.nativeRetirementView(popup,[&](auto& queue,uri::View* view,const auto& views)->std::optional<std::string> {
            const auto binding=authority_->native.binding();
            require(importedReceiver(view,binding,epoch),"Original receiver before native actor retirement query");
            const auto owned=subjects.active_.find(entry);
            require(owned!=subjects.active_.end(),"Known exact C actor retirement serial");
            const auto subject=owned->second;
            const auto frame=authority_->frames.find(entry);
            const auto intent=intents_.find(entry);
            require(frame!=authority_->frames.end() || intent.has_value(),"Own native imported retirement history");
            require((frame==authority_->frames.end() || (frame->second.job.binding==binding && frame->second.job.context.incarnation==subject)) &&
                intents_.canForgetRetired(entry,binding,subject),"Exact native frame and intent retirement subject");
            // Validate the original journal receiver before querying native.
            require(delivery.canForgetRetired(endpoint_,popup,view,entry,binding,subject),"Own original native receipt retirement receiver");
            if(journal)require(journal->acceptReady(popup,epoch,entry,readiness),
                "Exact retained Elm readiness before native retirement query");
            else require(readiness.empty(),"Legacy native retirement carries no renderer readiness");
            const auto fact=observeIncarnationRetirement(authority_->native,subject,retirementCursor_);
            if(fact.state!=IncarnationState::Retired)return {};
            auto& broker=queue.nativeBroker();
            if(!broker.canForgetRetired(entry,binding,subject) || !queue.canForgetRetired(entry,binding,subject))return {};
            for(const auto& [receiver,registered]:views)if(receiver!=popup && registered.entries.contains(entry))return {};
            if(frame!=authority_->frames.end()) {
                const auto& f=frame->second;
                if(f.mapping || (f.attempted && (!f.mappingClosed || !f.nativeOwnership ||
                    !f.nativeOwnership->exportReleased() || !f.nativeOwnership->producerRetired() ||
                    f.nativeOwnership->pendingLock())))return {};
            }
            uint64_t floor=0;
            const auto actor=broker.actors_.find(entry);
            if(actor!=broker.actors_.end())floor=actor->second.floor;
            // Allocate the wire before committing; nothing below can allocate,
            // query, fail validation or release an unsettled native resource.
            const ActorRetired final{fact,entry,subjects.issuedThrough_,floor};
            auto wire=encodeActorRetired(final);
            if(journal) {
                auto prepared=journal->prepare(popup,epoch,entry,final);
                if(!prepared)return {};
                // Reserve both retained and immediate wire before native erasure.
                wire=prepared->wire();
                if(!journal->commit(std::move(*prepared)))return {};
            }
            delivery.forgetRetired(entry);view->entries.erase(entry);
            queue.forgetRetired(entry);broker.forgetRetired(entry);
            intents_.forgetRetired(entry);authority_->frames.erase(entry);
            subjects.forgetRetired(entry);
            return wire;
        });
    }
    std::optional<std::string> observeRetirementForDelivery(uint64_t popup,uint64_t epoch,
            uint64_t entry,RetirementJournal& journal) {
        return endpoint_.nativeDemandView(popup,[&](auto&,uri::View* view)->std::optional<std::string> {
            const auto binding=authority_->native.binding();
            require(importedReceiver(view,binding,epoch),"Original receiver before retained native retirement observation");
            const auto original=intents_.find(entry);const auto frame=authority_->frames.find(entry);
            require(original.has_value() || frame!=authority_->frames.end(),"Known native retirement observation subject");
            const auto subject=frame!=authority_->frames.end()?frame->second.job.context.incarnation:original->subject;
            if(const auto* retained=journal.observation(popup,epoch,binding,entry)) {
                require(retained->subject==subject,"Original retained native retirement subject");
                return encodeIncarnationRetirement(*retained);
            }
            const auto fact=observeIncarnationRetirement(authority_->native,subject,retirementCursor_);
            if(fact.state!=IncarnationState::Retired || !journal.retain(popup,epoch,entry,fact))return {};
            return encodeIncarnationRetirement(fact);
        });
    }
    std::string pendingRetirementDelivery(uint64_t popup,uint64_t epoch,
            const ReceiptDelivery& delivery,const RetirementJournal& journal) {
        return endpoint_.nativeRetirementView(popup,[&](auto&,const uri::View* view,const auto&) {
            const auto binding=authority_->native.binding();
            require(importedReceiver(view,binding,epoch) && &delivery.endpoint_==&endpoint_,
                "Original own receiver before pending retirement delivery");
            delivery.view(popup,view);
            const auto* wire=journal.nextCompletion(popup,epoch,binding);
            return wire?"["+*wire+"]":std::string("[]");
        });
    }
    std::string pollRetirementDelivery(uint64_t popup,uint64_t epoch,
            ReceiptDelivery& delivery,ImportedSubjects& subjects,RetirementJournal& journal) {
        const auto waiting=endpoint_.nativeRetirementView(popup,[&](auto&,const uri::View* view,const auto&) {
            const auto binding=authority_->native.binding();
            require(importedReceiver(view,binding,epoch) && &delivery.endpoint_==&endpoint_,
                "Original receiver and Endpoint before readiness retry");
            delivery.view(popup,view);
            return journal.pendingReadiness(popup,epoch,binding);
        });
        for(const auto& ready:waiting) {
            const auto owned=subjects.active_.find(ready.entry);
            require(owned!=subjects.active_.end() && owned->second==ready.subject,
                "Original retained C actor before readiness retry");
            // Purely native revalidation of the retained input. No capture,
            // cancellation or final-proof ACK is repeated by this rendezvous.
            retireAtReceiver(popup,epoch,ready.entry,delivery,subjects,&journal,ready.wire);
        }
        return pendingRetirementDelivery(popup,epoch,delivery,journal);
    }
    bool acknowledgeRetirementDelivery(uint64_t popup,uint64_t epoch,
            const ReceiptDelivery& delivery,RetirementJournal& journal,std::string_view raw) {
        return endpoint_.nativeRetirementView(popup,[&](auto&,const uri::View* view,const auto&) {
            require(importedReceiver(view,authority_->native.binding(),epoch) && &delivery.endpoint_==&endpoint_,
                "Original own receiver before retirement processing acknowledgment");
            delivery.view(popup,view);
            return journal.acknowledge(popup,epoch,raw);
        });
    }
    std::string actorCounts(uint64_t popup,const ReceiptDelivery& delivery,const ImportedSubjects& subjects) {
        return endpoint_.nativeRetirementView(popup,[&](auto& queue,const uri::View* view,const auto&) {
            require(&delivery.endpoint_==&endpoint_,"Own native inventory endpoint");
            delivery.view(popup,view);
            return Wire().integer("subjects",subjects.size()).integer("frames",authority_->frames.size())
                .integer("intents",intents_.size()).integer("predecessors",intents_.predecessorCount())
                .integer("slots",queue.slotCount()).integer("actors",queue.nativeBroker().actorCount())
                .integer("receiverEntries",view?view->entries.size():0).integer("deliverySubjects",delivery.subjects_.size())
                .counter("entryIssuedThrough",subjects.issuedThrough_).counter("nativeEntryIssuedThrough",issuedEntryThrough_)
                .counter("brokerEntryIssuedThrough",queue.nativeBroker().issuedEntryThrough()).finish();
        });
    }
    std::string start(uint64_t entry,Id<Incarnation> subject,uint64_t publication,uint64_t lease) {
        auto attempt=tryStart(entry,subject,publication,lease,0);
        require(attempt.intent==ImportedIntentLedger::Admission::Admitted && attempt.native.status==demand::Attempt::Status::Started && attempt.native.job,"Original imported job reservation");
        return attempt.events;
    }
    Job job(uint64_t entry){return endpoint_.native([&](auto&){return frame(entry).job;});}
    uint64_t lease(uint64_t entry){return endpoint_.native([&](auto&){return frame(entry).lease;});}
    std::string resume(uint64_t entry,uint64_t publication,uint64_t lease) {
        return endpoint_.nativeDemand([&](auto& queue) {
            return resumeObserved(queue,entry,publication,lease).events;
        });
    }
    ImportedStartAttempt resumeAtReceiver(uint64_t popup,uint64_t epoch,uint64_t entry,uint64_t publication,uint64_t lease) {
        return endpoint_.nativeDemandView(popup,[&](auto& queue,uri::View* view) {
            require(importedReceiver(view,authority_->native.binding(),epoch),"Original imported resume receiver before native query");
            return resumeObserved(queue,entry,publication,lease);
        });
    }
    ImportedStartAttempt resumeNextAtReceiver(uint64_t popup,uint64_t epoch,uint64_t entry,uint64_t publication,uint64_t lease) {
        return endpoint_.nativeDemandView(popup,[&](auto& queue,uri::View* view) {
            require(importedReceiver(view,authority_->native.binding(),epoch),"Original imported receiver before explicit later resume query");
            return resumeObserved(queue,entry,publication,lease,true);
        });
    }
    std::string command(uint64_t entry,const std::string& identity,const std::string& text) {
        return endpoint_.native([&](Broker& broker) {
            auto& f=frame(entry);const auto command=decodeClientCommand(identity,text,f.job,f.packet);
            if(command==ClientCommand::Acquire) {
                if(f.rejected)return std::string("[]");
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
    std::string poll(uint64_t entry,uint64_t publication=0,uint64_t lease=0) {
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
                const bool newPresentation=admitRetainedImportedPresentation(broker,entry,f.job,current,*f.packet,f.lease,publication,lease);
                if(newPresentation)f.lease=lease;
                std::string events=(changed || newPresentation)?((publication && lease==f.lease)?clientSeed(current,publication,lease):clientObservation(current)):"";
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
            wire.begin("job").job(f.job).end();
            if(f.resumeIntent)wire.counter("resumeDeadline",f.resumeIntent->deadline).counter("resumePublication",f.resumeIntent->publication).counter("resumeLease",f.resumeIntent->lease);
            if(f.resumePredecessor)wire.counter("previousResumeDeadline",f.resumePredecessor->deadline).counter("previousResumePublication",f.resumePredecessor->publication).counter("previousResumeLease",f.resumePredecessor->lease);
            return wire.text("charge",std::to_string(broker.charge())).integer("records",broker.recordCount())
                .boolean("mappedFDClosed",f.mappingClosed).boolean("exportReleased",f.nativeOwnership && f.nativeOwnership->exportReleased())
                .boolean("producerRetired",f.nativeOwnership && f.nativeOwnership->producerRetired())
                .boolean("retirementPending",f.nativeOwnership && f.nativeOwnership->pendingLock()).finish();
        });
    }
    bool empty(){return endpoint_.readers()==0 && endpoint_.native([](auto& broker){return broker.recordCount()==0 && broker.charge()==0;});}
};
}

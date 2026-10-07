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
#include "imported_control_admission.hpp"
#include "retained_client_command.hpp"

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
        std::optional<ClientCaptureIntent> captureIntent;
        std::optional<ClientCapture> capture;
        std::optional<ClientResourceSnapshot> resources;
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
        ClientResourceCursor resources;
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
    bool reconciling_{};
    uint64_t reconciliationAfter_{};
    ImportedControlAdmission* controlAdmission_{};
    PreviewControlGrant controlGrant_{};
    uri::Endpoint endpoint_;
    Frame& frame(uint64_t entry) {auto found=authority_->frames.find(entry);require(found!=authority_->frames.end(),"Enrolled imported source");return found->second;}
    static bool backendEmpty(const Frame& f) {
        return !f.attempted || (f.resources && f.resources->backendEmpty()) ||
            (f.nativeOwnership && f.nativeOwnership->exportReleased() && f.nativeOwnership->producerRetired() && !f.nativeOwnership->pendingLock());
    }
    bool drainReconciled(Broker& broker,uint64_t entry,Frame& f) {
        auto record=broker.record(entry,f.job);
        if(!record || record->terminal)return false;
        if(!f.cleanup) {
            broker.cancel(entry,f.job.binding,f.job);f.cleanup=true;
        }
        if(!f.attempted) {
            auto result=broker.producerRefused(entry,f.job);return result.status==Result::Status::Complete;
        }
        require(f.captureIntent.has_value(),"Original capture intent before backend reconciliation");
        auto observe=[&](ClientResourceOperation operation,uint64_t transfer) {
            auto fact=clientResources(authority_->native,*f.captureIntent,operation,transfer,authority_->resources);
            if(f.nativeOwnership)f.nativeOwnership->observeResources(fact);
            f.resources=fact;
        };
        // Fresh observation repairs a lost release/retirement acknowledgment.
        // No original capture request or Unknown acquisition is invoked here.
        observe(ClientResourceOperation::Observe,0);
        if(f.resources->exportTransfer)observe(ClientResourceOperation::ReleaseExport,f.resources->exportTransfer);
        if(f.resources->producerBytes)observe(ClientResourceOperation::RetireProducer,0);
        if(!f.resources->backendEmpty())return false;
        if(!record->buffer && !record->packet) {
            require(!f.mapping && !f.packet,"No adopted local storage before unoffered reservation settlement");
            f.mappingClosed=true;
            const auto terminal=broker.producerRefused(entry,f.job);
            return terminal.status==Result::Status::Complete;
        }
        require(record->buffer && record->packet && (f.mappingClosed || record->buffer.get()==f.mapping),
            "Actual Broker mapping custody before reconciled local retirement");
        // The sealed mapping constructor validated immutable encoded storage.
        // Adoption can precede a result-allocation exception; this completion
        // never fabricates a producer refusal for an adopted packet.
        if(!record->producerDone)broker.producerComplete(entry,f.job);
        if(!broker.consumerComplete(entry,f.job))return false;
        if(!f.mappingClosed) {
            require(f.mapping && f.mapping->close(),"Actual reconciled local mapping and FD close");
            f.mappingClosed=true;f.mapping=nullptr;
        }
        const auto terminal=broker.destroy(entry,f.job);
        return terminal.status==Result::Status::Complete;
    }
    bool drain(Broker& broker,uint64_t entry,Frame& f) {
        if(reconciling_)return drainReconciled(broker,entry,f);
        if(!f.cleanup || !f.mapping || !broker.consumerComplete(entry,f.job))return false;
        require(f.nativeOwnership.has_value(),"Retained backend retirement obligation");
        if(!f.nativeOwnership->settle(authority_->native))return false;
        require(f.mapping->close(),"Actual local imported mapping and FD close");f.mappingClosed=true;
        auto terminal=broker.destroy(entry,f.job);
        require(terminal.status==Result::Status::Complete && !terminal.receipts.empty(),"Physical imported terminal proof");f.mapping=nullptr;return true;
    }
    ImportedStartAttempt startObserved(demand::Coordinator& queue,uint64_t entry,Id<Incarnation> subject,
            uint64_t publication,uint64_t lease,uint64_t originalDeadline,uri::View* view=nullptr,bool laterIntent=false) {
        require(!reconciling_ && entry && subject.value && publication && lease,"Trusted open imported subject and presentation stamp");
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
        auto issue=[&]() -> ImportedStartAttempt {
          if(newStamp) {
            const auto decision=intents_.advance(entry,{s.binding,s.context.incarnation,s.clock,publication,lease,deadline},s.now);
            if(decision!=ImportedIntentLedger::Admission::Admitted) {
                ImportedStartAttempt refused{decision,{},"[]"};
                refused.feedback=importedLocalFeedback(refused,observed,publication,lease,previous->deadline,true);
                return refused;
            }
          }
          return reserveImportedIntent(queue,intents_,entry,s,observed.maximumTransferBytes,publication,lease,deadline,view);
        };
        auto result=controlAdmission_?controlAdmission_->admit(controlGrant_,view,queue.nativeBroker(),entry,s,issue):issue();
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
    ImportedStartAttempt resumeObserved(demand::Coordinator& queue,uint64_t entry,uint64_t publication,uint64_t lease,bool nextIntent=false,uri::View* view=nullptr) {
        auto& f=frame(entry);
        require(!reconciling_,"Quarantined original binding cannot resume acquisition");
        if(!publication || lease<=f.lease || !importedEntryRetired(queue.nativeBroker(),entry))return {};
        require(!f.mapping && (!f.attempted || (f.mappingClosed && backendEmpty(f))),"Own imported physical/backend retirement before new source query");
        if(controlAdmission_ && controlAdmission_->containsJob(entry)) {
            if(!controlAdmission_->releaseRetiredJob(controlGrant_,view,queue.nativeBroker(),entry,f.job))
                return {ImportedIntentLedger::Admission::Capacity,{},"[]"};
        }
        SourceObservation fresh;
        try {fresh=authority_->native.clientScope(f.job.context.incarnation);}
        catch(const ScopeDenied&){return {};}
        auto issue=[&]{return reserveImportedResumeAttempt(queue,entry,f.job,f.latest,f.lease,fresh,publication,lease,f.resumeIntent,nextIntent,&f.resumePredecessor);};
        auto result=controlAdmission_?controlAdmission_->admit(controlGrant_,view,queue.nativeBroker(),entry,fresh.scope,issue):issue();
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
    static std::string reconciliationIdentity(Binding binding) {
        return "binding:"+std::to_string(binding.lifetime.value)+":"+std::to_string(binding.session.value)+":"+std::to_string(binding.frontend.value);
    }
    static std::string reconciliationBody(Binding binding) {
        const auto command=Wire().text("kind","reconcile").begin("binding").binding(binding).end().finish();
        auto body=Wire().text("identity",reconciliationIdentity(binding)).finish();body.pop_back();
        return body+",\"commands\":["+command+"]}";
    }
    std::optional<ImportedControlAdmission::Proposal> proposeReconciliation(PreviewControlGrant actual,
            const std::string& identity,const std::string& text) {
        return endpoint_.nativeDemandView(actual.receiver,[&](auto& queue,uri::View* view) {
            const auto binding=authority_->native.binding();
            require(controlAdmission_ && preview_control_grant_equal(controlGrant_,actual) && importedReceiver(view,binding,actual.epoch),
                "Original receiver before canonical native reconciliation proposal");
            require(!text.empty() && text.size()<=4096 && !identity.empty() && identity.size()<=512,"Bounded reconciliation proposal");
            Json message(text);auto object=message.object();Json::fields(object,{"kind","binding"});
            require(std::string_view(Json::text(object,"kind"))=="reconcile" && decodeBinding(Json::child(object,"binding"))==binding,
                "Typed original native binding reconciliation");
            if(identity!=reconciliationIdentity(binding)) {
                bool known=false;
                for(const auto& [entry,f]:authority_->frames) {(void)entry;if(identity=="family:"+std::to_string(f.job.context.incarnation.value))known=true;}
                require(known,"Original retained family before binding reconciliation deduplication");
            }
            return controlAdmission_->issueReconciliation(actual,view,queue.nativeBroker(),reconciliationBody(binding));
        });
    }
    void reconcileAtReceiver(PreviewControlGrant actual,const std::string& identity,const std::string& text) {
        endpoint_.nativeDemandView(actual.receiver,[&](auto& queue,uri::View* view) {
            const auto binding=authority_->native.binding();const auto body=reconciliationBody(binding);
            Json message(text);auto object=message.object();Json::fields(object,{"kind","binding"});
            require(identity==reconciliationIdentity(binding) && std::string_view(Json::text(object,"kind"))=="reconcile" &&
                decodeBinding(Json::child(object,"binding"))==binding && controlAdmission_ &&
                controlAdmission_->reconciliationDispatched(actual,view,queue.nativeBroker(),body,true),
                "Original currently invoking native reconciliation ticket");
            // Retain quarantine before any fallible cleanup. Polling may finish
            // original obligations even if this dispatcher response is lost.
            reconciling_=true;
        });
    }
    bool pollReconciliation(PreviewControlGrant actual) {
        return endpoint_.nativeDemandView(actual.receiver,[&](auto& queue,uri::View* view) {
            if(!reconciling_)return false;
            require(controlAdmission_ && controlAdmission_->reconciliationDispatched(actual,view,queue.nativeBroker(),
                reconciliationBody(authority_->native.binding())),"Original dispatched reconciliation before native polling");
            // At most one original job and three metadata operations per poll.
            // The entry cursor advances before effects, so one failing peer
            // cannot monopolize the bounded native cohort.
            auto begin=authority_->frames.upper_bound(reconciliationAfter_);
            for(size_t n=0;n<authority_->frames.size();++n) {
                if(begin==authority_->frames.end())begin=authority_->frames.begin();
                auto& [entry,f]=*begin++;auto record=queue.nativeBroker().record(entry,f.job);
                if(!record || record->terminal)continue;
                reconciliationAfter_=entry;return drainReconciled(queue.nativeBroker(),entry,f);
            }
            return false;
        });
    }
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
    // Opt in only before any intent, actor or job exists. The endpoint enrolled
    // an empty trusted receiver first; no old obligations can be adopted/reset.
    void attachControlAdmission(ImportedControlAdmission& admission,PreviewControlGrant grant) {
        endpoint_.nativeDemandView(grant.receiver,[&](auto& queue,uri::View* view){
            const auto owner=authority_->native.binding();
            require(!controlAdmission_ && authority_->frames.empty() && !intents_.size() &&
                !queue.slotCount() && queue.nativeBroker().inspect().empty() &&
                view && view->entries.empty() && importedReceiver(view,owner,grant.epoch) &&
                grant.lifetime==owner.lifetime.value && grant.session==owner.session.value && grant.frontend==owner.frontend.value &&
                admission.ownsBroker(queue.nativeBroker(),grant),"Fresh original receiver and owning admission guard before jobs");
            controlGrant_=grant;controlAdmission_=&admission;
        });
    }
    // A proposal carries immutable frontend command bytes, never a frontend
    // ordinal or cleanup authority. Native selects a stable purpose slot only
    // after checking its actual frame/packet/terminal journal under this lock.
    std::optional<ImportedControlAdmission::Proposal> proposeJobControl(
            PreviewControlGrant actual,uint64_t entry,const std::string& identity,
            const std::string& text) {
        return endpoint_.nativeDemandView(actual.receiver,[&](auto& queue,uri::View* view)
                ->std::optional<ImportedControlAdmission::Proposal> {
            require(controlAdmission_ && preview_control_grant_equal(controlGrant_,actual) &&
                importedReceiver(view,authority_->native.binding(),actual.epoch),
                "Original attached native receiver before command proposal decoding");
            require(!text.empty() && text.size()<=4096 && !identity.empty() && identity.size()<=512,
                "Bounded immutable frontend command proposal");
            Json message(text);auto object=message.object();const std::string_view kind=Json::text(object,"kind");
            require(kind=="acquire" || kind=="cancel" || kind=="release" || kind=="acknowledge",
                "Closed original job command proposal union");
            const auto original=kind=="release"?decodeJob(Json::child(Json::child(object,"frame"),"job")):
                decodeJob(Json::child(object,"job"));
            require(original.binding==authority_->native.binding() &&
                identity=="family:"+std::to_string(original.context.incarnation.value),
                "Exact original native proposal family and binding");
            auto body=Wire().text("identity",identity).finish();body.pop_back();
            body+=",\"commands\":["+text+"]}";
            auto& broker=queue.nativeBroker();
            if(auto retry=controlAdmission_->retryJobControl(actual,view,broker,entry,original,body))return retry;
            auto& f=frame(entry);require(f.job==original,"Current actual native job before new ticket");
            uint64_t slot=0;
            if(kind=="acknowledge") {
                Json::fields(object,{"kind","job","sequence"});const auto sequence=message.counter("sequence");
                const auto records=broker.inspect();
                const auto record=std::find_if(records.begin(),records.end(),[&](const auto& row){return row.entry==entry && row.job==original;});
                require(record!=records.end() && record->terminal && !record->bytes &&
                    !record->proofs.empty() && record->proofs.size()<=2,
                    "Actual native settled terminal proofs before acknowledgment ticket");
                const auto proof=std::find_if(record->proofs.begin(),record->proofs.end(),[&](const auto& row){return row.entry==entry && row.job==original && row.sequence.value==sequence;});
                require(proof!=record->proofs.end(),"Exact original native terminal sequence");
                slot=4+static_cast<uint64_t>(std::distance(record->proofs.begin(),proof));
            }else {
                const auto command=decodeRetainedClientCommand(identity,text,f.job,f.packet);
                if(command==ClientCommand::Acquire) {
                    require(f.rejected || (!f.attempted && !f.cleanup),"No new ticket after actual acquisition or cleanup");slot=1;
                }else slot=command==ClientCommand::Cancel?2:3;
            }
            return controlAdmission_->issueJobControl(actual,view,broker,entry,original,slot,body);
        });
    }
    std::optional<ImportedControlAdmission::Proposal> proposeActorControl(
            PreviewControlGrant actual,uint64_t entry,const std::string& identity,
            const std::string& text,RetirementJournal& journal) {
        return endpoint_.nativeDemandView(actual.receiver,[&](auto& queue,uri::View* view)
                ->std::optional<ImportedControlAdmission::Proposal> {
            require(controlAdmission_ && preview_control_grant_equal(controlGrant_,actual) &&
                importedReceiver(view,authority_->native.binding(),actual.epoch),
                "Original attached receiver before actor proposal decoding");
            require(!text.empty() && text.size()<=4096 && !identity.empty() && identity.size()<=512,
                "Bounded immutable actor command proposal");
            auto& broker=queue.nativeBroker();const auto subject=controlAdmission_->actorSubject(entry);
            require(identity=="family:"+std::to_string(subject.value),"Exact native retained actor proposal family");
            auto body=Wire().text("identity",identity).finish();body.pop_back();body+=",\"commands\":["+text+"]}";
            if(auto retry=controlAdmission_->retryActorControl(actual,view,broker,entry,subject,body))return retry;
            Json message(text);const std::string_view kind=Json::text(message.object(),"kind");uint64_t slot=0;
            if(kind=="retire-ready") {
                require(journal.ready(actual.receiver,actual.epoch,entry,text),"Exact original retained native retirement observation");slot=1;
            }else {
                require(kind=="retire-delivery-ack","Closed native actor control proposal union");
                const auto final=journal.completionForAcknowledgment(actual.receiver,actual.epoch,text);
                require(final && final->entry==entry && final->native.binding==authority_->native.binding() &&
                    final->native.subject==subject,"Actual original contiguous native actor completion");slot=2;
            }
            return controlAdmission_->issueActorControl(actual,view,broker,entry,subject,slot,body);
        });
    }
    size_t settleConfirmedActorControls(PreviewControlGrant actual) {
        return endpoint_.nativeDemandView(actual.receiver,[&](auto& queue,uri::View* view){
            require(controlAdmission_ && preview_control_grant_equal(controlGrant_,actual),"Original attached actor confirmation receiver");
            return controlAdmission_->collectConfirmedActors(actual,view,queue.nativeBroker());
        });
    }
    bool canCloseControlBinding(PreviewControlGrant actual) {
        return endpoint_.nativeDemandView(actual.receiver,[&](auto& queue,uri::View* view){
            require(controlAdmission_ && preview_control_grant_equal(controlGrant_,actual),"Original attached binding close receiver");
            if(!authority_->frames.empty() || intents_.size() || queue.slotCount() || !view || !view->entries.empty())return false;
            return controlAdmission_->canReleaseBinding(actual,view,queue.nativeBroker());
        });
    }
    bool closeControlBinding(PreviewControlGrant actual) {
        return endpoint_.nativeDemandView(actual.receiver,[&](auto& queue,uri::View* view){
            require(controlAdmission_ && preview_control_grant_equal(controlGrant_,actual),"Original attached binding close receiver");
            if(!authority_->frames.empty() || intents_.size() || queue.slotCount() || !view || !view->entries.empty())return false;
            return controlAdmission_->releaseBinding(actual,view,queue.nativeBroker());
        });
    }
    ImportedStartAttempt tryStart(uint64_t entry,Id<Incarnation> subject,uint64_t publication,uint64_t lease,uint64_t originalDeadline) {
        return endpoint_.nativeDemand([&](auto& queue) {
            require(!controlAdmission_,"Controlled admission requires original native receiver");
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
            if(controlAdmission_) {
                auto body=Wire().text("identity","family:"+std::to_string(subject.value)).finish();body.pop_back();
                body+=",\"commands\":["+std::string(readiness)+"]}";
                require(controlAdmission_->actorDispatched(controlGrant_,view,queue.nativeBroker(),entry,1,body),
                    "Original native issued and dispatched readiness before actor effect");
            }
            if(journal)require(journal->acceptReady(popup,epoch,entry,readiness),
                "Exact retained Elm readiness before native retirement query");
            else require(readiness.empty(),"Legacy native retirement carries no renderer readiness");
            auto& broker=queue.nativeBroker();
            if(!broker.canForgetRetired(entry,binding,subject) || !queue.canForgetRetired(entry,binding,subject))return {};
            for(const auto& [receiver,registered]:views)if(receiver!=popup && registered.entries.contains(entry))return {};
            if(frame!=authority_->frames.end()) {
                const auto& f=frame->second;
                if(f.mapping || (f.attempted && (!f.mappingClosed || !backendEmpty(f))))return {};
            }
            if(controlAdmission_) {
                require(journal,"Controlled actor removal retains original final delivery journal");
                if(controlAdmission_->containsJob(entry)) {
                    require(frame!=authority_->frames.end(),"Original frame before confirmed job control release");
                    if(!controlAdmission_->releaseRetiredJob(controlGrant_,view,broker,entry,frame->second.job))return {};
                }
                require(controlAdmission_->canCommitActorRetirement(controlGrant_,view,broker,entry,subject),
                    "Original native actor quota prepared before all-map removal");
            }
            // No synchronous native query while a local owner still blocks
            // retirement. These checks cannot grant removal: a fresh exact
            // native Retired fact remains mandatory after every barrier clears.
            const auto fact=observeIncarnationRetirement(authority_->native,subject,retirementCursor_);
            if(fact.state!=IncarnationState::Retired)return {};
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
            if(controlAdmission_)controlAdmission_->commitActorRetirement(entry);
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
            return journal.nextReadiness(popup,epoch,binding);
        });
        if(waiting) {
            const auto& ready=*waiting;
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
        return endpoint_.nativeRetirementView(popup,[&](auto& queue,const uri::View* view,const auto&) {
            require(importedReceiver(view,authority_->native.binding(),epoch) && &delivery.endpoint_==&endpoint_,
                "Original own receiver before retirement processing acknowledgment");
            delivery.view(popup,view);
            if(!controlAdmission_)return journal.acknowledge(popup,epoch,raw);
            const auto final=journal.completionForAcknowledgment(popup,epoch,raw);
            require(final && controlAdmission_->canAcknowledgeActor(final->entry,final->native.subject),
                "Actual original retired actor before final acknowledgment effect");
            auto body=Wire().text("identity","family:"+std::to_string(final->native.subject.value)).finish();body.pop_back();
            body+=",\"commands\":["+std::string(raw)+"]}";
            require(controlAdmission_->actorDispatched(controlGrant_,view,queue.nativeBroker(),final->entry,2,body,true),
                "Original native final ACK currently invoking before processing-prefix mutation");
            if(!journal.acknowledge(popup,epoch,raw))return false;
            controlAdmission_->commitActorAcknowledgment(final->entry);return true;
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
    std::optional<ClientCaptureIntent> captureIntent(uint64_t entry){return endpoint_.native([&](auto&){return frame(entry).captureIntent;});}
    uint64_t lease(uint64_t entry){return endpoint_.native([&](auto&){return frame(entry).lease;});}
    std::string resume(uint64_t entry,uint64_t publication,uint64_t lease) {
        return endpoint_.nativeDemand([&](auto& queue) {
            require(!controlAdmission_,"Controlled resume requires original native receiver");
            return resumeObserved(queue,entry,publication,lease).events;
        });
    }
    ImportedStartAttempt resumeAtReceiver(uint64_t popup,uint64_t epoch,uint64_t entry,uint64_t publication,uint64_t lease) {
        return endpoint_.nativeDemandView(popup,[&](auto& queue,uri::View* view) {
            require(importedReceiver(view,authority_->native.binding(),epoch),"Original imported resume receiver before native query");
            return resumeObserved(queue,entry,publication,lease,false,view);
        });
    }
    ImportedStartAttempt resumeNextAtReceiver(uint64_t popup,uint64_t epoch,uint64_t entry,uint64_t publication,uint64_t lease) {
        return endpoint_.nativeDemandView(popup,[&](auto& queue,uri::View* view) {
            require(importedReceiver(view,authority_->native.binding(),epoch),"Original imported receiver before explicit later resume query");
            return resumeObserved(queue,entry,publication,lease,true,view);
        });
    }
    std::string command(uint64_t entry,const std::string& identity,const std::string& text) {
        return endpoint_.native([&](Broker& broker) {
            auto& f=frame(entry);const auto command=controlAdmission_?
                decodeRetainedClientCommand(identity,text,f.job,f.packet):decodeClientCommand(identity,text,f.job,f.packet);
            if(command==ClientCommand::Acquire) {
                if(f.rejected)return std::string("[]");
                require(!f.attempted && !f.cleanup && !reconciling_,"Single original imported capture");
                // Native producer retirement is binding-wide. Never let a new
                // capture overwrite an unresolved earlier backend obligation.
                for(const auto& [id,other]:authority_->frames) {
                    if(id!=entry && other.attempted)require(backendEmpty(other),"Previous native producer retirement before another capture");
                }
                f.captureIntent.emplace(prepareClientCapture(authority_->native,f.latest,f.job.deadline));
                f.attempted=true;f.capture=captureClient(authority_->native,*f.captureIntent);
                auto received=authority_->native.query(fd::Get,f.capture->request,f.job.context.incarnation.value);
                require(received && received->rights.size()==1 && clientFrameMatches(received->words,*f.capture),"Exact imported native FD envelope");f.header=received->words;
                // Own the exact export before mapping/adoption can fail. This
                // does not establish local FD drain or producer retirement.
                f.nativeOwnership.emplace(*f.capture,f.header);
                auto mapping=std::make_unique<fd::Mapped>(std::move(received->rights.front()),f.header,f.latest.maximumTransferBytes,fd::SourcePlane::ClientMain);
                auto candidate=mapping.get();std::unique_ptr<const Buffer> payload=std::move(mapping);
                auto allocated=allocateImportedMapping(broker,entry,f.job,payload,candidate,f.mapping,f.header[fd::Expires]);
                require(allocated.receipts.size()==1 && allocated.receipts.front().packet && !payload,"Shared Broker owns sealed local FD and mapping");
                const auto before=*allocated.receipts.front().packet;
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
            if(reconciling_)return drainReconciled(broker,entry,f);
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
                .boolean("mappedFDClosed",f.mappingClosed).boolean("exportReleased",f.resources?!f.resources->exportTransfer:(f.nativeOwnership && f.nativeOwnership->exportReleased()))
                .boolean("producerRetired",f.resources?!f.resources->producerBytes:(f.nativeOwnership && f.nativeOwnership->producerRetired()))
                .boolean("retirementPending",f.resources?f.resources->status==ClientResourceStatus::PendingLock:(f.nativeOwnership && f.nativeOwnership->pendingLock())).finish();
        });
    }
    bool empty(){return endpoint_.readers()==0 && endpoint_.native([](auto& broker){return broker.recordCount()==0 && broker.charge()==0;});}
};
}

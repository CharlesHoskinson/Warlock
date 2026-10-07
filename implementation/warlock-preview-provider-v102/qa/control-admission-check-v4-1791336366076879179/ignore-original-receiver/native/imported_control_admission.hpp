#pragma once
#include "control_reservations.hpp"
#include "imported_enrollment.hpp"

namespace preview::bridge {
// Transport reservations around the original native issuer, not a scheduler or
// second UI policy. All calls share Endpoint's native receiver/Broker lock.
class ImportedControlAdmission {
    struct JobRow {uint64_t reservation;std::optional<Job> job;};
    struct ConfirmedJob {Job job;std::vector<ControlReservations::Ticket> tickets;};
    struct ActorRow {uint64_t reservation;Id<Incarnation> subject;bool retired{},finalAcknowledged{};};
    ControlReservations& controls_;
    const Broker* broker_;
    const PreviewControlGrant grant_;
    const Binding owner_;
    const size_t actorLimit_,jobLimit_;
    uint64_t reconciliation_{};
    std::map<uint64_t,ActorRow> actors_;
    std::map<uint64_t,JobRow> jobs_;
    // At most one confirmed predecessor per retained native actor, never an
    // unbounded lifetime cache. It can suppress an exact stale proposal only;
    // the released original ticket is no longer owned by the invoking bank.
    std::map<uint64_t,ConfirmedJob> confirmed_;
    bool bindingClosed_{};
    void receiver(PreviewControlGrant actual,const uri::View* view)const {
        require(actual.receiver>0 && importedReceiver(view,owner_,grant_.epoch),
            "Original native admission receiver before reservation or issuance");
    }
    bool prepare(uint64_t entry,Id<Incarnation> subject) {
        require(entry && subject.value && !bindingClosed_,"Open original native admission and subject serial");
        const auto retained=actors_.find(entry);
        require(retained==actors_.end() || (retained->second.subject==subject && !retained->second.retired),
            "Original active native control actor before admission");
        // A retained unknown issuance cannot be tried again as a fresh job.
        if(jobs_.contains(entry) || jobs_.size()>=jobLimit_)return false;
        const bool fresh=!actors_.contains(entry);
        if(fresh && actors_.size()>=actorLimit_)return false;
        std::optional<uint64_t> actor;
        if(fresh){actor=controls_.reserve(grant_,actorQuota);if(!actor)return false;}
        std::optional<uint64_t> job;
        try {
            job=controls_.reserve(grant_,jobQuota);
            if(!job){if(actor)require(controls_.release(grant_,*actor),"Unused actor quota rollback");return false;}
            if(actor)actors_.emplace(entry,ActorRow{*actor,subject});
            try {jobs_.emplace(entry,JobRow{*job,{}});}
            catch(...){if(actor)actors_.erase(entry);throw;}
        }catch(...) {
            if(job)controls_.release(grant_,*job);
            if(actor)controls_.release(grant_,*actor);
            throw;
        }
        return true;
    }
public:
    struct Proposal {ControlReservations::Ticket ticket;bool alreadyDelivered;};
    // One imported packet, one acquire/cancel/release and at most two native
    // terminal proofs. Repeated exact commands must reuse their native slots.
    static constexpr uint64_t jobQuota=5,actorQuota=2,reconciliationQuota=1;
    ImportedControlAdmission(ControlReservations& controls,PreviewControlGrant grant,
            const Broker& broker,size_t subjects):controls_(controls),broker_(&broker),grant_(grant),
        owner_{{grant.lifetime},{grant.session},{grant.frontend}},actorLimit_(2*subjects),jobLimit_(broker.limits().records) {
        require(subjects && subjects<=256 && broker.limits().entries==subjects &&
            jobLimit_ && jobLimit_<=8 && broker.inspect().empty(),"Fresh owning imported Broker and bounded control cohorts");
        controls_.claimAdmission(grant_);
        auto reservation=controls_.reserve(grant_,reconciliationQuota);
        require(reservation.has_value(),"Binding reconciliation reserved before native admission");
        reconciliation_=*reservation;
    }
    ImportedControlAdmission(const ImportedControlAdmission&)=delete;
    ImportedControlAdmission& operator=(const ImportedControlAdmission&)=delete;
    size_t actorCount()const noexcept{return actors_.size();}
    size_t jobCount()const noexcept{return jobs_.size();}
    uint64_t reconciliationReservation()const noexcept{return reconciliation_;}
    uint64_t actorReservation(uint64_t entry)const{return actors_.at(entry).reservation;}
    uint64_t jobReservation(uint64_t entry)const{return jobs_.at(entry).reservation;}
    bool containsJob(uint64_t entry)const noexcept{return jobs_.contains(entry);}
    std::optional<Job> retainedJob(uint64_t entry)const{return jobs_.at(entry).job;}
    bool ownsBroker(const Broker& broker,PreviewControlGrant actual)const noexcept {
        return broker_==&broker && actual.receiver>0;
    }
    bool containsActor(uint64_t entry)const noexcept{return actors_.contains(entry);}
    Id<Incarnation> actorSubject(uint64_t entry)const{return actors_.at(entry).subject;}
    bool actorRetired(uint64_t entry)const{return actors_.at(entry).retired;}
    std::optional<Proposal> retryActorControl(PreviewControlGrant actual,const uri::View* view,
            const Broker& broker,uint64_t entry,Id<Incarnation> subject,std::string_view body)const {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        const auto found=actors_.find(entry);
        require(found!=actors_.end() && found->second.subject==subject,"Original retained native control actor");
        auto ticket=controls_.retry(grant_,found->second.reservation,body);
        return ticket?std::optional<Proposal>{Proposal{std::move(*ticket),false}}:std::nullopt;
    }
    std::optional<Proposal> issueActorControl(PreviewControlGrant actual,const uri::View* view,
            const Broker& broker,uint64_t entry,Id<Incarnation> subject,uint64_t slot,std::string_view body) {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        const auto found=actors_.find(entry);
        require(found!=actors_.end() && found->second.subject==subject && !bindingClosed_ &&
            ((slot==1 && !found->second.retired) || (slot==2 && found->second.retired)),
            "Native readiness or completed original actor purpose");
        auto ticket=controls_.issue(grant_,found->second.reservation,slot,body);
        return ticket?std::optional<Proposal>{Proposal{std::move(*ticket),false}}:std::nullopt;
    }
    bool canCommitActorRetirement(PreviewControlGrant actual,const uri::View* view,
            const Broker& broker,uint64_t entry,Id<Incarnation> subject)const {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        const auto found=actors_.find(entry);
        return found!=actors_.end() && found->second.subject==subject && !found->second.retired &&
            !jobs_.contains(entry);
    }
    // The owning all-map retirement transaction validated this exact row and
    // all original physical/proof/fresh-native-fact barriers before commit.
    void commitActorRetirement(uint64_t entry)noexcept {actors_.find(entry)->second.retired=true;}
    bool canAcknowledgeActor(uint64_t entry,Id<Incarnation> subject)const noexcept {
        const auto found=actors_.find(entry);return found!=actors_.end() &&
            found->second.subject==subject && found->second.retired;
    }
    bool actorDispatched(PreviewControlGrant actual,const uri::View* view,const Broker& broker,
            uint64_t entry,uint64_t slot,std::string_view body,bool invokingOnly=false)const {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        const auto found=actors_.find(entry);return found!=actors_.end() &&
            controls_.dispatched(grant_,found->second.reservation,slot,body,invokingOnly);
    }
    void commitActorAcknowledgment(uint64_t entry)noexcept {actors_.find(entry)->second.finalAcknowledged=true;}
    size_t collectConfirmedActors(PreviewControlGrant actual,const uri::View* view,const Broker& broker) {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        size_t removed=0;
        for(auto row=actors_.begin();row!=actors_.end();) {
            if(row->second.retired && row->second.finalAcknowledged &&
                controls_.release(grant_,row->second.reservation)) {
                confirmed_.erase(row->first);row=actors_.erase(row);++removed;
            }else ++row;
        }
        return removed;
    }
    bool releaseBinding(PreviewControlGrant actual,const uri::View* view,const Broker& broker) {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        if(bindingClosed_)return true;
        if(!actors_.empty() || !jobs_.empty() || !confirmed_.empty() || broker.actorCount() ||
            broker.recordCount() || broker.charge())return false;
        if(!controls_.release(grant_,reconciliation_))return false;
        bindingClosed_=true;return true;
    }
    size_t confirmedJobCount()const noexcept{return confirmed_.size();}
    std::optional<Proposal> retryJobControl(PreviewControlGrant actual,const uri::View* view,
            const Broker& broker,uint64_t entry,const Job& job,std::string_view body)const {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        const auto active=jobs_.find(entry);
        if(active!=jobs_.end() && active->second.job==std::optional<Job>{job}) {
            if(auto retry=controls_.retry(grant_,active->second.reservation,body))
                return Proposal{std::move(*retry),false};
        }
        const auto previous=confirmed_.find(entry);
        if(previous!=confirmed_.end() && previous->second.job==job) {
            for(const auto& ticket:previous->second.tickets)
                if(controls_.exactBody(grant_,ticket,body))return Proposal{ticket,true};
        }
        return {};
    }
    // Called only after the owning ImportedClients has validated the actual
    // native job/packet/proof and chosen its stable purpose slot under its lock.
    std::optional<Proposal> issueJobControl(PreviewControlGrant actual,const uri::View* view,
            const Broker& broker,uint64_t entry,const Job& job,uint64_t slot,std::string_view body) {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        const auto found=jobs_.find(entry);
        require(found!=jobs_.end() && found->second.job==std::optional<Job>{job} &&
            broker.owningEntry(job)==std::optional<uint64_t>{entry},"Actual retained original job before typed ticket");
        auto ticket=controls_.issue(grant_,found->second.reservation,slot,body);
        return ticket?std::optional<Proposal>{Proposal{std::move(*ticket),false}}:std::nullopt;
    }
    // The owning ImportedClients caller first verifies its original mapping,
    // export and backend retirement barriers. Record absence and transport
    // confirmation here are additional checks, never substitutes for them.
    bool releaseRetiredJob(PreviewControlGrant actual,const uri::View* view,
            const Broker& broker,uint64_t entry,const Job& expected) {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        const auto found=jobs_.find(entry);
        require(found!=jobs_.end() && found->second.job==std::optional<Job>{expected},
            "Known original issued control job before release");
        const auto records=broker.inspect();
        if(std::any_of(records.begin(),records.end(),[&](const auto& row){return row.entry==entry;}))return false;
        auto tickets=controls_.confirmedTickets(grant_,found->second.reservation);if(!tickets)return false;
        // Allocate the bounded predecessor before releasing any credits. No
        // failure can forget an exact accepted retry while advancing admission.
        ConfirmedJob previous{expected,std::move(*tickets)};
        confirmed_.insert_or_assign(entry,std::move(previous));
        require(controls_.release(grant_,found->second.reservation),"Serialized confirmed original quota release");
        jobs_.erase(found);return true;
    }
    // The native callback invokes only the original owning Coordinator/Broker.
    // Any exception retains the pending reservation. A missing returned job
    // must additionally agree with actual native record absence before rollback.
    template<class F> ImportedStartAttempt admit(PreviewControlGrant actual,const uri::View* view,
            Broker& broker,uint64_t entry,const Scope& scope,F&& issue) {
        receiver(actual,view);require(ownsBroker(broker,actual),"Original owning control Broker");
        require(scope.binding==owner_,"Original native observed binding");
        if(!prepare(entry,scope.context.incarnation))return {ImportedIntentLedger::Admission::Capacity,{},"[]"};
        auto result=std::invoke(std::forward<F>(issue));
        if(result.native.job) {
            const auto& job=*result.native.job;
            require(job.binding==owner_ && job.context.incarnation==scope.context.incarnation &&
                broker.owningEntry(job)==std::optional<uint64_t>{entry},"Actual own issued native job before publishing controls");
            jobs_.at(entry).job=job;
        }else {
            const auto records=broker.inspect();
            require(std::none_of(records.begin(),records.end(),[&](const auto& row){return row.entry==entry;}),
                "Missing returned job is not proof of absent native issuance");
            require(controls_.release(grant_,jobs_.at(entry).reservation),"Unused job cleanup quota rollback");
            jobs_.erase(entry);
        }
        return result;
    }
    ImportedStartAttempt reserveIntent(demand::Coordinator& queue,ImportedIntentLedger& ledger,
            PreviewControlGrant actual,uri::View* view,uint64_t entry,const Scope& scope,uint64_t cost,
            uint64_t publication,uint64_t lease,uint64_t deadline) {
        return admit(actual,view,queue.nativeBroker(),entry,scope,[&]{
            return reserveImportedIntent(queue,ledger,entry,scope,cost,publication,lease,deadline,view);
        });
    }
};
}

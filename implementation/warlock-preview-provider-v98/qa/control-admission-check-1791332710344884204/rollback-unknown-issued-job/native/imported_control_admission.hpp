#pragma once
#include "control_reservations.hpp"
#include "imported_enrollment.hpp"

namespace preview::bridge {
// Transport reservations around the original native issuer, not a scheduler or
// second UI policy. All calls share Endpoint's native receiver/Broker lock.
class ImportedControlAdmission {
    struct JobRow {uint64_t reservation;std::optional<Job> job;};
    ControlReservations& controls_;
    const PreviewControlGrant grant_;
    const Binding owner_;
    const size_t actorLimit_,jobLimit_;
    uint64_t reconciliation_{};
    std::map<uint64_t,uint64_t> actors_;
    std::map<uint64_t,JobRow> jobs_;
    void receiver(PreviewControlGrant actual,const uri::View* view)const {
        require(preview_control_grant_equal(grant_,actual) && importedReceiver(view,owner_,grant_.epoch),
            "Original native admission receiver before reservation or issuance");
    }
    bool prepare(uint64_t entry) {
        require(entry,"Original positive native admission serial");
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
            if(actor)actors_.emplace(entry,*actor);
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
    // One imported packet, one acquire/cancel/release and at most two native
    // terminal proofs. Repeated exact commands must reuse their native slots.
    static constexpr uint64_t jobQuota=5,actorQuota=2,reconciliationQuota=1;
    ImportedControlAdmission(ControlReservations& controls,PreviewControlGrant grant,
            const Broker& broker,size_t subjects):controls_(controls),grant_(grant),
        owner_{{grant.lifetime},{grant.session},{grant.frontend}},actorLimit_(2*subjects),jobLimit_(broker.limits().records) {
        require(subjects && subjects<=256 && broker.limits().entries==subjects &&
            jobLimit_ && jobLimit_<=8 && broker.inspect().empty(),"Fresh owning imported Broker and bounded control cohorts");
        auto reservation=controls_.reserve(grant_,reconciliationQuota);
        require(reservation.has_value(),"Binding reconciliation reserved before native admission");
        reconciliation_=*reservation;
    }
    ImportedControlAdmission(const ImportedControlAdmission&)=delete;
    ImportedControlAdmission& operator=(const ImportedControlAdmission&)=delete;
    size_t actorCount()const noexcept{return actors_.size();}
    size_t jobCount()const noexcept{return jobs_.size();}
    uint64_t reconciliationReservation()const noexcept{return reconciliation_;}
    uint64_t actorReservation(uint64_t entry)const{return actors_.at(entry);}
    uint64_t jobReservation(uint64_t entry)const{return jobs_.at(entry).reservation;}
    std::optional<Job> retainedJob(uint64_t entry)const{return jobs_.at(entry).job;}
    // The native callback invokes only the original owning Coordinator/Broker.
    // Any exception retains the pending reservation. A missing returned job
    // must additionally agree with actual native record absence before rollback.
    template<class F> ImportedStartAttempt admit(PreviewControlGrant actual,const uri::View* view,
            Broker& broker,uint64_t entry,const Scope& scope,F&& issue) {
        receiver(actual,view);require(scope.binding==owner_,"Original native observed binding");
        if(!prepare(entry))return {ImportedIntentLedger::Admission::Capacity,{},"[]"};
        auto result=[&]{try{return std::invoke(std::forward<F>(issue));}catch(...){controls_.release(grant_,jobs_.at(entry).reservation);jobs_.erase(entry);throw;}}();
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

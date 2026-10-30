#pragma once
// Bounded decision owner. Component checks do not establish native acceptance.
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>

namespace warlock::cancellation {
using U = std::uint64_t;
struct OwnerId {
    U peer{}, start{}, lifetime{}, session{}, frontend{};
    bool operator==(const OwnerId&) const = default;
};
struct Intent {
    U request{}, generation{}, incarnation{}, lifetime{}, epoch{}, output{}, revision{};
    // Stage 1 accepts only restore; it is represented explicitly in the key.
    enum class Operation { Restore } operation{Operation::Restore};
    bool operator==(const Intent&) const = default;
};
struct Key {
    OwnerId owner{}; U effectProtocol{1}; Intent intent{};
    bool operator==(const Key&) const = default;
};
enum class Phase { Prepared, Committing, Committed, Refused, Cancelled, ExecutionUnknown };
enum class Error { None, Invalid, Expired, Busy, Capacity, Exhausted, Foreign, Unacknowledgeable, Resource };
enum class Progress { NoNativeMutation, NativeMutationStarted };
enum class Decision { RefusedBeforeMutation, RefusedAfterProvedCompensation, CommittedObserved, ExecutionUncertain };
// Reasons are bounded stable native vocabulary, never externally supplied strings.
enum class Reason { Cancelled, Deadline, Unproven, Applied, NativeRefusal };
struct Facts { U revision{}, outputGeneration{}; Reason reason{Reason::Unproven}; const char* detail{}; };
struct ExecutionResult { Decision decision; Progress progress; Facts facts; };
struct Buffer { std::array<char,4096> data{}; std::size_t size{}; };
struct Record { Key key{}; U deadline{}, id{}; Phase phase{Phase::Prepared}; Buffer reply{}; bool token{}; Facts facts{}; bool replyReady{}; Phase proofPhase{Phase::ExecutionUnknown}; Facts proofFacts{}; bool hasProof{}; };
struct Result { Error error{Error::None}; const Record* record{}; };
// The formatter has no allocation and either publishes complete bytes or fails.
using Format = bool (*)(Buffer&, const Key&, U id, U deadline, Phase, Facts) noexcept;
using Retire = void (*)(void*, const Key&) noexcept;
class Owner {
public:
    class CommitPermit {
        friend class Owner;
        explicit CommitPermit(const Key& k) noexcept : key_(&k) {}
        const Key* key_;
    public:
        CommitPermit(const CommitPermit&)=delete;
        CommitPermit& operator=(const CommitPermit&)=delete;
        bool matches(const Key& k) const noexcept { return *key_==k; }
    };
    // Adapter must call the shared real executor, not decode a wire status.
    using Execute = ExecutionResult (*)(void*, const CommitPermit&) noexcept;
    Owner(Format f, Retire r, void* context) noexcept : format_(f), retire_(r), context_(context) {}
    bool busy(const OwnerId& o) const noexcept { return owner(o)!=nullptr; }
    Result prepare(const Key& k, U deadline, U now, U watermark, U generation) noexcept {
        if (!valid(k) || !deadline || !now) return fail(Error::Invalid);
        if (auto* s=owner(k.owner)) return s->key==k && s->deadline==deadline ? ok(*s) : fail(Error::Busy);
        if(k.intent.request<=watermark || k.intent.generation<=generation || now>=deadline) return fail(Error::Expired);
        if(next_==std::numeric_limits<U>::max()) return fail(Error::Exhausted);
        auto* s=free(); if(!s)return fail(Error::Capacity);
        Record candidate{}; candidate.key=k; candidate.deadline=deadline; candidate.id=next_+1;
        candidate.token=true;
        if(!format_ || !format_(candidate.reply,k,candidate.id,deadline,Phase::Prepared,{})) return fail(Error::Resource);
        if(!candidate.reply.size || candidate.reply.size>candidate.reply.data.size()) return fail(Error::Resource);
        candidate.replyReady=true;
        *s=candidate; occupied_[index(s)]=true; ++next_; return ok(*s);
    }
    Result lookup(const Key& k,U id,U deadline) noexcept { auto* s=find(k,id,deadline);return s?publish(*s):fail(Error::Foreign); }
    Result cancel(const Key& k,U id,U deadline,Facts facts) noexcept {
        auto* s=find(k,id,deadline);if(!s)return fail(Error::Foreign);
        if(s->phase!=Phase::Prepared)return publish(*s);
        // Semantic cancellation fences execution before encoding or delivery.
        facts.reason=Reason::Cancelled; facts.detail=nullptr;
        s->facts=facts;s->phase=Phase::Cancelled;s->replyReady=false;s->reply.size=0;
        retire(*s);return publish(*s);
    }
    Result commit(const Key& k,U id,U deadline,U now,Facts current,Execute execute,void* context) noexcept {
        auto* s=find(k,id,deadline);if(!s)return fail(Error::Foreign);
        if(s->phase!=Phase::Prepared)return publish(*s);
        if(!now || !execute)return fail(Error::Invalid);
        if(now>=deadline) {
            current.reason=Reason::Deadline;current.detail=nullptr;
            s->facts=current;s->phase=Phase::Refused;s->replyReady=false;s->reply.size=0;
            retire(*s);return publish(*s);
        }
        current.reason=Reason::Unproven;current.detail=nullptr; Buffer fallback{};
        if(!format_ || !format_(fallback,k,id,deadline,Phase::ExecutionUnknown,current))return fail(Error::Resource);
        if(!fallback.size || fallback.size>fallback.data.size())return fail(Error::Resource);
        s->reply=fallback;s->replyReady=true;s->facts=current;s->phase=Phase::Committing;
        // No event loop or async continuation is permitted through execute.
        CommitPermit permit(s->key); s->phase=Phase::ExecutionUnknown;
        const auto x=execute(context,permit);
        Phase phase=Phase::ExecutionUnknown;
        if(x.decision==Decision::RefusedBeforeMutation && x.progress==Progress::NoNativeMutation)phase=Phase::Refused;
        else if(x.decision==Decision::RefusedAfterProvedCompensation && x.progress==Progress::NativeMutationStarted)phase=Phase::Refused;
        else if(x.decision==Decision::CommittedObserved && x.progress==Progress::NativeMutationStarted)phase=Phase::Committed;
        if(phase==Phase::ExecutionUnknown)return ok(*s);
        // Retain typed proof separately from the last complete wire decision.
        // Until terminal encoding succeeds, the preinstalled Unknown remains
        // queryable and no execution or acknowledgement can reopen the slot.
        s->proofFacts=x.facts;s->proofPhase=phase;s->hasProof=true;
        retire(*s);return publish(*s);
    }
    // Caller retains the exact record in its per-session journal before freeing.
    Result acknowledge(const Key& k,U id,U deadline,Record& retained) noexcept {
        auto* s=find(k,id,deadline);if(!s)return fail(Error::Foreign);
        if(!s->replyReady || (s->phase!=Phase::Committed && s->phase!=Phase::Refused && s->phase!=Phase::Cancelled))return fail(Error::Unacknowledgeable);
        retained=*s;occupied_[index(s)]=false;return {Error::None,&retained};
    }
    void retireOwner(const OwnerId& o) noexcept {
        auto* s=owner(o);if(s && s->phase==Phase::Prepared){retire(*s);occupied_[index(s)]=false;}
    }
private:
    std::array<Record,64> records_{}; std::array<bool,64> occupied_{}; U next_{};
    Format format_; Retire retire_; void* context_;
    static bool valid(const Key& k) noexcept {const auto& o=k.owner;const auto& i=k.intent;return o.peer && o.start && o.lifetime && o.session && o.frontend && k.effectProtocol==1 && i.request && i.generation && i.incarnation && i.lifetime==o.lifetime && i.epoch==o.frontend && i.output && i.revision && i.operation==Intent::Operation::Restore;}
    std::size_t index(const Record* r) const noexcept {return static_cast<std::size_t>(r-records_.data());}
    Record* free() noexcept {for(std::size_t n=0;n<64;++n)if(!occupied_[n])return &records_[n];return nullptr;}
    const Record* owner(const OwnerId& o) const noexcept {for(std::size_t n=0;n<64;++n)if(occupied_[n] && records_[n].key.owner==o)return &records_[n];return nullptr;}
    Record* owner(const OwnerId& o) noexcept {return const_cast<Record*>(static_cast<const Owner*>(this)->owner(o));}
    Record* find(const Key& k,U id,U d) noexcept {auto* s=owner(k.owner);return s && s->key==k && s->id==id && s->deadline==d?s:nullptr;}
    Result publish(Record& s) noexcept {
        if(s.hasProof) {
            Buffer terminal{};
            if(!format_ || !format_(terminal,s.key,s.id,s.deadline,s.proofPhase,s.proofFacts) || !terminal.size || terminal.size>terminal.data.size())
                return s.replyReady ? ok(s) : Result{Error::Resource,&s};
            // Publish the complete terminal atomically, without allocation.
            s.reply=terminal;s.facts=s.proofFacts;s.phase=s.proofPhase;
            s.replyReady=true;s.hasProof=false;
        }
        if(s.replyReady)return ok(s);
        Buffer b{};
        if(!format_ || !format_(b,s.key,s.id,s.deadline,s.phase,s.facts) || !b.size || b.size>b.data.size())return {Error::Resource,&s};
        s.reply=b;s.replyReady=true;return ok(s);
    }
    void retire(Record& s) noexcept {if(s.token){s.token=false;if(retire_)retire_(context_,s.key);}}
    static Result fail(Error e) noexcept {return {e,nullptr};}
    static Result ok(const Record& s) noexcept {return {Error::None,&s};}
};
}

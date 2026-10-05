#pragma once
#include <array>
#include <compare>
#include <cstdint>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <stdexcept>
#include <vector>
#include <cerrno>
#include <sys/random.h>

namespace preview {
template<class Domain> struct Id {
    uint64_t value{};
    auto operator<=>(const Id&) const = default;
};
struct Lifetime; struct Session; struct Frontend; struct Incarnation;
struct Output; struct Privacy; struct Rendering; struct Scene; struct Content;
struct Request; struct Origin; struct Clock; struct ReceiptSequence;
struct Binding {
    Id<Lifetime> lifetime; Id<Session> session; Id<Frontend> frontend;
    auto operator<=>(const Binding&) const = default;
};
struct Context {
    Id<Lifetime> lifetime; Id<Incarnation> incarnation; Id<Output> output;
    Id<Privacy> privacy; Id<Rendering> rendering; Id<Scene> scene; Id<Content> content;
    auto operator<=>(const Context&) const = default;
};
struct Job {
    Binding binding; Context context; Id<Request> request; Id<Origin> origin;
    Id<Clock> clock; uint64_t deadline{};
    auto operator<=>(const Job&) const = default;
};
struct Scope {
    Binding binding; Context context; Id<Clock> clock; uint64_t now{};
    bool present{true}, sourceLive{true}, locked{false}, gpuReady{true};
};
struct Token {
    std::array<uint8_t,16> brokerNonce{}; uint64_t sequence{};
    auto operator<=>(const Token&) const = default;
};
struct Packet {
    Job job; Token token; bool signaled{};
    enum class Fidelity { Client, Family } fidelity{Fidelity::Client};
    uint8_t coverage{1}; uint64_t expires{};
};
struct Buffer {
    virtual ~Buffer() = default;
    virtual uint64_t charge() const noexcept = 0;
};
struct Limits { size_t entries, records, items; uint64_t bytes; };
struct Receipt {
    enum class Kind { Offer, Fence, Refused, Cancelled, Released } kind;
    uint64_t entry; Job job; std::optional<Packet> packet;
    Id<ReceiptSequence> sequence;
};
struct Result {
    enum class Status { Admitted, Refused, Duplicate, Ignored, Backpressure, Complete, Exhausted } status{Status::Ignored};
    std::vector<Receipt> receipts;
};
class Broker {
    struct Actor { Scope scope; uint64_t cost, floor{}; bool coherent{true}; };
    struct Record {
        uint64_t entry; Job job; uint64_t bytes{};
        std::shared_ptr<const Buffer> buffer{};
        std::optional<Packet> packet{};
        bool cleanup{}, producerDone{}, consumerDone{true}, cancelled{}, terminal{};
        std::vector<Receipt> proof{};
    };
    Limits limits_;
    std::array<uint8_t,16> nonce_{};
    std::map<uint64_t,Actor> actors_;
    std::map<Job,Record> records_;
    uint64_t nextToken_{1}, nextReceipt_{1};
    bool tokenExhausted_{}, receiptExhausted_{};
    static bool positive(const Binding& b) { return b.lifetime.value && b.session.value && b.frontend.value; }
    static bool positive(const Context& c) { return c.lifetime.value && c.incarnation.value && c.output.value && c.privacy.value && c.rendering.value && c.scene.value && c.content.value; }
    static bool valid(const Scope& s) { return positive(s.binding) && positive(s.context) && s.binding.lifetime==s.context.lifetime && s.clock.value && s.now; }
    static bool valid(const Job& j) { return positive(j.binding) && positive(j.context) && j.binding.lifetime==j.context.lifetime && j.request.value && j.origin.value && j.clock.value && j.deadline; }
    static bool generations(const Context& a,const Context& b) { return a.lifetime==b.lifetime && a.incarnation==b.incarnation && a.output==b.output && a.privacy==b.privacy && a.rendering==b.rendering; }
    Actor* actor(uint64_t entry,const Binding& authenticated) {
        auto it=actors_.find(entry);
        return it!=actors_.end() && it->second.scope.binding==authenticated ? &it->second : nullptr;
    }
    Record* record(uint64_t entry,const Job& job) {
        auto it=records_.find(job);
        return it!=records_.end() && it->second.entry==entry ? &it->second : nullptr;
    }
    std::optional<Receipt> receipt(Receipt::Kind kind,const Record& r) {
        if(receiptExhausted_) return {};
        Receipt result{kind,r.entry,r.job,r.packet,{nextReceipt_}};
        if(nextReceipt_==std::numeric_limits<uint64_t>::max()) receiptExhausted_=true;
        else ++nextReceipt_;
        return result;
    }
    Result replay(const Record& r) const { return {Result::Status::Duplicate,r.terminal ? r.proof : std::vector<Receipt>{}}; }
    static void cleanup(Record& r) { r.cleanup=true; }
    size_t items() const {
        size_t count=0; for(const auto& [j,r]:records_) if(!r.terminal && r.bytes) ++count;
        return count;
    }
    bool eligible(const Actor& a,const Job& j) const {
        return a.coherent && j.binding==a.scope.binding && j.context==a.scope.context && j.clock==a.scope.clock && j.deadline>a.scope.now && a.scope.present && a.scope.sourceLive && !a.scope.locked && a.scope.gpuReady;
    }
public:
    explicit Broker(Limits limits):limits_(limits) {
        if(!limits.entries || !limits.records || !limits.items || !limits.bytes) throw std::invalid_argument("Positive broker limits");
        size_t offset=0;
        while(offset<nonce_.size()) {
            ssize_t got=::getrandom(nonce_.data()+offset,nonce_.size()-offset,0);
            if(got<0 && errno==EINTR) continue;
            if(got<=0) throw std::runtime_error("Native broker nonce unavailable");
            offset+=static_cast<size_t>(got);
        }
    }
    // This API is called only with a native-enrolled subject, never wire JSON.
    // The transport adapter must retain every returned control receipt until Ack.
    bool enroll(uint64_t entry,const Scope& s,uint64_t cost,std::vector<Packet>* expired=nullptr) {
        if(!entry || !valid(s) || !cost || cost>limits_.bytes) return false;
        for(const auto& [other,a]:actors_) if(other!=entry && a.scope.binding==s.binding && a.scope.context==s.context) return false;
        auto old=actors_.find(entry);
        if(old==actors_.end()) {
            if(actors_.size()>=limits_.entries) return false;
            actors_.emplace(entry,Actor{s,cost}); return true;
        }
        if(old->second.scope.binding==s.binding) return observe(entry,s,cost,expired);
        for(auto& [j,r]:records_) if(r.entry==entry && !r.terminal) { cleanup(r); if(!r.packet) r.cancelled=true; else if(expired) expired->push_back(*r.packet); }
        old->second={s,cost,0,true}; return true;
    }
    bool observe(uint64_t entry,const Scope& incoming,uint64_t cost,std::vector<Packet>* expired=nullptr) {
        auto it=actors_.find(entry);
        if(it==actors_.end() || !valid(incoming) || !cost || cost>limits_.bytes || incoming.binding!=it->second.scope.binding) return false;
        for(const auto& [other,a]:actors_) if(other!=entry && a.scope.binding==incoming.binding && a.scope.context==incoming.context) return false;
        auto& a=it->second; const Scope& old=a.scope;
        bool coherent=incoming.clock==old.clock && incoming.now>=old.now && incoming.context.output>=old.context.output && incoming.context.privacy>=old.context.privacy && incoming.context.rendering>=old.context.rendering && (incoming.context.incarnation!=old.context.incarnation || (incoming.context.scene>=old.context.scene && incoming.context.content>=old.context.content && (incoming.sourceLive==old.sourceLive || incoming.context.scene>old.context.scene)));
        if(!coherent) {
            a.coherent=false;
            for(auto& [j,r]:records_) if(r.entry==entry && !r.terminal) { cleanup(r); if(!r.packet) r.cancelled=true; else if(expired) expired->push_back(*r.packet); }
            return false;
        }
        a.scope=incoming; a.cost=cost;
        for(auto& [j,r]:records_) {
            if(r.entry!=entry || r.terminal) continue;
            if(!generations(j.context,incoming.context) || !incoming.present || incoming.locked || !incoming.gpuReady || (!r.packet && (!incoming.sourceLive || j.deadline<=incoming.now)) || (r.packet && ((!r.producerDone && j.deadline<=incoming.now) || r.packet->expires<=incoming.now))) { cleanup(r); if(!r.packet) r.cancelled=true; else if(expired) expired->push_back(*r.packet); }
        }
        return true;
    }
    Result acquire(uint64_t entry,const Binding& authenticated,const Job& job) {
        Actor* a=actor(entry,authenticated);
        if(!a || !valid(job) || job.binding!=authenticated) return {};
        if(Record* r=record(entry,job)) return replay(*r);
        if(records_.contains(job)) return {};
        if(job.request.value<=a->floor) return {};
        if(receiptExhausted_) return {Result::Status::Exhausted,{}};
        if(records_.size()>=limits_.records) return {Result::Status::Backpressure,{}};
        const bool admit=eligible(*a,job) && items()<limits_.items && a->cost<=limits_.bytes-charge();
        a->floor=job.request.value;
        Record r{entry,job};
        if(admit) { r.bytes=a->cost; records_.emplace(job,std::move(r)); return {Result::Status::Admitted,{}}; }
        r.terminal=true;
        auto proof=receipt(Receipt::Kind::Refused,r);
        if(proof) r.proof.push_back(*proof);
        auto output=r.proof; records_.emplace(job,std::move(r));
        return {Result::Status::Refused,std::move(output)};
    }
    Result cancel(uint64_t entry,const Binding& authenticated,const Job& job) {
        Actor* a=actor(entry,authenticated);
        Record* r=record(entry,job);
        if(!valid(job) || (!a && (!r || r->job.binding!=authenticated))) return {};
        if(r) {
            if(r->terminal) {
                for(const auto& proof:r->proof) if(proof.kind==Receipt::Kind::Cancelled) return {Result::Status::Complete,{proof}};
                if(receiptExhausted_) return {Result::Status::Exhausted,{}};
                r->cancelled=true;
                auto proof=receipt(Receipt::Kind::Cancelled,*r);
                if(proof) { r->proof.push_back(*proof); return {Result::Status::Complete,{*proof}}; }
                return {Result::Status::Exhausted,{}};
            }
            r->cancelled=true; cleanup(*r); return {};
        }
        if(job.binding!=authenticated || job.request.value<=a->floor) return {};
        if(receiptExhausted_) return {Result::Status::Exhausted,{}};
        if(records_.size()>=limits_.records) return {Result::Status::Backpressure,{}};
        a->floor=job.request.value;
        Record closed{entry,job}; closed.cancelled=true; closed.terminal=true;
        auto proof=receipt(Receipt::Kind::Cancelled,closed);
        if(proof) closed.proof.push_back(*proof);
        auto output=closed.proof; records_.emplace(job,std::move(closed));
        return {Result::Status::Complete,std::move(output)};
    }
    Result release(uint64_t entry,const Binding& authenticated,const Job& job,const Token& token) {
        Record* r=record(entry,job);
        if(!actor(entry,authenticated) && (!r || r->job.binding!=authenticated)) return {};
        if(!r || !r->packet || r->packet->token!=token) return {};
        if(r->terminal) return replay(*r);
        cleanup(*r); return {};
    }
    Result allocate(uint64_t entry,const Job& job,std::unique_ptr<const Buffer>& buffer,uint64_t expires,Packet::Fidelity fidelity=Packet::Fidelity::Client,uint8_t coverage=1) {
        Record* r=record(entry,job); auto a=actors_.find(entry);
        if(!r || !buffer || r->terminal || r->cleanup || r->packet || a==actors_.end() || !eligible(a->second,job) || expires<=a->second.scope.now || !buffer->charge() || buffer->charge()>r->bytes || !(coverage&1) || (coverage&~15) || (fidelity==Packet::Fidelity::Family && coverage!=15)) return {};
        if(tokenExhausted_ || receiptExhausted_) return {Result::Status::Exhausted,{}};
        Packet packet{job,{nonce_,nextToken_},false,fidelity,coverage,expires};
        if(nextToken_==std::numeric_limits<uint64_t>::max()) tokenExhausted_=true; else ++nextToken_;
        r->buffer=std::move(buffer); r->packet=packet; r->consumerDone=false;
        auto offer=receipt(Receipt::Kind::Offer,*r);
        return {Result::Status::Admitted,offer ? std::vector<Receipt>{*offer} : std::vector<Receipt>{}};
    }
    // Trusted producer completion: capture refused after reservation but before
    // any buffer was adopted. Never turn an owned packet into a refusal proof.
    // Stable terminal receipts follow reservation retirement, with cancellation
    // proof preserved when cancellation raced the actual producer completion.
    Result producerRefused(uint64_t entry,const Job& job) {
        Record* r=record(entry,job);
        if(!r) return {};
        if(r->terminal) return replay(*r);
        if(r->packet || r->buffer) return {};
        const unsigned needed=1+static_cast<unsigned>(r->cancelled);
        if(receiptExhausted_ || needed>std::numeric_limits<uint64_t>::max()-nextReceipt_+1) return {Result::Status::Exhausted,{}};
        r->cleanup=true; r->producerDone=true; r->consumerDone=true;
        r->bytes=0; r->terminal=true;
        auto refused=receipt(Receipt::Kind::Refused,*r); if(refused) r->proof.push_back(*refused);
        if(r->cancelled) {auto cancelled=receipt(Receipt::Kind::Cancelled,*r); if(cancelled) r->proof.push_back(*cancelled);}
        return {Result::Status::Complete,r->proof};
    }
    // Only the native allocator/fence driver calls these methods; frontend flags
    // and URI-load callbacks cannot establish producer or consumer completion.
    Result producerComplete(uint64_t entry,const Job& job) {
        Record* r=record(entry,job);
        if(!r || r->terminal || (!r->packet && !r->cleanup)) return {};
        r->producerDone=true;
        if(!r->packet) return {};
        r->packet->signaled=true;
        if(r->cleanup) return {};
        auto fence=receipt(Receipt::Kind::Fence,*r);
        return {Result::Status::Complete,fence ? std::vector<Receipt>{*fence} : std::vector<Receipt>{}};
    }
    bool consumerComplete(uint64_t entry,const Job& job) {
        Record* r=record(entry,job);
        if(!r || r->terminal || !r->cleanup || (r->buffer && r->buffer.use_count()!=1)) return false;
        r->consumerDone=true; return true;
    }
    Result destroy(uint64_t entry,const Job& job) {
        Record* r=record(entry,job);
        if(!r || r->terminal || !r->cleanup || !r->producerDone || !r->consumerDone || (r->buffer && r->buffer.use_count()!=1)) return {};
        const unsigned needed=static_cast<unsigned>(r->packet.has_value())+static_cast<unsigned>(r->cancelled);
        if(receiptExhausted_ || needed>std::numeric_limits<uint64_t>::max()-nextReceipt_+1) return {Result::Status::Exhausted,{}};
        // The native buffer is physically destroyed before a final cleanup proof.
        r->buffer.reset(); r->bytes=0; r->terminal=true;
        if(r->packet) { auto proof=receipt(Receipt::Kind::Released,*r); if(proof) r->proof.push_back(*proof); }
        if(r->cancelled) { auto proof=receipt(Receipt::Kind::Cancelled,*r); if(proof) r->proof.push_back(*proof); }
        return {Result::Status::Complete,r->proof};
    }
    bool acknowledge(uint64_t entry,const Binding& authenticated,const Job& job,Id<ReceiptSequence> finalSequence) {
        Record* r=record(entry,job);
        if(!actor(entry,authenticated) && (!r || r->job.binding!=authenticated)) return false;
        if(!r || !r->terminal || r->buffer || r->proof.empty() || r->proof.back().sequence!=finalSequence) return false;
        records_.erase(job); return true;
    }
    std::shared_ptr<const Buffer> fetch(uint64_t entry,const Binding& authenticated,const Token& token) const {
        auto a=actors_.find(entry);
        if(a==actors_.end() || a->second.scope.binding!=authenticated || !a->second.coherent) return {};
        const auto& sc=a->second.scope;
        for(const auto& [job,r]:records_) {
            if(r.entry!=entry || r.terminal || r.cleanup || !r.producerDone || !r.packet || r.packet->token!=token || job.binding!=authenticated || job.clock!=sc.clock || !generations(job.context,sc.context) || r.packet->expires<=sc.now || !sc.present || sc.locked || !sc.gpuReady) continue;
            return r.buffer;
        }
        return {};
    }
    struct ViewRecord {
        uint64_t entry; Job job; uint64_t bytes; bool allocated, cleanup, producerDone, consumerDone, terminal;
        std::optional<Packet> packet; std::vector<Receipt> proofs;
    };
    std::vector<ViewRecord> inspect() const {
        std::vector<ViewRecord> result;
        for(const auto& [j,r]:records_) result.push_back({r.entry,r.job,r.bytes,r.packet.has_value(),r.cleanup,r.producerDone,r.consumerDone,r.terminal,r.packet,r.proof});
        return result;
    }
    std::optional<uint64_t> owningEntry(const Job& job) const {
        auto it=records_.find(job); return it==records_.end() ? std::nullopt : std::optional<uint64_t>{it->second.entry};
    }
    const Scope& nativeScope(uint64_t entry) const { return actors_.at(entry).scope; }
    uint64_t nativeCost(uint64_t entry) const { return actors_.at(entry).cost; }
    uint64_t nextProofSequence() const { return nextReceipt_; }
    uint64_t nextTokenSequence() const { return nextToken_; }
    uint64_t charge() const {
        uint64_t bytes=0; for(const auto& [j,r]:records_) bytes+=r.bytes;
        return bytes;
    }
    size_t activeItems() const { return items(); }
    size_t recordCount() const { return records_.size(); }
    uint64_t requestFloor(uint64_t entry) const { return actors_.at(entry).floor; }
};
}

#pragma once
#include "demand.hpp"
#include <gio/gio.h>
#include <functional>
#include <mutex>
#include <set>
#include <span>
#include <string_view>
#include <utility>

namespace preview::uri {
// Native producer-owned encoded bytes. The producer's full allocation must be
// accounted by charge(), including any retained backing storage. JSON cannot
// construct this type or establish completion of either native fence.
struct Payload : Buffer {
    virtual std::span<const uint8_t> png() const noexcept=0;
};
struct View {
    Binding binding;
    std::set<uint64_t> entries;
    uint64_t epoch{};
};
struct NativeTime { Id<Clock> clock; uint64_t now; };
using ClockSource=std::function<std::optional<NativeTime>(uint64_t)>;
struct Shared {
    std::mutex lock;
    Broker broker;
    std::unique_ptr<demand::Coordinator> demand;
    std::map<uint64_t,View> views;
    uint64_t nextView{1};
    bool viewExhausted{};
    size_t readers{},maxReaders,maxViews;
    ClockSource time;
    explicit Shared(Limits limits,size_t readers,size_t views,ClockSource clock):broker(limits),maxReaders(readers),maxViews(views),time(std::move(clock)) {
        if(!readers || !views || !time) throw std::invalid_argument("Positive URI limits and native clock source");
    }
};
struct Reader {
    std::shared_ptr<Shared> state;
    std::shared_ptr<const Payload> payload;
    uint64_t view{},epoch{},entry{};
    Binding binding;
    Token token;
    size_t offset{};
};
std::string encode(const Token&);
// Exact lower-case opaque64 token, including the broker's nonce. No percent
// decoding, query strings, file paths, decimal token aliases or host aliases.
std::optional<Token> decode(std::string_view);
GInputStream* stream(std::unique_ptr<Reader>);
class Endpoint {
    std::shared_ptr<Shared> state_;
public:
    Endpoint(Limits limits,size_t readers,size_t views,ClockSource clock):state_(std::make_shared<Shared>(limits,readers,views,std::move(clock))){}
    // Trusted native API only, serialized with reads. The production caller
    // must enroll source facts from the owning compositor and supervised bridge.
    template<class F> auto native(F&& f) {
        std::lock_guard guard(state_->lock);
        return std::invoke(std::forward<F>(f),state_->broker);
    }
    // Trusted journal operations inspect receiver and broker in one critical
    // section. A copied view must not authorize a replaced receiver epoch.
    template<class F> auto nativeView(uint64_t id,F&& f) {
        std::lock_guard guard(state_->lock);
        auto found=state_->views.find(id);
        const View* view=found==state_->views.end()?nullptr:&found->second;
        return std::invoke(std::forward<F>(f),state_->broker,view);
    }
    // Configure once through the trusted native provider; web content cannot
    // supply a policy or replace lifetime/clock ownership. The broker remains
    // owned by Shared so live Reader references keep physical storage alive.
    bool enableDemand(demand::Policy policy) {
        std::lock_guard guard(state_->lock);
        if(state_->demand) return false;
        state_->demand=std::make_unique<demand::Coordinator>(policy,state_->broker);
        return true;
    }
    template<class F> auto nativeDemand(F&& f) {
        std::lock_guard guard(state_->lock);
        if(!state_->demand) throw std::logic_error("Native demand not enrolled");
        return std::invoke(std::forward<F>(f),*state_->demand);
    }
    // Native enrollment validates the original receiver before querying scope,
    // retaining intent or reserving a job. Membership and reservation then
    // share this lock with receiver replacement, journal delivery and readers.
    template<class F> auto nativeDemandView(uint64_t id,F&& f) {
        std::lock_guard guard(state_->lock);
        if(!state_->demand) throw std::logic_error("Native demand not enrolled");
        auto found=state_->views.find(id);
        View* view=found==state_->views.end()?nullptr:&found->second;
        return std::invoke(std::forward<F>(f),*state_->demand,view);
    }
    // The aggregate native retirement preflight sees every receiver under the
    // same mutex as readers, producer/capture, demand and retained journal work.
    template<class F> auto nativeRetirementView(uint64_t id,F&& f) {
        std::lock_guard guard(state_->lock);
        if(!state_->demand)throw std::logic_error("Native demand not enrolled");
        auto found=state_->views.find(id);
        View* view=found==state_->views.end()?nullptr:&found->second;
        return std::invoke(std::forward<F>(f),*state_->demand,view,std::as_const(state_->views));
    }
    // ID is an enrolled native WebKitWebView identity, never a wire field.
    bool registerView(uint64_t id,const Binding& binding,std::set<uint64_t> entries);
    // Fresh trusted transport enrollment before any subject/job exists. Empty
    // membership cannot authorize URI reads; native admission extends it later.
    bool registerControlView(uint64_t id,const Binding& binding);
    // Trusted native admission only. Add previously enrolled own actors without
    // replacing the receiver epoch or revoking held readers of existing entries.
    bool extendView(uint64_t id,const Binding& binding,const std::set<uint64_t>& entries);
    void unregisterView(uint64_t id);
    std::optional<View> registeredView(uint64_t id) const {
        std::lock_guard guard(state_->lock);auto it=state_->views.find(id);
        return it==state_->views.end()?std::nullopt:std::optional<View>{it->second};
    }
    GInputStream* open(uint64_t view,std::string_view uri,gsize* length,GError** error);
    size_t readers() const { std::lock_guard guard(state_->lock); return state_->readers; }
};
}

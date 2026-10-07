#include "preview_uri.hpp"
#include <algorithm>
#include <array>
#include <cstring>
#include <iomanip>
#include <sstream>

namespace preview::uri {
std::string encode(const Token& token) {
    std::ostringstream out;
    out<<"0000000000000000"<<std::hex<<std::setfill('0');
    for(auto byte:token.brokerNonce) out<<std::setw(2)<<static_cast<unsigned>(byte);
    out<<std::setw(16)<<token.sequence;
    return "elm-shell://preview/"+out.str();
}
std::optional<Token> decode(std::string_view uri) {
    constexpr std::string_view prefix="elm-shell://preview/";
    if(uri.size()!=prefix.size()+64 || !uri.starts_with(prefix)) return {};
    auto hex=uri.substr(prefix.size());
    if(hex.substr(0,16)!="0000000000000000") return {};
    for(char c:hex) if(!((c>='0' && c<='9') || (c>='a' && c<='f'))) return {};
    auto nibble=[](char c)->uint8_t { return c<='9' ? c-'0' : c-'a'+10; };
    Token token;
    for(size_t i=0;i<16;++i) token.brokerNonce[i]=static_cast<uint8_t>(nibble(hex[16+i*2])*16+nibble(hex[17+i*2]));
    for(char c:hex.substr(48)) token.sequence=(token.sequence<<4)|nibble(c);
    if(!token.sequence) return {};
    return token;
}
static bool authorized(const Reader& r) {
    const auto lifetime=r.lifetime.lock();if(!lifetime || !lifetime->active)return false;
    auto view=r.state->views.find(r.view);
    if(view==r.state->views.end() || view->second.epoch!=r.epoch || view->second.binding!=r.binding || !view->second.entries.contains(r.entry)) return false;
    try {
        const auto& scope=r.state->broker.nativeScope(r.entry);
        const auto time=r.state->time(r.entry);
        if(!time || time->clock!=scope.clock || time->now<scope.now) return false;
        for(const auto& record:r.state->broker.inspect())
            if(record.entry==r.entry && record.packet && record.packet->token==r.token)
                return time->now<record.packet->expires && static_cast<bool>(r.state->broker.fetch(r.entry,r.binding,r.token));
    } catch(...) {return false;}
    return false;
}
typedef struct _PreviewStream { GInputStream parent; Reader* reader; } PreviewStream;
typedef struct _PreviewStreamClass { GInputStreamClass parent; } PreviewStreamClass;
G_DEFINE_TYPE(PreviewStream,preview_stream,G_TYPE_INPUT_STREAM)
static void releaseReader(PreviewStream* self) {
    if(!self->reader) return;
    std::unique_ptr<Reader> r(self->reader);self->reader=nullptr;
    std::lock_guard guard(r->state->lock);
    r->payload.reset();
    --r->state->readers;
    // Closing a stream drops only its read reference. It does not signal a
    // native producer/consumer fence or acknowledge a terminal broker record.
}
static gssize readStream(GInputStream* input,void* output,gsize requested,GCancellable* cancel,GError** error) {
    auto self=reinterpret_cast<PreviewStream*>(input);
    if(g_cancellable_set_error_if_cancelled(cancel,error)) return -1;
    Reader* r=self->reader;
    if(!r) {g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_CLOSED,"Preview reader closed");return -1;}
    std::lock_guard guard(r->state->lock);
    if(!authorized(*r)) {g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,"Preview authority revoked");return -1;}
    auto bytes=r->payload->png();
    if(r->offset>bytes.size()) {g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Native preview size changed");return -1;}
    size_t count=std::min(static_cast<size_t>(requested),bytes.size()-r->offset);
    if(count) std::memcpy(output,bytes.data()+r->offset,count);
    r->offset+=count;
    return static_cast<gssize>(count);
}
static gboolean closeStream(GInputStream* input,GCancellable*,GError**) {
    releaseReader(reinterpret_cast<PreviewStream*>(input));return TRUE;
}
static void finalizeStream(GObject* object) {
    releaseReader(reinterpret_cast<PreviewStream*>(object));
    G_OBJECT_CLASS(preview_stream_parent_class)->finalize(object);
}
static void preview_stream_class_init(PreviewStreamClass* klass) {
    auto streamClass=G_INPUT_STREAM_CLASS(klass);
    streamClass->read_fn=readStream;streamClass->close_fn=closeStream;
    G_OBJECT_CLASS(klass)->finalize=finalizeStream;
}
static void preview_stream_init(PreviewStream* self) {self->reader=nullptr;}
GInputStream* stream(std::unique_ptr<Reader> reader) {
    auto object=reinterpret_cast<PreviewStream*>(g_object_new(preview_stream_get_type(),nullptr));
    object->reader=reader.release();return G_INPUT_STREAM(object);
}
bool Endpoint::registerControlView(uint64_t id,const Binding& binding,uint64_t nativeRealmEpoch) {
    std::lock_guard guard(state_->lock);
    if(!id || !binding.lifetime.value || !binding.session.value || !binding.frontend.value ||
       state_->viewExhausted || state_->views.contains(id) || state_->views.size()>=state_->maxViews)return false;
    if(nativeRealmEpoch && (nativeRealmEpoch<state_->nextView || !state_->views.empty() ||
       state_->broker.actorCount() || state_->broker.recordCount() || state_->readers))return false;
    const auto epoch=nativeRealmEpoch?nativeRealmEpoch:state_->nextView;
    // Publish the native receiver before advancing its namespace; allocation
    // failure creates neither a receiver nor an invented native subject.
    state_->views.emplace(id,View{binding,{},epoch});
    if(epoch==std::numeric_limits<uint64_t>::max())state_->viewExhausted=true;else state_->nextView=epoch+1;
    return true;
}
bool Endpoint::registerView(uint64_t id,const Binding& binding,std::set<uint64_t> entries) {
    std::lock_guard guard(state_->lock);
    if(!id || !binding.lifetime.value || !binding.session.value || !binding.frontend.value || entries.empty() || state_->viewExhausted || state_->views.contains(id) || state_->views.size()>=state_->maxViews) return false;
    for(auto entry:entries) { try {state_->broker.nativeScope(entry);} catch(const std::out_of_range&) {return false;} }
    const auto epoch=state_->nextView;
    if(epoch==std::numeric_limits<uint64_t>::max()) state_->viewExhausted=true;else ++state_->nextView;
    state_->views.emplace(id,View{binding,std::move(entries),epoch});return true;
}
bool Endpoint::extendView(uint64_t id,const Binding& binding,const std::set<uint64_t>& entries) {
    std::lock_guard guard(state_->lock);
    const auto found=state_->views.find(id);
    if(found==state_->views.end() || found->second.binding!=binding || entries.empty())return false;
    auto joined=found->second.entries;
    for(auto entry:entries) {
        if(!entry)return false;
        try {if(state_->broker.nativeScope(entry).binding!=binding)return false;}
        catch(const std::out_of_range&) {return false;}
        joined.insert(entry);
    }
    if(joined.size()>state_->broker.limits().entries)return false;
    found->second.entries=std::move(joined);
    return true;
}
void Endpoint::unregisterView(uint64_t id) {std::lock_guard guard(state_->lock);state_->views.erase(id);}
static GInputStream* openLocked(const std::shared_ptr<Shared>& state,const std::shared_ptr<EndpointLifetime>& lifetime,uint64_t id,std::string_view uri,gsize* length,GError** error) {
    auto token=decode(uri);auto view=state->views.find(id);
    if(!token || view==state->views.end() || state->readers>=state->maxReaders) {g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,"Preview request refused");return nullptr;}
    for(const auto& record:state->broker.inspect()) {
        if(!record.packet || record.packet->token!=*token || !view->second.entries.contains(record.entry)) continue;
        auto payload=std::dynamic_pointer_cast<const Payload>(state->broker.fetch(record.entry,view->second.binding,*token));
        constexpr std::array<uint8_t,8> magic{137,80,78,71,13,10,26,10};
        if(!payload || payload->png().size()<magic.size() || payload->png().size()>static_cast<size_t>(G_MAXSSIZE) || !std::equal(magic.begin(),magic.end(),payload->png().begin())) break;
        auto reader=std::make_unique<Reader>(Reader{state,payload,id,view->second.epoch,record.entry,view->second.binding,*token,0,lifetime});
        if(!authorized(*reader)) break;
        ++state->readers;
        if(length) *length=payload->png().size();
        return stream(std::move(reader));
    }
    g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,"Preview pixels unavailable");return nullptr;
}
GInputStream* Endpoint::open(uint64_t id,std::string_view uri,gsize* length,GError** error) {
    if(length)*length=0;
    std::lock_guard guard(state_->lock);
    return openLocked(state_,lifetime_,id,uri,length,error);
}
GInputStream* ReadCapability::open(uint64_t id,std::string_view uri,gsize* length,GError** error)const {
    if(length)*length=0;
    auto state=state_.lock();auto lifetime=lifetime_.lock();
    if(state && lifetime){
        std::lock_guard guard(state->lock);auto found=state->views.find(id);
        if(lifetime->active && id==view_ && found!=state->views.end() && found->second.binding==binding_ && found->second.epoch==epoch_)
            return openLocked(state,lifetime,id,uri,length,error);
    }
    g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,"Native preview route retired");return nullptr;
}
}

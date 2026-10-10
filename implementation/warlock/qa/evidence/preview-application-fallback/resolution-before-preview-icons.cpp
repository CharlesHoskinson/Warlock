#include "preview_icons.hpp"
#include <sys/random.h>
namespace preview::icons {
namespace {
constexpr std::string_view prefix="elm-shell://icon/";
constexpr size_t maxAsset=65536,maxAssets=2,maxReaders=4;
std::string randomToken() {
    std::array<uint8_t,32> bytes{};size_t offset=0;
    while(offset<bytes.size()) {const auto n=getrandom(bytes.data()+offset,bytes.size()-offset,0);if(n<0 && errno==EINTR)continue;require(n>0,"Native icon nonce");offset+=n;}
    const char* hex="0123456789abcdef";std::string token;token.reserve(64);
    for(auto b:bytes){token+=hex[b>>4];token+=hex[b&15];}require(token!=std::string(64,'0'),"Nonzero native icon nonce");return token;
}
bool canonical(std::string_view token) {return token.size()==64 && token!=std::string(64,'0') && std::all_of(token.begin(),token.end(),[](char c){return (c>='0' && c<='9') || (c>='a' && c<='f');});}
bool permitted(const State& state,const Record& record) {
    if(!state.view || record.revoked || record.metadata.binding!=state.binding || record.metadata.subject!=state.subject)return false;
    try {return state.authorize(record);}catch(...){return false;}
}
struct Reader {std::shared_ptr<State> state;std::shared_ptr<Record> record;size_t offset{};};
typedef struct _WarlockIconStream {GInputStream parent;Reader* reader;} WarlockIconStream;
typedef struct _WarlockIconStreamClass {GInputStreamClass parent;} WarlockIconStreamClass;
G_DEFINE_TYPE(WarlockIconStream,warlock_icon_stream,G_TYPE_INPUT_STREAM)
void release(WarlockIconStream* stream) {
    if(!stream->reader)return;
    std::unique_ptr<Reader> reader(stream->reader);stream->reader=nullptr;
    std::lock_guard guard(reader->state->lock);--reader->record->readers;--reader->state->readers;
    std::erase_if(reader->state->records,[](const auto& row){return row->revoked && !row->readers;});
}
gssize read(GInputStream* input,void* output,gsize requested,GCancellable* cancel,GError** error) {
    auto stream=reinterpret_cast<WarlockIconStream*>(input);if(g_cancellable_set_error_if_cancelled(cancel,error))return -1;
    auto reader=stream->reader;if(!reader)return 0;
    std::unique_lock guard(reader->state->lock);
    if(!permitted(*reader->state,*reader->record)) {g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,"Native icon authority revoked");return -1;}
    const auto& bytes=reader->record->asset.png;if(reader->offset>bytes.size()){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Native icon reader offset");return -1;}
    const auto count=std::min<size_t>(requested,bytes.size()-reader->offset);if(count)memcpy(output,bytes.data()+reader->offset,count);reader->offset+=count;
    const bool consumed=reader->offset==bytes.size();guard.unlock();if(consumed)release(stream);return count;
}
gboolean close(GInputStream* input,GCancellable*,GError**) {release(reinterpret_cast<WarlockIconStream*>(input));return TRUE;}
void finalize(GObject* object) {release(reinterpret_cast<WarlockIconStream*>(object));G_OBJECT_CLASS(warlock_icon_stream_parent_class)->finalize(object);}
void warlock_icon_stream_class_init(WarlockIconStreamClass* klass) {auto base=G_INPUT_STREAM_CLASS(klass);base->read_fn=read;base->close_fn=close;G_OBJECT_CLASS(klass)->finalize=finalize;}
void warlock_icon_stream_init(WarlockIconStream* stream) {stream->reader=nullptr;}
}
std::optional<Asset> resolveApplication(const std::string& application) {
    GIcon* icon=nullptr;std::string kind="generic";
    const bool valid=!application.empty() && application.size()<=255 && std::all_of(application.begin(),application.end(),[](char c){return (c>='a' && c<='z') || (c>='A' && c<='Z') || (c>='0' && c<='9') || c=='.' || c=='-' || c=='_';});
    if(valid && application!="." && application!="..") {
        auto id=application.ends_with(".desktop")?application:application+".desktop";
        GDesktopAppInfo* app=g_desktop_app_info_new(id.c_str());
        if(app) {if(auto actual=g_app_info_get_icon(G_APP_INFO(app))){icon=G_ICON(g_object_ref(actual));kind="application";}g_object_unref(app);}
    }
    if(!icon)icon=g_themed_icon_new("application-x-executable");
    auto theme=gtk_icon_theme_get_default();if(!theme){g_object_unref(icon);return {};}
    GtkIconInfo* info=gtk_icon_theme_lookup_by_gicon(theme,icon,48,GTK_ICON_LOOKUP_FORCE_SIZE);g_object_unref(icon);
    if(!info && kind=="application") {kind="generic";info=gtk_icon_theme_lookup_icon(theme,"application-x-executable",48,GTK_ICON_LOOKUP_FORCE_SIZE);}
    if(!info)return {};
    GError* error=nullptr;GdkPixbuf* image=gtk_icon_info_load_icon(info,&error);g_object_unref(info);g_clear_error(&error);if(!image)return {};
    const auto width=gdk_pixbuf_get_width(image),height=gdk_pixbuf_get_height(image);
    if(width<=0 || height<=0 || width>128 || height>128){g_object_unref(image);return {};}
    gchar* bytes=nullptr;gsize size=0;const bool saved=gdk_pixbuf_save_to_buffer(image,&bytes,&size,"png",&error,nullptr);g_object_unref(image);g_clear_error(&error);
    if(!saved || size<8 || size>maxAsset){g_free(bytes);return {};}
    Asset asset{{reinterpret_cast<uint8_t*>(bytes),reinterpret_cast<uint8_t*>(bytes)+size},kind};g_free(bytes);return asset;
}
Endpoint::Endpoint(uint64_t view,Binding binding,uint64_t subject,std::function<bool(const Record&)> authorize):state_(std::make_shared<State>()) {
    require(view && subject && binding.lifetime.value && binding.session.value && binding.frontend.value && authorize,"Native icon owner enrollment");
    state_->view=view;state_->binding=binding;state_->subject=subject;state_->authorize=std::move(authorize);
}
std::optional<std::string> Endpoint::issue(const WindowMetadata& metadata,const Scope& scope,Asset asset) {
    std::lock_guard guard(state_->lock);
    require(metadata.binding==state_->binding && metadata.subject==state_->subject && scope.binding==state_->binding && scope.context.incarnation.value==metadata.subject && scope.present && !scope.locked,"Own current native icon metadata scope");
    const std::array<uint8_t,8> magic{137,80,78,71,13,10,26,10};
    require(asset.png.size()>=8 && asset.png.size()<=maxAsset && std::equal(magic.begin(),magic.end(),asset.png.begin()) && (asset.kind=="application" || asset.kind=="generic"),"Bounded native PNG icon");
    for(auto& row:state_->records) {
        if(!row->revoked && row->metadata.application==metadata.application && row->privacy==scope.context.privacy.value && row->asset.kind==asset.kind && row->asset.png==asset.png)return row->token;
        row->revoked=true;
    }
    std::erase_if(state_->records,[](const auto& row){return row->revoked && !row->readers;});
    if(!state_->view || state_->records.size()>=maxAssets)return {};
    auto record=std::make_shared<Record>(Record{metadata,scope.context.privacy.value,randomToken(),std::move(asset),0,false});state_->records.push_back(record);return record->token;
}
GInputStream* Endpoint::open(uint64_t view,std::string_view uri,gsize* length,GError** error) {
    if(length)*length=0;
    std::lock_guard guard(state_->lock);
    if(view==state_->view && uri.starts_with(prefix) && canonical(uri.substr(prefix.size())) && state_->readers<maxReaders) {
        for(auto& row:state_->records)if(row->token==uri.substr(prefix.size()) && permitted(*state_,*row)) {
            ++row->readers;++state_->readers;if(length)*length=row->asset.png.size();
            auto stream=reinterpret_cast<WarlockIconStream*>(g_object_new(warlock_icon_stream_get_type(),nullptr));stream->reader=new Reader{state_,row,0};return G_INPUT_STREAM(stream);
        }
    }
    g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,"Native icon unavailable");return nullptr;
}
bool Endpoint::close() {std::lock_guard guard(state_->lock);if(state_->readers)return false;state_->view=0;state_->records.clear();return true;}
unsigned Endpoint::readers() {std::lock_guard guard(state_->lock);return state_->readers;}
std::string Endpoint::status() {std::lock_guard guard(state_->lock);size_t bytes=0;for(const auto& row:state_->records)bytes+=row->asset.png.size();Wire wire;return wire.integer("assets",state_->records.size()).integer("readers",state_->readers).integer("bytes",bytes).finish();}
}

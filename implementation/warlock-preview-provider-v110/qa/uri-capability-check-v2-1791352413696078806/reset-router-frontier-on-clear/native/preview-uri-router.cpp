#include "preview-uri-router.h"
#include "preview_uri.hpp"

struct PreviewURIRouter {
    gatomicrefcount references;
    GThread* const thread=g_thread_ref(g_thread_self());
    std::optional<preview::uri::ReadCapability> route;
    std::optional<preview::Binding> binding;
    uint64_t through{};
    PreviewURIRouter(){g_atomic_ref_count_init(&references);}
    ~PreviewURIRouter(){g_thread_unref(thread);}
    void own()const {if(thread!=g_thread_self())throw std::invalid_argument("Native URI router creator thread");}
};
extern "C" PreviewURIRouter* preview_uri_router_new(void){
    try{return new PreviewURIRouter;}catch(...){return nullptr;}
}
extern "C" PreviewURIRouter* preview_uri_router_ref(PreviewURIRouter* router){
    if(router)g_atomic_ref_count_inc(&router->references);
    return router;
}
extern "C" void preview_uri_router_unref(gpointer opaque){
    auto router=static_cast<PreviewURIRouter*>(opaque);
    if(router && g_atomic_ref_count_dec(&router->references))delete router;
}
extern "C" gboolean preview_uri_router_bind(PreviewURIRouter* router,void* opaque,gpointer receiver,guint64 epoch,GError** error){
    try{
        if(!router || !opaque || !receiver || !epoch)throw std::invalid_argument("Native URI router enrollment inputs");
        router->own();const auto& endpoint=*static_cast<preview::uri::Endpoint*>(opaque);
        auto candidate=endpoint.readCapability(reinterpret_cast<uint64_t>(receiver),epoch);
        if(router->binding && *router->binding!=candidate.binding())throw std::invalid_argument("Original native URI router binding");
        if(epoch<=router->through){
            if(router->route && router->route->sameRealm(candidate))return TRUE;
            throw std::invalid_argument("Monotonic native URI router realm");
        }
        // All fallible validation precedes replacement. Capabilities retain weak
        // authority only; callback ownership cannot pin physical broker storage.
        router->route=std::move(candidate);router->binding=router->route->binding();router->through=epoch;return TRUE;
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,exception.what());return FALSE;}
}
extern "C" gboolean preview_uri_router_clear(PreviewURIRouter* router,GError** error){
    try{if(!router)throw std::invalid_argument("Native URI router owner");router->own();router->route.reset();router->through=0;return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,exception.what());return FALSE;}
}
extern "C" GInputStream* preview_uri_router_open(PreviewURIRouter* router,gpointer receiver,const char* uri,gsize* length,GError** error){
    if(length)*length=0;
    try{
        if(!router || !receiver || !uri)throw std::invalid_argument("Native URI callback inputs");
        router->own();if(router->route)return router->route->open(reinterpret_cast<uint64_t>(receiver),uri,length,error);
        throw std::invalid_argument("Native preview route unavailable");
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,exception.what());return nullptr;}
}

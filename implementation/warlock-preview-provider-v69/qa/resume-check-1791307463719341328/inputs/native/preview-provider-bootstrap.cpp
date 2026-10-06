#include "preview-provider-bootstrap.h"
#include "preview_delivery.hpp"
#include "preview_metadata.hpp"
#include <climits>

struct WarlockPreviewBootstrap {std::unique_ptr<preview::bridge::Native> native;std::unique_ptr<preview::bridge::ReceiptDelivery> delivery;};
namespace {
using namespace preview::bridge;
Json configuration(const char* name) {
    require(name!=nullptr,"Native enrollment config path");std::string path(name);auto split=path.rfind('/');
    require(split!=path.npos && split>0 && split+1<path.size(),"Absolute native enrollment file");
    auto base=path.substr(split+1);require(base!="." && base!="..","Native enrollment basename");
    auto parent=directory(path.substr(0,split));preview::fd::Owned file(::openat(parent.get(),base.c_str(),O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK));
    struct stat before{};require(file && fstat(file.get(),&before)==0 && S_ISREG(before.st_mode) && before.st_uid==getuid() && (before.st_mode&0777)==0600 && before.st_nlink==1 && before.st_size>0 && before.st_size<=65536,"Private bounded native enrollment file");
    std::string bytes;std::array<char,4096> buffer{};
    for(;;) {auto n=read(file.get(),buffer.data(),buffer.size());if(n<0 && errno==EINTR)continue;require(n>=0,"Native enrollment read");if(!n)break;require(bytes.size()+static_cast<size_t>(n)<=65536,"Native enrollment byte bound");bytes.append(buffer.data(),n);}
    struct stat after{};require(fstat(file.get(),&after)==0 && same(before,after) && before.st_nlink==after.st_nlink && before.st_size==after.st_size && static_cast<size_t>(before.st_size)==bytes.size() && before.st_mtim.tv_sec==after.st_mtim.tv_sec && before.st_mtim.tv_nsec==after.st_mtim.tv_nsec && before.st_ctim.tv_sec==after.st_ctim.tv_sec && before.st_ctim.tv_nsec==after.st_ctim.tv_nsec,"Native enrollment bytes stable during read");
    return Json(bytes);
}
void failure(GError** error,const char* message) {
    // A local admission/transport failure does not fabricate a native Refused
    // receipt or settle any previously issued operation.
    g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,message);
}
}
extern "C" WarlockPreviewBootstrap* warlock_preview_bootstrap_open(const char* name,GError** error) {
    try {
        auto config=configuration(name);auto object=config.object();Json::fields(object,{"runtime","instance","pid","expected_start","binary_sha256"});
        auto pid=Json::integer(object,"pid"),start=Json::integer(object,"expected_start");require(pid>0 && pid<=INT_MAX && start>0,"Native config process identity");
        auto owner=std::make_unique<WarlockPreviewBootstrap>();owner->native=std::make_unique<Native>(static_cast<pid_t>(pid),static_cast<uint64_t>(start),Json::text(object,"runtime"),Json::text(object,"instance"),Json::text(object,"binary_sha256"));return owner.release();
    }catch(const std::exception& exception){failure(error,exception.what());return nullptr;}
    catch(...){failure(error,"Native provider enrollment unavailable");return nullptr;}
}
extern "C" gboolean warlock_preview_bootstrap_binding(WarlockPreviewBootstrap* owner,char** binding,GError** error) {
    if(binding)*binding=nullptr;
    try {require(owner && owner->native && binding,"Native provider owner required");auto json=owner->native->bindingJSON();*binding=g_strdup(json.c_str());return TRUE;}
    catch(const std::exception& exception){failure(error,exception.what());return FALSE;}
    catch(...){failure(error,"Native provider binding unavailable");return FALSE;}
}
extern "C" void* warlock_preview_bootstrap_native_transport(WarlockPreviewBootstrap* owner,GError** error) {
    try {require(owner && owner->native,"Own native provider required");owner->native->binding();return owner->native.get();}
    catch(const std::exception& exception){failure(error,exception.what());return nullptr;}
    catch(...){failure(error,"Native producer transport unavailable");return nullptr;}
}
namespace {
template<class F> gboolean output(WarlockPreviewBootstrap* owner,char** json,GError** error,F function) {
    if(json)*json=nullptr;
    try {require(owner && owner->native && json,"Native provider output owner required");*json=g_strdup(function(*owner).c_str());return TRUE;}
    catch(const std::exception& exception){failure(error,exception.what());return FALSE;}
    catch(...){failure(error,"Native provider output unavailable");return FALSE;}
}
}
extern "C" gboolean warlock_preview_bootstrap_enrollment(WarlockPreviewBootstrap* owner,char** json,GError** error) {
    return output(owner,json,error,[](auto& provider) {
        auto native=provider.native->enrollment();Wire out;
        out.integer("enrollmentProtocol",1).text("kind","native-preview-enrollment").begin("binding").binding(native.binding).end().begin("provider").integer("pid",native.providerPID).counter("start",native.providerStart).end().begin("compositor").integer("pid",native.compositorPID).counter("start",native.compositorStart).text("executableSHA256",native.executableSHA256).text("coreABIMetadata",native.coreABIMetadata).text("instance",native.instance).end().boolean("loadedPluginAttested",false).begin("capabilities").boolean("observe",native.observe).boolean("effects",native.effects).boolean("minimizedState",native.minimizedState).boolean("canonicalScene",native.canonicalScene).integer("effectProtocol",native.effectProtocol).integer("taskbarProjectionProtocol",native.taskbarProjectionProtocol).integer("effectInvalidationProtocol",native.effectInvalidationProtocol).array("operations");
        for(const auto& operation:native.operations){out.element(operation.c_str());}
        return out.endArray().end().finish();
    });
}
extern "C" gboolean warlock_preview_bootstrap_catalog(WarlockPreviewBootstrap* owner,guint64 publication,guint64 lease,char** json,GError** error) {
    return output(owner,json,error,[&](auto& provider) {
        require(publication && lease,"Current picker metadata enrollment stamp");
        const auto catalog=windowCatalog(*provider.native);Wire out;
        out.integer("protocolVersion",3).text("kind","catalog").counter("publication",publication).counter("lease",lease).begin("binding").binding(catalog.binding).end().counter("requestId",catalog.request).counter("sequence",catalog.sequence).counter("revision",catalog.revision).array("windows");
        for(const auto& row:catalog.windows) {
            out.beginElement().counter("incarnation",row.subject).text("application",row.application).text("label",row.title).boolean("minimized",row.minimized).end();
        }
        return out.endArray().finish();
    });
}
extern "C" gboolean warlock_preview_bootstrap_scope(WarlockPreviewBootstrap* owner,guint64 subject,char** json,GError** error) {
    return output(owner,json,error,[&](auto& provider) {
        const auto observed=provider.native->scope({subject});const auto& scope=observed.scope;Wire out;
        out.integer("protocolVersion",3).text("kind","preview-capture-probe-scope").begin("binding").binding(scope.binding).end().counter("requestId",observed.request).begin("scope").begin("binding").binding(scope.binding).end().begin("context").context(scope.context).end().counter("observation",observed.observation).counter("clock",scope.clock.value).counter("now",scope.now).boolean("present",scope.present).boolean("sourceLive",scope.sourceLive).boolean("locked",scope.locked).boolean("gpuReady",scope.gpuReady).end().counter("maximumTransferBytes",observed.maximumTransferBytes).boolean("previewEligible",false).text("scopeKind","root-surface-commit-monitor-plane-unqualified");return out.finish();
    });
}
extern "C" gboolean warlock_preview_bootstrap_client_scope(WarlockPreviewBootstrap* owner,guint64 subject,char** json,GError** error) {
    return output(owner,json,error,[&](auto& provider) {
        const auto observed=provider.native->clientScope({subject});const auto& scope=observed.scope;Wire out;
        out.integer("protocolVersion",3).text("kind","preview-client-scope").begin("binding").binding(scope.binding).end().counter("requestId",observed.request).begin("scope").begin("binding").binding(scope.binding).end().begin("context").context(scope.context).end().counter("observation",observed.observation).counter("clock",scope.clock.value).counter("now",scope.now).boolean("present",scope.present).boolean("sourceLive",scope.sourceLive).boolean("locked",scope.locked).boolean("gpuReady",scope.gpuReady).end().counter("maximumTransferBytes",observed.maximumTransferBytes).boolean("previewEligible",false).text("scopeKind","isolated-root-client-unqualified");return out.finish();
    });
}
extern "C" gboolean warlock_preview_bootstrap_attach_delivery(WarlockPreviewBootstrap* owner,void* endpoint,gpointer popup,GError** error) {
    try {require(owner && owner->native && endpoint && popup && !owner->delivery,"One native delivery enrollment");owner->delivery=std::make_unique<preview::bridge::ReceiptDelivery>(*static_cast<preview::uri::Endpoint*>(endpoint),owner->native->binding(),reinterpret_cast<uintptr_t>(popup));return TRUE;}
    catch(const std::exception& exception){failure(error,exception.what());return FALSE;}
    catch(...){failure(error,"Native receipt enrollment unavailable");return FALSE;}
}
extern "C" gboolean warlock_preview_bootstrap_extend_delivery(WarlockPreviewBootstrap* owner,gpointer popup,GError** error) {
    try {require(owner && owner->native && owner->delivery && popup,"Native receipt membership owner required");owner->native->binding();return owner->delivery->extendSubjects(reinterpret_cast<uintptr_t>(popup));}
    catch(const std::exception& exception){failure(error,exception.what());return FALSE;}
    catch(...){failure(error,"Native receipt membership unavailable");return FALSE;}
}
extern "C" gboolean warlock_preview_bootstrap_pending(WarlockPreviewBootstrap* owner,gpointer popup,char** json,GError** error) {
    return output(owner,json,error,[&](auto& provider) {
        provider.native->binding();require(bool(provider.delivery),"Native receipt delivery enrolled");auto wires=provider.delivery->pending(reinterpret_cast<uintptr_t>(popup));std::string encoded="[";
        for(const auto& wire:wires){if(encoded.size()>1)encoded+=",";encoded+=wire;}encoded+="]";return encoded;
    });
}
extern "C" gboolean warlock_preview_bootstrap_acknowledge(WarlockPreviewBootstrap* owner,gpointer popup,const char* identity,const char* command,GError** error) {
    try {require(owner && owner->native && owner->delivery && identity && command,"Native acknowledgement owner required");owner->native->binding();return owner->delivery->acknowledge(reinterpret_cast<uintptr_t>(popup),identity,command);}
    catch(const std::exception& exception){failure(error,exception.what());return FALSE;}
    catch(...){failure(error,"Native receipt acknowledgement unavailable");return FALSE;}
}
extern "C" void warlock_preview_bootstrap_free(WarlockPreviewBootstrap* owner) {
    // Releasing this C++ handle is not physical capture cleanup or a grant
    // retirement certificate. Those retain their native ownership protocol.
    delete owner;
}

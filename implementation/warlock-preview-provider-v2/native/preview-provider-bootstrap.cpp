#include "preview-provider-bootstrap.h"
#include "preview_client.hpp"
#include <climits>

struct WarlockPreviewBootstrap {std::unique_ptr<preview::bridge::Native> native;};
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
extern "C" void warlock_preview_bootstrap_free(WarlockPreviewBootstrap* owner) {
    // Releasing this C++ handle is not physical capture cleanup or a grant
    // retirement certificate. Those retain their native ownership protocol.
    delete owner;
}

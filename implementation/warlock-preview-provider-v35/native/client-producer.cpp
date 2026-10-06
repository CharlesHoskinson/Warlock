#include "client-producer.h"
#include "client_producer.hpp"
#include "family_producer.hpp"
struct WarlockClientProducer {
 std::unique_ptr<preview::bridge::ClientProducer> client;
 std::unique_ptr<preview::bridge::FamilyProducer> family;
 WarlockClientProducer(preview::bridge::Native& native,uint64_t popup,uint64_t subject,uint64_t publication,uint64_t lease,bool useFamily=false,preview::bridge::FamilyPlane plane=preview::bridge::FamilyPlane::Transparent){if(useFamily)family=std::make_unique<preview::bridge::FamilyProducer>(native,popup,subject,publication,lease,plane);else client=std::make_unique<preview::bridge::ClientProducer>(native,popup,subject,publication,lease);}
 template<class F> auto visit(F&& call){if(family)return call(*family);return call(*client);}
};
namespace {
template<class F> gboolean output(WarlockClientProducer* owner,char** events,GError** error,F call) {
    if(events)*events=nullptr;
    try {preview::bridge::require(owner && events,"Own native client producer output");*events=g_strdup(owner->visit(call).c_str());return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
}
extern "C" WarlockClientProducer* warlock_client_producer_open(void* native,gpointer popup,guint64 subject,guint64 publication,guint64 lease,char** initial,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {preview::bridge::require(native && popup && initial && endpoint,"Trusted client producer enrollment");auto owner=std::make_unique<WarlockClientProducer>(*static_cast<preview::bridge::Native*>(native),reinterpret_cast<uintptr_t>(popup),subject,publication,lease);*initial=g_strdup(owner->visit([](auto& value){return value.initial();}).c_str());*endpoint=owner->visit([](auto& value){return &value.endpoint();});return owner.release();}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" WarlockClientProducer* warlock_family_producer_open(void* native,gpointer popup,guint64 subject,guint64 publication,guint64 lease,char** initial,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {preview::bridge::require(native && popup && initial && endpoint,"Trusted client producer enrollment");auto owner=std::make_unique<WarlockClientProducer>(*static_cast<preview::bridge::Native*>(native),reinterpret_cast<uintptr_t>(popup),subject,publication,lease,true);*initial=g_strdup(owner->visit([](auto& value){return value.initial();}).c_str());*endpoint=owner->visit([](auto& value){return &value.endpoint();});return owner.release();}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" WarlockClientProducer* warlock_backdrop_producer_open(void* native,gpointer popup,guint64 subject,guint64 publication,guint64 lease,char** initial,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {preview::bridge::require(native && popup && initial && endpoint,"Trusted client producer enrollment");auto owner=std::make_unique<WarlockClientProducer>(*static_cast<preview::bridge::Native*>(native),reinterpret_cast<uintptr_t>(popup),subject,publication,lease,true,preview::bridge::FamilyPlane::GeneratedBackdrop);*initial=g_strdup(owner->visit([](auto& value){return value.initial();}).c_str());*endpoint=owner->visit([](auto& value){return &value.endpoint();});return owner.release();}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" gboolean warlock_client_producer_command(WarlockClientProducer* owner,const char* identity,const char* command,char** events,GError** error) {
    return output(owner,events,error,[&](auto& value){preview::bridge::require(identity && command,"Native client command wire");return value.command(identity,command);});
}
extern "C" gboolean warlock_client_producer_poll(WarlockClientProducer* owner,guint64 publication,guint64 lease,char** events,GError** error) {return output(owner,events,error,[&](auto& value){return value.poll(publication,lease);});}
extern "C" gboolean warlock_client_producer_resume(WarlockClientProducer* owner,guint64 publication,guint64 lease,char** events,GError** error) {return output(owner,events,error,[&](auto& value){return value.resume(publication,lease);});}
extern "C" guint64 warlock_client_producer_lease(WarlockClientProducer* owner) {return owner?owner->visit([](auto& value){return value.lease();}):0;}
extern "C" guint64 warlock_client_producer_request(WarlockClientProducer* owner) {return owner?owner->visit([](auto& value){return value.job().request.value;}):0;}
extern "C" gboolean warlock_client_producer_uri(WarlockClientProducer* owner,char** uri,GError** error) {return output(owner,uri,error,[](auto& value){return value.currentURI();});}
extern "C" gboolean warlock_client_producer_empty(WarlockClientProducer* owner) {return owner && owner->visit([](auto& value){return value.empty();});}
extern "C" gboolean warlock_client_producer_status(WarlockClientProducer* owner,char** status,GError** error) {return output(owner,status,error,[](auto& value){return value.status();});}
extern "C" gboolean warlock_client_producer_close(WarlockClientProducer* owner,GError** error) {
    if(!owner)return TRUE;
    try {preview::bridge::require(owner->visit([](auto& value){return value.close();}),"Outstanding physical client/journal ownership at host teardown");delete owner;return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}

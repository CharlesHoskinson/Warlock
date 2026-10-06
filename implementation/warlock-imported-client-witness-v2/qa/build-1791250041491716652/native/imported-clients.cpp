#include "imported-clients.h"
#include "imported_clients.hpp"
using namespace preview;using namespace preview::bridge;
struct WarlockImportedClients {
    ImportedClients value;
    uint64_t popup;
    std::array<Id<Incarnation>,2> subjects;
    std::string initial;
    WarlockImportedClients(Native& native,uint64_t popup,uint64_t first,uint64_t second,uint64_t publication,uint64_t lease):
        value(native),popup(popup),subjects{{{first},{second}}} {
        auto a=value.start(1,subjects[0],publication,lease);auto b=value.start(2,subjects[1],publication,lease);
        require(a.size()>2 && b.size()>2 && a.front()=='[' && a.back()==']' && b.front()=='[' && b.back()==']',"Actual shared imported seed/request arrays");
        a.pop_back();initial=a+","+b.substr(1);
        require(value.endpoint().registerView(popup,native.binding(),{1,2}),"Actual GTK receiver for shared imported ownership");
    }
    uint64_t entry(const char* identity)const {
        require(identity,"Typed own imported family identity");
        for(size_t i=0;i<subjects.size();++i)if(std::string_view(identity)=="family:"+std::to_string(subjects[i].value))return i+1;
        throw std::runtime_error("Foreign imported family identity");
    }
};
namespace {
template<class F> gboolean output(WarlockImportedClients* owner,char** result,GError** error,F call) {
    if(result)*result=nullptr;
    try {require(owner && result,"Own shared imported bridge output");*result=g_strdup(call(*owner).c_str());return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
}
extern "C" WarlockImportedClients* warlock_imported_clients_open(void* transport,gpointer popup,guint64 first,guint64 second,guint64 publication,guint64 lease,char** initial,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {
        require(transport && popup && first && second && first!=second && publication && lease && initial && endpoint,"Trusted shared imported GTK enrollment");
        auto owner=std::make_unique<WarlockImportedClients>(*static_cast<Native*>(transport),reinterpret_cast<uint64_t>(popup),first,second,publication,lease);
        *initial=g_strdup(owner->initial.c_str());*endpoint=&owner->value.endpoint();return owner.release();
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" gboolean warlock_imported_clients_command(WarlockImportedClients* owner,const char* identity,const char* command,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o){require(command,"Typed imported command text");return o.value.command(o.entry(identity),identity,command);});
}
extern "C" gboolean warlock_imported_clients_poll(WarlockImportedClients* owner,const char* identity,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o){return o.value.poll(o.entry(identity));});
}
extern "C" gboolean warlock_imported_clients_uri(WarlockImportedClients* owner,const char* identity,char** uriOutput,GError** error) {
    return output(owner,uriOutput,error,[&](auto& o){
        const auto entry=o.entry(identity);const auto packet=o.value.packet(entry);if(!packet)return std::string{};
        return o.value.endpoint().native([&](auto& broker){return broker.fetch(entry,packet->job.binding,packet->token)?uri::encode(packet->token):std::string{};});
    });
}
extern "C" gboolean warlock_imported_clients_status(WarlockImportedClients* owner,char** status,GError** error) {
    return output(owner,status,error,[](auto& o){return "["+o.value.status(1)+","+o.value.status(2)+"]";});
}
extern "C" gboolean warlock_imported_clients_empty(WarlockImportedClients* owner){return owner && owner->value.empty();}
extern "C" gboolean warlock_imported_clients_close(WarlockImportedClients* owner,GError** error) {
    if(!owner)return TRUE;
    try {require(owner->value.empty(),"Outstanding shared imported physical or journal ownership");owner->value.endpoint().unregisterView(owner->popup);delete owner;return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}

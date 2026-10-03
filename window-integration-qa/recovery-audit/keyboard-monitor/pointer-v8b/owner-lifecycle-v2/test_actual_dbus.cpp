#include "../native/PointerNotificationFence.hpp"
#include "../native/PointerLocatorState.hpp"
#include <cassert>
#include <cstdarg>
#include <iostream>
#include <memory>
#include <set>
#include <vector>
#include <dbus/dbus.h>
#include <chrono>
#include <thread>
constexpr auto PATH="/org/freedesktop/a11y/Manager",POINTER_IFACE="org.freedesktop.a11y.PointerLocator";
DBusConnection* bus=nullptr;
bool retiring=false,initializing=false;
uint64_t clockMs(){return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
bool sendPointer(DBusMessage* m){const bool sent=dbus_connection_send(bus,m,nullptr);dbus_message_unref(m);return sent;}
namespace Pointer {struct CPointerManager{PointerLocator::Point point{};auto position(){return point;}};}
using MotionFn=void(*)(Pointer::CPointerManager*);
void originalMotion(Pointer::CPointerManager*){}
struct Hook{void* m_original=reinterpret_cast<void*>(originalMotion);};Hook hook;Hook* motionHook=&hook;
PointerLocator::State pointerState;
PointerLocator::NotificationFence pointerFence;
std::map<std::string,uint64_t> pointerEpochs;
std::map<std::string,std::string> registrations;
std::map<uint64_t,DBusPendingCall*> pointerFenceCalls;
uint64_t nextPointerEpoch=0;
struct PointerQuery{};std::vector<std::unique_ptr<PointerQuery>> pointerQueries;
void queryError(PointerQuery&,const char*,const char*,bool){}
#include "actual_functions.inc"

const std::string name="org.actual.Fence.KeyboardMonitor";
unsigned received=0;
DBusHandlerResult ownerEvent(DBusConnection*,DBusMessage* m,void*) {
    if(!dbus_message_is_signal(m,DBUS_INTERFACE_DBUS,"NameOwnerChanged")||!dbus_message_has_sender(m,DBUS_SERVICE_DBUS))return DBUS_HANDLER_RESULT_NOT_YET_HANDLED;
    const char *changed=nullptr,*old=nullptr,*owner=nullptr;
    if(dbus_message_get_args(m,nullptr,DBUS_TYPE_STRING,&changed,DBUS_TYPE_STRING,&old,DBUS_TYPE_STRING,&owner,DBUS_TYPE_INVALID)&&name==changed){
        rotatePointerOwner(old);if(std::string(owner)!=old)rotatePointerOwner(owner);
        registrations.erase(changed);if(*owner)registrations[changed]=owner;reconcilePointerOwners();
    }
    return DBUS_HANDLER_RESULT_HANDLED;
}
DBusHandlerResult clientEvent(DBusConnection*,DBusMessage* m,void*){
    if(dbus_message_is_signal(m,POINTER_IFACE,"PointerPositionChanged")){++received;return DBUS_HANDLER_RESULT_HANDLED;}
    return DBUS_HANDLER_RESULT_NOT_YET_HANDLED;
}
void drain(DBusConnection* c){dbus_connection_read_write(c,0);for(unsigned n=0;n<32&&dbus_connection_get_dispatch_status(c)==DBUS_DISPATCH_DATA_REMAINS;++n)dbus_connection_dispatch(c);}
void cycle(DBusConnection* client,unsigned milliseconds){const auto end=clockMs()+milliseconds;do{drain(bus);if(dbus_connection_get_dispatch_status(bus)!=DBUS_DISPATCH_DATA_REMAINS)pollPointerNotifications();dbus_connection_flush(bus);drain(client);std::this_thread::sleep_for(std::chrono::milliseconds(1));}while(clockMs()<end);}
int main(){
    DBusError error;dbus_error_init(&error);
    bus=dbus_bus_get_private(DBUS_BUS_SESSION,&error);assert(bus);
    auto* client=dbus_bus_get_private(DBUS_BUS_SESSION,&error);assert(client);
    dbus_connection_set_exit_on_disconnect(bus,false);dbus_connection_set_exit_on_disconnect(client,false);
    dbus_connection_add_filter(bus,ownerEvent,nullptr,nullptr);dbus_connection_add_filter(client,clientEvent,nullptr,nullptr);
    dbus_bus_add_match(bus,"type='signal',sender='org.freedesktop.DBus',interface='org.freedesktop.DBus',member='NameOwnerChanged'",&error);
    dbus_bus_add_match(client,"type='signal',interface='org.freedesktop.a11y.PointerLocator',member='PointerPositionChanged'",&error);
    assert(!dbus_error_is_set(&error));
    assert(dbus_bus_request_name(client,name.c_str(),DBUS_NAME_FLAG_DO_NOT_QUEUE,&error)==DBUS_REQUEST_NAME_REPLY_PRIMARY_OWNER);
    const std::string sender=dbus_bus_get_unique_name(client);cycle(client,25);assert(pointerEpochs.contains(sender));
    Pointer::CPointerManager manager;
    assert(pointerState.replySent(sender,pointerEpochs.at(sender),{0,0}));manager.point={1,0};observeMotion(&manager);cycle(client,75);assert(received==1);
    for(unsigned index=0;index<20;++index){
        const auto old=pointerEpochs.at(sender);
        assert(pointerState.replySent(sender,old,manager.point));
        // Daemon has actually changed owner twice; do NOT dispatch bridge yet.
        assert(dbus_bus_release_name(client,name.c_str(),&error)==DBUS_RELEASE_NAME_REPLY_RELEASED);
        assert(dbus_bus_request_name(client,name.c_str(),DBUS_NAME_FLAG_DO_NOT_QUEUE,&error)==DBUS_REQUEST_NAME_REPLY_PRIMARY_OWNER);
        manager.point.x+=1;observeMotion(&manager);assert(pointerFence.notes.size()==1);
        // Real same-connection async method is started while local cache is old.
        pollPointerNotifications();assert(pointerFenceCalls.size()==1);cycle(client,50);
        assert(received==1+index&&pointerEpochs.at(sender)>old&&pointerFence.notes.empty()&&pointerFenceCalls.empty());
        assert(pointerState.replySent(sender,pointerEpochs.at(sender),manager.point));manager.point.x+=1;observeMotion(&manager);cycle(client,50);assert(received==2+index);
    }
    pointerRetire();dbus_connection_close(client);dbus_connection_unref(client);dbus_connection_close(bus);dbus_connection_unref(bus);bus=nullptr;
    std::cout<<"actual staged functions with real private D-Bus: valid directed signal + 20 loss/reclaim and fresh-rearm cycles PASS\n";
}

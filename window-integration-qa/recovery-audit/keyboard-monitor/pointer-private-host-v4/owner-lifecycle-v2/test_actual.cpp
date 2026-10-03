#include "../native/PointerNotificationFence.hpp"
#include "../native/PointerLocatorState.hpp"
#include <cassert>
#include <cstdarg>
#include <iostream>
#include <memory>
#include <set>
#include <vector>
using uint64_t=std::uint64_t;
constexpr auto DBUS_SERVICE_DBUS="org.freedesktop.DBus",DBUS_PATH_DBUS="/org/freedesktop/DBus",DBUS_INTERFACE_DBUS="org.freedesktop.DBus";
constexpr auto PATH="/org/freedesktop/a11y/Manager",POINTER_IFACE="org.freedesktop.a11y.PointerLocator",DBUS_ERROR_ACCESS_DENIED="denied";
constexpr int DBUS_TYPE_STRING=1,DBUS_TYPE_INVALID=0,DBUS_MESSAGE_TYPE_METHOD_RETURN=2,DBUS_DISPATCH_DATA_REMAINS=3;
struct DBusMessage{std::string value,destination;int type=DBUS_MESSAGE_TYPE_METHOD_RETURN;};
struct DBusPendingCall{bool completed=false;DBusMessage* reply=nullptr;};
struct DBusConnection{bool connected=true,backlog=false;};
DBusConnection connection;DBusConnection* bus=&connection;
bool retiring=false,initializing=false,allocationFails=false;
uint64_t nowMs=1000;int wireSends=0;std::vector<std::string> delivered;
uint64_t clockMs(){return nowMs;}
bool dbus_connection_get_is_connected(DBusConnection* c){return c->connected;}
int dbus_connection_get_dispatch_status(DBusConnection* c){return c->backlog?DBUS_DISPATCH_DATA_REMAINS:0;}
DBusMessage* dbus_message_new_method_call(const char*,const char*,const char*,const char*){return allocationFails?nullptr:new DBusMessage;}
DBusMessage* dbus_message_new_signal(const char*,const char*,const char*){return allocationFails?nullptr:new DBusMessage;}
void dbus_message_append_args(DBusMessage* m,int,const char** value,int){m->value=*value;}
void dbus_message_set_destination(DBusMessage* m,const char* value){m->destination=value;}
void dbus_message_unref(DBusMessage* m){delete m;}
bool dbus_connection_send_with_reply(DBusConnection*,DBusMessage*,DBusPendingCall** p,int timeout){assert(timeout>=1&&timeout<=500);*p=new DBusPendingCall;++wireSends;return true;}
void dbus_pending_call_cancel(DBusPendingCall*){}
void dbus_pending_call_unref(DBusPendingCall* p){if(p->reply)delete p->reply;delete p;}
bool dbus_pending_call_get_completed(DBusPendingCall* p){return p->completed;}
DBusMessage* dbus_pending_call_steal_reply(DBusPendingCall* p){auto r=p->reply;p->reply=nullptr;return r;}
int dbus_message_get_type(DBusMessage* m){return m->type;}
bool dbus_message_get_args(DBusMessage* m,void*,int,const char** value,int){*value=m->value.c_str();return true;}
bool sendPointer(DBusMessage* m){delivered.push_back(m->destination);delete m;return true;}
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
const std::string sender=":1.20",name="org.test.KeyboardMonitor";
Pointer::CPointerManager manager;
void reset(){pointerRetire();pointerState={};pointerFence={};pointerEpochs.clear();registrations={{name,sender}};nextPointerEpoch=0;connection={};retiring=false;allocationFails=false;nowMs=1000;wireSends=0;delivered.clear();manager.point={0,0};reconcilePointerOwners();}
void arm(){assert(pointerState.replySent(sender,pointerEpochs.at(sender),manager.point));}
void motion(){manager.point.x+=1;observeMotion(&manager);}
void reply(const std::string& owner=sender,bool error=false){for(auto& [id,p]:pointerFenceCalls){p->completed=true;p->reply=new DBusMessage{owner,{},error?9:DBUS_MESSAGE_TYPE_METHOD_RETURN};}}
void lossReclaim(){rotatePointerOwner(sender.c_str());registrations.erase(name);reconcilePointerOwners();registrations[name]=sender;rotatePointerOwner(sender.c_str());reconcilePointerOwners();}
int main(){
    // Actual hook queues only; actual timer starts one asynchronous lookup.
    reset();arm();motion();assert(delivered.empty()&&wireSends==0);pollPointerNotifications();assert(wireSends==1&&delivered.empty());reply();pollPointerNotifications();assert(delivered.size()==1&&pointerFence.notes.empty());motion();pollPointerNotifications();assert(delivered.size()==1);
    // Confirmed native causal ordering: pending arm, remote loss/reclaim,
    // real motion before local owner dispatch, lookup, earlier owner dispatch,
    // then same-unique reply. The old epoch must never emit.
    reset();arm();motion();pollPointerNotifications();lossReclaim();reply();pollPointerNotifications();assert(delivered.empty()&&pointerFenceCalls.empty());arm();motion();pollPointerNotifications();reply();pollPointerNotifications();assert(delivered.size()==1);
    // Alias still owned must not retain the previous pointer epoch.
    reset();registrations["org.alias.KeyboardMonitor"]=sender;arm();motion();pollPointerNotifications();const auto old=pointerEpochs.at(sender);rotatePointerOwner(sender.c_str());registrations.erase(name);reconcilePointerOwners();assert(pointerEpochs.at(sender)>old);reply();pollPointerNotifications();assert(delivered.empty());
    // A secondary alias changes to a different unique owner while the main
    // registration survives. Old pending authority still must be invalidated.
    reset();registrations["org.alias.KeyboardMonitor"]=sender;arm();motion();pollPointerNotifications();rotatePointerOwner(sender.c_str());rotatePointerOwner(":1.99");registrations["org.alias.KeyboardMonitor"]=":1.99";reconcilePointerOwners();reply();pollPointerNotifications();assert(delivered.empty()&&pointerEpochs.contains(sender)&&pointerEpochs.contains(":1.99"));
    // A completed fence cannot emit before the known owner backlog drains.
    reset();arm();motion();pollPointerNotifications();reply();connection.backlog=true;pollPointerNotifications();assert(delivered.empty());lossReclaim();connection.backlog=false;pollPointerNotifications();assert(delivered.empty());
    // Retirement after completion, including a queued late completion.
    reset();arm();motion();pollPointerNotifications();reply();connection.backlog=true;pollPointerNotifications();pointerRetire();connection.backlog=false;pollPointerNotifications();assert(delivered.empty()&&pointerFenceCalls.empty());assert(!pointerFence.complete(1,sender));
    // Session loss after a completed fence.
    reset();arm();motion();pollPointerNotifications();reply();connection.backlog=true;pollPointerNotifications();connection.connected=false;connection.backlog=false;pollPointerNotifications();assert(delivered.empty()&&pointerFence.notes.empty());
    // Deadline discards only its own note; another accepted arm survives.
    reset();arm();motion();pollPointerNotifications();nowMs+=1000;arm();motion();nowMs+=501;pollPointerNotifications();assert(pointerFence.notes.size()==1);reply();pollPointerNotifications();assert(delivered.size()==1);
    reset();arm();motion();pollPointerNotifications();reply({},true);pollPointerNotifications();assert(delivered.empty());
    reset();arm();motion();pollPointerNotifications();reply(":1.99");pollPointerNotifications();assert(delivered.empty());
    // Resource refusal retains all existing notes; 16 calls maximum.
    reset();for(unsigned i=0;i<512;++i)assert(pointerFence.capture(sender,pointerEpochs.at(sender),name,nowMs));assert(!pointerFence.reserve(0,0));assert(!pointerFence.capture(sender,pointerEpochs.at(sender),name,nowMs));assert(pointerFence.notes.size()==512);pollPointerNotifications();assert(pointerFenceCalls.size()==16&&wireSends==16);reply();pollPointerNotifications();assert(delivered.size()==16&&pointerFence.notes.size()==496&&pointerFenceCalls.size()<=16);
    // A saturated control queue still expires calls/notes on deadline,
    // without consuming a ready reply or sending a signal ahead of owners.
    reset();arm();motion();pollPointerNotifications();reply();connection.backlog=true;nowMs+=1500;pollPointerNotifications();assert(delivered.empty()&&pointerFence.notes.empty()&&pointerFenceCalls.empty());
    // Allocation failure and no-owner reply never authorize delivery.
    reset();arm();motion();allocationFails=true;pollPointerNotifications();assert(delivered.empty()&&pointerFence.notes.empty());
    reset();arm();motion();pollPointerNotifications();reply({});pollPointerNotifications();assert(delivered.empty());
    // Timer must not reset a valid prior pending arm on refusal.
    reset();arm();for(unsigned i=0;i<511;++i)assert(pointerFence.capture(sender,pointerEpochs.at(sender),name,nowMs));assert(!pointerFence.reserve(pointerState.pendingCount(),0));assert(pointerState.pendingCount()==1);
    pointerRetire();std::cout<<"actual staged functions: 15 scenarios PASS\n";
}

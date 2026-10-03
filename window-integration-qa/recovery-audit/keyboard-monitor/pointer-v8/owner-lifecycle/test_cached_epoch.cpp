#include <cassert>
#include <set>
#include <unordered_map>
#include <string>
#include <vector>
#include "../pointer-v7c/PointerLocatorState.hpp"
namespace Pointer { struct CPointerManager {PointerLocator::Point pos; auto position(){return pos;}}; }
struct DBusMessage {std::string recipient;};
struct Hook {void* m_original;};
void originalMotion(Pointer::CPointerManager*) {}
using MotionFn=void(*)(Pointer::CPointerManager*);
Hook originalHook{reinterpret_cast<void*>(originalMotion)};Hook* motionHook=&originalHook;
void* bus=reinterpret_cast<void*>(1);bool retiring=false,initializing=false;
const char* PATH="/org/freedesktop/a11y/Manager";
const char* POINTER_IFACE="org.freedesktop.a11y.PointerLocator";
PointerLocator::State pointerState;
std::unordered_map<std::string,std::string> registrations;
std::unordered_map<std::string,std::uint64_t> pointerEpochs;
std::uint64_t nextPointerEpoch=0;
std::vector<std::string> emitted;
DBusMessage* dbus_message_new_signal(const char*,const char*,const char*){return new DBusMessage;}
void dbus_message_set_destination(DBusMessage* m,const char* dest){m->recipient=dest;}
bool dbus_connection_send(void*,DBusMessage* m,void*){emitted.push_back(m->recipient);return true;}
void dbus_message_unref(DBusMessage* m){delete m;}
#include "actual-extracted-functions.cpp"
int main(){
 registrations["org.test.Actual.KeyboardMonitor"]=":1.3";reconcilePointerOwners();
 const auto epoch=pointerEpochs.at(":1.3");assert(pointerState.replySent(":1.3",epoch,{0,0}));
 // Actual daemon may already have released registration; its owner event is
 // queued for the compositor's separate timer, so cached state is unchanged.
 const bool daemonOwnerReleased=true;Pointer::CPointerManager manager{{1,0}};
 observeMotion(&manager);
 assert(daemonOwnerReleased && emitted==std::vector<std::string>{":1.3"});
 // If actual owner reconciliation occurs first, the same production helper
 // prevents the stale notification. No product policy is patched here.
 emitted.clear();registrations.clear();reconcilePointerOwners();manager.pos={2,0};observeMotion(&manager);
 assert(emitted.empty());
}

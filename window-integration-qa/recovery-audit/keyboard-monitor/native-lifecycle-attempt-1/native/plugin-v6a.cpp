// Offline/private candidate only. This file has never been loaded on the main compositor.
#include "key_policy.hpp"
#include "xkb_helpers.hpp"
#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/devices/IKeyboard.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <dbus/dbus.h>
#include <wayland-server-core.h>
#include <xkbcommon/xkbcommon.h>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <memory>
#include <stdexcept>
#include <sys/stat.h>
#include <unistd.h>

using namespace KeyboardMonitor;
namespace {
constexpr auto HASH="efb50993780079460b0cbed1363e2166a2de1d9f";
constexpr auto PATH="/org/freedesktop/a11y/Manager";
constexpr auto IFACE="org.freedesktop.a11y.KeyboardMonitor";
HANDLE handle=nullptr;
Policy policy;
bool retiring=false;
bool initializing=true;
DBusConnection* bus=nullptr;
wl_event_source* timer=nullptr;
std::map<std::string,std::string> registrations;
CFunctionHook *pressedHook=nullptr,*keyHook=nullptr,*maskHook=nullptr;
using PressedFn=bool(*)(IKeyboard*,uint32_t,bool);
using KeyFn=void(*)(CInputManager*,const IKeyboard::SKeyEvent&,SP<IKeyboard>);
using MaskFn=void(*)(IKeyboard*,uint32_t,uint32_t,uint32_t,uint32_t);
struct Device {
    xkb_keymap* map=nullptr;
    xkb_state *passed=nullptr,*captured=nullptr,*lookup=nullptr;
    VirtualMaskGuard virtualMask;
    uint32_t controlledLocks=0;
    bool passedDirty=false;
    bool mapDirty=false;
    bool lastPermission=true;
    bool mapBaselinePending=false;
    bool lockFiltering=false;
    Mask mapBaseline;
    std::map<std::pair<uint32_t,uint32_t>,uint32_t> lockBits;
    std::map<uint32_t,uint32_t> lockRoutes;
    std::map<uint32_t,Result> pending;
    CHyprSignalListener removed,keymap;
    Device(IKeyboard* kb):map(xkb_keymap_ref(kb->m_xkbKeymap)) {
        passed=xkb_state_new(map);captured=xkb_state_new(map);lookup=xkb_state_new(map);
        if(!passed||!captured||!lookup) throw std::runtime_error("XKB state allocation");
        // Reconstruct already accepted physical keys, so reader startup cannot
        // steal their matching release or clear their modifier contributions.
        for(auto key=xkb_keymap_min_keycode(map);key<=xkb_keymap_max_keycode(map);++key)
            if(key>=8&&kb->getPressed(key-8)) xkb_state_update_key(passed,key,XKB_KEY_DOWN);
        const auto n=kb->m_modifiersState;
        xkb_state_update_mask(passed,n.depressed,n.latched,n.locked,0,0,n.group);
    }
    ~Device(){if(passed)xkb_state_unref(passed);if(captured)xkb_state_unref(captured);if(lookup)xkb_state_unref(lookup);if(map)xkb_keymap_unref(map);}
    void refreshPassed(IKeyboard* kb) {
        // A passive service may have skipped ordinary input since last use.
        // Rebuild from native bookkeeping before handling this new packet.
        xkb_state_unref(passed);passed=xkb_state_new(map);
        if(!passed)throw std::runtime_error("XKB passed-state allocation");
        for(auto key=xkb_keymap_min_keycode(map);key<=xkb_keymap_max_keycode(map);++key)
            if(key>=8&&kb->getPressed(key-8))xkb_state_update_key(passed,key,XKB_KEY_DOWN);
        const auto n=kb->m_modifiersState;
        xkb_state_update_mask(passed,n.depressed,n.latched,n.locked,0,0,n.group);
        passedDirty=false;
    }
    void replaceMap(IKeyboard* kb) {
        const auto previous=kb->m_modifiersState;
        const auto priorCorrection=virtualMask.parity();
        auto* next=kb->m_xkbKeymap;
        const auto baselineLocks=kb->isVirtual()?remapModifiers(map,next,previous.locked):xkb_state_serialize_mods(kb->m_xkbState,XKB_STATE_MODS_LOCKED);
        const auto remappedCorrection=remapModifiers(map,next,priorCorrection);
        const auto baselineMask=kb->isVirtual()&&lockFiltering?remapModifiers(map,next,previous.locked|priorCorrection):0;
        mapBaseline={remapModifiers(map,next,previous.depressed),remapModifiers(map,next,previous.latched),baselineLocks,0};
        xkb_state_unref(passed);xkb_state_unref(captured);xkb_state_unref(lookup);xkb_keymap_unref(map);
        map=xkb_keymap_ref(kb->m_xkbKeymap);passed=xkb_state_new(map);captured=xkb_state_new(map);lookup=xkb_state_new(map);
        if(!passed||!captured||!lookup)throw std::runtime_error("XKB replacement allocation");
        refreshPassed(kb);
        xkb_state_update_mask(passed,mapBaseline.depressed,mapBaseline.latched,mapBaseline.locked,0,0,0);
        for(auto key:policy.capturedKeys(reinterpret_cast<uintptr_t>(kb)))xkb_state_update_key(captured,key+8,XKB_KEY_DOWN);
        xkb_state_update_mask(captured,xkb_state_serialize_mods(captured,XKB_STATE_MODS_DEPRESSED),0,0,0,0,kb->m_modifiersState.group);
        virtualMask.remapCorrection(remappedCorrection);controlledLocks=baselineMask;lockRoutes.clear();lockBits.clear();pending.clear();mapDirty=false;mapBaselinePending=kb->isVirtual();
        policy.resetTaps();
    }
    uint32_t keyLockBits(uint32_t key,uint32_t group) {
        const auto identity=std::pair{key,group};
        if(auto it=lockBits.find(identity);it!=lockBits.end())return it->second;
        const auto bits=KeyboardMonitor::keyLockBits(map,key,group);
        lockBits.emplace(identity,bits);return bits;
    }
};
std::map<IKeyboard*,std::unique_ptr<Device>> devices;
uint64_t clockMs(){return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
bool interested(){return !retiring&&!policy.clients.empty();}
bool unloadQuiescent() {
    if(!policy.quiescent())return false;
    for(const auto& [kb,d]:devices)if(kb->isVirtual()&&(d->virtualMask.parity()!=0||d->controlledLocks!=0||!d->lockRoutes.empty()||d->mapBaselinePending))return false;
    return true;
}
bool permitted(IKeyboard* kb){return kb&&kb->m_enabled&&kb->m_allowed&&(!kb->isVirtual()||!g_pInputManager->shouldIgnoreVirtualKeyboard(kb->m_self.lock()));}
void removeDevice(IKeyboard* kb){policy.removeDevice(reinterpret_cast<uintptr_t>(kb));devices.erase(kb);}
Device& getDevice(IKeyboard* kb) {
    if(auto it=devices.find(kb);it!=devices.end()) {
        if(it->second->mapDirty||it->second->map!=kb->m_xkbKeymap)it->second->replaceMap(kb);
        return *it->second;
    }
    auto owned=std::make_unique<Device>(kb);
    owned->removed=kb->m_events.destroy.listen([kb]{removeDevice(kb);});
    // Map replacement rebuilds symbolic state on the next key; hardware route
    // tombstones survive and use their original press keysym through release.
    owned->keymap=kb->m_keyboardEvents.keymap.listen([kb](const auto&){if(auto it=devices.find(kb);it!=devices.end())it->second->mapDirty=true;policy.resetTaps();});
    auto& result=*owned;devices.emplace(kb,std::move(owned));return result;
}
bool registered(const char* sender) {
    if(!sender) return false;
    for(const auto& [name,owner]:registrations) if(owner==sender) return true;
    return false;
}
bool monitorName(const std::string& name){return name.size()>16&&name.ends_with(".KeyboardMonitor")&&dbus_validate_bus_name(name.c_str(),nullptr);}
void prune(const std::string& owner){if(!registered(owner.c_str())) policy.drop(owner);}
void send(DBusMessage* m){if(!m)return;dbus_connection_send(bus,m,nullptr);dbus_message_unref(m);}
void reply(DBusMessage* m){send(dbus_message_new_method_return(m));}
void error(DBusMessage* m,const char* name,const char* why){send(dbus_message_new_error(m,name,why));}
void event(const Result& result,bool released,uint32_t state,uint32_t unicode,uint32_t key) {
    if(!bus||key+8>UINT16_MAX)return;
    for(const auto& recipient:result.recipients) {
        if(!registered(recipient.c_str()))continue;
        auto* m=dbus_message_new_signal(PATH,IFACE,"KeyEvent");if(!m)continue;
        dbus_message_set_destination(m,recipient.c_str());
        dbus_bool_t release=released;dbus_uint32_t mask=state,sym=result.sym,uni=unicode;dbus_uint16_t code=key+8;
        dbus_message_append_args(m,DBUS_TYPE_BOOLEAN,&release,DBUS_TYPE_UINT32,&mask,DBUS_TYPE_UINT32,&sym,DBUS_TYPE_UINT32,&uni,DBUS_TYPE_UINT16,&code,DBUS_TYPE_INVALID);send(m);
    }
}
bool onPressed(IKeyboard* kb,uint32_t key,bool press) {
    auto original=reinterpret_cast<PressedFn>(pressedHook->m_original);
    const auto identity=reinterpret_cast<uintptr_t>(kb);
    const bool allowed=permitted(kb);
    if(auto it=devices.find(kb);it!=devices.end()) {
        if(it->second->lastPermission!=allowed)policy.resetTaps();
        it->second->lastPermission=allowed;
    }
    if(!allowed||!kb->m_xkbKeymap||!kb->m_xkbState) {
        if(!policy.captured(identity,key))return original(kb,key,press);
        // Revocation cannot turn a captured press into an orphan native
        // release. Retain its routing while exposing no forbidden observation.
        auto result=policy.key(identity,key,0,0,press,clockMs(),1,false,false);
        if(auto it=devices.find(kb);it!=devices.end()) {
            it->second->pending[key]=result;
            if(!press&&it->second->captured) {
                xkb_state_update_key(it->second->captured,key+8,XKB_KEY_UP);
                it->second->controlledLocks|=it->second->lockRoutes[key];
                it->second->lockRoutes.erase(key);
            }
        }
        return false;
    }
    // No subscription: the original code handles every new packet unchanged.
    if(!interested()&&!policy.captured(reinterpret_cast<uintptr_t>(kb),key)) {
        if(auto it=devices.find(kb);it!=devices.end())it->second->passedDirty=true;
        return original(kb,key,press);
    }
    auto& d=getDevice(kb);if(d.passedDirty)d.refreshPassed(kb);auto native=kb->m_modifiersState;
    if(d.mapBaselinePending){native.depressed=d.mapBaseline.depressed;native.latched=d.mapBaseline.latched;native.locked=d.mapBaseline.locked;native.group=d.mapBaseline.group;}
    uint32_t capturedLockBits=0;
    for(auto held:policy.capturedKeys(reinterpret_cast<uintptr_t>(kb)))capturedLockBits|=d.keyLockBits(held,native.group);
    const auto packet=packetBeforeKey(d.lookup,d.captured,{native.depressed,native.latched,native.locked,native.group},key,capturedLockBits);
    const auto sym=packet.sym,state=packet.state;
    const auto device=reinterpret_cast<uintptr_t>(kb);
    const bool known=policy.known(device,key),alreadyNative=kb->getPressed(key);
    auto result=policy.key(device,key,sym,state,press,clockMs(),std::max(kb->m_repeatDelay,1),alreadyNative);
    d.pending[key]=result;
    auto shadow=result.consumed?d.captured:d.passed;
    const auto before=xkb_state_serialize_mods(shadow,XKB_STATE_MODS_LOCKED);
    // Like native updatePressed, a repeat/unmatched release must not change
    // XKB key counts. Captured repeat packets still reach the reader.
    if(press?(!known&&!alreadyNative):(known||alreadyNative))
        xkb_state_update_key(shadow,key+8,press?XKB_KEY_DOWN:XKB_KEY_UP);
    const auto changedLocks=before^xkb_state_serialize_mods(shadow,XKB_STATE_MODS_LOCKED);
    const auto semanticLocks=d.keyLockBits(key,native.group);
    if(result.consumed&&semanticLocks)d.lockFiltering=true;
    if(press&&semanticLocks)d.lockRoutes[key]=semanticLocks;
    if(d.lockFiltering)d.controlledLocks|=changedLocks|d.lockRoutes[key];
    if(!press)d.lockRoutes.erase(key);
    if(result.consumed) {
        xkb_state_update_mask(shadow,xkb_state_serialize_mods(shadow,XKB_STATE_MODS_DEPRESSED),xkb_state_serialize_mods(shadow,XKB_STATE_MODS_LATCHED),0,0,0,native.group);
    }
    // Consistent pre-event mask and lookup convention. Shadow transitions are
    // for the next packet/filter only. Queueing never waits on a client.
    event(result,!press,state,xkb_keysym_to_utf32(result.sym),key);
    if(result.consumed)return false; // physical callback skips XKB update
    return original(kb,key,press);
}
void onKey(CInputManager* input,const IKeyboard::SKeyEvent& ev,SP<IKeyboard> kb) {
    if(auto it=devices.find(kb.get());it!=devices.end()) {
        auto packet=it->second->pending.find(ev.keycode);
        if(packet!=it->second->pending.end()) {bool consumed=packet->second.consumed;it->second->pending.erase(packet);if(consumed)return;}
    }
    reinterpret_cast<KeyFn>(keyHook->m_original)(input,ev,kb);
}
void onMask(IKeyboard* kb,uint32_t depressed,uint32_t latched,uint32_t locked,uint32_t group) {
    auto original=reinterpret_cast<MaskFn>(maskHook->m_original);
    if(!kb||!kb->isVirtual()) {original(kb,depressed,latched,locked,group);return;}
    auto it=devices.find(kb);
    if(it==devices.end()){original(kb,depressed,latched,locked,group);return;}
    if(!kb->m_xkbKeymap||!kb->m_xkbState){original(kb,depressed,latched,locked,group);return;}
    // Modifier packets may be the first event after a virtual keymap change.
    auto& d=getDevice(kb);
    const auto captured=xkb_state_serialize_mods(d.captured,XKB_STATE_MODS_DEPRESSED);
    const auto passed=xkb_state_serialize_mods(d.passed,XKB_STATE_MODS_DEPRESSED);
    bool full=false;if(permitted(kb))for(const auto& [id,c]:policy.clients)full|=c.full;
    auto n=kb->m_modifiersState;
    auto filtered=d.virtualMask.filter({depressed,latched,locked,group},{n.depressed,n.latched,n.locked,n.group},captured&~passed,d.controlledLocks,full,xkb_state_serialize_mods(d.passed,XKB_STATE_MODS_LOCKED));
    d.controlledLocks=0;
    d.mapBaselinePending=false;
    xkb_state_update_mask(d.passed,filtered.depressed,filtered.latched,filtered.locked,0,0,filtered.group);
    original(kb,filtered.depressed,filtered.latched,filtered.locked,filtered.group);
    if(d.virtualMask.parity()==0&&d.lockRoutes.empty()&&policy.capturedKeys(reinterpret_cast<uintptr_t>(kb)).empty())d.lockFiltering=false;
}
DBusHandlerResult dispatch(DBusConnection*,DBusMessage* m,void*) {
    if(dbus_message_is_signal(m,DBUS_INTERFACE_DBUS,"NameOwnerChanged")&&dbus_message_has_sender(m,DBUS_SERVICE_DBUS)) {
        const char *name=nullptr,*old=nullptr,*owner=nullptr;
        if(dbus_message_get_args(m,nullptr,DBUS_TYPE_STRING,&name,DBUS_TYPE_STRING,&old,DBUS_TYPE_STRING,&owner,DBUS_TYPE_INVALID)) {
            if(monitorName(name)){registrations.erase(name);if(*owner)registrations[name]=owner;prune(old);policy.resetTaps();}
            else if(*name==':'&&!*owner) {for(auto it=registrations.begin();it!=registrations.end();)if(it->second==name)it=registrations.erase(it);else ++it;policy.drop(name);}
        }
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if(dbus_message_get_type(m)!=DBUS_MESSAGE_TYPE_METHOD_CALL||std::string(dbus_message_get_path(m)?dbus_message_get_path(m):"")!=PATH)return DBUS_HANDLER_RESULT_NOT_YET_HANDLED;
    const char* sender=dbus_message_get_sender(m);
    if(dbus_message_is_method_call(m,DBUS_INTERFACE_INTROSPECTABLE,"Introspect")) {
        constexpr const char* xml="<node><interface name='org.freedesktop.a11y.KeyboardMonitor'><method name='WatchKeyboard'/><method name='UnwatchKeyboard'/><method name='GrabKeyboard'/><method name='UngrabKeyboard'/><method name='SetKeyGrabs'><arg type='au' direction='in'/><arg type='a(uu)' direction='in'/></method><signal name='KeyEvent'><arg type='b'/><arg type='u'/><arg type='u'/><arg type='u'/><arg type='q'/></signal></interface><interface name='org.omarchy.KeyboardMonitorProbe'><method name='State'><arg type='s' direction='out'/></method><method name='PrepareUnload'><arg type='b' direction='out'/></method></interface></node>";
        auto* r=dbus_message_new_method_return(m);dbus_message_append_args(r,DBUS_TYPE_STRING,&xml,DBUS_TYPE_INVALID);send(r);return DBUS_HANDLER_RESULT_HANDLED;
    }
    if(dbus_message_has_interface(m,"org.omarchy.KeyboardMonitorProbe")) {
        if(dbus_message_has_member(m,"PrepareUnload")) {
            dbus_bool_t ready=unloadQuiescent();if(ready){retiring=true;policy.stop();}
            auto* r=dbus_message_new_method_return(m);dbus_message_append_args(r,DBUS_TYPE_BOOLEAN,&ready,DBUS_TYPE_INVALID);send(r);return DBUS_HANDLER_RESULT_HANDLED;
        }
        if(dbus_message_has_member(m,"State")) {
            const auto value=std::string("{\"retiring\":")+(retiring?"true":"false")+",\"unloadQuiescent\":"+(unloadQuiescent()?"true":"false")+",\"registrations\":"+std::to_string(registrations.size())+",\"clients\":"+std::to_string(policy.clients.size())+",\"devices\":"+std::to_string(devices.size())+",\"quiescent\":"+(policy.quiescent()?"true":"false")+",\"nativeInputProved\":false}";
            const char* s=value.c_str();auto* r=dbus_message_new_method_return(m);dbus_message_append_args(r,DBUS_TYPE_STRING,&s,DBUS_TYPE_INVALID);send(r);return DBUS_HANDLER_RESULT_HANDLED;
        }
    }
    if(!dbus_message_has_interface(m,IFACE)) {error(m,DBUS_ERROR_UNKNOWN_INTERFACE,"keyboard-only staged service");return DBUS_HANDLER_RESULT_HANDLED;}
    if(retiring||initializing){error(m,"org.freedesktop.a11y.ServiceRetired","service incarnation is not accepting subscriptions");return DBUS_HANDLER_RESULT_HANDLED;}
    if(!registered(sender)){error(m,DBUS_ERROR_ACCESS_DENIED,"caller must own its KeyboardMonitor registration");return DBUS_HANDLER_RESULT_HANDLED;}
    auto& c=policy.clients[sender];
    if(dbus_message_has_member(m,"WatchKeyboard")&&dbus_message_has_signature(m,""))c.watch=true;
    else if(dbus_message_has_member(m,"UnwatchKeyboard")&&dbus_message_has_signature(m,""))c.watch=false;
    else if(dbus_message_has_member(m,"GrabKeyboard")&&dbus_message_has_signature(m,"")){c.full=true;policy.resetTaps();}
    else if(dbus_message_has_member(m,"UngrabKeyboard")&&dbus_message_has_signature(m,"")){c.full=false;policy.resetTaps();}
    else if(dbus_message_has_member(m,"SetKeyGrabs")&&dbus_message_has_signature(m,"aua(uu)")) {
        DBusMessageIter args,array,entry;dbus_message_iter_init(m,&args);dbus_message_iter_recurse(&args,&array);
        Client next=c;next.modifiers.clear();next.strokes.clear();
        while(dbus_message_iter_get_arg_type(&array)!=DBUS_TYPE_INVALID){uint32_t v;dbus_message_iter_get_basic(&array,&v);next.modifiers.insert(v);dbus_message_iter_next(&array);}
        dbus_message_iter_next(&args);dbus_message_iter_recurse(&args,&array);
        while(dbus_message_iter_get_arg_type(&array)!=DBUS_TYPE_INVALID){uint32_t sym,mask;dbus_message_iter_recurse(&array,&entry);dbus_message_iter_get_basic(&entry,&sym);dbus_message_iter_next(&entry);dbus_message_iter_get_basic(&entry,&mask);next.strokes.insert({sym,mask});dbus_message_iter_next(&array);}
        c=std::move(next);policy.resetTaps();
    } else {error(m,DBUS_ERROR_INVALID_ARGS,"unknown method or signature");return DBUS_HANDLER_RESULT_HANDLED;}
    if(!c.watch&&!c.full&&c.modifiers.empty()&&c.strokes.empty())policy.clients.erase(sender);
    reply(m);return DBUS_HANDLER_RESULT_HANDLED;
}
int poll(void*) {
    if(!bus)return 0;
    if(!dbus_connection_read_write(bus,0)||!dbus_connection_get_is_connected(bus))policy.stop();
    else for(unsigned int budget=0;budget<32&&dbus_connection_get_dispatch_status(bus)==DBUS_DISPATCH_DATA_REMAINS;++budget)dbus_connection_dispatch(bus);
    wl_event_source_timer_update(timer,5);return 0;
}
void cleanup() {
    if(timer){wl_event_source_remove(timer);timer=nullptr;}
    if(bus){dbus_connection_remove_filter(bus,dispatch,nullptr);dbus_connection_close(bus);dbus_connection_unref(bus);bus=nullptr;}
    policy.stop();devices.clear();registrations.clear();
}
void hook(CFunctionHook*& output,const char* name,void* target) {
    auto matches=HyprlandAPI::findFunctionsByName(handle,name);
    if(matches.size()!=1)throw std::runtime_error(std::string("non-unique ABI target: ")+name);
    output=HyprlandAPI::createFunctionHook(handle,matches.front().address,target);
    if(!output||!output->hook())throw std::runtime_error(std::string("hook failed: ")+name);
}
}
APICALL EXPORT std::string PLUGIN_API_VERSION(){return HYPRLAND_API_VERSION;}
APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE h) {
    handle=h;
    const char* enabled=getenv("HYPR_A11Y_BRIDGE_PRIVATE");const char* runtime=getenv("XDG_RUNTIME_DIR");
    const char* address=getenv("DBUS_SESSION_BUS_ADDRESS");
    struct stat st{};
    if(!enabled||std::string(enabled)!="1"||!runtime||!std::string(runtime).starts_with("/tmp/kbn-")||stat(runtime,&st)||st.st_uid!=getuid()||(st.st_mode&0777)!=0700)
        throw std::runtime_error("candidate restricted to explicit private keyboard-native runtime");
    const auto expected=std::string("unix:path=")+runtime+"/bus";
    const auto configured=address?std::string(address):std::string();
    struct stat socketStat{};
    if((configured!=expected&&!configured.starts_with(expected+","))||lstat((std::string(runtime)+"/bus").c_str(),&socketStat)||!S_ISSOCK(socketStat.st_mode)||socketStat.st_uid!=getuid())
        throw std::runtime_error("candidate requires its own D-Bus socket inside private runtime");
    if(HyprlandAPI::getHyprlandVersion(handle).hash!=HASH)throw std::runtime_error("exact Hyprland ABI mismatch");
    try {
        DBusError err;dbus_error_init(&err);
        bus=dbus_bus_get_private(DBUS_BUS_SESSION,&err);
        if(!bus){std::string why=err.message?err.message:"private D-Bus unavailable";dbus_error_free(&err);throw std::runtime_error(why);}
        dbus_connection_set_exit_on_disconnect(bus,false);
        // Subscribe before snapshot; never infer client policy from names.
        // The service name is claimed only after bounded owner reconciliation.
        retiring=false;initializing=true;
        dbus_bus_add_match(bus,"type='signal',sender='org.freedesktop.DBus',interface='org.freedesktop.DBus',member='NameOwnerChanged'",&err);
        if(dbus_error_is_set(&err)){std::string why=err.message;dbus_error_free(&err);throw std::runtime_error(why);}
        if(!dbus_connection_add_filter(bus,dispatch,nullptr,nullptr))throw std::runtime_error("D-Bus filter allocation");
        const auto deadline=clockMs()+1500;
        auto call=[&](const char* method,const char* arg=nullptr) {
            if(clockMs()>=deadline)throw std::runtime_error("registration adoption deadline");
            auto* request=dbus_message_new_method_call(DBUS_SERVICE_DBUS,DBUS_PATH_DBUS,DBUS_INTERFACE_DBUS,method);
            if(!request)throw std::runtime_error("registration request allocation");
            if(arg)dbus_message_append_args(request,DBUS_TYPE_STRING,&arg,DBUS_TYPE_INVALID);
            const auto now=clockMs();
            if(now>=deadline){dbus_message_unref(request);throw std::runtime_error("registration adoption deadline");}
            // Capture time once, then check before unsigned subtraction and
            // bounded signed conversion. Never pass zero/default infinity.
            const int timeout=static_cast<int>(std::clamp<uint64_t>(deadline-now,1,500));
            auto* response=dbus_connection_send_with_reply_and_block(bus,request,timeout,&err);
            dbus_message_unref(request);
            if(!response&&dbus_error_is_set(&err)&&dbus_error_has_name(&err,DBUS_ERROR_NAME_HAS_NO_OWNER)){dbus_error_free(&err);return response;}
            if(!response){std::string why=err.message?err.message:"registration response unavailable";dbus_error_free(&err);throw std::runtime_error(why);}
            return response;
        };
        auto* namesReply=call("ListNames");
        char** names=nullptr;int count=0;
        if(!dbus_message_get_args(namesReply,&err,DBUS_TYPE_ARRAY,DBUS_TYPE_STRING,&names,&count,DBUS_TYPE_INVALID)){
            dbus_message_unref(namesReply);dbus_error_free(&err);throw std::runtime_error("invalid registration enumeration");
        }
        std::vector<std::string> candidates;
        for(int i=0;i<count;++i)if(monitorName(names[i]))candidates.emplace_back(names[i]);
        dbus_free_string_array(names);dbus_message_unref(namesReply);
        if(candidates.size()>256)throw std::runtime_error("registration adoption budget exceeded");
        for(const auto& name:candidates) {
            auto* response=call("GetNameOwner",name.c_str());if(!response)continue;
            const char* owner=nullptr;
            if(dbus_message_get_args(response,nullptr,DBUS_TYPE_STRING,&owner,DBUS_TYPE_INVALID)&&owner&&*owner)registrations[name]=owner;
            dbus_message_unref(response);
        }
        // Signals queued around synchronous snapshots restore their bus order
        // before availability. Floods fail initialization rather than stall.
        unsigned dispatches=0;
        do {
            dbus_connection_read_write(bus,0);
            while(dbus_connection_get_dispatch_status(bus)==DBUS_DISPATCH_DATA_REMAINS) {
                if(++dispatches>1024||clockMs()>=deadline)throw std::runtime_error("owner reconciliation budget exceeded");
                dbus_connection_dispatch(bus);
            }
        } while(dbus_connection_read_write(bus,0)&&dbus_connection_get_dispatch_status(bus)==DBUS_DISPATCH_DATA_REMAINS);
        const int result=dbus_bus_request_name(bus,"org.freedesktop.a11y.Manager",DBUS_NAME_FLAG_DO_NOT_QUEUE,&err);
        if(result!=DBUS_REQUEST_NAME_REPLY_PRIMARY_OWNER)throw std::runtime_error("manager already owned or unavailable");
        initializing=false;
        hook(pressedHook,"_ZN9IKeyboard13updatePressedEjb",reinterpret_cast<void*>(onPressed));
        hook(keyHook,"_ZN13CInputManager13onKeyboardKeyERKN9IKeyboard9SKeyEventEN9Hyprutils6Memory14CSharedPointerIS0_EE",reinterpret_cast<void*>(onKey));
        hook(maskHook,"_ZN9IKeyboard15updateModifiersEjjjj",reinterpret_cast<void*>(onMask));
        timer=wl_event_loop_add_timer(g_pCompositor->m_wlEventLoop,poll,nullptr);
        if(!timer)throw std::runtime_error("Wayland dispatch timer allocation");
        wl_event_source_timer_update(timer,5);
    } catch(...) {
        for(auto* entry:{pressedHook,keyHook,maskHook})if(entry)HyprlandAPI::removeFunctionHook(handle,entry);
        pressedHook=keyHook=maskHook=nullptr;cleanup();throw;
    }
    return {"keyboard-monitor-private","Exact ABI keyboard monitor isolated candidate","local parity QA","0.6-private-retirement"};
}
APICALL EXPORT void PLUGIN_EXIT() {
    // PrepareUnload is the normal quiescence precondition. Accepted keys stay
    // in Hyprland and receive their natural releases; no synthetic duplicates.
    // Forced/error unload while captured keys are held is explicitly unproved.
    cleanup();
}

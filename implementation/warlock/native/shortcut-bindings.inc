// Fixed route/chord authority. Foreign bindings are never removed or disabled.
struct ShortcutSpec { const char* route; const char* label; const char* dispatcher; const char* key; xkb_keysym_t symbol; uint32_t code; const char* modifiers; const char* alternateModifiers; const char* chord; const char* alternateChord; ShellRoute routeValue; };
const std::array<ShortcutSpec,3> shortcutSpecs = {{
    {"applications","Apps menu","warlock_apps_menu","SPACE",XKB_KEY_space,57,"SUPER ALT","SUPER CTRL ALT","SUPER + ALT + SPACE","SUPER + CTRL + ALT + SPACE",ShellRoute::Applications},
    {"system","System menu","warlock_system_menu","ESCAPE",XKB_KEY_Escape,1,"SUPER","SUPER CTRL","SUPER + ESCAPE","SUPER + CTRL + ESCAPE",ShellRoute::System},
    {"notifications","Notification history","warlock_notification_history","comma",XKB_KEY_comma,51,"SUPER SHIFT ALT","SUPER CTRL ALT","SUPER + SHIFT + ALT + comma","SUPER + CTRL + ALT + comma",ShellRoute::Notifications}
}};
std::array<SP<SKeybind>,3> ownedShortcutBindings;
uint64_t shortcutConfigurationRevision=1;
struct ShortcutApplyReceipt { uint64_t request=0; std::string proposal; std::string reply; };
std::map<std::string,ShortcutApplyReceipt> shortcutApplyReceipts;
bool shortcutOwned(const SP<SKeybind>& binding) {
    return std::ranges::any_of(ownedShortcutBindings,[&](const auto& owned){return owned && owned==binding;});
}
bool shortcutPresent(const SP<SKeybind>& binding) {
    return binding && std::ranges::find(g_pKeybindManager->m_keybinds,binding)!=g_pKeybindManager->m_keybinds.end();
}
bool shortcutFree(size_t index,bool alternate) {
    if(!g_pKeybindManager || g_pKeybindManager->m_keybinds.size()>4096)return false;
    const auto& spec=shortcutSpecs[index];const auto mask=g_pKeybindManager->stringToModMask(alternate?spec.alternateModifiers:spec.modifiers);
    for(const auto& bind:g_pKeybindManager->m_keybinds) {
        if(!bind || !bind->enabled || shortcutOwned(bind))continue;
        // Device/submap/release/transparent bindings are preserved too. A
        // multikey/catchall is conservatively unavailable; no alias is guessed.
        const bool key=bind->catchAll || bind->multiKey || xkb_keysym_from_name(bind->key.c_str(),XKB_KEYSYM_CASE_INSENSITIVE)==spec.symbol || bind->keycode==spec.code+8 || bind->keycode==spec.code;
        if(key && (bind->ignoreMods || bind->multiKey || bind->modmask==mask))return false;
    }
    return true;
}
std::string shortcutFingerprint() {
    if(!g_pKeybindManager || g_pKeybindManager->m_keybinds.size()>4096)throw std::runtime_error("Shortcut inventory unavailable");
    std::string bytes=std::to_string(shortcutConfigurationRevision)+"\n";
    for(const auto& bind:g_pKeybindManager->m_keybinds) {
        if(!bind || shortcutOwned(bind))continue;
        std::string flags;
        for(bool flag:{bind->enabled,bind->catchAll,bind->locked,bind->release,bind->repeat,bind->longPress,bind->mouse,bind->nonConsuming,bind->autoConsuming,bind->transparent,bind->ignoreMods,bind->multiKey,bind->dontInhibit,bind->click,bind->drag,bind->submapUniversal,bind->deviceInclusive,bind->allowInputCapture})flags+=flag?'1':'0';
        bytes+=quote(bind->key)+":"+std::to_string(bind->keycode)+":"+std::to_string(bind->modmask)+":"+quote(bind->handler)+":"+quote(bind->arg)+":"+quote(bind->submap.name)+":"+flags+":";
        for(auto [symbol,code]:bind->sMkKeys)bytes+=std::to_string(symbol)+","+std::to_string(code)+";";
        bytes+=':';for(auto [symbol,code]:bind->sMkMods)bytes+=std::to_string(symbol)+","+std::to_string(code)+";";
        std::vector<std::string> devices(bind->devices.begin(),bind->devices.end());std::ranges::sort(devices);for(const auto& device:devices)bytes+=quote(device);bytes+='\n';
        if(bytes.size()>1048576)throw std::runtime_error("Shortcut inventory capacity");
    }
    auto* hash=g_compute_checksum_for_data(G_CHECKSUM_SHA256,reinterpret_cast<const guchar*>(bytes.data()),bytes.size());
    if(!hash)throw std::runtime_error("Shortcut fingerprint unavailable");
    std::string result=hash;g_free(hash);return result;
}
std::string shortcutInventory() {
    std::string result="{\"fingerprint\":"+quote(shortcutFingerprint());
    for(size_t i=0;i<shortcutSpecs.size();++i) {
        const auto& spec=shortcutSpecs[i];const bool normal=shortcutFree(i,false),alternate=shortcutFree(i,true);
        const auto& owned=ownedShortcutBindings[i];std::string active="keep";
        if(shortcutPresent(owned) && owned->enabled){if(owned->modmask==g_pKeybindManager->stringToModMask(spec.modifiers) && normal)active="default";else if(owned->modmask==g_pKeybindManager->stringToModMask(spec.alternateModifiers) && alternate)active="alternate";}
        result+=","+quote(spec.route)+":{\"defaultChord\":"+quote(spec.chord)+",\"alternateChord\":"+quote(spec.alternateChord)+",\"defaultAvailable\":"+(normal?"true":"false")+",\"alternateAvailable\":"+(alternate?"true":"false")+",\"active\":"+quote(active)+"}";
    }
    return result+"}";
}
SP<SKeybind> shortcutCreate(size_t i,bool alternate) {
    const auto& spec=shortcutSpecs[i];SKeybind key{};key.key=spec.key;key.modmask=g_pKeybindManager->stringToModMask(alternate?spec.alternateModifiers:spec.modifiers);key.handler=spec.dispatcher;key.description=spec.label;key.hasDescription=true;key.displayKey=alternate?spec.alternateChord:spec.chord;
    return g_pKeybindManager->addKeybind(key);
}
void retireShortcutBindings() noexcept {
    if(g_pKeybindManager)for(const auto& owned:ownedShortcutBindings)if(owned)std::erase(g_pKeybindManager->m_keybinds,owned);
    ownedShortcutBindings={};shortcutApplyReceipts.clear();
}
void registerShortcutBindings(HANDLE handle) {
    retireShortcutBindings();
    for(size_t i=0;i<shortcutSpecs.size();++i) {
        const auto& spec=shortcutSpecs[i];
        if(!HyprlandAPI::addDispatcherV2(handle,spec.dispatcher,[i](std::string){
            const auto& owned=ownedShortcutBindings[i];
            if(shortcutPresent(owned) && owned->enabled && shortcutFree(i,owned->modmask==g_pKeybindManager->stringToModMask(shortcutSpecs[i].alternateModifiers)))shellShortcut(shortcutSpecs[i].routeValue);
            return SDispatchResult{};
        }))throw std::runtime_error("Shortcut dispatcher registration failed");
        // The approved default is installed only when the live chord is free.
        if(shortcutFree(i,false))ownedShortcutBindings[i]=shortcutCreate(i,false);
    }
}
std::string shortcutBindingsReply(const Session& session,uint64_t request,const char* kind,const char* status=nullptr) {
    return "{\"protocolVersion\":3,\"kind\":"+quote(kind)+",\"binding\":"+binding(session)+",\"requestId\":"+quote(std::to_string(request))+(status?",\"status\":"+quote(status):"")+",\"inventory\":"+shortcutInventory()+"}";
}
std::string applyShortcutBindings(const Session& session,uint64_t request,JsonObject* choices,const std::string& fingerprint) {
    std::array<std::string,3> selected;std::string proposal=fingerprint;
    for(size_t i=0;i<shortcutSpecs.size();++i){auto* node=json_object_get_member(choices,shortcutSpecs[i].route);std::string value=node && json_node_get_value_type(node)==G_TYPE_STRING?json_node_get_string(node):"";if(value!="keep" && value!="default" && value!="alternate")return error("shortcut-choice");selected[i]=value;proposal+=":"+value;}
    auto key=binding(session);auto found=shortcutApplyReceipts.find(key);
    if(found!=shortcutApplyReceipts.end() && request<=found->second.request){if(request==found->second.request && found->second.proposal==proposal)return found->second.reply;return error("shortcut-request-retired");}
    if(found==shortcutApplyReceipts.end() && shortcutApplyReceipts.size()>=64)return error("shortcut-receipt-capacity");
    auto finish=[&](const char* status){auto reply=shortcutBindingsReply(session,request,"shortcut-bindings-outcome",status);shortcutApplyReceipts[key]={request,proposal,reply};return reply;};
    if(shortcutConfigurationRevision==std::numeric_limits<uint64_t>::max() || fingerprint!=shortcutFingerprint() || g_pSessionLockManager->isSessionLocked() || g_layoutManager->dragController()->target())return finish("Refused");
    for(size_t i=0;i<selected.size();++i)if(selected[i]!="keep" && !shortcutFree(i,selected[i]=="alternate"))return finish("Refused");
    std::array<SP<SKeybind>,3> prepared;
    try {
        for(size_t i=0;i<selected.size();++i)if(selected[i]!="keep"){prepared[i]=shortcutCreate(i,selected[i]=="alternate");if(!prepared[i])throw std::runtime_error("Shortcut installation failed");}
    } catch(...) {
        for(const auto& owned:prepared)if(owned)std::erase(g_pKeybindManager->m_keybinds,owned);
        return finish("Refused");
    }
    for(const auto& owned:ownedShortcutBindings)if(owned)std::erase(g_pKeybindManager->m_keybinds,owned);
    ownedShortcutBindings=prepared;++shortcutConfigurationRevision;
    return finish("Applied");
}

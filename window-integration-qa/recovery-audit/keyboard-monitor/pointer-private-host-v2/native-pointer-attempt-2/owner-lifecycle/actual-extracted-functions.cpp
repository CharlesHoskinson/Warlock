bool registered(const char* sender) {
    if(!sender) return false;
    for(const auto& [name,owner]:registrations) if(owner==sender) return true;
    return false;
}
void send(DBusMessage* m){if(!m)return;dbus_connection_send(bus,m,nullptr);dbus_message_unref(m);}
void reconcilePointerOwners() {
    std::set<std::string> current;
    for(const auto& [name,owner]:registrations)current.insert(owner);
    for(auto it=pointerEpochs.begin();it!=pointerEpochs.end();) {
        if(!current.contains(it->first)){pointerState.disconnect(it->first,it->second);it=pointerEpochs.erase(it);}
        else ++it;
    }
    for(const auto& owner:current)if(!pointerEpochs.contains(owner)) {
        const auto epoch=++nextPointerEpoch;
        if(pointerState.claim(owner,epoch))pointerEpochs.emplace(owner,epoch);
    }
}
void observeMotion(Pointer::CPointerManager* manager) {
    reinterpret_cast<MotionFn>(motionHook->m_original)(manager);
    if(!bus||retiring||initializing)return;
    const auto pos=manager->position();
    for(const auto& note:pointerState.motion({pos.x,pos.y})) {
        if(!pointerState.authorized(note.sender,note.epoch)||!registered(note.sender.c_str()))continue;
        auto* message=dbus_message_new_signal(PATH,POINTER_IFACE,"PointerPositionChanged");
        if(message){dbus_message_set_destination(message,note.sender.c_str());send(message);}
    }
}

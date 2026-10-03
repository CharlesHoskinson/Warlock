// Exact staged production-function bodies; deterministic transport adapter below.
void rotatePointerOwner(const char* owner) {
    if(!owner||!*owner)return;
    const auto found=pointerEpochs.find(owner);
    if(found==pointerEpochs.end())return;
    pointerState.disconnect(found->first,found->second);pointerEpochs.erase(found);
}

std::string pointerRegistration(const std::string& sender) {
    for(const auto& [name,owner]:registrations)if(owner==sender)return name;
    return {};
}

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
        if(!pointerState.authorized(note.sender,note.epoch))continue;
        // No IPC, synchronous owner lookup, or signal emission in this hook.
        pointerFence.capture(note.sender,note.epoch,pointerRegistration(note.sender),clockMs());
    }
}

void pollPointerNotifications() {
    const auto now=clockMs();
    const bool connected=bus&&dbus_connection_get_is_connected(bus);
    const bool controlBacklog=connected&&dbus_connection_get_dispatch_status(bus)==DBUS_DISPATCH_DATA_REMAINS;
    for(auto it=pointerFence.notes.begin();it!=pointerFence.notes.end();) {
        const auto id=it->first;auto& note=it->second;++it;
        auto epoch=pointerEpochs.find(note.sender);
        auto registration=registrations.find(note.name);
        if(!connected||retiring||now>=note.deadline||epoch==pointerEpochs.end()
           ||epoch->second!=note.epoch||registration==registrations.end()||registration->second!=note.sender) {
            auto call=pointerFenceCalls.find(id);
            if(call!=pointerFenceCalls.end()){dbus_pending_call_cancel(call->second);dbus_pending_call_unref(call->second);pointerFenceCalls.erase(call);}
            pointerFence.drop(id);continue;
        }
        // Expiration/cancellation remains bounded and runs even during a
        // saturated control queue. No fence completion/start or delivery may
        // overtake those known owner packets.
        if(controlBacklog)continue;
        if(note.phase==PointerLocator::NotificationFence::Note::Queued) {
            if(pointerFence.active()>=PointerLocator::NotificationFence::MAX_CALLS)continue;
            auto* request=dbus_message_new_method_call(DBUS_SERVICE_DBUS,DBUS_PATH_DBUS,DBUS_INTERFACE_DBUS,"GetNameOwner");
            const char* name=note.name.c_str();DBusPendingCall* call=nullptr;
            bool sent=false;
            if(request) {
                dbus_message_append_args(request,DBUS_TYPE_STRING,&name,DBUS_TYPE_INVALID);
                const int timeout=static_cast<int>(std::clamp<uint64_t>(note.deadline-now,1,500));
                sent=dbus_connection_send_with_reply(bus,request,&call,timeout);dbus_message_unref(request);
            }
            if(!sent||!call){if(call){dbus_pending_call_cancel(call);dbus_pending_call_unref(call);}pointerFence.drop(id);continue;}
            if(!pointerFence.start(id)){dbus_pending_call_cancel(call);dbus_pending_call_unref(call);pointerFence.drop(id);continue;}
            pointerFenceCalls.emplace(id,call);
        } else if(note.phase==PointerLocator::NotificationFence::Note::InFlight) {
            auto call=pointerFenceCalls.find(id);
            if(call==pointerFenceCalls.end()){pointerFence.drop(id);continue;}
            if(!dbus_pending_call_get_completed(call->second))continue;
            auto* response=dbus_pending_call_steal_reply(call->second);
            dbus_pending_call_unref(call->second);pointerFenceCalls.erase(call);
            const char* owner=nullptr;
            const bool matched=response&&dbus_message_get_type(response)==DBUS_MESSAGE_TYPE_METHOD_RETURN
                &&dbus_message_get_args(response,nullptr,DBUS_TYPE_STRING,&owner,DBUS_TYPE_INVALID)
                &&owner&&note.sender==owner;
            if(matched)pointerFence.complete(id,owner);
            if(response)dbus_message_unref(response);
            if(!matched){pointerFence.drop(id);continue;}
        }
        const bool backlog=dbus_connection_get_dispatch_status(bus)==DBUS_DISPATCH_DATA_REMAINS;
        if(pointerFence.valid(id,epoch->second,registration->second,backlog,clockMs())) {
            auto* message=dbus_message_new_signal(PATH,POINTER_IFACE,"PointerPositionChanged");
            bool delivered=false;
            if(message){dbus_message_set_destination(message,note.sender.c_str());delivered=sendPointer(message);}
            if(delivered)pointerFence.sent(id);else pointerFence.drop(id);
        }
    }
}

void pointerRetire() {pointerState.retire();pointerFence.retire();
    for(auto& [id,call]:pointerFenceCalls){dbus_pending_call_cancel(call);dbus_pending_call_unref(call);}pointerFenceCalls.clear();for(auto& q:pointerQueries)queryError(*q,DBUS_ERROR_ACCESS_DENIED,"service retired",false);pointerQueries.clear();}


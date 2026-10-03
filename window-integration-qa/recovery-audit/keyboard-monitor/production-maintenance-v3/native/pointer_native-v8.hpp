// Included within the private bridge namespace after existing key hooks.
// Contract: ../AX_MAPPING_CONTRACT.md and root PointerLocatorState.hpp.
constexpr auto POINTER_IFACE="org.freedesktop.a11y.PointerLocator";
PointerLocator::State pointerState;
std::map<std::string,uint64_t> pointerEpochs;
uint64_t nextPointerEpoch=0;
PointerLocator::NotificationFence pointerFence;
std::map<uint64_t,DBusPendingCall*> pointerFenceCalls;
// A monitor alias transition invalidates the principal even if another alias
// still exists. Keyboard definitions/captured releases are unaffected.
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
DBusConnection* axBus=nullptr;
CFunctionHook* motionHook=nullptr;
using MotionFn=void(*)(Pointer::CPointerManager*);
struct Hover {
    PHLWINDOW window;
    pid_t pid=0;
    uint64_t start=0;
    PointerLocator::Point pointer{},relative{};
};
uint64_t processStart(pid_t pid) {
    std::ifstream file("/proc/"+std::to_string(pid)+"/stat");std::string line;
    if(!std::getline(file,line))return 0;
    const auto end=line.rfind(')');if(end==std::string::npos)return 0;
    std::istringstream fields(line.substr(end+2));std::string field;
    for(unsigned i=0;i<=19;++i)if(!(fields>>field))return 0;
    try{return std::stoull(field);}catch(...){return 0;}
}
std::optional<Hover> freshHover() {
    const auto pos=Pointer::mgr()->position();
    if(!std::isfinite(pos.x)||!std::isfinite(pos.y)||g_pSessionLockManager->isSessionLocked()
       ||g_pInputManager->m_relay.popupFromCoords(pos))return std::nullopt;
    const auto monitor=State::monitorState()->query().vec(pos).run();if(!monitor)return std::nullopt;
    auto hits=Desktop::viewState()->hitTest();
    auto window=hits.windowAt(pos,Desktop::View::FOCUS_PRIORITY|Desktop::View::ALLOW_FLOATING);
    Vector2D local;PHLLS layer;
    if(!window) {
        if(!g_pInputManager->m_exclusiveLSes.empty()
           ||hits.layerPopupSurfaceAt(pos,monitor,&local,&layer)
           ||hits.layerSurfaceAt(pos,&monitor->m_layerSurfaceLayers[ZWLR_LAYER_SHELL_V1_LAYER_OVERLAY],&local,&layer)
           ||hits.layerSurfaceAt(pos,&monitor->m_layerSurfaceLayers[ZWLR_LAYER_SHELL_V1_LAYER_TOP],&local,&layer))return std::nullopt;
        window=hits.windowAt(pos,Desktop::View::RESERVED_EXTENTS|Desktop::View::INPUT_EXTENTS|Desktop::View::ALLOW_FLOATING);
    }
    if(!window||!window->m_isMapped||window->m_isX11||!window->wlSurface()
       ||!hits.windowSurfaceAt(pos,window,local))return std::nullopt;
    const auto origin=window->wlSurface()->getSurfaceBoxGlobal();if(!origin)return std::nullopt;
    const auto relative=PointerLocator::relative({pos.x,pos.y},{origin->x,origin->y});if(!relative)return std::nullopt;
    const auto pid=window->getPID();if(pid<=0)return std::nullopt;
    unsigned count=0;
    for(const auto& w:Desktop::windowState()->windows())if(w->m_isMapped&&w->getPID()==pid)++count;
    if(count!=1)return std::nullopt;
    const auto start=processStart(pid);if(!start)return std::nullopt;
    return Hover{window,pid,start,{pos.x,pos.y},*relative};
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
struct AxRef {std::string bus,path;};
bool refs(DBusMessage* reply,std::vector<AxRef>& result) {
    if(!reply||!dbus_message_has_signature(reply,"a(so)"))return false;
    DBusMessageIter root,array,entry;dbus_message_iter_init(reply,&root);dbus_message_iter_recurse(&root,&array);
    while(dbus_message_iter_get_arg_type(&array)!=DBUS_TYPE_INVALID) {
        if(result.size()>=64)return false;
        const char *name=nullptr,*path=nullptr;
        dbus_message_iter_recurse(&array,&entry);dbus_message_iter_get_basic(&entry,&name);
        dbus_message_iter_next(&entry);dbus_message_iter_get_basic(&entry,&path);
        if(!name||*name!=':'||!dbus_validate_bus_name(name,nullptr)||!path||!dbus_validate_path(path,nullptr))return false;
        result.push_back({name,path});dbus_message_iter_next(&array);
    }
    return true;
}
struct PointerQuery {
    DBusMessage* request=nullptr;
    DBusPendingCall* pending=nullptr;
    std::string sender;
    uint64_t epoch=0,deadline=0;
    Hover hover;
    int phase=0;
    size_t index=0;
    std::vector<AxRef> applications,matches;
    AxRef target;
    bool done=false;
    ~PointerQuery(){if(pending){dbus_pending_call_cancel(pending);dbus_pending_call_unref(pending);}if(request)dbus_message_unref(request);}
};
std::vector<std::unique_ptr<PointerQuery>> pointerQueries;
bool sendPointer(DBusMessage* message) {
    if(!message)return false;
    const bool sent=bus&&dbus_connection_get_is_connected(bus)&&dbus_connection_send(bus,message,nullptr);
    dbus_message_unref(message);return sent;
}
void queryError(PointerQuery& query,const char* name,const char* why,bool arm) {
    if(query.done)return;
    const bool sent=sendPointer(dbus_message_new_error(query.request,name,why));query.done=true;
    if(sent&&arm&&!retiring&&!initializing&&pointerState.authorized(query.sender,query.epoch)) {
        const auto pos=Pointer::mgr()->position();pointerState.replySent(query.sender,query.epoch,{pos.x,pos.y});
    }
}
void unknown(PointerQuery& query) {
    queryError(query,"org.freedesktop.a11y.UnknownToplevel","no verified unique accessibility toplevel",true);
}
bool issue(PointerQuery& query,const char* destination,const char* path,const char* iface,const char* method,const char* arg=nullptr) {
    if(!axBus||!dbus_connection_get_is_connected(axBus))return false;
    auto* message=dbus_message_new_method_call(destination,path,iface,method);if(!message)return false;
    if(arg)dbus_message_append_args(message,DBUS_TYPE_STRING,&arg,DBUS_TYPE_INVALID);
    const auto now=clockMs();
    if(now>=query.deadline){dbus_message_unref(message);return false;}
    const auto remaining=query.deadline-now;
    const int timeout=static_cast<int>(std::clamp<uint64_t>(remaining,1,500));
    const bool sent=dbus_connection_send_with_reply(axBus,message,&query.pending,timeout);
    dbus_message_unref(message);return sent&&query.pending;
}
void nextApplication(PointerQuery& query) {
    if(query.index<query.applications.size()) {
        query.phase=2;
        if(!issue(query,DBUS_SERVICE_DBUS,DBUS_PATH_DBUS,DBUS_INTERFACE_DBUS,"GetConnectionUnixProcessID",query.applications[query.index].bus.c_str()))unknown(query);
    } else if(query.matches.size()==1) {
        query.phase=3;const auto& app=query.matches.front();
        if(!issue(query,app.bus.c_str(),app.path.c_str(),"org.a11y.atspi.Accessible","GetChildren"))unknown(query);
    } else unknown(query);
}
void metadata(PointerQuery& query) {
    auto hit=freshHover();
    if(!hit||hit->window!=query.hover.window||hit->pid!=query.hover.pid||hit->start!=query.hover.start){unknown(query);return;}
    auto* response=dbus_message_new_method_return(query.request);if(!response){unknown(query);return;}
    DBusMessageIter root,dict,entry,value;dbus_message_iter_init_append(response,&root);
    dbus_message_iter_open_container(&root,DBUS_TYPE_ARRAY,"{sv}",&dict);
    auto property=[&](const char* key,int type,const char* signature,const char* text) {
        dbus_message_iter_open_container(&dict,DBUS_TYPE_DICT_ENTRY,nullptr,&entry);
        dbus_message_iter_append_basic(&entry,DBUS_TYPE_STRING,&key);
        dbus_message_iter_open_container(&entry,DBUS_TYPE_VARIANT,signature,&value);
        dbus_message_iter_append_basic(&value,type,&text);
        dbus_message_iter_close_container(&entry,&value);dbus_message_iter_close_container(&dict,&entry);
    };
    property("app-dbus-name",DBUS_TYPE_STRING,"s",query.target.bus.c_str());
    property("toplevel-object-path",DBUS_TYPE_OBJECT_PATH,"o",query.target.path.c_str());
    dbus_message_iter_close_container(&root,&dict);
    dbus_message_iter_append_basic(&root,DBUS_TYPE_DOUBLE,&hit->relative.x);
    dbus_message_iter_append_basic(&root,DBUS_TYPE_DOUBLE,&hit->relative.y);
    const bool sent=sendPointer(response);query.done=true;
    if(sent)pointerState.replySent(query.sender,query.epoch,hit->pointer);
}
void pollPointers() {
    if(axBus&&dbus_connection_get_is_connected(axBus)) {
        dbus_connection_read_write(axBus,0);
        for(unsigned n=0;n<32&&dbus_connection_get_dispatch_status(axBus)==DBUS_DISPATCH_DATA_REMAINS;++n)dbus_connection_dispatch(axBus);
    }
    unsigned budget=32;
    for(auto& item:pointerQueries) {
        auto& query=*item;if(query.done)continue;
        if(retiring||!pointerState.authorized(query.sender,query.epoch)) {
            queryError(query,DBUS_ERROR_ACCESS_DENIED,"registration epoch retired",false);continue;
        }
        if(clockMs()>=query.deadline||!axBus||!dbus_connection_get_is_connected(axBus)){unknown(query);continue;}
        if(!budget||!query.pending||!dbus_pending_call_get_completed(query.pending))continue;
        --budget;
        auto* response=dbus_pending_call_steal_reply(query.pending);dbus_pending_call_unref(query.pending);query.pending=nullptr;
        if(!response||dbus_message_get_type(response)==DBUS_MESSAGE_TYPE_ERROR){if(response)dbus_message_unref(response);unknown(query);continue;}
        if(query.phase==1) {
            if(!refs(response,query.applications)){dbus_message_unref(response);unknown(query);continue;}
            nextApplication(query);
        } else if(query.phase==2) {
            dbus_uint32_t pid=0;
            if(dbus_message_get_args(response,nullptr,DBUS_TYPE_UINT32,&pid,DBUS_TYPE_INVALID)&&pid==static_cast<uint32_t>(query.hover.pid))query.matches.push_back(query.applications[query.index]);
            ++query.index;nextApplication(query);
        } else if(query.phase==3) {
            std::vector<AxRef> children;
            if(!refs(response,children)||children.size()!=1||children.front().bus!=query.matches.front().bus){dbus_message_unref(response);unknown(query);continue;}
            query.target=children.front();query.phase=4;
            if(!issue(query,query.target.bus.c_str(),query.target.path.c_str(),"org.a11y.atspi.Accessible","GetRole"))unknown(query);
        } else if(query.phase==4) {
            dbus_uint32_t role=0;
            if(dbus_message_get_args(response,nullptr,DBUS_TYPE_UINT32,&role,DBUS_TYPE_INVALID)
               &&(role==ATSPI_ROLE_FRAME||role==ATSPI_ROLE_DIALOG||role==ATSPI_ROLE_WINDOW))metadata(query);
            else unknown(query);
        }
        dbus_message_unref(response);
    }
    std::erase_if(pointerQueries,[](const auto& item){return item->done;});
}
// Expiration runs on every bounded control tick. Fence work runs only after
// ordinary dispatch has drained the known session queue. GetNameOwner uses this SAME connection, so its daemon reply
// follows earlier NameOwnerChanged packets. Never block/steal an undispached
// reply; get_completed is reached only through normal libdbus dispatch.
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
void queryPointer(DBusMessage* request,const char* sender) {
    const auto found=pointerEpochs.find(sender);
    if(found==pointerEpochs.end()||!pointerState.authorized(sender,found->second)) {error(request,DBUS_ERROR_ACCESS_DENIED,"caller requires current registration");return;}
    // Conservatively reserve every accepted asynchronous query as well as
    // one-shot arms. Refusal does not evict any previous accepted notification.
    if(!pointerFence.reserve(pointerState.pendingCount(),pointerQueries.size())) {
        ++pointerFence.refused;error(request,DBUS_ERROR_LIMITS_EXCEEDED,"pointer notification capacity");return;
    }
    auto query=std::make_unique<PointerQuery>();query->request=dbus_message_ref(request);
    query->sender=sender;query->epoch=found->second;query->deadline=clockMs()+1500;
    auto hit=freshHover();
    if(!hit||pointerQueries.size()>=16){unknown(*query);return;}
    query->hover=*hit;query->phase=1;
    if(!issue(*query,"org.a11y.atspi.Registry","/org/a11y/atspi/accessible/root","org.a11y.atspi.Accessible","GetChildren")){unknown(*query);return;}
    pointerQueries.push_back(std::move(query));
}
void pointerRetire() {pointerState.retire();pointerFence.retire();
    for(auto& [id,call]:pointerFenceCalls){dbus_pending_call_cancel(call);dbus_pending_call_unref(call);}pointerFenceCalls.clear();for(auto& q:pointerQueries)queryError(*q,DBUS_ERROR_ACCESS_DENIED,"service retired",false);pointerQueries.clear();}
void pointerCleanup() {
    pointerRetire();pointerEpochs.clear();
    if(axBus){dbus_connection_close(axBus);dbus_connection_unref(axBus);axBus=nullptr;}
}
void connectAccessibility() {
    DBusError err;dbus_error_init(&err);
    auto* request=dbus_message_new_method_call("org.a11y.Bus","/org/a11y/bus","org.a11y.Bus","GetAddress");
    if(!request)throw std::runtime_error("accessibility address allocation");
    auto* response=dbus_connection_send_with_reply_and_block(bus,request,500,&err);dbus_message_unref(request);
    const char* address=nullptr;
    if(!response||!dbus_message_get_args(response,&err,DBUS_TYPE_STRING,&address,DBUS_TYPE_INVALID)) {
        if(response)dbus_message_unref(response);
        dbus_error_free(&err);throw std::runtime_error("private accessibility address unavailable");
    }
    const std::string configured=address;dbus_message_unref(response);
    const auto prefix=std::string("unix:path=")+getenv("XDG_RUNTIME_DIR")+"/";
    if(!configured.starts_with(prefix)||configured.find(';')!=std::string::npos)throw std::runtime_error("accessibility bus is outside private runtime");
    const auto end=configured.find(',');const auto path=configured.substr(10,end==std::string::npos?end:end-10);
    const auto canonical=std::filesystem::weakly_canonical(path).string();
    const auto runtime=std::filesystem::canonical(getenv("XDG_RUNTIME_DIR")).string()+"/";
    if(!canonical.starts_with(runtime))throw std::runtime_error("accessibility socket escapes private runtime");
    struct stat socketStat{};
    if(lstat(path.c_str(),&socketStat)||!S_ISSOCK(socketStat.st_mode)||socketStat.st_uid!=getuid())throw std::runtime_error("private accessibility socket ownership mismatch");
    axBus=dbus_connection_open_private(configured.c_str(),&err);
    if(!axBus){dbus_error_free(&err);throw std::runtime_error("private accessibility connection unavailable");}
    dbus_connection_set_exit_on_disconnect(axBus,false);
    auto* hello=dbus_message_new_method_call(DBUS_SERVICE_DBUS,DBUS_PATH_DBUS,DBUS_INTERFACE_DBUS,"Hello");
    auto* reply=hello?dbus_connection_send_with_reply_and_block(axBus,hello,500,&err):nullptr;
    if(hello)dbus_message_unref(hello);
    const char* unique=nullptr;
    if(!reply||!dbus_message_get_args(reply,&err,DBUS_TYPE_STRING,&unique,DBUS_TYPE_INVALID)||!dbus_bus_set_unique_name(axBus,unique)) {
        if(reply)dbus_message_unref(reply);
        dbus_error_free(&err);throw std::runtime_error("private accessibility Hello failed");
    }
    dbus_message_unref(reply);dbus_error_free(&err);
}

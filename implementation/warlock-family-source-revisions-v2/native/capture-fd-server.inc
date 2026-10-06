void revokePreview(bool privacy) noexcept {
    for(auto& [pid,probe]:captureProbes)probe.revoked=true;
    auto& generation=privacy?previewPrivacy:previewRendering;
    if(generation!=std::numeric_limits<uint64_t>::max())++generation;
}
struct PreviewPeer {
    preview::fd::Owned socket;
    wl_event_source *read=nullptr,*timer=nullptr;
    ucred credentials{};
    ~PreviewPeer(){if(read)wl_event_source_remove(read);if(timer)wl_event_source_remove(timer);}
};
preview::fd::Owned previewListener;
wl_event_source* previewListenerSource=nullptr;
std::map<int,std::unique_ptr<PreviewPeer>> previewPeers;
void stopPreviewFdServer() noexcept {
    if(previewListenerSource)wl_event_source_remove(previewListenerSource);
    previewListenerSource=nullptr;previewPeers.clear();previewListener=preview::fd::Owned{};previewFdAddress.clear();
}
preview::fd::Header previewImageReply(pid_t pid,const preview::fd::Query& q) {
    using namespace preview::fd;
    Header out{};out[Magic]=MAGIC;out[Version]=1;out[Status]=1;out[Request]=q[RRequest];
    if(q[RMagic]!=MAGIC || q[RVersion]!=1 || q[ROp]<Get || q[ROp]>Observe || !q[RRequest] || !q[RCapture] || !q[RSubject])return out;
    auto session=sessions.find(pid);const auto start=startTime(pid);
    if(session==sessions.end() || start.empty() || session->second.start!=start || !grantRegistry->callerMatches(verifiedPeer(pid,start),{q[RLifetime],q[RSession],q[RFrontend]})){out[Status]=2;return out;}
    auto found=captureProbes.find(pid);
    if(found==captureProbes.end() || found->second.session!=q[RSession] || found->second.frontend!=q[RFrontend] || found->second.request!=q[RCapture] || found->second.incarnation!=q[RSubject]){out[Status]=3;return out;}
    auto& probe=found->second;
    if(q[ROp]==Release) {
        if(!probe.exported || !q[RTransfer] || probe.exported->transfer!=q[RTransfer]){out[Status]=4;return out;}
        out[Status]=0;out[Lifetime]=lifetime;out[preview::fd::Session]=probe.session;out[Frontend]=probe.frontend;out[Capture]=probe.request;out[Subject]=probe.incarnation;out[Transfer]=probe.exported->transfer;
        probe.exported.reset();return out;
    }
    refreshFacts();
    if(!g_pSessionLockManager || g_pSessionLockManager->isSessionLocked() || probe.output!=outputGeneration || !g_pHyprRenderer || !Render::GL::g_pHyprOpenGL)probe.revoked=true;
    const uint64_t now=preview::capture::nativeNow();
    if(probe.revoked || now>=probe.completed+5000000000ULL){out[Status]=5;return out;}
    if(q[ROp]==Get) {
        if(q[RTransfer] || (probe.exported && probe.exported->sent)){out[Status]=6;return out;}
        if(!probe.exported) {
            // Reserve the page-rounded kernel backing before creating it. The
            // producer raster reservation and export reservation are separate.
            const uint64_t charge=(probe.image->png().size()+4095)&~uint64_t{4095};
            auto reserved=captureBudget->reserve(charge);
            if(!reserved){out[Status]=7;return out;}
            auto image=preview::fd::seal(probe.image->png());
            probe.exported=std::make_unique<ExportedImage>(ExportedImage{std::move(image),std::move(*reserved),randomIdentity(),false});
        }
    }
    if(!probe.exported || (q[RTransfer] && q[RTransfer]!=probe.exported->transfer)){out[Status]=8;return out;}
    const auto member=std::find_if(members.begin(),members.end(),[&](const Member& item){return item.id==probe.incarnation;});
    const auto window=member==members.end()?PHLWINDOW{}:member->window.lock();
    const bool present=window && window->m_isMapped;
    const bool live=present && !Desktop::WindowPolicy::isMinimized(window) && g_pHyprRenderer->shouldRenderWindow(window);
    out[Status]=0;out[Lifetime]=lifetime;out[preview::fd::Session]=probe.session;out[Frontend]=probe.frontend;out[Capture]=probe.request;out[Subject]=probe.incarnation;out[Output]=probe.output;
    out[Completed]=probe.completed;out[Now]=now;out[Width]=probe.image->width;out[Height]=probe.image->height;out[Bytes]=probe.image->png().size();out[Charge]=probe.exported->reservation.bytes();
    out[Transfer]=probe.exported->transfer;out[CRC]=probe.checksum;out[Privacy]=probe.privacy;out[Rendering]=probe.rendering;out[Scene]=probe.scene;out[Content]=probe.content;
    out[Flags]=(probe.popup?RootPopupPlane:probe.client?IsolatedClientPlane:FullMonitorPlane)|(present?uint64_t{Present}:0ULL)|(live?uint64_t{SourceLive}:0ULL);out[Deadline]=probe.deadline;out[Expires]=probe.completed+5000000000ULL;return out;
}
int previewPeerTimeout(void* data) {
    auto peer=static_cast<PreviewPeer*>(data);previewPeers.erase(peer->socket.get());return 0;
}
int previewPeerRead(int descriptor,uint32_t mask,void* data) {
    auto peer=static_cast<PreviewPeer*>(data);
    try {
        if((mask&WL_EVENT_READABLE) && peer->credentials.uid==getuid() && std::this_thread::get_id()==ownerThread) {
            auto request=preview::fd::receive<preview::fd::RCount>(descriptor,0);
            if(request) {
                const auto reply=previewImageReply(peer->credentials.pid,request->words);
                int image=-1;
                auto probe=captureProbes.find(peer->credentials.pid);
                if(reply[preview::fd::Status]==0 && request->words[preview::fd::ROp]==preview::fd::Get && probe!=captureProbes.end() && probe->second.exported)image=probe->second.exported->file.get();
                const bool sent=preview::fd::send(descriptor,reply,image);
                if(image>=0 && probe!=captureProbes.end()) {
                    if(sent)probe->second.exported->sent=true;
                    else probe->second.exported.reset();
                }
            }
        }
    } catch(...) { /* no native exception escapes into compositor */ }
    previewPeers.erase(descriptor);return 0;
}
int previewAccept(int descriptor,uint32_t,void*) {
    for(unsigned count=0;count<8;++count) {
        preview::fd::Owned connection(::accept4(descriptor,nullptr,nullptr,SOCK_CLOEXEC|SOCK_NONBLOCK));
        if(!connection)break;
        if(previewPeers.size()>=4)continue;
        auto peer=std::make_unique<PreviewPeer>();peer->socket=std::move(connection);
        socklen_t size=sizeof(peer->credentials);
        if(::getsockopt(peer->socket.get(),SOL_SOCKET,SO_PEERCRED,&peer->credentials,&size) || size!=sizeof(peer->credentials) || peer->credentials.uid!=getuid() || peer->credentials.pid<=0)continue;
        peer->read=wl_event_loop_add_fd(g_pCompositor->m_wlEventLoop,peer->socket.get(),WL_EVENT_READABLE,previewPeerRead,peer.get());
        peer->timer=wl_event_loop_add_timer(g_pCompositor->m_wlEventLoop,previewPeerTimeout,peer.get());
        if(!peer->read || !peer->timer || wl_event_source_timer_update(peer->timer,1000))continue;
        const int key=peer->socket.get();previewPeers.emplace(key,std::move(peer));
    }
    return 0;
}
void startPreviewFdServer() {
    stopPreviewFdServer();
    previewFdAddress="elm-preview-"+std::to_string(getpid())+"-"+std::to_string(lifetime);
    const auto [address,size]=preview::fd::address(previewFdAddress);
    previewListener=preview::fd::Owned{::socket(AF_UNIX,SOCK_SEQPACKET|SOCK_CLOEXEC|SOCK_NONBLOCK,0)};
    if(!previewListener || ::bind(previewListener.get(),reinterpret_cast<const sockaddr*>(&address),size) || ::listen(previewListener.get(),4)) {stopPreviewFdServer();throw std::runtime_error("Native preview socket unavailable");}
    previewListenerSource=wl_event_loop_add_fd(g_pCompositor->m_wlEventLoop,previewListener.get(),WL_EVENT_READABLE,previewAccept,nullptr);
    if(!previewListenerSource){stopPreviewFdServer();throw std::runtime_error("Native preview socket watch unavailable");}
}

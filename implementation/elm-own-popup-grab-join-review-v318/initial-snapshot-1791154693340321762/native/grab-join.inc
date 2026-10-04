// Same-callback diagnostic. No host/window/menu authorization token is issued.
std::string observeXdgGrabJoin(eHyprCtlOutputFormat, std::string request) {
    if (request != "elm_xdg_grab_join" || std::this_thread::get_id() != owner || !privateSession() ||
        !g_pCompositor || g_pCompositor->m_isShuttingDown || !PROTO::compositor || !PROTO::xdgShell ||
        !g_pSeatManager || !g_pInputManager || !g_pSessionLockManager || !g_layoutManager ||
        !g_layoutManager->dragController() || !Desktop::otherViewState() ||
        censusSequence == std::numeric_limits<uint64_t>::max()) return R"({"refused":true})";
    const auto grab = g_pSeatManager->m_seatGrab;
    const auto xdg = PROTO::xdgShell->currentActiveGrab();
    if (xdg && xdg->grab != grab) return R"({"refused":true})";
    CensusBudget budget;
    std::map<wl_client*, size_t> clients;
    std::string members = "[", popups = "[";
    auto identity = [&](const SP<CWLSurfaceResource>& surface) {
        if (!surface || !surface->getResource() || !surface->getResource()->resource()) throw CensusRefused{};
        const auto raw = surface->getResource()->resource();
        const auto client = wl_resource_get_client(raw);
        const auto found = clients.find(client);
        if (found == clients.end()) throw CensusRefused{};
        pid_t pid = 0; uid_t uid = 0; gid_t gid = 0;
        wl_client_get_credentials(client, &pid, &uid, &gid);
        if (pid <= 0) throw CensusRefused{};
        return std::format(R"({{"id":{},"pid":{},"uid":{},"connection":{}}})",
            wl_resource_get_id(raw), pid, uid, found->second);
    };
    try {
        PROTO::compositor->forEachSurface([&](SP<CWLSurfaceResource> surface) {
            if (!surface || !surface->getResource() || !surface->getResource()->resource()) throw CensusRefused{};
            const auto raw = surface->getResource()->resource();
            const auto client = wl_resource_get_client(raw);
            const bool accepted = grab && grab->accepts(surface);
            budget.visit(reinterpret_cast<uintptr_t>(client), wl_resource_get_id(raw), accepted);
            if (!clients.contains(client)) clients.emplace(client, clients.size() + 1);
            if (!accepted) return;
            if (budget.members() > 1) members += ',';
            members += std::format(R"({{"surface":{},"mapped":{}}})", identity(surface), surface->m_mapped);
            budget.output(members.size());
        });
        const auto& views = Desktop::otherViewState()->views();
        if (views.size() > 512) throw CensusRefused{};
        size_t count = 0, visits = 0;
        if (xdg) for (const auto& member : xdg->popups) {
            const auto sx = member->m_surface.lock();
            const auto surface = sx ? sx->m_surface.lock() : nullptr;
            const auto px = member->m_parent.lock();
            const auto parent = px ? px->m_surface.lock() : nullptr;
            SP<Desktop::View::CPopup> found;
            size_t matches = 0;
            for (const auto& weak : views) {
                if (++visits > 32768) throw CensusRefused{};
                const auto v = weak.lock();
                if (!v || v->type() != Desktop::View::VIEW_TYPE_POPUP) continue;
                const auto p = Desktop::View::CPopup::fromView(v);
                if (p && p->m_mapped && !p->inert() && p->resource() == surface) { found = p; ++matches; }
            }
            if (matches != 1 || !found || !surface) throw CensusRefused{};
            const auto rootOwner = found->getT1Owner();
            const auto root = rootOwner ? rootOwner->resource() : nullptr;
            const auto layer = found->layerOwner();
            if (!root || !root->m_mapped || (layer && (!layer->m_mapped || layer->resource() != root))) throw CensusRefused{};
            if (++count > 64) throw CensusRefused{};
            if (count > 1) popups += ',';
            popups += std::format(R"({{"surface":{},"parent":{},"root":{},"layerRoot":{},"owner":{},"visible":{},"rootAccepted":{}}})",
                identity(surface), parent ? identity(parent) : "null", identity(root), static_cast<bool>(layer),
                member == xdg->owner, found->visible(), grab && grab->accepts(root));
            budget.output(members.size() + popups.size());
        }
        if (g_pSeatManager->m_seatGrab != grab || (xdg && xdg->grab != grab)) throw CensusRefused{};
    } catch (...) { return R"({"refused":true})"; }
    members += ']'; popups += ']';
    return std::format(R"({{"schema":1,"pid":{},"sequence":"{}","complete":true,"surfaceCount":{},"surfaceClientCount":{},"grabPresent":{},"grabKeyboard":{},"grabPointer":{},"xdgGrab":{},"sessionLocked":{},"exclusiveLayerPresent":{},"layoutDragPresent":{},"heldButtons":{},"members":{},"popups":{}}})",
        getpid(), ++censusSequence, budget.surfaces(), clients.size(), static_cast<bool>(grab), grab && grab->m_keyboard,
        grab && grab->m_pointer, static_cast<bool>(xdg), g_pSessionLockManager->isSessionLocked(),
        !g_pInputManager->m_exclusiveLSes.empty(), static_cast<bool>(g_layoutManager->dragController()->target()),
        g_pInputManager->hasHeldButtons(), members, popups);
}

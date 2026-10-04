#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/debug/HyprCtl.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <hyprland/src/managers/SeatManager.hpp>
#include <hyprland/src/managers/KeybindManager.hpp>
#include <hyprland/src/protocols/core/Seat.hpp>
#include <hyprland/src/protocols/core/Compositor.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <hyprland/src/protocols/XDGShell.hpp>
#include <hyprland/src/protocols/XDGDialog.hpp>
#include <hyprland/src/desktop/state/OtherViewState.hpp>
#include <hyprland/src/desktop/view/Popup.hpp>
#include <cmath>
#include <sys/stat.h>
#include <unistd.h>
#include <cstdlib>
#include <filesystem>
#include <thread>

namespace {
HANDLE handle;
SP<SHyprCtlCommand> command;
SP<SHyprCtlCommand> roleCommand;
SP<SHyprCtlCommand> popupCommand;
std::thread::id owner;
bool privateSession() {
    const auto runtime = std::getenv("XDG_RUNTIME_DIR");
    const auto backend = std::getenv("AQ_BACKENDS");
    if (!runtime || !backend || std::string(backend) != "wayland") return false;
    const std::filesystem::path path(runtime);
    if (path.parent_path() != std::filesystem::path(std::format("/run/user/{}/wqa", geteuid()))) return false;
    struct stat info;
    return lstat(runtime, &info) == 0 && S_ISDIR(info.st_mode) &&
        info.st_uid == geteuid() && (info.st_mode & 0777) == 0700;
}
std::string surfaceIdentity(const SP<CWLSurfaceResource>& surface) {
    if (!surface) return "null";
    const auto resource = surface->getResource()->resource();
    if (!resource) return "null";
    pid_t pid = 0; uid_t uid = 0; gid_t gid = 0;
    wl_client_get_credentials(wl_resource_get_client(resource), &pid, &uid, &gid);
    return std::format(R"({{"id":{},"pid":{},"uid":{}}})", wl_resource_get_id(resource), pid, uid);
}
std::string observePopups(eHyprCtlOutputFormat, std::string request) {
    if (request != "elm_popup_state" || std::this_thread::get_id() != owner || !privateSession() ||
        !g_pCompositor || g_pCompositor->m_isShuttingDown || !g_pSeatManager || !Desktop::otherViewState())
        return R"({"refused":true})";
    const auto& views = Desktop::otherViewState()->views();
    if (views.size() > 512) return R"({"refused":true})";
    const auto grab = g_pSeatManager->m_seatGrab;
    std::string result = std::format(R"({{"schema":1,"pid":{},"grabPresent":{},"grabKeyboard":{},"grabPointer":{},"keyboardFocus":{},"pointerFocus":{},"popups":[)",
        getpid(), static_cast<bool>(grab), grab && grab->m_keyboard, grab && grab->m_pointer,
        surfaceIdentity(g_pSeatManager->m_state.keyboardFocus.lock()), surfaceIdentity(g_pSeatManager->m_state.pointerFocus.lock()));
    size_t count = 0, ownershipVisits = 0;
    struct OwnershipBound {};
    for (const auto& weak : views) {
        const auto view = weak.lock();
        if (!view || view->type() != Desktop::View::VIEW_TYPE_POPUP) continue;
        const auto popup = Desktop::View::CPopup::fromView(view);
        if (!popup || !popup->m_mapped || popup->inert()) continue;
        if (++count > 256) return R"({"refused":true})";
        const auto surface = popup->resource();
        if (!surface || !surface->getResource() || !surface->getResource()->resource() || !Desktop::windowState())
            return R"({"refused":true})";
        if (Desktop::windowState()->windows().size() > 256) return R"({"refused":true})";
        PHLWINDOW rootWindow;
        size_t matches = 0;
        for (const auto& window : Desktop::windowState()->windows()) {
            if (!window || !window->m_isMapped || !window->m_popupHead) continue;
            bool belongs = false;
            try {
                window->m_popupHead->breadthfirst([&](SP<Desktop::View::CPopup> node, void*) {
                    if (++ownershipVisits > 1024) throw OwnershipBound{};
                    if (node == popup) belongs = true;
                }, nullptr);
            } catch (const OwnershipBound&) {
                return R"({"refused":true})";
            }
            if (belongs) { rootWindow = window; ++matches; }
        }
        if (matches != 1 || !rootWindow) return R"({"refused":true})";
        const auto root = rootWindow->resource();
        if (!root || !root->getResource() || !root->getResource()->resource()) return R"({"refused":true})";
        const auto position = popup->coordsGlobal();
        const auto size = popup->size();
        if (!surface || !root || !std::isfinite(position.x) || !std::isfinite(position.y) ||
            !std::isfinite(size.x) || !std::isfinite(size.y) || std::abs(position.x) > 1000000 ||
            std::abs(position.y) > 1000000 || size.x <= 0 || size.y <= 0 || size.x > 65536 || size.y > 65536)
            return R"({"refused":true})";
        if (count > 1) result += ',';
        result += std::format(R"({{"viewAddress":"0x{:x}","surface":{},"t1Root":{},"position":[{},{}],"size":[{},{}],"visible":{},"grabMember":{},"rootGrabMember":{}}})",
            reinterpret_cast<uintptr_t>(popup.get()), surfaceIdentity(surface), surfaceIdentity(root),
            position.x, position.y, size.x, size.y, popup->visible(), grab && grab->accepts(surface), grab && grab->accepts(root));
        if (result.size() > 65520) return R"({"refused":true})";
    }
    return result + "]}";
}
std::string observeRoles(eHyprCtlOutputFormat, std::string request) {
    if (request != "elm_role_state" || std::this_thread::get_id() != owner || !privateSession() ||
        !g_pCompositor || g_pCompositor->m_isShuttingDown || !Desktop::windowState())
        return R"({"refused":true})";
    std::string result = std::format(R"({{"schema":1,"pid":{},"windows":[)", getpid());
    size_t count = 0;
    for (const auto& window : Desktop::windowState()->windows()) {
        if (!window || !window->m_isMapped) continue;
        if (++count > 256) return R"({"refused":true})";
        const auto parent = window->parent();
        const auto xdg = window->m_xdgSurface.lock();
        const auto toplevel = xdg ? xdg->m_toplevel.lock() : nullptr;
        const auto dialog = toplevel ? toplevel->m_dialog.lock() : nullptr;
        if (count > 1) result += ',';
        result += std::format(R"({{"address":"0x{:x}","pid":{},"parentAddress":"0x{:x}","xdgToplevel":{},"dialogPresent":{},"dialogModal":{},"nativeModal":{},"inputBlocked":{},"acceptsInput":{},"hidden":{},"xwayland":{}}})",
            reinterpret_cast<uintptr_t>(window.get()), window->getPID(), reinterpret_cast<uintptr_t>(parent.get()),
            static_cast<bool>(toplevel), static_cast<bool>(dialog), dialog && dialog->modal,
            window->isModal(), window->isInputBlocked(), window->acceptsInput(), window->isHidden(), window->m_isX11);
        if (result.size() > 65520) return R"({"refused":true})";
    }
    return result + "]}";
}
std::string observe(eHyprCtlOutputFormat, std::string request) {
    if (request != "elm_held_state" || std::this_thread::get_id() != owner || !privateSession() ||
        !g_pCompositor || g_pCompositor->m_isShuttingDown || !g_pInputManager || !g_pSeatManager)
        return R"({"refused":true})";
    if (!g_pKeybindManager) return R"({"refused":true})";
    auto array = [](const auto& keys) {
        std::string out = "[";
        for (const auto& key : keys) {
            if (out.size() > 1) out += ",";
            out += std::to_string(key);
        }
        return out + "]";
    };
    std::vector<uint32_t> binds;
    for (const auto& key : g_pKeybindManager->m_pressedKeys) binds.push_back(key.keycode);
    const auto focus = g_pSeatManager->m_state.keyboardFocus.lock();
    const auto focusSeat = g_pSeatManager->m_state.keyboardFocusResource.lock();
    pid_t focusPID = 0, seatPID = 0; uid_t uid = 0; gid_t gid = 0;
    if (focus) wl_client_get_credentials(focus->client(), &focusPID, &uid, &gid);
    if (focusSeat) wl_client_get_credentials(focusSeat->client(), &seatPID, &uid, &gid);
    size_t liveResources = 0;
    if (focusSeat) for (const auto& k : focusSeat->m_keyboards) if (!k.expired()) ++liveResources;
    const auto resource = focus ? focus->getResource()->resource() : nullptr;
    const auto focusJSON = std::format(R"({{"surfacePresent":{},"surfaceId":{},"surfaceClientPID":{},"seatPresent":{},"seatClientPID":{},"liveKeyboardResources":{},"surfaceIdentity":"{:x}","seatIdentity":"{:x}"}})",
        static_cast<bool>(focus), resource ? wl_resource_get_id(resource) : 0, focusPID,
        static_cast<bool>(focusSeat), seatPID, liveResources, reinterpret_cast<uintptr_t>(focus.get()), reinterpret_cast<uintptr_t>(focusSeat.get()));
    return std::format(R"({{"focus":{},"schema":1,"pid":{},"held":{},"mousePresent":{},"pointerFocus":{},"seatGrab":{},"keys":{},"bindKeys":{},"mods":{},"keyboardPresent":{}}})",
        focusJSON, getpid(), g_pInputManager->hasHeldButtons(), !g_pSeatManager->m_mouse.expired(),
        !g_pSeatManager->m_state.pointerFocus.expired(), static_cast<bool>(g_pSeatManager->m_seatGrab),
        array(g_pInputManager->getKeysFromAllKBs()), array(binds), g_pInputManager->getModsFromAllKBs(),
        !g_pSeatManager->m_keyboard.expired());
}
}
APICALL EXPORT std::string PLUGIN_API_VERSION() { return HYPRLAND_API_VERSION; }
APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE plugin) {
    if (!privateSession() || std::string(__hyprland_api_get_hash()) != std::string(__hyprland_api_get_client_hash()))
        throw std::runtime_error("Exact owning ABI and private QA session required");
    handle = plugin; owner = std::this_thread::get_id();
    command = HyprlandAPI::registerHyprCtlCommand(handle, {"elm_held_state", false, observe});
    if (!command) throw std::runtime_error("Read-only held-state registration failed");
    roleCommand = HyprlandAPI::registerHyprCtlCommand(handle, {"elm_role_state", false, observeRoles});
    if (!roleCommand) {
        HyprlandAPI::unregisterHyprCtlCommand(handle, command);
        command.reset();
        throw std::runtime_error("Read-only role-state registration failed");
    }
    popupCommand = HyprlandAPI::registerHyprCtlCommand(handle, {"elm_popup_state", false, observePopups});
    if (!popupCommand) {
        HyprlandAPI::unregisterHyprCtlCommand(handle, roleCommand);
        roleCommand.reset();
        HyprlandAPI::unregisterHyprCtlCommand(handle, command);
        command.reset();
        throw std::runtime_error("Read-only popup-state registration failed");
    }
    return {"elm-held-state-qa", "Read-only private input retirement observer", "local", "0.1"};
}
APICALL EXPORT void PLUGIN_EXIT() {
    if (popupCommand) HyprlandAPI::unregisterHyprCtlCommand(handle, popupCommand);
    popupCommand.reset();
    if (roleCommand) HyprlandAPI::unregisterHyprCtlCommand(handle, roleCommand);
    roleCommand.reset();
    if (command) HyprlandAPI::unregisterHyprCtlCommand(handle, command);
    command.reset();
}

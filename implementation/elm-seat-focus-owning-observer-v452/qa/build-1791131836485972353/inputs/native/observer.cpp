#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/debug/HyprCtl.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <hyprland/src/managers/SeatManager.hpp>
#include <hyprland/src/managers/KeybindManager.hpp>
#include <hyprland/src/protocols/core/Seat.hpp>
#include <hyprland/src/protocols/core/Compositor.hpp>
#include <sys/stat.h>
#include <unistd.h>
#include <cstdlib>
#include <filesystem>
#include <thread>

namespace {
HANDLE handle;
SP<SHyprCtlCommand> command;
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
    return {"elm-held-state-qa", "Read-only private input retirement observer", "local", "0.1"};
}
APICALL EXPORT void PLUGIN_EXIT() {
    if (command) HyprlandAPI::unregisterHyprCtlCommand(handle, command);
    command.reset();
}

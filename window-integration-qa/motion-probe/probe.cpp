// Opt-in, bounded observation only. No hooks, geometry changes or per-frame IO.
#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/output/Monitor.hpp>
#include <hyprland/src/event/EventBus.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <chrono>
#include <deque>
#include <iomanip>
#include <sstream>

namespace {
HANDLE handle;
SP<SHyprCtlCommand> command;
CHyprSignalListener preCommit, outputCommit, present, mouse;
PHLWINDOWREF owner;
PHLMONITORREF monitor;
bool active = false, overflow = false;
constexpr size_t LIMIT = 12000;
uint64_t identity = 0;
int pid = 0;
using Clock = std::chrono::steady_clock;
Clock::time_point started;
double now() { return std::chrono::duration<double, std::milli>(Clock::now() - started).count(); }
struct Geometry {
    double t, x, y, w, h, gx, gy, gw, gh, fade, px, py;
    bool animating;
};
struct Presentation {
    double observed, hardware;
    unsigned seq, flags;
    int refresh;
    uint64_t commitID;
    bool displayed;
    int frame;
};
struct Input { double t, x, y; };
std::vector<Geometry> frames;
std::vector<Presentation> presentations;
std::vector<Input> inputs;
std::vector<std::pair<std::string,double>> marks;
std::deque<int> pending;
std::optional<Geometry> candidate;
Vector2D pointer;
size_t unmatched = 0, ambiguous = 0;

bool recording() {
    if (!active) return false;
    const auto w = owner.lock();
    if (now() > 20000 || !validMapped(w) || w->m_stableID != identity || w->getPID() != pid) {
        active = false;
        return false;
    }
    return true;
}
void resetListeners() {
    active = false;
    outputCommit.reset(); present.reset(); owner.reset(); monitor.reset();
    candidate.reset(); pending.clear();
}
std::string dump() {
    std::ostringstream out;
    out << std::setprecision(12) << "{\"active\":" << (active ? "true" : "false")
        << ",\"overflow\":" << (overflow ? "true" : "false") << ",\"unmatched\":" << unmatched
        << ",\"ambiguous\":" << ambiguous << ",\"identity\":" << identity << ",\"pid\":" << pid << ",\"frames\":[";
    for (size_t i = 0; i < frames.size(); ++i) {
        const auto& f = frames[i];
        if (i) out << ',';
        out << '[' << f.t << ',' << f.x << ',' << f.y << ',' << f.w << ',' << f.h
            << ',' << f.gx << ',' << f.gy << ',' << f.gw << ',' << f.gh << ',' << f.fade
            << ',' << f.px << ',' << f.py << ',' << (f.animating ? "true" : "false") << ']';
    }
    out << "],\"presentations\":[";
    for (size_t i = 0; i < presentations.size(); ++i) {
        const auto& p = presentations[i];
        if (i) out << ',';
        out << '[' << p.observed << ',' << p.hardware << ',' << p.seq << ',' << p.flags << ','
            << p.refresh << ',' << p.commitID << ',' << (p.displayed ? "true" : "false") << ',' << p.frame << ']';
    }
    out << "],\"inputs\":[";
    for (size_t i = 0; i < inputs.size(); ++i) {
        if (i) out << ',';
        out << '[' << inputs[i].t << ',' << inputs[i].x << ',' << inputs[i].y << ']';
    }
    out << "],\"marks\":[";
    for (size_t i = 0; i < marks.size(); ++i) {
        if (i) out << ',';
        // Names are validated as alphanumeric/underscore before recording.
        out << "[\"" << marks[i].first << "\"," << marks[i].second << ']';
    }
    out << "]}";
    return out.str();
}
std::string request(eHyprCtlOutputFormat, std::string text) {
    std::istringstream in(text);
    std::string name, verb, address;
    in >> name >> verb;
    if (verb == "stop") { active = false; return dump(); }
    if (verb == "status") return dump();
    if (verb == "mark") {
        std::string label; in >> label;
        if (!recording() || marks.size() >= 100 || label.empty() ||
            !std::all_of(label.begin(),label.end(),[](unsigned char c){return std::isalnum(c)||c=='_';}))
            return "{\"error\":\"invalid mark or capture inactive\"}";
        marks.emplace_back(label,now());
        return "{\"marked\":true}";
    }
    if (verb != "start") return "{\"error\":\"expected start ADDRESS PID, stop or status\"}";
    int expectedPID = 0;
    in >> address >> expectedPID;
    PHLWINDOW chosen;
    for (const auto& w : Desktop::windowState()->windows())
        if (std::format("0x{:x}", reinterpret_cast<uintptr_t>(w.get())) == address && validMapped(w) && w->getPID() == expectedPID)
            chosen = w;
    if (!chosen || !chosen->m_monitor || !chosen->m_monitor->m_output)
        return "{\"error\":\"captured owner not live or PID mismatch\"}";
    resetListeners();
    owner = chosen; monitor = chosen->m_monitor;
    identity = chosen->m_stableID; pid = chosen->getPID();
    frames.clear(); presentations.clear(); inputs.clear(); marks.clear();
    frames.reserve(LIMIT); presentations.reserve(LIMIT); inputs.reserve(LIMIT);
    overflow = false; unmatched = ambiguous = 0;
    pointer = g_pInputManager->getMouseCoordsInternal();
    started = Clock::now();
    const auto output = chosen->m_monitor->m_output;
    // Synchronous DRM commits emit this only after successful submission.
    // preCommit sampled the geometry used by the renderer for this submission.
    outputCommit = output->events.commit.listen([] {
        if (!recording() || !candidate) return;
        if (frames.size() >= LIMIT) { overflow = true; active = false; return; }
        frames.push_back(*candidate); candidate.reset();
        pending.push_back(static_cast<int>(frames.size() - 1));
    });
    present = output->events.present.listen([](const Aquamarine::IOutput::SPresentEvent& e) {
        if (!recording()) return;
        if (presentations.size() >= LIMIT) { overflow = true; active = false; return; }
        int frame = -1;
        // Require exactly one successful submission. Never guess after an
        // ambiguous queue, modeset, untracked commit or queued commit API.
        if (pending.size() == 1 && e.commitID == 0) frame = pending.front();
        else if (pending.empty()) ++unmatched;
        else ++ambiguous;
        pending.clear();
        double hw = -1;
        if (e.when) hw = e.when->tv_sec * 1000.0 + e.when->tv_nsec / 1000000.0;
        presentations.push_back({now(), hw, e.seq, e.flags, e.refresh, e.commitID, e.presented, frame});
    });
    active = true;
    return "{\"active\":true}";
}
}

APICALL EXPORT std::string PLUGIN_API_VERSION() { return HYPRLAND_API_VERSION; }
APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE h) {
    handle = h;
    if (std::string(__hyprland_api_get_hash()) != std::string(__hyprland_api_get_client_hash()))
        throw std::runtime_error("motion probe: compositor/header ABI mismatch");
    preCommit = Event::bus()->m_events.monitor.preCommit.listen([](PHLMONITOR mon) {
        if (!recording() || mon != monitor.lock()) return;
        const auto w = owner.lock();
        const auto p = w->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT);
        const auto s = w->size(Desktop::View::IGeometric::GEOMETRIC_CURRENT);
        const auto gp = w->position(Desktop::View::IGeometric::GEOMETRIC_GOAL);
        const auto gs = w->size(Desktop::View::IGeometric::GEOMETRIC_GOAL);
        candidate = Geometry{now(), p.x, p.y, s.x, s.y, gp.x, gp.y, gs.x, gs.y,
            w->alpha(Desktop::View::WINDOW_ALPHA_FADE)->value(), pointer.x, pointer.y,
            w->positionAnimation()->isBeingAnimated() || w->sizeAnimation()->isBeingAnimated()};
    });
    mouse = Event::bus()->m_events.input.mouse.move.listen([](Vector2D p, Event::SCallbackInfo&) {
        pointer = p;
        if (!recording()) return;
        if (inputs.size() >= LIMIT) { overflow = true; active = false; return; }
        inputs.push_back({now(), p.x, p.y});
    });
    command = HyprlandAPI::registerHyprCtlCommand(handle, {"motionprobe", false, request});
    if (!command) { preCommit.reset(); mouse.reset(); throw std::runtime_error("motion probe: command registration failed"); }
    return {"motion-probe", "Bounded window submission/presentation observer", "local QA", "1"};
}
APICALL EXPORT void PLUGIN_EXIT() {
    resetListeners(); preCommit.reset(); mouse.reset();
    if (command) HyprlandAPI::unregisterHyprCtlCommand(handle, command);
    command.reset();
}

#include <algorithm>
#include "GlobalVersion.hpp"
#include "NestedLifecycle.hpp"
#include "BufferDimensions.hpp"
#include <memory>
#include <unordered_map>
#include <aquamarine/backend/Wayland.hpp>
#include <aquamarine/input/ParentInput.hpp>
#include <wayland.hpp>
#include <xdg-shell.hpp>
#include <viewporter.hpp>
#include "Shared.hpp"
#include "FormatUtils.hpp"
#include <chrono>
#include <cstring>
#include <cstdlib>
#include <xf86drm.h>
#include <gbm.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

using namespace Aquamarine;
using namespace Hyprutils::Memory;
using namespace Hyprutils::Math;
#define SP CSharedPointer

// Event-loop-owned lifecycle state; public class layout remains unchanged.
static std::unordered_map<CWaylandOutput*, std::shared_ptr<NestedPolicy::ConfigureLifecycle>> outputLifecycle;
struct PrivateViewportBackend { SP<CCWpViewporter> resource; uint32_t global = 0; };
static std::unordered_map<CWaylandBackend*, PrivateViewportBackend> backendViewport;
static std::unordered_map<CWaylandOutput*, SP<CCWpViewport>> outputViewport;
static std::unordered_map<CWaylandPointer*, NestedPolicy::BalancedButtons> pointerButtons;
static std::unordered_map<CWaylandOutput*, uint64_t> frameGeneration;
// Parent-surface coordinates survive child pixel-mode and scale changes. Weak
// focus prevents an idle replay from reviving an output or a disconnected seat.
struct ParentPointerPosition {
    Hyprutils::Memory::CWeakPointer<CWaylandOutput> output;
    wl_fixed_t x = 0, y = 0;
};
static std::unordered_map<CWaylandPointer*, ParentPointerPosition> parentPointerPosition;
static bool mappingReady(CWaylandOutput* output) {
    const auto it = outputLifecycle.find(output);
    return it != outputLifecycle.end() && it->second->presentation.inputAllowed();
}


static std::pair<int, std::string> openExclusiveShm() {
    // Only absolute paths can be shared across different shm_open() calls
    srand(time(nullptr));
    std::string name = std::format("/aq{:x}", rand() % RAND_MAX);

    for (size_t i = 0; i < 69; ++i) {
        int fd = shm_open(name.c_str(), O_RDWR | O_CREAT | O_EXCL, 0600);
        if (fd >= 0)
            return {fd, name};
    }

    return {-1, ""};
}

static int allocateSHMFile(size_t len) {
    auto [fd, name] = openExclusiveShm();
    if (fd < 0)
        return -1;

    shm_unlink(name.c_str());

    int ret;
    do {
        ret = ftruncate(fd, len);
    } while (ret < 0 && errno == EINTR);

    if (ret < 0) {
        close(fd);
        return -1;
    }

    return fd;
}

wl_shm_format shmFormatFromDRM(uint32_t drmFormat) {
    switch (drmFormat) {
        case DRM_FORMAT_XRGB8888: return WL_SHM_FORMAT_XRGB8888;
        case DRM_FORMAT_ARGB8888: return WL_SHM_FORMAT_ARGB8888;
        default: return (wl_shm_format)drmFormat;
    }

    return (wl_shm_format)drmFormat;
}

Aquamarine::CWaylandBackend::~CWaylandBackend() {
    outputs.clear();
    backendViewport.erase(this);
    keyboards.clear();
    pointers.clear();
    idleCallbacks.clear();

    waylandState.dmabufFeedback.reset();
    waylandState.dmabuf.reset();
    waylandState.shm.reset();
    waylandState.compositor.reset();
    waylandState.xdg.reset();
    waylandState.seat.reset();
    waylandState.registry.reset();

    if (waylandState.display) {
        wl_display_disconnect(waylandState.display);
        waylandState.display = nullptr;
    }

    if (drmState.fd >= 0) {
        close(drmState.fd);
        drmState.fd = -1;
    }
}

eBackendType Aquamarine::CWaylandBackend::type() {
    return AQ_BACKEND_WAYLAND;
}

Aquamarine::CWaylandBackend::CWaylandBackend(SP<CBackend> backend_) : backend(backend_) {
    ;
}

bool Aquamarine::CWaylandBackend::start() {
    backend->log(AQ_LOG_DEBUG, "Starting the Wayland backend!");

    waylandState.display = wl_display_connect(nullptr);

    if (!waylandState.display) {
        backend->log(AQ_LOG_ERROR, "Wayland backend cannot start: wl_display_connect failed (is a wayland compositor running?)");
        return false;
    }

    auto XDGCURRENTDESKTOP = getenv("XDG_CURRENT_DESKTOP");
    backend->log(AQ_LOG_DEBUG, std::format("Connected to a wayland compositor: {}", (XDGCURRENTDESKTOP ? XDGCURRENTDESKTOP : "unknown (XDG_CURRENT_DEKSTOP unset?)")));

    waylandState.registry = makeShared<CCWlRegistry>((wl_proxy*)wl_display_get_registry(waylandState.display));

    backend->log(AQ_LOG_DEBUG, std::format("Got registry at 0x{:x}", (uintptr_t)waylandState.registry->resource()));

    waylandState.registry->setGlobal([this](CCWlRegistry* r, uint32_t id, const char* name, uint32_t version) {
        TRACE(backend->log(AQ_LOG_TRACE, std::format(" | received global: {} (version {}) with id {}", name, version, id)));

        const std::string NAME = name;

        if (NAME == "wp_viewporter" && version >= 1) {
            auto& viewport = backendViewport[this];
            viewport.resource = makeShared<CCWpViewporter>((wl_proxy*)wl_registry_bind((wl_registry*)waylandState.registry->resource(), id, &wp_viewporter_interface, 1));
            viewport.global = id;
        } else if (NAME == "wl_seat") {
            const auto chosen = RegistryVersion::negotiate(version, 9, 5);
            if (!chosen) {
                backend->log(AQ_LOG_ERROR, std::format("Wayland: {} advertised version {} below required 5", name, version));
                return;
            }
            TRACE(backend->log(AQ_LOG_TRACE, std::format("  > binding to global: {} (version {}) with id {}", name, chosen, id)));
            waylandState.seat = makeShared<CCWlSeat>((wl_proxy*)wl_registry_bind((wl_registry*)waylandState.registry->resource(), id, &wl_seat_interface, chosen));
            initSeat();
        } else if (NAME == "xdg_wm_base") {
            const auto chosen = RegistryVersion::negotiate(version, 6, 1);
            if (!chosen) {
                backend->log(AQ_LOG_ERROR, std::format("Wayland: {} advertised version {} below required 1", name, version));
                return;
            }
            TRACE(backend->log(AQ_LOG_TRACE, std::format("  > binding to global: {} (version {}) with id {}", name, chosen, id)));
            waylandState.xdg = makeShared<CCXdgWmBase>((wl_proxy*)wl_registry_bind((wl_registry*)waylandState.registry->resource(), id, &xdg_wm_base_interface, chosen));
            initShell();
        } else if (NAME == "wl_compositor") {
            const auto chosen = RegistryVersion::negotiate(version, 6, 4);
            if (!chosen) {
                backend->log(AQ_LOG_ERROR, std::format("Wayland: {} advertised version {} below required 4", name, version));
                return;
            }
            TRACE(backend->log(AQ_LOG_TRACE, std::format("  > binding to global: {} (version {}) with id {}", name, chosen, id)));
            waylandState.compositor = makeShared<CCWlCompositor>((wl_proxy*)wl_registry_bind((wl_registry*)waylandState.registry->resource(), id, &wl_compositor_interface, chosen));
        } else if (NAME == "wl_shm") {
            const auto chosen = RegistryVersion::negotiate(version, 1, 1);
            if (!chosen) {
                backend->log(AQ_LOG_ERROR, std::format("Wayland: {} advertised version {} below required 1", name, version));
                return;
            }
            TRACE(backend->log(AQ_LOG_TRACE, std::format("  > binding to global: {} (version {}) with id {}", name, chosen, id)));
            waylandState.shm = makeShared<CCWlShm>((wl_proxy*)wl_registry_bind((wl_registry*)waylandState.registry->resource(), id, &wl_shm_interface, chosen));
        } else if (NAME == "zwp_linux_dmabuf_v1") {
            const auto chosen = RegistryVersion::negotiate(version, 4, 4);
            if (!chosen) {
                backend->log(AQ_LOG_ERROR, std::format("Wayland: {} advertised version {} below required 4", name, version));
                return;
            }
            TRACE(backend->log(AQ_LOG_TRACE, std::format("  > binding to global: {} (version {}) with id {}", name, chosen, id)));
            waylandState.dmabuf =
                makeShared<CCZwpLinuxDmabufV1>((wl_proxy*)wl_registry_bind((wl_registry*)waylandState.registry->resource(), id, &zwp_linux_dmabuf_v1_interface, chosen));
            if (!initDmabuf()) {
                backend->log(AQ_LOG_ERROR, "Wayland backend cannot start: zwp_linux_dmabuf_v1 init failed");
                waylandState.dmabufFailed = true;
            }
        }
    });
    waylandState.registry->setGlobalRemove([this](CCWlRegistry* r, uint32_t id) {
        backend->log(AQ_LOG_DEBUG, std::format("Global {} removed", id));
        const auto it = backendViewport.find(this);
        if (it != backendViewport.end() && it->second.global == id) {
            for (const auto& output : outputs) {
                const auto state = outputLifecycle.find(output.get());
                if (state != outputLifecycle.end()) state->second->destroy();
            }
            it->second.resource.reset();
        }
    });

    wl_display_roundtrip(waylandState.display);

    if (!backendViewport[this].resource || !waylandState.xdg || !waylandState.compositor || !waylandState.seat || !waylandState.dmabuf || waylandState.dmabufFailed || !waylandState.shm) {
        backend->log(AQ_LOG_ERROR, "Wayland backend cannot start: Missing protocols");
        return false;
    }

    if (!dispatchEvents())
        return false;

    createOutput();

    return true;
}

int Aquamarine::CWaylandBackend::drmFD() {
    return drmState.fd;
}

int Aquamarine::CWaylandBackend::drmRenderNodeFD() {
    // creation already attempts to use the rendernode, so just return same fd as drmFD().
    return drmState.fd;
}

bool Aquamarine::CWaylandBackend::createOutput(const std::string& szName) {
    std::string name = szName;
    if (name.empty()) {
        // skip past any auto-name slots already claimed by an explicit createOutput,
        // so we never hand out a duplicate WAYLAND-N (see #185).
        do {
            name = std::format("WAYLAND-{}", ++lastOutputID);
        } while (std::ranges::any_of(outputs, [&name](const auto& o) { return o->name == name; }));
    } else if (std::ranges::any_of(outputs, [&name](const auto& o) { return o->name == name; })) {
        backend->log(AQ_LOG_ERROR, std::format("Wayland: refusing to create output {}, name already in use", name));
        return false;
    }

    auto o  = outputs.emplace_back(SP<CWaylandOutput>(new CWaylandOutput(name, self)));
    o->self = o;
    if (backend->ready)
        o->swapchain = CSwapchain::create(backend->primaryAllocator, self.lock());
    // Initial newOutput is queued by the first xdg_surface ACK, never before.
    return true;
}

std::vector<Hyprutils::Memory::CSharedPointer<SPollFD>> Aquamarine::CWaylandBackend::pollFDs() {
    if (!waylandState.display)
        return {};

    return {makeShared<SPollFD>(wl_display_get_fd(waylandState.display), [this]() { dispatchEvents(); })};
}

bool Aquamarine::CWaylandBackend::dispatchEvents() {
    const auto transportAlive = [this]() {
        if (wl_display_get_error(waylandState.display) == 0)
            return true;
        backend->log(AQ_LOG_CRITICAL, "Wayland parent transport failed; invalidating every nested output");
        if (NestedPolicy::selection(std::getenv("AQ_BACKENDS")) == NestedPolicy::Selection::Wayland)
            backend->ready = false;
        for (const auto& output : outputs) {
            if (const auto state = outputLifecycle.find(output.get()); state != outputLifecycle.end())
                state->second->destroy();
            output->needsFrame = false;
            output->waylandState.frameCallback.reset();
            output->sched.invalidate();
        }
        return false;
    };
    if (!transportAlive())
        return false;
    wl_display_flush(waylandState.display);

    if (wl_display_prepare_read(waylandState.display) == 0) {
        wl_display_read_events(waylandState.display);
        wl_display_dispatch_pending(waylandState.display);
    } else
        wl_display_dispatch(waylandState.display);

    if (!transportAlive())
        return false;
    int ret = 0;
    do {
        ret = wl_display_dispatch_pending(waylandState.display);
        wl_display_flush(waylandState.display);
    } while (ret > 0);
    if (!transportAlive())
        return false;

    // dispatch frames
    if (backend->ready) {
        for (auto const& f : idleCallbacks) {
            f();
        }
        idleCallbacks.clear();
    }

    return true;
}

uint32_t Aquamarine::CWaylandBackend::capabilities() {
    return AQ_BACKEND_CAPABILITY_POINTER;
}

bool Aquamarine::CWaylandBackend::setCursor(Hyprutils::Memory::CSharedPointer<IBuffer> buffer, const Hyprutils::Math::Vector2D& hotspot) {
    // TODO:
    return true;
}

void Aquamarine::CWaylandBackend::onReady() {
    for (auto const& o : outputs) {
        o->swapchain = CSwapchain::create(backend->primaryAllocator, self.lock());
        if (!o->swapchain) {
            backend->log(AQ_LOG_ERROR, std::format("Output {} failed: swapchain creation failed", o->name));
            continue;
        }
    }
}

Aquamarine::CWaylandKeyboard::CWaylandKeyboard(SP<CCWlKeyboard> keyboard_, Hyprutils::Memory::CWeakPointer<CWaylandBackend> backend_) : keyboard(keyboard_), backend(backend_) {
    if (!keyboard->resource())
        return;

    backend->backend->log(AQ_LOG_DEBUG, "New wayland keyboard wl_keyboard");

    keyboard->setKey([this](CCWlKeyboard* r, uint32_t serial, uint32_t timeMs, uint32_t key, wl_keyboard_key_state state) {
        events.key.emit(SKeyEvent{
            .timeMs  = timeMs,
            .key     = key,
            .pressed = state == WL_KEYBOARD_KEY_STATE_PRESSED,
        });
    });

    keyboard->setModifiers([this](CCWlKeyboard* r, uint32_t serial, uint32_t depressed, uint32_t latched, uint32_t locked, uint32_t group) {
        events.modifiers.emit(SModifiersEvent{
            .depressed = depressed,
            .latched   = latched,
            .locked    = locked,
            .group     = group,
        });
    });
}

Aquamarine::CWaylandKeyboard::~CWaylandKeyboard() {
    ;
}

const std::string& Aquamarine::CWaylandKeyboard::getName() {
    return name;
}

Aquamarine::CWaylandPointer::CWaylandPointer(SP<CCWlPointer> pointer_, Hyprutils::Memory::CWeakPointer<CWaylandBackend> backend_) : pointer(pointer_), backend(backend_) {
    if (!pointer->resource())
        return;

    backend->backend->log(AQ_LOG_DEBUG, "New wayland pointer wl_pointer");

    pointer->setMotion([this](CCWlPointer* r, uint32_t timeMs, wl_fixed_t x, wl_fixed_t y) { emitWarp(timeMs, x, y); });

    pointer->setEnter([this](CCWlPointer* r, uint32_t serial, wl_proxy* surface, wl_fixed_t x, wl_fixed_t y) {
        backend->lastEnterSerial = serial;

        for (auto const& o : backend->outputs) {
            if (o->waylandState.surface->resource() != surface)
                continue;

            backend->focusedOutput = o;
            backend->backend->log(AQ_LOG_DEBUG, std::format("[wayland] focus changed: {}", o->name));
            o->onEnter(pointer, serial);
            emitWarp(std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch()).count(), x, y);
            break;
        }
    });

    pointer->setLeave([this](CCWlPointer* r, uint32_t serial, wl_proxy* surface) {
        for (auto const& o : backend->outputs) {
            if (o->waylandState.surface->resource() != surface)
                continue;

            parentPointerPosition.erase(this);
            o->cursorState.serial = 0;
            if (backend->focusedOutput.lock() == o)
                backend->focusedOutput = {};
            break;
        }
    });

    pointer->setButton([this](CCWlPointer* r, uint32_t serial, uint32_t timeMs, uint32_t button, wl_pointer_button_state state) {
        const auto output = backend->focusedOutput.lock();
        if (!pointerButtons[this].admit(button, state == WL_POINTER_BUTTON_STATE_PRESSED, output && mappingReady(output.get()))) return;
        events.button.emit(SButtonEvent{
            .timeMs  = timeMs,
            .button  = button,
            .pressed = state == WL_POINTER_BUTTON_STATE_PRESSED,
        });
    });

    pointer->setAxis([this](CCWlPointer* r, uint32_t timeMs, wl_pointer_axis axis, wl_fixed_t value) {
        const auto output = backend->focusedOutput.lock();
        if (!output || !mappingReady(output.get())) return;
        events.axis.emit(SAxisEvent{
            .timeMs = timeMs,
            .axis   = axis == WL_POINTER_AXIS_HORIZONTAL_SCROLL ? AQ_POINTER_AXIS_HORIZONTAL : AQ_POINTER_AXIS_VERTICAL,
            .delta  = wl_fixed_to_double(value),
        });
    });

    pointer->setFrame([this](CCWlPointer* r) { events.frame.emit(); });
}

void Aquamarine::CWaylandPointer::emitWarp(uint32_t timeMs, wl_fixed_t x, wl_fixed_t y) {
    const auto output = backend->focusedOutput.lock();
    if (output)
        parentPointerPosition[this] = {output, x, y};
    if (!output || !mappingReady(output.get()) || output->waylandState.surfaceSize.x <= 0 || output->waylandState.surfaceSize.y <= 0)
        return;

    events.warp.emit(SWarpEvent{
        .timeMs   = timeMs,
        .absolute = Vector2D{wl_fixed_to_double(x), wl_fixed_to_double(y)} / output->waylandState.surfaceSize,
        .output   = SP<IOutput>(output),
    });
}

Aquamarine::ParentInputStatus Aquamarine::parentPointerInputStatus(const IPointer* pointer, const IOutput* output) {
    const auto parentPointer = dynamic_cast<const CWaylandPointer*>(pointer);
    if (!parentPointer) return ParentInputStatus::Unsupported;
    return parentPointer->inputAllowedOn(output) ? ParentInputStatus::Ready : ParentInputStatus::Inactive;
}

bool Aquamarine::CWaylandPointer::inputAllowedOn(const IOutput* output) const {
    const auto parent = backend.lock();
    if (!parent || !output) return false;
    const auto focused = parent->focusedOutput.lock();
    return focused && focused.get() == output && mappingReady(focused.get());
}

Aquamarine::CWaylandPointer::~CWaylandPointer() {
    pointerButtons.erase(this);
    parentPointerPosition.erase(this);
}

const std::string& Aquamarine::CWaylandPointer::getName() {
    return name;
}

void Aquamarine::CWaylandBackend::initSeat() {
    waylandState.seat->setCapabilities([this](CCWlSeat* r, wl_seat_capability cap) {
        const bool HAS_KEYBOARD = ((uint32_t)cap) & WL_SEAT_CAPABILITY_KEYBOARD;
        const bool HAS_POINTER  = ((uint32_t)cap) & WL_SEAT_CAPABILITY_POINTER;

        if (HAS_KEYBOARD && keyboards.empty()) {
            auto k = keyboards.emplace_back(makeShared<CWaylandKeyboard>(makeShared<CCWlKeyboard>(waylandState.seat->sendGetKeyboard()), self));
            const auto weakBackend = self;
            const auto weakDevice = CWeakPointer<CWaylandKeyboard>(k);
            idleCallbacks.emplace_back([weakBackend, weakDevice]() {
                const auto parent = weakBackend.lock();
                const auto device = weakDevice.lock();
                if (!parent || !device || std::ranges::find(parent->keyboards, device) == parent->keyboards.end())
                    return;
                const auto owner = parent->backend.lock();
                if (!owner || !owner->ready || !parent->waylandState.display || wl_display_get_error(parent->waylandState.display) != 0)
                    return;
                owner->events.newKeyboard.emit(SP<IKeyboard>(device));
            });
        } else if (!HAS_KEYBOARD && !keyboards.empty())
            keyboards.clear();

        if (HAS_POINTER && pointers.empty()) {
            auto p = pointers.emplace_back(makeShared<CWaylandPointer>(makeShared<CCWlPointer>(waylandState.seat->sendGetPointer()), self));
            const auto weakBackend = self;
            const auto weakDevice = CWeakPointer<CWaylandPointer>(p);
            idleCallbacks.emplace_back([weakBackend, weakDevice]() {
                const auto parent = weakBackend.lock();
                const auto device = weakDevice.lock();
                if (!parent || !device || std::ranges::find(parent->pointers, device) == parent->pointers.end())
                    return;
                const auto owner = parent->backend.lock();
                if (!owner || !owner->ready || !parent->waylandState.display || wl_display_get_error(parent->waylandState.display) != 0)
                    return;
                owner->events.newPointer.emit(SP<IPointer>(device));
            });
        } else if (!HAS_POINTER && !pointers.empty())
            pointers.clear();
    });
}

void Aquamarine::CWaylandBackend::initShell() {
    waylandState.xdg->setPing([](CCXdgWmBase* r, uint32_t serial) { r->sendPong(serial); });
}

bool Aquamarine::CWaylandBackend::initDmabuf() {
    waylandState.dmabufFeedback = makeShared<CCZwpLinuxDmabufFeedbackV1>(waylandState.dmabuf->sendGetDefaultFeedback());
    if (!waylandState.dmabufFeedback) {
        backend->log(AQ_LOG_ERROR, "initDmabuf: failed to get default feedback");
        return false;
    }

    waylandState.dmabufFeedback->setDone([this](CCZwpLinuxDmabufFeedbackV1* r) {
        // no-op
        backend->log(AQ_LOG_DEBUG, "zwp_linux_dmabuf_v1: Got done");
    });

    waylandState.dmabufFeedback->setMainDevice([this](CCZwpLinuxDmabufFeedbackV1* r, wl_array* deviceArr) {
        backend->log(AQ_LOG_DEBUG, "zwp_linux_dmabuf_v1: Got main device");

        dev_t device;
        ASSERT(deviceArr->size == sizeof(device));
        memcpy(&device, deviceArr->data, sizeof(device));

        drmDevice* drmDev;
        if (drmGetDeviceFromDevId(device, /* flags */ 0, &drmDev) != 0) {
            backend->log(AQ_LOG_ERROR, "zwp_linux_dmabuf_v1: drmGetDeviceFromDevId failed");
            return;
        }

        const char* name = nullptr;
        if (drmDev->available_nodes & (1 << DRM_NODE_RENDER))
            name = drmDev->nodes[DRM_NODE_RENDER];
        else {
            // Likely a split display/render setup. Pick the primary node and hope
            // Mesa will open the right render node under-the-hood.
            ASSERT(drmDev->available_nodes & (1 << DRM_NODE_PRIMARY));
            name = drmDev->nodes[DRM_NODE_PRIMARY];
            backend->log(AQ_LOG_WARNING, "zwp_linux_dmabuf_v1: DRM device has no render node, using primary.");
        }

        if (!name) {
            backend->log(AQ_LOG_ERROR, "zwp_linux_dmabuf_v1: no node name");
            drmFreeDevice(&drmDev);
            return;
        }

        drmState.nodeName = name;

        drmFreeDevice(&drmDev);

        backend->log(AQ_LOG_DEBUG, std::format("zwp_linux_dmabuf_v1: Got node {}", drmState.nodeName));
    });

    waylandState.dmabufFeedback->setFormatTable([this](CCZwpLinuxDmabufFeedbackV1* r, int32_t fd, uint32_t size) {
#pragma pack(push, 1)
        struct wlDrmFormatMarshalled {
            uint32_t drmFormat;
            char     pad[4];
            uint64_t modifier;
        };
#pragma pack(pop)
        static_assert(sizeof(wlDrmFormatMarshalled) == 16);

        auto formatTable = mmap(nullptr, size, PROT_READ, MAP_PRIVATE, fd, 0);
        if (formatTable == MAP_FAILED) {
            backend->log(AQ_LOG_ERROR, std::format("zwp_linux_dmabuf_v1: Failed to mmap the format table"));
            return;
        }

        const auto FORMATS = (wlDrmFormatMarshalled*)formatTable;

        for (size_t i = 0; i < size / 16; ++i) {
            auto& fmt = FORMATS[i];

            auto  modName = drmGetFormatModifierName(fmt.modifier);
            backend->log(AQ_LOG_DEBUG, std::format("zwp_linux_dmabuf_v1: Got format {} with modifier {}", fourccToName(fmt.drmFormat), modName ? modName : "UNKNOWN"));
            free(modName);

            auto it = std::ranges::find_if(dmabufFormats, [&fmt](const auto& e) { return e.drmFormat == fmt.drmFormat; });
            if (it == dmabufFormats.end()) {
                dmabufFormats.emplace_back(SDRMFormat{.drmFormat = fmt.drmFormat, .modifiers = {fmt.modifier}});
                continue;
            }

            it->modifiers.emplace_back(fmt.modifier);
        }

        munmap(formatTable, size);
    });

    wl_display_roundtrip(waylandState.display);

    if (!drmState.nodeName.empty()) {
        drmState.fd = open(drmState.nodeName.c_str(), O_RDWR | O_NONBLOCK | O_CLOEXEC);
        if (drmState.fd < 0) {
            backend->log(AQ_LOG_ERROR, std::format("zwp_linux_dmabuf_v1: Failed to open node {}", drmState.nodeName));
            return false;
        }

        backend->log(AQ_LOG_DEBUG, std::format("zwp_linux_dmabuf_v1: opened node {} with fd {}", drmState.nodeName, drmState.fd));
    }

    return true;
}

std::vector<SDRMFormat> Aquamarine::CWaylandBackend::getRenderFormats() {
    return dmabufFormats;
}

std::vector<SDRMFormat> Aquamarine::CWaylandBackend::getCursorFormats() {
    return dmabufFormats;
}

SP<IAllocator> Aquamarine::CWaylandBackend::preferredAllocator() {
    return backend->primaryAllocator;
}

std::vector<SP<IAllocator>> Aquamarine::CWaylandBackend::getAllocators() {
    return {backend->primaryAllocator};
}

Hyprutils::Memory::CWeakPointer<IBackendImplementation> Aquamarine::CWaylandBackend::getPrimary() {
    return {};
}

Aquamarine::CWaylandOutput::CWaylandOutput(const std::string& name_, Hyprutils::Memory::CWeakPointer<CWaylandBackend> backend_) : backend(backend_) {
    name = name_;
    const auto lifecycle = std::make_shared<NestedPolicy::ConfigureLifecycle>();
    outputLifecycle.emplace(this, lifecycle);

    // The scheduler's frameReady signal drives the public events.frame on this output.
    frameReadyListener = sched.frameReady.listen([this, lifecycle]() { if (lifecycle->bufferAllowed()) events.frame.emit(); });

    // a scheduleFrame mid frame, reschedule one more.
    rescheduleListener = sched.rescheduleNeeded.listen([this]() { scheduleFrame(AQ_SCHEDULE_NEEDS_FRAME); });

    // Idle that emits the scheduled frame, fired via the core backend's idle queue
    // (addIdleEvent), which the consumer's event loop pumps every iteration. Deliberately
    // not the backend-local idleCallbacks vector: that only drains inside dispatchEvents,
    // i.e. when the wayland fd is readable, so a frame scheduled with no host traffic
    // pending (e.g. right after a focus change) would never fire.
    frameIdle = makeShared<std::function<void(void)>>([this]() {
        sched.setFrameScheduled(false);
        const auto lifecycle = outputLifecycle.find(this);
        if (lifecycle == outputLifecycle.end() || !lifecycle->second->bufferAllowed())
            return;
        if (sched.frameInFlight() || sched.frameRunning())
            return;
        sched.frameReady.emit();
    });

    waylandState.surface = makeShared<CCWlSurface>(backend->waylandState.compositor->sendCreateSurface());

    if (!waylandState.surface->resource()) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {} failed: no surface given. Errno: {}", name, errno));
        return;
    }

    const auto manager = backendViewport.find(backend.lock().get());
    if (manager == backendViewport.end() || !manager->second.resource) return;
    outputViewport[this] = makeShared<CCWpViewport>(manager->second.resource->sendGetViewport(waylandState.surface->resource()));
    if (!outputViewport[this]->resource()) return;

    waylandState.xdgSurface = makeShared<CCXdgSurface>(backend->waylandState.xdg->sendGetXdgSurface(waylandState.surface->resource()));

    if (!waylandState.xdgSurface->resource()) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {} failed: no xdgSurface given. Errno: {}", name, errno));
        return;
    }

    waylandState.xdgSurface->setConfigure([this, lifecycle](CCXdgSurface* r, uint32_t serial) {
        backend->backend->log(AQ_LOG_DEBUG, std::format("Output {}: configure surface with {}", name, serial));
        r->sendAckConfigure(serial);
        if (!lifecycle->acknowledge())
            return;
        // ACK precedes every consumer signal and buffer commit. Weak ownership
        // prevents queued configure work from reviving a destroyed output.
        const auto weak = self;
        const auto width = lifecycle->width, height = lifecycle->height;
        const auto generation = lifecycle->presentation.acked.generation;
        backend->idleCallbacks.emplace_back([weak, lifecycle, width, height, generation]() {
            const auto output = weak.lock();
            if (!output || !lifecycle->presentation.current(generation))
                return;
            if (lifecycle->announce())
                output->backend->backend->events.newOutput.emit(SP<IOutput>(output));
            if (!lifecycle->presentation.current(generation))
                return;
            output->events.state.emit(SStateEvent{.size = {width, height}});
            if (!lifecycle->bufferAllowed() || !lifecycle->presentation.current(generation))
                return;
            output->needsFrame = true;
            output->sched.frameReady.emit();
        });
    });

    waylandState.xdgToplevel = makeShared<CCXdgToplevel>(waylandState.xdgSurface->sendGetToplevel());

    if (!waylandState.xdgToplevel->resource()) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {} failed: no xdgToplevel given. Errno: {}", name, errno));
        return;
    }

    waylandState.xdgToplevel->setWmCapabilities(
        [this](CCXdgToplevel* r, wl_array* arr) { backend->backend->log(AQ_LOG_DEBUG, std::format("Output {}: wm_capabilities received", name)); });

    waylandState.xdgToplevel->setConfigure([this, lifecycle](CCXdgToplevel* r, int32_t w, int32_t h, wl_array* arr) {
        backend->backend->log(AQ_LOG_DEBUG, std::format("Output {}: stage toplevel configure {}x{} until surface ACK", name, w, h));
        bool fullscreen = false, maximized = false;
        if (arr) for (size_t i = 0; i < arr->size / sizeof(uint32_t); ++i) {
            const auto value = static_cast<const uint32_t*>(arr->data)[i];
            fullscreen |= value == XDG_TOPLEVEL_STATE_FULLSCREEN;
            maximized |= value == XDG_TOPLEVEL_STATE_MAXIMIZED;
        }
        lifecycle->stageSize(w, h, fullscreen, maximized);
    });

    waylandState.xdgToplevel->setClose([this](CCXdgToplevel* r) { destroy(); });

    waylandState.xdgToplevel->sendSetTitle(std::format("aquamarine - {}", name).c_str());
    waylandState.xdgToplevel->sendSetAppId("aquamarine");

    auto inputRegion = makeShared<CCWlRegion>(backend->waylandState.compositor->sendCreateRegion());
    inputRegion->sendAdd(0, 0, INT32_MAX, INT32_MAX);

    waylandState.surface->sendSetInputRegion(inputRegion.get());
    waylandState.surface->sendAttach(nullptr, 0, 0);
    waylandState.surface->sendCommit();

    inputRegion->sendDestroy();

    backend->backend->log(AQ_LOG_DEBUG, std::format("Output {}: initialized", name));
}

Aquamarine::CWaylandOutput::~CWaylandOutput() {
    if (const auto state = outputLifecycle.find(this); state != outputLifecycle.end()) {
        state->second->destroy();
        outputLifecycle.erase(state);
    }
    frameGeneration.erase(this);
    events.destroy.emit();
    // frameIdle captures a raw this and may still be queued; pull it before we die.
    backend->backend->removeIdleEvent(frameIdle);
    if (waylandState.xdgToplevel)
        waylandState.xdgToplevel->sendDestroy();
    if (waylandState.xdgSurface)
        waylandState.xdgSurface->sendDestroy();
    if (const auto viewport = outputViewport.find(this); viewport != outputViewport.end()) {
        viewport->second->sendDestroy(); outputViewport.erase(viewport);
    }
    if (waylandState.surface)
        waylandState.surface->sendDestroy();
}

std::vector<SDRMFormat> Aquamarine::CWaylandOutput::getRenderFormats() {
    // TODO
    // this is technically wrong because this returns the format table formats
    // the actually supported formats are given by tranche formats
    return backend->getRenderFormats();
}

bool Aquamarine::CWaylandOutput::pendingPageFlip() {
    return sched.frameInFlight();
}

bool Aquamarine::CWaylandOutput::pendingIdleFrame() {
    return sched.frameScheduled();
}

bool Aquamarine::CWaylandOutput::destroy() {
    if (const auto state = outputLifecycle.find(this); state != outputLifecycle.end())
        state->second->destroy();
    if (backend->focusedOutput.lock() == self.lock())
        backend->focusedOutput = {};

    events.destroy.emit();
    if (const auto viewport = outputViewport.find(this); viewport != outputViewport.end()) {
        viewport->second->sendDestroy(); outputViewport.erase(viewport);
    }
    waylandState.surface->sendAttach(nullptr, 0, 0);
    waylandState.surface->sendCommit();
    waylandState.frameCallback.reset();
    sched.invalidate();
    std::erase(backend->outputs, self.lock());
    return true;
}

bool Aquamarine::CWaylandOutput::test() {
    const auto lifecycle = outputLifecycle.find(this);
    if (lifecycle == outputLifecycle.end() || !lifecycle->second->bufferAllowed() || !swapchain) return false;
    const auto snapshot = state->snapshot();
    const auto& pending = snapshot.state();
    const auto mode = pending.customMode ? pending.customMode : pending.mode;
    if (!mode) return false;
    return lifecycle->second->presentation.preflight(mode->pixelSize.x, mode->pixelSize.y,
        bool(pending.buffer), pending.buffer ? pending.buffer->size.x : 0, pending.buffer ? pending.buffer->size.y : 0,
        !pending.buffer && (pending.committed & COutputState::AQ_OUTPUT_STATE_BUFFER), pending.drmFormat != DRM_FORMAT_INVALID,
        outputViewport.contains(this));
}

bool Aquamarine::CWaylandOutput::commit() {
    const auto alive = self.lock();
    const auto lifecycle = outputLifecycle.find(this);
    const auto policy = lifecycle != outputLifecycle.end() ? lifecycle->second : nullptr;
    if (!alive || !policy || !test()) {
        backend->backend->log(AQ_LOG_WARNING, std::format("Output {}: refusing commit before initial configure ACK/publication or after destroy", name));
        return false;
    }
    const auto admissionGeneration = policy->presentation.acked.generation;
    const auto  snapshot  = state->snapshot();
    const auto& STATE     = snapshot.state();
    Vector2D    pixelSize = {};

    if (STATE.customMode)
        pixelSize = STATE.customMode->pixelSize;
    else if (STATE.mode)
        pixelSize = STATE.mode->pixelSize;
    else {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: pending state rejected: invalid mode", name));
        return false;
    }

    // Reject before swapchain, wl_buffer import, release flags or frame mutation.
    if (!NestedPolicy::validPixelDimensions(pixelSize.x, pixelSize.y) ||
        (STATE.buffer && !NestedPolicy::bufferMatchesMode(
            STATE.buffer->size.x, STATE.buffer->size.y, pixelSize.x, pixelSize.y))) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: pending state rejected: invalid mode dimensions or buffer/mode size mismatch", name));
        return false;
    }

    uint32_t format = STATE.drmFormat;

    if (format == DRM_FORMAT_INVALID) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: pending state rejected: invalid format", name));
        return false;
    }

    if (!swapchain) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: pending state rejected: no swapchain", name));
        return false;
    }

    if (!swapchain->reconfigure(SSwapchainOptions{.length = swapchain->currentOptions().length, .size = pixelSize, .format = format})) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: pending state rejected: swapchain failed reconfiguring", name));
        return false;
    }

    if (!policy->presentation.current(admissionGeneration) || !test()) return false;

    if (!STATE.buffer) {
        // if the consumer explicitly committed a null buffer, that's a violation.
        if (STATE.committed & COutputState::AQ_OUTPUT_STATE_BUFFER) {
            backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: pending state rejected: no buffer", name));
            return false;
        }

        events.commit.emit();
        state->consume(snapshot);
        return true;
    }

    auto wlBuffer = wlBufferFromBuffer(STATE.buffer);

    if (!wlBuffer) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: pending state rejected: no wlBuffer??", name));
        return false;
    }

    const auto generation = admissionGeneration;
    if (!test() || !policy->presentation.current(generation)) return false;

    if (wlBuffer->pendingRelease)
        backend->backend->log(AQ_LOG_WARNING, std::format("Output {}: pending state has a non-released buffer??", name));

    wlBuffer->pendingRelease = true;

    const auto geometry = policy->presentation.acked;
    outputViewport.at(this)->sendSetDestination(geometry.width, geometry.height);
    waylandState.xdgSurface->sendSetWindowGeometry(0, 0, geometry.width, geometry.height);
    waylandState.surface->sendSetBufferScale(1);
    waylandState.surface->sendAttach(wlBuffer->waylandState.buffer.get(), 0, 0);
    waylandState.surface->sendDamageBuffer(0, 0, INT32_MAX, INT32_MAX);

    // Register the next wl_surface.frame callback as part of this commit's pending state,
    // but only if one isn't already pending. A consumer that commits twice in quick
    // succession (e.g. cursor + buffer) shares the in-flight callback — when it fires,
    // onFrameDone runs and the next render cycle registers a fresh one. Mirrors DRM's
    // "one flip in flight per CRTC" invariant, expressed via the scheduler.
    //
    // PROTOCOL: wl_surface.frame becomes part of pending state and takes effect on the
    // NEXT wl_surface.commit. So the frame request must precede sendCommit() — sending
    // it after commit would queue the callback for a future commit that never happens.
    if (!sched.frameInFlight()) {
        frameGeneration[this] = geometry.generation;
        waylandState.frameCallback = makeShared<CCWlCallback>(waylandState.surface->sendFrame());
        waylandState.frameCallback->setDone([this](CCWlCallback* r, uint32_t ms) { onFrameDone(); });
        sched.onFrameSubmitted();
    }

    const bool mappingChanged = policy->presentation.committed.generation != geometry.generation ||
        policy->presentation.pixelWidth != pixelSize.x || policy->presentation.pixelHeight != pixelSize.y;
    waylandState.surface->sendCommit();
    policy->presentation.queueCommit(geometry.generation, pixelSize.x, pixelSize.y);
    waylandState.surfaceSize = {geometry.width, geometry.height};
    if (!policy->presentation.identityMapping() && !backend->pointers.empty() && cursorState.serial)
        backend->pointers.at(0)->pointer->sendSetCursor(cursorState.serial, nullptr, 0, 0);

    if (mappingChanged) {
        // The consumer has finished applying its monitor mode before this idle
        // runs. Reapply the latest parent point to the new logical monitor size;
        // a stationary device must not jump when its viewport is stretched.
        const auto weakOutput = self;
        for (const auto& pointer : backend->pointers) {
            const Hyprutils::Memory::CWeakPointer<CWaylandPointer> weakPointer = pointer;
            backend->backend->addIdleEvent(makeShared<std::function<void(void)>>(
                [weakOutput, weakPointer, generation = geometry.generation, pixelSize]() {
                    const auto output = weakOutput.lock();
                    const auto pointer = weakPointer.lock();
                    if (!output || !pointer) return;
                    const auto lifecycle = outputLifecycle.find(output.get());
                    if (lifecycle == outputLifecycle.end()) return;
                    const auto& mapping = lifecycle->second->presentation;
                    if (!mapping.inputAllowed() || mapping.committed.generation != generation ||
                        mapping.pixelWidth != pixelSize.x || mapping.pixelHeight != pixelSize.y) return;
                    const auto sample = parentPointerPosition.find(pointer.get());
                    if (sample == parentPointerPosition.end() || sample->second.output.lock() != output ||
                        output->backend->focusedOutput.lock() != output) return;
                    const auto coordinates = Vector2D{wl_fixed_to_double(sample->second.x), wl_fixed_to_double(sample->second.y)};
                    const auto timeMs = std::chrono::duration_cast<std::chrono::milliseconds>(
                        std::chrono::steady_clock::now().time_since_epoch()).count();
                    pointer->events.warp.emit(IPointer::SWarpEvent{
                        .timeMs = static_cast<uint32_t>(timeMs),
                        .absolute = coordinates / output->waylandState.surfaceSize,
                        .output = SP<IOutput>(output),
                    });
                    pointer->events.frame.emit();
                }));
        }
    }

    // Flush immediately: commit() runs from the consumer's render path, outside
    // dispatchEvents() (which flushes only at its top). Without this the buffer commit and
    // frame request sit unflushed, the host never sends wl_callback.done, the fd never
    // becomes readable, and the frame loop deadlocks.
    if (wl_display_flush(backend->waylandState.display) < 0 && errno != EAGAIN) {
        policy->destroy(); return false;
    }

    events.commit.emit();
    state->consume(snapshot);
    needsFrame = false;

    return true;
}

SP<IBackendImplementation> Aquamarine::CWaylandOutput::getBackend() {
    return SP<IBackendImplementation>(backend.lock());
}

SP<CWaylandBuffer> Aquamarine::CWaylandOutput::wlBufferFromBuffer(SP<IBuffer> buffer) {
    std::erase_if(backendState.buffers, [this](const auto& el) { return el.first.expired() || !swapchain->contains(el.first.lock()); });

    for (auto const& [k, v] : backendState.buffers) {
        if (k != buffer)
            continue;

        return v;
    }

    // create a new one
    auto wlBuffer = makeShared<CWaylandBuffer>(buffer, backend);

    if (!wlBuffer->good())
        return nullptr;

    backendState.buffers.emplace_back(std::make_pair<>(buffer, wlBuffer));

    return wlBuffer;
}

void Aquamarine::CWaylandOutput::onFrameDone() {
    // Hold a live output across synchronous listener calls that may destroy it.
    const auto alive = self.lock();
    const auto lifecycle = outputLifecycle.find(this);
    const auto policy = lifecycle != outputLifecycle.end() ? lifecycle->second : nullptr;
    if (!alive || !policy)
        return;
    // Mirrors DRM's handlePF: settle scheduler state, emit present, then emit frame
    // via the scheduler signal. The loop self-limits — if the consumer doesn't
    // commit (its needsFrame bit clears in renderMonitor), no new wl_surface.frame
    // is registered (registration lives in commit()), so no further done arrives.
    waylandState.frameCallback.reset();
    sched.onFrameComplete();

    const bool currentFrame = frameGeneration.contains(this) && policy->presentation.current(frameGeneration.at(this));
    frameGeneration.erase(this);
    if (!policy->bufferAllowed()) return;
    CFrameRunningGuard frameRunning(sched);

    if (currentFrame) events.present.emit(IOutput::SPresentEvent{.presented = true});

    sched.frameReady.emit();
}

bool Aquamarine::CWaylandOutput::setCursor(Hyprutils::Memory::CSharedPointer<IBuffer> buffer, const Hyprutils::Math::Vector2D& hotspot) {
    const auto lifecycle = outputLifecycle.find(this);
    if (buffer && (lifecycle == outputLifecycle.end() || !lifecycle->second->presentation.identityMapping())) {
        if (!backend->pointers.empty() && cursorState.serial)
            backend->pointers.at(0)->pointer->sendSetCursor(cursorState.serial, nullptr, 0, 0);
        return false; // Hardware cursor scaling/hotspot mapping is not qualified.
    }
    if (!cursorState.cursorSurface)
        cursorState.cursorSurface = makeShared<CCWlSurface>(backend->waylandState.compositor->sendCreateSurface());

    if (!cursorState.cursorSurface) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: Failed to create a wl_surface for the cursor", name));
        return false;
    }

    if (!buffer) {
        cursorState.cursorBuffer.reset();
        cursorState.cursorWlBuffer.reset();
        if (!backend->pointers.empty())
            backend->pointers.at(0)->pointer->sendSetCursor(cursorState.serial, nullptr, cursorState.hotspot.x, cursorState.hotspot.y);
        return true;
    }

    cursorState.cursorBuffer = buffer;
    cursorState.hotspot      = hotspot;

    if (buffer->shm().success) {
        auto attrs                    = buffer->shm();
        auto [pixelData, fmt, bufLen] = buffer->beginDataPtr(0);

        int fd = allocateSHMFile(bufLen);
        if (fd < 0) {
            backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: Failed to allocate a shm file", name));
            return false;
        }

        void* data = mmap(nullptr, bufLen, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
        if (data == MAP_FAILED) {
            backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: Failed to mmap the cursor pixel data", name));
            close(fd);
            return false;
        }

        memcpy(data, pixelData, bufLen);
        munmap(data, bufLen);

        auto pool = makeShared<CCWlShmPool>(backend->waylandState.shm->sendCreatePool(fd, bufLen));
        if (!pool) {
            backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: Failed to submit a wl_shm pool", name));
            close(fd);
            return false;
        }

        cursorState.cursorWlBuffer = makeShared<CCWlBuffer>(pool->sendCreateBuffer(0, attrs.size.x, attrs.size.y, attrs.stride, shmFormatFromDRM(attrs.format)));

        pool.reset();

        close(fd);
    } else if (auto attrs = buffer->dmabuf(); attrs.success) {
        auto params = makeShared<CCZwpLinuxBufferParamsV1>(backend->waylandState.dmabuf->sendCreateParams());

        for (int i = 0; i < attrs.planes; ++i) {
            params->sendAdd(attrs.fds.at(i), i, attrs.offsets.at(i), attrs.strides.at(i), attrs.modifier >> 32, attrs.modifier & 0xFFFFFFFF);
        }

        cursorState.cursorWlBuffer = makeShared<CCWlBuffer>(params->sendCreateImmed(attrs.size.x, attrs.size.y, attrs.format, (zwpLinuxBufferParamsV1Flags)0));
    } else {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: Failed to create a buffer for cursor: No known attrs (tried dmabuf / shm)", name));
        return false;
    }

    if (!cursorState.cursorWlBuffer) {
        backend->backend->log(AQ_LOG_ERROR, std::format("Output {}: Failed to create a buffer for cursor", name));
        return false;
    }

    cursorState.cursorSurface->sendSetBufferScale(1);
    cursorState.cursorSurface->sendSetBufferTransform(WL_OUTPUT_TRANSFORM_NORMAL);
    cursorState.cursorSurface->sendAttach(cursorState.cursorWlBuffer.get(), 0, 0);
    cursorState.cursorSurface->sendDamage(0, 0, INT32_MAX, INT32_MAX);
    cursorState.cursorSurface->sendCommit();

    // this may fail if we are not in focus
    if (!backend->pointers.empty() && cursorState.serial)
        backend->pointers.at(0)->pointer->sendSetCursor(cursorState.serial, cursorState.cursorSurface.get(), cursorState.hotspot.x, cursorState.hotspot.y);

    return true;
}

void Aquamarine::CWaylandOutput::moveCursor(const Hyprutils::Math::Vector2D& coord, bool skipSchedule) {
    ;
}

void Aquamarine::CWaylandOutput::onEnter(SP<CCWlPointer> pointer, uint32_t serial) {
    cursorState.serial = serial;

    const auto lifecycle = outputLifecycle.find(this);
    if (!cursorState.cursorSurface || lifecycle == outputLifecycle.end() || !lifecycle->second->presentation.identityMapping()) {
        pointer->sendSetCursor(serial, nullptr, 0, 0); return;
    }

    pointer->sendSetCursor(serial, cursorState.cursorSurface.get(), cursorState.hotspot.x, cursorState.hotspot.y);
}

Hyprutils::Math::Vector2D Aquamarine::CWaylandOutput::cursorPlaneSize() {
    return {-1, -1}; // no limit
}

void Aquamarine::CWaylandOutput::scheduleFrame(const scheduleFrameReason reason) {
    TRACE(backend->backend->log(AQ_LOG_TRACE,
                                std::format("CWaylandOutput::scheduleFrame: reason {}, needsFrame {}, canSchedule {}", (uint32_t)reason, needsFrame, sched.canSchedule())));
    needsFrame = true;

    // scheduled from inside a running frame, schedule it once the running frame is done.
    if (sched.frameRunning()) {
        sched.requestReschedule();
        return;
    }

    if (!sched.canSchedule())
        return;

    sched.setFrameScheduled(true);
    backend->backend->addIdleEvent(frameIdle);
}

Aquamarine::CWaylandBuffer::CWaylandBuffer(SP<IBuffer> buffer_, Hyprutils::Memory::CWeakPointer<CWaylandBackend> backend_) : buffer(buffer_), backend(backend_) {
    auto params = makeShared<CCZwpLinuxBufferParamsV1>(backend->waylandState.dmabuf->sendCreateParams());

    if (!params) {
        backend->backend->log(AQ_LOG_ERROR, "WaylandBuffer: failed to query params");
        return;
    }

    auto attrs = buffer->dmabuf();

    for (int i = 0; i < attrs.planes; ++i) {
        params->sendAdd(attrs.fds.at(i), i, attrs.offsets.at(i), attrs.strides.at(i), attrs.modifier >> 32, attrs.modifier & 0xFFFFFFFF);
    }

    waylandState.buffer = makeShared<CCWlBuffer>(params->sendCreateImmed(attrs.size.x, attrs.size.y, attrs.format, (zwpLinuxBufferParamsV1Flags)0));

    waylandState.buffer->setRelease([this](CCWlBuffer* r) { pendingRelease = false; });

    params->sendDestroy();
}

Aquamarine::CWaylandBuffer::~CWaylandBuffer() {
    if (waylandState.buffer && waylandState.buffer->resource())
        waylandState.buffer->sendDestroy();
}

bool Aquamarine::CWaylandBuffer::good() {
    return waylandState.buffer && waylandState.buffer->resource();
}

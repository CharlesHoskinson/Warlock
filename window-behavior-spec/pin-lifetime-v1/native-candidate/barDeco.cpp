#include "barDeco.hpp"
#include <stdexcept>
#include "atlasAdapter.hpp"
#include "dragBridge.hpp"
#include "pinBridge.hpp"

#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/desktop/state/FocusState.hpp>
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/desktop/state/LayerState.hpp>
#include <hyprland/src/desktop/state/ViewHitTester.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <hyprland/src/desktop/view/LayerSurface.hpp>
#include <hyprland/src/helpers/MiscFunctions.hpp>
#include <hyprland/src/managers/SeatManager.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <hyprland/src/render/Renderer.hpp>
#include <hyprland/src/config/ConfigManager.hpp>
#include <hyprland/src/config/shared/animation/AnimationTree.hpp>
#include <hyprland/src/config/shared/parserUtils/ParserUtils.hpp>
#include <hyprland/src/config/supplementary/executor/Executor.hpp>
#include <hyprland/src/managers/eventLoop/EventLoopManager.hpp>
#include <hyprland/src/config/shared/actions/ConfigActions.hpp>
#include <hyprland/src/animation/AnimationManager.hpp>
#include <hyprland/src/protocols/LayerShell.hpp>
#include <hyprland/src/event/EventBus.hpp>
#include <hyprland/src/layout/LayoutManager.hpp>
#include <hyprland/src/render/OpenGL.hpp>
#include <hyprland/src/state/MonitorState.hpp>

#include "globals.hpp"
#include "BarPassElement.hpp"

#include <climits>

using namespace Render::GL;

static CHyprColor configColor(Config::INTEGER color) {
    return CHyprColor{static_cast<uint64_t>(color)};
}

// Hyprbars runs button commands asynchronously. Resolve the owning window at
// click time so a later focus change cannot redirect close/minimize/pin/snap.
static std::string commandForWindow(std::string command, const PHLWINDOW& window) {
    if (!window)
        return command;

    constexpr std::string_view marker = "%WINDOW_ADDRESS%";
    const auto address = std::format("0x{:x}", (uintptr_t)window.get());
    size_t pos = 0;
    while ((pos = command.find(marker, pos)) != std::string::npos) {
        command.replace(pos, marker.size(), address);
        pos += address.size();
    }
    return command;
}

CHyprBar::CHyprBar(PHLWINDOW pWindow) : IHyprWindowDecoration(pWindow) {
    m_pWindow = pWindow;
    m_hoverPollTimer = makeShared<CEventLoopTimer>(std::chrono::milliseconds(100), [this](SP<CEventLoopTimer> timer, void*) {
        updateMaximizeHover();
        timer->updateTimeout(std::chrono::milliseconds(100));
    }, nullptr);
    g_pEventLoopManager->addTimer(m_hoverPollTimer);

    const auto PMONITOR         = pWindow->m_monitor.lock();
    PMONITOR->m_scheduledRecalc = true;

    // button events
    m_pMouseButtonCallback = Event::bus()->m_events.input.mouse.button.listen([&](IPointer::SButtonEvent e, Event::SCallbackInfo& info) { onMouseButton(info, e); });
    m_pKeyboardCallback = Event::bus()->m_events.input.keyboard.key.listen([&](IKeyboard::SKeyEvent event, Event::SCallbackInfo&) {
        // Core cancels an active native move on keyboard input. Apply the same
        // interruption to an unstarted caption press, including Escape. The key
        // keeps its ordinary input route and we retain the swallowed release.
        if (m_bDragPending && event.state == WL_KEYBOARD_KEY_STATE_PRESSED) {
            m_bDragPending = false;
            m_captionPress = {};
        }
    });
    m_pTouchDownCallback   = Event::bus()->m_events.input.touch.down.listen([&](ITouch::SDownEvent e, Event::SCallbackInfo& info) { onTouchDown(info, e); });
    m_pTouchUpCallback     = Event::bus()->m_events.input.touch.up.listen([&](ITouch::SUpEvent e, Event::SCallbackInfo& info) { onTouchUp(info, e); });

    // move events
    m_pTouchMoveCallback = Event::bus()->m_events.input.touch.motion.listen([&](ITouch::SMotionEvent e, Event::SCallbackInfo& info) { onTouchMove(info, e); });
    m_pMouseMoveCallback = Event::bus()->m_events.input.mouse.move.listen([&](Vector2D c, Event::SCallbackInfo& info) { onMouseMove(c); });

    Animation::mgr()->createAnimation(configColor(g_pGlobalState->config.barColor->value()), m_cRealBarColor, Config::animationTree()->getAnimationPropertyConfig("border"),
                                      pWindow, AVARDAMAGE_NONE);
    m_cRealBarColor->setUpdateCallback([&](auto) { damageEntire(); });
}

CHyprBar::~CHyprBar() {
    if (m_hoverPollTimer) {
        m_hoverPollTimer->cancel();
        g_pEventLoopManager->removeTimer(m_hoverPollTimer);
    }
    if (m_maximizeHoverTimer) {
        m_maximizeHoverTimer->cancel();
        g_pEventLoopManager->removeTimer(m_maximizeHoverTimer);
    }
    std::erase(g_pGlobalState->bars, m_self);
}

SDecorationPositioningInfo CHyprBar::getPositioningInfo() {
    const auto                 HEIGHT     = g_pGlobalState->config.barHeight->value();
    const auto                 ENABLED    = g_pGlobalState->config.enabled->value();
    const auto                 PRECEDENCE = g_pGlobalState->config.barPrecedenceOverBorder->value();

    SDecorationPositioningInfo info;
    info.policy         = m_hidden ? DECORATION_POSITION_ABSOLUTE : DECORATION_POSITION_STICKY;
    info.edges          = DECORATION_EDGE_TOP;
    info.priority       = PRECEDENCE ? 10005 : 5000;
    info.reserved       = true;
    info.desiredExtents = {{0, m_hidden || !ENABLED ? 0 : HEIGHT}, {0, 0}};
    return info;
}

void CHyprBar::onPositioningReply(const SDecorationPositioningReply& reply) {
    if (reply.assignedGeometry.size() != m_bAssignedBox.size())
        m_bWindowSizeChanged = true;

    m_bAssignedBox = reply.assignedGeometry;
}

std::string CHyprBar::getDisplayName() {
    return "Hyprbar";
}

bool CHyprBar::inputIsValid() {
    if (m_hidden)
        return false;

    if (g_pSeatManager->m_seatGrab && !g_pSeatManager->m_seatGrab->accepts(m_pWindow->wlSurface()->resource()))
        return false;

    const auto MOUSE    = g_pInputManager->getMouseCoordsInternal();
    auto       PMONITOR = Desktop::focusState()->monitor();

    if (!PMONITOR)
        return false;

    Desktop::CViewHitTester hitTester{*Desktop::viewState()};

    const auto              WINDOWATCURSOR = hitTester.windowAt(MOUSE, Desktop::View::RESERVED_EXTENTS | Desktop::View::INPUT_EXTENTS | Desktop::View::ALLOW_FLOATING);

    auto                    focusState = Desktop::focusState();
    auto                    window     = focusState->window();

    if (WINDOWATCURSOR != m_pWindow && m_pWindow != window)
        return false;

    PHLLS    foundSurface = nullptr;
    Vector2D surfaceCoords;

    // Check Top Layer
    hitTester.layerSurfaceAt(MOUSE, &PMONITOR->m_layerSurfaceLayers[ZWLR_LAYER_SHELL_V1_LAYER_TOP], &surfaceCoords, &foundSurface);
    if (foundSurface)
        return false;

    // Check Overlay Layer
    hitTester.layerSurfaceAt(MOUSE, &PMONITOR->m_layerSurfaceLayers[ZWLR_LAYER_SHELL_V1_LAYER_OVERLAY], &surfaceCoords, &foundSurface);
    if (foundSurface)
        return false;

    return true;
}

void CHyprBar::onMouseButton(Event::SCallbackInfo& info, IPointer::SButtonEvent e) {
    // A release belongs to our pending drag even if focus moved or a menu
    // covered the titlebar while the button was held.
    if (e.state != WL_POINTER_BUTTON_STATE_PRESSED && (m_bDraggingThis || m_bDragPending || m_bCancelledDown)) {
        handleUpEvent(info);
        return;
    }
    if (info.cancelled)
        return;
    if (!inputIsValid())
        return;

    if (e.state != WL_POINTER_BUTTON_STATE_PRESSED) {
        handleUpEvent(info);
        return;
    }

    if (m_maximizeHoverTimer)
        m_maximizeHoverTimer->updateTimeout(std::nullopt);

    if (e.button == BTN_RIGHT) {
        const auto COORDS = cursorRelativeToBar();
        if (!VECINRECT(COORDS, 0, 0, assignedBoxGlobal().w, g_pGlobalState->config.barHeight->value()) || hoveredButton() >= 0)
            return;
        const auto command = g_pGlobalState->config.onRightClick->value();
        if (!command.empty()) {
            const auto window = m_pWindow.lock();
            Desktop::focusState()->fullWindowFocus(window, Desktop::FOCUS_REASON_CLICK);
            if (window->m_isFloating)
                Desktop::windowState()->raise(window);
            info.cancelled = true;
            m_bCancelledDown = true;
            Config::Supplementary::executor()->spawn(commandForWindow(command, window));
        }
        return;
    }
    if (e.button != BTN_LEFT)
        return;

    handleDownEvent(info, std::nullopt);
}

void CHyprBar::onTouchDown(Event::SCallbackInfo& info, ITouch::SDownEvent e) {
    // Don't do anything if you're already grabbed a window with another finger
    if (!inputIsValid() || e.touchID != 0)
        return;

    handleDownEvent(info, e);
}

void CHyprBar::onTouchUp(Event::SCallbackInfo& info, ITouch::SUpEvent e) {
    if (!m_bDragPending || !m_bTouchEv || e.touchID != m_touchId)
        return;

    handleUpEvent(info);
}

void CHyprBar::onMouseMove(Vector2D coords) {
    updateMaximizeHover();
    // ensure proper redraws of button icons on hover when using hardware cursors
    if (g_pGlobalState->config.iconOnHover->value())
        damageOnButtonHover();

    if (!m_bDragPending || m_bTouchEv || !validMapped(m_pWindow) || m_touchId != 0)
        return;

    m_bDragPending = false;
    handleMovement();
}

int CHyprBar::hoveredButton() {
    const auto coords = cursorRelativeToBar();
    const auto padding = g_pGlobalState->config.barPadding->value();
    const auto buttonPadding = g_pGlobalState->config.barButtonPadding->value();
    const auto height = g_pGlobalState->config.barHeight->value();
    const bool right = g_pGlobalState->config.barButtonsAlignment->value() != "left";
    float offset = padding;
    for (size_t i = 0; i < g_pGlobalState->buttons.size(); ++i) {
        const auto& button = g_pGlobalState->buttons[i];
        const Vector2D pos = Vector2D{right ? assignedBoxGlobal().w - buttonPadding - button.size - offset : offset, (height - button.size) / 2.0}.floor();
        if (VECINRECT(coords, pos.x, pos.y, pos.x + button.size + buttonPadding, pos.y + button.size))
            return i;
        offset += buttonPadding + button.size;
    }
    return -1;
}

void CHyprBar::updateMaximizeHover() {
    if (!validMapped(m_pWindow) || g_pGlobalState->config.onMaximizeHover->value().empty())
        return;
    const auto index = hoveredButton();
    Desktop::CViewHitTester hitTester{*Desktop::viewState()};
    const auto underCursor = hitTester.windowAt(g_pInputManager->getMouseCoordsInternal(), Desktop::View::RESERVED_EXTENTS | Desktop::View::INPUT_EXTENTS | Desktop::View::ALLOW_FLOATING);
    const bool hovered = index >= 0 && g_pGlobalState->buttons[index].icon == "□" && (underCursor == m_pWindow || Desktop::focusState()->window() == m_pWindow) && inputIsValid() && !m_bDraggingThis && !m_bDragPending;
    if (hovered == m_maximizeHovered)
        return;
    m_maximizeHovered = hovered;
    if (!m_maximizeHoverTimer) {
        m_maximizeHoverTimer = makeShared<CEventLoopTimer>(std::nullopt, [this](SP<CEventLoopTimer>, void*) {
            if (m_maximizeHovered && validMapped(m_pWindow) && inputIsValid() && !m_bDraggingThis) {
                const auto command = g_pGlobalState->config.onMaximizeHover->value();
                if (!command.empty())
                    Config::Supplementary::executor()->spawn(commandForWindow(command, m_pWindow.lock()));
            }
        }, nullptr);
        g_pEventLoopManager->addTimer(m_maximizeHoverTimer);
    }
    m_maximizeHoverTimer->updateTimeout(hovered ? std::optional<Time::steady_dur>{std::chrono::milliseconds(450)} : std::nullopt);
}

void CHyprBar::onTouchMove(Event::SCallbackInfo& info, ITouch::SMotionEvent e) {
    if (!m_bDragPending || !m_bTouchEv || !validMapped(m_pWindow) || e.touchID != m_touchId)
        return;

    auto PMONITOR     = m_pWindow->m_monitor.lock();
    PMONITOR          = PMONITOR ? PMONITOR : Desktop::focusState()->monitor();
    const auto COORDS = Vector2D(PMONITOR->m_position.x + e.pos.x * PMONITOR->m_size.x, PMONITOR->m_position.y + e.pos.y * PMONITOR->m_size.y);

    if (!m_bDraggingThis) {
        // Initial setup for dragging a window.
        g_pKeybindManager->m_dispatchers["setfloating"]("activewindow");
        g_pKeybindManager->m_dispatchers["resizewindowpixel"]("exact 50% 50%,activewindow");
        // pin it so you can change workspaces while dragging a window
        g_pKeybindManager->m_dispatchers["pin"]("activewindow");
    }
    g_pKeybindManager->m_dispatchers["movewindowpixel"](std::format("exact {} {},activewindow", (int)(COORDS.x - (assignedBoxGlobal().w / 2)), (int)COORDS.y));
    m_bDraggingThis = true;
}

void CHyprBar::handleDownEvent(Event::SCallbackInfo& info, std::optional<ITouch::SDownEvent> touchEvent) {
    m_bTouchEv = touchEvent.has_value();
    if (m_bTouchEv)
        m_touchId = touchEvent.value().touchID;

    const auto PWINDOW = m_pWindow.lock();

    auto       COORDS = cursorRelativeToBar();
    if (m_bTouchEv) {
        ITouch::SDownEvent e        = touchEvent.value();
        PHLMONITOR         PMONITOR = nullptr;
        for (auto& m : State::monitorState()->monitors()) {
            if (m->m_name == (!e.device->m_boundOutput.empty() ? e.device->m_boundOutput : "")) {
                PMONITOR = m;
                break;
            }
        }
        PMONITOR = PMONITOR ? PMONITOR : Desktop::focusState()->monitor();
        COORDS   = Vector2D(PMONITOR->m_position.x + e.pos.x * PMONITOR->m_size.x, PMONITOR->m_position.y + e.pos.y * PMONITOR->m_size.y) - assignedBoxGlobal().pos();
    }

    const auto HEIGHT           = g_pGlobalState->config.barHeight->value();
    const auto BARBUTTONPADDING = g_pGlobalState->config.barButtonPadding->value();
    const auto BARPADDING       = g_pGlobalState->config.barPadding->value();
    const auto ALIGNBUTTONS     = g_pGlobalState->config.barButtonsAlignment->value();
    const auto ON_DOUBLE_CLICK  = g_pGlobalState->config.onDoubleClick->value();

    const bool BUTTONSRIGHT = ALIGNBUTTONS != "left";

    if (!VECINRECT(COORDS, 0, 0, assignedBoxGlobal().w, HEIGHT - 1)) {

        if (m_bDraggingThis) {
            if (m_bTouchEv)
                g_pKeybindManager->m_dispatchers["settiled"]("activewindow");
            g_pKeybindManager->m_dispatchers["mouse"]("0movewindow");
            Log::logger->log(Log::DEBUG, "[hyprbars] Dragging ended on {:x}", (uintptr_t)PWINDOW.get());
        }

        m_bDraggingThis = false;
        m_bDragPending  = false;
        m_bTouchEv      = false;
        return;
    }

    if (Desktop::focusState()->window() != PWINDOW)
        Desktop::focusState()->fullWindowFocus(PWINDOW, Desktop::FOCUS_REASON_CLICK);

    if (PWINDOW->m_isFloating)
        Desktop::windowState()->raise(PWINDOW);

    info.cancelled   = true;
    m_bCancelledDown = true;

    if (doButtonPress(BARPADDING, BARBUTTONPADDING, HEIGHT, COORDS, BUTTONSRIGHT))
        return;

    if (!ON_DOUBLE_CLICK.empty() &&
        std::chrono::duration_cast<std::chrono::milliseconds>(Time::steadyNow() - m_lastMouseDown).count() < 400 /* Arbitrary delay I found suitable */) {
        Config::Supplementary::executor()->spawn(commandForWindow(ON_DOUBLE_CLICK, PWINDOW));
        m_bDragPending = false;
    } else {
        m_lastMouseDown = Time::steadyNow();
        m_bDragPending  = true;
        m_captionPress = g_pInputManager->getMouseCoordsInternal();
    }
}

void CHyprBar::handleUpEvent(Event::SCallbackInfo& info) {
    if (m_pWindow.lock() != Desktop::focusState()->window() && !m_bDraggingThis && !m_bDragPending && !m_bCancelledDown)
        return;

    if (m_bCancelledDown)
        info.cancelled = true;

    m_bCancelledDown = false;

    if (m_bDraggingThis) {
        g_pKeybindManager->changeMouseBindMode(MBIND_INVALID);
        m_bDraggingThis = false;
        if (m_bTouchEv)
            (void)Config::Actions::floatWindow(Config::Actions::eTogglableAction::TOGGLE_ACTION_DISABLE);

        Log::logger->log(Log::DEBUG, "[hyprbars] Dragging ended on {:x}", (uintptr_t)m_pWindow.lock().get());

        const auto ON_DRAG_END = g_pGlobalState->config.onDragEnd->value();
        if (!ON_DRAG_END.empty())
            Config::Supplementary::executor()->spawn(commandForWindow(ON_DRAG_END, m_pWindow.lock()));
    }

    m_bDragPending = false;
    m_bTouchEv     = false;
    m_touchId      = 0;
}

void CHyprBar::handleMovement() {
    if (!startCaptionDrag(m_pWindow.lock(), m_captionPress))
        g_pKeybindManager->changeMouseBindMode(MBIND_MOVE);
    m_bDraggingThis = true;
    Log::logger->log(Log::DEBUG, "[hyprbars] Dragging initiated on {:x}", (uintptr_t)m_pWindow.lock().get());

    const auto ON_DRAG_START = g_pGlobalState->config.onDragStart->value();
    if (!ON_DRAG_START.empty())
        Config::Supplementary::executor()->spawn(commandForWindow(ON_DRAG_START, m_pWindow.lock()));
    return;
}

bool CHyprBar::doButtonPress(Config::INTEGER barPadding, Config::INTEGER barButtonPadding, Config::INTEGER barHeight, Vector2D COORDS, const bool BUTTONSRIGHT) {
    //check if on a button
    float offset = barPadding;

    for (auto& b : g_pGlobalState->buttons) {
        const auto BARBUF     = Vector2D{(int)assignedBoxGlobal().w, barHeight};
        Vector2D   currentPos = Vector2D{(BUTTONSRIGHT ? BARBUF.x - barButtonPadding - b.size - offset : offset), (BARBUF.y - b.size) / 2.0}.floor();

        if (VECINRECT(COORDS, currentPos.x, currentPos.y, currentPos.x + b.size + barButtonPadding, currentPos.y + b.size)) {
            // hit on close
            if (b.cmd == "hyprbars:pin-toggle") {
                std::string reason;
                if (!toggleCapturedPin(m_pWindow.lock(), reason))
                    Log::logger->log(Log::WARN, "[hyprbars] Captured pin refused: {}", reason);
            } else {
                g_pKeybindManager->m_dispatchers["exec"](commandForWindow(b.cmd, m_pWindow.lock()));
            }
            return true;
        }

        offset += barButtonPadding + b.size;
    }
    return false;
}

void CHyprBar::renderBarTitle(const Vector2D& bufferSize, const float scale) {
    const auto COLORVAL         = g_pGlobalState->config.textColor->value();
    const auto SIZE             = g_pGlobalState->config.barTextSize->value();
    const auto WEIGHT           = g_pGlobalState->config.barTextWeight->value();
    const auto FONT             = g_pGlobalState->config.barTextFont->value();
    const auto ALIGN            = g_pGlobalState->config.barTextAlign->value();
    const auto BARPADDING       = g_pGlobalState->config.barPadding->value();
    const auto BARBUTTONPADDING = g_pGlobalState->config.barButtonPadding->value();

    float      buttonSizes = BARBUTTONPADDING;
    for (auto& b : g_pGlobalState->buttons) {
        buttonSizes += b.size + BARBUTTONPADDING;
    }

    const int  scaledSize        = std::round(SIZE * scale);
    const auto scaledButtonsSize = buttonSizes * scale;
    const auto scaledBarPadding  = BARPADDING * scale;
    const int  paddingTotal      = scaledBarPadding * 2 + scaledButtonsSize + (ALIGN != "left" ? scaledButtonsSize : 0);
    const int  maxWidth          = std::clamp(static_cast<int>(bufferSize.x - paddingTotal), 0, INT_MAX);

    const CHyprColor COLOR = m_bForcedTitleColor.value_or(configColor(COLORVAL));
    const CaptionCache::TitleKey key{scale,bufferSize.x,bufferSize.y,scaledSize,WEIGHT.m_value,maxWidth,
        static_cast<int>(BARPADDING),static_cast<int>(BARBUTTONPADDING),m_szLastTitle,FONT,ALIGN,{COLOR.r,COLOR.g,COLOR.b,COLOR.a}};
    if(m_titleRasterKey && *m_titleRasterKey==key && m_pTextTex && m_pTextTex->m_texID!=0)return;
    m_titleRasterKey=key;
    if (m_szLastTitle.empty() || maxWidth < 1) {
        m_pTextTex = nullptr;
        return;
    }

    m_pTextTex             = g_pHyprRenderer->renderText(m_szLastTitle, COLOR, scaledSize, false, FONT, maxWidth, WEIGHT.m_value);
}

size_t CHyprBar::getVisibleButtonCount(Config::INTEGER barButtonPadding, Config::INTEGER barPadding, const Vector2D& bufferSize, const float scale) {
    float  availableSpace = bufferSize.x - barPadding * scale * 2;
    size_t count          = 0;

    for (const auto& button : g_pGlobalState->buttons) {
        const float buttonSpace = (button.size + barButtonPadding) * scale;
        if (availableSpace >= buttonSpace) {
            count++;
            availableSpace -= buttonSpace;
        } else
            break;
    }

    return count;
}

void CHyprBar::renderBarButtons(CBox* barBox, const float scale, const float a) {
    const auto BARBUTTONPADDING = g_pGlobalState->config.barButtonPadding->value();
    const auto BARPADDING       = g_pGlobalState->config.barPadding->value();
    const auto ALIGNBUTTONS     = g_pGlobalState->config.barButtonsAlignment->value();
    const auto INACTIVECOLOR    = g_pGlobalState->config.inactiveButtonColor->value();

    const bool BUTTONSRIGHT    = ALIGNBUTTONS != "left";
    const auto visibleCount    = getVisibleButtonCount(BARBUTTONPADDING, BARPADDING, Vector2D{barBox->w, barBox->h}, scale);

    int        offset = BARPADDING * scale;
    for (size_t i = 0; i < visibleCount; ++i) {
        auto&      button           = g_pGlobalState->buttons[i];
        const auto scaledButtonSize = button.size * scale;
        const auto scaledButtonsPad = BARBUTTONPADDING * scale;

        auto       color = button.bgcol;

        if (INACTIVECOLOR > 0) {
            color = m_bWindowHasFocus ? color : configColor(INACTIVECOLOR);

        }

        color.a *= a;

        CBox buttonBox = {barBox->x + (BUTTONSRIGHT ? barBox->w - offset - scaledButtonSize : offset), barBox->y + (barBox->h - scaledButtonSize) / 2.0, scaledButtonSize,
                          scaledButtonSize};
        buttonBox.round();

        g_pHyprOpenGL->renderRect(buttonBox, color, {.round = static_cast<int>(std::round(scaledButtonSize / 2.0)), .roundingPower = 2.F});

        offset += scaledButtonsPad + scaledButtonSize;
    }
}

void CHyprBar::renderBarButtonsText(CBox* barBox, const float scale, const float a) {
    const auto HEIGHT           = g_pGlobalState->config.barHeight->value();
    const auto BARBUTTONPADDING = g_pGlobalState->config.barButtonPadding->value();
    const auto BARPADDING       = g_pGlobalState->config.barPadding->value();
    const auto ALIGNBUTTONS     = g_pGlobalState->config.barButtonsAlignment->value();
    const auto ICONONHOVER      = g_pGlobalState->config.iconOnHover->value();

    const bool BUTTONSRIGHT = ALIGNBUTTONS != "left";
    const auto visibleCount = getVisibleButtonCount(BARBUTTONPADDING, BARPADDING, Vector2D{barBox->w, barBox->h}, scale);
    const auto COORDS       = cursorRelativeToBar();

    m_iconRasters.resize(g_pGlobalState->buttons.size());
    int        offset        = BARPADDING * scale;
    float      noScaleOffset = BARPADDING;

    for (size_t i = 0; i < visibleCount; ++i) {
        auto&      button           = g_pGlobalState->buttons[i];
        const auto scaledButtonSize = button.size * scale;
        const auto scaledButtonsPad = BARBUTTONPADDING * scale;

        // check if hovering here
        const auto BARBUF     = Vector2D{(int)assignedBoxGlobal().w, HEIGHT};
        Vector2D   currentPos = Vector2D{(BUTTONSRIGHT ? BARBUF.x - BARBUTTONPADDING - button.size - noScaleOffset : noScaleOffset), (BARBUF.y - button.size) / 2.0}.floor();
        bool       hovering   = VECINRECT(COORDS, currentPos.x, currentPos.y, currentPos.x + button.size + BARBUTTONPADDING, currentPos.y + button.size);
        noScaleOffset += BARBUTTONPADDING + button.size;

        auto& raster=m_iconRasters[i];
        const auto fgcol = button.userfg ? button.fgcol : (button.bgcol.r + button.bgcol.g + button.bgcol.b < 1) ? CHyprColor(0xFFFFFFFF) : CHyprColor(0xFF000000);
        const CaptionCache::IconKey key{scale,scaledButtonSize,scaledButtonSize,button.size,
            static_cast<int>(std::round(button.size*.62*scale)),button.userfg,button.icon,"sans",
            {fgcol.r,fgcol.g,fgcol.b,fgcol.a},{button.bgcol.r,button.bgcol.g,button.bgcol.b,button.bgcol.a}};
        if(!raster.matches(key) || (raster.texture && raster.texture->m_texID==0)) {
            raster.store(key,button.icon.empty() ? nullptr : g_pHyprRenderer->renderText(button.icon,fgcol,key.pixelSize,false,key.font,scaledButtonSize));
        }
        const auto& icon=raster.texture;
        if (!icon || icon->m_texID == 0)continue;

        const auto iconX = barBox->x + (BUTTONSRIGHT ? barBox->width - offset - scaledButtonSize / 2.0 : offset + scaledButtonSize / 2.0) - icon->m_size.x / 2.0;
        const auto iconY = barBox->y + barBox->height / 2.0 - icon->m_size.y / 2.0;
        CBox       pos   = {iconX, iconY, icon->m_size.x, icon->m_size.y};

        if (!ICONONHOVER || (ICONONHOVER && m_iButtonHoverState > 0))
            g_pHyprOpenGL->renderTexture(icon, pos, {.a = a});
        offset += scaledButtonsPad + scaledButtonSize;

        bool currentBit = (m_iButtonHoverState & (1 << i)) != 0;
        if (!g_pHyprRenderer->m_bRenderingSnapshot && hovering != currentBit) {
            m_iButtonHoverState ^= (1 << i);
            // damage to get rid of some artifacts when icons are "hidden"
            damageEntire();
        }
    }
}

void CHyprBar::draw(PHLMONITOR pMonitor, const float& a) {
    const auto ENABLED = g_pGlobalState->config.enabled->value();

    if (m_bLastEnabledState != ENABLED) {
        m_bLastEnabledState = ENABLED;
        g_pDecorationPositioner->repositionDeco(this);
    }

    if (m_hidden || !validMapped(m_pWindow) || !ENABLED)
        return;

    const auto PWINDOW = m_pWindow.lock();

    if (!PWINDOW->m_ruleApplicator->decorate().valueOrDefault())
        return;

    auto data = CBarPassElement::SBarData{this, a};
    g_pHyprRenderer->m_renderPass.add(makeUnique<CBarPassElement>(data));
}

void CHyprBar::renderPass(PHLMONITOR pMonitor, const float& a) {
    const bool exportPass=g_pHyprRenderer->m_bRenderingSnapshot && g_pHyprRenderer->m_renderData.projectionType==Render::RPT_EXPORT;
    // Export may generate temporary rasters, but normal texture references and
    // flags survive exactly, including early returns and exceptions.
    const auto oldText=exportPass ? m_pTextTex : nullptr;const auto oldKey=exportPass ? m_titleRasterKey : std::nullopt;
    const auto oldIcons=exportPass ? m_iconRasters : decltype(m_iconRasters){};
    const auto oldTitle=exportPass ? m_szLastTitle : std::string{};const auto oldExtents=m_seExtents;
    const auto oldSize=m_bWindowSizeChanged,oldDirty=m_bButtonsDirty,oldColor=m_bTitleColorChanged,oldFocus=m_bWindowHasFocus;
    const auto oldHover=m_iButtonHoverState;const auto oldHeight=m_iLastHeight;
    CaptionCache::RestoreScope restore([&] {
        m_pTextTex=oldText;m_titleRasterKey=oldKey;m_iconRasters=oldIcons;m_szLastTitle=oldTitle;m_seExtents=oldExtents;
        m_bWindowSizeChanged=oldSize;m_bButtonsDirty=oldDirty;m_bTitleColorChanged=oldColor;m_bWindowHasFocus=oldFocus;
        m_iButtonHoverState=oldHover;m_iLastHeight=oldHeight;
    },exportPass);
    const auto  PWINDOW = m_pWindow.lock();

    static auto PENABLEBLURGLOBAL = CConfigValue<Config::BOOL>("decoration:blur:enabled");
    const auto  BARCOLOR          = g_pGlobalState->config.barColor->value();
    const auto  HEIGHT            = g_pGlobalState->config.barHeight->value();
    const auto  PRECEDENCE        = g_pGlobalState->config.barPrecedenceOverBorder->value();
    const auto  ALIGNBUTTONS      = g_pGlobalState->config.barButtonsAlignment->value();
    const auto  ENABLETITLE       = g_pGlobalState->config.barTitleEnabled->value();
    const auto  ENABLEBLUR        = g_pGlobalState->config.barBlur->value();
    const auto  INACTIVECOLOR     = g_pGlobalState->config.inactiveButtonColor->value();

    if (INACTIVECOLOR > 0) {
        bool currentWindowFocus = PWINDOW == Desktop::focusState()->window();
        if (currentWindowFocus != m_bWindowHasFocus) {
            m_bWindowHasFocus = currentWindowFocus;
            m_bButtonsDirty   = true;
        }
    }

    const CHyprColor DEST_COLOR = m_bForcedBarColor.value_or(configColor(BARCOLOR));
    if (!exportPass && DEST_COLOR != m_cRealBarColor->goal())
        *m_cRealBarColor = DEST_COLOR;

    CHyprColor color = m_cRealBarColor->value();

    color.a *= a;
    const bool BUTTONSRIGHT = ALIGNBUTTONS != "left";
    const bool SHOULDBLUR   = ENABLEBLUR && *PENABLEBLURGLOBAL && color.a < 1.F;
    if(exportPass && SHOULDBLUR)throw std::runtime_error("atlas blurred caption backdrop unsupported");

    if (HEIGHT < 1) {
        m_iLastHeight = HEIGHT;
        return;
    }

    const auto PWORKSPACE      = PWINDOW->m_workspace;
    const auto WORKSPACEOFFSET = PWORKSPACE && !PWINDOW->m_pinned ? PWORKSPACE->m_renderOffset->value() : Vector2D();

    const auto ROUNDING = PWINDOW->rounding() + (PRECEDENCE ? 0 : PWINDOW->getRealBorderSize());

    const auto scaledRounding = ROUNDING > 0 ? ROUNDING * pMonitor->m_scale - 2 /* idk why but otherwise it looks bad due to the gaps */ : 0;

    m_seExtents = {{0, HEIGHT}, {}};

    const auto DECOBOX = assignedBoxGlobal();

    const auto BARBUF = DECOBOX.size() * pMonitor->m_scale;

    CBox       titleBarBox = {DECOBOX.x - pMonitor->m_position.x, DECOBOX.y - pMonitor->m_position.y, DECOBOX.w,
                              DECOBOX.h + ROUNDING * 3 /* to fill the bottom cuz we can't disable rounding there */};

    titleBarBox.translate(PWINDOW->m_floatingOffset).scale(pMonitor->m_scale).round();
    titleBarBox=atlasCaptionClip(titleBarBox);

    if (titleBarBox.w < 1 || titleBarBox.h < 1)
        return;

    if(g_pHyprRenderer->m_bRenderingSnapshot && g_pHyprRenderer->m_renderData.projectionType==Render::RPT_EXPORT) {
        auto atlasClip=titleBarBox;
        // titleBarBox is already normalized for atlas export.
        g_pHyprOpenGL->scissor(atlasClip,false);
    } else g_pHyprOpenGL->scissor(titleBarBox);

    if (ROUNDING) {
        // the +1 is a shit garbage temp fix until renderRect supports an alpha matte
        CBox windowBox = {PWINDOW->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT).x + PWINDOW->m_floatingOffset.x - pMonitor->m_position.x + 1,
                          PWINDOW->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT).y + PWINDOW->m_floatingOffset.y - pMonitor->m_position.y + 1,
                          PWINDOW->size(Desktop::View::IGeometric::GEOMETRIC_CURRENT).x - 2, PWINDOW->size(Desktop::View::IGeometric::GEOMETRIC_CURRENT).y - 2};

        if (windowBox.w < 1 || windowBox.h < 1)
            return;

        glClearStencil(0);
        glClear(GL_STENCIL_BUFFER_BIT);

        g_pHyprOpenGL->setCapStatus(GL_STENCIL_TEST, true);

        glStencilFunc(GL_ALWAYS, 1, -1);
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE);

        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE);

        windowBox.translate(WORKSPACEOFFSET).scale(pMonitor->m_scale).round();
        windowBox=atlasCaptionClip(windowBox);
        g_pHyprOpenGL->renderRect(windowBox, CHyprColor(0, 0, 0, 0), {.round = scaledRounding, .roundingPower = m_pWindow->roundingPower()});
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);

        glStencilFunc(GL_NOTEQUAL, 1, -1);
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE);
    }

    if (SHOULDBLUR)
        g_pHyprOpenGL->renderRect(titleBarBox, color, {.round = scaledRounding, .roundingPower = m_pWindow->roundingPower(), .blur = true, .blurA = a});
    else
        g_pHyprOpenGL->renderRect(titleBarBox, color, {.round = scaledRounding, .roundingPower = m_pWindow->roundingPower()});

    // render title
    if (ENABLETITLE) {
        m_szLastTitle = PWINDOW->m_title;
        renderBarTitle(BARBUF, pMonitor->m_scale);
    }

    if (ROUNDING) {
        // cleanup stencil
        glClearStencil(0);
        glClear(GL_STENCIL_BUFFER_BIT);
        g_pHyprOpenGL->setCapStatus(GL_STENCIL_TEST, false);
        glStencilMask(-1);
        glStencilFunc(GL_ALWAYS, 1, 0xFF);
    }

    CBox textBox = {titleBarBox.x, titleBarBox.y, (int)BARBUF.x, (int)BARBUF.y};
    if (ENABLETITLE && m_pTextTex) {
        const auto BARPADDING       = g_pGlobalState->config.barPadding->value();
        const auto BARBUTTONPADDING = g_pGlobalState->config.barButtonPadding->value();
        const auto ALIGN            = g_pGlobalState->config.barTextAlign->value();

        float      buttonSizes = BARBUTTONPADDING;
        for (auto& b : g_pGlobalState->buttons) {
            buttonSizes += b.size + BARBUTTONPADDING;
        }

        const auto scaledBorderSize  = PWINDOW->getRealBorderSize() * pMonitor->m_scale;
        const auto scaledButtonsSize = buttonSizes * pMonitor->m_scale;
        const auto scaledBarPadding  = BARPADDING * pMonitor->m_scale;
        const auto xOffset           = ALIGN == "left" ? std::round(scaledBarPadding + (BUTTONSRIGHT ? 0 : scaledButtonsSize)) :
                                                         std::round(((BARBUF.x - scaledBorderSize) / 2.0 - m_pTextTex->m_size.x / 2.0));
        const auto yOffset           = std::round((BARBUF.y - m_pTextTex->m_size.y) / 2.0);
        CBox       titleBox          = {textBox.x + xOffset, textBox.y + yOffset, m_pTextTex->m_size.x, m_pTextTex->m_size.y};

        g_pHyprOpenGL->renderTexture(m_pTextTex, titleBox, {.a = a});
    }

    renderBarButtons(&textBox, pMonitor->m_scale, a);
    m_bButtonsDirty = false;

    g_pHyprOpenGL->scissor(nullptr);

    renderBarButtonsText(&textBox, pMonitor->m_scale, a);

    m_bWindowSizeChanged = false;
    m_bTitleColorChanged = false;

    // dynamic updates change the extents
    if (!exportPass && m_iLastHeight != HEIGHT) {
        PWINDOW->layoutTarget()->recalc();
        m_iLastHeight = HEIGHT;
    }
}

eDecorationType CHyprBar::getDecorationType() {
    return DECORATION_CUSTOM;
}

void CHyprBar::updateWindow(PHLWINDOW pWindow) {
    damageEntire();
}

bool CHyprBar::retireCaptionIntent() {
    // Preserve swallowed-release authority until the genuine release arrives.
    const bool hadIntent = m_bDragPending || m_bDraggingThis;
    m_bDragPending = false;
    m_bDraggingThis = false;
    m_bTouchEv = false;
    m_touchId = 0;
    m_captionPress = {};
    return hadIntent;
}

void CHyprBar::onConfigReloaded() {
    // A later movement must not revive a caption press from before reload.
    retireCaptionIntent();
    m_bButtonsDirty      = true;
    m_bTitleColorChanged = true;
    m_pTextTex           = nullptr;
    m_titleRasterKey.reset();
    m_iconRasters.clear();

    g_pDecorationPositioner->repositionDeco(this);
    damageEntire();
}

void CHyprBar::damageEntire() {
    g_pHyprRenderer->damageBox(assignedBoxGlobal());
}

Vector2D CHyprBar::cursorRelativeToBar() {
    return g_pInputManager->getMouseCoordsInternal() - assignedBoxGlobal().pos();
}

eDecorationLayer CHyprBar::getDecorationLayer() {
    return DECORATION_LAYER_UNDER;
}

uint64_t CHyprBar::getDecorationFlags() {
    return DECORATION_ALLOWS_MOUSE_INPUT | (g_pGlobalState->config.barPartOfWindow->value() ? DECORATION_PART_OF_MAIN_WINDOW : 0);
}

CBox CHyprBar::assignedBoxGlobal() {
    if (!validMapped(m_pWindow))
        return {};

    CBox box = m_bAssignedBox;
    box.translate(g_pDecorationPositioner->getEdgeDefinedPoint(DECORATION_EDGE_TOP, m_pWindow.lock()));

    const auto PWORKSPACE      = m_pWindow->m_workspace;
    const auto WORKSPACEOFFSET = PWORKSPACE && !m_pWindow->m_pinned ? PWORKSPACE->m_renderOffset->value() : Vector2D();

    return box.translate(WORKSPACEOFFSET);
}

PHLWINDOW CHyprBar::getOwner() {
    return m_pWindow.lock();
}

void CHyprBar::updateRules() {
    const auto PWINDOW              = m_pWindow.lock();
    auto       prevHidden           = m_hidden;
    auto       prevForcedTitleColor = m_bForcedTitleColor;

    m_bForcedBarColor   = std::nullopt;
    m_bForcedTitleColor = std::nullopt;
    m_hidden            = false;

    if (PWINDOW->m_ruleApplicator->m_otherProps.props.contains(g_pGlobalState->nobarRuleIdx))
        m_hidden = truthy(PWINDOW->m_ruleApplicator->m_otherProps.props.at(g_pGlobalState->nobarRuleIdx)->effect);
    if (PWINDOW->m_ruleApplicator->m_otherProps.props.contains(g_pGlobalState->barColorRuleIdx))
        m_bForcedBarColor = CHyprColor(Config::ParserUtils::parseColor(PWINDOW->m_ruleApplicator->m_otherProps.props.at(g_pGlobalState->barColorRuleIdx)->effect).value_or(0));
    if (PWINDOW->m_ruleApplicator->m_otherProps.props.contains(g_pGlobalState->titleColorRuleIdx))
        m_bForcedTitleColor = CHyprColor(Config::ParserUtils::parseColor(PWINDOW->m_ruleApplicator->m_otherProps.props.at(g_pGlobalState->titleColorRuleIdx)->effect).value_or(0));

    if (prevHidden != m_hidden)
        g_pDecorationPositioner->repositionDeco(this);
    if (prevForcedTitleColor != m_bForcedTitleColor)
        m_bTitleColorChanged = true;
}

void CHyprBar::damageOnButtonHover() {
    const auto BARPADDING       = g_pGlobalState->config.barPadding->value();
    const auto BARBUTTONPADDING = g_pGlobalState->config.barButtonPadding->value();
    const auto HEIGHT           = g_pGlobalState->config.barHeight->value();
    const auto ALIGNBUTTONS     = g_pGlobalState->config.barButtonsAlignment->value();
    const bool BUTTONSRIGHT     = ALIGNBUTTONS != "left";

    float      offset = BARPADDING;

    const auto COORDS = cursorRelativeToBar();

    for (auto& b : g_pGlobalState->buttons) {
        const auto BARBUF     = Vector2D{(int)assignedBoxGlobal().w, HEIGHT};
        Vector2D   currentPos = Vector2D{(BUTTONSRIGHT ? BARBUF.x - BARBUTTONPADDING - b.size - offset : offset), (BARBUF.y - b.size) / 2.0}.floor();

        bool       hover = VECINRECT(COORDS, currentPos.x, currentPos.y, currentPos.x + b.size + BARBUTTONPADDING, currentPos.y + b.size);

        if (hover != m_bButtonHovered) {
            m_bButtonHovered = hover;
            damageEntire();
        }

        offset += BARBUTTONPADDING + b.size;
    }
}

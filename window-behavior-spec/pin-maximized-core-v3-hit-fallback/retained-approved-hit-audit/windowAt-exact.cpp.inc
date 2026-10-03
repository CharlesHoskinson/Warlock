PHLWINDOW CViewHitTester::windowAt(const Vector2D& pos, uint16_t properties, PHLWINDOW ignoreWindow) const {
    const auto PMONITOR = State::monitorState()->query().vec(pos).run();
    if (!PMONITOR)
        return nullptr;

    static auto PRESIZEONBORDER       = CConfigValue<Config::INTEGER>("general:resize_on_border");
    static auto PBORDERSIZE           = CConfigValue<Config::INTEGER>("general:border_size");
    static auto PBORDERGRABEXTEND     = CConfigValue<Config::INTEGER>("general:extend_border_grab_area");
    static auto PSPECIALFALLTHRU      = CConfigValue<Config::INTEGER>("input:special_fallthrough");
    static auto PMODALPARENTBLOCKING  = CConfigValue<Config::INTEGER>("general:modal_parent_blocking");
    static auto PFOLLOWMOUSESHRINK    = CConfigValue<Config::INTEGER>("input:follow_mouse_shrink");
    const auto  BORDER_GRAB_AREA      = *PRESIZEONBORDER ? *PBORDERSIZE + *PBORDERGRABEXTEND : 0;
    const bool  ONLY_PRIORITY         = properties & FOCUS_PRIORITY;
    const bool  DO_FOLLOW_MOUSE_CHECK = properties & FOLLOW_MOUSE_CHECK;
    const auto  HITBOX_SHRINK         = DO_FOLLOW_MOUSE_CHECK ? *PFOLLOWMOUSESHRINK : 0;
    const auto  LASTFOCUSED           = focusState()->window();
    const auto& WINDOWS               = m_tracker.windows();

    const auto  isShadowedByModal = [](PHLWINDOW w) -> bool {
        return *PMODALPARENTBLOCKING && w->m_xdgSurface && w->m_xdgSurface->m_toplevel && w->m_xdgSurface->m_toplevel->anyChildModal();
    };

    // pinned windows on top of floating regardless
    {
        const auto PROTECTED_BAND = Desktop::Pin::band();
        for (auto const& w : PROTECTED_BAND | std::views::reverse) {
            if ((w->m_isFloating && !(properties & ALLOW_FLOATING)) || (!w->m_isFloating && (properties & FLOATING_ONLY)))
                continue;
            if (ONLY_PRIORITY && !w->priorityFocus())
                continue;

            if (w->m_isMapped && w->acceptsInput() && !w->m_X11ShouldntFocus && Desktop::Pin::effective(w) && !w->m_ruleApplicator->noFocus().valueOrDefault() &&
                w != ignoreWindow && !isShadowedByModal(w)) {
                const auto BB  = w->getWindowBoxUnified(properties);
                CBox       box = BB.copy().expand(!w->isX11OverrideRedirect() ? BORDER_GRAB_AREA : 0);
                if (HITBOX_SHRINK > 0 && w != LASTFOCUSED)
                    box = box.copy().expand(-HITBOX_SHRINK);
                if (box.containsPoint(pos))
                    return w;

                if (!w->m_isX11) {
                    if (w->hasPopupAt(pos))
                        return w;
                }
            }
        }
    }

    auto windowForWorkspace = [&](bool special) -> PHLWINDOW {
        auto floating = [&](bool aboveFullscreen) -> PHLWINDOW {
            for (auto const& w : WINDOWS | std::views::reverse) {
                if (special && !w->onSpecialWorkspace()) // because special floating may creep up into regular
                    continue;

                if (!w->m_workspace)
                    continue;

                if (ONLY_PRIORITY && !w->priorityFocus())
                    continue;

                const auto PWINDOWMONITOR = w->m_monitor.lock();

                // to avoid focusing windows behind special workspaces from other monitors
                if (!*PSPECIALFALLTHRU && PWINDOWMONITOR && PWINDOWMONITOR->m_activeSpecialWorkspace && w->m_workspace != PWINDOWMONITOR->m_activeSpecialWorkspace) {
                    const auto BB = w->getWindowBoxUnified(properties);
                    if (BB.x >= PWINDOWMONITOR->m_position.x && BB.y >= PWINDOWMONITOR->m_position.y &&
                        BB.x + BB.width <= PWINDOWMONITOR->m_position.x + PWINDOWMONITOR->m_size.x && BB.y + BB.height <= PWINDOWMONITOR->m_position.y + PWINDOWMONITOR->m_size.y)
                        continue;
                }

                if (w->m_isFloating && w->m_isMapped && w->m_workspace->isVisible() && w->acceptsInput() && !Desktop::Pin::effective(w) &&
                    !w->m_ruleApplicator->noFocus().valueOrDefault() && w != ignoreWindow && (!aboveFullscreen || w->isAllowedOverFullscreen()) && !isShadowedByModal(w)) {
                    // OR windows should add focus to parent
                    if (w->m_X11ShouldntFocus && !w->isX11OverrideRedirect())
                        continue;

                    const auto BB  = w->getWindowBoxUnified(properties);
                    CBox       box = BB.copy().expand(!w->isX11OverrideRedirect() ? BORDER_GRAB_AREA : 0);
                    if (HITBOX_SHRINK > 0 && w != LASTFOCUSED)
                        box = box.copy().expand(-HITBOX_SHRINK);
                    if (box.containsPoint(pos)) {
                        if (w->m_isX11 && w->isX11OverrideRedirect() && !w->m_xwaylandSurface->wantsFocus()) {
                            // Override Redirect
                            return focusState()->window(); // we kinda trick everything here.
                            // TODO: this is wrong, we should focus the parent, but idk how to get it considering it's nullptr in most cases.
                        }

                        return w;
                    }

                    if (!w->m_isX11) {
                        if (w->hasPopupAt(pos))
                            return w;
                    }
                }
            }

            return nullptr;
        };

        if (properties & ALLOW_FLOATING) {
            // first loop over floating cuz they're above, m_lWindows should be sorted bottom->top, for tiled it doesn't matter.
            auto found = floating(true);
            if (found)
                return found;
        }

        if (properties & FLOATING_ONLY)
            return floating(false);

        const WORKSPACEID WSPID      = special ? PMONITOR->activeSpecialWorkspaceID() : PMONITOR->activeWorkspaceID();
        const auto        PWORKSPACE = State::workspaceState()->query().id(WSPID).run();

        if (Fullscreen::controller()->hasFullscreen(PWORKSPACE) && !(properties & SKIP_FULLSCREEN_PRIORITY) && !ONLY_PRIORITY) {
            const auto FS_WINDOW = Fullscreen::controller()->getFullscreenWindow(PWORKSPACE);

            if (!FS_WINDOW || Desktop::Pin::effective(FS_WINDOW))
                return nullptr;

            // for maximized windows, don't return a window if we are not directly on it.
            if (!Fullscreen::controller()->isFullscreen(FS_WINDOW, Fullscreen::FSMODE_MAXIMIZED) || FS_WINDOW->getWindowBoxUnified(properties).containsPoint(pos))
                return Fullscreen::controller()->getFullscreenWindow(PWORKSPACE);
            else
                return nullptr;
        }

        auto found = floating(false);
        if (found)
            return found;

        // for windows, we need to check their extensions too, first.
        for (auto const& w : WINDOWS) {
            if (ONLY_PRIORITY && !w->priorityFocus())
                continue;

            if (special != w->onSpecialWorkspace())
                continue;

            if (!w->m_workspace)
                continue;

            if (!w->m_isX11 && !Desktop::Pin::effective(w) && !w->m_isFloating && w->m_isMapped && w->workspaceID() == WSPID && w->acceptsInput() && !w->m_X11ShouldntFocus &&
                !w->m_ruleApplicator->noFocus().valueOrDefault() && w != ignoreWindow && !isShadowedByModal(w)) {
                if (w->hasPopupAt(pos))
                    return w;
            }
        }

        for (auto const& w : WINDOWS) {
            if (ONLY_PRIORITY && !w->priorityFocus())
                continue;

            if (special != w->onSpecialWorkspace())
                continue;

            if (!w->m_workspace)
                continue;

            if (!Desktop::Pin::effective(w) && !w->m_isFloating && w->m_isMapped && w->workspaceID() == WSPID && w->acceptsInput() && !w->m_X11ShouldntFocus &&
                !w->m_ruleApplicator->noFocus().valueOrDefault() && w != ignoreWindow && !isShadowedByModal(w)) {
                CBox box = (properties & USE_PROP_TILED) ? w->getWindowBoxUnified(properties) : w->layoutBox();
                if ((properties & INPUT_EXTENTS) && BORDER_GRAB_AREA > 0 && !w->isX11OverrideRedirect()) {
                    const auto WORKAREA                    = PWORKSPACE->m_space->workArea();
                    auto       isWindowCloseToWorkAreaEdge = [&](const Math::eDirection dir) -> bool {
                        constexpr double STICK_THRESHOLD = 2.0; // This constant is taken from isAdjacent in CWindowQuery::inDirection
                        double           aEdge           = -1;
                        double           bEdge           = -1;

                        switch (dir) {
                            case Math::DIRECTION_LEFT:
                                aEdge = WORKAREA.x;
                                bEdge = box.x;
                                break;
                            case Math::DIRECTION_RIGHT:
                                aEdge = WORKAREA.x + WORKAREA.width;
                                bEdge = box.x + box.width;
                                break;
                            case Math::DIRECTION_UP:
                                aEdge = WORKAREA.y;
                                bEdge = box.y;
                                break;
                            case Math::DIRECTION_DOWN:
                                aEdge = WORKAREA.y + WORKAREA.height;
                                bEdge = box.y + box.height;
                                break;
                            default: break;
                        }
                        const double delta = aEdge - bEdge;
                        return std::abs(delta) < STICK_THRESHOLD;
                    };

                    if (isWindowCloseToWorkAreaEdge(Math::eDirection::DIRECTION_LEFT)) {
                        box.x -= BORDER_GRAB_AREA;
                        box.width += BORDER_GRAB_AREA;
                    }

                    if (isWindowCloseToWorkAreaEdge(Math::eDirection::DIRECTION_RIGHT))
                        box.width += BORDER_GRAB_AREA;

                    if (isWindowCloseToWorkAreaEdge(Math::eDirection::DIRECTION_UP)) {
                        box.y -= BORDER_GRAB_AREA;
                        box.height += BORDER_GRAB_AREA;
                    }

                    if (isWindowCloseToWorkAreaEdge(Math::eDirection::DIRECTION_DOWN))
                        box.height += BORDER_GRAB_AREA;
                }
                if (HITBOX_SHRINK > 0 && w != LASTFOCUSED)
                    box = box.copy().expand(-HITBOX_SHRINK);
                if (box.containsPoint(pos))
                    return w;
            }
        }

        return nullptr;
    };

    // special workspace
    if (PMONITOR->m_activeSpecialWorkspace && !*PSPECIALFALLTHRU)
        return windowForWorkspace(true);

    if (PMONITOR->m_activeSpecialWorkspace) {
        const auto PWINDOW = windowForWorkspace(true);

        if (PWINDOW)
            return PWINDOW;
    }

    return windowForWorkspace(false);
}


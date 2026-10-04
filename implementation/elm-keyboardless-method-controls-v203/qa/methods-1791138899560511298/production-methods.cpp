void CSeatManager::setKeyboard(SP<IKeyboard> KEEB) {
    if (m_keyboard == KEEB)
        return;

    // A focus selected while no device existed must enter the first live
    // keyboard. Retain its identity across keymap callbacks, never an old one.
    const auto RESTORED_FOCUS = !m_keyboard && KEEB ? m_state.keyboardFocus.lock() : nullptr;
    if (m_keyboard)
        m_keyboard->m_active = false;
    m_keyboard = KEEB;

    if (KEEB)
        KEEB->m_active = true;

    updateActiveKeyboardData();
    if (RESTORED_FOCUS && m_state.keyboardFocus == RESTORED_FOCUS && m_keyboard == KEEB) {
        m_state.keyboardFocus.reset();
        setKeyboardFocus(RESTORED_FOCUS);
    }
}

void CSeatManager::updateActiveKeyboardData() {
    if (m_keyboard)
        PROTO::seat->updateRepeatInfo(m_keyboard->m_repeatRate, m_keyboard->m_repeatDelay);
    PROTO::seat->updateKeymap();
    PROTO::inputCapture->updateKeymap();
}

void CSeatManager::setKeyboardFocus(SP<CWLSurfaceResource> surf) {
    if (m_state.keyboardFocus == surf)
        return;

    if (!m_keyboard) {
        // Focus policy is independent of device availability. Keep only the
        // admitted live surface intent; no keyboard resource or event is forged.
        m_listeners.keyboardSurfaceDestroy.reset();
        m_state.keyboardFocusResource.reset();
        m_state.keyboardFocus = surf;
        if (surf)
            m_listeners.keyboardSurfaceDestroy = surf->m_events.destroy.listen([this] { setKeyboardFocus(nullptr); });
        m_events.keyboardFocusChange.emit();
        return;
    }

    m_listeners.keyboardSurfaceDestroy.reset();

    // Don't gate leave on m_state.keyboardFocusResource — the WP can
    // be stale. sendLeave no-ops on keyboards without m_currentSurface.
    for (auto const& k : PROTO::seat->m_keyboards) {
        if (!k)
            continue;

        k->sendMods(0, m_keyboard->m_modifiersState.latched, m_keyboard->m_modifiersState.locked, m_keyboard->m_modifiersState.group);
        k->sendLeave();
    }

    m_state.keyboardFocusResource.reset();
    m_state.keyboardFocus = surf;

    if (!surf) {
        m_events.keyboardFocusChange.emit();
        return;
    }

    wl_array keys;
    wl_array_init(&keys);
    CScopeGuard x([&keys] { wl_array_release(&keys); });

    const auto& PRESSED = g_pInputManager->getKeysFromAllKBs();
    static_assert(std::is_same_v<std::decay_t<decltype(PRESSED)>::value_type, uint32_t>, "Element type different from keycode type uint32_t");

    const auto PRESSEDARRSIZE = PRESSED.size() * sizeof(uint32_t);
    if (PRESSEDARRSIZE > 0) {
        const auto PKEYS = wl_array_add(&keys, PRESSEDARRSIZE);
        if (PKEYS)
            std::ranges::copy(PRESSED, sc<uint32_t*>(PKEYS));
    }

    auto client = surf->client();
    for (auto const& r : m_seatResources | std::views::reverse) {
        if (r->resource->client() != client)
            continue;

        m_state.keyboardFocusResource = r->resource;
        for (auto const& k : r->resource->m_keyboards) {
            if (!k)
                continue;

            k->sendEnter(surf, &keys);
            uint32_t depressed = m_keyboard->m_modifiersState.depressed;
            uint32_t latched   = m_keyboard->m_modifiersState.latched;
            uint32_t locked    = m_keyboard->m_modifiersState.locked;
            for (auto const& kb : g_pInputManager->m_keyboards) {
                if (!kb->m_enabled || !kb->shareStates() || (kb->isVirtual() && g_pInputManager->shouldIgnoreVirtualKeyboard(kb)))
                    continue;
                depressed |= kb->m_modifiersState.depressed;
                latched |= kb->m_modifiersState.latched;
                locked |= kb->m_modifiersState.locked;
            }
            k->sendMods(depressed, latched, locked, m_keyboard->m_modifiersState.group);
        }
    }

    m_listeners.keyboardSurfaceDestroy = surf->m_events.destroy.listen([this] { setKeyboardFocus(nullptr); });

    m_events.keyboardFocusChange.emit();
}
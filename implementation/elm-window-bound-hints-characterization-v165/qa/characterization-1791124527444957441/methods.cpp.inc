std::optional<Vector2D> CWindow::minSize() {
    // first check for overrides
    if (m_ruleApplicator->minSize().hasValue())
        return m_ruleApplicator->minSize().value();

    // then check if we have any proto overrides
    bool hasSizeHints = m_xwaylandSurface ? !!m_xwaylandSurface->m_sizeHints : false;
    bool hasTopLevel  = m_xdgSurface ? !!m_xdgSurface->m_toplevel : false;
    if ((m_isX11 && !hasSizeHints) || (!m_isX11 && !hasTopLevel))
        return std::nullopt;

    Vector2D minSize = m_isX11 ? Vector2D(m_xwaylandSurface->m_sizeHints->min_width, m_xwaylandSurface->m_sizeHints->min_height) : m_xdgSurface->m_toplevel->layoutMinSize();

    minSize = minSize.clamp({1, 1});

    return minSize;
}

std::optional<Vector2D> CWindow::maxSize() {
    // first check for overrides
    if (m_ruleApplicator->maxSize().hasValue())
        return m_ruleApplicator->maxSize().value();

    // then check if we have any proto overrides
    if (((m_isX11 && !m_xwaylandSurface->m_sizeHints) || (!m_isX11 && (!m_xdgSurface || !m_xdgSurface->m_toplevel)) || m_ruleApplicator->noMaxSize().valueOrDefault()))
        return std::nullopt;

    constexpr const double NO_MAX_SIZE_LIMIT = std::numeric_limits<double>::max();

    Vector2D maxSize = m_isX11 ? Vector2D(m_xwaylandSurface->m_sizeHints->max_width, m_xwaylandSurface->m_sizeHints->max_height) : m_xdgSurface->m_toplevel->layoutMaxSize();

    if (maxSize.x < 5)
        maxSize.x = NO_MAX_SIZE_LIMIT;
    if (maxSize.y < 5)
        maxSize.y = NO_MAX_SIZE_LIMIT;

    return maxSize;
}

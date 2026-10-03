        if (Fullscreen::controller()->hasFullscreen(PWORKSPACE) && Fullscreen::controller()->getFullscreenModes(PWORKSPACE).internal == Fullscreen::FSMODE_MAXIMIZED) {
            if (!foundSurface) {
                if (PMONITOR->m_activeSpecialWorkspace) {
                    const auto& PWINDOWIDEAL = getWindowIdeal();
                    if (pFoundWindow != PWINDOWIDEAL)
                        pFoundWindow = PWINDOWIDEAL;

                    if (pFoundWindow && !pFoundWindow->onSpecialWorkspace()) {
                        pFoundWindow = Fullscreen::controller()->getFullscreenWindow(PWORKSPACE);
                    }
                } else {
                    // if we have a maximized window, allow focusing on a bar or something if in reserved area.
                    if (State::monitorLayoutController()->isPointOnReservedArea(mouseCoords, PMONITOR)) {
                        foundSurface = Desktop::viewState()->hitTest().layerSurfaceAt(mouseCoords, &PMONITOR->m_layerSurfaceLayers[ZWLR_LAYER_SHELL_V1_LAYER_BOTTOM],
                                                                                      &surfaceCoords, &pFoundLayerSurface);
                    }

                    if (!foundSurface) {
                        const auto& PWINDOWIDEAL = getWindowIdeal();
                        if (pFoundWindow != PWINDOWIDEAL)
                            pFoundWindow = PWINDOWIDEAL;

                        if (!(pFoundWindow && (pFoundWindow->m_isFloating && pFoundWindow->isAllowedOverFullscreen())))
                            pFoundWindow = Fullscreen::controller()->getFullscreenWindow(PWORKSPACE);
                    }
                }
            }

        } else {
            const auto& PWINDOWIDEAL = getWindowIdeal();
            if (pFoundWindow != PWINDOWIDEAL)
                pFoundWindow = PWINDOWIDEAL;
        }

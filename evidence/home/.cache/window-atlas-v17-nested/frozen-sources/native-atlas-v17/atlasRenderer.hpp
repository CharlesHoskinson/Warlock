#pragma once
#include <hyprland/src/render/Renderer.hpp>
SP<Render::IFramebuffer> makeCanonicalAtlas(PHLWINDOW,PHLMONITOR,const Vector2D& offset,const Vector2D& size);

#pragma once
#include <hyprland/src/render/Renderer.hpp>
void initAtlasAdapter();
void exitAtlasAdapter();
void beginAtlasCoordinates(const Vector2D& pixelOffset,PHLMONITOR monitor);
void endAtlasCoordinates();
void validateAtlasCoordinates();
CBox atlasCaptionClip(const CBox& box);

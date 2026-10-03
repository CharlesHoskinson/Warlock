#include <hyprland/src/render/Renderer.hpp>
struct WindowRenderAccess : Render::IHyprRenderer {
 static constexpr auto method() { return &WindowRenderAccess::renderWindow; }
};
void render(Render::IHyprRenderer* renderer, PHLWINDOW window, PHLMONITOR monitor) {
 (renderer->*WindowRenderAccess::method())(window,monitor,Time::steadyNow(),true,Render::RENDER_PASS_ALL,false,false);
}

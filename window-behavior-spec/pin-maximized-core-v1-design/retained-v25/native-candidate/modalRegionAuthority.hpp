#pragma once
#include <cmath>
#include <utility>
namespace ModalRegionAuthority {
// Only this selector may choose the Wayland-only versus X11 root-resource API.
template<class WaylandLookup,class X11Lookup>
bool bodyInput(bool x11,double x11Scale,WaylandLookup&& wayland,X11Lookup&& xresource) {
 if (!x11) return bool(std::forward<WaylandLookup>(wayland)());
 if (!std::isfinite(x11Scale) || x11Scale<=0) return false;
 return bool(std::forward<X11Lookup>(xresource)(x11Scale));
}
}

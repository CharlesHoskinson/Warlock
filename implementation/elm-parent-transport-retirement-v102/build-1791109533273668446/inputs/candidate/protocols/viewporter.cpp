// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// viewporter

/*
 This protocol's authors' copyright notice is:


    Copyright © 2013-2016 Collabora, Ltd.

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice (including the next
    paragraph) shall be included in all copies or substantial portions of the
    Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
  
*/

#define private public
#define HYPRWAYLAND_SCANNER_NO_INTERFACES
#include "viewporter.hpp"
#undef private
#define F std::function

static const wl_interface* viewporter_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wp_viewporter_interface;
extern const wl_interface wp_viewport_interface;
extern const wl_interface wl_surface_interface;

static const void* _CCWpViewporterVTable[] = {
    nullptr,
};

void CCWpViewporter::sendDestroy() {
    if (!pResource)
        return;
    destroyed = true;

    auto proxy = wl_proxy_marshal_flags(pResource, 0, nullptr, wl_proxy_get_version(pResource), 1);
    proxy;
}

wl_proxy* CCWpViewporter::sendGetViewport(wl_proxy* surface) {
    if (!pResource)
        return nullptr;

    auto proxy = wl_proxy_marshal_flags(pResource, 1, &wp_viewport_interface, wl_proxy_get_version(pResource), 0, nullptr, surface);

    return proxy;
}
static const wl_interface* _CWpViewporterGetViewportTypes[] = {
    &wp_viewport_interface,
    &wl_surface_interface,
};

static const wl_message _CWpViewporterRequests[] = {
    { .name = "destroy", .signature = "", .types = viewporter_dummyTypes + 0},
    { .name = "get_viewport", .signature = "no", .types = _CWpViewporterGetViewportTypes + 0},
};

const wl_interface wp_viewporter_interface = {
    .name = "wp_viewporter", .version = 1,
    .method_count = 2, .methods = _CWpViewporterRequests,
    .event_count = 0, .events = nullptr,
};

CCWpViewporter::CCWpViewporter(wl_proxy* resource) : pResource(resource) {

    if (!pResource)
        return;

    wl_proxy_add_listener(pResource, (void (**)(void))&_CCWpViewporterVTable, this);
}

CCWpViewporter::~CCWpViewporter() {
    if (!destroyed)
        sendDestroy();
}

static const void* _CCWpViewportVTable[] = {
    nullptr,
};

void CCWpViewport::sendDestroy() {
    if (!pResource)
        return;
    destroyed = true;

    auto proxy = wl_proxy_marshal_flags(pResource, 0, nullptr, wl_proxy_get_version(pResource), 1);
    proxy;
}

void CCWpViewport::sendSetSource(wl_fixed_t x, wl_fixed_t y, wl_fixed_t width, wl_fixed_t height) {
    if (!pResource)
        return;

    auto proxy = wl_proxy_marshal_flags(pResource, 1, nullptr, wl_proxy_get_version(pResource), 0, x, y, width, height);
    proxy;
}

void CCWpViewport::sendSetDestination(int32_t width, int32_t height) {
    if (!pResource)
        return;

    auto proxy = wl_proxy_marshal_flags(pResource, 2, nullptr, wl_proxy_get_version(pResource), 0, width, height);
    proxy;
}
static const wl_interface* _CWpViewportSetSourceTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWpViewportSetDestinationTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CWpViewportRequests[] = {
    { .name = "destroy", .signature = "", .types = viewporter_dummyTypes + 0},
    { .name = "set_source", .signature = "ffff", .types = _CWpViewportSetSourceTypes + 0},
    { .name = "set_destination", .signature = "ii", .types = _CWpViewportSetDestinationTypes + 0},
};

const wl_interface wp_viewport_interface = {
    .name = "wp_viewport", .version = 1,
    .method_count = 3, .methods = _CWpViewportRequests,
    .event_count = 0, .events = nullptr,
};

CCWpViewport::CCWpViewport(wl_proxy* resource) : pResource(resource) {

    if (!pResource)
        return;

    wl_proxy_add_listener(pResource, (void (**)(void))&_CCWpViewportVTable, this);
}

CCWpViewport::~CCWpViewport() {
    if (!destroyed)
        sendDestroy();
}

#undef F

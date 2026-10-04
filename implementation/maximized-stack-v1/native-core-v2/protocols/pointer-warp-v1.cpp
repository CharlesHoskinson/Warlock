// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// pointer_warp_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2024 Neal Gompa
    Copyright © 2024 Xaver Hugl
    Copyright © 2024 Matthias Klumpp
    Copyright © 2024 Vlad Zahorodnii

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
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
  
*/

#define private public
#define HYPRWAYLAND_SCANNER_NO_INTERFACES
#include "pointer-warp-v1.hpp"
#undef private
#define F std::function

static const wl_interface* pointerWarpV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wp_pointer_warp_v1_interface;
extern const wl_interface wl_surface_interface;
extern const wl_interface wl_pointer_interface;

static void _CWpPointerWarpV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpPointerWarpV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpPointerWarpV1WarpPointer(wl_client* client, wl_resource* resource, wl_resource* surface, wl_resource* pointer, wl_fixed_t x, wl_fixed_t y, uint32_t serial) {
    const auto PO = (CWpPointerWarpV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.warpPointer)
        PO->requests.warpPointer(PO, surface, pointer, x, y, serial);
}

static void _CWpPointerWarpV1__DestroyListener(wl_listener* l, void* d) {
    CWpPointerWarpV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpPointerWarpV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpPointerWarpV1VTable[] = {
    (void*)_CWpPointerWarpV1Destroy,
    (void*)_CWpPointerWarpV1WarpPointer,
};
static const wl_interface* _CWpPointerWarpV1WarpPointerTypes[] = {
    &wl_surface_interface,
    &wl_pointer_interface,
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CWpPointerWarpV1Requests[] = {
    { .name = "destroy", .signature = "", .types = pointerWarpV1_dummyTypes + 0},
    { .name = "warp_pointer", .signature = "ooffu", .types = _CWpPointerWarpV1WarpPointerTypes + 0},
};

const wl_interface wp_pointer_warp_v1_interface = {
    .name = "wp_pointer_warp_v1", .version = 1,
    .method_count = 2, .methods = _CWpPointerWarpV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpPointerWarpV1::CWpPointerWarpV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_pointer_warp_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpPointerWarpV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpPointerWarpV1VTable, this, nullptr);
}

CWpPointerWarpV1::~CWpPointerWarpV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpPointerWarpV1::onDestroyCalled() {
    wl_resource_set_user_data(pResource, nullptr);
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // set the resource to nullptr,
    // as it will be freed. If the consumer does not destroy this resource
    // in onDestroy here, we'd be doing a UAF in the ~dtor
    pResource = nullptr;

    if (onDestroy)
        onDestroy(this);
}

void CWpPointerWarpV1::setDestroy(F<void(CWpPointerWarpV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpPointerWarpV1::setWarpPointer(F<void(CWpPointerWarpV1*, wl_resource*, wl_resource*, wl_fixed_t, wl_fixed_t, uint32_t)> &&handler) {
    requests.warpPointer = std::move(handler);
}

#undef F

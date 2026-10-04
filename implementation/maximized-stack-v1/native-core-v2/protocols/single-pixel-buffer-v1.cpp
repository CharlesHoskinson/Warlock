// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// single_pixel_buffer_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2022 Simon Ser

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
#include "single-pixel-buffer-v1.hpp"
#undef private
#define F std::function

static const wl_interface* singlePixelBufferV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wp_single_pixel_buffer_manager_v1_interface;
extern const wl_interface wl_buffer_interface;

static void _CWpSinglePixelBufferManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpSinglePixelBufferManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpSinglePixelBufferManagerV1CreateU32RgbaBuffer(wl_client* client, wl_resource* resource, uint32_t id, uint32_t r, uint32_t g, uint32_t b, uint32_t a) {
    const auto PO = (CWpSinglePixelBufferManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createU32RgbaBuffer)
        PO->requests.createU32RgbaBuffer(PO, id, r, g, b, a);
}

static void _CWpSinglePixelBufferManagerV1__DestroyListener(wl_listener* l, void* d) {
    CWpSinglePixelBufferManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpSinglePixelBufferManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpSinglePixelBufferManagerV1VTable[] = {
    (void*)_CWpSinglePixelBufferManagerV1Destroy,
    (void*)_CWpSinglePixelBufferManagerV1CreateU32RgbaBuffer,
};
static const wl_interface* _CWpSinglePixelBufferManagerV1CreateU32RgbaBufferTypes[] = {
    &wl_buffer_interface,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CWpSinglePixelBufferManagerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = singlePixelBufferV1_dummyTypes + 0},
    { .name = "create_u32_rgba_buffer", .signature = "nuuuu", .types = _CWpSinglePixelBufferManagerV1CreateU32RgbaBufferTypes + 0},
};

const wl_interface wp_single_pixel_buffer_manager_v1_interface = {
    .name = "wp_single_pixel_buffer_manager_v1", .version = 1,
    .method_count = 2, .methods = _CWpSinglePixelBufferManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpSinglePixelBufferManagerV1::CWpSinglePixelBufferManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_single_pixel_buffer_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpSinglePixelBufferManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpSinglePixelBufferManagerV1VTable, this, nullptr);
}

CWpSinglePixelBufferManagerV1::~CWpSinglePixelBufferManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpSinglePixelBufferManagerV1::onDestroyCalled() {
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

void CWpSinglePixelBufferManagerV1::setDestroy(F<void(CWpSinglePixelBufferManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpSinglePixelBufferManagerV1::setCreateU32RgbaBuffer(F<void(CWpSinglePixelBufferManagerV1*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t)> &&handler) {
    requests.createU32RgbaBuffer = std::move(handler);
}

#undef F

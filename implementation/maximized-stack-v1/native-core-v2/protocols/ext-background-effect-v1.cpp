// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// ext_background_effect_v1

/*
 This protocol's authors' copyright notice is:


    Copyright (C) 2015 Martin Gräßlin
    Copyright (C) 2015 Marco Martin
    Copyright (C) 2020 Vlad Zahorodnii
    Copyright (C) 2024 Xaver Hugl

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
#include "ext-background-effect-v1.hpp"
#undef private
#define F std::function

static const wl_interface* extBackgroundEffectV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface ext_background_effect_manager_v1_interface;
extern const wl_interface ext_background_effect_surface_v1_interface;
extern const wl_interface wl_surface_interface;
extern const wl_interface wl_region_interface;

static void _CExtBackgroundEffectManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtBackgroundEffectManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtBackgroundEffectManagerV1GetBackgroundEffect(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CExtBackgroundEffectManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getBackgroundEffect)
        PO->requests.getBackgroundEffect(PO, id, surface);
}

static void _CExtBackgroundEffectManagerV1__DestroyListener(wl_listener* l, void* d) {
    CExtBackgroundEffectManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtBackgroundEffectManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtBackgroundEffectManagerV1VTable[] = {
    (void*)_CExtBackgroundEffectManagerV1Destroy,
    (void*)_CExtBackgroundEffectManagerV1GetBackgroundEffect,
};

void CExtBackgroundEffectManagerV1::sendCapabilities(extBackgroundEffectManagerV1Capability flags) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, flags);
}

void CExtBackgroundEffectManagerV1::sendCapabilitiesRaw(extBackgroundEffectManagerV1Capability flags) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, flags);
}
static const wl_interface* _CExtBackgroundEffectManagerV1GetBackgroundEffectTypes[] = {
    &ext_background_effect_surface_v1_interface,
    &wl_surface_interface,
};
static const wl_interface* _CExtBackgroundEffectManagerV1CapabilitiesTypes[] = {
    nullptr,
};

static const wl_message _CExtBackgroundEffectManagerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = extBackgroundEffectV1_dummyTypes + 0},
    { .name = "get_background_effect", .signature = "no", .types = _CExtBackgroundEffectManagerV1GetBackgroundEffectTypes + 0},
};

static const wl_message _CExtBackgroundEffectManagerV1Events[] = {
    { .name = "capabilities", .signature = "u", .types = _CExtBackgroundEffectManagerV1CapabilitiesTypes + 0},
};

const wl_interface ext_background_effect_manager_v1_interface = {
    .name = "ext_background_effect_manager_v1", .version = 1,
    .method_count = 2, .methods = _CExtBackgroundEffectManagerV1Requests,
    .event_count = 1, .events = _CExtBackgroundEffectManagerV1Events,
};

CExtBackgroundEffectManagerV1::CExtBackgroundEffectManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_background_effect_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtBackgroundEffectManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtBackgroundEffectManagerV1VTable, this, nullptr);
}

CExtBackgroundEffectManagerV1::~CExtBackgroundEffectManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtBackgroundEffectManagerV1::onDestroyCalled() {
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

void CExtBackgroundEffectManagerV1::setDestroy(F<void(CExtBackgroundEffectManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CExtBackgroundEffectManagerV1::setGetBackgroundEffect(F<void(CExtBackgroundEffectManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getBackgroundEffect = std::move(handler);
}

static void _CExtBackgroundEffectSurfaceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtBackgroundEffectSurfaceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtBackgroundEffectSurfaceV1SetBlurRegion(wl_client* client, wl_resource* resource, wl_resource* region) {
    const auto PO = (CExtBackgroundEffectSurfaceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setBlurRegion)
        PO->requests.setBlurRegion(PO, region);
}

static void _CExtBackgroundEffectSurfaceV1__DestroyListener(wl_listener* l, void* d) {
    CExtBackgroundEffectSurfaceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtBackgroundEffectSurfaceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtBackgroundEffectSurfaceV1VTable[] = {
    (void*)_CExtBackgroundEffectSurfaceV1Destroy,
    (void*)_CExtBackgroundEffectSurfaceV1SetBlurRegion,
};
static const wl_interface* _CExtBackgroundEffectSurfaceV1SetBlurRegionTypes[] = {
    &wl_region_interface,
};

static const wl_message _CExtBackgroundEffectSurfaceV1Requests[] = {
    { .name = "destroy", .signature = "", .types = extBackgroundEffectV1_dummyTypes + 0},
    { .name = "set_blur_region", .signature = "?o", .types = _CExtBackgroundEffectSurfaceV1SetBlurRegionTypes + 0},
};

const wl_interface ext_background_effect_surface_v1_interface = {
    .name = "ext_background_effect_surface_v1", .version = 1,
    .method_count = 2, .methods = _CExtBackgroundEffectSurfaceV1Requests,
    .event_count = 0, .events = nullptr,
};

CExtBackgroundEffectSurfaceV1::CExtBackgroundEffectSurfaceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_background_effect_surface_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtBackgroundEffectSurfaceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtBackgroundEffectSurfaceV1VTable, this, nullptr);
}

CExtBackgroundEffectSurfaceV1::~CExtBackgroundEffectSurfaceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtBackgroundEffectSurfaceV1::onDestroyCalled() {
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

void CExtBackgroundEffectSurfaceV1::setDestroy(F<void(CExtBackgroundEffectSurfaceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CExtBackgroundEffectSurfaceV1::setSetBlurRegion(F<void(CExtBackgroundEffectSurfaceV1*, wl_resource*)> &&handler) {
    requests.setBlurRegion = std::move(handler);
}

#undef F

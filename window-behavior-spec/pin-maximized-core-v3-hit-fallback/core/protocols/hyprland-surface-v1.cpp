// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// hyprland_surface_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2025 outfoxxed
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    3. Neither the name of the copyright holder nor the names of its
       contributors may be used to endorse or promote products derived from
       this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  
*/

#define private public
#define HYPRWAYLAND_SCANNER_NO_INTERFACES
#include "hyprland-surface-v1.hpp"
#undef private
#define F std::function

static const wl_interface* hyprlandSurfaceV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface hyprland_surface_manager_v1_interface;
extern const wl_interface hyprland_surface_v1_interface;
extern const wl_interface wl_surface_interface;
extern const wl_interface wl_region_interface;

static void _CHyprlandSurfaceManagerV1GetHyprlandSurface(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CHyprlandSurfaceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getHyprlandSurface)
        PO->requests.getHyprlandSurface(PO, id, surface);
}

static void _CHyprlandSurfaceManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandSurfaceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandSurfaceManagerV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandSurfaceManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandSurfaceManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandSurfaceManagerV1VTable[] = {
    (void*)_CHyprlandSurfaceManagerV1GetHyprlandSurface,
    (void*)_CHyprlandSurfaceManagerV1Destroy,
};
static const wl_interface* _CHyprlandSurfaceManagerV1GetHyprlandSurfaceTypes[] = {
    &hyprland_surface_v1_interface,
    &wl_surface_interface,
};

static const wl_message _CHyprlandSurfaceManagerV1Requests[] = {
    { .name = "get_hyprland_surface", .signature = "no", .types = _CHyprlandSurfaceManagerV1GetHyprlandSurfaceTypes + 0},
    { .name = "destroy", .signature = "", .types = hyprlandSurfaceV1_dummyTypes + 0},
};

const wl_interface hyprland_surface_manager_v1_interface = {
    .name = "hyprland_surface_manager_v1", .version = 2,
    .method_count = 2, .methods = _CHyprlandSurfaceManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CHyprlandSurfaceManagerV1::CHyprlandSurfaceManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_surface_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandSurfaceManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandSurfaceManagerV1VTable, this, nullptr);
}

CHyprlandSurfaceManagerV1::~CHyprlandSurfaceManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandSurfaceManagerV1::onDestroyCalled() {
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

void CHyprlandSurfaceManagerV1::setGetHyprlandSurface(F<void(CHyprlandSurfaceManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getHyprlandSurface = std::move(handler);
}

void CHyprlandSurfaceManagerV1::setDestroy(F<void(CHyprlandSurfaceManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CHyprlandSurfaceV1SetOpacity(wl_client* client, wl_resource* resource, wl_fixed_t opacity) {
    const auto PO = (CHyprlandSurfaceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setOpacity)
        PO->requests.setOpacity(PO, opacity);
}

static void _CHyprlandSurfaceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandSurfaceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandSurfaceV1SetVisibleRegion(wl_client* client, wl_resource* resource, wl_resource* region) {
    const auto PO = (CHyprlandSurfaceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setVisibleRegion)
        PO->requests.setVisibleRegion(PO, region);
}

static void _CHyprlandSurfaceV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandSurfaceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandSurfaceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandSurfaceV1VTable[] = {
    (void*)_CHyprlandSurfaceV1SetOpacity,
    (void*)_CHyprlandSurfaceV1Destroy,
    (void*)_CHyprlandSurfaceV1SetVisibleRegion,
};
static const wl_interface* _CHyprlandSurfaceV1SetOpacityTypes[] = {
    nullptr,
};
static const wl_interface* _CHyprlandSurfaceV1SetVisibleRegionTypes[] = {
    &wl_region_interface,
};

static const wl_message _CHyprlandSurfaceV1Requests[] = {
    { .name = "set_opacity", .signature = "f", .types = _CHyprlandSurfaceV1SetOpacityTypes + 0},
    { .name = "destroy", .signature = "", .types = hyprlandSurfaceV1_dummyTypes + 0},
    { .name = "set_visible_region", .signature = "2?o", .types = _CHyprlandSurfaceV1SetVisibleRegionTypes + 0},
};

const wl_interface hyprland_surface_v1_interface = {
    .name = "hyprland_surface_v1", .version = 2,
    .method_count = 3, .methods = _CHyprlandSurfaceV1Requests,
    .event_count = 0, .events = nullptr,
};

CHyprlandSurfaceV1::CHyprlandSurfaceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_surface_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandSurfaceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandSurfaceV1VTable, this, nullptr);
}

CHyprlandSurfaceV1::~CHyprlandSurfaceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandSurfaceV1::onDestroyCalled() {
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

void CHyprlandSurfaceV1::setSetOpacity(F<void(CHyprlandSurfaceV1*, wl_fixed_t)> &&handler) {
    requests.setOpacity = std::move(handler);
}

void CHyprlandSurfaceV1::setDestroy(F<void(CHyprlandSurfaceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CHyprlandSurfaceV1::setSetVisibleRegion(F<void(CHyprlandSurfaceV1*, wl_resource*)> &&handler) {
    requests.setVisibleRegion = std::move(handler);
}

#undef F

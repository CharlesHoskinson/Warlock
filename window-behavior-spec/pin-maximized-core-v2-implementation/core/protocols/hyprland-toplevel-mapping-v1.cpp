// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// hyprland_toplevel_mapping_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2025 WhySoBad
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
#include "hyprland-toplevel-mapping-v1.hpp"
#undef private
#define F std::function

static const wl_interface* hyprlandToplevelMappingV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface hyprland_toplevel_mapping_manager_v1_interface;
extern const wl_interface hyprland_toplevel_window_mapping_handle_v1_interface;
extern const wl_interface ext_foreign_toplevel_handle_v1_interface;
extern const wl_interface zwlr_foreign_toplevel_handle_v1_interface;

static void _CHyprlandToplevelMappingManagerV1GetWindowForToplevel(wl_client* client, wl_resource* resource, uint32_t handle, wl_resource* toplevel) {
    const auto PO = (CHyprlandToplevelMappingManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getWindowForToplevel)
        PO->requests.getWindowForToplevel(PO, handle, toplevel);
}

static void _CHyprlandToplevelMappingManagerV1GetWindowForToplevelWlr(wl_client* client, wl_resource* resource, uint32_t handle, wl_resource* toplevel) {
    const auto PO = (CHyprlandToplevelMappingManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getWindowForToplevelWlr)
        PO->requests.getWindowForToplevelWlr(PO, handle, toplevel);
}

static void _CHyprlandToplevelMappingManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandToplevelMappingManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandToplevelMappingManagerV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandToplevelMappingManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandToplevelMappingManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandToplevelMappingManagerV1VTable[] = {
    (void*)_CHyprlandToplevelMappingManagerV1GetWindowForToplevel,
    (void*)_CHyprlandToplevelMappingManagerV1GetWindowForToplevelWlr,
    (void*)_CHyprlandToplevelMappingManagerV1Destroy,
};
static const wl_interface* _CHyprlandToplevelMappingManagerV1GetWindowForToplevelTypes[] = {
    &hyprland_toplevel_window_mapping_handle_v1_interface,
    &ext_foreign_toplevel_handle_v1_interface,
};
static const wl_interface* _CHyprlandToplevelMappingManagerV1GetWindowForToplevelWlrTypes[] = {
    &hyprland_toplevel_window_mapping_handle_v1_interface,
    &zwlr_foreign_toplevel_handle_v1_interface,
};

static const wl_message _CHyprlandToplevelMappingManagerV1Requests[] = {
    { .name = "get_window_for_toplevel", .signature = "no", .types = _CHyprlandToplevelMappingManagerV1GetWindowForToplevelTypes + 0},
    { .name = "get_window_for_toplevel_wlr", .signature = "no", .types = _CHyprlandToplevelMappingManagerV1GetWindowForToplevelWlrTypes + 0},
    { .name = "destroy", .signature = "", .types = hyprlandToplevelMappingV1_dummyTypes + 0},
};

const wl_interface hyprland_toplevel_mapping_manager_v1_interface = {
    .name = "hyprland_toplevel_mapping_manager_v1", .version = 1,
    .method_count = 3, .methods = _CHyprlandToplevelMappingManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CHyprlandToplevelMappingManagerV1::CHyprlandToplevelMappingManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_toplevel_mapping_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandToplevelMappingManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandToplevelMappingManagerV1VTable, this, nullptr);
}

CHyprlandToplevelMappingManagerV1::~CHyprlandToplevelMappingManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandToplevelMappingManagerV1::onDestroyCalled() {
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

void CHyprlandToplevelMappingManagerV1::setGetWindowForToplevel(F<void(CHyprlandToplevelMappingManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getWindowForToplevel = std::move(handler);
}

void CHyprlandToplevelMappingManagerV1::setGetWindowForToplevelWlr(F<void(CHyprlandToplevelMappingManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getWindowForToplevelWlr = std::move(handler);
}

void CHyprlandToplevelMappingManagerV1::setDestroy(F<void(CHyprlandToplevelMappingManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CHyprlandToplevelWindowMappingHandleV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandToplevelWindowMappingHandleV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandToplevelWindowMappingHandleV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandToplevelWindowMappingHandleV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandToplevelWindowMappingHandleV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandToplevelWindowMappingHandleV1VTable[] = {
    (void*)_CHyprlandToplevelWindowMappingHandleV1Destroy,
};

void CHyprlandToplevelWindowMappingHandleV1::sendWindowAddress(uint32_t address_hi, uint32_t address) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, address_hi, address);
}

void CHyprlandToplevelWindowMappingHandleV1::sendFailed() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CHyprlandToplevelWindowMappingHandleV1::sendWindowAddressRaw(uint32_t address_hi, uint32_t address) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, address_hi, address);
}

void CHyprlandToplevelWindowMappingHandleV1::sendFailedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}
static const wl_interface* _CHyprlandToplevelWindowMappingHandleV1WindowAddressTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CHyprlandToplevelWindowMappingHandleV1Requests[] = {
    { .name = "destroy", .signature = "", .types = hyprlandToplevelMappingV1_dummyTypes + 0},
};

static const wl_message _CHyprlandToplevelWindowMappingHandleV1Events[] = {
    { .name = "window_address", .signature = "uu", .types = _CHyprlandToplevelWindowMappingHandleV1WindowAddressTypes + 0},
    { .name = "failed", .signature = "", .types = hyprlandToplevelMappingV1_dummyTypes + 0},
};

const wl_interface hyprland_toplevel_window_mapping_handle_v1_interface = {
    .name = "hyprland_toplevel_window_mapping_handle_v1", .version = 1,
    .method_count = 1, .methods = _CHyprlandToplevelWindowMappingHandleV1Requests,
    .event_count = 2, .events = _CHyprlandToplevelWindowMappingHandleV1Events,
};

CHyprlandToplevelWindowMappingHandleV1::CHyprlandToplevelWindowMappingHandleV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_toplevel_window_mapping_handle_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandToplevelWindowMappingHandleV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandToplevelWindowMappingHandleV1VTable, this, nullptr);
}

CHyprlandToplevelWindowMappingHandleV1::~CHyprlandToplevelWindowMappingHandleV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandToplevelWindowMappingHandleV1::onDestroyCalled() {
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

void CHyprlandToplevelWindowMappingHandleV1::setDestroy(F<void(CHyprlandToplevelWindowMappingHandleV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

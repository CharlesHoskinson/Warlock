// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// hyprland_global_shortcuts_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2022 Vaxry
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
#include "hyprland-global-shortcuts-v1.hpp"
#undef private
#define F std::function

static const wl_interface* hyprlandGlobalShortcutsV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface hyprland_global_shortcuts_manager_v1_interface;
extern const wl_interface hyprland_global_shortcut_v1_interface;

static void _CHyprlandGlobalShortcutsManagerV1RegisterShortcut(wl_client* client, wl_resource* resource, uint32_t shortcut, const char* id, const char* app_id, const char* description, const char* trigger_description) {
    const auto PO = (CHyprlandGlobalShortcutsManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.registerShortcut)
        PO->requests.registerShortcut(PO, shortcut, id, app_id, description, trigger_description);
}

static void _CHyprlandGlobalShortcutsManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandGlobalShortcutsManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandGlobalShortcutsManagerV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandGlobalShortcutsManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandGlobalShortcutsManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandGlobalShortcutsManagerV1VTable[] = {
    (void*)_CHyprlandGlobalShortcutsManagerV1RegisterShortcut,
    (void*)_CHyprlandGlobalShortcutsManagerV1Destroy,
};
static const wl_interface* _CHyprlandGlobalShortcutsManagerV1RegisterShortcutTypes[] = {
    &hyprland_global_shortcut_v1_interface,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CHyprlandGlobalShortcutsManagerV1Requests[] = {
    { .name = "register_shortcut", .signature = "nssss", .types = _CHyprlandGlobalShortcutsManagerV1RegisterShortcutTypes + 0},
    { .name = "destroy", .signature = "", .types = hyprlandGlobalShortcutsV1_dummyTypes + 0},
};

const wl_interface hyprland_global_shortcuts_manager_v1_interface = {
    .name = "hyprland_global_shortcuts_manager_v1", .version = 1,
    .method_count = 2, .methods = _CHyprlandGlobalShortcutsManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CHyprlandGlobalShortcutsManagerV1::CHyprlandGlobalShortcutsManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_global_shortcuts_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandGlobalShortcutsManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandGlobalShortcutsManagerV1VTable, this, nullptr);
}

CHyprlandGlobalShortcutsManagerV1::~CHyprlandGlobalShortcutsManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandGlobalShortcutsManagerV1::onDestroyCalled() {
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

void CHyprlandGlobalShortcutsManagerV1::setRegisterShortcut(F<void(CHyprlandGlobalShortcutsManagerV1*, uint32_t, const char*, const char*, const char*, const char*)> &&handler) {
    requests.registerShortcut = std::move(handler);
}

void CHyprlandGlobalShortcutsManagerV1::setDestroy(F<void(CHyprlandGlobalShortcutsManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CHyprlandGlobalShortcutV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandGlobalShortcutV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandGlobalShortcutV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandGlobalShortcutV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandGlobalShortcutV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandGlobalShortcutV1VTable[] = {
    (void*)_CHyprlandGlobalShortcutV1Destroy,
};

void CHyprlandGlobalShortcutV1::sendPressed(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, tv_sec_hi, tv_sec_lo, tv_nsec);
}

void CHyprlandGlobalShortcutV1::sendReleased(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, tv_sec_hi, tv_sec_lo, tv_nsec);
}

void CHyprlandGlobalShortcutV1::sendPressedRaw(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, tv_sec_hi, tv_sec_lo, tv_nsec);
}

void CHyprlandGlobalShortcutV1::sendReleasedRaw(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, tv_sec_hi, tv_sec_lo, tv_nsec);
}
static const wl_interface* _CHyprlandGlobalShortcutV1PressedTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CHyprlandGlobalShortcutV1ReleasedTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CHyprlandGlobalShortcutV1Requests[] = {
    { .name = "destroy", .signature = "", .types = hyprlandGlobalShortcutsV1_dummyTypes + 0},
};

static const wl_message _CHyprlandGlobalShortcutV1Events[] = {
    { .name = "pressed", .signature = "uuu", .types = _CHyprlandGlobalShortcutV1PressedTypes + 0},
    { .name = "released", .signature = "uuu", .types = _CHyprlandGlobalShortcutV1ReleasedTypes + 0},
};

const wl_interface hyprland_global_shortcut_v1_interface = {
    .name = "hyprland_global_shortcut_v1", .version = 1,
    .method_count = 1, .methods = _CHyprlandGlobalShortcutV1Requests,
    .event_count = 2, .events = _CHyprlandGlobalShortcutV1Events,
};

CHyprlandGlobalShortcutV1::CHyprlandGlobalShortcutV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_global_shortcut_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandGlobalShortcutV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandGlobalShortcutV1VTable, this, nullptr);
}

CHyprlandGlobalShortcutV1::~CHyprlandGlobalShortcutV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandGlobalShortcutV1::onDestroyCalled() {
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

void CHyprlandGlobalShortcutV1::setDestroy(F<void(CHyprlandGlobalShortcutV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

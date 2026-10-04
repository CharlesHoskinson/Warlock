// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// vicinae_hotkey_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2026 Aurelien Brabant

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
#include "vicinae-hotkey-v1.hpp"
#undef private
#define F std::function

static const wl_interface* vicinaeHotkeyV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface vicinae_hotkey_manager_v1_interface;
extern const wl_interface vicinae_hotkey_v1_interface;
extern const wl_interface wl_seat_interface;

static void _CVicinaeHotkeyManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CVicinaeHotkeyManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CVicinaeHotkeyManagerV1Bind(wl_client* client, wl_resource* resource, uint32_t id, uint32_t keysym, vicinaeHotkeyManagerV1Modifiers modifiers, wl_resource* seat, const char* app_id, const char* description) {
    const auto PO = (CVicinaeHotkeyManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.bind)
        PO->requests.bind(PO, id, keysym, modifiers, seat, app_id, description);
}

static void _CVicinaeHotkeyManagerV1__DestroyListener(wl_listener* l, void* d) {
    CVicinaeHotkeyManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CVicinaeHotkeyManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CVicinaeHotkeyManagerV1VTable[] = {
    (void*)_CVicinaeHotkeyManagerV1Destroy,
    (void*)_CVicinaeHotkeyManagerV1Bind,
};
static const wl_interface* _CVicinaeHotkeyManagerV1BindTypes[] = {
    &vicinae_hotkey_v1_interface,
    nullptr,
    nullptr,
    &wl_seat_interface,
    nullptr,
    nullptr,
};

static const wl_message _CVicinaeHotkeyManagerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = vicinaeHotkeyV1_dummyTypes + 0},
    { .name = "bind", .signature = "nuu?oss", .types = _CVicinaeHotkeyManagerV1BindTypes + 0},
};

const wl_interface vicinae_hotkey_manager_v1_interface = {
    .name = "vicinae_hotkey_manager_v1", .version = 1,
    .method_count = 2, .methods = _CVicinaeHotkeyManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CVicinaeHotkeyManagerV1::CVicinaeHotkeyManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &vicinae_hotkey_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CVicinaeHotkeyManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CVicinaeHotkeyManagerV1VTable, this, nullptr);
}

CVicinaeHotkeyManagerV1::~CVicinaeHotkeyManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CVicinaeHotkeyManagerV1::onDestroyCalled() {
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

void CVicinaeHotkeyManagerV1::setDestroy(F<void(CVicinaeHotkeyManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CVicinaeHotkeyManagerV1::setBind(F<void(CVicinaeHotkeyManagerV1*, uint32_t, uint32_t, vicinaeHotkeyManagerV1Modifiers, wl_resource*, const char*, const char*)> &&handler) {
    requests.bind = std::move(handler);
}

static void _CVicinaeHotkeyV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CVicinaeHotkeyV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CVicinaeHotkeyV1__DestroyListener(wl_listener* l, void* d) {
    CVicinaeHotkeyV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CVicinaeHotkeyV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CVicinaeHotkeyV1VTable[] = {
    (void*)_CVicinaeHotkeyV1Destroy,
};

void CVicinaeHotkeyV1::sendBound() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CVicinaeHotkeyV1::sendDenied(vicinaeHotkeyV1DenyReason reason, const char* message) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, reason, message);
}

void CVicinaeHotkeyV1::sendRevoked(vicinaeHotkeyV1RevokeReason reason, const char* message) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, reason, message);
}

void CVicinaeHotkeyV1::sendPressed(uint32_t serial, uint32_t time) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, serial, time);
}

void CVicinaeHotkeyV1::sendReleased(uint32_t serial, uint32_t time) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, serial, time);
}

void CVicinaeHotkeyV1::sendBoundRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CVicinaeHotkeyV1::sendDeniedRaw(vicinaeHotkeyV1DenyReason reason, const char* message) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, reason, message);
}

void CVicinaeHotkeyV1::sendRevokedRaw(vicinaeHotkeyV1RevokeReason reason, const char* message) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, reason, message);
}

void CVicinaeHotkeyV1::sendPressedRaw(uint32_t serial, uint32_t time) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, serial, time);
}

void CVicinaeHotkeyV1::sendReleasedRaw(uint32_t serial, uint32_t time) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, serial, time);
}
static const wl_interface* _CVicinaeHotkeyV1DeniedTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CVicinaeHotkeyV1RevokedTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CVicinaeHotkeyV1PressedTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CVicinaeHotkeyV1ReleasedTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CVicinaeHotkeyV1Requests[] = {
    { .name = "destroy", .signature = "", .types = vicinaeHotkeyV1_dummyTypes + 0},
};

static const wl_message _CVicinaeHotkeyV1Events[] = {
    { .name = "bound", .signature = "", .types = vicinaeHotkeyV1_dummyTypes + 0},
    { .name = "denied", .signature = "us", .types = _CVicinaeHotkeyV1DeniedTypes + 0},
    { .name = "revoked", .signature = "us", .types = _CVicinaeHotkeyV1RevokedTypes + 0},
    { .name = "pressed", .signature = "uu", .types = _CVicinaeHotkeyV1PressedTypes + 0},
    { .name = "released", .signature = "uu", .types = _CVicinaeHotkeyV1ReleasedTypes + 0},
};

const wl_interface vicinae_hotkey_v1_interface = {
    .name = "vicinae_hotkey_v1", .version = 1,
    .method_count = 1, .methods = _CVicinaeHotkeyV1Requests,
    .event_count = 5, .events = _CVicinaeHotkeyV1Events,
};

CVicinaeHotkeyV1::CVicinaeHotkeyV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &vicinae_hotkey_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CVicinaeHotkeyV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CVicinaeHotkeyV1VTable, this, nullptr);
}

CVicinaeHotkeyV1::~CVicinaeHotkeyV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CVicinaeHotkeyV1::onDestroyCalled() {
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

void CVicinaeHotkeyV1::setDestroy(F<void(CVicinaeHotkeyV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

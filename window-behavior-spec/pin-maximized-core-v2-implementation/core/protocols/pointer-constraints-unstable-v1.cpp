// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// pointer_constraints_unstable_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2014      Jonas Ådahl
    Copyright © 2015      Red Hat Inc.

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
#include "pointer-constraints-unstable-v1.hpp"
#undef private
#define F std::function

static const wl_interface* pointerConstraintsUnstableV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface zwp_pointer_constraints_v1_interface;
extern const wl_interface zwp_locked_pointer_v1_interface;
extern const wl_interface zwp_confined_pointer_v1_interface;
extern const wl_interface wl_surface_interface;
extern const wl_interface wl_pointer_interface;
extern const wl_interface wl_region_interface;

static void _CZwpPointerConstraintsV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpPointerConstraintsV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpPointerConstraintsV1LockPointer(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface, wl_resource* pointer, wl_resource* region, zwpPointerConstraintsV1Lifetime lifetime) {
    const auto PO = (CZwpPointerConstraintsV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.lockPointer)
        PO->requests.lockPointer(PO, id, surface, pointer, region, lifetime);
}

static void _CZwpPointerConstraintsV1ConfinePointer(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface, wl_resource* pointer, wl_resource* region, zwpPointerConstraintsV1Lifetime lifetime) {
    const auto PO = (CZwpPointerConstraintsV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.confinePointer)
        PO->requests.confinePointer(PO, id, surface, pointer, region, lifetime);
}

static void _CZwpPointerConstraintsV1__DestroyListener(wl_listener* l, void* d) {
    CZwpPointerConstraintsV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpPointerConstraintsV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpPointerConstraintsV1VTable[] = {
    (void*)_CZwpPointerConstraintsV1Destroy,
    (void*)_CZwpPointerConstraintsV1LockPointer,
    (void*)_CZwpPointerConstraintsV1ConfinePointer,
};
static const wl_interface* _CZwpPointerConstraintsV1LockPointerTypes[] = {
    &zwp_locked_pointer_v1_interface,
    &wl_surface_interface,
    &wl_pointer_interface,
    &wl_region_interface,
    nullptr,
};
static const wl_interface* _CZwpPointerConstraintsV1ConfinePointerTypes[] = {
    &zwp_confined_pointer_v1_interface,
    &wl_surface_interface,
    &wl_pointer_interface,
    &wl_region_interface,
    nullptr,
};

static const wl_message _CZwpPointerConstraintsV1Requests[] = {
    { .name = "destroy", .signature = "", .types = pointerConstraintsUnstableV1_dummyTypes + 0},
    { .name = "lock_pointer", .signature = "noo?ou", .types = _CZwpPointerConstraintsV1LockPointerTypes + 0},
    { .name = "confine_pointer", .signature = "noo?ou", .types = _CZwpPointerConstraintsV1ConfinePointerTypes + 0},
};

const wl_interface zwp_pointer_constraints_v1_interface = {
    .name = "zwp_pointer_constraints_v1", .version = 1,
    .method_count = 3, .methods = _CZwpPointerConstraintsV1Requests,
    .event_count = 0, .events = nullptr,
};

CZwpPointerConstraintsV1::CZwpPointerConstraintsV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_pointer_constraints_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpPointerConstraintsV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpPointerConstraintsV1VTable, this, nullptr);
}

CZwpPointerConstraintsV1::~CZwpPointerConstraintsV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpPointerConstraintsV1::onDestroyCalled() {
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

void CZwpPointerConstraintsV1::setDestroy(F<void(CZwpPointerConstraintsV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZwpPointerConstraintsV1::setLockPointer(F<void(CZwpPointerConstraintsV1*, uint32_t, wl_resource*, wl_resource*, wl_resource*, zwpPointerConstraintsV1Lifetime)> &&handler) {
    requests.lockPointer = std::move(handler);
}

void CZwpPointerConstraintsV1::setConfinePointer(F<void(CZwpPointerConstraintsV1*, uint32_t, wl_resource*, wl_resource*, wl_resource*, zwpPointerConstraintsV1Lifetime)> &&handler) {
    requests.confinePointer = std::move(handler);
}

static void _CZwpLockedPointerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpLockedPointerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpLockedPointerV1SetCursorPositionHint(wl_client* client, wl_resource* resource, wl_fixed_t surface_x, wl_fixed_t surface_y) {
    const auto PO = (CZwpLockedPointerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setCursorPositionHint)
        PO->requests.setCursorPositionHint(PO, surface_x, surface_y);
}

static void _CZwpLockedPointerV1SetRegion(wl_client* client, wl_resource* resource, wl_resource* region) {
    const auto PO = (CZwpLockedPointerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setRegion)
        PO->requests.setRegion(PO, region);
}

static void _CZwpLockedPointerV1__DestroyListener(wl_listener* l, void* d) {
    CZwpLockedPointerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpLockedPointerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpLockedPointerV1VTable[] = {
    (void*)_CZwpLockedPointerV1Destroy,
    (void*)_CZwpLockedPointerV1SetCursorPositionHint,
    (void*)_CZwpLockedPointerV1SetRegion,
};

void CZwpLockedPointerV1::sendLocked() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CZwpLockedPointerV1::sendUnlocked() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CZwpLockedPointerV1::sendLockedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CZwpLockedPointerV1::sendUnlockedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}
static const wl_interface* _CZwpLockedPointerV1SetCursorPositionHintTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CZwpLockedPointerV1SetRegionTypes[] = {
    &wl_region_interface,
};

static const wl_message _CZwpLockedPointerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = pointerConstraintsUnstableV1_dummyTypes + 0},
    { .name = "set_cursor_position_hint", .signature = "ff", .types = _CZwpLockedPointerV1SetCursorPositionHintTypes + 0},
    { .name = "set_region", .signature = "?o", .types = _CZwpLockedPointerV1SetRegionTypes + 0},
};

static const wl_message _CZwpLockedPointerV1Events[] = {
    { .name = "locked", .signature = "", .types = pointerConstraintsUnstableV1_dummyTypes + 0},
    { .name = "unlocked", .signature = "", .types = pointerConstraintsUnstableV1_dummyTypes + 0},
};

const wl_interface zwp_locked_pointer_v1_interface = {
    .name = "zwp_locked_pointer_v1", .version = 1,
    .method_count = 3, .methods = _CZwpLockedPointerV1Requests,
    .event_count = 2, .events = _CZwpLockedPointerV1Events,
};

CZwpLockedPointerV1::CZwpLockedPointerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_locked_pointer_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpLockedPointerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpLockedPointerV1VTable, this, nullptr);
}

CZwpLockedPointerV1::~CZwpLockedPointerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpLockedPointerV1::onDestroyCalled() {
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

void CZwpLockedPointerV1::setDestroy(F<void(CZwpLockedPointerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZwpLockedPointerV1::setSetCursorPositionHint(F<void(CZwpLockedPointerV1*, wl_fixed_t, wl_fixed_t)> &&handler) {
    requests.setCursorPositionHint = std::move(handler);
}

void CZwpLockedPointerV1::setSetRegion(F<void(CZwpLockedPointerV1*, wl_resource*)> &&handler) {
    requests.setRegion = std::move(handler);
}

static void _CZwpConfinedPointerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpConfinedPointerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpConfinedPointerV1SetRegion(wl_client* client, wl_resource* resource, wl_resource* region) {
    const auto PO = (CZwpConfinedPointerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setRegion)
        PO->requests.setRegion(PO, region);
}

static void _CZwpConfinedPointerV1__DestroyListener(wl_listener* l, void* d) {
    CZwpConfinedPointerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpConfinedPointerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpConfinedPointerV1VTable[] = {
    (void*)_CZwpConfinedPointerV1Destroy,
    (void*)_CZwpConfinedPointerV1SetRegion,
};

void CZwpConfinedPointerV1::sendConfined() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CZwpConfinedPointerV1::sendUnconfined() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CZwpConfinedPointerV1::sendConfinedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CZwpConfinedPointerV1::sendUnconfinedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}
static const wl_interface* _CZwpConfinedPointerV1SetRegionTypes[] = {
    &wl_region_interface,
};

static const wl_message _CZwpConfinedPointerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = pointerConstraintsUnstableV1_dummyTypes + 0},
    { .name = "set_region", .signature = "?o", .types = _CZwpConfinedPointerV1SetRegionTypes + 0},
};

static const wl_message _CZwpConfinedPointerV1Events[] = {
    { .name = "confined", .signature = "", .types = pointerConstraintsUnstableV1_dummyTypes + 0},
    { .name = "unconfined", .signature = "", .types = pointerConstraintsUnstableV1_dummyTypes + 0},
};

const wl_interface zwp_confined_pointer_v1_interface = {
    .name = "zwp_confined_pointer_v1", .version = 1,
    .method_count = 2, .methods = _CZwpConfinedPointerV1Requests,
    .event_count = 2, .events = _CZwpConfinedPointerV1Events,
};

CZwpConfinedPointerV1::CZwpConfinedPointerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_confined_pointer_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpConfinedPointerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpConfinedPointerV1VTable, this, nullptr);
}

CZwpConfinedPointerV1::~CZwpConfinedPointerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpConfinedPointerV1::onDestroyCalled() {
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

void CZwpConfinedPointerV1::setDestroy(F<void(CZwpConfinedPointerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZwpConfinedPointerV1::setSetRegion(F<void(CZwpConfinedPointerV1*, wl_resource*)> &&handler) {
    requests.setRegion = std::move(handler);
}

#undef F

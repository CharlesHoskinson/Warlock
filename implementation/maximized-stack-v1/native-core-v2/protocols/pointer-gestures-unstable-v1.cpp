// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// pointer_gestures_unstable_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2015, 2021 Red Hat Inc.

    Permission to use, copy, modify, distribute, and sell this
    software and its documentation for any purpose is hereby granted
    without fee, provided that the above copyright notice appear in
    all copies and that both that copyright notice and this permission
    notice appear in supporting documentation, and that the name of
    the copyright holders not be used in advertising or publicity
    pertaining to distribution of the software without specific,
    written prior permission.  The copyright holders make no
    representations about the suitability of this software for any
    purpose.  It is provided "as is" without express or implied
    warranty.

    THE COPYRIGHT HOLDERS DISCLAIM ALL WARRANTIES WITH REGARD TO THIS
    SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
    FITNESS, IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
    SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
    AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
    ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
    THIS SOFTWARE.
  
*/

#define private public
#define HYPRWAYLAND_SCANNER_NO_INTERFACES
#include "pointer-gestures-unstable-v1.hpp"
#undef private
#define F std::function

static const wl_interface* pointerGesturesUnstableV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface zwp_pointer_gestures_v1_interface;
extern const wl_interface zwp_pointer_gesture_swipe_v1_interface;
extern const wl_interface zwp_pointer_gesture_pinch_v1_interface;
extern const wl_interface zwp_pointer_gesture_hold_v1_interface;
extern const wl_interface wl_pointer_interface;
extern const wl_interface wl_surface_interface;

static void _CZwpPointerGesturesV1GetSwipeGesture(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* pointer) {
    const auto PO = (CZwpPointerGesturesV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getSwipeGesture)
        PO->requests.getSwipeGesture(PO, id, pointer);
}

static void _CZwpPointerGesturesV1GetPinchGesture(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* pointer) {
    const auto PO = (CZwpPointerGesturesV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getPinchGesture)
        PO->requests.getPinchGesture(PO, id, pointer);
}

static void _CZwpPointerGesturesV1Release(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpPointerGesturesV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CZwpPointerGesturesV1GetHoldGesture(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* pointer) {
    const auto PO = (CZwpPointerGesturesV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getHoldGesture)
        PO->requests.getHoldGesture(PO, id, pointer);
}

static void _CZwpPointerGesturesV1__DestroyListener(wl_listener* l, void* d) {
    CZwpPointerGesturesV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpPointerGesturesV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpPointerGesturesV1VTable[] = {
    (void*)_CZwpPointerGesturesV1GetSwipeGesture,
    (void*)_CZwpPointerGesturesV1GetPinchGesture,
    (void*)_CZwpPointerGesturesV1Release,
    (void*)_CZwpPointerGesturesV1GetHoldGesture,
};
static const wl_interface* _CZwpPointerGesturesV1GetSwipeGestureTypes[] = {
    &zwp_pointer_gesture_swipe_v1_interface,
    &wl_pointer_interface,
};
static const wl_interface* _CZwpPointerGesturesV1GetPinchGestureTypes[] = {
    &zwp_pointer_gesture_pinch_v1_interface,
    &wl_pointer_interface,
};
static const wl_interface* _CZwpPointerGesturesV1GetHoldGestureTypes[] = {
    &zwp_pointer_gesture_hold_v1_interface,
    &wl_pointer_interface,
};

static const wl_message _CZwpPointerGesturesV1Requests[] = {
    { .name = "get_swipe_gesture", .signature = "no", .types = _CZwpPointerGesturesV1GetSwipeGestureTypes + 0},
    { .name = "get_pinch_gesture", .signature = "no", .types = _CZwpPointerGesturesV1GetPinchGestureTypes + 0},
    { .name = "release", .signature = "2", .types = pointerGesturesUnstableV1_dummyTypes + 0},
    { .name = "get_hold_gesture", .signature = "3no", .types = _CZwpPointerGesturesV1GetHoldGestureTypes + 0},
};

const wl_interface zwp_pointer_gestures_v1_interface = {
    .name = "zwp_pointer_gestures_v1", .version = 3,
    .method_count = 4, .methods = _CZwpPointerGesturesV1Requests,
    .event_count = 0, .events = nullptr,
};

CZwpPointerGesturesV1::CZwpPointerGesturesV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_pointer_gestures_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpPointerGesturesV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpPointerGesturesV1VTable, this, nullptr);
}

CZwpPointerGesturesV1::~CZwpPointerGesturesV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpPointerGesturesV1::onDestroyCalled() {
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

void CZwpPointerGesturesV1::setGetSwipeGesture(F<void(CZwpPointerGesturesV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getSwipeGesture = std::move(handler);
}

void CZwpPointerGesturesV1::setGetPinchGesture(F<void(CZwpPointerGesturesV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getPinchGesture = std::move(handler);
}

void CZwpPointerGesturesV1::setRelease(F<void(CZwpPointerGesturesV1*)> &&handler) {
    requests.release = std::move(handler);
}

void CZwpPointerGesturesV1::setGetHoldGesture(F<void(CZwpPointerGesturesV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getHoldGesture = std::move(handler);
}

static void _CZwpPointerGestureSwipeV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpPointerGestureSwipeV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpPointerGestureSwipeV1__DestroyListener(wl_listener* l, void* d) {
    CZwpPointerGestureSwipeV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpPointerGestureSwipeV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpPointerGestureSwipeV1VTable[] = {
    (void*)_CZwpPointerGestureSwipeV1Destroy,
};

void CZwpPointerGestureSwipeV1::sendBegin(uint32_t serial, uint32_t time, wl_resource* surface, uint32_t fingers) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, time, surface, fingers);
}

void CZwpPointerGestureSwipeV1::sendUpdate(uint32_t time, wl_fixed_t dx, wl_fixed_t dy) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, time, dx, dy);
}

void CZwpPointerGestureSwipeV1::sendEnd(uint32_t serial, uint32_t time, int32_t cancelled) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, serial, time, cancelled);
}

void CZwpPointerGestureSwipeV1::sendBeginRaw(uint32_t serial, uint32_t time, wl_resource* surface, uint32_t fingers) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, time, surface, fingers);
}

void CZwpPointerGestureSwipeV1::sendUpdateRaw(uint32_t time, wl_fixed_t dx, wl_fixed_t dy) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, time, dx, dy);
}

void CZwpPointerGestureSwipeV1::sendEndRaw(uint32_t serial, uint32_t time, int32_t cancelled) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, serial, time, cancelled);
}
static const wl_interface* _CZwpPointerGestureSwipeV1BeginTypes[] = {
    nullptr,
    nullptr,
    &wl_surface_interface,
    nullptr,
};
static const wl_interface* _CZwpPointerGestureSwipeV1UpdateTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CZwpPointerGestureSwipeV1EndTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CZwpPointerGestureSwipeV1Requests[] = {
    { .name = "destroy", .signature = "", .types = pointerGesturesUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwpPointerGestureSwipeV1Events[] = {
    { .name = "begin", .signature = "uuou", .types = _CZwpPointerGestureSwipeV1BeginTypes + 0},
    { .name = "update", .signature = "uff", .types = _CZwpPointerGestureSwipeV1UpdateTypes + 0},
    { .name = "end", .signature = "uui", .types = _CZwpPointerGestureSwipeV1EndTypes + 0},
};

const wl_interface zwp_pointer_gesture_swipe_v1_interface = {
    .name = "zwp_pointer_gesture_swipe_v1", .version = 3,
    .method_count = 1, .methods = _CZwpPointerGestureSwipeV1Requests,
    .event_count = 3, .events = _CZwpPointerGestureSwipeV1Events,
};

CZwpPointerGestureSwipeV1::CZwpPointerGestureSwipeV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_pointer_gesture_swipe_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpPointerGestureSwipeV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpPointerGestureSwipeV1VTable, this, nullptr);
}

CZwpPointerGestureSwipeV1::~CZwpPointerGestureSwipeV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpPointerGestureSwipeV1::onDestroyCalled() {
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

void CZwpPointerGestureSwipeV1::setDestroy(F<void(CZwpPointerGestureSwipeV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZwpPointerGesturePinchV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpPointerGesturePinchV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpPointerGesturePinchV1__DestroyListener(wl_listener* l, void* d) {
    CZwpPointerGesturePinchV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpPointerGesturePinchV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpPointerGesturePinchV1VTable[] = {
    (void*)_CZwpPointerGesturePinchV1Destroy,
};

void CZwpPointerGesturePinchV1::sendBegin(uint32_t serial, uint32_t time, wl_resource* surface, uint32_t fingers) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, time, surface, fingers);
}

void CZwpPointerGesturePinchV1::sendUpdate(uint32_t time, wl_fixed_t dx, wl_fixed_t dy, wl_fixed_t scale, wl_fixed_t rotation) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, time, dx, dy, scale, rotation);
}

void CZwpPointerGesturePinchV1::sendEnd(uint32_t serial, uint32_t time, int32_t cancelled) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, serial, time, cancelled);
}

void CZwpPointerGesturePinchV1::sendBeginRaw(uint32_t serial, uint32_t time, wl_resource* surface, uint32_t fingers) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, time, surface, fingers);
}

void CZwpPointerGesturePinchV1::sendUpdateRaw(uint32_t time, wl_fixed_t dx, wl_fixed_t dy, wl_fixed_t scale, wl_fixed_t rotation) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, time, dx, dy, scale, rotation);
}

void CZwpPointerGesturePinchV1::sendEndRaw(uint32_t serial, uint32_t time, int32_t cancelled) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, serial, time, cancelled);
}
static const wl_interface* _CZwpPointerGesturePinchV1BeginTypes[] = {
    nullptr,
    nullptr,
    &wl_surface_interface,
    nullptr,
};
static const wl_interface* _CZwpPointerGesturePinchV1UpdateTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CZwpPointerGesturePinchV1EndTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CZwpPointerGesturePinchV1Requests[] = {
    { .name = "destroy", .signature = "", .types = pointerGesturesUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwpPointerGesturePinchV1Events[] = {
    { .name = "begin", .signature = "uuou", .types = _CZwpPointerGesturePinchV1BeginTypes + 0},
    { .name = "update", .signature = "uffff", .types = _CZwpPointerGesturePinchV1UpdateTypes + 0},
    { .name = "end", .signature = "uui", .types = _CZwpPointerGesturePinchV1EndTypes + 0},
};

const wl_interface zwp_pointer_gesture_pinch_v1_interface = {
    .name = "zwp_pointer_gesture_pinch_v1", .version = 3,
    .method_count = 1, .methods = _CZwpPointerGesturePinchV1Requests,
    .event_count = 3, .events = _CZwpPointerGesturePinchV1Events,
};

CZwpPointerGesturePinchV1::CZwpPointerGesturePinchV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_pointer_gesture_pinch_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpPointerGesturePinchV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpPointerGesturePinchV1VTable, this, nullptr);
}

CZwpPointerGesturePinchV1::~CZwpPointerGesturePinchV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpPointerGesturePinchV1::onDestroyCalled() {
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

void CZwpPointerGesturePinchV1::setDestroy(F<void(CZwpPointerGesturePinchV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZwpPointerGestureHoldV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpPointerGestureHoldV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpPointerGestureHoldV1__DestroyListener(wl_listener* l, void* d) {
    CZwpPointerGestureHoldV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpPointerGestureHoldV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpPointerGestureHoldV1VTable[] = {
    (void*)_CZwpPointerGestureHoldV1Destroy,
};

void CZwpPointerGestureHoldV1::sendBegin(uint32_t serial, uint32_t time, wl_resource* surface, uint32_t fingers) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, time, surface, fingers);
}

void CZwpPointerGestureHoldV1::sendEnd(uint32_t serial, uint32_t time, int32_t cancelled) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, time, cancelled);
}

void CZwpPointerGestureHoldV1::sendBeginRaw(uint32_t serial, uint32_t time, wl_resource* surface, uint32_t fingers) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, time, surface, fingers);
}

void CZwpPointerGestureHoldV1::sendEndRaw(uint32_t serial, uint32_t time, int32_t cancelled) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, time, cancelled);
}
static const wl_interface* _CZwpPointerGestureHoldV1BeginTypes[] = {
    nullptr,
    nullptr,
    &wl_surface_interface,
    nullptr,
};
static const wl_interface* _CZwpPointerGestureHoldV1EndTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CZwpPointerGestureHoldV1Requests[] = {
    { .name = "destroy", .signature = "3", .types = pointerGesturesUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwpPointerGestureHoldV1Events[] = {
    { .name = "begin", .signature = "3uuou", .types = _CZwpPointerGestureHoldV1BeginTypes + 0},
    { .name = "end", .signature = "3uui", .types = _CZwpPointerGestureHoldV1EndTypes + 0},
};

const wl_interface zwp_pointer_gesture_hold_v1_interface = {
    .name = "zwp_pointer_gesture_hold_v1", .version = 3,
    .method_count = 1, .methods = _CZwpPointerGestureHoldV1Requests,
    .event_count = 2, .events = _CZwpPointerGestureHoldV1Events,
};

CZwpPointerGestureHoldV1::CZwpPointerGestureHoldV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_pointer_gesture_hold_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpPointerGestureHoldV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpPointerGestureHoldV1VTable, this, nullptr);
}

CZwpPointerGestureHoldV1::~CZwpPointerGestureHoldV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpPointerGestureHoldV1::onDestroyCalled() {
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

void CZwpPointerGestureHoldV1::setDestroy(F<void(CZwpPointerGestureHoldV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

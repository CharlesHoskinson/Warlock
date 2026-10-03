// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// commit_timing_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2023 Valve Corporation

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
#include "commit-timing-v1.hpp"
#undef private
#define F std::function

static const wl_interface* commitTimingV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wp_commit_timing_manager_v1_interface;
extern const wl_interface wp_commit_timer_v1_interface;
extern const wl_interface wl_surface_interface;

static void _CWpCommitTimingManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpCommitTimingManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpCommitTimingManagerV1GetTimer(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CWpCommitTimingManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getTimer)
        PO->requests.getTimer(PO, id, surface);
}

static void _CWpCommitTimingManagerV1__DestroyListener(wl_listener* l, void* d) {
    CWpCommitTimingManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpCommitTimingManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpCommitTimingManagerV1VTable[] = {
    (void*)_CWpCommitTimingManagerV1Destroy,
    (void*)_CWpCommitTimingManagerV1GetTimer,
};
static const wl_interface* _CWpCommitTimingManagerV1GetTimerTypes[] = {
    &wp_commit_timer_v1_interface,
    &wl_surface_interface,
};

static const wl_message _CWpCommitTimingManagerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = commitTimingV1_dummyTypes + 0},
    { .name = "get_timer", .signature = "no", .types = _CWpCommitTimingManagerV1GetTimerTypes + 0},
};

const wl_interface wp_commit_timing_manager_v1_interface = {
    .name = "wp_commit_timing_manager_v1", .version = 1,
    .method_count = 2, .methods = _CWpCommitTimingManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpCommitTimingManagerV1::CWpCommitTimingManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_commit_timing_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpCommitTimingManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpCommitTimingManagerV1VTable, this, nullptr);
}

CWpCommitTimingManagerV1::~CWpCommitTimingManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpCommitTimingManagerV1::onDestroyCalled() {
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

void CWpCommitTimingManagerV1::setDestroy(F<void(CWpCommitTimingManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpCommitTimingManagerV1::setGetTimer(F<void(CWpCommitTimingManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getTimer = std::move(handler);
}

static void _CWpCommitTimerV1SetTimestamp(wl_client* client, wl_resource* resource, uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    const auto PO = (CWpCommitTimerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setTimestamp)
        PO->requests.setTimestamp(PO, tv_sec_hi, tv_sec_lo, tv_nsec);
}

static void _CWpCommitTimerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpCommitTimerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpCommitTimerV1__DestroyListener(wl_listener* l, void* d) {
    CWpCommitTimerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpCommitTimerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpCommitTimerV1VTable[] = {
    (void*)_CWpCommitTimerV1SetTimestamp,
    (void*)_CWpCommitTimerV1Destroy,
};
static const wl_interface* _CWpCommitTimerV1SetTimestampTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CWpCommitTimerV1Requests[] = {
    { .name = "set_timestamp", .signature = "uuu", .types = _CWpCommitTimerV1SetTimestampTypes + 0},
    { .name = "destroy", .signature = "", .types = commitTimingV1_dummyTypes + 0},
};

const wl_interface wp_commit_timer_v1_interface = {
    .name = "wp_commit_timer_v1", .version = 1,
    .method_count = 2, .methods = _CWpCommitTimerV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpCommitTimerV1::CWpCommitTimerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_commit_timer_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpCommitTimerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpCommitTimerV1VTable, this, nullptr);
}

CWpCommitTimerV1::~CWpCommitTimerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpCommitTimerV1::onDestroyCalled() {
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

void CWpCommitTimerV1::setSetTimestamp(F<void(CWpCommitTimerV1*, uint32_t, uint32_t, uint32_t)> &&handler) {
    requests.setTimestamp = std::move(handler);
}

void CWpCommitTimerV1::setDestroy(F<void(CWpCommitTimerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

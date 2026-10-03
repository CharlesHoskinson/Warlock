// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// linux_drm_syncobj_v1

/*
 This protocol's authors' copyright notice is:


    Copyright 2016 The Chromium Authors.
    Copyright 2017 Intel Corporation
    Copyright 2018 Collabora, Ltd
    Copyright 2021 Simon Ser

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
#include "linux-drm-syncobj-v1.hpp"
#undef private
#define F std::function

static const wl_interface* linuxDrmSyncobjV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wp_linux_drm_syncobj_manager_v1_interface;
extern const wl_interface wp_linux_drm_syncobj_timeline_v1_interface;
extern const wl_interface wp_linux_drm_syncobj_surface_v1_interface;
extern const wl_interface wl_surface_interface;

static void _CWpLinuxDrmSyncobjManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpLinuxDrmSyncobjManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpLinuxDrmSyncobjManagerV1GetSurface(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CWpLinuxDrmSyncobjManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getSurface)
        PO->requests.getSurface(PO, id, surface);
}

static void _CWpLinuxDrmSyncobjManagerV1ImportTimeline(wl_client* client, wl_resource* resource, uint32_t id, int32_t fd) {
    const auto PO = (CWpLinuxDrmSyncobjManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.importTimeline)
        PO->requests.importTimeline(PO, id, fd);
}

static void _CWpLinuxDrmSyncobjManagerV1__DestroyListener(wl_listener* l, void* d) {
    CWpLinuxDrmSyncobjManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpLinuxDrmSyncobjManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpLinuxDrmSyncobjManagerV1VTable[] = {
    (void*)_CWpLinuxDrmSyncobjManagerV1Destroy,
    (void*)_CWpLinuxDrmSyncobjManagerV1GetSurface,
    (void*)_CWpLinuxDrmSyncobjManagerV1ImportTimeline,
};
static const wl_interface* _CWpLinuxDrmSyncobjManagerV1GetSurfaceTypes[] = {
    &wp_linux_drm_syncobj_surface_v1_interface,
    &wl_surface_interface,
};
static const wl_interface* _CWpLinuxDrmSyncobjManagerV1ImportTimelineTypes[] = {
    &wp_linux_drm_syncobj_timeline_v1_interface,
    nullptr,
};

static const wl_message _CWpLinuxDrmSyncobjManagerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = linuxDrmSyncobjV1_dummyTypes + 0},
    { .name = "get_surface", .signature = "no", .types = _CWpLinuxDrmSyncobjManagerV1GetSurfaceTypes + 0},
    { .name = "import_timeline", .signature = "nh", .types = _CWpLinuxDrmSyncobjManagerV1ImportTimelineTypes + 0},
};

const wl_interface wp_linux_drm_syncobj_manager_v1_interface = {
    .name = "wp_linux_drm_syncobj_manager_v1", .version = 1,
    .method_count = 3, .methods = _CWpLinuxDrmSyncobjManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpLinuxDrmSyncobjManagerV1::CWpLinuxDrmSyncobjManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_linux_drm_syncobj_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpLinuxDrmSyncobjManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpLinuxDrmSyncobjManagerV1VTable, this, nullptr);
}

CWpLinuxDrmSyncobjManagerV1::~CWpLinuxDrmSyncobjManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpLinuxDrmSyncobjManagerV1::onDestroyCalled() {
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

void CWpLinuxDrmSyncobjManagerV1::setDestroy(F<void(CWpLinuxDrmSyncobjManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpLinuxDrmSyncobjManagerV1::setGetSurface(F<void(CWpLinuxDrmSyncobjManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getSurface = std::move(handler);
}

void CWpLinuxDrmSyncobjManagerV1::setImportTimeline(F<void(CWpLinuxDrmSyncobjManagerV1*, uint32_t, int32_t)> &&handler) {
    requests.importTimeline = std::move(handler);
}

static void _CWpLinuxDrmSyncobjTimelineV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpLinuxDrmSyncobjTimelineV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpLinuxDrmSyncobjTimelineV1__DestroyListener(wl_listener* l, void* d) {
    CWpLinuxDrmSyncobjTimelineV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpLinuxDrmSyncobjTimelineV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpLinuxDrmSyncobjTimelineV1VTable[] = {
    (void*)_CWpLinuxDrmSyncobjTimelineV1Destroy,
};

static const wl_message _CWpLinuxDrmSyncobjTimelineV1Requests[] = {
    { .name = "destroy", .signature = "", .types = linuxDrmSyncobjV1_dummyTypes + 0},
};

const wl_interface wp_linux_drm_syncobj_timeline_v1_interface = {
    .name = "wp_linux_drm_syncobj_timeline_v1", .version = 1,
    .method_count = 1, .methods = _CWpLinuxDrmSyncobjTimelineV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpLinuxDrmSyncobjTimelineV1::CWpLinuxDrmSyncobjTimelineV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_linux_drm_syncobj_timeline_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpLinuxDrmSyncobjTimelineV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpLinuxDrmSyncobjTimelineV1VTable, this, nullptr);
}

CWpLinuxDrmSyncobjTimelineV1::~CWpLinuxDrmSyncobjTimelineV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpLinuxDrmSyncobjTimelineV1::onDestroyCalled() {
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

void CWpLinuxDrmSyncobjTimelineV1::setDestroy(F<void(CWpLinuxDrmSyncobjTimelineV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CWpLinuxDrmSyncobjSurfaceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpLinuxDrmSyncobjSurfaceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpLinuxDrmSyncobjSurfaceV1SetAcquirePoint(wl_client* client, wl_resource* resource, wl_resource* timeline, uint32_t point_hi, uint32_t point_lo) {
    const auto PO = (CWpLinuxDrmSyncobjSurfaceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setAcquirePoint)
        PO->requests.setAcquirePoint(PO, timeline, point_hi, point_lo);
}

static void _CWpLinuxDrmSyncobjSurfaceV1SetReleasePoint(wl_client* client, wl_resource* resource, wl_resource* timeline, uint32_t point_hi, uint32_t point_lo) {
    const auto PO = (CWpLinuxDrmSyncobjSurfaceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setReleasePoint)
        PO->requests.setReleasePoint(PO, timeline, point_hi, point_lo);
}

static void _CWpLinuxDrmSyncobjSurfaceV1__DestroyListener(wl_listener* l, void* d) {
    CWpLinuxDrmSyncobjSurfaceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpLinuxDrmSyncobjSurfaceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpLinuxDrmSyncobjSurfaceV1VTable[] = {
    (void*)_CWpLinuxDrmSyncobjSurfaceV1Destroy,
    (void*)_CWpLinuxDrmSyncobjSurfaceV1SetAcquirePoint,
    (void*)_CWpLinuxDrmSyncobjSurfaceV1SetReleasePoint,
};
static const wl_interface* _CWpLinuxDrmSyncobjSurfaceV1SetAcquirePointTypes[] = {
    &wp_linux_drm_syncobj_timeline_v1_interface,
    nullptr,
    nullptr,
};
static const wl_interface* _CWpLinuxDrmSyncobjSurfaceV1SetReleasePointTypes[] = {
    &wp_linux_drm_syncobj_timeline_v1_interface,
    nullptr,
    nullptr,
};

static const wl_message _CWpLinuxDrmSyncobjSurfaceV1Requests[] = {
    { .name = "destroy", .signature = "", .types = linuxDrmSyncobjV1_dummyTypes + 0},
    { .name = "set_acquire_point", .signature = "ouu", .types = _CWpLinuxDrmSyncobjSurfaceV1SetAcquirePointTypes + 0},
    { .name = "set_release_point", .signature = "ouu", .types = _CWpLinuxDrmSyncobjSurfaceV1SetReleasePointTypes + 0},
};

const wl_interface wp_linux_drm_syncobj_surface_v1_interface = {
    .name = "wp_linux_drm_syncobj_surface_v1", .version = 1,
    .method_count = 3, .methods = _CWpLinuxDrmSyncobjSurfaceV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpLinuxDrmSyncobjSurfaceV1::CWpLinuxDrmSyncobjSurfaceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_linux_drm_syncobj_surface_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpLinuxDrmSyncobjSurfaceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpLinuxDrmSyncobjSurfaceV1VTable, this, nullptr);
}

CWpLinuxDrmSyncobjSurfaceV1::~CWpLinuxDrmSyncobjSurfaceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpLinuxDrmSyncobjSurfaceV1::onDestroyCalled() {
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

void CWpLinuxDrmSyncobjSurfaceV1::setDestroy(F<void(CWpLinuxDrmSyncobjSurfaceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpLinuxDrmSyncobjSurfaceV1::setSetAcquirePoint(F<void(CWpLinuxDrmSyncobjSurfaceV1*, wl_resource*, uint32_t, uint32_t)> &&handler) {
    requests.setAcquirePoint = std::move(handler);
}

void CWpLinuxDrmSyncobjSurfaceV1::setSetReleasePoint(F<void(CWpLinuxDrmSyncobjSurfaceV1*, wl_resource*, uint32_t, uint32_t)> &&handler) {
    requests.setReleasePoint = std::move(handler);
}

#undef F

// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// fifo_v1

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
#include "fifo-v1.hpp"
#undef private
#define F std::function

static const wl_interface* fifoV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wp_fifo_manager_v1_interface;
extern const wl_interface wp_fifo_v1_interface;
extern const wl_interface wl_surface_interface;

static void _CWpFifoManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpFifoManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpFifoManagerV1GetFifo(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CWpFifoManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getFifo)
        PO->requests.getFifo(PO, id, surface);
}

static void _CWpFifoManagerV1__DestroyListener(wl_listener* l, void* d) {
    CWpFifoManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpFifoManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpFifoManagerV1VTable[] = {
    (void*)_CWpFifoManagerV1Destroy,
    (void*)_CWpFifoManagerV1GetFifo,
};
static const wl_interface* _CWpFifoManagerV1GetFifoTypes[] = {
    &wp_fifo_v1_interface,
    &wl_surface_interface,
};

static const wl_message _CWpFifoManagerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = fifoV1_dummyTypes + 0},
    { .name = "get_fifo", .signature = "no", .types = _CWpFifoManagerV1GetFifoTypes + 0},
};

const wl_interface wp_fifo_manager_v1_interface = {
    .name = "wp_fifo_manager_v1", .version = 1,
    .method_count = 2, .methods = _CWpFifoManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpFifoManagerV1::CWpFifoManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_fifo_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpFifoManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpFifoManagerV1VTable, this, nullptr);
}

CWpFifoManagerV1::~CWpFifoManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpFifoManagerV1::onDestroyCalled() {
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

void CWpFifoManagerV1::setDestroy(F<void(CWpFifoManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpFifoManagerV1::setGetFifo(F<void(CWpFifoManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getFifo = std::move(handler);
}

static void _CWpFifoV1SetBarrier(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpFifoV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setBarrier)
        PO->requests.setBarrier(PO);
}

static void _CWpFifoV1WaitBarrier(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpFifoV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.waitBarrier)
        PO->requests.waitBarrier(PO);
}

static void _CWpFifoV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpFifoV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpFifoV1__DestroyListener(wl_listener* l, void* d) {
    CWpFifoV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpFifoV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpFifoV1VTable[] = {
    (void*)_CWpFifoV1SetBarrier,
    (void*)_CWpFifoV1WaitBarrier,
    (void*)_CWpFifoV1Destroy,
};

static const wl_message _CWpFifoV1Requests[] = {
    { .name = "set_barrier", .signature = "", .types = fifoV1_dummyTypes + 0},
    { .name = "wait_barrier", .signature = "", .types = fifoV1_dummyTypes + 0},
    { .name = "destroy", .signature = "", .types = fifoV1_dummyTypes + 0},
};

const wl_interface wp_fifo_v1_interface = {
    .name = "wp_fifo_v1", .version = 1,
    .method_count = 3, .methods = _CWpFifoV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpFifoV1::CWpFifoV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_fifo_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpFifoV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpFifoV1VTable, this, nullptr);
}

CWpFifoV1::~CWpFifoV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpFifoV1::onDestroyCalled() {
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

void CWpFifoV1::setSetBarrier(F<void(CWpFifoV1*)> &&handler) {
    requests.setBarrier = std::move(handler);
}

void CWpFifoV1::setWaitBarrier(F<void(CWpFifoV1*)> &&handler) {
    requests.waitBarrier = std::move(handler);
}

void CWpFifoV1::setDestroy(F<void(CWpFifoV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

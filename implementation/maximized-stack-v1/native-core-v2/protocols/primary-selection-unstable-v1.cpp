// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// wp_primary_selection_unstable_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2015, 2016 Red Hat

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
#include "primary-selection-unstable-v1.hpp"
#undef private
#define F std::function

static const wl_interface* wpPrimarySelectionUnstableV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface zwp_primary_selection_device_manager_v1_interface;
extern const wl_interface zwp_primary_selection_device_v1_interface;
extern const wl_interface zwp_primary_selection_offer_v1_interface;
extern const wl_interface zwp_primary_selection_source_v1_interface;
extern const wl_interface wl_seat_interface;

static void _CZwpPrimarySelectionDeviceManagerV1CreateSource(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CZwpPrimarySelectionDeviceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createSource)
        PO->requests.createSource(PO, id);
}

static void _CZwpPrimarySelectionDeviceManagerV1GetDevice(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* seat) {
    const auto PO = (CZwpPrimarySelectionDeviceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getDevice)
        PO->requests.getDevice(PO, id, seat);
}

static void _CZwpPrimarySelectionDeviceManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpPrimarySelectionDeviceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpPrimarySelectionDeviceManagerV1__DestroyListener(wl_listener* l, void* d) {
    CZwpPrimarySelectionDeviceManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpPrimarySelectionDeviceManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpPrimarySelectionDeviceManagerV1VTable[] = {
    (void*)_CZwpPrimarySelectionDeviceManagerV1CreateSource,
    (void*)_CZwpPrimarySelectionDeviceManagerV1GetDevice,
    (void*)_CZwpPrimarySelectionDeviceManagerV1Destroy,
};
static const wl_interface* _CZwpPrimarySelectionDeviceManagerV1CreateSourceTypes[] = {
    &zwp_primary_selection_source_v1_interface,
};
static const wl_interface* _CZwpPrimarySelectionDeviceManagerV1GetDeviceTypes[] = {
    &zwp_primary_selection_device_v1_interface,
    &wl_seat_interface,
};

static const wl_message _CZwpPrimarySelectionDeviceManagerV1Requests[] = {
    { .name = "create_source", .signature = "n", .types = _CZwpPrimarySelectionDeviceManagerV1CreateSourceTypes + 0},
    { .name = "get_device", .signature = "no", .types = _CZwpPrimarySelectionDeviceManagerV1GetDeviceTypes + 0},
    { .name = "destroy", .signature = "", .types = wpPrimarySelectionUnstableV1_dummyTypes + 0},
};

const wl_interface zwp_primary_selection_device_manager_v1_interface = {
    .name = "zwp_primary_selection_device_manager_v1", .version = 1,
    .method_count = 3, .methods = _CZwpPrimarySelectionDeviceManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CZwpPrimarySelectionDeviceManagerV1::CZwpPrimarySelectionDeviceManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_primary_selection_device_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpPrimarySelectionDeviceManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpPrimarySelectionDeviceManagerV1VTable, this, nullptr);
}

CZwpPrimarySelectionDeviceManagerV1::~CZwpPrimarySelectionDeviceManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpPrimarySelectionDeviceManagerV1::onDestroyCalled() {
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

void CZwpPrimarySelectionDeviceManagerV1::setCreateSource(F<void(CZwpPrimarySelectionDeviceManagerV1*, uint32_t)> &&handler) {
    requests.createSource = std::move(handler);
}

void CZwpPrimarySelectionDeviceManagerV1::setGetDevice(F<void(CZwpPrimarySelectionDeviceManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getDevice = std::move(handler);
}

void CZwpPrimarySelectionDeviceManagerV1::setDestroy(F<void(CZwpPrimarySelectionDeviceManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZwpPrimarySelectionDeviceV1SetSelection(wl_client* client, wl_resource* resource, wl_resource* source, uint32_t serial) {
    const auto PO = (CZwpPrimarySelectionDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setSelection)
        PO->requests.setSelection(PO, source, serial);
}

static void _CZwpPrimarySelectionDeviceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpPrimarySelectionDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpPrimarySelectionDeviceV1__DestroyListener(wl_listener* l, void* d) {
    CZwpPrimarySelectionDeviceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpPrimarySelectionDeviceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpPrimarySelectionDeviceV1VTable[] = {
    (void*)_CZwpPrimarySelectionDeviceV1SetSelection,
    (void*)_CZwpPrimarySelectionDeviceV1Destroy,
};

void CZwpPrimarySelectionDeviceV1::sendDataOffer(CZwpPrimarySelectionOfferV1* offer) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, offer ? offer->pResource : nullptr);
}

void CZwpPrimarySelectionDeviceV1::sendSelection(CZwpPrimarySelectionOfferV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id ? id->pResource : nullptr);
}

void CZwpPrimarySelectionDeviceV1::sendDataOfferRaw(CZwpPrimarySelectionOfferV1* offer) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, offer);
}

void CZwpPrimarySelectionDeviceV1::sendSelectionRaw(wl_resource* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id);
}
static const wl_interface* _CZwpPrimarySelectionDeviceV1SetSelectionTypes[] = {
    &zwp_primary_selection_source_v1_interface,
    nullptr,
};
static const wl_interface* _CZwpPrimarySelectionDeviceV1DataOfferTypes[] = {
    &zwp_primary_selection_offer_v1_interface,
};
static const wl_interface* _CZwpPrimarySelectionDeviceV1SelectionTypes[] = {
    &zwp_primary_selection_offer_v1_interface,
};

static const wl_message _CZwpPrimarySelectionDeviceV1Requests[] = {
    { .name = "set_selection", .signature = "?ou", .types = _CZwpPrimarySelectionDeviceV1SetSelectionTypes + 0},
    { .name = "destroy", .signature = "", .types = wpPrimarySelectionUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwpPrimarySelectionDeviceV1Events[] = {
    { .name = "data_offer", .signature = "n", .types = _CZwpPrimarySelectionDeviceV1DataOfferTypes + 0},
    { .name = "selection", .signature = "?o", .types = _CZwpPrimarySelectionDeviceV1SelectionTypes + 0},
};

const wl_interface zwp_primary_selection_device_v1_interface = {
    .name = "zwp_primary_selection_device_v1", .version = 1,
    .method_count = 2, .methods = _CZwpPrimarySelectionDeviceV1Requests,
    .event_count = 2, .events = _CZwpPrimarySelectionDeviceV1Events,
};

CZwpPrimarySelectionDeviceV1::CZwpPrimarySelectionDeviceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_primary_selection_device_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpPrimarySelectionDeviceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpPrimarySelectionDeviceV1VTable, this, nullptr);
}

CZwpPrimarySelectionDeviceV1::~CZwpPrimarySelectionDeviceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpPrimarySelectionDeviceV1::onDestroyCalled() {
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

void CZwpPrimarySelectionDeviceV1::setSetSelection(F<void(CZwpPrimarySelectionDeviceV1*, wl_resource*, uint32_t)> &&handler) {
    requests.setSelection = std::move(handler);
}

void CZwpPrimarySelectionDeviceV1::setDestroy(F<void(CZwpPrimarySelectionDeviceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZwpPrimarySelectionOfferV1Receive(wl_client* client, wl_resource* resource, const char* mime_type, int32_t fd) {
    const auto PO = (CZwpPrimarySelectionOfferV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.receive)
        PO->requests.receive(PO, mime_type, fd);
}

static void _CZwpPrimarySelectionOfferV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpPrimarySelectionOfferV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpPrimarySelectionOfferV1__DestroyListener(wl_listener* l, void* d) {
    CZwpPrimarySelectionOfferV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpPrimarySelectionOfferV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpPrimarySelectionOfferV1VTable[] = {
    (void*)_CZwpPrimarySelectionOfferV1Receive,
    (void*)_CZwpPrimarySelectionOfferV1Destroy,
};

void CZwpPrimarySelectionOfferV1::sendOffer(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}

void CZwpPrimarySelectionOfferV1::sendOfferRaw(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}
static const wl_interface* _CZwpPrimarySelectionOfferV1ReceiveTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CZwpPrimarySelectionOfferV1OfferTypes[] = {
    nullptr,
};

static const wl_message _CZwpPrimarySelectionOfferV1Requests[] = {
    { .name = "receive", .signature = "sh", .types = _CZwpPrimarySelectionOfferV1ReceiveTypes + 0},
    { .name = "destroy", .signature = "", .types = wpPrimarySelectionUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwpPrimarySelectionOfferV1Events[] = {
    { .name = "offer", .signature = "s", .types = _CZwpPrimarySelectionOfferV1OfferTypes + 0},
};

const wl_interface zwp_primary_selection_offer_v1_interface = {
    .name = "zwp_primary_selection_offer_v1", .version = 1,
    .method_count = 2, .methods = _CZwpPrimarySelectionOfferV1Requests,
    .event_count = 1, .events = _CZwpPrimarySelectionOfferV1Events,
};

CZwpPrimarySelectionOfferV1::CZwpPrimarySelectionOfferV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_primary_selection_offer_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpPrimarySelectionOfferV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpPrimarySelectionOfferV1VTable, this, nullptr);
}

CZwpPrimarySelectionOfferV1::~CZwpPrimarySelectionOfferV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpPrimarySelectionOfferV1::onDestroyCalled() {
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

void CZwpPrimarySelectionOfferV1::setReceive(F<void(CZwpPrimarySelectionOfferV1*, const char*, int32_t)> &&handler) {
    requests.receive = std::move(handler);
}

void CZwpPrimarySelectionOfferV1::setDestroy(F<void(CZwpPrimarySelectionOfferV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZwpPrimarySelectionSourceV1Offer(wl_client* client, wl_resource* resource, const char* mime_type) {
    const auto PO = (CZwpPrimarySelectionSourceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.offer)
        PO->requests.offer(PO, mime_type);
}

static void _CZwpPrimarySelectionSourceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpPrimarySelectionSourceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpPrimarySelectionSourceV1__DestroyListener(wl_listener* l, void* d) {
    CZwpPrimarySelectionSourceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpPrimarySelectionSourceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpPrimarySelectionSourceV1VTable[] = {
    (void*)_CZwpPrimarySelectionSourceV1Offer,
    (void*)_CZwpPrimarySelectionSourceV1Destroy,
};

void CZwpPrimarySelectionSourceV1::sendSend(const char* mime_type, int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type, fd);
}

void CZwpPrimarySelectionSourceV1::sendCancelled() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CZwpPrimarySelectionSourceV1::sendSendRaw(const char* mime_type, int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type, fd);
}

void CZwpPrimarySelectionSourceV1::sendCancelledRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}
static const wl_interface* _CZwpPrimarySelectionSourceV1OfferTypes[] = {
    nullptr,
};
static const wl_interface* _CZwpPrimarySelectionSourceV1SendTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CZwpPrimarySelectionSourceV1Requests[] = {
    { .name = "offer", .signature = "s", .types = _CZwpPrimarySelectionSourceV1OfferTypes + 0},
    { .name = "destroy", .signature = "", .types = wpPrimarySelectionUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwpPrimarySelectionSourceV1Events[] = {
    { .name = "send", .signature = "sh", .types = _CZwpPrimarySelectionSourceV1SendTypes + 0},
    { .name = "cancelled", .signature = "", .types = wpPrimarySelectionUnstableV1_dummyTypes + 0},
};

const wl_interface zwp_primary_selection_source_v1_interface = {
    .name = "zwp_primary_selection_source_v1", .version = 1,
    .method_count = 2, .methods = _CZwpPrimarySelectionSourceV1Requests,
    .event_count = 2, .events = _CZwpPrimarySelectionSourceV1Events,
};

CZwpPrimarySelectionSourceV1::CZwpPrimarySelectionSourceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_primary_selection_source_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpPrimarySelectionSourceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpPrimarySelectionSourceV1VTable, this, nullptr);
}

CZwpPrimarySelectionSourceV1::~CZwpPrimarySelectionSourceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpPrimarySelectionSourceV1::onDestroyCalled() {
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

void CZwpPrimarySelectionSourceV1::setOffer(F<void(CZwpPrimarySelectionSourceV1*, const char*)> &&handler) {
    requests.offer = std::move(handler);
}

void CZwpPrimarySelectionSourceV1::setDestroy(F<void(CZwpPrimarySelectionSourceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

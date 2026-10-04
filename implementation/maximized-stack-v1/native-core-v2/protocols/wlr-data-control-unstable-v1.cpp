// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// wlr_data_control_unstable_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2018 Simon Ser
    Copyright © 2019 Ivan Molodetskikh

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
#include "wlr-data-control-unstable-v1.hpp"
#undef private
#define F std::function

static const wl_interface* wlrDataControlUnstableV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface zwlr_data_control_manager_v1_interface;
extern const wl_interface zwlr_data_control_device_v1_interface;
extern const wl_interface zwlr_data_control_source_v1_interface;
extern const wl_interface zwlr_data_control_offer_v1_interface;
extern const wl_interface wl_seat_interface;

static void _CZwlrDataControlManagerV1CreateDataSource(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CZwlrDataControlManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createDataSource)
        PO->requests.createDataSource(PO, id);
}

static void _CZwlrDataControlManagerV1GetDataDevice(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* seat) {
    const auto PO = (CZwlrDataControlManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getDataDevice)
        PO->requests.getDataDevice(PO, id, seat);
}

static void _CZwlrDataControlManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrDataControlManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwlrDataControlManagerV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrDataControlManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrDataControlManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrDataControlManagerV1VTable[] = {
    (void*)_CZwlrDataControlManagerV1CreateDataSource,
    (void*)_CZwlrDataControlManagerV1GetDataDevice,
    (void*)_CZwlrDataControlManagerV1Destroy,
};
static const wl_interface* _CZwlrDataControlManagerV1CreateDataSourceTypes[] = {
    &zwlr_data_control_source_v1_interface,
};
static const wl_interface* _CZwlrDataControlManagerV1GetDataDeviceTypes[] = {
    &zwlr_data_control_device_v1_interface,
    &wl_seat_interface,
};

static const wl_message _CZwlrDataControlManagerV1Requests[] = {
    { .name = "create_data_source", .signature = "n", .types = _CZwlrDataControlManagerV1CreateDataSourceTypes + 0},
    { .name = "get_data_device", .signature = "no", .types = _CZwlrDataControlManagerV1GetDataDeviceTypes + 0},
    { .name = "destroy", .signature = "", .types = wlrDataControlUnstableV1_dummyTypes + 0},
};

const wl_interface zwlr_data_control_manager_v1_interface = {
    .name = "zwlr_data_control_manager_v1", .version = 2,
    .method_count = 3, .methods = _CZwlrDataControlManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CZwlrDataControlManagerV1::CZwlrDataControlManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_data_control_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrDataControlManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrDataControlManagerV1VTable, this, nullptr);
}

CZwlrDataControlManagerV1::~CZwlrDataControlManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrDataControlManagerV1::onDestroyCalled() {
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

void CZwlrDataControlManagerV1::setCreateDataSource(F<void(CZwlrDataControlManagerV1*, uint32_t)> &&handler) {
    requests.createDataSource = std::move(handler);
}

void CZwlrDataControlManagerV1::setGetDataDevice(F<void(CZwlrDataControlManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getDataDevice = std::move(handler);
}

void CZwlrDataControlManagerV1::setDestroy(F<void(CZwlrDataControlManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZwlrDataControlDeviceV1SetSelection(wl_client* client, wl_resource* resource, wl_resource* source) {
    const auto PO = (CZwlrDataControlDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setSelection)
        PO->requests.setSelection(PO, source);
}

static void _CZwlrDataControlDeviceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrDataControlDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwlrDataControlDeviceV1SetPrimarySelection(wl_client* client, wl_resource* resource, wl_resource* source) {
    const auto PO = (CZwlrDataControlDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setPrimarySelection)
        PO->requests.setPrimarySelection(PO, source);
}

static void _CZwlrDataControlDeviceV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrDataControlDeviceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrDataControlDeviceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrDataControlDeviceV1VTable[] = {
    (void*)_CZwlrDataControlDeviceV1SetSelection,
    (void*)_CZwlrDataControlDeviceV1Destroy,
    (void*)_CZwlrDataControlDeviceV1SetPrimarySelection,
};

void CZwlrDataControlDeviceV1::sendDataOffer(CZwlrDataControlOfferV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, id ? id->pResource : nullptr);
}

void CZwlrDataControlDeviceV1::sendSelection(CZwlrDataControlOfferV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id ? id->pResource : nullptr);
}

void CZwlrDataControlDeviceV1::sendFinished() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CZwlrDataControlDeviceV1::sendPrimarySelection(CZwlrDataControlOfferV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, id ? id->pResource : nullptr);
}

void CZwlrDataControlDeviceV1::sendDataOfferRaw(CZwlrDataControlOfferV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, id);
}

void CZwlrDataControlDeviceV1::sendSelectionRaw(wl_resource* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id);
}

void CZwlrDataControlDeviceV1::sendFinishedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CZwlrDataControlDeviceV1::sendPrimarySelectionRaw(wl_resource* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, id);
}
static const wl_interface* _CZwlrDataControlDeviceV1SetSelectionTypes[] = {
    &zwlr_data_control_source_v1_interface,
};
static const wl_interface* _CZwlrDataControlDeviceV1SetPrimarySelectionTypes[] = {
    &zwlr_data_control_source_v1_interface,
};
static const wl_interface* _CZwlrDataControlDeviceV1DataOfferTypes[] = {
    &zwlr_data_control_offer_v1_interface,
};
static const wl_interface* _CZwlrDataControlDeviceV1SelectionTypes[] = {
    &zwlr_data_control_offer_v1_interface,
};
static const wl_interface* _CZwlrDataControlDeviceV1PrimarySelectionTypes[] = {
    &zwlr_data_control_offer_v1_interface,
};

static const wl_message _CZwlrDataControlDeviceV1Requests[] = {
    { .name = "set_selection", .signature = "?o", .types = _CZwlrDataControlDeviceV1SetSelectionTypes + 0},
    { .name = "destroy", .signature = "", .types = wlrDataControlUnstableV1_dummyTypes + 0},
    { .name = "set_primary_selection", .signature = "2?o", .types = _CZwlrDataControlDeviceV1SetPrimarySelectionTypes + 0},
};

static const wl_message _CZwlrDataControlDeviceV1Events[] = {
    { .name = "data_offer", .signature = "n", .types = _CZwlrDataControlDeviceV1DataOfferTypes + 0},
    { .name = "selection", .signature = "?o", .types = _CZwlrDataControlDeviceV1SelectionTypes + 0},
    { .name = "finished", .signature = "", .types = wlrDataControlUnstableV1_dummyTypes + 0},
    { .name = "primary_selection", .signature = "2?o", .types = _CZwlrDataControlDeviceV1PrimarySelectionTypes + 0},
};

const wl_interface zwlr_data_control_device_v1_interface = {
    .name = "zwlr_data_control_device_v1", .version = 2,
    .method_count = 3, .methods = _CZwlrDataControlDeviceV1Requests,
    .event_count = 4, .events = _CZwlrDataControlDeviceV1Events,
};

CZwlrDataControlDeviceV1::CZwlrDataControlDeviceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_data_control_device_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrDataControlDeviceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrDataControlDeviceV1VTable, this, nullptr);
}

CZwlrDataControlDeviceV1::~CZwlrDataControlDeviceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrDataControlDeviceV1::onDestroyCalled() {
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

void CZwlrDataControlDeviceV1::setSetSelection(F<void(CZwlrDataControlDeviceV1*, wl_resource*)> &&handler) {
    requests.setSelection = std::move(handler);
}

void CZwlrDataControlDeviceV1::setDestroy(F<void(CZwlrDataControlDeviceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZwlrDataControlDeviceV1::setSetPrimarySelection(F<void(CZwlrDataControlDeviceV1*, wl_resource*)> &&handler) {
    requests.setPrimarySelection = std::move(handler);
}

static void _CZwlrDataControlSourceV1Offer(wl_client* client, wl_resource* resource, const char* mime_type) {
    const auto PO = (CZwlrDataControlSourceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.offer)
        PO->requests.offer(PO, mime_type);
}

static void _CZwlrDataControlSourceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrDataControlSourceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwlrDataControlSourceV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrDataControlSourceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrDataControlSourceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrDataControlSourceV1VTable[] = {
    (void*)_CZwlrDataControlSourceV1Offer,
    (void*)_CZwlrDataControlSourceV1Destroy,
};

void CZwlrDataControlSourceV1::sendSend(const char* mime_type, int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type, fd);
}

void CZwlrDataControlSourceV1::sendCancelled() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CZwlrDataControlSourceV1::sendSendRaw(const char* mime_type, int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type, fd);
}

void CZwlrDataControlSourceV1::sendCancelledRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}
static const wl_interface* _CZwlrDataControlSourceV1OfferTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrDataControlSourceV1SendTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CZwlrDataControlSourceV1Requests[] = {
    { .name = "offer", .signature = "s", .types = _CZwlrDataControlSourceV1OfferTypes + 0},
    { .name = "destroy", .signature = "", .types = wlrDataControlUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwlrDataControlSourceV1Events[] = {
    { .name = "send", .signature = "sh", .types = _CZwlrDataControlSourceV1SendTypes + 0},
    { .name = "cancelled", .signature = "", .types = wlrDataControlUnstableV1_dummyTypes + 0},
};

const wl_interface zwlr_data_control_source_v1_interface = {
    .name = "zwlr_data_control_source_v1", .version = 1,
    .method_count = 2, .methods = _CZwlrDataControlSourceV1Requests,
    .event_count = 2, .events = _CZwlrDataControlSourceV1Events,
};

CZwlrDataControlSourceV1::CZwlrDataControlSourceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_data_control_source_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrDataControlSourceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrDataControlSourceV1VTable, this, nullptr);
}

CZwlrDataControlSourceV1::~CZwlrDataControlSourceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrDataControlSourceV1::onDestroyCalled() {
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

void CZwlrDataControlSourceV1::setOffer(F<void(CZwlrDataControlSourceV1*, const char*)> &&handler) {
    requests.offer = std::move(handler);
}

void CZwlrDataControlSourceV1::setDestroy(F<void(CZwlrDataControlSourceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZwlrDataControlOfferV1Receive(wl_client* client, wl_resource* resource, const char* mime_type, int32_t fd) {
    const auto PO = (CZwlrDataControlOfferV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.receive)
        PO->requests.receive(PO, mime_type, fd);
}

static void _CZwlrDataControlOfferV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrDataControlOfferV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwlrDataControlOfferV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrDataControlOfferV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrDataControlOfferV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrDataControlOfferV1VTable[] = {
    (void*)_CZwlrDataControlOfferV1Receive,
    (void*)_CZwlrDataControlOfferV1Destroy,
};

void CZwlrDataControlOfferV1::sendOffer(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}

void CZwlrDataControlOfferV1::sendOfferRaw(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}
static const wl_interface* _CZwlrDataControlOfferV1ReceiveTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CZwlrDataControlOfferV1OfferTypes[] = {
    nullptr,
};

static const wl_message _CZwlrDataControlOfferV1Requests[] = {
    { .name = "receive", .signature = "sh", .types = _CZwlrDataControlOfferV1ReceiveTypes + 0},
    { .name = "destroy", .signature = "", .types = wlrDataControlUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwlrDataControlOfferV1Events[] = {
    { .name = "offer", .signature = "s", .types = _CZwlrDataControlOfferV1OfferTypes + 0},
};

const wl_interface zwlr_data_control_offer_v1_interface = {
    .name = "zwlr_data_control_offer_v1", .version = 1,
    .method_count = 2, .methods = _CZwlrDataControlOfferV1Requests,
    .event_count = 1, .events = _CZwlrDataControlOfferV1Events,
};

CZwlrDataControlOfferV1::CZwlrDataControlOfferV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_data_control_offer_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrDataControlOfferV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrDataControlOfferV1VTable, this, nullptr);
}

CZwlrDataControlOfferV1::~CZwlrDataControlOfferV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrDataControlOfferV1::onDestroyCalled() {
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

void CZwlrDataControlOfferV1::setReceive(F<void(CZwlrDataControlOfferV1*, const char*, int32_t)> &&handler) {
    requests.receive = std::move(handler);
}

void CZwlrDataControlOfferV1::setDestroy(F<void(CZwlrDataControlOfferV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

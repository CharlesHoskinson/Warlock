// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// ext_data_control_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2018 Simon Ser
    Copyright © 2019 Ivan Molodetskikh
    Copyright © 2024 Neal Gompa

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
#include "ext-data-control-v1.hpp"
#undef private
#define F std::function

static const wl_interface* extDataControlV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface ext_data_control_manager_v1_interface;
extern const wl_interface ext_data_control_device_v1_interface;
extern const wl_interface ext_data_control_source_v1_interface;
extern const wl_interface ext_data_control_offer_v1_interface;
extern const wl_interface wl_seat_interface;

static void _CExtDataControlManagerV1CreateDataSource(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CExtDataControlManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createDataSource)
        PO->requests.createDataSource(PO, id);
}

static void _CExtDataControlManagerV1GetDataDevice(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* seat) {
    const auto PO = (CExtDataControlManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getDataDevice)
        PO->requests.getDataDevice(PO, id, seat);
}

static void _CExtDataControlManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtDataControlManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtDataControlManagerV1__DestroyListener(wl_listener* l, void* d) {
    CExtDataControlManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtDataControlManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtDataControlManagerV1VTable[] = {
    (void*)_CExtDataControlManagerV1CreateDataSource,
    (void*)_CExtDataControlManagerV1GetDataDevice,
    (void*)_CExtDataControlManagerV1Destroy,
};
static const wl_interface* _CExtDataControlManagerV1CreateDataSourceTypes[] = {
    &ext_data_control_source_v1_interface,
};
static const wl_interface* _CExtDataControlManagerV1GetDataDeviceTypes[] = {
    &ext_data_control_device_v1_interface,
    &wl_seat_interface,
};

static const wl_message _CExtDataControlManagerV1Requests[] = {
    { .name = "create_data_source", .signature = "n", .types = _CExtDataControlManagerV1CreateDataSourceTypes + 0},
    { .name = "get_data_device", .signature = "no", .types = _CExtDataControlManagerV1GetDataDeviceTypes + 0},
    { .name = "destroy", .signature = "", .types = extDataControlV1_dummyTypes + 0},
};

const wl_interface ext_data_control_manager_v1_interface = {
    .name = "ext_data_control_manager_v1", .version = 1,
    .method_count = 3, .methods = _CExtDataControlManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CExtDataControlManagerV1::CExtDataControlManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_data_control_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtDataControlManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtDataControlManagerV1VTable, this, nullptr);
}

CExtDataControlManagerV1::~CExtDataControlManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtDataControlManagerV1::onDestroyCalled() {
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

void CExtDataControlManagerV1::setCreateDataSource(F<void(CExtDataControlManagerV1*, uint32_t)> &&handler) {
    requests.createDataSource = std::move(handler);
}

void CExtDataControlManagerV1::setGetDataDevice(F<void(CExtDataControlManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getDataDevice = std::move(handler);
}

void CExtDataControlManagerV1::setDestroy(F<void(CExtDataControlManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CExtDataControlDeviceV1SetSelection(wl_client* client, wl_resource* resource, wl_resource* source) {
    const auto PO = (CExtDataControlDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setSelection)
        PO->requests.setSelection(PO, source);
}

static void _CExtDataControlDeviceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtDataControlDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtDataControlDeviceV1SetPrimarySelection(wl_client* client, wl_resource* resource, wl_resource* source) {
    const auto PO = (CExtDataControlDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setPrimarySelection)
        PO->requests.setPrimarySelection(PO, source);
}

static void _CExtDataControlDeviceV1__DestroyListener(wl_listener* l, void* d) {
    CExtDataControlDeviceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtDataControlDeviceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtDataControlDeviceV1VTable[] = {
    (void*)_CExtDataControlDeviceV1SetSelection,
    (void*)_CExtDataControlDeviceV1Destroy,
    (void*)_CExtDataControlDeviceV1SetPrimarySelection,
};

void CExtDataControlDeviceV1::sendDataOffer(CExtDataControlOfferV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, id ? id->pResource : nullptr);
}

void CExtDataControlDeviceV1::sendSelection(CExtDataControlOfferV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id ? id->pResource : nullptr);
}

void CExtDataControlDeviceV1::sendFinished() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CExtDataControlDeviceV1::sendPrimarySelection(CExtDataControlOfferV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, id ? id->pResource : nullptr);
}

void CExtDataControlDeviceV1::sendDataOfferRaw(CExtDataControlOfferV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, id);
}

void CExtDataControlDeviceV1::sendSelectionRaw(wl_resource* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id);
}

void CExtDataControlDeviceV1::sendFinishedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CExtDataControlDeviceV1::sendPrimarySelectionRaw(wl_resource* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, id);
}
static const wl_interface* _CExtDataControlDeviceV1SetSelectionTypes[] = {
    &ext_data_control_source_v1_interface,
};
static const wl_interface* _CExtDataControlDeviceV1SetPrimarySelectionTypes[] = {
    &ext_data_control_source_v1_interface,
};
static const wl_interface* _CExtDataControlDeviceV1DataOfferTypes[] = {
    &ext_data_control_offer_v1_interface,
};
static const wl_interface* _CExtDataControlDeviceV1SelectionTypes[] = {
    &ext_data_control_offer_v1_interface,
};
static const wl_interface* _CExtDataControlDeviceV1PrimarySelectionTypes[] = {
    &ext_data_control_offer_v1_interface,
};

static const wl_message _CExtDataControlDeviceV1Requests[] = {
    { .name = "set_selection", .signature = "?o", .types = _CExtDataControlDeviceV1SetSelectionTypes + 0},
    { .name = "destroy", .signature = "", .types = extDataControlV1_dummyTypes + 0},
    { .name = "set_primary_selection", .signature = "?o", .types = _CExtDataControlDeviceV1SetPrimarySelectionTypes + 0},
};

static const wl_message _CExtDataControlDeviceV1Events[] = {
    { .name = "data_offer", .signature = "n", .types = _CExtDataControlDeviceV1DataOfferTypes + 0},
    { .name = "selection", .signature = "?o", .types = _CExtDataControlDeviceV1SelectionTypes + 0},
    { .name = "finished", .signature = "", .types = extDataControlV1_dummyTypes + 0},
    { .name = "primary_selection", .signature = "?o", .types = _CExtDataControlDeviceV1PrimarySelectionTypes + 0},
};

const wl_interface ext_data_control_device_v1_interface = {
    .name = "ext_data_control_device_v1", .version = 1,
    .method_count = 3, .methods = _CExtDataControlDeviceV1Requests,
    .event_count = 4, .events = _CExtDataControlDeviceV1Events,
};

CExtDataControlDeviceV1::CExtDataControlDeviceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_data_control_device_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtDataControlDeviceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtDataControlDeviceV1VTable, this, nullptr);
}

CExtDataControlDeviceV1::~CExtDataControlDeviceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtDataControlDeviceV1::onDestroyCalled() {
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

void CExtDataControlDeviceV1::setSetSelection(F<void(CExtDataControlDeviceV1*, wl_resource*)> &&handler) {
    requests.setSelection = std::move(handler);
}

void CExtDataControlDeviceV1::setDestroy(F<void(CExtDataControlDeviceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CExtDataControlDeviceV1::setSetPrimarySelection(F<void(CExtDataControlDeviceV1*, wl_resource*)> &&handler) {
    requests.setPrimarySelection = std::move(handler);
}

static void _CExtDataControlSourceV1Offer(wl_client* client, wl_resource* resource, const char* mime_type) {
    const auto PO = (CExtDataControlSourceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.offer)
        PO->requests.offer(PO, mime_type);
}

static void _CExtDataControlSourceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtDataControlSourceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtDataControlSourceV1__DestroyListener(wl_listener* l, void* d) {
    CExtDataControlSourceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtDataControlSourceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtDataControlSourceV1VTable[] = {
    (void*)_CExtDataControlSourceV1Offer,
    (void*)_CExtDataControlSourceV1Destroy,
};

void CExtDataControlSourceV1::sendSend(const char* mime_type, int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type, fd);
}

void CExtDataControlSourceV1::sendCancelled() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CExtDataControlSourceV1::sendSendRaw(const char* mime_type, int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type, fd);
}

void CExtDataControlSourceV1::sendCancelledRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}
static const wl_interface* _CExtDataControlSourceV1OfferTypes[] = {
    nullptr,
};
static const wl_interface* _CExtDataControlSourceV1SendTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CExtDataControlSourceV1Requests[] = {
    { .name = "offer", .signature = "s", .types = _CExtDataControlSourceV1OfferTypes + 0},
    { .name = "destroy", .signature = "", .types = extDataControlV1_dummyTypes + 0},
};

static const wl_message _CExtDataControlSourceV1Events[] = {
    { .name = "send", .signature = "sh", .types = _CExtDataControlSourceV1SendTypes + 0},
    { .name = "cancelled", .signature = "", .types = extDataControlV1_dummyTypes + 0},
};

const wl_interface ext_data_control_source_v1_interface = {
    .name = "ext_data_control_source_v1", .version = 1,
    .method_count = 2, .methods = _CExtDataControlSourceV1Requests,
    .event_count = 2, .events = _CExtDataControlSourceV1Events,
};

CExtDataControlSourceV1::CExtDataControlSourceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_data_control_source_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtDataControlSourceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtDataControlSourceV1VTable, this, nullptr);
}

CExtDataControlSourceV1::~CExtDataControlSourceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtDataControlSourceV1::onDestroyCalled() {
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

void CExtDataControlSourceV1::setOffer(F<void(CExtDataControlSourceV1*, const char*)> &&handler) {
    requests.offer = std::move(handler);
}

void CExtDataControlSourceV1::setDestroy(F<void(CExtDataControlSourceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CExtDataControlOfferV1Receive(wl_client* client, wl_resource* resource, const char* mime_type, int32_t fd) {
    const auto PO = (CExtDataControlOfferV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.receive)
        PO->requests.receive(PO, mime_type, fd);
}

static void _CExtDataControlOfferV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtDataControlOfferV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtDataControlOfferV1__DestroyListener(wl_listener* l, void* d) {
    CExtDataControlOfferV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtDataControlOfferV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtDataControlOfferV1VTable[] = {
    (void*)_CExtDataControlOfferV1Receive,
    (void*)_CExtDataControlOfferV1Destroy,
};

void CExtDataControlOfferV1::sendOffer(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}

void CExtDataControlOfferV1::sendOfferRaw(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}
static const wl_interface* _CExtDataControlOfferV1ReceiveTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CExtDataControlOfferV1OfferTypes[] = {
    nullptr,
};

static const wl_message _CExtDataControlOfferV1Requests[] = {
    { .name = "receive", .signature = "sh", .types = _CExtDataControlOfferV1ReceiveTypes + 0},
    { .name = "destroy", .signature = "", .types = extDataControlV1_dummyTypes + 0},
};

static const wl_message _CExtDataControlOfferV1Events[] = {
    { .name = "offer", .signature = "s", .types = _CExtDataControlOfferV1OfferTypes + 0},
};

const wl_interface ext_data_control_offer_v1_interface = {
    .name = "ext_data_control_offer_v1", .version = 1,
    .method_count = 2, .methods = _CExtDataControlOfferV1Requests,
    .event_count = 1, .events = _CExtDataControlOfferV1Events,
};

CExtDataControlOfferV1::CExtDataControlOfferV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_data_control_offer_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtDataControlOfferV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtDataControlOfferV1VTable, this, nullptr);
}

CExtDataControlOfferV1::~CExtDataControlOfferV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtDataControlOfferV1::onDestroyCalled() {
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

void CExtDataControlOfferV1::setReceive(F<void(CExtDataControlOfferV1*, const char*, int32_t)> &&handler) {
    requests.receive = std::move(handler);
}

void CExtDataControlOfferV1::setDestroy(F<void(CExtDataControlOfferV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

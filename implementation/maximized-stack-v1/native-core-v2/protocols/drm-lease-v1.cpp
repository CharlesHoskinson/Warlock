// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// drm_lease_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2018 NXP
    Copyright © 2019 Status Research & Development GmbH.
    Copyright © 2021 Xaver Hugl

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
#include "drm-lease-v1.hpp"
#undef private
#define F std::function

static const wl_interface* drmLeaseV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wp_drm_lease_device_v1_interface;
extern const wl_interface wp_drm_lease_connector_v1_interface;
extern const wl_interface wp_drm_lease_request_v1_interface;
extern const wl_interface wp_drm_lease_v1_interface;

static void _CWpDrmLeaseDeviceV1CreateLeaseRequest(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CWpDrmLeaseDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createLeaseRequest)
        PO->requests.createLeaseRequest(PO, id);
}

static void _CWpDrmLeaseDeviceV1Release(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpDrmLeaseDeviceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWpDrmLeaseDeviceV1__DestroyListener(wl_listener* l, void* d) {
    CWpDrmLeaseDeviceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpDrmLeaseDeviceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpDrmLeaseDeviceV1VTable[] = {
    (void*)_CWpDrmLeaseDeviceV1CreateLeaseRequest,
    (void*)_CWpDrmLeaseDeviceV1Release,
};

void CWpDrmLeaseDeviceV1::sendDrmFd(int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, fd);
}

void CWpDrmLeaseDeviceV1::sendConnector(CWpDrmLeaseConnectorV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id ? id->pResource : nullptr);
}

void CWpDrmLeaseDeviceV1::sendDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CWpDrmLeaseDeviceV1::sendReleased() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CWpDrmLeaseDeviceV1::sendDrmFdRaw(int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, fd);
}

void CWpDrmLeaseDeviceV1::sendConnectorRaw(CWpDrmLeaseConnectorV1* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id);
}

void CWpDrmLeaseDeviceV1::sendDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CWpDrmLeaseDeviceV1::sendReleasedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}
static const wl_interface* _CWpDrmLeaseDeviceV1CreateLeaseRequestTypes[] = {
    &wp_drm_lease_request_v1_interface,
};
static const wl_interface* _CWpDrmLeaseDeviceV1DrmFdTypes[] = {
    nullptr,
};
static const wl_interface* _CWpDrmLeaseDeviceV1ConnectorTypes[] = {
    &wp_drm_lease_connector_v1_interface,
};

static const wl_message _CWpDrmLeaseDeviceV1Requests[] = {
    { .name = "create_lease_request", .signature = "n", .types = _CWpDrmLeaseDeviceV1CreateLeaseRequestTypes + 0},
    { .name = "release", .signature = "", .types = drmLeaseV1_dummyTypes + 0},
};

static const wl_message _CWpDrmLeaseDeviceV1Events[] = {
    { .name = "drm_fd", .signature = "h", .types = _CWpDrmLeaseDeviceV1DrmFdTypes + 0},
    { .name = "connector", .signature = "n", .types = _CWpDrmLeaseDeviceV1ConnectorTypes + 0},
    { .name = "done", .signature = "", .types = drmLeaseV1_dummyTypes + 0},
    { .name = "released", .signature = "", .types = drmLeaseV1_dummyTypes + 0},
};

const wl_interface wp_drm_lease_device_v1_interface = {
    .name = "wp_drm_lease_device_v1", .version = 1,
    .method_count = 2, .methods = _CWpDrmLeaseDeviceV1Requests,
    .event_count = 4, .events = _CWpDrmLeaseDeviceV1Events,
};

CWpDrmLeaseDeviceV1::CWpDrmLeaseDeviceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_drm_lease_device_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpDrmLeaseDeviceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpDrmLeaseDeviceV1VTable, this, nullptr);
}

CWpDrmLeaseDeviceV1::~CWpDrmLeaseDeviceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpDrmLeaseDeviceV1::onDestroyCalled() {
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

void CWpDrmLeaseDeviceV1::setCreateLeaseRequest(F<void(CWpDrmLeaseDeviceV1*, uint32_t)> &&handler) {
    requests.createLeaseRequest = std::move(handler);
}

void CWpDrmLeaseDeviceV1::setRelease(F<void(CWpDrmLeaseDeviceV1*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWpDrmLeaseConnectorV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpDrmLeaseConnectorV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpDrmLeaseConnectorV1__DestroyListener(wl_listener* l, void* d) {
    CWpDrmLeaseConnectorV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpDrmLeaseConnectorV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpDrmLeaseConnectorV1VTable[] = {
    (void*)_CWpDrmLeaseConnectorV1Destroy,
};

void CWpDrmLeaseConnectorV1::sendName(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, name);
}

void CWpDrmLeaseConnectorV1::sendDescription(const char* description) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, description);
}

void CWpDrmLeaseConnectorV1::sendConnectorId(uint32_t connector_id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, connector_id);
}

void CWpDrmLeaseConnectorV1::sendDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CWpDrmLeaseConnectorV1::sendWithdrawn() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CWpDrmLeaseConnectorV1::sendNameRaw(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, name);
}

void CWpDrmLeaseConnectorV1::sendDescriptionRaw(const char* description) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, description);
}

void CWpDrmLeaseConnectorV1::sendConnectorIdRaw(uint32_t connector_id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, connector_id);
}

void CWpDrmLeaseConnectorV1::sendDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CWpDrmLeaseConnectorV1::sendWithdrawnRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}
static const wl_interface* _CWpDrmLeaseConnectorV1NameTypes[] = {
    nullptr,
};
static const wl_interface* _CWpDrmLeaseConnectorV1DescriptionTypes[] = {
    nullptr,
};
static const wl_interface* _CWpDrmLeaseConnectorV1ConnectorIdTypes[] = {
    nullptr,
};

static const wl_message _CWpDrmLeaseConnectorV1Requests[] = {
    { .name = "destroy", .signature = "", .types = drmLeaseV1_dummyTypes + 0},
};

static const wl_message _CWpDrmLeaseConnectorV1Events[] = {
    { .name = "name", .signature = "s", .types = _CWpDrmLeaseConnectorV1NameTypes + 0},
    { .name = "description", .signature = "s", .types = _CWpDrmLeaseConnectorV1DescriptionTypes + 0},
    { .name = "connector_id", .signature = "u", .types = _CWpDrmLeaseConnectorV1ConnectorIdTypes + 0},
    { .name = "done", .signature = "", .types = drmLeaseV1_dummyTypes + 0},
    { .name = "withdrawn", .signature = "", .types = drmLeaseV1_dummyTypes + 0},
};

const wl_interface wp_drm_lease_connector_v1_interface = {
    .name = "wp_drm_lease_connector_v1", .version = 1,
    .method_count = 1, .methods = _CWpDrmLeaseConnectorV1Requests,
    .event_count = 5, .events = _CWpDrmLeaseConnectorV1Events,
};

CWpDrmLeaseConnectorV1::CWpDrmLeaseConnectorV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_drm_lease_connector_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpDrmLeaseConnectorV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpDrmLeaseConnectorV1VTable, this, nullptr);
}

CWpDrmLeaseConnectorV1::~CWpDrmLeaseConnectorV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpDrmLeaseConnectorV1::onDestroyCalled() {
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

void CWpDrmLeaseConnectorV1::setDestroy(F<void(CWpDrmLeaseConnectorV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CWpDrmLeaseRequestV1RequestConnector(wl_client* client, wl_resource* resource, wl_resource* connector) {
    const auto PO = (CWpDrmLeaseRequestV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.requestConnector)
        PO->requests.requestConnector(PO, connector);
}

static void _CWpDrmLeaseRequestV1Submit(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CWpDrmLeaseRequestV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.submit)
        PO->requests.submit(PO, id);
}

static void _CWpDrmLeaseRequestV1__DestroyListener(wl_listener* l, void* d) {
    CWpDrmLeaseRequestV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpDrmLeaseRequestV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpDrmLeaseRequestV1VTable[] = {
    (void*)_CWpDrmLeaseRequestV1RequestConnector,
    (void*)_CWpDrmLeaseRequestV1Submit,
};
static const wl_interface* _CWpDrmLeaseRequestV1RequestConnectorTypes[] = {
    &wp_drm_lease_connector_v1_interface,
};
static const wl_interface* _CWpDrmLeaseRequestV1SubmitTypes[] = {
    &wp_drm_lease_v1_interface,
};

static const wl_message _CWpDrmLeaseRequestV1Requests[] = {
    { .name = "request_connector", .signature = "o", .types = _CWpDrmLeaseRequestV1RequestConnectorTypes + 0},
    { .name = "submit", .signature = "n", .types = _CWpDrmLeaseRequestV1SubmitTypes + 0},
};

const wl_interface wp_drm_lease_request_v1_interface = {
    .name = "wp_drm_lease_request_v1", .version = 1,
    .method_count = 2, .methods = _CWpDrmLeaseRequestV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpDrmLeaseRequestV1::CWpDrmLeaseRequestV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_drm_lease_request_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpDrmLeaseRequestV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpDrmLeaseRequestV1VTable, this, nullptr);
}

CWpDrmLeaseRequestV1::~CWpDrmLeaseRequestV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpDrmLeaseRequestV1::onDestroyCalled() {
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

void CWpDrmLeaseRequestV1::setRequestConnector(F<void(CWpDrmLeaseRequestV1*, wl_resource*)> &&handler) {
    requests.requestConnector = std::move(handler);
}

void CWpDrmLeaseRequestV1::setSubmit(F<void(CWpDrmLeaseRequestV1*, uint32_t)> &&handler) {
    requests.submit = std::move(handler);
}

static void _CWpDrmLeaseV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpDrmLeaseV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpDrmLeaseV1__DestroyListener(wl_listener* l, void* d) {
    CWpDrmLeaseV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpDrmLeaseV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpDrmLeaseV1VTable[] = {
    (void*)_CWpDrmLeaseV1Destroy,
};

void CWpDrmLeaseV1::sendLeaseFd(int32_t leased_fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, leased_fd);
}

void CWpDrmLeaseV1::sendFinished() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CWpDrmLeaseV1::sendLeaseFdRaw(int32_t leased_fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, leased_fd);
}

void CWpDrmLeaseV1::sendFinishedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}
static const wl_interface* _CWpDrmLeaseV1LeaseFdTypes[] = {
    nullptr,
};

static const wl_message _CWpDrmLeaseV1Requests[] = {
    { .name = "destroy", .signature = "", .types = drmLeaseV1_dummyTypes + 0},
};

static const wl_message _CWpDrmLeaseV1Events[] = {
    { .name = "lease_fd", .signature = "h", .types = _CWpDrmLeaseV1LeaseFdTypes + 0},
    { .name = "finished", .signature = "", .types = drmLeaseV1_dummyTypes + 0},
};

const wl_interface wp_drm_lease_v1_interface = {
    .name = "wp_drm_lease_v1", .version = 1,
    .method_count = 1, .methods = _CWpDrmLeaseV1Requests,
    .event_count = 2, .events = _CWpDrmLeaseV1Events,
};

CWpDrmLeaseV1::CWpDrmLeaseV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_drm_lease_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpDrmLeaseV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpDrmLeaseV1VTable, this, nullptr);
}

CWpDrmLeaseV1::~CWpDrmLeaseV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpDrmLeaseV1::onDestroyCalled() {
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

void CWpDrmLeaseV1::setDestroy(F<void(CWpDrmLeaseV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

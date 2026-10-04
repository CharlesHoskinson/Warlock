// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// linux_dmabuf_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2014, 2015 Collabora, Ltd.

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
#include "linux-dmabuf-v1.hpp"
#undef private
#define F std::function

static const wl_interface* linuxDmabufV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface zwp_linux_dmabuf_v1_interface;
extern const wl_interface zwp_linux_buffer_params_v1_interface;
extern const wl_interface zwp_linux_dmabuf_feedback_v1_interface;
extern const wl_interface wl_surface_interface;
extern const wl_interface wl_buffer_interface;

static void _CZwpLinuxDmabufV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpLinuxDmabufV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpLinuxDmabufV1CreateParams(wl_client* client, wl_resource* resource, uint32_t params_id) {
    const auto PO = (CZwpLinuxDmabufV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createParams)
        PO->requests.createParams(PO, params_id);
}

static void _CZwpLinuxDmabufV1GetDefaultFeedback(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CZwpLinuxDmabufV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getDefaultFeedback)
        PO->requests.getDefaultFeedback(PO, id);
}

static void _CZwpLinuxDmabufV1GetSurfaceFeedback(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CZwpLinuxDmabufV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getSurfaceFeedback)
        PO->requests.getSurfaceFeedback(PO, id, surface);
}

static void _CZwpLinuxDmabufV1__DestroyListener(wl_listener* l, void* d) {
    CZwpLinuxDmabufV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpLinuxDmabufV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpLinuxDmabufV1VTable[] = {
    (void*)_CZwpLinuxDmabufV1Destroy,
    (void*)_CZwpLinuxDmabufV1CreateParams,
    (void*)_CZwpLinuxDmabufV1GetDefaultFeedback,
    (void*)_CZwpLinuxDmabufV1GetSurfaceFeedback,
};

void CZwpLinuxDmabufV1::sendFormat(uint32_t format) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format);
}

void CZwpLinuxDmabufV1::sendModifier(uint32_t format, uint32_t modifier_hi, uint32_t modifier_lo) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, format, modifier_hi, modifier_lo);
}

void CZwpLinuxDmabufV1::sendFormatRaw(uint32_t format) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format);
}

void CZwpLinuxDmabufV1::sendModifierRaw(uint32_t format, uint32_t modifier_hi, uint32_t modifier_lo) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, format, modifier_hi, modifier_lo);
}
static const wl_interface* _CZwpLinuxDmabufV1CreateParamsTypes[] = {
    &zwp_linux_buffer_params_v1_interface,
};
static const wl_interface* _CZwpLinuxDmabufV1GetDefaultFeedbackTypes[] = {
    &zwp_linux_dmabuf_feedback_v1_interface,
};
static const wl_interface* _CZwpLinuxDmabufV1GetSurfaceFeedbackTypes[] = {
    &zwp_linux_dmabuf_feedback_v1_interface,
    &wl_surface_interface,
};
static const wl_interface* _CZwpLinuxDmabufV1FormatTypes[] = {
    nullptr,
};
static const wl_interface* _CZwpLinuxDmabufV1ModifierTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CZwpLinuxDmabufV1Requests[] = {
    { .name = "destroy", .signature = "", .types = linuxDmabufV1_dummyTypes + 0},
    { .name = "create_params", .signature = "n", .types = _CZwpLinuxDmabufV1CreateParamsTypes + 0},
    { .name = "get_default_feedback", .signature = "4n", .types = _CZwpLinuxDmabufV1GetDefaultFeedbackTypes + 0},
    { .name = "get_surface_feedback", .signature = "4no", .types = _CZwpLinuxDmabufV1GetSurfaceFeedbackTypes + 0},
};

static const wl_message _CZwpLinuxDmabufV1Events[] = {
    { .name = "format", .signature = "u", .types = _CZwpLinuxDmabufV1FormatTypes + 0},
    { .name = "modifier", .signature = "3uuu", .types = _CZwpLinuxDmabufV1ModifierTypes + 0},
};

const wl_interface zwp_linux_dmabuf_v1_interface = {
    .name = "zwp_linux_dmabuf_v1", .version = 6,
    .method_count = 4, .methods = _CZwpLinuxDmabufV1Requests,
    .event_count = 2, .events = _CZwpLinuxDmabufV1Events,
};

CZwpLinuxDmabufV1::CZwpLinuxDmabufV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_linux_dmabuf_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpLinuxDmabufV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpLinuxDmabufV1VTable, this, nullptr);
}

CZwpLinuxDmabufV1::~CZwpLinuxDmabufV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpLinuxDmabufV1::onDestroyCalled() {
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

void CZwpLinuxDmabufV1::setDestroy(F<void(CZwpLinuxDmabufV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZwpLinuxDmabufV1::setCreateParams(F<void(CZwpLinuxDmabufV1*, uint32_t)> &&handler) {
    requests.createParams = std::move(handler);
}

void CZwpLinuxDmabufV1::setGetDefaultFeedback(F<void(CZwpLinuxDmabufV1*, uint32_t)> &&handler) {
    requests.getDefaultFeedback = std::move(handler);
}

void CZwpLinuxDmabufV1::setGetSurfaceFeedback(F<void(CZwpLinuxDmabufV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getSurfaceFeedback = std::move(handler);
}

static void _CZwpLinuxBufferParamsV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpLinuxBufferParamsV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpLinuxBufferParamsV1Add(wl_client* client, wl_resource* resource, int32_t fd, uint32_t plane_idx, uint32_t offset, uint32_t stride, uint32_t modifier_hi, uint32_t modifier_lo) {
    const auto PO = (CZwpLinuxBufferParamsV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.add)
        PO->requests.add(PO, fd, plane_idx, offset, stride, modifier_hi, modifier_lo);
}

static void _CZwpLinuxBufferParamsV1Create(wl_client* client, wl_resource* resource, int32_t width, int32_t height, uint32_t format, zwpLinuxBufferParamsV1Flags flags) {
    const auto PO = (CZwpLinuxBufferParamsV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.create)
        PO->requests.create(PO, width, height, format, flags);
}

static void _CZwpLinuxBufferParamsV1CreateImmed(wl_client* client, wl_resource* resource, uint32_t buffer_id, int32_t width, int32_t height, uint32_t format, zwpLinuxBufferParamsV1Flags flags) {
    const auto PO = (CZwpLinuxBufferParamsV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createImmed)
        PO->requests.createImmed(PO, buffer_id, width, height, format, flags);
}

static void _CZwpLinuxBufferParamsV1SetSamplingDevice(wl_client* client, wl_resource* resource, wl_array* device) {
    const auto PO = (CZwpLinuxBufferParamsV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setSamplingDevice)
        PO->requests.setSamplingDevice(PO, device);
}

static void _CZwpLinuxBufferParamsV1__DestroyListener(wl_listener* l, void* d) {
    CZwpLinuxBufferParamsV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpLinuxBufferParamsV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpLinuxBufferParamsV1VTable[] = {
    (void*)_CZwpLinuxBufferParamsV1Destroy,
    (void*)_CZwpLinuxBufferParamsV1Add,
    (void*)_CZwpLinuxBufferParamsV1Create,
    (void*)_CZwpLinuxBufferParamsV1CreateImmed,
    (void*)_CZwpLinuxBufferParamsV1SetSamplingDevice,
};

void CZwpLinuxBufferParamsV1::sendCreated(wl_resource* buffer) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, buffer);
}

void CZwpLinuxBufferParamsV1::sendFailed() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CZwpLinuxBufferParamsV1::sendCreatedRaw(wl_resource* buffer) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, buffer);
}

void CZwpLinuxBufferParamsV1::sendFailedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}
static const wl_interface* _CZwpLinuxBufferParamsV1AddTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CZwpLinuxBufferParamsV1CreateTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CZwpLinuxBufferParamsV1CreateImmedTypes[] = {
    &wl_buffer_interface,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CZwpLinuxBufferParamsV1SetSamplingDeviceTypes[] = {
    nullptr,
};
static const wl_interface* _CZwpLinuxBufferParamsV1CreatedTypes[] = {
    &wl_buffer_interface,
};

static const wl_message _CZwpLinuxBufferParamsV1Requests[] = {
    { .name = "destroy", .signature = "", .types = linuxDmabufV1_dummyTypes + 0},
    { .name = "add", .signature = "huuuuu", .types = _CZwpLinuxBufferParamsV1AddTypes + 0},
    { .name = "create", .signature = "iiuu", .types = _CZwpLinuxBufferParamsV1CreateTypes + 0},
    { .name = "create_immed", .signature = "2niiuu", .types = _CZwpLinuxBufferParamsV1CreateImmedTypes + 0},
    { .name = "set_sampling_device", .signature = "6a", .types = _CZwpLinuxBufferParamsV1SetSamplingDeviceTypes + 0},
};

static const wl_message _CZwpLinuxBufferParamsV1Events[] = {
    { .name = "created", .signature = "n", .types = _CZwpLinuxBufferParamsV1CreatedTypes + 0},
    { .name = "failed", .signature = "", .types = linuxDmabufV1_dummyTypes + 0},
};

const wl_interface zwp_linux_buffer_params_v1_interface = {
    .name = "zwp_linux_buffer_params_v1", .version = 6,
    .method_count = 5, .methods = _CZwpLinuxBufferParamsV1Requests,
    .event_count = 2, .events = _CZwpLinuxBufferParamsV1Events,
};

CZwpLinuxBufferParamsV1::CZwpLinuxBufferParamsV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_linux_buffer_params_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpLinuxBufferParamsV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpLinuxBufferParamsV1VTable, this, nullptr);
}

CZwpLinuxBufferParamsV1::~CZwpLinuxBufferParamsV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpLinuxBufferParamsV1::onDestroyCalled() {
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

void CZwpLinuxBufferParamsV1::setDestroy(F<void(CZwpLinuxBufferParamsV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZwpLinuxBufferParamsV1::setAdd(F<void(CZwpLinuxBufferParamsV1*, int32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t)> &&handler) {
    requests.add = std::move(handler);
}

void CZwpLinuxBufferParamsV1::setCreate(F<void(CZwpLinuxBufferParamsV1*, int32_t, int32_t, uint32_t, zwpLinuxBufferParamsV1Flags)> &&handler) {
    requests.create = std::move(handler);
}

void CZwpLinuxBufferParamsV1::setCreateImmed(F<void(CZwpLinuxBufferParamsV1*, uint32_t, int32_t, int32_t, uint32_t, zwpLinuxBufferParamsV1Flags)> &&handler) {
    requests.createImmed = std::move(handler);
}

void CZwpLinuxBufferParamsV1::setSetSamplingDevice(F<void(CZwpLinuxBufferParamsV1*, wl_array*)> &&handler) {
    requests.setSamplingDevice = std::move(handler);
}

static void _CZwpLinuxDmabufFeedbackV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwpLinuxDmabufFeedbackV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwpLinuxDmabufFeedbackV1__DestroyListener(wl_listener* l, void* d) {
    CZwpLinuxDmabufFeedbackV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwpLinuxDmabufFeedbackV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwpLinuxDmabufFeedbackV1VTable[] = {
    (void*)_CZwpLinuxDmabufFeedbackV1Destroy,
};

void CZwpLinuxDmabufFeedbackV1::sendDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CZwpLinuxDmabufFeedbackV1::sendFormatTable(int32_t fd, uint32_t size) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, fd, size);
}

void CZwpLinuxDmabufFeedbackV1::sendMainDevice(wl_array* device) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, device);
}

void CZwpLinuxDmabufFeedbackV1::sendTrancheDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CZwpLinuxDmabufFeedbackV1::sendTrancheTargetDevice(wl_array* device) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, device);
}

void CZwpLinuxDmabufFeedbackV1::sendTrancheFormats(wl_array* indices) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, indices);
}

void CZwpLinuxDmabufFeedbackV1::sendTrancheFlags(zwpLinuxDmabufFeedbackV1TrancheFlags flags) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6, flags);
}

void CZwpLinuxDmabufFeedbackV1::sendDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CZwpLinuxDmabufFeedbackV1::sendFormatTableRaw(int32_t fd, uint32_t size) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, fd, size);
}

void CZwpLinuxDmabufFeedbackV1::sendMainDeviceRaw(wl_array* device) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, device);
}

void CZwpLinuxDmabufFeedbackV1::sendTrancheDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CZwpLinuxDmabufFeedbackV1::sendTrancheTargetDeviceRaw(wl_array* device) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, device);
}

void CZwpLinuxDmabufFeedbackV1::sendTrancheFormatsRaw(wl_array* indices) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, indices);
}

void CZwpLinuxDmabufFeedbackV1::sendTrancheFlagsRaw(zwpLinuxDmabufFeedbackV1TrancheFlags flags) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6, flags);
}
static const wl_interface* _CZwpLinuxDmabufFeedbackV1FormatTableTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CZwpLinuxDmabufFeedbackV1MainDeviceTypes[] = {
    nullptr,
};
static const wl_interface* _CZwpLinuxDmabufFeedbackV1TrancheTargetDeviceTypes[] = {
    nullptr,
};
static const wl_interface* _CZwpLinuxDmabufFeedbackV1TrancheFormatsTypes[] = {
    nullptr,
};
static const wl_interface* _CZwpLinuxDmabufFeedbackV1TrancheFlagsTypes[] = {
    nullptr,
};

static const wl_message _CZwpLinuxDmabufFeedbackV1Requests[] = {
    { .name = "destroy", .signature = "", .types = linuxDmabufV1_dummyTypes + 0},
};

static const wl_message _CZwpLinuxDmabufFeedbackV1Events[] = {
    { .name = "done", .signature = "", .types = linuxDmabufV1_dummyTypes + 0},
    { .name = "format_table", .signature = "hu", .types = _CZwpLinuxDmabufFeedbackV1FormatTableTypes + 0},
    { .name = "main_device", .signature = "a", .types = _CZwpLinuxDmabufFeedbackV1MainDeviceTypes + 0},
    { .name = "tranche_done", .signature = "", .types = linuxDmabufV1_dummyTypes + 0},
    { .name = "tranche_target_device", .signature = "a", .types = _CZwpLinuxDmabufFeedbackV1TrancheTargetDeviceTypes + 0},
    { .name = "tranche_formats", .signature = "a", .types = _CZwpLinuxDmabufFeedbackV1TrancheFormatsTypes + 0},
    { .name = "tranche_flags", .signature = "u", .types = _CZwpLinuxDmabufFeedbackV1TrancheFlagsTypes + 0},
};

const wl_interface zwp_linux_dmabuf_feedback_v1_interface = {
    .name = "zwp_linux_dmabuf_feedback_v1", .version = 6,
    .method_count = 1, .methods = _CZwpLinuxDmabufFeedbackV1Requests,
    .event_count = 7, .events = _CZwpLinuxDmabufFeedbackV1Events,
};

CZwpLinuxDmabufFeedbackV1::CZwpLinuxDmabufFeedbackV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwp_linux_dmabuf_feedback_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwpLinuxDmabufFeedbackV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwpLinuxDmabufFeedbackV1VTable, this, nullptr);
}

CZwpLinuxDmabufFeedbackV1::~CZwpLinuxDmabufFeedbackV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwpLinuxDmabufFeedbackV1::onDestroyCalled() {
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

void CZwpLinuxDmabufFeedbackV1::setDestroy(F<void(CZwpLinuxDmabufFeedbackV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

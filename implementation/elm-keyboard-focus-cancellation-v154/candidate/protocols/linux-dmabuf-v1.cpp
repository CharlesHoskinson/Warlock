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

static void _CZwpLinuxDmabufV1Format(void* data, void* resource, uint32_t format) {
    const auto PO = (CCZwpLinuxDmabufV1*)data;
    if (PO && PO->requests.format)
        PO->requests.format(PO, format);
}

static void _CZwpLinuxDmabufV1Modifier(void* data, void* resource, uint32_t format, uint32_t modifier_hi, uint32_t modifier_lo) {
    const auto PO = (CCZwpLinuxDmabufV1*)data;
    if (PO && PO->requests.modifier)
        PO->requests.modifier(PO, format, modifier_hi, modifier_lo);
}

static const void* _CCZwpLinuxDmabufV1VTable[] = {
    (void*)_CZwpLinuxDmabufV1Format,
    (void*)_CZwpLinuxDmabufV1Modifier,
};

void CCZwpLinuxDmabufV1::sendDestroy() {
    if (!pResource)
        return;
    destroyed = true;

    auto proxy = wl_proxy_marshal_flags(pResource, 0, nullptr, wl_proxy_get_version(pResource), 1);
    proxy;
}

wl_proxy* CCZwpLinuxDmabufV1::sendCreateParams() {
    if (!pResource)
        return nullptr;

    auto proxy = wl_proxy_marshal_flags(pResource, 1, &zwp_linux_buffer_params_v1_interface, wl_proxy_get_version(pResource), 0, nullptr);

    return proxy;
}

wl_proxy* CCZwpLinuxDmabufV1::sendGetDefaultFeedback() {
    if (!pResource)
        return nullptr;

    auto proxy = wl_proxy_marshal_flags(pResource, 2, &zwp_linux_dmabuf_feedback_v1_interface, wl_proxy_get_version(pResource), 0, nullptr);

    return proxy;
}

wl_proxy* CCZwpLinuxDmabufV1::sendGetSurfaceFeedback(wl_proxy* surface) {
    if (!pResource)
        return nullptr;

    auto proxy = wl_proxy_marshal_flags(pResource, 3, &zwp_linux_dmabuf_feedback_v1_interface, wl_proxy_get_version(pResource), 0, nullptr, surface);

    return proxy;
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

CCZwpLinuxDmabufV1::CCZwpLinuxDmabufV1(wl_proxy* resource) : pResource(resource) {

    if (!pResource)
        return;

    wl_proxy_add_listener(pResource, (void (**)(void))&_CCZwpLinuxDmabufV1VTable, this);
}

CCZwpLinuxDmabufV1::~CCZwpLinuxDmabufV1() {
    if (!destroyed)
        sendDestroy();
}

void CCZwpLinuxDmabufV1::setFormat(F<void(CCZwpLinuxDmabufV1*, uint32_t)> &&handler) {
    requests.format = std::move(handler);
}

void CCZwpLinuxDmabufV1::setModifier(F<void(CCZwpLinuxDmabufV1*, uint32_t, uint32_t, uint32_t)> &&handler) {
    requests.modifier = std::move(handler);
}

static void _CZwpLinuxBufferParamsV1Created(void* data, void* resource, wl_proxy* buffer) {
    const auto PO = (CCZwpLinuxBufferParamsV1*)data;
    if (PO && PO->requests.created)
        PO->requests.created(PO, buffer);
}

static void _CZwpLinuxBufferParamsV1Failed(void* data, void* resource) {
    const auto PO = (CCZwpLinuxBufferParamsV1*)data;
    if (PO && PO->requests.failed)
        PO->requests.failed(PO);
}

static const void* _CCZwpLinuxBufferParamsV1VTable[] = {
    (void*)_CZwpLinuxBufferParamsV1Created,
    (void*)_CZwpLinuxBufferParamsV1Failed,
};

void CCZwpLinuxBufferParamsV1::sendDestroy() {
    if (!pResource)
        return;
    destroyed = true;

    auto proxy = wl_proxy_marshal_flags(pResource, 0, nullptr, wl_proxy_get_version(pResource), 1);
    proxy;
}

void CCZwpLinuxBufferParamsV1::sendAdd(int32_t fd, uint32_t plane_idx, uint32_t offset, uint32_t stride, uint32_t modifier_hi, uint32_t modifier_lo) {
    if (!pResource)
        return;

    auto proxy = wl_proxy_marshal_flags(pResource, 1, nullptr, wl_proxy_get_version(pResource), 0, fd, plane_idx, offset, stride, modifier_hi, modifier_lo);
    proxy;
}

void CCZwpLinuxBufferParamsV1::sendCreate(int32_t width, int32_t height, uint32_t format, zwpLinuxBufferParamsV1Flags flags) {
    if (!pResource)
        return;

    auto proxy = wl_proxy_marshal_flags(pResource, 2, nullptr, wl_proxy_get_version(pResource), 0, width, height, format, flags);
    proxy;
}

wl_proxy* CCZwpLinuxBufferParamsV1::sendCreateImmed(int32_t width, int32_t height, uint32_t format, zwpLinuxBufferParamsV1Flags flags) {
    if (!pResource)
        return nullptr;

    auto proxy = wl_proxy_marshal_flags(pResource, 3, &wl_buffer_interface, wl_proxy_get_version(pResource), 0, nullptr, width, height, format, flags);

    return proxy;
}

void CCZwpLinuxBufferParamsV1::sendSetSamplingDevice(wl_array* device) {
    if (!pResource)
        return;

    auto proxy = wl_proxy_marshal_flags(pResource, 4, nullptr, wl_proxy_get_version(pResource), 0, device);
    proxy;
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

CCZwpLinuxBufferParamsV1::CCZwpLinuxBufferParamsV1(wl_proxy* resource) : pResource(resource) {

    if (!pResource)
        return;

    wl_proxy_add_listener(pResource, (void (**)(void))&_CCZwpLinuxBufferParamsV1VTable, this);
}

CCZwpLinuxBufferParamsV1::~CCZwpLinuxBufferParamsV1() {
    if (!destroyed)
        sendDestroy();
}

void CCZwpLinuxBufferParamsV1::setCreated(F<void(CCZwpLinuxBufferParamsV1*, wl_proxy*)> &&handler) {
    requests.created = std::move(handler);
}

void CCZwpLinuxBufferParamsV1::setFailed(F<void(CCZwpLinuxBufferParamsV1*)> &&handler) {
    requests.failed = std::move(handler);
}

static void _CZwpLinuxDmabufFeedbackV1Done(void* data, void* resource) {
    const auto PO = (CCZwpLinuxDmabufFeedbackV1*)data;
    if (PO && PO->requests.done)
        PO->requests.done(PO);
}

static void _CZwpLinuxDmabufFeedbackV1FormatTable(void* data, void* resource, int32_t fd, uint32_t size) {
    const auto PO = (CCZwpLinuxDmabufFeedbackV1*)data;
    if (PO && PO->requests.formatTable)
        PO->requests.formatTable(PO, fd, size);
}

static void _CZwpLinuxDmabufFeedbackV1MainDevice(void* data, void* resource, wl_array* device) {
    const auto PO = (CCZwpLinuxDmabufFeedbackV1*)data;
    if (PO && PO->requests.mainDevice)
        PO->requests.mainDevice(PO, device);
}

static void _CZwpLinuxDmabufFeedbackV1TrancheDone(void* data, void* resource) {
    const auto PO = (CCZwpLinuxDmabufFeedbackV1*)data;
    if (PO && PO->requests.trancheDone)
        PO->requests.trancheDone(PO);
}

static void _CZwpLinuxDmabufFeedbackV1TrancheTargetDevice(void* data, void* resource, wl_array* device) {
    const auto PO = (CCZwpLinuxDmabufFeedbackV1*)data;
    if (PO && PO->requests.trancheTargetDevice)
        PO->requests.trancheTargetDevice(PO, device);
}

static void _CZwpLinuxDmabufFeedbackV1TrancheFormats(void* data, void* resource, wl_array* indices) {
    const auto PO = (CCZwpLinuxDmabufFeedbackV1*)data;
    if (PO && PO->requests.trancheFormats)
        PO->requests.trancheFormats(PO, indices);
}

static void _CZwpLinuxDmabufFeedbackV1TrancheFlags(void* data, void* resource, zwpLinuxDmabufFeedbackV1TrancheFlags flags) {
    const auto PO = (CCZwpLinuxDmabufFeedbackV1*)data;
    if (PO && PO->requests.trancheFlags)
        PO->requests.trancheFlags(PO, flags);
}

static const void* _CCZwpLinuxDmabufFeedbackV1VTable[] = {
    (void*)_CZwpLinuxDmabufFeedbackV1Done,
    (void*)_CZwpLinuxDmabufFeedbackV1FormatTable,
    (void*)_CZwpLinuxDmabufFeedbackV1MainDevice,
    (void*)_CZwpLinuxDmabufFeedbackV1TrancheDone,
    (void*)_CZwpLinuxDmabufFeedbackV1TrancheTargetDevice,
    (void*)_CZwpLinuxDmabufFeedbackV1TrancheFormats,
    (void*)_CZwpLinuxDmabufFeedbackV1TrancheFlags,
};

void CCZwpLinuxDmabufFeedbackV1::sendDestroy() {
    if (!pResource)
        return;
    destroyed = true;

    auto proxy = wl_proxy_marshal_flags(pResource, 0, nullptr, wl_proxy_get_version(pResource), 1);
    proxy;
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

CCZwpLinuxDmabufFeedbackV1::CCZwpLinuxDmabufFeedbackV1(wl_proxy* resource) : pResource(resource) {

    if (!pResource)
        return;

    wl_proxy_add_listener(pResource, (void (**)(void))&_CCZwpLinuxDmabufFeedbackV1VTable, this);
}

CCZwpLinuxDmabufFeedbackV1::~CCZwpLinuxDmabufFeedbackV1() {
    if (!destroyed)
        sendDestroy();
}

void CCZwpLinuxDmabufFeedbackV1::setDone(F<void(CCZwpLinuxDmabufFeedbackV1*)> &&handler) {
    requests.done = std::move(handler);
}

void CCZwpLinuxDmabufFeedbackV1::setFormatTable(F<void(CCZwpLinuxDmabufFeedbackV1*, int32_t, uint32_t)> &&handler) {
    requests.formatTable = std::move(handler);
}

void CCZwpLinuxDmabufFeedbackV1::setMainDevice(F<void(CCZwpLinuxDmabufFeedbackV1*, wl_array*)> &&handler) {
    requests.mainDevice = std::move(handler);
}

void CCZwpLinuxDmabufFeedbackV1::setTrancheDone(F<void(CCZwpLinuxDmabufFeedbackV1*)> &&handler) {
    requests.trancheDone = std::move(handler);
}

void CCZwpLinuxDmabufFeedbackV1::setTrancheTargetDevice(F<void(CCZwpLinuxDmabufFeedbackV1*, wl_array*)> &&handler) {
    requests.trancheTargetDevice = std::move(handler);
}

void CCZwpLinuxDmabufFeedbackV1::setTrancheFormats(F<void(CCZwpLinuxDmabufFeedbackV1*, wl_array*)> &&handler) {
    requests.trancheFormats = std::move(handler);
}

void CCZwpLinuxDmabufFeedbackV1::setTrancheFlags(F<void(CCZwpLinuxDmabufFeedbackV1*, zwpLinuxDmabufFeedbackV1TrancheFlags)> &&handler) {
    requests.trancheFlags = std::move(handler);
}

#undef F

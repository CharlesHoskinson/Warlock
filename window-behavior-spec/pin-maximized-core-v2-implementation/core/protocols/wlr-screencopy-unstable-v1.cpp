// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// wlr_screencopy_unstable_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2018 Simon Ser
    Copyright © 2019 Andri Yngvason

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
#include "wlr-screencopy-unstable-v1.hpp"
#undef private
#define F std::function

static const wl_interface* wlrScreencopyUnstableV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface zwlr_screencopy_manager_v1_interface;
extern const wl_interface zwlr_screencopy_frame_v1_interface;
extern const wl_interface wl_output_interface;
extern const wl_interface wl_buffer_interface;

static void _CZwlrScreencopyManagerV1CaptureOutput(wl_client* client, wl_resource* resource, uint32_t frame, int32_t overlay_cursor, wl_resource* output) {
    const auto PO = (CZwlrScreencopyManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.captureOutput)
        PO->requests.captureOutput(PO, frame, overlay_cursor, output);
}

static void _CZwlrScreencopyManagerV1CaptureOutputRegion(wl_client* client, wl_resource* resource, uint32_t frame, int32_t overlay_cursor, wl_resource* output, int32_t x, int32_t y, int32_t width, int32_t height) {
    const auto PO = (CZwlrScreencopyManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.captureOutputRegion)
        PO->requests.captureOutputRegion(PO, frame, overlay_cursor, output, x, y, width, height);
}

static void _CZwlrScreencopyManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrScreencopyManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwlrScreencopyManagerV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrScreencopyManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrScreencopyManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrScreencopyManagerV1VTable[] = {
    (void*)_CZwlrScreencopyManagerV1CaptureOutput,
    (void*)_CZwlrScreencopyManagerV1CaptureOutputRegion,
    (void*)_CZwlrScreencopyManagerV1Destroy,
};
static const wl_interface* _CZwlrScreencopyManagerV1CaptureOutputTypes[] = {
    &zwlr_screencopy_frame_v1_interface,
    nullptr,
    &wl_output_interface,
};
static const wl_interface* _CZwlrScreencopyManagerV1CaptureOutputRegionTypes[] = {
    &zwlr_screencopy_frame_v1_interface,
    nullptr,
    &wl_output_interface,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CZwlrScreencopyManagerV1Requests[] = {
    { .name = "capture_output", .signature = "nio", .types = _CZwlrScreencopyManagerV1CaptureOutputTypes + 0},
    { .name = "capture_output_region", .signature = "nioiiii", .types = _CZwlrScreencopyManagerV1CaptureOutputRegionTypes + 0},
    { .name = "destroy", .signature = "", .types = wlrScreencopyUnstableV1_dummyTypes + 0},
};

const wl_interface zwlr_screencopy_manager_v1_interface = {
    .name = "zwlr_screencopy_manager_v1", .version = 3,
    .method_count = 3, .methods = _CZwlrScreencopyManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CZwlrScreencopyManagerV1::CZwlrScreencopyManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_screencopy_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrScreencopyManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrScreencopyManagerV1VTable, this, nullptr);
}

CZwlrScreencopyManagerV1::~CZwlrScreencopyManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrScreencopyManagerV1::onDestroyCalled() {
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

void CZwlrScreencopyManagerV1::setCaptureOutput(F<void(CZwlrScreencopyManagerV1*, uint32_t, int32_t, wl_resource*)> &&handler) {
    requests.captureOutput = std::move(handler);
}

void CZwlrScreencopyManagerV1::setCaptureOutputRegion(F<void(CZwlrScreencopyManagerV1*, uint32_t, int32_t, wl_resource*, int32_t, int32_t, int32_t, int32_t)> &&handler) {
    requests.captureOutputRegion = std::move(handler);
}

void CZwlrScreencopyManagerV1::setDestroy(F<void(CZwlrScreencopyManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZwlrScreencopyFrameV1Copy(wl_client* client, wl_resource* resource, wl_resource* buffer) {
    const auto PO = (CZwlrScreencopyFrameV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.copy)
        PO->requests.copy(PO, buffer);
}

static void _CZwlrScreencopyFrameV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrScreencopyFrameV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwlrScreencopyFrameV1CopyWithDamage(wl_client* client, wl_resource* resource, wl_resource* buffer) {
    const auto PO = (CZwlrScreencopyFrameV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.copyWithDamage)
        PO->requests.copyWithDamage(PO, buffer);
}

static void _CZwlrScreencopyFrameV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrScreencopyFrameV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrScreencopyFrameV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrScreencopyFrameV1VTable[] = {
    (void*)_CZwlrScreencopyFrameV1Copy,
    (void*)_CZwlrScreencopyFrameV1Destroy,
    (void*)_CZwlrScreencopyFrameV1CopyWithDamage,
};

void CZwlrScreencopyFrameV1::sendBuffer(uint32_t format, uint32_t width, uint32_t height, uint32_t stride) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format, width, height, stride);
}

void CZwlrScreencopyFrameV1::sendFlags(zwlrScreencopyFrameV1Flags flags) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, flags);
}

void CZwlrScreencopyFrameV1::sendReady(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, tv_sec_hi, tv_sec_lo, tv_nsec);
}

void CZwlrScreencopyFrameV1::sendFailed() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CZwlrScreencopyFrameV1::sendDamage(uint32_t x, uint32_t y, uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, x, y, width, height);
}

void CZwlrScreencopyFrameV1::sendLinuxDmabuf(uint32_t format, uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, format, width, height);
}

void CZwlrScreencopyFrameV1::sendBufferDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6);
}

void CZwlrScreencopyFrameV1::sendBufferRaw(uint32_t format, uint32_t width, uint32_t height, uint32_t stride) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format, width, height, stride);
}

void CZwlrScreencopyFrameV1::sendFlagsRaw(zwlrScreencopyFrameV1Flags flags) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, flags);
}

void CZwlrScreencopyFrameV1::sendReadyRaw(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, tv_sec_hi, tv_sec_lo, tv_nsec);
}

void CZwlrScreencopyFrameV1::sendFailedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CZwlrScreencopyFrameV1::sendDamageRaw(uint32_t x, uint32_t y, uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, x, y, width, height);
}

void CZwlrScreencopyFrameV1::sendLinuxDmabufRaw(uint32_t format, uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, format, width, height);
}

void CZwlrScreencopyFrameV1::sendBufferDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6);
}
static const wl_interface* _CZwlrScreencopyFrameV1CopyTypes[] = {
    &wl_buffer_interface,
};
static const wl_interface* _CZwlrScreencopyFrameV1CopyWithDamageTypes[] = {
    &wl_buffer_interface,
};
static const wl_interface* _CZwlrScreencopyFrameV1BufferTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CZwlrScreencopyFrameV1FlagsTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrScreencopyFrameV1ReadyTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CZwlrScreencopyFrameV1DamageTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CZwlrScreencopyFrameV1LinuxDmabufTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CZwlrScreencopyFrameV1Requests[] = {
    { .name = "copy", .signature = "o", .types = _CZwlrScreencopyFrameV1CopyTypes + 0},
    { .name = "destroy", .signature = "", .types = wlrScreencopyUnstableV1_dummyTypes + 0},
    { .name = "copy_with_damage", .signature = "2o", .types = _CZwlrScreencopyFrameV1CopyWithDamageTypes + 0},
};

static const wl_message _CZwlrScreencopyFrameV1Events[] = {
    { .name = "buffer", .signature = "uuuu", .types = _CZwlrScreencopyFrameV1BufferTypes + 0},
    { .name = "flags", .signature = "u", .types = _CZwlrScreencopyFrameV1FlagsTypes + 0},
    { .name = "ready", .signature = "uuu", .types = _CZwlrScreencopyFrameV1ReadyTypes + 0},
    { .name = "failed", .signature = "", .types = wlrScreencopyUnstableV1_dummyTypes + 0},
    { .name = "damage", .signature = "2uuuu", .types = _CZwlrScreencopyFrameV1DamageTypes + 0},
    { .name = "linux_dmabuf", .signature = "3uuu", .types = _CZwlrScreencopyFrameV1LinuxDmabufTypes + 0},
    { .name = "buffer_done", .signature = "3", .types = wlrScreencopyUnstableV1_dummyTypes + 0},
};

const wl_interface zwlr_screencopy_frame_v1_interface = {
    .name = "zwlr_screencopy_frame_v1", .version = 3,
    .method_count = 3, .methods = _CZwlrScreencopyFrameV1Requests,
    .event_count = 7, .events = _CZwlrScreencopyFrameV1Events,
};

CZwlrScreencopyFrameV1::CZwlrScreencopyFrameV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_screencopy_frame_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrScreencopyFrameV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrScreencopyFrameV1VTable, this, nullptr);
}

CZwlrScreencopyFrameV1::~CZwlrScreencopyFrameV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrScreencopyFrameV1::onDestroyCalled() {
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

void CZwlrScreencopyFrameV1::setCopy(F<void(CZwlrScreencopyFrameV1*, wl_resource*)> &&handler) {
    requests.copy = std::move(handler);
}

void CZwlrScreencopyFrameV1::setDestroy(F<void(CZwlrScreencopyFrameV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZwlrScreencopyFrameV1::setCopyWithDamage(F<void(CZwlrScreencopyFrameV1*, wl_resource*)> &&handler) {
    requests.copyWithDamage = std::move(handler);
}

#undef F

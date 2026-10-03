// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// ext_image_copy_capture_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2021-2023 Andri Yngvason
    Copyright © 2024 Simon Ser

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
#include "ext-image-copy-capture-v1.hpp"
#undef private
#define F std::function

static const wl_interface* extImageCopyCaptureV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface ext_image_copy_capture_manager_v1_interface;
extern const wl_interface ext_image_copy_capture_session_v1_interface;
extern const wl_interface ext_image_copy_capture_frame_v1_interface;
extern const wl_interface ext_image_copy_capture_cursor_session_v1_interface;
extern const wl_interface ext_image_capture_source_v1_interface;
extern const wl_interface wl_pointer_interface;
extern const wl_interface wl_buffer_interface;

static void _CExtImageCopyCaptureManagerV1CreateSession(wl_client* client, wl_resource* resource, uint32_t session, wl_resource* source, extImageCopyCaptureManagerV1Options options) {
    const auto PO = (CExtImageCopyCaptureManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createSession)
        PO->requests.createSession(PO, session, source, options);
}

static void _CExtImageCopyCaptureManagerV1CreatePointerCursorSession(wl_client* client, wl_resource* resource, uint32_t session, wl_resource* source, wl_resource* pointer) {
    const auto PO = (CExtImageCopyCaptureManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createPointerCursorSession)
        PO->requests.createPointerCursorSession(PO, session, source, pointer);
}

static void _CExtImageCopyCaptureManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtImageCopyCaptureManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtImageCopyCaptureManagerV1__DestroyListener(wl_listener* l, void* d) {
    CExtImageCopyCaptureManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtImageCopyCaptureManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtImageCopyCaptureManagerV1VTable[] = {
    (void*)_CExtImageCopyCaptureManagerV1CreateSession,
    (void*)_CExtImageCopyCaptureManagerV1CreatePointerCursorSession,
    (void*)_CExtImageCopyCaptureManagerV1Destroy,
};
static const wl_interface* _CExtImageCopyCaptureManagerV1CreateSessionTypes[] = {
    &ext_image_copy_capture_session_v1_interface,
    &ext_image_capture_source_v1_interface,
    nullptr,
};
static const wl_interface* _CExtImageCopyCaptureManagerV1CreatePointerCursorSessionTypes[] = {
    &ext_image_copy_capture_cursor_session_v1_interface,
    &ext_image_capture_source_v1_interface,
    &wl_pointer_interface,
};

static const wl_message _CExtImageCopyCaptureManagerV1Requests[] = {
    { .name = "create_session", .signature = "nou", .types = _CExtImageCopyCaptureManagerV1CreateSessionTypes + 0},
    { .name = "create_pointer_cursor_session", .signature = "noo", .types = _CExtImageCopyCaptureManagerV1CreatePointerCursorSessionTypes + 0},
    { .name = "destroy", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
};

const wl_interface ext_image_copy_capture_manager_v1_interface = {
    .name = "ext_image_copy_capture_manager_v1", .version = 1,
    .method_count = 3, .methods = _CExtImageCopyCaptureManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CExtImageCopyCaptureManagerV1::CExtImageCopyCaptureManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_image_copy_capture_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtImageCopyCaptureManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtImageCopyCaptureManagerV1VTable, this, nullptr);
}

CExtImageCopyCaptureManagerV1::~CExtImageCopyCaptureManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtImageCopyCaptureManagerV1::onDestroyCalled() {
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

void CExtImageCopyCaptureManagerV1::setCreateSession(F<void(CExtImageCopyCaptureManagerV1*, uint32_t, wl_resource*, extImageCopyCaptureManagerV1Options)> &&handler) {
    requests.createSession = std::move(handler);
}

void CExtImageCopyCaptureManagerV1::setCreatePointerCursorSession(F<void(CExtImageCopyCaptureManagerV1*, uint32_t, wl_resource*, wl_resource*)> &&handler) {
    requests.createPointerCursorSession = std::move(handler);
}

void CExtImageCopyCaptureManagerV1::setDestroy(F<void(CExtImageCopyCaptureManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CExtImageCopyCaptureSessionV1CreateFrame(wl_client* client, wl_resource* resource, uint32_t frame) {
    const auto PO = (CExtImageCopyCaptureSessionV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createFrame)
        PO->requests.createFrame(PO, frame);
}

static void _CExtImageCopyCaptureSessionV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtImageCopyCaptureSessionV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtImageCopyCaptureSessionV1__DestroyListener(wl_listener* l, void* d) {
    CExtImageCopyCaptureSessionV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtImageCopyCaptureSessionV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtImageCopyCaptureSessionV1VTable[] = {
    (void*)_CExtImageCopyCaptureSessionV1CreateFrame,
    (void*)_CExtImageCopyCaptureSessionV1Destroy,
};

void CExtImageCopyCaptureSessionV1::sendBufferSize(uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, width, height);
}

void CExtImageCopyCaptureSessionV1::sendShmFormat(uint32_t format) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, format);
}

void CExtImageCopyCaptureSessionV1::sendDmabufDevice(wl_array* device) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, device);
}

void CExtImageCopyCaptureSessionV1::sendDmabufFormat(uint32_t format, wl_array* modifiers) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, format, modifiers);
}

void CExtImageCopyCaptureSessionV1::sendDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CExtImageCopyCaptureSessionV1::sendStopped() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5);
}

void CExtImageCopyCaptureSessionV1::sendBufferSizeRaw(uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, width, height);
}

void CExtImageCopyCaptureSessionV1::sendShmFormatRaw(uint32_t format) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, format);
}

void CExtImageCopyCaptureSessionV1::sendDmabufDeviceRaw(wl_array* device) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, device);
}

void CExtImageCopyCaptureSessionV1::sendDmabufFormatRaw(uint32_t format, wl_array* modifiers) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, format, modifiers);
}

void CExtImageCopyCaptureSessionV1::sendDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CExtImageCopyCaptureSessionV1::sendStoppedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5);
}
static const wl_interface* _CExtImageCopyCaptureSessionV1CreateFrameTypes[] = {
    &ext_image_copy_capture_frame_v1_interface,
};
static const wl_interface* _CExtImageCopyCaptureSessionV1BufferSizeTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CExtImageCopyCaptureSessionV1ShmFormatTypes[] = {
    nullptr,
};
static const wl_interface* _CExtImageCopyCaptureSessionV1DmabufDeviceTypes[] = {
    nullptr,
};
static const wl_interface* _CExtImageCopyCaptureSessionV1DmabufFormatTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CExtImageCopyCaptureSessionV1Requests[] = {
    { .name = "create_frame", .signature = "n", .types = _CExtImageCopyCaptureSessionV1CreateFrameTypes + 0},
    { .name = "destroy", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
};

static const wl_message _CExtImageCopyCaptureSessionV1Events[] = {
    { .name = "buffer_size", .signature = "uu", .types = _CExtImageCopyCaptureSessionV1BufferSizeTypes + 0},
    { .name = "shm_format", .signature = "u", .types = _CExtImageCopyCaptureSessionV1ShmFormatTypes + 0},
    { .name = "dmabuf_device", .signature = "a", .types = _CExtImageCopyCaptureSessionV1DmabufDeviceTypes + 0},
    { .name = "dmabuf_format", .signature = "ua", .types = _CExtImageCopyCaptureSessionV1DmabufFormatTypes + 0},
    { .name = "done", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
    { .name = "stopped", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
};

const wl_interface ext_image_copy_capture_session_v1_interface = {
    .name = "ext_image_copy_capture_session_v1", .version = 1,
    .method_count = 2, .methods = _CExtImageCopyCaptureSessionV1Requests,
    .event_count = 6, .events = _CExtImageCopyCaptureSessionV1Events,
};

CExtImageCopyCaptureSessionV1::CExtImageCopyCaptureSessionV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_image_copy_capture_session_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtImageCopyCaptureSessionV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtImageCopyCaptureSessionV1VTable, this, nullptr);
}

CExtImageCopyCaptureSessionV1::~CExtImageCopyCaptureSessionV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtImageCopyCaptureSessionV1::onDestroyCalled() {
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

void CExtImageCopyCaptureSessionV1::setCreateFrame(F<void(CExtImageCopyCaptureSessionV1*, uint32_t)> &&handler) {
    requests.createFrame = std::move(handler);
}

void CExtImageCopyCaptureSessionV1::setDestroy(F<void(CExtImageCopyCaptureSessionV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CExtImageCopyCaptureFrameV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtImageCopyCaptureFrameV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtImageCopyCaptureFrameV1AttachBuffer(wl_client* client, wl_resource* resource, wl_resource* buffer) {
    const auto PO = (CExtImageCopyCaptureFrameV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.attachBuffer)
        PO->requests.attachBuffer(PO, buffer);
}

static void _CExtImageCopyCaptureFrameV1DamageBuffer(wl_client* client, wl_resource* resource, int32_t x, int32_t y, int32_t width, int32_t height) {
    const auto PO = (CExtImageCopyCaptureFrameV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.damageBuffer)
        PO->requests.damageBuffer(PO, x, y, width, height);
}

static void _CExtImageCopyCaptureFrameV1Capture(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtImageCopyCaptureFrameV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.capture)
        PO->requests.capture(PO);
}

static void _CExtImageCopyCaptureFrameV1__DestroyListener(wl_listener* l, void* d) {
    CExtImageCopyCaptureFrameV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtImageCopyCaptureFrameV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtImageCopyCaptureFrameV1VTable[] = {
    (void*)_CExtImageCopyCaptureFrameV1Destroy,
    (void*)_CExtImageCopyCaptureFrameV1AttachBuffer,
    (void*)_CExtImageCopyCaptureFrameV1DamageBuffer,
    (void*)_CExtImageCopyCaptureFrameV1Capture,
};

void CExtImageCopyCaptureFrameV1::sendTransform(uint32_t transform) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, transform);
}

void CExtImageCopyCaptureFrameV1::sendDamage(int32_t x, int32_t y, int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, x, y, width, height);
}

void CExtImageCopyCaptureFrameV1::sendPresentationTime(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, tv_sec_hi, tv_sec_lo, tv_nsec);
}

void CExtImageCopyCaptureFrameV1::sendReady() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CExtImageCopyCaptureFrameV1::sendFailed(extImageCopyCaptureFrameV1FailureReason reason) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, reason);
}

void CExtImageCopyCaptureFrameV1::sendTransformRaw(uint32_t transform) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, transform);
}

void CExtImageCopyCaptureFrameV1::sendDamageRaw(int32_t x, int32_t y, int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, x, y, width, height);
}

void CExtImageCopyCaptureFrameV1::sendPresentationTimeRaw(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, tv_sec_hi, tv_sec_lo, tv_nsec);
}

void CExtImageCopyCaptureFrameV1::sendReadyRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CExtImageCopyCaptureFrameV1::sendFailedRaw(extImageCopyCaptureFrameV1FailureReason reason) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, reason);
}
static const wl_interface* _CExtImageCopyCaptureFrameV1AttachBufferTypes[] = {
    &wl_buffer_interface,
};
static const wl_interface* _CExtImageCopyCaptureFrameV1DamageBufferTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CExtImageCopyCaptureFrameV1TransformTypes[] = {
    nullptr,
};
static const wl_interface* _CExtImageCopyCaptureFrameV1DamageTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CExtImageCopyCaptureFrameV1PresentationTimeTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CExtImageCopyCaptureFrameV1FailedTypes[] = {
    nullptr,
};

static const wl_message _CExtImageCopyCaptureFrameV1Requests[] = {
    { .name = "destroy", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
    { .name = "attach_buffer", .signature = "o", .types = _CExtImageCopyCaptureFrameV1AttachBufferTypes + 0},
    { .name = "damage_buffer", .signature = "iiii", .types = _CExtImageCopyCaptureFrameV1DamageBufferTypes + 0},
    { .name = "capture", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
};

static const wl_message _CExtImageCopyCaptureFrameV1Events[] = {
    { .name = "transform", .signature = "u", .types = _CExtImageCopyCaptureFrameV1TransformTypes + 0},
    { .name = "damage", .signature = "iiii", .types = _CExtImageCopyCaptureFrameV1DamageTypes + 0},
    { .name = "presentation_time", .signature = "uuu", .types = _CExtImageCopyCaptureFrameV1PresentationTimeTypes + 0},
    { .name = "ready", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
    { .name = "failed", .signature = "u", .types = _CExtImageCopyCaptureFrameV1FailedTypes + 0},
};

const wl_interface ext_image_copy_capture_frame_v1_interface = {
    .name = "ext_image_copy_capture_frame_v1", .version = 1,
    .method_count = 4, .methods = _CExtImageCopyCaptureFrameV1Requests,
    .event_count = 5, .events = _CExtImageCopyCaptureFrameV1Events,
};

CExtImageCopyCaptureFrameV1::CExtImageCopyCaptureFrameV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_image_copy_capture_frame_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtImageCopyCaptureFrameV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtImageCopyCaptureFrameV1VTable, this, nullptr);
}

CExtImageCopyCaptureFrameV1::~CExtImageCopyCaptureFrameV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtImageCopyCaptureFrameV1::onDestroyCalled() {
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

void CExtImageCopyCaptureFrameV1::setDestroy(F<void(CExtImageCopyCaptureFrameV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CExtImageCopyCaptureFrameV1::setAttachBuffer(F<void(CExtImageCopyCaptureFrameV1*, wl_resource*)> &&handler) {
    requests.attachBuffer = std::move(handler);
}

void CExtImageCopyCaptureFrameV1::setDamageBuffer(F<void(CExtImageCopyCaptureFrameV1*, int32_t, int32_t, int32_t, int32_t)> &&handler) {
    requests.damageBuffer = std::move(handler);
}

void CExtImageCopyCaptureFrameV1::setCapture(F<void(CExtImageCopyCaptureFrameV1*)> &&handler) {
    requests.capture = std::move(handler);
}

static void _CExtImageCopyCaptureCursorSessionV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtImageCopyCaptureCursorSessionV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtImageCopyCaptureCursorSessionV1GetCaptureSession(wl_client* client, wl_resource* resource, uint32_t session) {
    const auto PO = (CExtImageCopyCaptureCursorSessionV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getCaptureSession)
        PO->requests.getCaptureSession(PO, session);
}

static void _CExtImageCopyCaptureCursorSessionV1__DestroyListener(wl_listener* l, void* d) {
    CExtImageCopyCaptureCursorSessionV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtImageCopyCaptureCursorSessionV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtImageCopyCaptureCursorSessionV1VTable[] = {
    (void*)_CExtImageCopyCaptureCursorSessionV1Destroy,
    (void*)_CExtImageCopyCaptureCursorSessionV1GetCaptureSession,
};

void CExtImageCopyCaptureCursorSessionV1::sendEnter() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CExtImageCopyCaptureCursorSessionV1::sendLeave() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CExtImageCopyCaptureCursorSessionV1::sendPosition(int32_t x, int32_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, x, y);
}

void CExtImageCopyCaptureCursorSessionV1::sendHotspot(int32_t x, int32_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, x, y);
}

void CExtImageCopyCaptureCursorSessionV1::sendEnterRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CExtImageCopyCaptureCursorSessionV1::sendLeaveRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CExtImageCopyCaptureCursorSessionV1::sendPositionRaw(int32_t x, int32_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, x, y);
}

void CExtImageCopyCaptureCursorSessionV1::sendHotspotRaw(int32_t x, int32_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, x, y);
}
static const wl_interface* _CExtImageCopyCaptureCursorSessionV1GetCaptureSessionTypes[] = {
    &ext_image_copy_capture_session_v1_interface,
};
static const wl_interface* _CExtImageCopyCaptureCursorSessionV1PositionTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CExtImageCopyCaptureCursorSessionV1HotspotTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CExtImageCopyCaptureCursorSessionV1Requests[] = {
    { .name = "destroy", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
    { .name = "get_capture_session", .signature = "n", .types = _CExtImageCopyCaptureCursorSessionV1GetCaptureSessionTypes + 0},
};

static const wl_message _CExtImageCopyCaptureCursorSessionV1Events[] = {
    { .name = "enter", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
    { .name = "leave", .signature = "", .types = extImageCopyCaptureV1_dummyTypes + 0},
    { .name = "position", .signature = "ii", .types = _CExtImageCopyCaptureCursorSessionV1PositionTypes + 0},
    { .name = "hotspot", .signature = "ii", .types = _CExtImageCopyCaptureCursorSessionV1HotspotTypes + 0},
};

const wl_interface ext_image_copy_capture_cursor_session_v1_interface = {
    .name = "ext_image_copy_capture_cursor_session_v1", .version = 1,
    .method_count = 2, .methods = _CExtImageCopyCaptureCursorSessionV1Requests,
    .event_count = 4, .events = _CExtImageCopyCaptureCursorSessionV1Events,
};

CExtImageCopyCaptureCursorSessionV1::CExtImageCopyCaptureCursorSessionV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_image_copy_capture_cursor_session_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtImageCopyCaptureCursorSessionV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtImageCopyCaptureCursorSessionV1VTable, this, nullptr);
}

CExtImageCopyCaptureCursorSessionV1::~CExtImageCopyCaptureCursorSessionV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtImageCopyCaptureCursorSessionV1::onDestroyCalled() {
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

void CExtImageCopyCaptureCursorSessionV1::setDestroy(F<void(CExtImageCopyCaptureCursorSessionV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CExtImageCopyCaptureCursorSessionV1::setGetCaptureSession(F<void(CExtImageCopyCaptureCursorSessionV1*, uint32_t)> &&handler) {
    requests.getCaptureSession = std::move(handler);
}

#undef F

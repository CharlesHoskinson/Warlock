// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// ext_image_capture_source_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2022 Andri Yngvason
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
#include "ext-image-capture-source-v1.hpp"
#undef private
#define F std::function

static const wl_interface* extImageCaptureSourceV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface ext_image_capture_source_v1_interface;
extern const wl_interface ext_output_image_capture_source_manager_v1_interface;
extern const wl_interface ext_foreign_toplevel_image_capture_source_manager_v1_interface;
extern const wl_interface wl_output_interface;
extern const wl_interface ext_foreign_toplevel_handle_v1_interface;

static void _CExtImageCaptureSourceV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtImageCaptureSourceV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtImageCaptureSourceV1__DestroyListener(wl_listener* l, void* d) {
    CExtImageCaptureSourceV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtImageCaptureSourceV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtImageCaptureSourceV1VTable[] = {
    (void*)_CExtImageCaptureSourceV1Destroy,
};

static const wl_message _CExtImageCaptureSourceV1Requests[] = {
    { .name = "destroy", .signature = "", .types = extImageCaptureSourceV1_dummyTypes + 0},
};

const wl_interface ext_image_capture_source_v1_interface = {
    .name = "ext_image_capture_source_v1", .version = 1,
    .method_count = 1, .methods = _CExtImageCaptureSourceV1Requests,
    .event_count = 0, .events = nullptr,
};

CExtImageCaptureSourceV1::CExtImageCaptureSourceV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_image_capture_source_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtImageCaptureSourceV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtImageCaptureSourceV1VTable, this, nullptr);
}

CExtImageCaptureSourceV1::~CExtImageCaptureSourceV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtImageCaptureSourceV1::onDestroyCalled() {
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

void CExtImageCaptureSourceV1::setDestroy(F<void(CExtImageCaptureSourceV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CExtOutputImageCaptureSourceManagerV1CreateSource(wl_client* client, wl_resource* resource, uint32_t source, wl_resource* output) {
    const auto PO = (CExtOutputImageCaptureSourceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createSource)
        PO->requests.createSource(PO, source, output);
}

static void _CExtOutputImageCaptureSourceManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtOutputImageCaptureSourceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtOutputImageCaptureSourceManagerV1__DestroyListener(wl_listener* l, void* d) {
    CExtOutputImageCaptureSourceManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtOutputImageCaptureSourceManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtOutputImageCaptureSourceManagerV1VTable[] = {
    (void*)_CExtOutputImageCaptureSourceManagerV1CreateSource,
    (void*)_CExtOutputImageCaptureSourceManagerV1Destroy,
};
static const wl_interface* _CExtOutputImageCaptureSourceManagerV1CreateSourceTypes[] = {
    &ext_image_capture_source_v1_interface,
    &wl_output_interface,
};

static const wl_message _CExtOutputImageCaptureSourceManagerV1Requests[] = {
    { .name = "create_source", .signature = "no", .types = _CExtOutputImageCaptureSourceManagerV1CreateSourceTypes + 0},
    { .name = "destroy", .signature = "", .types = extImageCaptureSourceV1_dummyTypes + 0},
};

const wl_interface ext_output_image_capture_source_manager_v1_interface = {
    .name = "ext_output_image_capture_source_manager_v1", .version = 1,
    .method_count = 2, .methods = _CExtOutputImageCaptureSourceManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CExtOutputImageCaptureSourceManagerV1::CExtOutputImageCaptureSourceManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_output_image_capture_source_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtOutputImageCaptureSourceManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtOutputImageCaptureSourceManagerV1VTable, this, nullptr);
}

CExtOutputImageCaptureSourceManagerV1::~CExtOutputImageCaptureSourceManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtOutputImageCaptureSourceManagerV1::onDestroyCalled() {
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

void CExtOutputImageCaptureSourceManagerV1::setCreateSource(F<void(CExtOutputImageCaptureSourceManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.createSource = std::move(handler);
}

void CExtOutputImageCaptureSourceManagerV1::setDestroy(F<void(CExtOutputImageCaptureSourceManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CExtForeignToplevelImageCaptureSourceManagerV1CreateSource(wl_client* client, wl_resource* resource, uint32_t source, wl_resource* toplevel_handle) {
    const auto PO = (CExtForeignToplevelImageCaptureSourceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createSource)
        PO->requests.createSource(PO, source, toplevel_handle);
}

static void _CExtForeignToplevelImageCaptureSourceManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtForeignToplevelImageCaptureSourceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtForeignToplevelImageCaptureSourceManagerV1__DestroyListener(wl_listener* l, void* d) {
    CExtForeignToplevelImageCaptureSourceManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtForeignToplevelImageCaptureSourceManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtForeignToplevelImageCaptureSourceManagerV1VTable[] = {
    (void*)_CExtForeignToplevelImageCaptureSourceManagerV1CreateSource,
    (void*)_CExtForeignToplevelImageCaptureSourceManagerV1Destroy,
};
static const wl_interface* _CExtForeignToplevelImageCaptureSourceManagerV1CreateSourceTypes[] = {
    &ext_image_capture_source_v1_interface,
    &ext_foreign_toplevel_handle_v1_interface,
};

static const wl_message _CExtForeignToplevelImageCaptureSourceManagerV1Requests[] = {
    { .name = "create_source", .signature = "no", .types = _CExtForeignToplevelImageCaptureSourceManagerV1CreateSourceTypes + 0},
    { .name = "destroy", .signature = "", .types = extImageCaptureSourceV1_dummyTypes + 0},
};

const wl_interface ext_foreign_toplevel_image_capture_source_manager_v1_interface = {
    .name = "ext_foreign_toplevel_image_capture_source_manager_v1", .version = 1,
    .method_count = 2, .methods = _CExtForeignToplevelImageCaptureSourceManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CExtForeignToplevelImageCaptureSourceManagerV1::CExtForeignToplevelImageCaptureSourceManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_foreign_toplevel_image_capture_source_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtForeignToplevelImageCaptureSourceManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtForeignToplevelImageCaptureSourceManagerV1VTable, this, nullptr);
}

CExtForeignToplevelImageCaptureSourceManagerV1::~CExtForeignToplevelImageCaptureSourceManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtForeignToplevelImageCaptureSourceManagerV1::onDestroyCalled() {
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

void CExtForeignToplevelImageCaptureSourceManagerV1::setCreateSource(F<void(CExtForeignToplevelImageCaptureSourceManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.createSource = std::move(handler);
}

void CExtForeignToplevelImageCaptureSourceManagerV1::setDestroy(F<void(CExtForeignToplevelImageCaptureSourceManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

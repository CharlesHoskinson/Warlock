// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// content_type_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2021 Emmanuel Gil Peyrot
    Copyright © 2022 Xaver Hugl

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
#include "content-type-v1.hpp"
#undef private
#define F std::function

static const wl_interface* contentTypeV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wp_content_type_manager_v1_interface;
extern const wl_interface wp_content_type_v1_interface;
extern const wl_interface wl_surface_interface;

static void _CWpContentTypeManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpContentTypeManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpContentTypeManagerV1GetSurfaceContentType(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CWpContentTypeManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getSurfaceContentType)
        PO->requests.getSurfaceContentType(PO, id, surface);
}

static void _CWpContentTypeManagerV1__DestroyListener(wl_listener* l, void* d) {
    CWpContentTypeManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpContentTypeManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpContentTypeManagerV1VTable[] = {
    (void*)_CWpContentTypeManagerV1Destroy,
    (void*)_CWpContentTypeManagerV1GetSurfaceContentType,
};
static const wl_interface* _CWpContentTypeManagerV1GetSurfaceContentTypeTypes[] = {
    &wp_content_type_v1_interface,
    &wl_surface_interface,
};

static const wl_message _CWpContentTypeManagerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = contentTypeV1_dummyTypes + 0},
    { .name = "get_surface_content_type", .signature = "no", .types = _CWpContentTypeManagerV1GetSurfaceContentTypeTypes + 0},
};

const wl_interface wp_content_type_manager_v1_interface = {
    .name = "wp_content_type_manager_v1", .version = 1,
    .method_count = 2, .methods = _CWpContentTypeManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpContentTypeManagerV1::CWpContentTypeManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_content_type_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpContentTypeManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpContentTypeManagerV1VTable, this, nullptr);
}

CWpContentTypeManagerV1::~CWpContentTypeManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpContentTypeManagerV1::onDestroyCalled() {
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

void CWpContentTypeManagerV1::setDestroy(F<void(CWpContentTypeManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpContentTypeManagerV1::setGetSurfaceContentType(F<void(CWpContentTypeManagerV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getSurfaceContentType = std::move(handler);
}

static void _CWpContentTypeV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpContentTypeV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpContentTypeV1SetContentType(wl_client* client, wl_resource* resource, wpContentTypeV1Type content_type) {
    const auto PO = (CWpContentTypeV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setContentType)
        PO->requests.setContentType(PO, content_type);
}

static void _CWpContentTypeV1__DestroyListener(wl_listener* l, void* d) {
    CWpContentTypeV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpContentTypeV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpContentTypeV1VTable[] = {
    (void*)_CWpContentTypeV1Destroy,
    (void*)_CWpContentTypeV1SetContentType,
};
static const wl_interface* _CWpContentTypeV1SetContentTypeTypes[] = {
    nullptr,
};

static const wl_message _CWpContentTypeV1Requests[] = {
    { .name = "destroy", .signature = "", .types = contentTypeV1_dummyTypes + 0},
    { .name = "set_content_type", .signature = "u", .types = _CWpContentTypeV1SetContentTypeTypes + 0},
};

const wl_interface wp_content_type_v1_interface = {
    .name = "wp_content_type_v1", .version = 1,
    .method_count = 2, .methods = _CWpContentTypeV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpContentTypeV1::CWpContentTypeV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_content_type_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpContentTypeV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpContentTypeV1VTable, this, nullptr);
}

CWpContentTypeV1::~CWpContentTypeV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpContentTypeV1::onDestroyCalled() {
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

void CWpContentTypeV1::setDestroy(F<void(CWpContentTypeV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpContentTypeV1::setSetContentType(F<void(CWpContentTypeV1*, wpContentTypeV1Type)> &&handler) {
    requests.setContentType = std::move(handler);
}

#undef F

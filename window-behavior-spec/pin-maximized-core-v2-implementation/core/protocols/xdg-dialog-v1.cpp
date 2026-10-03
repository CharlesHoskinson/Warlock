// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// xdg_dialog_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2023 Carlos Garnacho

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
#include "xdg-dialog-v1.hpp"
#undef private
#define F std::function

static const wl_interface* xdgDialogV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface xdg_wm_dialog_v1_interface;
extern const wl_interface xdg_dialog_v1_interface;
extern const wl_interface xdg_toplevel_interface;

static void _CXdgWmDialogV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgWmDialogV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CXdgWmDialogV1GetXdgDialog(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* toplevel) {
    const auto PO = (CXdgWmDialogV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getXdgDialog)
        PO->requests.getXdgDialog(PO, id, toplevel);
}

static void _CXdgWmDialogV1__DestroyListener(wl_listener* l, void* d) {
    CXdgWmDialogV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CXdgWmDialogV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CXdgWmDialogV1VTable[] = {
    (void*)_CXdgWmDialogV1Destroy,
    (void*)_CXdgWmDialogV1GetXdgDialog,
};
static const wl_interface* _CXdgWmDialogV1GetXdgDialogTypes[] = {
    &xdg_dialog_v1_interface,
    &xdg_toplevel_interface,
};

static const wl_message _CXdgWmDialogV1Requests[] = {
    { .name = "destroy", .signature = "", .types = xdgDialogV1_dummyTypes + 0},
    { .name = "get_xdg_dialog", .signature = "no", .types = _CXdgWmDialogV1GetXdgDialogTypes + 0},
};

const wl_interface xdg_wm_dialog_v1_interface = {
    .name = "xdg_wm_dialog_v1", .version = 1,
    .method_count = 2, .methods = _CXdgWmDialogV1Requests,
    .event_count = 0, .events = nullptr,
};

CXdgWmDialogV1::CXdgWmDialogV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &xdg_wm_dialog_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CXdgWmDialogV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CXdgWmDialogV1VTable, this, nullptr);
}

CXdgWmDialogV1::~CXdgWmDialogV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CXdgWmDialogV1::onDestroyCalled() {
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

void CXdgWmDialogV1::setDestroy(F<void(CXdgWmDialogV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CXdgWmDialogV1::setGetXdgDialog(F<void(CXdgWmDialogV1*, uint32_t, wl_resource*)> &&handler) {
    requests.getXdgDialog = std::move(handler);
}

static void _CXdgDialogV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgDialogV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CXdgDialogV1SetModal(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgDialogV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setModal)
        PO->requests.setModal(PO);
}

static void _CXdgDialogV1UnsetModal(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgDialogV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.unsetModal)
        PO->requests.unsetModal(PO);
}

static void _CXdgDialogV1__DestroyListener(wl_listener* l, void* d) {
    CXdgDialogV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CXdgDialogV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CXdgDialogV1VTable[] = {
    (void*)_CXdgDialogV1Destroy,
    (void*)_CXdgDialogV1SetModal,
    (void*)_CXdgDialogV1UnsetModal,
};

static const wl_message _CXdgDialogV1Requests[] = {
    { .name = "destroy", .signature = "", .types = xdgDialogV1_dummyTypes + 0},
    { .name = "set_modal", .signature = "", .types = xdgDialogV1_dummyTypes + 0},
    { .name = "unset_modal", .signature = "", .types = xdgDialogV1_dummyTypes + 0},
};

const wl_interface xdg_dialog_v1_interface = {
    .name = "xdg_dialog_v1", .version = 1,
    .method_count = 3, .methods = _CXdgDialogV1Requests,
    .event_count = 0, .events = nullptr,
};

CXdgDialogV1::CXdgDialogV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &xdg_dialog_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CXdgDialogV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CXdgDialogV1VTable, this, nullptr);
}

CXdgDialogV1::~CXdgDialogV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CXdgDialogV1::onDestroyCalled() {
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

void CXdgDialogV1::setDestroy(F<void(CXdgDialogV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CXdgDialogV1::setSetModal(F<void(CXdgDialogV1*)> &&handler) {
    requests.setModal = std::move(handler);
}

void CXdgDialogV1::setUnsetModal(F<void(CXdgDialogV1*)> &&handler) {
    requests.unsetModal = std::move(handler);
}

#undef F

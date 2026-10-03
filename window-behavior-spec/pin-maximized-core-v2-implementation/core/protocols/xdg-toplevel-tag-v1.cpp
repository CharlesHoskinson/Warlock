// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// xdg_toplevel_tag_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2024 Xaver Hugl

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
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
  
*/

#define private public
#define HYPRWAYLAND_SCANNER_NO_INTERFACES
#include "xdg-toplevel-tag-v1.hpp"
#undef private
#define F std::function

static const wl_interface* xdgToplevelTagV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface xdg_toplevel_tag_manager_v1_interface;
extern const wl_interface xdg_toplevel_interface;

static void _CXdgToplevelTagManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgToplevelTagManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CXdgToplevelTagManagerV1SetToplevelTag(wl_client* client, wl_resource* resource, wl_resource* toplevel, const char* tag) {
    const auto PO = (CXdgToplevelTagManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setToplevelTag)
        PO->requests.setToplevelTag(PO, toplevel, tag);
}

static void _CXdgToplevelTagManagerV1SetToplevelDescription(wl_client* client, wl_resource* resource, wl_resource* toplevel, const char* description) {
    const auto PO = (CXdgToplevelTagManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setToplevelDescription)
        PO->requests.setToplevelDescription(PO, toplevel, description);
}

static void _CXdgToplevelTagManagerV1__DestroyListener(wl_listener* l, void* d) {
    CXdgToplevelTagManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CXdgToplevelTagManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CXdgToplevelTagManagerV1VTable[] = {
    (void*)_CXdgToplevelTagManagerV1Destroy,
    (void*)_CXdgToplevelTagManagerV1SetToplevelTag,
    (void*)_CXdgToplevelTagManagerV1SetToplevelDescription,
};
static const wl_interface* _CXdgToplevelTagManagerV1SetToplevelTagTypes[] = {
    &xdg_toplevel_interface,
    nullptr,
};
static const wl_interface* _CXdgToplevelTagManagerV1SetToplevelDescriptionTypes[] = {
    &xdg_toplevel_interface,
    nullptr,
};

static const wl_message _CXdgToplevelTagManagerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = xdgToplevelTagV1_dummyTypes + 0},
    { .name = "set_toplevel_tag", .signature = "os", .types = _CXdgToplevelTagManagerV1SetToplevelTagTypes + 0},
    { .name = "set_toplevel_description", .signature = "os", .types = _CXdgToplevelTagManagerV1SetToplevelDescriptionTypes + 0},
};

const wl_interface xdg_toplevel_tag_manager_v1_interface = {
    .name = "xdg_toplevel_tag_manager_v1", .version = 1,
    .method_count = 3, .methods = _CXdgToplevelTagManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CXdgToplevelTagManagerV1::CXdgToplevelTagManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &xdg_toplevel_tag_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CXdgToplevelTagManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CXdgToplevelTagManagerV1VTable, this, nullptr);
}

CXdgToplevelTagManagerV1::~CXdgToplevelTagManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CXdgToplevelTagManagerV1::onDestroyCalled() {
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

void CXdgToplevelTagManagerV1::setDestroy(F<void(CXdgToplevelTagManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CXdgToplevelTagManagerV1::setSetToplevelTag(F<void(CXdgToplevelTagManagerV1*, wl_resource*, const char*)> &&handler) {
    requests.setToplevelTag = std::move(handler);
}

void CXdgToplevelTagManagerV1::setSetToplevelDescription(F<void(CXdgToplevelTagManagerV1*, wl_resource*, const char*)> &&handler) {
    requests.setToplevelDescription = std::move(handler);
}

#undef F

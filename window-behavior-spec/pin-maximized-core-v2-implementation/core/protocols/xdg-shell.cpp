// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// xdg_shell

/*
 This protocol's authors' copyright notice is:


    Copyright © 2008-2013 Kristian Høgsberg
    Copyright © 2013      Rafael Antognolli
    Copyright © 2013      Jasper St. Pierre
    Copyright © 2010-2013 Intel Corporation
    Copyright © 2015-2017 Samsung Electronics Co., Ltd
    Copyright © 2015-2017 Red Hat Inc.

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
#include "xdg-shell.hpp"
#undef private
#define F std::function

static const wl_interface* xdgShell_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface xdg_wm_base_interface;
extern const wl_interface xdg_positioner_interface;
extern const wl_interface xdg_surface_interface;
extern const wl_interface xdg_toplevel_interface;
extern const wl_interface xdg_popup_interface;
extern const wl_interface wl_surface_interface;
extern const wl_interface wl_seat_interface;
extern const wl_interface wl_output_interface;

static void _CXdgWmBaseDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgWmBase*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CXdgWmBaseCreatePositioner(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CXdgWmBase*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createPositioner)
        PO->requests.createPositioner(PO, id);
}

static void _CXdgWmBaseGetXdgSurface(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CXdgWmBase*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getXdgSurface)
        PO->requests.getXdgSurface(PO, id, surface);
}

static void _CXdgWmBasePong(wl_client* client, wl_resource* resource, uint32_t serial) {
    const auto PO = (CXdgWmBase*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.pong)
        PO->requests.pong(PO, serial);
}

static void _CXdgWmBase__DestroyListener(wl_listener* l, void* d) {
    CXdgWmBaseDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CXdgWmBase* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CXdgWmBaseVTable[] = {
    (void*)_CXdgWmBaseDestroy,
    (void*)_CXdgWmBaseCreatePositioner,
    (void*)_CXdgWmBaseGetXdgSurface,
    (void*)_CXdgWmBasePong,
};

void CXdgWmBase::sendPing(uint32_t serial) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial);
}

void CXdgWmBase::sendPingRaw(uint32_t serial) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial);
}
static const wl_interface* _CXdgWmBaseCreatePositionerTypes[] = {
    &xdg_positioner_interface,
};
static const wl_interface* _CXdgWmBaseGetXdgSurfaceTypes[] = {
    &xdg_surface_interface,
    &wl_surface_interface,
};
static const wl_interface* _CXdgWmBasePongTypes[] = {
    nullptr,
};
static const wl_interface* _CXdgWmBasePingTypes[] = {
    nullptr,
};

static const wl_message _CXdgWmBaseRequests[] = {
    { .name = "destroy", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "create_positioner", .signature = "n", .types = _CXdgWmBaseCreatePositionerTypes + 0},
    { .name = "get_xdg_surface", .signature = "no", .types = _CXdgWmBaseGetXdgSurfaceTypes + 0},
    { .name = "pong", .signature = "u", .types = _CXdgWmBasePongTypes + 0},
};

static const wl_message _CXdgWmBaseEvents[] = {
    { .name = "ping", .signature = "u", .types = _CXdgWmBasePingTypes + 0},
};

const wl_interface xdg_wm_base_interface = {
    .name = "xdg_wm_base", .version = 7,
    .method_count = 4, .methods = _CXdgWmBaseRequests,
    .event_count = 1, .events = _CXdgWmBaseEvents,
};

CXdgWmBase::CXdgWmBase(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &xdg_wm_base_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CXdgWmBase__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CXdgWmBaseVTable, this, nullptr);
}

CXdgWmBase::~CXdgWmBase() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CXdgWmBase::onDestroyCalled() {
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

void CXdgWmBase::setDestroy(F<void(CXdgWmBase*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CXdgWmBase::setCreatePositioner(F<void(CXdgWmBase*, uint32_t)> &&handler) {
    requests.createPositioner = std::move(handler);
}

void CXdgWmBase::setGetXdgSurface(F<void(CXdgWmBase*, uint32_t, wl_resource*)> &&handler) {
    requests.getXdgSurface = std::move(handler);
}

void CXdgWmBase::setPong(F<void(CXdgWmBase*, uint32_t)> &&handler) {
    requests.pong = std::move(handler);
}

static void _CXdgPositionerDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CXdgPositionerSetSize(wl_client* client, wl_resource* resource, int32_t width, int32_t height) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setSize)
        PO->requests.setSize(PO, width, height);
}

static void _CXdgPositionerSetAnchorRect(wl_client* client, wl_resource* resource, int32_t x, int32_t y, int32_t width, int32_t height) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setAnchorRect)
        PO->requests.setAnchorRect(PO, x, y, width, height);
}

static void _CXdgPositionerSetAnchor(wl_client* client, wl_resource* resource, xdgPositionerAnchor anchor) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setAnchor)
        PO->requests.setAnchor(PO, anchor);
}

static void _CXdgPositionerSetGravity(wl_client* client, wl_resource* resource, xdgPositionerGravity gravity) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setGravity)
        PO->requests.setGravity(PO, gravity);
}

static void _CXdgPositionerSetConstraintAdjustment(wl_client* client, wl_resource* resource, xdgPositionerConstraintAdjustment constraint_adjustment) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setConstraintAdjustment)
        PO->requests.setConstraintAdjustment(PO, constraint_adjustment);
}

static void _CXdgPositionerSetOffset(wl_client* client, wl_resource* resource, int32_t x, int32_t y) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setOffset)
        PO->requests.setOffset(PO, x, y);
}

static void _CXdgPositionerSetReactive(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setReactive)
        PO->requests.setReactive(PO);
}

static void _CXdgPositionerSetParentSize(wl_client* client, wl_resource* resource, int32_t parent_width, int32_t parent_height) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setParentSize)
        PO->requests.setParentSize(PO, parent_width, parent_height);
}

static void _CXdgPositionerSetParentConfigure(wl_client* client, wl_resource* resource, uint32_t serial) {
    const auto PO = (CXdgPositioner*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setParentConfigure)
        PO->requests.setParentConfigure(PO, serial);
}

static void _CXdgPositioner__DestroyListener(wl_listener* l, void* d) {
    CXdgPositionerDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CXdgPositioner* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CXdgPositionerVTable[] = {
    (void*)_CXdgPositionerDestroy,
    (void*)_CXdgPositionerSetSize,
    (void*)_CXdgPositionerSetAnchorRect,
    (void*)_CXdgPositionerSetAnchor,
    (void*)_CXdgPositionerSetGravity,
    (void*)_CXdgPositionerSetConstraintAdjustment,
    (void*)_CXdgPositionerSetOffset,
    (void*)_CXdgPositionerSetReactive,
    (void*)_CXdgPositionerSetParentSize,
    (void*)_CXdgPositionerSetParentConfigure,
};
static const wl_interface* _CXdgPositionerSetSizeTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgPositionerSetAnchorRectTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgPositionerSetAnchorTypes[] = {
    nullptr,
};
static const wl_interface* _CXdgPositionerSetGravityTypes[] = {
    nullptr,
};
static const wl_interface* _CXdgPositionerSetConstraintAdjustmentTypes[] = {
    nullptr,
};
static const wl_interface* _CXdgPositionerSetOffsetTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgPositionerSetParentSizeTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgPositionerSetParentConfigureTypes[] = {
    nullptr,
};

static const wl_message _CXdgPositionerRequests[] = {
    { .name = "destroy", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "set_size", .signature = "ii", .types = _CXdgPositionerSetSizeTypes + 0},
    { .name = "set_anchor_rect", .signature = "iiii", .types = _CXdgPositionerSetAnchorRectTypes + 0},
    { .name = "set_anchor", .signature = "u", .types = _CXdgPositionerSetAnchorTypes + 0},
    { .name = "set_gravity", .signature = "u", .types = _CXdgPositionerSetGravityTypes + 0},
    { .name = "set_constraint_adjustment", .signature = "u", .types = _CXdgPositionerSetConstraintAdjustmentTypes + 0},
    { .name = "set_offset", .signature = "ii", .types = _CXdgPositionerSetOffsetTypes + 0},
    { .name = "set_reactive", .signature = "3", .types = xdgShell_dummyTypes + 0},
    { .name = "set_parent_size", .signature = "3ii", .types = _CXdgPositionerSetParentSizeTypes + 0},
    { .name = "set_parent_configure", .signature = "3u", .types = _CXdgPositionerSetParentConfigureTypes + 0},
};

const wl_interface xdg_positioner_interface = {
    .name = "xdg_positioner", .version = 7,
    .method_count = 10, .methods = _CXdgPositionerRequests,
    .event_count = 0, .events = nullptr,
};

CXdgPositioner::CXdgPositioner(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &xdg_positioner_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CXdgPositioner__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CXdgPositionerVTable, this, nullptr);
}

CXdgPositioner::~CXdgPositioner() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CXdgPositioner::onDestroyCalled() {
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

void CXdgPositioner::setDestroy(F<void(CXdgPositioner*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CXdgPositioner::setSetSize(F<void(CXdgPositioner*, int32_t, int32_t)> &&handler) {
    requests.setSize = std::move(handler);
}

void CXdgPositioner::setSetAnchorRect(F<void(CXdgPositioner*, int32_t, int32_t, int32_t, int32_t)> &&handler) {
    requests.setAnchorRect = std::move(handler);
}

void CXdgPositioner::setSetAnchor(F<void(CXdgPositioner*, xdgPositionerAnchor)> &&handler) {
    requests.setAnchor = std::move(handler);
}

void CXdgPositioner::setSetGravity(F<void(CXdgPositioner*, xdgPositionerGravity)> &&handler) {
    requests.setGravity = std::move(handler);
}

void CXdgPositioner::setSetConstraintAdjustment(F<void(CXdgPositioner*, xdgPositionerConstraintAdjustment)> &&handler) {
    requests.setConstraintAdjustment = std::move(handler);
}

void CXdgPositioner::setSetOffset(F<void(CXdgPositioner*, int32_t, int32_t)> &&handler) {
    requests.setOffset = std::move(handler);
}

void CXdgPositioner::setSetReactive(F<void(CXdgPositioner*)> &&handler) {
    requests.setReactive = std::move(handler);
}

void CXdgPositioner::setSetParentSize(F<void(CXdgPositioner*, int32_t, int32_t)> &&handler) {
    requests.setParentSize = std::move(handler);
}

void CXdgPositioner::setSetParentConfigure(F<void(CXdgPositioner*, uint32_t)> &&handler) {
    requests.setParentConfigure = std::move(handler);
}

static void _CXdgSurfaceDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CXdgSurfaceGetToplevel(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CXdgSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getToplevel)
        PO->requests.getToplevel(PO, id);
}

static void _CXdgSurfaceGetPopup(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* parent, wl_resource* positioner) {
    const auto PO = (CXdgSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getPopup)
        PO->requests.getPopup(PO, id, parent, positioner);
}

static void _CXdgSurfaceSetWindowGeometry(wl_client* client, wl_resource* resource, int32_t x, int32_t y, int32_t width, int32_t height) {
    const auto PO = (CXdgSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setWindowGeometry)
        PO->requests.setWindowGeometry(PO, x, y, width, height);
}

static void _CXdgSurfaceAckConfigure(wl_client* client, wl_resource* resource, uint32_t serial) {
    const auto PO = (CXdgSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.ackConfigure)
        PO->requests.ackConfigure(PO, serial);
}

static void _CXdgSurface__DestroyListener(wl_listener* l, void* d) {
    CXdgSurfaceDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CXdgSurface* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CXdgSurfaceVTable[] = {
    (void*)_CXdgSurfaceDestroy,
    (void*)_CXdgSurfaceGetToplevel,
    (void*)_CXdgSurfaceGetPopup,
    (void*)_CXdgSurfaceSetWindowGeometry,
    (void*)_CXdgSurfaceAckConfigure,
};

void CXdgSurface::sendConfigure(uint32_t serial) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial);
}

void CXdgSurface::sendConfigureRaw(uint32_t serial) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial);
}
static const wl_interface* _CXdgSurfaceGetToplevelTypes[] = {
    &xdg_toplevel_interface,
};
static const wl_interface* _CXdgSurfaceGetPopupTypes[] = {
    &xdg_popup_interface,
    &xdg_surface_interface,
    &xdg_positioner_interface,
};
static const wl_interface* _CXdgSurfaceSetWindowGeometryTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgSurfaceAckConfigureTypes[] = {
    nullptr,
};
static const wl_interface* _CXdgSurfaceConfigureTypes[] = {
    nullptr,
};

static const wl_message _CXdgSurfaceRequests[] = {
    { .name = "destroy", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "get_toplevel", .signature = "n", .types = _CXdgSurfaceGetToplevelTypes + 0},
    { .name = "get_popup", .signature = "n?oo", .types = _CXdgSurfaceGetPopupTypes + 0},
    { .name = "set_window_geometry", .signature = "iiii", .types = _CXdgSurfaceSetWindowGeometryTypes + 0},
    { .name = "ack_configure", .signature = "u", .types = _CXdgSurfaceAckConfigureTypes + 0},
};

static const wl_message _CXdgSurfaceEvents[] = {
    { .name = "configure", .signature = "u", .types = _CXdgSurfaceConfigureTypes + 0},
};

const wl_interface xdg_surface_interface = {
    .name = "xdg_surface", .version = 7,
    .method_count = 5, .methods = _CXdgSurfaceRequests,
    .event_count = 1, .events = _CXdgSurfaceEvents,
};

CXdgSurface::CXdgSurface(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &xdg_surface_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CXdgSurface__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CXdgSurfaceVTable, this, nullptr);
}

CXdgSurface::~CXdgSurface() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CXdgSurface::onDestroyCalled() {
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

void CXdgSurface::setDestroy(F<void(CXdgSurface*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CXdgSurface::setGetToplevel(F<void(CXdgSurface*, uint32_t)> &&handler) {
    requests.getToplevel = std::move(handler);
}

void CXdgSurface::setGetPopup(F<void(CXdgSurface*, uint32_t, wl_resource*, wl_resource*)> &&handler) {
    requests.getPopup = std::move(handler);
}

void CXdgSurface::setSetWindowGeometry(F<void(CXdgSurface*, int32_t, int32_t, int32_t, int32_t)> &&handler) {
    requests.setWindowGeometry = std::move(handler);
}

void CXdgSurface::setAckConfigure(F<void(CXdgSurface*, uint32_t)> &&handler) {
    requests.ackConfigure = std::move(handler);
}

static void _CXdgToplevelDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CXdgToplevelSetParent(wl_client* client, wl_resource* resource, wl_resource* parent) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setParent)
        PO->requests.setParent(PO, parent);
}

static void _CXdgToplevelSetTitle(wl_client* client, wl_resource* resource, const char* title) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setTitle)
        PO->requests.setTitle(PO, title);
}

static void _CXdgToplevelSetAppId(wl_client* client, wl_resource* resource, const char* app_id) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setAppId)
        PO->requests.setAppId(PO, app_id);
}

static void _CXdgToplevelShowWindowMenu(wl_client* client, wl_resource* resource, wl_resource* seat, uint32_t serial, int32_t x, int32_t y) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.showWindowMenu)
        PO->requests.showWindowMenu(PO, seat, serial, x, y);
}

static void _CXdgToplevelMove(wl_client* client, wl_resource* resource, wl_resource* seat, uint32_t serial) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.move)
        PO->requests.move(PO, seat, serial);
}

static void _CXdgToplevelResize(wl_client* client, wl_resource* resource, wl_resource* seat, uint32_t serial, xdgToplevelResizeEdge edges) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.resize)
        PO->requests.resize(PO, seat, serial, edges);
}

static void _CXdgToplevelSetMaxSize(wl_client* client, wl_resource* resource, int32_t width, int32_t height) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setMaxSize)
        PO->requests.setMaxSize(PO, width, height);
}

static void _CXdgToplevelSetMinSize(wl_client* client, wl_resource* resource, int32_t width, int32_t height) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setMinSize)
        PO->requests.setMinSize(PO, width, height);
}

static void _CXdgToplevelSetMaximized(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setMaximized)
        PO->requests.setMaximized(PO);
}

static void _CXdgToplevelUnsetMaximized(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.unsetMaximized)
        PO->requests.unsetMaximized(PO);
}

static void _CXdgToplevelSetFullscreen(wl_client* client, wl_resource* resource, wl_resource* output) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setFullscreen)
        PO->requests.setFullscreen(PO, output);
}

static void _CXdgToplevelUnsetFullscreen(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.unsetFullscreen)
        PO->requests.unsetFullscreen(PO);
}

static void _CXdgToplevelSetMinimized(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgToplevel*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setMinimized)
        PO->requests.setMinimized(PO);
}

static void _CXdgToplevel__DestroyListener(wl_listener* l, void* d) {
    CXdgToplevelDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CXdgToplevel* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CXdgToplevelVTable[] = {
    (void*)_CXdgToplevelDestroy,
    (void*)_CXdgToplevelSetParent,
    (void*)_CXdgToplevelSetTitle,
    (void*)_CXdgToplevelSetAppId,
    (void*)_CXdgToplevelShowWindowMenu,
    (void*)_CXdgToplevelMove,
    (void*)_CXdgToplevelResize,
    (void*)_CXdgToplevelSetMaxSize,
    (void*)_CXdgToplevelSetMinSize,
    (void*)_CXdgToplevelSetMaximized,
    (void*)_CXdgToplevelUnsetMaximized,
    (void*)_CXdgToplevelSetFullscreen,
    (void*)_CXdgToplevelUnsetFullscreen,
    (void*)_CXdgToplevelSetMinimized,
};

void CXdgToplevel::sendConfigure(int32_t width, int32_t height, wl_array* states) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, width, height, states);
}

void CXdgToplevel::sendClose() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CXdgToplevel::sendConfigureBounds(int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, width, height);
}

void CXdgToplevel::sendWmCapabilities(wl_array* capabilities) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, capabilities);
}

void CXdgToplevel::sendConfigureRaw(int32_t width, int32_t height, wl_array* states) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, width, height, states);
}

void CXdgToplevel::sendCloseRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CXdgToplevel::sendConfigureBoundsRaw(int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, width, height);
}

void CXdgToplevel::sendWmCapabilitiesRaw(wl_array* capabilities) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, capabilities);
}
static const wl_interface* _CXdgToplevelSetParentTypes[] = {
    &xdg_toplevel_interface,
};
static const wl_interface* _CXdgToplevelSetTitleTypes[] = {
    nullptr,
};
static const wl_interface* _CXdgToplevelSetAppIdTypes[] = {
    nullptr,
};
static const wl_interface* _CXdgToplevelShowWindowMenuTypes[] = {
    &wl_seat_interface,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgToplevelMoveTypes[] = {
    &wl_seat_interface,
    nullptr,
};
static const wl_interface* _CXdgToplevelResizeTypes[] = {
    &wl_seat_interface,
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgToplevelSetMaxSizeTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgToplevelSetMinSizeTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgToplevelSetFullscreenTypes[] = {
    &wl_output_interface,
};
static const wl_interface* _CXdgToplevelConfigureTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgToplevelConfigureBoundsTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgToplevelWmCapabilitiesTypes[] = {
    nullptr,
};

static const wl_message _CXdgToplevelRequests[] = {
    { .name = "destroy", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "set_parent", .signature = "?o", .types = _CXdgToplevelSetParentTypes + 0},
    { .name = "set_title", .signature = "s", .types = _CXdgToplevelSetTitleTypes + 0},
    { .name = "set_app_id", .signature = "s", .types = _CXdgToplevelSetAppIdTypes + 0},
    { .name = "show_window_menu", .signature = "ouii", .types = _CXdgToplevelShowWindowMenuTypes + 0},
    { .name = "move", .signature = "ou", .types = _CXdgToplevelMoveTypes + 0},
    { .name = "resize", .signature = "ouu", .types = _CXdgToplevelResizeTypes + 0},
    { .name = "set_max_size", .signature = "ii", .types = _CXdgToplevelSetMaxSizeTypes + 0},
    { .name = "set_min_size", .signature = "ii", .types = _CXdgToplevelSetMinSizeTypes + 0},
    { .name = "set_maximized", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "unset_maximized", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "set_fullscreen", .signature = "?o", .types = _CXdgToplevelSetFullscreenTypes + 0},
    { .name = "unset_fullscreen", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "set_minimized", .signature = "", .types = xdgShell_dummyTypes + 0},
};

static const wl_message _CXdgToplevelEvents[] = {
    { .name = "configure", .signature = "iia", .types = _CXdgToplevelConfigureTypes + 0},
    { .name = "close", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "configure_bounds", .signature = "4ii", .types = _CXdgToplevelConfigureBoundsTypes + 0},
    { .name = "wm_capabilities", .signature = "5a", .types = _CXdgToplevelWmCapabilitiesTypes + 0},
};

const wl_interface xdg_toplevel_interface = {
    .name = "xdg_toplevel", .version = 7,
    .method_count = 14, .methods = _CXdgToplevelRequests,
    .event_count = 4, .events = _CXdgToplevelEvents,
};

CXdgToplevel::CXdgToplevel(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &xdg_toplevel_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CXdgToplevel__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CXdgToplevelVTable, this, nullptr);
}

CXdgToplevel::~CXdgToplevel() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CXdgToplevel::onDestroyCalled() {
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

void CXdgToplevel::setDestroy(F<void(CXdgToplevel*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CXdgToplevel::setSetParent(F<void(CXdgToplevel*, wl_resource*)> &&handler) {
    requests.setParent = std::move(handler);
}

void CXdgToplevel::setSetTitle(F<void(CXdgToplevel*, const char*)> &&handler) {
    requests.setTitle = std::move(handler);
}

void CXdgToplevel::setSetAppId(F<void(CXdgToplevel*, const char*)> &&handler) {
    requests.setAppId = std::move(handler);
}

void CXdgToplevel::setShowWindowMenu(F<void(CXdgToplevel*, wl_resource*, uint32_t, int32_t, int32_t)> &&handler) {
    requests.showWindowMenu = std::move(handler);
}

void CXdgToplevel::setMove(F<void(CXdgToplevel*, wl_resource*, uint32_t)> &&handler) {
    requests.move = std::move(handler);
}

void CXdgToplevel::setResize(F<void(CXdgToplevel*, wl_resource*, uint32_t, xdgToplevelResizeEdge)> &&handler) {
    requests.resize = std::move(handler);
}

void CXdgToplevel::setSetMaxSize(F<void(CXdgToplevel*, int32_t, int32_t)> &&handler) {
    requests.setMaxSize = std::move(handler);
}

void CXdgToplevel::setSetMinSize(F<void(CXdgToplevel*, int32_t, int32_t)> &&handler) {
    requests.setMinSize = std::move(handler);
}

void CXdgToplevel::setSetMaximized(F<void(CXdgToplevel*)> &&handler) {
    requests.setMaximized = std::move(handler);
}

void CXdgToplevel::setUnsetMaximized(F<void(CXdgToplevel*)> &&handler) {
    requests.unsetMaximized = std::move(handler);
}

void CXdgToplevel::setSetFullscreen(F<void(CXdgToplevel*, wl_resource*)> &&handler) {
    requests.setFullscreen = std::move(handler);
}

void CXdgToplevel::setUnsetFullscreen(F<void(CXdgToplevel*)> &&handler) {
    requests.unsetFullscreen = std::move(handler);
}

void CXdgToplevel::setSetMinimized(F<void(CXdgToplevel*)> &&handler) {
    requests.setMinimized = std::move(handler);
}

static void _CXdgPopupDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CXdgPopup*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CXdgPopupGrab(wl_client* client, wl_resource* resource, wl_resource* seat, uint32_t serial) {
    const auto PO = (CXdgPopup*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.grab)
        PO->requests.grab(PO, seat, serial);
}

static void _CXdgPopupReposition(wl_client* client, wl_resource* resource, wl_resource* positioner, uint32_t token) {
    const auto PO = (CXdgPopup*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.reposition)
        PO->requests.reposition(PO, positioner, token);
}

static void _CXdgPopup__DestroyListener(wl_listener* l, void* d) {
    CXdgPopupDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CXdgPopup* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CXdgPopupVTable[] = {
    (void*)_CXdgPopupDestroy,
    (void*)_CXdgPopupGrab,
    (void*)_CXdgPopupReposition,
};

void CXdgPopup::sendConfigure(int32_t x, int32_t y, int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, x, y, width, height);
}

void CXdgPopup::sendPopupDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CXdgPopup::sendRepositioned(uint32_t token) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, token);
}

void CXdgPopup::sendConfigureRaw(int32_t x, int32_t y, int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, x, y, width, height);
}

void CXdgPopup::sendPopupDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CXdgPopup::sendRepositionedRaw(uint32_t token) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, token);
}
static const wl_interface* _CXdgPopupGrabTypes[] = {
    &wl_seat_interface,
    nullptr,
};
static const wl_interface* _CXdgPopupRepositionTypes[] = {
    &xdg_positioner_interface,
    nullptr,
};
static const wl_interface* _CXdgPopupConfigureTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CXdgPopupRepositionedTypes[] = {
    nullptr,
};

static const wl_message _CXdgPopupRequests[] = {
    { .name = "destroy", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "grab", .signature = "ou", .types = _CXdgPopupGrabTypes + 0},
    { .name = "reposition", .signature = "3ou", .types = _CXdgPopupRepositionTypes + 0},
};

static const wl_message _CXdgPopupEvents[] = {
    { .name = "configure", .signature = "iiii", .types = _CXdgPopupConfigureTypes + 0},
    { .name = "popup_done", .signature = "", .types = xdgShell_dummyTypes + 0},
    { .name = "repositioned", .signature = "3u", .types = _CXdgPopupRepositionedTypes + 0},
};

const wl_interface xdg_popup_interface = {
    .name = "xdg_popup", .version = 7,
    .method_count = 3, .methods = _CXdgPopupRequests,
    .event_count = 3, .events = _CXdgPopupEvents,
};

CXdgPopup::CXdgPopup(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &xdg_popup_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CXdgPopup__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CXdgPopupVTable, this, nullptr);
}

CXdgPopup::~CXdgPopup() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CXdgPopup::onDestroyCalled() {
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

void CXdgPopup::setDestroy(F<void(CXdgPopup*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CXdgPopup::setGrab(F<void(CXdgPopup*, wl_resource*, uint32_t)> &&handler) {
    requests.grab = std::move(handler);
}

void CXdgPopup::setReposition(F<void(CXdgPopup*, wl_resource*, uint32_t)> &&handler) {
    requests.reposition = std::move(handler);
}

#undef F

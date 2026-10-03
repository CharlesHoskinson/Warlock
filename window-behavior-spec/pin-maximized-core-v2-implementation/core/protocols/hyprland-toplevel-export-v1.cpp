// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// hyprland_toplevel_export_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2022 Vaxry
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    3. Neither the name of the copyright holder nor the names of its
       contributors may be used to endorse or promote products derived from
       this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  
*/

#define private public
#define HYPRWAYLAND_SCANNER_NO_INTERFACES
#include "hyprland-toplevel-export-v1.hpp"
#undef private
#define F std::function

static const wl_interface* hyprlandToplevelExportV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface hyprland_toplevel_export_manager_v1_interface;
extern const wl_interface hyprland_toplevel_export_frame_v1_interface;
extern const wl_interface zwlr_foreign_toplevel_handle_v1_interface;
extern const wl_interface wl_buffer_interface;

static void _CHyprlandToplevelExportManagerV1CaptureToplevel(wl_client* client, wl_resource* resource, uint32_t frame, int32_t overlay_cursor, uint32_t handle) {
    const auto PO = (CHyprlandToplevelExportManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.captureToplevel)
        PO->requests.captureToplevel(PO, frame, overlay_cursor, handle);
}

static void _CHyprlandToplevelExportManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandToplevelExportManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandToplevelExportManagerV1CaptureToplevelWithWlrToplevelHandle(wl_client* client, wl_resource* resource, uint32_t frame, int32_t overlay_cursor, wl_resource* handle) {
    const auto PO = (CHyprlandToplevelExportManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.captureToplevelWithWlrToplevelHandle)
        PO->requests.captureToplevelWithWlrToplevelHandle(PO, frame, overlay_cursor, handle);
}

static void _CHyprlandToplevelExportManagerV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandToplevelExportManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandToplevelExportManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandToplevelExportManagerV1VTable[] = {
    (void*)_CHyprlandToplevelExportManagerV1CaptureToplevel,
    (void*)_CHyprlandToplevelExportManagerV1Destroy,
    (void*)_CHyprlandToplevelExportManagerV1CaptureToplevelWithWlrToplevelHandle,
};
static const wl_interface* _CHyprlandToplevelExportManagerV1CaptureToplevelTypes[] = {
    &hyprland_toplevel_export_frame_v1_interface,
    nullptr,
    nullptr,
};
static const wl_interface* _CHyprlandToplevelExportManagerV1CaptureToplevelWithWlrToplevelHandleTypes[] = {
    &hyprland_toplevel_export_frame_v1_interface,
    nullptr,
    &zwlr_foreign_toplevel_handle_v1_interface,
};

static const wl_message _CHyprlandToplevelExportManagerV1Requests[] = {
    { .name = "capture_toplevel", .signature = "niu", .types = _CHyprlandToplevelExportManagerV1CaptureToplevelTypes + 0},
    { .name = "destroy", .signature = "", .types = hyprlandToplevelExportV1_dummyTypes + 0},
    { .name = "capture_toplevel_with_wlr_toplevel_handle", .signature = "2nio", .types = _CHyprlandToplevelExportManagerV1CaptureToplevelWithWlrToplevelHandleTypes + 0},
};

const wl_interface hyprland_toplevel_export_manager_v1_interface = {
    .name = "hyprland_toplevel_export_manager_v1", .version = 2,
    .method_count = 3, .methods = _CHyprlandToplevelExportManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CHyprlandToplevelExportManagerV1::CHyprlandToplevelExportManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_toplevel_export_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandToplevelExportManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandToplevelExportManagerV1VTable, this, nullptr);
}

CHyprlandToplevelExportManagerV1::~CHyprlandToplevelExportManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandToplevelExportManagerV1::onDestroyCalled() {
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

void CHyprlandToplevelExportManagerV1::setCaptureToplevel(F<void(CHyprlandToplevelExportManagerV1*, uint32_t, int32_t, uint32_t)> &&handler) {
    requests.captureToplevel = std::move(handler);
}

void CHyprlandToplevelExportManagerV1::setDestroy(F<void(CHyprlandToplevelExportManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CHyprlandToplevelExportManagerV1::setCaptureToplevelWithWlrToplevelHandle(F<void(CHyprlandToplevelExportManagerV1*, uint32_t, int32_t, wl_resource*)> &&handler) {
    requests.captureToplevelWithWlrToplevelHandle = std::move(handler);
}

static void _CHyprlandToplevelExportFrameV1Copy(wl_client* client, wl_resource* resource, wl_resource* buffer, int32_t ignore_damage) {
    const auto PO = (CHyprlandToplevelExportFrameV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.copy)
        PO->requests.copy(PO, buffer, ignore_damage);
}

static void _CHyprlandToplevelExportFrameV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandToplevelExportFrameV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandToplevelExportFrameV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandToplevelExportFrameV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandToplevelExportFrameV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandToplevelExportFrameV1VTable[] = {
    (void*)_CHyprlandToplevelExportFrameV1Copy,
    (void*)_CHyprlandToplevelExportFrameV1Destroy,
};

void CHyprlandToplevelExportFrameV1::sendBuffer(uint32_t format, uint32_t width, uint32_t height, uint32_t stride) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format, width, height, stride);
}

void CHyprlandToplevelExportFrameV1::sendDamage(uint32_t x, uint32_t y, uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, x, y, width, height);
}

void CHyprlandToplevelExportFrameV1::sendFlags(hyprlandToplevelExportFrameV1Flags flags) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, flags);
}

void CHyprlandToplevelExportFrameV1::sendReady(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, tv_sec_hi, tv_sec_lo, tv_nsec);
}

void CHyprlandToplevelExportFrameV1::sendFailed() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CHyprlandToplevelExportFrameV1::sendLinuxDmabuf(uint32_t format, uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, format, width, height);
}

void CHyprlandToplevelExportFrameV1::sendBufferDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6);
}

void CHyprlandToplevelExportFrameV1::sendBufferRaw(uint32_t format, uint32_t width, uint32_t height, uint32_t stride) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format, width, height, stride);
}

void CHyprlandToplevelExportFrameV1::sendDamageRaw(uint32_t x, uint32_t y, uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, x, y, width, height);
}

void CHyprlandToplevelExportFrameV1::sendFlagsRaw(hyprlandToplevelExportFrameV1Flags flags) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, flags);
}

void CHyprlandToplevelExportFrameV1::sendReadyRaw(uint32_t tv_sec_hi, uint32_t tv_sec_lo, uint32_t tv_nsec) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, tv_sec_hi, tv_sec_lo, tv_nsec);
}

void CHyprlandToplevelExportFrameV1::sendFailedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CHyprlandToplevelExportFrameV1::sendLinuxDmabufRaw(uint32_t format, uint32_t width, uint32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, format, width, height);
}

void CHyprlandToplevelExportFrameV1::sendBufferDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6);
}
static const wl_interface* _CHyprlandToplevelExportFrameV1CopyTypes[] = {
    &wl_buffer_interface,
    nullptr,
};
static const wl_interface* _CHyprlandToplevelExportFrameV1BufferTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CHyprlandToplevelExportFrameV1DamageTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CHyprlandToplevelExportFrameV1FlagsTypes[] = {
    nullptr,
};
static const wl_interface* _CHyprlandToplevelExportFrameV1ReadyTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CHyprlandToplevelExportFrameV1LinuxDmabufTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CHyprlandToplevelExportFrameV1Requests[] = {
    { .name = "copy", .signature = "oi", .types = _CHyprlandToplevelExportFrameV1CopyTypes + 0},
    { .name = "destroy", .signature = "", .types = hyprlandToplevelExportV1_dummyTypes + 0},
};

static const wl_message _CHyprlandToplevelExportFrameV1Events[] = {
    { .name = "buffer", .signature = "uuuu", .types = _CHyprlandToplevelExportFrameV1BufferTypes + 0},
    { .name = "damage", .signature = "uuuu", .types = _CHyprlandToplevelExportFrameV1DamageTypes + 0},
    { .name = "flags", .signature = "u", .types = _CHyprlandToplevelExportFrameV1FlagsTypes + 0},
    { .name = "ready", .signature = "uuu", .types = _CHyprlandToplevelExportFrameV1ReadyTypes + 0},
    { .name = "failed", .signature = "", .types = hyprlandToplevelExportV1_dummyTypes + 0},
    { .name = "linux_dmabuf", .signature = "uuu", .types = _CHyprlandToplevelExportFrameV1LinuxDmabufTypes + 0},
    { .name = "buffer_done", .signature = "", .types = hyprlandToplevelExportV1_dummyTypes + 0},
};

const wl_interface hyprland_toplevel_export_frame_v1_interface = {
    .name = "hyprland_toplevel_export_frame_v1", .version = 2,
    .method_count = 2, .methods = _CHyprlandToplevelExportFrameV1Requests,
    .event_count = 7, .events = _CHyprlandToplevelExportFrameV1Events,
};

CHyprlandToplevelExportFrameV1::CHyprlandToplevelExportFrameV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_toplevel_export_frame_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandToplevelExportFrameV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandToplevelExportFrameV1VTable, this, nullptr);
}

CHyprlandToplevelExportFrameV1::~CHyprlandToplevelExportFrameV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandToplevelExportFrameV1::onDestroyCalled() {
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

void CHyprlandToplevelExportFrameV1::setCopy(F<void(CHyprlandToplevelExportFrameV1*, wl_resource*, int32_t)> &&handler) {
    requests.copy = std::move(handler);
}

void CHyprlandToplevelExportFrameV1::setDestroy(F<void(CHyprlandToplevelExportFrameV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

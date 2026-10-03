// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// hyprland_input_capture_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2025 Fl0w

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
#include "hyprland-input-capture-v1.hpp"
#undef private
#define F std::function

static const wl_interface* hyprlandInputCaptureV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface hyprland_input_capture_manager_v1_interface;
extern const wl_interface hyprland_input_capture_v1_interface;

static void _CHyprlandInputCaptureManagerV1CreateSession(wl_client* client, wl_resource* resource, uint32_t session, const char* handle) {
    const auto PO = (CHyprlandInputCaptureManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createSession)
        PO->requests.createSession(PO, session, handle);
}

static void _CHyprlandInputCaptureManagerV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandInputCaptureManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandInputCaptureManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandInputCaptureManagerV1VTable[] = {
    (void*)_CHyprlandInputCaptureManagerV1CreateSession,
};
static const wl_interface* _CHyprlandInputCaptureManagerV1CreateSessionTypes[] = {
    &hyprland_input_capture_v1_interface,
    nullptr,
};

static const wl_message _CHyprlandInputCaptureManagerV1Requests[] = {
    { .name = "create_session", .signature = "ns", .types = _CHyprlandInputCaptureManagerV1CreateSessionTypes + 0},
};

const wl_interface hyprland_input_capture_manager_v1_interface = {
    .name = "hyprland_input_capture_manager_v1", .version = 1,
    .method_count = 1, .methods = _CHyprlandInputCaptureManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CHyprlandInputCaptureManagerV1::CHyprlandInputCaptureManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_input_capture_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandInputCaptureManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandInputCaptureManagerV1VTable, this, nullptr);
}

CHyprlandInputCaptureManagerV1::~CHyprlandInputCaptureManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandInputCaptureManagerV1::onDestroyCalled() {
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

void CHyprlandInputCaptureManagerV1::setCreateSession(F<void(CHyprlandInputCaptureManagerV1*, uint32_t, const char*)> &&handler) {
    requests.createSession = std::move(handler);
}

static void _CHyprlandInputCaptureV1ClearBarriers(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandInputCaptureV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.clearBarriers)
        PO->requests.clearBarriers(PO);
}

static void _CHyprlandInputCaptureV1AddBarrier(wl_client* client, wl_resource* resource, uint32_t zone_set, uint32_t id, uint32_t x1, uint32_t y1, uint32_t x2, uint32_t y2) {
    const auto PO = (CHyprlandInputCaptureV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.addBarrier)
        PO->requests.addBarrier(PO, zone_set, id, x1, y1, x2, y2);
}

static void _CHyprlandInputCaptureV1Enable(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandInputCaptureV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.enable)
        PO->requests.enable(PO);
}

static void _CHyprlandInputCaptureV1Disable(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandInputCaptureV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.disable)
        PO->requests.disable(PO);
}

static void _CHyprlandInputCaptureV1Release(wl_client* client, wl_resource* resource, uint32_t activation_id, wl_fixed_t x, wl_fixed_t y) {
    const auto PO = (CHyprlandInputCaptureV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO, activation_id, x, y);
}

static void _CHyprlandInputCaptureV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandInputCaptureV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandInputCaptureV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandInputCaptureV1VTable[] = {
    (void*)_CHyprlandInputCaptureV1ClearBarriers,
    (void*)_CHyprlandInputCaptureV1AddBarrier,
    (void*)_CHyprlandInputCaptureV1Enable,
    (void*)_CHyprlandInputCaptureV1Disable,
    (void*)_CHyprlandInputCaptureV1Release,
};

void CHyprlandInputCaptureV1::sendEisFd(int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, fd);
}

void CHyprlandInputCaptureV1::sendDisabled() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CHyprlandInputCaptureV1::sendActivated(uint32_t activation_id, wl_fixed_t x, wl_fixed_t y, uint32_t barrier_id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, activation_id, x, y, barrier_id);
}

void CHyprlandInputCaptureV1::sendDeactivated(uint32_t activation_id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, activation_id);
}

void CHyprlandInputCaptureV1::sendEisFdRaw(int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, fd);
}

void CHyprlandInputCaptureV1::sendDisabledRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CHyprlandInputCaptureV1::sendActivatedRaw(uint32_t activation_id, wl_fixed_t x, wl_fixed_t y, uint32_t barrier_id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, activation_id, x, y, barrier_id);
}

void CHyprlandInputCaptureV1::sendDeactivatedRaw(uint32_t activation_id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, activation_id);
}
static const wl_interface* _CHyprlandInputCaptureV1AddBarrierTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CHyprlandInputCaptureV1ReleaseTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CHyprlandInputCaptureV1EisFdTypes[] = {
    nullptr,
};
static const wl_interface* _CHyprlandInputCaptureV1ActivatedTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CHyprlandInputCaptureV1DeactivatedTypes[] = {
    nullptr,
};

static const wl_message _CHyprlandInputCaptureV1Requests[] = {
    { .name = "clear_barriers", .signature = "", .types = hyprlandInputCaptureV1_dummyTypes + 0},
    { .name = "add_barrier", .signature = "uuuuuu", .types = _CHyprlandInputCaptureV1AddBarrierTypes + 0},
    { .name = "enable", .signature = "", .types = hyprlandInputCaptureV1_dummyTypes + 0},
    { .name = "disable", .signature = "", .types = hyprlandInputCaptureV1_dummyTypes + 0},
    { .name = "release", .signature = "uff", .types = _CHyprlandInputCaptureV1ReleaseTypes + 0},
};

static const wl_message _CHyprlandInputCaptureV1Events[] = {
    { .name = "eis_fd", .signature = "h", .types = _CHyprlandInputCaptureV1EisFdTypes + 0},
    { .name = "disabled", .signature = "", .types = hyprlandInputCaptureV1_dummyTypes + 0},
    { .name = "activated", .signature = "uffu", .types = _CHyprlandInputCaptureV1ActivatedTypes + 0},
    { .name = "deactivated", .signature = "u", .types = _CHyprlandInputCaptureV1DeactivatedTypes + 0},
};

const wl_interface hyprland_input_capture_v1_interface = {
    .name = "hyprland_input_capture_v1", .version = 1,
    .method_count = 5, .methods = _CHyprlandInputCaptureV1Requests,
    .event_count = 4, .events = _CHyprlandInputCaptureV1Events,
};

CHyprlandInputCaptureV1::CHyprlandInputCaptureV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_input_capture_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandInputCaptureV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandInputCaptureV1VTable, this, nullptr);
}

CHyprlandInputCaptureV1::~CHyprlandInputCaptureV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandInputCaptureV1::onDestroyCalled() {
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

void CHyprlandInputCaptureV1::setClearBarriers(F<void(CHyprlandInputCaptureV1*)> &&handler) {
    requests.clearBarriers = std::move(handler);
}

void CHyprlandInputCaptureV1::setAddBarrier(F<void(CHyprlandInputCaptureV1*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t)> &&handler) {
    requests.addBarrier = std::move(handler);
}

void CHyprlandInputCaptureV1::setEnable(F<void(CHyprlandInputCaptureV1*)> &&handler) {
    requests.enable = std::move(handler);
}

void CHyprlandInputCaptureV1::setDisable(F<void(CHyprlandInputCaptureV1*)> &&handler) {
    requests.disable = std::move(handler);
}

void CHyprlandInputCaptureV1::setRelease(F<void(CHyprlandInputCaptureV1*, uint32_t, wl_fixed_t, wl_fixed_t)> &&handler) {
    requests.release = std::move(handler);
}

#undef F

// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// hyprland_ctm_control_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2024 Vaxry
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
#include "hyprland-ctm-control-v1.hpp"
#undef private
#define F std::function

static const wl_interface* hyprlandCtmControlV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface hyprland_ctm_control_manager_v1_interface;
extern const wl_interface wl_output_interface;

static void _CHyprlandCtmControlManagerV1SetCtmForOutput(wl_client* client, wl_resource* resource, wl_resource* output, wl_fixed_t mat0, wl_fixed_t mat1, wl_fixed_t mat2, wl_fixed_t mat3, wl_fixed_t mat4, wl_fixed_t mat5, wl_fixed_t mat6, wl_fixed_t mat7, wl_fixed_t mat8) {
    const auto PO = (CHyprlandCtmControlManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setCtmForOutput)
        PO->requests.setCtmForOutput(PO, output, mat0, mat1, mat2, mat3, mat4, mat5, mat6, mat7, mat8);
}

static void _CHyprlandCtmControlManagerV1Commit(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandCtmControlManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.commit)
        PO->requests.commit(PO);
}

static void _CHyprlandCtmControlManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandCtmControlManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandCtmControlManagerV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandCtmControlManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandCtmControlManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandCtmControlManagerV1VTable[] = {
    (void*)_CHyprlandCtmControlManagerV1SetCtmForOutput,
    (void*)_CHyprlandCtmControlManagerV1Commit,
    (void*)_CHyprlandCtmControlManagerV1Destroy,
};

void CHyprlandCtmControlManagerV1::sendBlocked() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CHyprlandCtmControlManagerV1::sendBlockedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}
static const wl_interface* _CHyprlandCtmControlManagerV1SetCtmForOutputTypes[] = {
    &wl_output_interface,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CHyprlandCtmControlManagerV1Requests[] = {
    { .name = "set_ctm_for_output", .signature = "offfffffff", .types = _CHyprlandCtmControlManagerV1SetCtmForOutputTypes + 0},
    { .name = "commit", .signature = "", .types = hyprlandCtmControlV1_dummyTypes + 0},
    { .name = "destroy", .signature = "", .types = hyprlandCtmControlV1_dummyTypes + 0},
};

static const wl_message _CHyprlandCtmControlManagerV1Events[] = {
    { .name = "blocked", .signature = "", .types = hyprlandCtmControlV1_dummyTypes + 0},
};

const wl_interface hyprland_ctm_control_manager_v1_interface = {
    .name = "hyprland_ctm_control_manager_v1", .version = 2,
    .method_count = 3, .methods = _CHyprlandCtmControlManagerV1Requests,
    .event_count = 1, .events = _CHyprlandCtmControlManagerV1Events,
};

CHyprlandCtmControlManagerV1::CHyprlandCtmControlManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_ctm_control_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandCtmControlManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandCtmControlManagerV1VTable, this, nullptr);
}

CHyprlandCtmControlManagerV1::~CHyprlandCtmControlManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandCtmControlManagerV1::onDestroyCalled() {
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

void CHyprlandCtmControlManagerV1::setSetCtmForOutput(F<void(CHyprlandCtmControlManagerV1*, wl_resource*, wl_fixed_t, wl_fixed_t, wl_fixed_t, wl_fixed_t, wl_fixed_t, wl_fixed_t, wl_fixed_t, wl_fixed_t, wl_fixed_t)> &&handler) {
    requests.setCtmForOutput = std::move(handler);
}

void CHyprlandCtmControlManagerV1::setCommit(F<void(CHyprlandCtmControlManagerV1*)> &&handler) {
    requests.commit = std::move(handler);
}

void CHyprlandCtmControlManagerV1::setDestroy(F<void(CHyprlandCtmControlManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// ext_workspace_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2019 Christopher Billington
    Copyright © 2020 Ilia Bozhinov
    Copyright © 2022 Victoria Brekenfeld

    Permission to use, copy, modify, distribute, and sell this
    software and its documentation for any purpose is hereby granted
    without fee, provided that the above copyright notice appear in
    all copies and that both that copyright notice and this permission
    notice appear in supporting documentation, and that the name of
    the copyright holders not be used in advertising or publicity
    pertaining to distribution of the software without specific,
    written prior permission.  The copyright holders make no
    representations about the suitability of this software for any
    purpose.  It is provided "as is" without express or implied
    warranty.

    THE COPYRIGHT HOLDERS DISCLAIM ALL WARRANTIES WITH REGARD TO THIS
    SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
    FITNESS, IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
    SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
    AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
    ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
    THIS SOFTWARE.
  
*/

#define private public
#define HYPRWAYLAND_SCANNER_NO_INTERFACES
#include "ext-workspace-v1.hpp"
#undef private
#define F std::function

static const wl_interface* extWorkspaceV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface ext_workspace_manager_v1_interface;
extern const wl_interface ext_workspace_group_handle_v1_interface;
extern const wl_interface ext_workspace_handle_v1_interface;
extern const wl_interface wl_output_interface;

static void _CExtWorkspaceManagerV1Commit(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtWorkspaceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.commit)
        PO->requests.commit(PO);
}

static void _CExtWorkspaceManagerV1Stop(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtWorkspaceManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.stop)
        PO->requests.stop(PO);
}

static void _CExtWorkspaceManagerV1__DestroyListener(wl_listener* l, void* d) {
    CExtWorkspaceManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtWorkspaceManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtWorkspaceManagerV1VTable[] = {
    (void*)_CExtWorkspaceManagerV1Commit,
    (void*)_CExtWorkspaceManagerV1Stop,
};

void CExtWorkspaceManagerV1::sendWorkspaceGroup(CExtWorkspaceGroupHandleV1* workspace_group) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, workspace_group ? workspace_group->pResource : nullptr);
}

void CExtWorkspaceManagerV1::sendWorkspace(CExtWorkspaceHandleV1* workspace) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, workspace ? workspace->pResource : nullptr);
}

void CExtWorkspaceManagerV1::sendDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CExtWorkspaceManagerV1::sendFinished() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CExtWorkspaceManagerV1::sendWorkspaceGroupRaw(CExtWorkspaceGroupHandleV1* workspace_group) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, workspace_group);
}

void CExtWorkspaceManagerV1::sendWorkspaceRaw(CExtWorkspaceHandleV1* workspace) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, workspace);
}

void CExtWorkspaceManagerV1::sendDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CExtWorkspaceManagerV1::sendFinishedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}
static const wl_interface* _CExtWorkspaceManagerV1WorkspaceGroupTypes[] = {
    &ext_workspace_group_handle_v1_interface,
};
static const wl_interface* _CExtWorkspaceManagerV1WorkspaceTypes[] = {
    &ext_workspace_handle_v1_interface,
};

static const wl_message _CExtWorkspaceManagerV1Requests[] = {
    { .name = "commit", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
    { .name = "stop", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
};

static const wl_message _CExtWorkspaceManagerV1Events[] = {
    { .name = "workspace_group", .signature = "n", .types = _CExtWorkspaceManagerV1WorkspaceGroupTypes + 0},
    { .name = "workspace", .signature = "n", .types = _CExtWorkspaceManagerV1WorkspaceTypes + 0},
    { .name = "done", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
    { .name = "finished", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
};

const wl_interface ext_workspace_manager_v1_interface = {
    .name = "ext_workspace_manager_v1", .version = 1,
    .method_count = 2, .methods = _CExtWorkspaceManagerV1Requests,
    .event_count = 4, .events = _CExtWorkspaceManagerV1Events,
};

CExtWorkspaceManagerV1::CExtWorkspaceManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_workspace_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtWorkspaceManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtWorkspaceManagerV1VTable, this, nullptr);
}

CExtWorkspaceManagerV1::~CExtWorkspaceManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtWorkspaceManagerV1::onDestroyCalled() {
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

void CExtWorkspaceManagerV1::setCommit(F<void(CExtWorkspaceManagerV1*)> &&handler) {
    requests.commit = std::move(handler);
}

void CExtWorkspaceManagerV1::setStop(F<void(CExtWorkspaceManagerV1*)> &&handler) {
    requests.stop = std::move(handler);
}

static void _CExtWorkspaceGroupHandleV1CreateWorkspace(wl_client* client, wl_resource* resource, const char* workspace) {
    const auto PO = (CExtWorkspaceGroupHandleV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createWorkspace)
        PO->requests.createWorkspace(PO, workspace);
}

static void _CExtWorkspaceGroupHandleV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtWorkspaceGroupHandleV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtWorkspaceGroupHandleV1__DestroyListener(wl_listener* l, void* d) {
    CExtWorkspaceGroupHandleV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtWorkspaceGroupHandleV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtWorkspaceGroupHandleV1VTable[] = {
    (void*)_CExtWorkspaceGroupHandleV1CreateWorkspace,
    (void*)_CExtWorkspaceGroupHandleV1Destroy,
};

void CExtWorkspaceGroupHandleV1::sendCapabilities(extWorkspaceGroupHandleV1GroupCapabilities capabilities) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, capabilities);
}

void CExtWorkspaceGroupHandleV1::sendOutputEnter(wl_resource* output) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, output);
}

void CExtWorkspaceGroupHandleV1::sendOutputLeave(wl_resource* output) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, output);
}

void CExtWorkspaceGroupHandleV1::sendWorkspaceEnter(CExtWorkspaceHandleV1* workspace) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, workspace ? workspace->pResource : nullptr);
}

void CExtWorkspaceGroupHandleV1::sendWorkspaceLeave(CExtWorkspaceHandleV1* workspace) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, workspace ? workspace->pResource : nullptr);
}

void CExtWorkspaceGroupHandleV1::sendRemoved() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5);
}

void CExtWorkspaceGroupHandleV1::sendCapabilitiesRaw(extWorkspaceGroupHandleV1GroupCapabilities capabilities) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, capabilities);
}

void CExtWorkspaceGroupHandleV1::sendOutputEnterRaw(wl_resource* output) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, output);
}

void CExtWorkspaceGroupHandleV1::sendOutputLeaveRaw(wl_resource* output) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, output);
}

void CExtWorkspaceGroupHandleV1::sendWorkspaceEnterRaw(wl_resource* workspace) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, workspace);
}

void CExtWorkspaceGroupHandleV1::sendWorkspaceLeaveRaw(wl_resource* workspace) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, workspace);
}

void CExtWorkspaceGroupHandleV1::sendRemovedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5);
}
static const wl_interface* _CExtWorkspaceGroupHandleV1CreateWorkspaceTypes[] = {
    nullptr,
};
static const wl_interface* _CExtWorkspaceGroupHandleV1CapabilitiesTypes[] = {
    nullptr,
};
static const wl_interface* _CExtWorkspaceGroupHandleV1OutputEnterTypes[] = {
    &wl_output_interface,
};
static const wl_interface* _CExtWorkspaceGroupHandleV1OutputLeaveTypes[] = {
    &wl_output_interface,
};
static const wl_interface* _CExtWorkspaceGroupHandleV1WorkspaceEnterTypes[] = {
    &ext_workspace_handle_v1_interface,
};
static const wl_interface* _CExtWorkspaceGroupHandleV1WorkspaceLeaveTypes[] = {
    &ext_workspace_handle_v1_interface,
};

static const wl_message _CExtWorkspaceGroupHandleV1Requests[] = {
    { .name = "create_workspace", .signature = "s", .types = _CExtWorkspaceGroupHandleV1CreateWorkspaceTypes + 0},
    { .name = "destroy", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
};

static const wl_message _CExtWorkspaceGroupHandleV1Events[] = {
    { .name = "capabilities", .signature = "u", .types = _CExtWorkspaceGroupHandleV1CapabilitiesTypes + 0},
    { .name = "output_enter", .signature = "o", .types = _CExtWorkspaceGroupHandleV1OutputEnterTypes + 0},
    { .name = "output_leave", .signature = "o", .types = _CExtWorkspaceGroupHandleV1OutputLeaveTypes + 0},
    { .name = "workspace_enter", .signature = "o", .types = _CExtWorkspaceGroupHandleV1WorkspaceEnterTypes + 0},
    { .name = "workspace_leave", .signature = "o", .types = _CExtWorkspaceGroupHandleV1WorkspaceLeaveTypes + 0},
    { .name = "removed", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
};

const wl_interface ext_workspace_group_handle_v1_interface = {
    .name = "ext_workspace_group_handle_v1", .version = 1,
    .method_count = 2, .methods = _CExtWorkspaceGroupHandleV1Requests,
    .event_count = 6, .events = _CExtWorkspaceGroupHandleV1Events,
};

CExtWorkspaceGroupHandleV1::CExtWorkspaceGroupHandleV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_workspace_group_handle_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtWorkspaceGroupHandleV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtWorkspaceGroupHandleV1VTable, this, nullptr);
}

CExtWorkspaceGroupHandleV1::~CExtWorkspaceGroupHandleV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtWorkspaceGroupHandleV1::onDestroyCalled() {
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

void CExtWorkspaceGroupHandleV1::setCreateWorkspace(F<void(CExtWorkspaceGroupHandleV1*, const char*)> &&handler) {
    requests.createWorkspace = std::move(handler);
}

void CExtWorkspaceGroupHandleV1::setDestroy(F<void(CExtWorkspaceGroupHandleV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CExtWorkspaceHandleV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtWorkspaceHandleV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CExtWorkspaceHandleV1Activate(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtWorkspaceHandleV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.activate)
        PO->requests.activate(PO);
}

static void _CExtWorkspaceHandleV1Deactivate(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtWorkspaceHandleV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.deactivate)
        PO->requests.deactivate(PO);
}

static void _CExtWorkspaceHandleV1Assign(wl_client* client, wl_resource* resource, wl_resource* workspace_group) {
    const auto PO = (CExtWorkspaceHandleV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.assign)
        PO->requests.assign(PO, workspace_group);
}

static void _CExtWorkspaceHandleV1Remove(wl_client* client, wl_resource* resource) {
    const auto PO = (CExtWorkspaceHandleV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.remove)
        PO->requests.remove(PO);
}

static void _CExtWorkspaceHandleV1__DestroyListener(wl_listener* l, void* d) {
    CExtWorkspaceHandleV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CExtWorkspaceHandleV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CExtWorkspaceHandleV1VTable[] = {
    (void*)_CExtWorkspaceHandleV1Destroy,
    (void*)_CExtWorkspaceHandleV1Activate,
    (void*)_CExtWorkspaceHandleV1Deactivate,
    (void*)_CExtWorkspaceHandleV1Assign,
    (void*)_CExtWorkspaceHandleV1Remove,
};

void CExtWorkspaceHandleV1::sendId(const char* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, id);
}

void CExtWorkspaceHandleV1::sendName(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, name);
}

void CExtWorkspaceHandleV1::sendCoordinates(wl_array* coordinates) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, coordinates);
}

void CExtWorkspaceHandleV1::sendState(extWorkspaceHandleV1State state) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, state);
}

void CExtWorkspaceHandleV1::sendCapabilities(extWorkspaceHandleV1WorkspaceCapabilities capabilities) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, capabilities);
}

void CExtWorkspaceHandleV1::sendRemoved() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5);
}

void CExtWorkspaceHandleV1::sendIdRaw(const char* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, id);
}

void CExtWorkspaceHandleV1::sendNameRaw(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, name);
}

void CExtWorkspaceHandleV1::sendCoordinatesRaw(wl_array* coordinates) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, coordinates);
}

void CExtWorkspaceHandleV1::sendStateRaw(extWorkspaceHandleV1State state) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, state);
}

void CExtWorkspaceHandleV1::sendCapabilitiesRaw(extWorkspaceHandleV1WorkspaceCapabilities capabilities) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, capabilities);
}

void CExtWorkspaceHandleV1::sendRemovedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5);
}
static const wl_interface* _CExtWorkspaceHandleV1AssignTypes[] = {
    &ext_workspace_group_handle_v1_interface,
};
static const wl_interface* _CExtWorkspaceHandleV1IdTypes[] = {
    nullptr,
};
static const wl_interface* _CExtWorkspaceHandleV1NameTypes[] = {
    nullptr,
};
static const wl_interface* _CExtWorkspaceHandleV1CoordinatesTypes[] = {
    nullptr,
};
static const wl_interface* _CExtWorkspaceHandleV1StateTypes[] = {
    nullptr,
};
static const wl_interface* _CExtWorkspaceHandleV1CapabilitiesTypes[] = {
    nullptr,
};

static const wl_message _CExtWorkspaceHandleV1Requests[] = {
    { .name = "destroy", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
    { .name = "activate", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
    { .name = "deactivate", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
    { .name = "assign", .signature = "o", .types = _CExtWorkspaceHandleV1AssignTypes + 0},
    { .name = "remove", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
};

static const wl_message _CExtWorkspaceHandleV1Events[] = {
    { .name = "id", .signature = "s", .types = _CExtWorkspaceHandleV1IdTypes + 0},
    { .name = "name", .signature = "s", .types = _CExtWorkspaceHandleV1NameTypes + 0},
    { .name = "coordinates", .signature = "a", .types = _CExtWorkspaceHandleV1CoordinatesTypes + 0},
    { .name = "state", .signature = "u", .types = _CExtWorkspaceHandleV1StateTypes + 0},
    { .name = "capabilities", .signature = "u", .types = _CExtWorkspaceHandleV1CapabilitiesTypes + 0},
    { .name = "removed", .signature = "", .types = extWorkspaceV1_dummyTypes + 0},
};

const wl_interface ext_workspace_handle_v1_interface = {
    .name = "ext_workspace_handle_v1", .version = 1,
    .method_count = 5, .methods = _CExtWorkspaceHandleV1Requests,
    .event_count = 6, .events = _CExtWorkspaceHandleV1Events,
};

CExtWorkspaceHandleV1::CExtWorkspaceHandleV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &ext_workspace_handle_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CExtWorkspaceHandleV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CExtWorkspaceHandleV1VTable, this, nullptr);
}

CExtWorkspaceHandleV1::~CExtWorkspaceHandleV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CExtWorkspaceHandleV1::onDestroyCalled() {
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

void CExtWorkspaceHandleV1::setDestroy(F<void(CExtWorkspaceHandleV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CExtWorkspaceHandleV1::setActivate(F<void(CExtWorkspaceHandleV1*)> &&handler) {
    requests.activate = std::move(handler);
}

void CExtWorkspaceHandleV1::setDeactivate(F<void(CExtWorkspaceHandleV1*)> &&handler) {
    requests.deactivate = std::move(handler);
}

void CExtWorkspaceHandleV1::setAssign(F<void(CExtWorkspaceHandleV1*, wl_resource*)> &&handler) {
    requests.assign = std::move(handler);
}

void CExtWorkspaceHandleV1::setRemove(F<void(CExtWorkspaceHandleV1*)> &&handler) {
    requests.remove = std::move(handler);
}

#undef F

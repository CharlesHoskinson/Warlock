// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// wlr_output_management_unstable_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2019 Purism SPC

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
#include "wlr-output-management-unstable-v1.hpp"
#undef private
#define F std::function

static const wl_interface* wlrOutputManagementUnstableV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface zwlr_output_manager_v1_interface;
extern const wl_interface zwlr_output_head_v1_interface;
extern const wl_interface zwlr_output_mode_v1_interface;
extern const wl_interface zwlr_output_configuration_v1_interface;
extern const wl_interface zwlr_output_configuration_head_v1_interface;

static void _CZwlrOutputManagerV1CreateConfiguration(wl_client* client, wl_resource* resource, uint32_t id, uint32_t serial) {
    const auto PO = (CZwlrOutputManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createConfiguration)
        PO->requests.createConfiguration(PO, id, serial);
}

static void _CZwlrOutputManagerV1Stop(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrOutputManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.stop)
        PO->requests.stop(PO);
}

static void _CZwlrOutputManagerV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrOutputManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrOutputManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrOutputManagerV1VTable[] = {
    (void*)_CZwlrOutputManagerV1CreateConfiguration,
    (void*)_CZwlrOutputManagerV1Stop,
};

void CZwlrOutputManagerV1::sendHead(CZwlrOutputHeadV1* head) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, head ? head->pResource : nullptr);
}

void CZwlrOutputManagerV1::sendDone(uint32_t serial) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial);
}

void CZwlrOutputManagerV1::sendFinished() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CZwlrOutputManagerV1::sendHeadRaw(CZwlrOutputHeadV1* head) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, head);
}

void CZwlrOutputManagerV1::sendDoneRaw(uint32_t serial) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial);
}

void CZwlrOutputManagerV1::sendFinishedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}
static const wl_interface* _CZwlrOutputManagerV1CreateConfigurationTypes[] = {
    &zwlr_output_configuration_v1_interface,
    nullptr,
};
static const wl_interface* _CZwlrOutputManagerV1HeadTypes[] = {
    &zwlr_output_head_v1_interface,
};
static const wl_interface* _CZwlrOutputManagerV1DoneTypes[] = {
    nullptr,
};

static const wl_message _CZwlrOutputManagerV1Requests[] = {
    { .name = "create_configuration", .signature = "nu", .types = _CZwlrOutputManagerV1CreateConfigurationTypes + 0},
    { .name = "stop", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwlrOutputManagerV1Events[] = {
    { .name = "head", .signature = "n", .types = _CZwlrOutputManagerV1HeadTypes + 0},
    { .name = "done", .signature = "u", .types = _CZwlrOutputManagerV1DoneTypes + 0},
    { .name = "finished", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
};

const wl_interface zwlr_output_manager_v1_interface = {
    .name = "zwlr_output_manager_v1", .version = 4,
    .method_count = 2, .methods = _CZwlrOutputManagerV1Requests,
    .event_count = 3, .events = _CZwlrOutputManagerV1Events,
};

CZwlrOutputManagerV1::CZwlrOutputManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_output_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrOutputManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrOutputManagerV1VTable, this, nullptr);
}

CZwlrOutputManagerV1::~CZwlrOutputManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrOutputManagerV1::onDestroyCalled() {
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

void CZwlrOutputManagerV1::setCreateConfiguration(F<void(CZwlrOutputManagerV1*, uint32_t, uint32_t)> &&handler) {
    requests.createConfiguration = std::move(handler);
}

void CZwlrOutputManagerV1::setStop(F<void(CZwlrOutputManagerV1*)> &&handler) {
    requests.stop = std::move(handler);
}

static void _CZwlrOutputHeadV1Release(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrOutputHeadV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CZwlrOutputHeadV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrOutputHeadV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrOutputHeadV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrOutputHeadV1VTable[] = {
    (void*)_CZwlrOutputHeadV1Release,
};

void CZwlrOutputHeadV1::sendName(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, name);
}

void CZwlrOutputHeadV1::sendDescription(const char* description) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, description);
}

void CZwlrOutputHeadV1::sendPhysicalSize(int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, width, height);
}

void CZwlrOutputHeadV1::sendMode(CZwlrOutputModeV1* mode) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, mode ? mode->pResource : nullptr);
}

void CZwlrOutputHeadV1::sendEnabled(int32_t enabled) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, enabled);
}

void CZwlrOutputHeadV1::sendCurrentMode(CZwlrOutputModeV1* mode) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, mode ? mode->pResource : nullptr);
}

void CZwlrOutputHeadV1::sendPosition(int32_t x, int32_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6, x, y);
}

void CZwlrOutputHeadV1::sendTransform(int32_t transform) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 7, transform);
}

void CZwlrOutputHeadV1::sendScale(wl_fixed_t scale) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 8, scale);
}

void CZwlrOutputHeadV1::sendFinished() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 9);
}

void CZwlrOutputHeadV1::sendMake(const char* make) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 10, make);
}

void CZwlrOutputHeadV1::sendModel(const char* model) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 11, model);
}

void CZwlrOutputHeadV1::sendSerialNumber(const char* serial_number) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 12, serial_number);
}

void CZwlrOutputHeadV1::sendAdaptiveSync(zwlrOutputHeadV1AdaptiveSyncState state) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 13, state);
}

void CZwlrOutputHeadV1::sendNameRaw(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, name);
}

void CZwlrOutputHeadV1::sendDescriptionRaw(const char* description) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, description);
}

void CZwlrOutputHeadV1::sendPhysicalSizeRaw(int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, width, height);
}

void CZwlrOutputHeadV1::sendModeRaw(CZwlrOutputModeV1* mode) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, mode);
}

void CZwlrOutputHeadV1::sendEnabledRaw(int32_t enabled) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, enabled);
}

void CZwlrOutputHeadV1::sendCurrentModeRaw(wl_resource* mode) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, mode);
}

void CZwlrOutputHeadV1::sendPositionRaw(int32_t x, int32_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6, x, y);
}

void CZwlrOutputHeadV1::sendTransformRaw(int32_t transform) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 7, transform);
}

void CZwlrOutputHeadV1::sendScaleRaw(wl_fixed_t scale) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 8, scale);
}

void CZwlrOutputHeadV1::sendFinishedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 9);
}

void CZwlrOutputHeadV1::sendMakeRaw(const char* make) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 10, make);
}

void CZwlrOutputHeadV1::sendModelRaw(const char* model) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 11, model);
}

void CZwlrOutputHeadV1::sendSerialNumberRaw(const char* serial_number) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 12, serial_number);
}

void CZwlrOutputHeadV1::sendAdaptiveSyncRaw(zwlrOutputHeadV1AdaptiveSyncState state) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 13, state);
}
static const wl_interface* _CZwlrOutputHeadV1NameTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1DescriptionTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1PhysicalSizeTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1ModeTypes[] = {
    &zwlr_output_mode_v1_interface,
};
static const wl_interface* _CZwlrOutputHeadV1EnabledTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1CurrentModeTypes[] = {
    &zwlr_output_mode_v1_interface,
};
static const wl_interface* _CZwlrOutputHeadV1PositionTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1TransformTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1ScaleTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1MakeTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1ModelTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1SerialNumberTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputHeadV1AdaptiveSyncTypes[] = {
    nullptr,
};

static const wl_message _CZwlrOutputHeadV1Requests[] = {
    { .name = "release", .signature = "3", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwlrOutputHeadV1Events[] = {
    { .name = "name", .signature = "s", .types = _CZwlrOutputHeadV1NameTypes + 0},
    { .name = "description", .signature = "s", .types = _CZwlrOutputHeadV1DescriptionTypes + 0},
    { .name = "physical_size", .signature = "ii", .types = _CZwlrOutputHeadV1PhysicalSizeTypes + 0},
    { .name = "mode", .signature = "n", .types = _CZwlrOutputHeadV1ModeTypes + 0},
    { .name = "enabled", .signature = "i", .types = _CZwlrOutputHeadV1EnabledTypes + 0},
    { .name = "current_mode", .signature = "o", .types = _CZwlrOutputHeadV1CurrentModeTypes + 0},
    { .name = "position", .signature = "ii", .types = _CZwlrOutputHeadV1PositionTypes + 0},
    { .name = "transform", .signature = "i", .types = _CZwlrOutputHeadV1TransformTypes + 0},
    { .name = "scale", .signature = "f", .types = _CZwlrOutputHeadV1ScaleTypes + 0},
    { .name = "finished", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
    { .name = "make", .signature = "2s", .types = _CZwlrOutputHeadV1MakeTypes + 0},
    { .name = "model", .signature = "2s", .types = _CZwlrOutputHeadV1ModelTypes + 0},
    { .name = "serial_number", .signature = "2s", .types = _CZwlrOutputHeadV1SerialNumberTypes + 0},
    { .name = "adaptive_sync", .signature = "4u", .types = _CZwlrOutputHeadV1AdaptiveSyncTypes + 0},
};

const wl_interface zwlr_output_head_v1_interface = {
    .name = "zwlr_output_head_v1", .version = 4,
    .method_count = 1, .methods = _CZwlrOutputHeadV1Requests,
    .event_count = 14, .events = _CZwlrOutputHeadV1Events,
};

CZwlrOutputHeadV1::CZwlrOutputHeadV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_output_head_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrOutputHeadV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrOutputHeadV1VTable, this, nullptr);
}

CZwlrOutputHeadV1::~CZwlrOutputHeadV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrOutputHeadV1::onDestroyCalled() {
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

void CZwlrOutputHeadV1::setRelease(F<void(CZwlrOutputHeadV1*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CZwlrOutputModeV1Release(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrOutputModeV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CZwlrOutputModeV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrOutputModeV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrOutputModeV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrOutputModeV1VTable[] = {
    (void*)_CZwlrOutputModeV1Release,
};

void CZwlrOutputModeV1::sendSize(int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, width, height);
}

void CZwlrOutputModeV1::sendRefresh(int32_t refresh) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, refresh);
}

void CZwlrOutputModeV1::sendPreferred() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CZwlrOutputModeV1::sendFinished() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CZwlrOutputModeV1::sendSizeRaw(int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, width, height);
}

void CZwlrOutputModeV1::sendRefreshRaw(int32_t refresh) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, refresh);
}

void CZwlrOutputModeV1::sendPreferredRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CZwlrOutputModeV1::sendFinishedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}
static const wl_interface* _CZwlrOutputModeV1SizeTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CZwlrOutputModeV1RefreshTypes[] = {
    nullptr,
};

static const wl_message _CZwlrOutputModeV1Requests[] = {
    { .name = "release", .signature = "3", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwlrOutputModeV1Events[] = {
    { .name = "size", .signature = "ii", .types = _CZwlrOutputModeV1SizeTypes + 0},
    { .name = "refresh", .signature = "i", .types = _CZwlrOutputModeV1RefreshTypes + 0},
    { .name = "preferred", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
    { .name = "finished", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
};

const wl_interface zwlr_output_mode_v1_interface = {
    .name = "zwlr_output_mode_v1", .version = 3,
    .method_count = 1, .methods = _CZwlrOutputModeV1Requests,
    .event_count = 4, .events = _CZwlrOutputModeV1Events,
};

CZwlrOutputModeV1::CZwlrOutputModeV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_output_mode_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrOutputModeV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrOutputModeV1VTable, this, nullptr);
}

CZwlrOutputModeV1::~CZwlrOutputModeV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrOutputModeV1::onDestroyCalled() {
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

void CZwlrOutputModeV1::setRelease(F<void(CZwlrOutputModeV1*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CZwlrOutputConfigurationV1EnableHead(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* head) {
    const auto PO = (CZwlrOutputConfigurationV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.enableHead)
        PO->requests.enableHead(PO, id, head);
}

static void _CZwlrOutputConfigurationV1DisableHead(wl_client* client, wl_resource* resource, wl_resource* head) {
    const auto PO = (CZwlrOutputConfigurationV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.disableHead)
        PO->requests.disableHead(PO, head);
}

static void _CZwlrOutputConfigurationV1Apply(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrOutputConfigurationV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.apply)
        PO->requests.apply(PO);
}

static void _CZwlrOutputConfigurationV1Test(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrOutputConfigurationV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.test)
        PO->requests.test(PO);
}

static void _CZwlrOutputConfigurationV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZwlrOutputConfigurationV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZwlrOutputConfigurationV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrOutputConfigurationV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrOutputConfigurationV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrOutputConfigurationV1VTable[] = {
    (void*)_CZwlrOutputConfigurationV1EnableHead,
    (void*)_CZwlrOutputConfigurationV1DisableHead,
    (void*)_CZwlrOutputConfigurationV1Apply,
    (void*)_CZwlrOutputConfigurationV1Test,
    (void*)_CZwlrOutputConfigurationV1Destroy,
};

void CZwlrOutputConfigurationV1::sendSucceeded() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CZwlrOutputConfigurationV1::sendFailed() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CZwlrOutputConfigurationV1::sendCancelled() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CZwlrOutputConfigurationV1::sendSucceededRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CZwlrOutputConfigurationV1::sendFailedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CZwlrOutputConfigurationV1::sendCancelledRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}
static const wl_interface* _CZwlrOutputConfigurationV1EnableHeadTypes[] = {
    &zwlr_output_configuration_head_v1_interface,
    &zwlr_output_head_v1_interface,
};
static const wl_interface* _CZwlrOutputConfigurationV1DisableHeadTypes[] = {
    &zwlr_output_head_v1_interface,
};

static const wl_message _CZwlrOutputConfigurationV1Requests[] = {
    { .name = "enable_head", .signature = "no", .types = _CZwlrOutputConfigurationV1EnableHeadTypes + 0},
    { .name = "disable_head", .signature = "o", .types = _CZwlrOutputConfigurationV1DisableHeadTypes + 0},
    { .name = "apply", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
    { .name = "test", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
    { .name = "destroy", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
};

static const wl_message _CZwlrOutputConfigurationV1Events[] = {
    { .name = "succeeded", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
    { .name = "failed", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
    { .name = "cancelled", .signature = "", .types = wlrOutputManagementUnstableV1_dummyTypes + 0},
};

const wl_interface zwlr_output_configuration_v1_interface = {
    .name = "zwlr_output_configuration_v1", .version = 4,
    .method_count = 5, .methods = _CZwlrOutputConfigurationV1Requests,
    .event_count = 3, .events = _CZwlrOutputConfigurationV1Events,
};

CZwlrOutputConfigurationV1::CZwlrOutputConfigurationV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_output_configuration_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrOutputConfigurationV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrOutputConfigurationV1VTable, this, nullptr);
}

CZwlrOutputConfigurationV1::~CZwlrOutputConfigurationV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrOutputConfigurationV1::onDestroyCalled() {
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

void CZwlrOutputConfigurationV1::setEnableHead(F<void(CZwlrOutputConfigurationV1*, uint32_t, wl_resource*)> &&handler) {
    requests.enableHead = std::move(handler);
}

void CZwlrOutputConfigurationV1::setDisableHead(F<void(CZwlrOutputConfigurationV1*, wl_resource*)> &&handler) {
    requests.disableHead = std::move(handler);
}

void CZwlrOutputConfigurationV1::setApply(F<void(CZwlrOutputConfigurationV1*)> &&handler) {
    requests.apply = std::move(handler);
}

void CZwlrOutputConfigurationV1::setTest(F<void(CZwlrOutputConfigurationV1*)> &&handler) {
    requests.test = std::move(handler);
}

void CZwlrOutputConfigurationV1::setDestroy(F<void(CZwlrOutputConfigurationV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZwlrOutputConfigurationHeadV1SetMode(wl_client* client, wl_resource* resource, wl_resource* mode) {
    const auto PO = (CZwlrOutputConfigurationHeadV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setMode)
        PO->requests.setMode(PO, mode);
}

static void _CZwlrOutputConfigurationHeadV1SetCustomMode(wl_client* client, wl_resource* resource, int32_t width, int32_t height, int32_t refresh) {
    const auto PO = (CZwlrOutputConfigurationHeadV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setCustomMode)
        PO->requests.setCustomMode(PO, width, height, refresh);
}

static void _CZwlrOutputConfigurationHeadV1SetPosition(wl_client* client, wl_resource* resource, int32_t x, int32_t y) {
    const auto PO = (CZwlrOutputConfigurationHeadV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setPosition)
        PO->requests.setPosition(PO, x, y);
}

static void _CZwlrOutputConfigurationHeadV1SetTransform(wl_client* client, wl_resource* resource, int32_t transform) {
    const auto PO = (CZwlrOutputConfigurationHeadV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setTransform)
        PO->requests.setTransform(PO, transform);
}

static void _CZwlrOutputConfigurationHeadV1SetScale(wl_client* client, wl_resource* resource, wl_fixed_t scale) {
    const auto PO = (CZwlrOutputConfigurationHeadV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setScale)
        PO->requests.setScale(PO, scale);
}

static void _CZwlrOutputConfigurationHeadV1SetAdaptiveSync(wl_client* client, wl_resource* resource, uint32_t state) {
    const auto PO = (CZwlrOutputConfigurationHeadV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setAdaptiveSync)
        PO->requests.setAdaptiveSync(PO, state);
}

static void _CZwlrOutputConfigurationHeadV1__DestroyListener(wl_listener* l, void* d) {
    CZwlrOutputConfigurationHeadV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZwlrOutputConfigurationHeadV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZwlrOutputConfigurationHeadV1VTable[] = {
    (void*)_CZwlrOutputConfigurationHeadV1SetMode,
    (void*)_CZwlrOutputConfigurationHeadV1SetCustomMode,
    (void*)_CZwlrOutputConfigurationHeadV1SetPosition,
    (void*)_CZwlrOutputConfigurationHeadV1SetTransform,
    (void*)_CZwlrOutputConfigurationHeadV1SetScale,
    (void*)_CZwlrOutputConfigurationHeadV1SetAdaptiveSync,
};
static const wl_interface* _CZwlrOutputConfigurationHeadV1SetModeTypes[] = {
    &zwlr_output_mode_v1_interface,
};
static const wl_interface* _CZwlrOutputConfigurationHeadV1SetCustomModeTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CZwlrOutputConfigurationHeadV1SetPositionTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CZwlrOutputConfigurationHeadV1SetTransformTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputConfigurationHeadV1SetScaleTypes[] = {
    nullptr,
};
static const wl_interface* _CZwlrOutputConfigurationHeadV1SetAdaptiveSyncTypes[] = {
    nullptr,
};

static const wl_message _CZwlrOutputConfigurationHeadV1Requests[] = {
    { .name = "set_mode", .signature = "o", .types = _CZwlrOutputConfigurationHeadV1SetModeTypes + 0},
    { .name = "set_custom_mode", .signature = "iii", .types = _CZwlrOutputConfigurationHeadV1SetCustomModeTypes + 0},
    { .name = "set_position", .signature = "ii", .types = _CZwlrOutputConfigurationHeadV1SetPositionTypes + 0},
    { .name = "set_transform", .signature = "i", .types = _CZwlrOutputConfigurationHeadV1SetTransformTypes + 0},
    { .name = "set_scale", .signature = "f", .types = _CZwlrOutputConfigurationHeadV1SetScaleTypes + 0},
    { .name = "set_adaptive_sync", .signature = "4u", .types = _CZwlrOutputConfigurationHeadV1SetAdaptiveSyncTypes + 0},
};

const wl_interface zwlr_output_configuration_head_v1_interface = {
    .name = "zwlr_output_configuration_head_v1", .version = 4,
    .method_count = 6, .methods = _CZwlrOutputConfigurationHeadV1Requests,
    .event_count = 0, .events = nullptr,
};

CZwlrOutputConfigurationHeadV1::CZwlrOutputConfigurationHeadV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zwlr_output_configuration_head_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZwlrOutputConfigurationHeadV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZwlrOutputConfigurationHeadV1VTable, this, nullptr);
}

CZwlrOutputConfigurationHeadV1::~CZwlrOutputConfigurationHeadV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZwlrOutputConfigurationHeadV1::onDestroyCalled() {
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

void CZwlrOutputConfigurationHeadV1::setSetMode(F<void(CZwlrOutputConfigurationHeadV1*, wl_resource*)> &&handler) {
    requests.setMode = std::move(handler);
}

void CZwlrOutputConfigurationHeadV1::setSetCustomMode(F<void(CZwlrOutputConfigurationHeadV1*, int32_t, int32_t, int32_t)> &&handler) {
    requests.setCustomMode = std::move(handler);
}

void CZwlrOutputConfigurationHeadV1::setSetPosition(F<void(CZwlrOutputConfigurationHeadV1*, int32_t, int32_t)> &&handler) {
    requests.setPosition = std::move(handler);
}

void CZwlrOutputConfigurationHeadV1::setSetTransform(F<void(CZwlrOutputConfigurationHeadV1*, int32_t)> &&handler) {
    requests.setTransform = std::move(handler);
}

void CZwlrOutputConfigurationHeadV1::setSetScale(F<void(CZwlrOutputConfigurationHeadV1*, wl_fixed_t)> &&handler) {
    requests.setScale = std::move(handler);
}

void CZwlrOutputConfigurationHeadV1::setSetAdaptiveSync(F<void(CZwlrOutputConfigurationHeadV1*, uint32_t)> &&handler) {
    requests.setAdaptiveSync = std::move(handler);
}

#undef F

// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// wayland

/*
 This protocol's authors' copyright notice is:


    Copyright © 2008-2011 Kristian Høgsberg
    Copyright © 2010-2011 Intel Corporation
    Copyright © 2012-2013 Collabora, Ltd.

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation files
    (the "Software"), to deal in the Software without restriction,
    including without limitation the rights to use, copy, modify, merge,
    publish, distribute, sublicense, and/or sell copies of the Software,
    and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice (including the
    next paragraph) shall be included in all copies or substantial
    portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
    BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
    ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
  
*/

#define private public
#define HYPRWAYLAND_SCANNER_NO_INTERFACES
#include "wayland.hpp"
#undef private
#define F std::function

static const wl_interface* wayland_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wl_display_interface;
extern const wl_interface wl_registry_interface;
extern const wl_interface wl_callback_interface;
extern const wl_interface wl_compositor_interface;
extern const wl_interface wl_shm_pool_interface;
extern const wl_interface wl_shm_interface;
extern const wl_interface wl_buffer_interface;
extern const wl_interface wl_data_offer_interface;
extern const wl_interface wl_data_source_interface;
extern const wl_interface wl_data_device_interface;
extern const wl_interface wl_data_device_manager_interface;
extern const wl_interface wl_shell_interface;
extern const wl_interface wl_shell_surface_interface;
extern const wl_interface wl_surface_interface;
extern const wl_interface wl_seat_interface;
extern const wl_interface wl_pointer_interface;
extern const wl_interface wl_keyboard_interface;
extern const wl_interface wl_touch_interface;
extern const wl_interface wl_output_interface;
extern const wl_interface wl_region_interface;
extern const wl_interface wl_subcompositor_interface;
extern const wl_interface wl_subsurface_interface;
extern const wl_interface wl_fixes_interface;

static void _CWlDisplaySync(wl_client* client, wl_resource* resource, uint32_t callback) {
    const auto PO = (CWlDisplay*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.sync)
        PO->requests.sync(PO, callback);
}

static void _CWlDisplayGetRegistry(wl_client* client, wl_resource* resource, uint32_t registry) {
    const auto PO = (CWlDisplay*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getRegistry)
        PO->requests.getRegistry(PO, registry);
}

static void _CWlDisplay__DestroyListener(wl_listener* l, void* d) {
    CWlDisplayDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlDisplay* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlDisplayVTable[] = {
    (void*)_CWlDisplaySync,
    (void*)_CWlDisplayGetRegistry,
};

void CWlDisplay::sendError(wl_resource* object_id, uint32_t code, const char* message) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, object_id, code, message);
}

void CWlDisplay::sendDeleteId(uint32_t id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id);
}

void CWlDisplay::sendErrorRaw(wl_resource* object_id, uint32_t code, const char* message) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, object_id, code, message);
}

void CWlDisplay::sendDeleteIdRaw(uint32_t id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, id);
}
static const wl_interface* _CWlDisplaySyncTypes[] = {
    &wl_callback_interface,
};
static const wl_interface* _CWlDisplayGetRegistryTypes[] = {
    &wl_registry_interface,
};
static const wl_interface* _CWlDisplayErrorTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlDisplayDeleteIdTypes[] = {
    nullptr,
};

static const wl_message _CWlDisplayRequests[] = {
    { .name = "sync", .signature = "n", .types = _CWlDisplaySyncTypes + 0},
    { .name = "get_registry", .signature = "n", .types = _CWlDisplayGetRegistryTypes + 0},
};

static const wl_message _CWlDisplayEvents[] = {
    { .name = "error", .signature = "ous", .types = _CWlDisplayErrorTypes + 0},
    { .name = "delete_id", .signature = "u", .types = _CWlDisplayDeleteIdTypes + 0},
};

const wl_interface wl_display_interface = {
    .name = "wl_display", .version = 1,
    .method_count = 2, .methods = _CWlDisplayRequests,
    .event_count = 2, .events = _CWlDisplayEvents,
};

CWlDisplay::CWlDisplay(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_display_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlDisplay__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlDisplayVTable, this, nullptr);
}

CWlDisplay::~CWlDisplay() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlDisplay::onDestroyCalled() {
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

void CWlDisplay::setSync(F<void(CWlDisplay*, uint32_t)> &&handler) {
    requests.sync = std::move(handler);
}

void CWlDisplay::setGetRegistry(F<void(CWlDisplay*, uint32_t)> &&handler) {
    requests.getRegistry = std::move(handler);
}

static void _CWlRegistryBind(wl_client* client, wl_resource* resource, uint32_t name, uint32_t id) {
    const auto PO = (CWlRegistry*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.bind)
        PO->requests.bind(PO, name, id);
}

static void _CWlRegistry__DestroyListener(wl_listener* l, void* d) {
    CWlRegistryDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlRegistry* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlRegistryVTable[] = {
    (void*)_CWlRegistryBind,
};

void CWlRegistry::sendGlobal(uint32_t name, const char* interface, uint32_t version) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, name, interface, version);
}

void CWlRegistry::sendGlobalRemove(uint32_t name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, name);
}

void CWlRegistry::sendGlobalRaw(uint32_t name, const char* interface, uint32_t version) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, name, interface, version);
}

void CWlRegistry::sendGlobalRemoveRaw(uint32_t name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, name);
}
static const wl_interface* _CWlRegistryBindTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlRegistryGlobalTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlRegistryGlobalRemoveTypes[] = {
    nullptr,
};

static const wl_message _CWlRegistryRequests[] = {
    { .name = "bind", .signature = "usun", .types = _CWlRegistryBindTypes + 0},
};

static const wl_message _CWlRegistryEvents[] = {
    { .name = "global", .signature = "usu", .types = _CWlRegistryGlobalTypes + 0},
    { .name = "global_remove", .signature = "u", .types = _CWlRegistryGlobalRemoveTypes + 0},
};

const wl_interface wl_registry_interface = {
    .name = "wl_registry", .version = 1,
    .method_count = 1, .methods = _CWlRegistryRequests,
    .event_count = 2, .events = _CWlRegistryEvents,
};

CWlRegistry::CWlRegistry(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_registry_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlRegistry__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlRegistryVTable, this, nullptr);
}

CWlRegistry::~CWlRegistry() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlRegistry::onDestroyCalled() {
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

void CWlRegistry::setBind(F<void(CWlRegistry*, uint32_t, uint32_t)> &&handler) {
    requests.bind = std::move(handler);
}

static void _CWlCallback__DestroyListener(wl_listener* l, void* d) {
    CWlCallbackDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlCallback* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlCallbackVTable[] = {
    nullptr,
};

void CWlCallback::sendDone(uint32_t callback_data) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, callback_data);
}

void CWlCallback::sendDoneRaw(uint32_t callback_data) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, callback_data);
}
static const wl_interface* _CWlCallbackDoneTypes[] = {
    nullptr,
};

static const wl_message _CWlCallbackEvents[] = {
    { .name = "done", .signature = "u", .types = _CWlCallbackDoneTypes + 0},
};

const wl_interface wl_callback_interface = {
    .name = "wl_callback", .version = 1,
    .method_count = 0, .methods = nullptr,
    .event_count = 1, .events = _CWlCallbackEvents,
};

CWlCallback::CWlCallback(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_callback_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlCallback__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlCallbackVTable, this, nullptr);
}

CWlCallback::~CWlCallback() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlCallback::onDestroyCalled() {
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

static void _CWlCompositorCreateSurface(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CWlCompositor*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createSurface)
        PO->requests.createSurface(PO, id);
}

static void _CWlCompositorCreateRegion(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CWlCompositor*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createRegion)
        PO->requests.createRegion(PO, id);
}

static void _CWlCompositorRelease(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlCompositor*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWlCompositor__DestroyListener(wl_listener* l, void* d) {
    CWlCompositorDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlCompositor* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlCompositorVTable[] = {
    (void*)_CWlCompositorCreateSurface,
    (void*)_CWlCompositorCreateRegion,
    (void*)_CWlCompositorRelease,
};
static const wl_interface* _CWlCompositorCreateSurfaceTypes[] = {
    &wl_surface_interface,
};
static const wl_interface* _CWlCompositorCreateRegionTypes[] = {
    &wl_region_interface,
};

static const wl_message _CWlCompositorRequests[] = {
    { .name = "create_surface", .signature = "n", .types = _CWlCompositorCreateSurfaceTypes + 0},
    { .name = "create_region", .signature = "n", .types = _CWlCompositorCreateRegionTypes + 0},
    { .name = "release", .signature = "7", .types = wayland_dummyTypes + 0},
};

const wl_interface wl_compositor_interface = {
    .name = "wl_compositor", .version = 7,
    .method_count = 3, .methods = _CWlCompositorRequests,
    .event_count = 0, .events = nullptr,
};

CWlCompositor::CWlCompositor(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_compositor_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlCompositor__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlCompositorVTable, this, nullptr);
}

CWlCompositor::~CWlCompositor() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlCompositor::onDestroyCalled() {
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

void CWlCompositor::setCreateSurface(F<void(CWlCompositor*, uint32_t)> &&handler) {
    requests.createSurface = std::move(handler);
}

void CWlCompositor::setCreateRegion(F<void(CWlCompositor*, uint32_t)> &&handler) {
    requests.createRegion = std::move(handler);
}

void CWlCompositor::setRelease(F<void(CWlCompositor*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWlShmPoolCreateBuffer(wl_client* client, wl_resource* resource, uint32_t id, int32_t offset, int32_t width, int32_t height, int32_t stride, uint32_t format) {
    const auto PO = (CWlShmPool*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createBuffer)
        PO->requests.createBuffer(PO, id, offset, width, height, stride, format);
}

static void _CWlShmPoolDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlShmPool*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWlShmPoolResize(wl_client* client, wl_resource* resource, int32_t size) {
    const auto PO = (CWlShmPool*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.resize)
        PO->requests.resize(PO, size);
}

static void _CWlShmPool__DestroyListener(wl_listener* l, void* d) {
    CWlShmPoolDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlShmPool* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlShmPoolVTable[] = {
    (void*)_CWlShmPoolCreateBuffer,
    (void*)_CWlShmPoolDestroy,
    (void*)_CWlShmPoolResize,
};
static const wl_interface* _CWlShmPoolCreateBufferTypes[] = {
    &wl_buffer_interface,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlShmPoolResizeTypes[] = {
    nullptr,
};

static const wl_message _CWlShmPoolRequests[] = {
    { .name = "create_buffer", .signature = "niiiiu", .types = _CWlShmPoolCreateBufferTypes + 0},
    { .name = "destroy", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "resize", .signature = "i", .types = _CWlShmPoolResizeTypes + 0},
};

const wl_interface wl_shm_pool_interface = {
    .name = "wl_shm_pool", .version = 3,
    .method_count = 3, .methods = _CWlShmPoolRequests,
    .event_count = 0, .events = nullptr,
};

CWlShmPool::CWlShmPool(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_shm_pool_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlShmPool__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlShmPoolVTable, this, nullptr);
}

CWlShmPool::~CWlShmPool() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlShmPool::onDestroyCalled() {
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

void CWlShmPool::setCreateBuffer(F<void(CWlShmPool*, uint32_t, int32_t, int32_t, int32_t, int32_t, uint32_t)> &&handler) {
    requests.createBuffer = std::move(handler);
}

void CWlShmPool::setDestroy(F<void(CWlShmPool*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWlShmPool::setResize(F<void(CWlShmPool*, int32_t)> &&handler) {
    requests.resize = std::move(handler);
}

static void _CWlShmCreatePool(wl_client* client, wl_resource* resource, uint32_t id, int32_t fd, int32_t size) {
    const auto PO = (CWlShm*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createPool)
        PO->requests.createPool(PO, id, fd, size);
}

static void _CWlShmRelease(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlShm*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWlShm__DestroyListener(wl_listener* l, void* d) {
    CWlShmDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlShm* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlShmVTable[] = {
    (void*)_CWlShmCreatePool,
    (void*)_CWlShmRelease,
};

void CWlShm::sendFormat(enum wl_shm_format format) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format);
}

void CWlShm::sendFormatRaw(enum wl_shm_format format) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format);
}
static const wl_interface* _CWlShmCreatePoolTypes[] = {
    &wl_shm_pool_interface,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlShmFormatTypes[] = {
    nullptr,
};

static const wl_message _CWlShmRequests[] = {
    { .name = "create_pool", .signature = "nhi", .types = _CWlShmCreatePoolTypes + 0},
    { .name = "release", .signature = "2", .types = wayland_dummyTypes + 0},
};

static const wl_message _CWlShmEvents[] = {
    { .name = "format", .signature = "u", .types = _CWlShmFormatTypes + 0},
};

const wl_interface wl_shm_interface = {
    .name = "wl_shm", .version = 3,
    .method_count = 2, .methods = _CWlShmRequests,
    .event_count = 1, .events = _CWlShmEvents,
};

CWlShm::CWlShm(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_shm_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlShm__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlShmVTable, this, nullptr);
}

CWlShm::~CWlShm() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlShm::onDestroyCalled() {
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

void CWlShm::setCreatePool(F<void(CWlShm*, uint32_t, int32_t, int32_t)> &&handler) {
    requests.createPool = std::move(handler);
}

void CWlShm::setRelease(F<void(CWlShm*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWlBufferDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlBuffer*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWlBuffer__DestroyListener(wl_listener* l, void* d) {
    CWlBufferDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlBuffer* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlBufferVTable[] = {
    (void*)_CWlBufferDestroy,
};

void CWlBuffer::sendRelease() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CWlBuffer::sendReleaseRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

static const wl_message _CWlBufferRequests[] = {
    { .name = "destroy", .signature = "", .types = wayland_dummyTypes + 0},
};

static const wl_message _CWlBufferEvents[] = {
    { .name = "release", .signature = "", .types = wayland_dummyTypes + 0},
};

const wl_interface wl_buffer_interface = {
    .name = "wl_buffer", .version = 1,
    .method_count = 1, .methods = _CWlBufferRequests,
    .event_count = 1, .events = _CWlBufferEvents,
};

CWlBuffer::CWlBuffer(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_buffer_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlBuffer__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlBufferVTable, this, nullptr);
}

CWlBuffer::~CWlBuffer() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlBuffer::onDestroyCalled() {
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

void CWlBuffer::setDestroy(F<void(CWlBuffer*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CWlDataOfferAccept(wl_client* client, wl_resource* resource, uint32_t serial, const char* mime_type) {
    const auto PO = (CWlDataOffer*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.accept)
        PO->requests.accept(PO, serial, mime_type);
}

static void _CWlDataOfferReceive(wl_client* client, wl_resource* resource, const char* mime_type, int32_t fd) {
    const auto PO = (CWlDataOffer*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.receive)
        PO->requests.receive(PO, mime_type, fd);
}

static void _CWlDataOfferDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlDataOffer*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWlDataOfferFinish(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlDataOffer*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.finish)
        PO->requests.finish(PO);
}

static void _CWlDataOfferSetActions(wl_client* client, wl_resource* resource, uint32_t dnd_actions, uint32_t preferred_action) {
    const auto PO = (CWlDataOffer*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setActions)
        PO->requests.setActions(PO, dnd_actions, preferred_action);
}

static void _CWlDataOffer__DestroyListener(wl_listener* l, void* d) {
    CWlDataOfferDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlDataOffer* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlDataOfferVTable[] = {
    (void*)_CWlDataOfferAccept,
    (void*)_CWlDataOfferReceive,
    (void*)_CWlDataOfferDestroy,
    (void*)_CWlDataOfferFinish,
    (void*)_CWlDataOfferSetActions,
};

void CWlDataOffer::sendOffer(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}

void CWlDataOffer::sendSourceActions(uint32_t source_actions) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, source_actions);
}

void CWlDataOffer::sendAction(uint32_t dnd_action) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, dnd_action);
}

void CWlDataOffer::sendOfferRaw(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}

void CWlDataOffer::sendSourceActionsRaw(uint32_t source_actions) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, source_actions);
}

void CWlDataOffer::sendActionRaw(uint32_t dnd_action) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, dnd_action);
}
static const wl_interface* _CWlDataOfferAcceptTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlDataOfferReceiveTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlDataOfferSetActionsTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlDataOfferOfferTypes[] = {
    nullptr,
};
static const wl_interface* _CWlDataOfferSourceActionsTypes[] = {
    nullptr,
};
static const wl_interface* _CWlDataOfferActionTypes[] = {
    nullptr,
};

static const wl_message _CWlDataOfferRequests[] = {
    { .name = "accept", .signature = "u?s", .types = _CWlDataOfferAcceptTypes + 0},
    { .name = "receive", .signature = "sh", .types = _CWlDataOfferReceiveTypes + 0},
    { .name = "destroy", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "finish", .signature = "3", .types = wayland_dummyTypes + 0},
    { .name = "set_actions", .signature = "3uu", .types = _CWlDataOfferSetActionsTypes + 0},
};

static const wl_message _CWlDataOfferEvents[] = {
    { .name = "offer", .signature = "s", .types = _CWlDataOfferOfferTypes + 0},
    { .name = "source_actions", .signature = "3u", .types = _CWlDataOfferSourceActionsTypes + 0},
    { .name = "action", .signature = "3u", .types = _CWlDataOfferActionTypes + 0},
};

const wl_interface wl_data_offer_interface = {
    .name = "wl_data_offer", .version = 4,
    .method_count = 5, .methods = _CWlDataOfferRequests,
    .event_count = 3, .events = _CWlDataOfferEvents,
};

CWlDataOffer::CWlDataOffer(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_data_offer_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlDataOffer__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlDataOfferVTable, this, nullptr);
}

CWlDataOffer::~CWlDataOffer() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlDataOffer::onDestroyCalled() {
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

void CWlDataOffer::setAccept(F<void(CWlDataOffer*, uint32_t, const char*)> &&handler) {
    requests.accept = std::move(handler);
}

void CWlDataOffer::setReceive(F<void(CWlDataOffer*, const char*, int32_t)> &&handler) {
    requests.receive = std::move(handler);
}

void CWlDataOffer::setDestroy(F<void(CWlDataOffer*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWlDataOffer::setFinish(F<void(CWlDataOffer*)> &&handler) {
    requests.finish = std::move(handler);
}

void CWlDataOffer::setSetActions(F<void(CWlDataOffer*, uint32_t, uint32_t)> &&handler) {
    requests.setActions = std::move(handler);
}

static void _CWlDataSourceOffer(wl_client* client, wl_resource* resource, const char* mime_type) {
    const auto PO = (CWlDataSource*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.offer)
        PO->requests.offer(PO, mime_type);
}

static void _CWlDataSourceDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlDataSource*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWlDataSourceSetActions(wl_client* client, wl_resource* resource, uint32_t dnd_actions) {
    const auto PO = (CWlDataSource*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setActions)
        PO->requests.setActions(PO, dnd_actions);
}

static void _CWlDataSource__DestroyListener(wl_listener* l, void* d) {
    CWlDataSourceDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlDataSource* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlDataSourceVTable[] = {
    (void*)_CWlDataSourceOffer,
    (void*)_CWlDataSourceDestroy,
    (void*)_CWlDataSourceSetActions,
};

void CWlDataSource::sendTarget(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}

void CWlDataSource::sendSend(const char* mime_type, int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, mime_type, fd);
}

void CWlDataSource::sendCancelled() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CWlDataSource::sendDndDropPerformed() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CWlDataSource::sendDndFinished() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CWlDataSource::sendAction(uint32_t dnd_action) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, dnd_action);
}

void CWlDataSource::sendTargetRaw(const char* mime_type) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, mime_type);
}

void CWlDataSource::sendSendRaw(const char* mime_type, int32_t fd) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, mime_type, fd);
}

void CWlDataSource::sendCancelledRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CWlDataSource::sendDndDropPerformedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CWlDataSource::sendDndFinishedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CWlDataSource::sendActionRaw(uint32_t dnd_action) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, dnd_action);
}
static const wl_interface* _CWlDataSourceOfferTypes[] = {
    nullptr,
};
static const wl_interface* _CWlDataSourceSetActionsTypes[] = {
    nullptr,
};
static const wl_interface* _CWlDataSourceTargetTypes[] = {
    nullptr,
};
static const wl_interface* _CWlDataSourceSendTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlDataSourceActionTypes[] = {
    nullptr,
};

static const wl_message _CWlDataSourceRequests[] = {
    { .name = "offer", .signature = "s", .types = _CWlDataSourceOfferTypes + 0},
    { .name = "destroy", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "set_actions", .signature = "3u", .types = _CWlDataSourceSetActionsTypes + 0},
};

static const wl_message _CWlDataSourceEvents[] = {
    { .name = "target", .signature = "?s", .types = _CWlDataSourceTargetTypes + 0},
    { .name = "send", .signature = "sh", .types = _CWlDataSourceSendTypes + 0},
    { .name = "cancelled", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "dnd_drop_performed", .signature = "3", .types = wayland_dummyTypes + 0},
    { .name = "dnd_finished", .signature = "3", .types = wayland_dummyTypes + 0},
    { .name = "action", .signature = "3u", .types = _CWlDataSourceActionTypes + 0},
};

const wl_interface wl_data_source_interface = {
    .name = "wl_data_source", .version = 4,
    .method_count = 3, .methods = _CWlDataSourceRequests,
    .event_count = 6, .events = _CWlDataSourceEvents,
};

CWlDataSource::CWlDataSource(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_data_source_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlDataSource__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlDataSourceVTable, this, nullptr);
}

CWlDataSource::~CWlDataSource() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlDataSource::onDestroyCalled() {
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

void CWlDataSource::setOffer(F<void(CWlDataSource*, const char*)> &&handler) {
    requests.offer = std::move(handler);
}

void CWlDataSource::setDestroy(F<void(CWlDataSource*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWlDataSource::setSetActions(F<void(CWlDataSource*, uint32_t)> &&handler) {
    requests.setActions = std::move(handler);
}

static void _CWlDataDeviceStartDrag(wl_client* client, wl_resource* resource, wl_resource* source, wl_resource* origin, wl_resource* icon, uint32_t serial) {
    const auto PO = (CWlDataDevice*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.startDrag)
        PO->requests.startDrag(PO, source, origin, icon, serial);
}

static void _CWlDataDeviceSetSelection(wl_client* client, wl_resource* resource, wl_resource* source, uint32_t serial) {
    const auto PO = (CWlDataDevice*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setSelection)
        PO->requests.setSelection(PO, source, serial);
}

static void _CWlDataDeviceRelease(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlDataDevice*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWlDataDevice__DestroyListener(wl_listener* l, void* d) {
    CWlDataDeviceDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlDataDevice* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlDataDeviceVTable[] = {
    (void*)_CWlDataDeviceStartDrag,
    (void*)_CWlDataDeviceSetSelection,
    (void*)_CWlDataDeviceRelease,
};

void CWlDataDevice::sendDataOffer(CWlDataOffer* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, id ? id->pResource : nullptr);
}

void CWlDataDevice::sendEnter(uint32_t serial, CWlSurface* surface, wl_fixed_t x, wl_fixed_t y, CWlDataOffer* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, surface ? surface->pResource : nullptr, x, y, id ? id->pResource : nullptr);
}

void CWlDataDevice::sendLeave() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CWlDataDevice::sendMotion(uint32_t time, wl_fixed_t x, wl_fixed_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, time, x, y);
}

void CWlDataDevice::sendDrop() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CWlDataDevice::sendSelection(CWlDataOffer* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, id ? id->pResource : nullptr);
}

void CWlDataDevice::sendDataOfferRaw(CWlDataOffer* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, id);
}

void CWlDataDevice::sendEnterRaw(uint32_t serial, wl_resource* surface, wl_fixed_t x, wl_fixed_t y, wl_resource* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, surface, x, y, id);
}

void CWlDataDevice::sendLeaveRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CWlDataDevice::sendMotionRaw(uint32_t time, wl_fixed_t x, wl_fixed_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, time, x, y);
}

void CWlDataDevice::sendDropRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CWlDataDevice::sendSelectionRaw(wl_resource* id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, id);
}
static const wl_interface* _CWlDataDeviceStartDragTypes[] = {
    &wl_data_source_interface,
    &wl_surface_interface,
    &wl_surface_interface,
    nullptr,
};
static const wl_interface* _CWlDataDeviceSetSelectionTypes[] = {
    &wl_data_source_interface,
    nullptr,
};
static const wl_interface* _CWlDataDeviceDataOfferTypes[] = {
    &wl_data_offer_interface,
};
static const wl_interface* _CWlDataDeviceEnterTypes[] = {
    nullptr,
    &wl_surface_interface,
    nullptr,
    nullptr,
    &wl_data_offer_interface,
};
static const wl_interface* _CWlDataDeviceMotionTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlDataDeviceSelectionTypes[] = {
    &wl_data_offer_interface,
};

static const wl_message _CWlDataDeviceRequests[] = {
    { .name = "start_drag", .signature = "?oo?ou", .types = _CWlDataDeviceStartDragTypes + 0},
    { .name = "set_selection", .signature = "?ou", .types = _CWlDataDeviceSetSelectionTypes + 0},
    { .name = "release", .signature = "2", .types = wayland_dummyTypes + 0},
};

static const wl_message _CWlDataDeviceEvents[] = {
    { .name = "data_offer", .signature = "n", .types = _CWlDataDeviceDataOfferTypes + 0},
    { .name = "enter", .signature = "uoff?o", .types = _CWlDataDeviceEnterTypes + 0},
    { .name = "leave", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "motion", .signature = "uff", .types = _CWlDataDeviceMotionTypes + 0},
    { .name = "drop", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "selection", .signature = "?o", .types = _CWlDataDeviceSelectionTypes + 0},
};

const wl_interface wl_data_device_interface = {
    .name = "wl_data_device", .version = 4,
    .method_count = 3, .methods = _CWlDataDeviceRequests,
    .event_count = 6, .events = _CWlDataDeviceEvents,
};

CWlDataDevice::CWlDataDevice(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_data_device_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlDataDevice__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlDataDeviceVTable, this, nullptr);
}

CWlDataDevice::~CWlDataDevice() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlDataDevice::onDestroyCalled() {
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

void CWlDataDevice::setStartDrag(F<void(CWlDataDevice*, wl_resource*, wl_resource*, wl_resource*, uint32_t)> &&handler) {
    requests.startDrag = std::move(handler);
}

void CWlDataDevice::setSetSelection(F<void(CWlDataDevice*, wl_resource*, uint32_t)> &&handler) {
    requests.setSelection = std::move(handler);
}

void CWlDataDevice::setRelease(F<void(CWlDataDevice*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWlDataDeviceManagerCreateDataSource(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CWlDataDeviceManager*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createDataSource)
        PO->requests.createDataSource(PO, id);
}

static void _CWlDataDeviceManagerGetDataDevice(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* seat) {
    const auto PO = (CWlDataDeviceManager*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getDataDevice)
        PO->requests.getDataDevice(PO, id, seat);
}

static void _CWlDataDeviceManagerRelease(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlDataDeviceManager*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWlDataDeviceManager__DestroyListener(wl_listener* l, void* d) {
    CWlDataDeviceManagerDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlDataDeviceManager* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlDataDeviceManagerVTable[] = {
    (void*)_CWlDataDeviceManagerCreateDataSource,
    (void*)_CWlDataDeviceManagerGetDataDevice,
    (void*)_CWlDataDeviceManagerRelease,
};
static const wl_interface* _CWlDataDeviceManagerCreateDataSourceTypes[] = {
    &wl_data_source_interface,
};
static const wl_interface* _CWlDataDeviceManagerGetDataDeviceTypes[] = {
    &wl_data_device_interface,
    &wl_seat_interface,
};

static const wl_message _CWlDataDeviceManagerRequests[] = {
    { .name = "create_data_source", .signature = "n", .types = _CWlDataDeviceManagerCreateDataSourceTypes + 0},
    { .name = "get_data_device", .signature = "no", .types = _CWlDataDeviceManagerGetDataDeviceTypes + 0},
    { .name = "release", .signature = "4", .types = wayland_dummyTypes + 0},
};

const wl_interface wl_data_device_manager_interface = {
    .name = "wl_data_device_manager", .version = 4,
    .method_count = 3, .methods = _CWlDataDeviceManagerRequests,
    .event_count = 0, .events = nullptr,
};

CWlDataDeviceManager::CWlDataDeviceManager(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_data_device_manager_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlDataDeviceManager__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlDataDeviceManagerVTable, this, nullptr);
}

CWlDataDeviceManager::~CWlDataDeviceManager() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlDataDeviceManager::onDestroyCalled() {
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

void CWlDataDeviceManager::setCreateDataSource(F<void(CWlDataDeviceManager*, uint32_t)> &&handler) {
    requests.createDataSource = std::move(handler);
}

void CWlDataDeviceManager::setGetDataDevice(F<void(CWlDataDeviceManager*, uint32_t, wl_resource*)> &&handler) {
    requests.getDataDevice = std::move(handler);
}

void CWlDataDeviceManager::setRelease(F<void(CWlDataDeviceManager*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWlShellGetShellSurface(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CWlShell*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getShellSurface)
        PO->requests.getShellSurface(PO, id, surface);
}

static void _CWlShell__DestroyListener(wl_listener* l, void* d) {
    CWlShellDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlShell* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlShellVTable[] = {
    (void*)_CWlShellGetShellSurface,
};
static const wl_interface* _CWlShellGetShellSurfaceTypes[] = {
    &wl_shell_surface_interface,
    &wl_surface_interface,
};

static const wl_message _CWlShellRequests[] = {
    { .name = "get_shell_surface", .signature = "no", .types = _CWlShellGetShellSurfaceTypes + 0},
};

const wl_interface wl_shell_interface = {
    .name = "wl_shell", .version = 1,
    .method_count = 1, .methods = _CWlShellRequests,
    .event_count = 0, .events = nullptr,
};

CWlShell::CWlShell(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_shell_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlShell__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlShellVTable, this, nullptr);
}

CWlShell::~CWlShell() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlShell::onDestroyCalled() {
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

void CWlShell::setGetShellSurface(F<void(CWlShell*, uint32_t, wl_resource*)> &&handler) {
    requests.getShellSurface = std::move(handler);
}

static void _CWlShellSurfacePong(wl_client* client, wl_resource* resource, uint32_t serial) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.pong)
        PO->requests.pong(PO, serial);
}

static void _CWlShellSurfaceMove(wl_client* client, wl_resource* resource, wl_resource* seat, uint32_t serial) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.move)
        PO->requests.move(PO, seat, serial);
}

static void _CWlShellSurfaceResize(wl_client* client, wl_resource* resource, wl_resource* seat, uint32_t serial, enum wl_shell_surface_resize edges) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.resize)
        PO->requests.resize(PO, seat, serial, edges);
}

static void _CWlShellSurfaceSetToplevel(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setToplevel)
        PO->requests.setToplevel(PO);
}

static void _CWlShellSurfaceSetTransient(wl_client* client, wl_resource* resource, wl_resource* parent, int32_t x, int32_t y, enum wl_shell_surface_transient flags) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setTransient)
        PO->requests.setTransient(PO, parent, x, y, flags);
}

static void _CWlShellSurfaceSetFullscreen(wl_client* client, wl_resource* resource, enum wl_shell_surface_fullscreen_method method, uint32_t framerate, wl_resource* output) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setFullscreen)
        PO->requests.setFullscreen(PO, method, framerate, output);
}

static void _CWlShellSurfaceSetPopup(wl_client* client, wl_resource* resource, wl_resource* seat, uint32_t serial, wl_resource* parent, int32_t x, int32_t y, enum wl_shell_surface_transient flags) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setPopup)
        PO->requests.setPopup(PO, seat, serial, parent, x, y, flags);
}

static void _CWlShellSurfaceSetMaximized(wl_client* client, wl_resource* resource, wl_resource* output) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setMaximized)
        PO->requests.setMaximized(PO, output);
}

static void _CWlShellSurfaceSetTitle(wl_client* client, wl_resource* resource, const char* title) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setTitle)
        PO->requests.setTitle(PO, title);
}

static void _CWlShellSurfaceSetClass(wl_client* client, wl_resource* resource, const char* class_) {
    const auto PO = (CWlShellSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setClass)
        PO->requests.setClass(PO, class_);
}

static void _CWlShellSurface__DestroyListener(wl_listener* l, void* d) {
    CWlShellSurfaceDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlShellSurface* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlShellSurfaceVTable[] = {
    (void*)_CWlShellSurfacePong,
    (void*)_CWlShellSurfaceMove,
    (void*)_CWlShellSurfaceResize,
    (void*)_CWlShellSurfaceSetToplevel,
    (void*)_CWlShellSurfaceSetTransient,
    (void*)_CWlShellSurfaceSetFullscreen,
    (void*)_CWlShellSurfaceSetPopup,
    (void*)_CWlShellSurfaceSetMaximized,
    (void*)_CWlShellSurfaceSetTitle,
    (void*)_CWlShellSurfaceSetClass,
};

void CWlShellSurface::sendPing(uint32_t serial) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial);
}

void CWlShellSurface::sendConfigure(enum wl_shell_surface_resize edges, int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, edges, width, height);
}

void CWlShellSurface::sendPopupDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CWlShellSurface::sendPingRaw(uint32_t serial) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial);
}

void CWlShellSurface::sendConfigureRaw(enum wl_shell_surface_resize edges, int32_t width, int32_t height) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, edges, width, height);
}

void CWlShellSurface::sendPopupDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}
static const wl_interface* _CWlShellSurfacePongTypes[] = {
    nullptr,
};
static const wl_interface* _CWlShellSurfaceMoveTypes[] = {
    &wl_seat_interface,
    nullptr,
};
static const wl_interface* _CWlShellSurfaceResizeTypes[] = {
    &wl_seat_interface,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlShellSurfaceSetTransientTypes[] = {
    &wl_surface_interface,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlShellSurfaceSetFullscreenTypes[] = {
    nullptr,
    nullptr,
    &wl_output_interface,
};
static const wl_interface* _CWlShellSurfaceSetPopupTypes[] = {
    &wl_seat_interface,
    nullptr,
    &wl_surface_interface,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlShellSurfaceSetMaximizedTypes[] = {
    &wl_output_interface,
};
static const wl_interface* _CWlShellSurfaceSetTitleTypes[] = {
    nullptr,
};
static const wl_interface* _CWlShellSurfaceSetClassTypes[] = {
    nullptr,
};
static const wl_interface* _CWlShellSurfacePingTypes[] = {
    nullptr,
};
static const wl_interface* _CWlShellSurfaceConfigureTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CWlShellSurfaceRequests[] = {
    { .name = "pong", .signature = "u", .types = _CWlShellSurfacePongTypes + 0},
    { .name = "move", .signature = "ou", .types = _CWlShellSurfaceMoveTypes + 0},
    { .name = "resize", .signature = "ouu", .types = _CWlShellSurfaceResizeTypes + 0},
    { .name = "set_toplevel", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "set_transient", .signature = "oiiu", .types = _CWlShellSurfaceSetTransientTypes + 0},
    { .name = "set_fullscreen", .signature = "uu?o", .types = _CWlShellSurfaceSetFullscreenTypes + 0},
    { .name = "set_popup", .signature = "ouoiiu", .types = _CWlShellSurfaceSetPopupTypes + 0},
    { .name = "set_maximized", .signature = "?o", .types = _CWlShellSurfaceSetMaximizedTypes + 0},
    { .name = "set_title", .signature = "s", .types = _CWlShellSurfaceSetTitleTypes + 0},
    { .name = "set_class", .signature = "s", .types = _CWlShellSurfaceSetClassTypes + 0},
};

static const wl_message _CWlShellSurfaceEvents[] = {
    { .name = "ping", .signature = "u", .types = _CWlShellSurfacePingTypes + 0},
    { .name = "configure", .signature = "uii", .types = _CWlShellSurfaceConfigureTypes + 0},
    { .name = "popup_done", .signature = "", .types = wayland_dummyTypes + 0},
};

const wl_interface wl_shell_surface_interface = {
    .name = "wl_shell_surface", .version = 1,
    .method_count = 10, .methods = _CWlShellSurfaceRequests,
    .event_count = 3, .events = _CWlShellSurfaceEvents,
};

CWlShellSurface::CWlShellSurface(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_shell_surface_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlShellSurface__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlShellSurfaceVTable, this, nullptr);
}

CWlShellSurface::~CWlShellSurface() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlShellSurface::onDestroyCalled() {
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

void CWlShellSurface::setPong(F<void(CWlShellSurface*, uint32_t)> &&handler) {
    requests.pong = std::move(handler);
}

void CWlShellSurface::setMove(F<void(CWlShellSurface*, wl_resource*, uint32_t)> &&handler) {
    requests.move = std::move(handler);
}

void CWlShellSurface::setResize(F<void(CWlShellSurface*, wl_resource*, uint32_t, enum wl_shell_surface_resize)> &&handler) {
    requests.resize = std::move(handler);
}

void CWlShellSurface::setSetToplevel(F<void(CWlShellSurface*)> &&handler) {
    requests.setToplevel = std::move(handler);
}

void CWlShellSurface::setSetTransient(F<void(CWlShellSurface*, wl_resource*, int32_t, int32_t, enum wl_shell_surface_transient)> &&handler) {
    requests.setTransient = std::move(handler);
}

void CWlShellSurface::setSetFullscreen(F<void(CWlShellSurface*, enum wl_shell_surface_fullscreen_method, uint32_t, wl_resource*)> &&handler) {
    requests.setFullscreen = std::move(handler);
}

void CWlShellSurface::setSetPopup(F<void(CWlShellSurface*, wl_resource*, uint32_t, wl_resource*, int32_t, int32_t, enum wl_shell_surface_transient)> &&handler) {
    requests.setPopup = std::move(handler);
}

void CWlShellSurface::setSetMaximized(F<void(CWlShellSurface*, wl_resource*)> &&handler) {
    requests.setMaximized = std::move(handler);
}

void CWlShellSurface::setSetTitle(F<void(CWlShellSurface*, const char*)> &&handler) {
    requests.setTitle = std::move(handler);
}

void CWlShellSurface::setSetClass(F<void(CWlShellSurface*, const char*)> &&handler) {
    requests.setClass = std::move(handler);
}

static void _CWlSurfaceDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWlSurfaceAttach(wl_client* client, wl_resource* resource, wl_resource* buffer, int32_t x, int32_t y) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.attach)
        PO->requests.attach(PO, buffer, x, y);
}

static void _CWlSurfaceDamage(wl_client* client, wl_resource* resource, int32_t x, int32_t y, int32_t width, int32_t height) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.damage)
        PO->requests.damage(PO, x, y, width, height);
}

static void _CWlSurfaceFrame(wl_client* client, wl_resource* resource, uint32_t callback) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.frame)
        PO->requests.frame(PO, callback);
}

static void _CWlSurfaceSetOpaqueRegion(wl_client* client, wl_resource* resource, wl_resource* region) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setOpaqueRegion)
        PO->requests.setOpaqueRegion(PO, region);
}

static void _CWlSurfaceSetInputRegion(wl_client* client, wl_resource* resource, wl_resource* region) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setInputRegion)
        PO->requests.setInputRegion(PO, region);
}

static void _CWlSurfaceCommit(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.commit)
        PO->requests.commit(PO);
}

static void _CWlSurfaceSetBufferTransform(wl_client* client, wl_resource* resource, int32_t transform) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setBufferTransform)
        PO->requests.setBufferTransform(PO, transform);
}

static void _CWlSurfaceSetBufferScale(wl_client* client, wl_resource* resource, int32_t scale) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setBufferScale)
        PO->requests.setBufferScale(PO, scale);
}

static void _CWlSurfaceDamageBuffer(wl_client* client, wl_resource* resource, int32_t x, int32_t y, int32_t width, int32_t height) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.damageBuffer)
        PO->requests.damageBuffer(PO, x, y, width, height);
}

static void _CWlSurfaceOffset(wl_client* client, wl_resource* resource, int32_t x, int32_t y) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.offset)
        PO->requests.offset(PO, x, y);
}

static void _CWlSurfaceGetRelease(wl_client* client, wl_resource* resource, uint32_t callback) {
    const auto PO = (CWlSurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getRelease)
        PO->requests.getRelease(PO, callback);
}

static void _CWlSurface__DestroyListener(wl_listener* l, void* d) {
    CWlSurfaceDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlSurface* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlSurfaceVTable[] = {
    (void*)_CWlSurfaceDestroy,
    (void*)_CWlSurfaceAttach,
    (void*)_CWlSurfaceDamage,
    (void*)_CWlSurfaceFrame,
    (void*)_CWlSurfaceSetOpaqueRegion,
    (void*)_CWlSurfaceSetInputRegion,
    (void*)_CWlSurfaceCommit,
    (void*)_CWlSurfaceSetBufferTransform,
    (void*)_CWlSurfaceSetBufferScale,
    (void*)_CWlSurfaceDamageBuffer,
    (void*)_CWlSurfaceOffset,
    (void*)_CWlSurfaceGetRelease,
};

void CWlSurface::sendEnter(CWlOutput* output) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, output ? output->pResource : nullptr);
}

void CWlSurface::sendLeave(CWlOutput* output) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, output ? output->pResource : nullptr);
}

void CWlSurface::sendPreferredBufferScale(int32_t factor) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, factor);
}

void CWlSurface::sendPreferredBufferTransform(uint32_t transform) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, transform);
}

void CWlSurface::sendEnterRaw(wl_resource* output) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, output);
}

void CWlSurface::sendLeaveRaw(wl_resource* output) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, output);
}

void CWlSurface::sendPreferredBufferScaleRaw(int32_t factor) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, factor);
}

void CWlSurface::sendPreferredBufferTransformRaw(uint32_t transform) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, transform);
}
static const wl_interface* _CWlSurfaceAttachTypes[] = {
    &wl_buffer_interface,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlSurfaceDamageTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlSurfaceFrameTypes[] = {
    &wl_callback_interface,
};
static const wl_interface* _CWlSurfaceSetOpaqueRegionTypes[] = {
    &wl_region_interface,
};
static const wl_interface* _CWlSurfaceSetInputRegionTypes[] = {
    &wl_region_interface,
};
static const wl_interface* _CWlSurfaceSetBufferTransformTypes[] = {
    nullptr,
};
static const wl_interface* _CWlSurfaceSetBufferScaleTypes[] = {
    nullptr,
};
static const wl_interface* _CWlSurfaceDamageBufferTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlSurfaceOffsetTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlSurfaceGetReleaseTypes[] = {
    &wl_callback_interface,
};
static const wl_interface* _CWlSurfaceEnterTypes[] = {
    &wl_output_interface,
};
static const wl_interface* _CWlSurfaceLeaveTypes[] = {
    &wl_output_interface,
};
static const wl_interface* _CWlSurfacePreferredBufferScaleTypes[] = {
    nullptr,
};
static const wl_interface* _CWlSurfacePreferredBufferTransformTypes[] = {
    nullptr,
};

static const wl_message _CWlSurfaceRequests[] = {
    { .name = "destroy", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "attach", .signature = "?oii", .types = _CWlSurfaceAttachTypes + 0},
    { .name = "damage", .signature = "iiii", .types = _CWlSurfaceDamageTypes + 0},
    { .name = "frame", .signature = "n", .types = _CWlSurfaceFrameTypes + 0},
    { .name = "set_opaque_region", .signature = "?o", .types = _CWlSurfaceSetOpaqueRegionTypes + 0},
    { .name = "set_input_region", .signature = "?o", .types = _CWlSurfaceSetInputRegionTypes + 0},
    { .name = "commit", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "set_buffer_transform", .signature = "2i", .types = _CWlSurfaceSetBufferTransformTypes + 0},
    { .name = "set_buffer_scale", .signature = "3i", .types = _CWlSurfaceSetBufferScaleTypes + 0},
    { .name = "damage_buffer", .signature = "4iiii", .types = _CWlSurfaceDamageBufferTypes + 0},
    { .name = "offset", .signature = "5ii", .types = _CWlSurfaceOffsetTypes + 0},
    { .name = "get_release", .signature = "7n", .types = _CWlSurfaceGetReleaseTypes + 0},
};

static const wl_message _CWlSurfaceEvents[] = {
    { .name = "enter", .signature = "o", .types = _CWlSurfaceEnterTypes + 0},
    { .name = "leave", .signature = "o", .types = _CWlSurfaceLeaveTypes + 0},
    { .name = "preferred_buffer_scale", .signature = "6i", .types = _CWlSurfacePreferredBufferScaleTypes + 0},
    { .name = "preferred_buffer_transform", .signature = "6u", .types = _CWlSurfacePreferredBufferTransformTypes + 0},
};

const wl_interface wl_surface_interface = {
    .name = "wl_surface", .version = 7,
    .method_count = 12, .methods = _CWlSurfaceRequests,
    .event_count = 4, .events = _CWlSurfaceEvents,
};

CWlSurface::CWlSurface(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_surface_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlSurface__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlSurfaceVTable, this, nullptr);
}

CWlSurface::~CWlSurface() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlSurface::onDestroyCalled() {
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

void CWlSurface::setDestroy(F<void(CWlSurface*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWlSurface::setAttach(F<void(CWlSurface*, wl_resource*, int32_t, int32_t)> &&handler) {
    requests.attach = std::move(handler);
}

void CWlSurface::setDamage(F<void(CWlSurface*, int32_t, int32_t, int32_t, int32_t)> &&handler) {
    requests.damage = std::move(handler);
}

void CWlSurface::setFrame(F<void(CWlSurface*, uint32_t)> &&handler) {
    requests.frame = std::move(handler);
}

void CWlSurface::setSetOpaqueRegion(F<void(CWlSurface*, wl_resource*)> &&handler) {
    requests.setOpaqueRegion = std::move(handler);
}

void CWlSurface::setSetInputRegion(F<void(CWlSurface*, wl_resource*)> &&handler) {
    requests.setInputRegion = std::move(handler);
}

void CWlSurface::setCommit(F<void(CWlSurface*)> &&handler) {
    requests.commit = std::move(handler);
}

void CWlSurface::setSetBufferTransform(F<void(CWlSurface*, int32_t)> &&handler) {
    requests.setBufferTransform = std::move(handler);
}

void CWlSurface::setSetBufferScale(F<void(CWlSurface*, int32_t)> &&handler) {
    requests.setBufferScale = std::move(handler);
}

void CWlSurface::setDamageBuffer(F<void(CWlSurface*, int32_t, int32_t, int32_t, int32_t)> &&handler) {
    requests.damageBuffer = std::move(handler);
}

void CWlSurface::setOffset(F<void(CWlSurface*, int32_t, int32_t)> &&handler) {
    requests.offset = std::move(handler);
}

void CWlSurface::setGetRelease(F<void(CWlSurface*, uint32_t)> &&handler) {
    requests.getRelease = std::move(handler);
}

static void _CWlSeatGetPointer(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CWlSeat*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getPointer)
        PO->requests.getPointer(PO, id);
}

static void _CWlSeatGetKeyboard(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CWlSeat*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getKeyboard)
        PO->requests.getKeyboard(PO, id);
}

static void _CWlSeatGetTouch(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CWlSeat*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getTouch)
        PO->requests.getTouch(PO, id);
}

static void _CWlSeatRelease(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlSeat*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWlSeat__DestroyListener(wl_listener* l, void* d) {
    CWlSeatDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlSeat* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlSeatVTable[] = {
    (void*)_CWlSeatGetPointer,
    (void*)_CWlSeatGetKeyboard,
    (void*)_CWlSeatGetTouch,
    (void*)_CWlSeatRelease,
};

void CWlSeat::sendCapabilities(enum wl_seat_capability capabilities) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, capabilities);
}

void CWlSeat::sendName(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, name);
}

void CWlSeat::sendCapabilitiesRaw(enum wl_seat_capability capabilities) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, capabilities);
}

void CWlSeat::sendNameRaw(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, name);
}
static const wl_interface* _CWlSeatGetPointerTypes[] = {
    &wl_pointer_interface,
};
static const wl_interface* _CWlSeatGetKeyboardTypes[] = {
    &wl_keyboard_interface,
};
static const wl_interface* _CWlSeatGetTouchTypes[] = {
    &wl_touch_interface,
};
static const wl_interface* _CWlSeatCapabilitiesTypes[] = {
    nullptr,
};
static const wl_interface* _CWlSeatNameTypes[] = {
    nullptr,
};

static const wl_message _CWlSeatRequests[] = {
    { .name = "get_pointer", .signature = "n", .types = _CWlSeatGetPointerTypes + 0},
    { .name = "get_keyboard", .signature = "n", .types = _CWlSeatGetKeyboardTypes + 0},
    { .name = "get_touch", .signature = "n", .types = _CWlSeatGetTouchTypes + 0},
    { .name = "release", .signature = "5", .types = wayland_dummyTypes + 0},
};

static const wl_message _CWlSeatEvents[] = {
    { .name = "capabilities", .signature = "u", .types = _CWlSeatCapabilitiesTypes + 0},
    { .name = "name", .signature = "2s", .types = _CWlSeatNameTypes + 0},
};

const wl_interface wl_seat_interface = {
    .name = "wl_seat", .version = 11,
    .method_count = 4, .methods = _CWlSeatRequests,
    .event_count = 2, .events = _CWlSeatEvents,
};

CWlSeat::CWlSeat(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_seat_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlSeat__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlSeatVTable, this, nullptr);
}

CWlSeat::~CWlSeat() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlSeat::onDestroyCalled() {
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

void CWlSeat::setGetPointer(F<void(CWlSeat*, uint32_t)> &&handler) {
    requests.getPointer = std::move(handler);
}

void CWlSeat::setGetKeyboard(F<void(CWlSeat*, uint32_t)> &&handler) {
    requests.getKeyboard = std::move(handler);
}

void CWlSeat::setGetTouch(F<void(CWlSeat*, uint32_t)> &&handler) {
    requests.getTouch = std::move(handler);
}

void CWlSeat::setRelease(F<void(CWlSeat*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWlPointerSetCursor(wl_client* client, wl_resource* resource, uint32_t serial, wl_resource* surface, int32_t hotspot_x, int32_t hotspot_y) {
    const auto PO = (CWlPointer*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setCursor)
        PO->requests.setCursor(PO, serial, surface, hotspot_x, hotspot_y);
}

static void _CWlPointerRelease(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlPointer*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWlPointer__DestroyListener(wl_listener* l, void* d) {
    CWlPointerDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlPointer* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlPointerVTable[] = {
    (void*)_CWlPointerSetCursor,
    (void*)_CWlPointerRelease,
};

void CWlPointer::sendEnter(uint32_t serial, CWlSurface* surface, wl_fixed_t surface_x, wl_fixed_t surface_y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, surface ? surface->pResource : nullptr, surface_x, surface_y);
}

void CWlPointer::sendLeave(uint32_t serial, CWlSurface* surface) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, surface ? surface->pResource : nullptr);
}

void CWlPointer::sendMotion(uint32_t time, wl_fixed_t surface_x, wl_fixed_t surface_y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, time, surface_x, surface_y);
}

void CWlPointer::sendButton(uint32_t serial, uint32_t time, uint32_t button, enum wl_pointer_button_state state) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, serial, time, button, state);
}

void CWlPointer::sendAxis(uint32_t time, enum wl_pointer_axis axis, wl_fixed_t value) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, time, axis, value);
}

void CWlPointer::sendFrame() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5);
}

void CWlPointer::sendAxisSource(enum wl_pointer_axis_source axis_source) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6, axis_source);
}

void CWlPointer::sendAxisStop(uint32_t time, enum wl_pointer_axis axis) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 7, time, axis);
}

void CWlPointer::sendAxisDiscrete(enum wl_pointer_axis axis, int32_t discrete) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 8, axis, discrete);
}

void CWlPointer::sendAxisValue120(enum wl_pointer_axis axis, int32_t value120) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 9, axis, value120);
}

void CWlPointer::sendAxisRelativeDirection(enum wl_pointer_axis axis, enum wl_pointer_axis_relative_direction direction) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 10, axis, direction);
}

void CWlPointer::sendWarp(wl_fixed_t surface_x, wl_fixed_t surface_y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 11, surface_x, surface_y);
}

void CWlPointer::sendEnterRaw(uint32_t serial, wl_resource* surface, wl_fixed_t surface_x, wl_fixed_t surface_y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, surface, surface_x, surface_y);
}

void CWlPointer::sendLeaveRaw(uint32_t serial, wl_resource* surface) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, surface);
}

void CWlPointer::sendMotionRaw(uint32_t time, wl_fixed_t surface_x, wl_fixed_t surface_y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, time, surface_x, surface_y);
}

void CWlPointer::sendButtonRaw(uint32_t serial, uint32_t time, uint32_t button, enum wl_pointer_button_state state) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, serial, time, button, state);
}

void CWlPointer::sendAxisRaw(uint32_t time, enum wl_pointer_axis axis, wl_fixed_t value) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, time, axis, value);
}

void CWlPointer::sendFrameRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5);
}

void CWlPointer::sendAxisSourceRaw(enum wl_pointer_axis_source axis_source) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6, axis_source);
}

void CWlPointer::sendAxisStopRaw(uint32_t time, enum wl_pointer_axis axis) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 7, time, axis);
}

void CWlPointer::sendAxisDiscreteRaw(enum wl_pointer_axis axis, int32_t discrete) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 8, axis, discrete);
}

void CWlPointer::sendAxisValue120Raw(enum wl_pointer_axis axis, int32_t value120) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 9, axis, value120);
}

void CWlPointer::sendAxisRelativeDirectionRaw(enum wl_pointer_axis axis, enum wl_pointer_axis_relative_direction direction) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 10, axis, direction);
}

void CWlPointer::sendWarpRaw(wl_fixed_t surface_x, wl_fixed_t surface_y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 11, surface_x, surface_y);
}
static const wl_interface* _CWlPointerSetCursorTypes[] = {
    nullptr,
    &wl_surface_interface,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlPointerEnterTypes[] = {
    nullptr,
    &wl_surface_interface,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlPointerLeaveTypes[] = {
    nullptr,
    &wl_surface_interface,
};
static const wl_interface* _CWlPointerMotionTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlPointerButtonTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlPointerAxisTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlPointerAxisSourceTypes[] = {
    nullptr,
};
static const wl_interface* _CWlPointerAxisStopTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlPointerAxisDiscreteTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlPointerAxisValue120Types[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlPointerAxisRelativeDirectionTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlPointerWarpTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CWlPointerRequests[] = {
    { .name = "set_cursor", .signature = "u?oii", .types = _CWlPointerSetCursorTypes + 0},
    { .name = "release", .signature = "3", .types = wayland_dummyTypes + 0},
};

static const wl_message _CWlPointerEvents[] = {
    { .name = "enter", .signature = "uoff", .types = _CWlPointerEnterTypes + 0},
    { .name = "leave", .signature = "uo", .types = _CWlPointerLeaveTypes + 0},
    { .name = "motion", .signature = "uff", .types = _CWlPointerMotionTypes + 0},
    { .name = "button", .signature = "uuuu", .types = _CWlPointerButtonTypes + 0},
    { .name = "axis", .signature = "uuf", .types = _CWlPointerAxisTypes + 0},
    { .name = "frame", .signature = "5", .types = wayland_dummyTypes + 0},
    { .name = "axis_source", .signature = "5u", .types = _CWlPointerAxisSourceTypes + 0},
    { .name = "axis_stop", .signature = "5uu", .types = _CWlPointerAxisStopTypes + 0},
    { .name = "axis_discrete", .signature = "5ui", .types = _CWlPointerAxisDiscreteTypes + 0},
    { .name = "axis_value120", .signature = "8ui", .types = _CWlPointerAxisValue120Types + 0},
    { .name = "axis_relative_direction", .signature = "9uu", .types = _CWlPointerAxisRelativeDirectionTypes + 0},
    { .name = "warp", .signature = "11ff", .types = _CWlPointerWarpTypes + 0},
};

const wl_interface wl_pointer_interface = {
    .name = "wl_pointer", .version = 11,
    .method_count = 2, .methods = _CWlPointerRequests,
    .event_count = 12, .events = _CWlPointerEvents,
};

CWlPointer::CWlPointer(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_pointer_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlPointer__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlPointerVTable, this, nullptr);
}

CWlPointer::~CWlPointer() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlPointer::onDestroyCalled() {
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

void CWlPointer::setSetCursor(F<void(CWlPointer*, uint32_t, wl_resource*, int32_t, int32_t)> &&handler) {
    requests.setCursor = std::move(handler);
}

void CWlPointer::setRelease(F<void(CWlPointer*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWlKeyboardRelease(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlKeyboard*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWlKeyboard__DestroyListener(wl_listener* l, void* d) {
    CWlKeyboardDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlKeyboard* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlKeyboardVTable[] = {
    (void*)_CWlKeyboardRelease,
};

void CWlKeyboard::sendKeymap(enum wl_keyboard_keymap_format format, int32_t fd, uint32_t size) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format, fd, size);
}

void CWlKeyboard::sendEnter(uint32_t serial, CWlSurface* surface, wl_array* keys) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, surface ? surface->pResource : nullptr, keys);
}

void CWlKeyboard::sendLeave(uint32_t serial, CWlSurface* surface) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, serial, surface ? surface->pResource : nullptr);
}

void CWlKeyboard::sendKey(uint32_t serial, uint32_t time, uint32_t key, enum wl_keyboard_key_state state) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, serial, time, key, state);
}

void CWlKeyboard::sendModifiers(uint32_t serial, uint32_t mods_depressed, uint32_t mods_latched, uint32_t mods_locked, uint32_t group) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, serial, mods_depressed, mods_latched, mods_locked, group);
}

void CWlKeyboard::sendRepeatInfo(int32_t rate, int32_t delay) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, rate, delay);
}

void CWlKeyboard::sendKeymapRaw(enum wl_keyboard_keymap_format format, int32_t fd, uint32_t size) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, format, fd, size);
}

void CWlKeyboard::sendEnterRaw(uint32_t serial, wl_resource* surface, wl_array* keys) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, surface, keys);
}

void CWlKeyboard::sendLeaveRaw(uint32_t serial, wl_resource* surface) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, serial, surface);
}

void CWlKeyboard::sendKeyRaw(uint32_t serial, uint32_t time, uint32_t key, enum wl_keyboard_key_state state) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, serial, time, key, state);
}

void CWlKeyboard::sendModifiersRaw(uint32_t serial, uint32_t mods_depressed, uint32_t mods_latched, uint32_t mods_locked, uint32_t group) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, serial, mods_depressed, mods_latched, mods_locked, group);
}

void CWlKeyboard::sendRepeatInfoRaw(int32_t rate, int32_t delay) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, rate, delay);
}
static const wl_interface* _CWlKeyboardKeymapTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlKeyboardEnterTypes[] = {
    nullptr,
    &wl_surface_interface,
    nullptr,
};
static const wl_interface* _CWlKeyboardLeaveTypes[] = {
    nullptr,
    &wl_surface_interface,
};
static const wl_interface* _CWlKeyboardKeyTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlKeyboardModifiersTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlKeyboardRepeatInfoTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CWlKeyboardRequests[] = {
    { .name = "release", .signature = "3", .types = wayland_dummyTypes + 0},
};

static const wl_message _CWlKeyboardEvents[] = {
    { .name = "keymap", .signature = "uhu", .types = _CWlKeyboardKeymapTypes + 0},
    { .name = "enter", .signature = "uoa", .types = _CWlKeyboardEnterTypes + 0},
    { .name = "leave", .signature = "uo", .types = _CWlKeyboardLeaveTypes + 0},
    { .name = "key", .signature = "uuuu", .types = _CWlKeyboardKeyTypes + 0},
    { .name = "modifiers", .signature = "uuuuu", .types = _CWlKeyboardModifiersTypes + 0},
    { .name = "repeat_info", .signature = "4ii", .types = _CWlKeyboardRepeatInfoTypes + 0},
};

const wl_interface wl_keyboard_interface = {
    .name = "wl_keyboard", .version = 11,
    .method_count = 1, .methods = _CWlKeyboardRequests,
    .event_count = 6, .events = _CWlKeyboardEvents,
};

CWlKeyboard::CWlKeyboard(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_keyboard_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlKeyboard__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlKeyboardVTable, this, nullptr);
}

CWlKeyboard::~CWlKeyboard() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlKeyboard::onDestroyCalled() {
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

void CWlKeyboard::setRelease(F<void(CWlKeyboard*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWlTouchRelease(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlTouch*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWlTouch__DestroyListener(wl_listener* l, void* d) {
    CWlTouchDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlTouch* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlTouchVTable[] = {
    (void*)_CWlTouchRelease,
};

void CWlTouch::sendDown(uint32_t serial, uint32_t time, CWlSurface* surface, int32_t id, wl_fixed_t x, wl_fixed_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, time, surface ? surface->pResource : nullptr, id, x, y);
}

void CWlTouch::sendUp(uint32_t serial, uint32_t time, int32_t id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, time, id);
}

void CWlTouch::sendMotion(uint32_t time, int32_t id, wl_fixed_t x, wl_fixed_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, time, id, x, y);
}

void CWlTouch::sendFrame() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CWlTouch::sendCancel() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CWlTouch::sendShape(int32_t id, wl_fixed_t major, wl_fixed_t minor) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, id, major, minor);
}

void CWlTouch::sendOrientation(int32_t id, wl_fixed_t orientation) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6, id, orientation);
}

void CWlTouch::sendDownRaw(uint32_t serial, uint32_t time, wl_resource* surface, int32_t id, wl_fixed_t x, wl_fixed_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, serial, time, surface, id, x, y);
}

void CWlTouch::sendUpRaw(uint32_t serial, uint32_t time, int32_t id) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, serial, time, id);
}

void CWlTouch::sendMotionRaw(uint32_t time, int32_t id, wl_fixed_t x, wl_fixed_t y) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2, time, id, x, y);
}

void CWlTouch::sendFrameRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3);
}

void CWlTouch::sendCancelRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4);
}

void CWlTouch::sendShapeRaw(int32_t id, wl_fixed_t major, wl_fixed_t minor) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, id, major, minor);
}

void CWlTouch::sendOrientationRaw(int32_t id, wl_fixed_t orientation) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 6, id, orientation);
}
static const wl_interface* _CWlTouchDownTypes[] = {
    nullptr,
    nullptr,
    &wl_surface_interface,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlTouchUpTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlTouchMotionTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlTouchShapeTypes[] = {
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlTouchOrientationTypes[] = {
    nullptr,
    nullptr,
};

static const wl_message _CWlTouchRequests[] = {
    { .name = "release", .signature = "3", .types = wayland_dummyTypes + 0},
};

static const wl_message _CWlTouchEvents[] = {
    { .name = "down", .signature = "uuoiff", .types = _CWlTouchDownTypes + 0},
    { .name = "up", .signature = "uui", .types = _CWlTouchUpTypes + 0},
    { .name = "motion", .signature = "uiff", .types = _CWlTouchMotionTypes + 0},
    { .name = "frame", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "cancel", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "shape", .signature = "6iff", .types = _CWlTouchShapeTypes + 0},
    { .name = "orientation", .signature = "6if", .types = _CWlTouchOrientationTypes + 0},
};

const wl_interface wl_touch_interface = {
    .name = "wl_touch", .version = 11,
    .method_count = 1, .methods = _CWlTouchRequests,
    .event_count = 7, .events = _CWlTouchEvents,
};

CWlTouch::CWlTouch(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_touch_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlTouch__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlTouchVTable, this, nullptr);
}

CWlTouch::~CWlTouch() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlTouch::onDestroyCalled() {
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

void CWlTouch::setRelease(F<void(CWlTouch*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWlOutputRelease(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlOutput*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.release)
        PO->requests.release(PO);
}

static void _CWlOutput__DestroyListener(wl_listener* l, void* d) {
    CWlOutputDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlOutput* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlOutputVTable[] = {
    (void*)_CWlOutputRelease,
};

void CWlOutput::sendGeometry(int32_t x, int32_t y, int32_t physical_width, int32_t physical_height, int32_t subpixel, const char* make, const char* model, int32_t transform) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, x, y, physical_width, physical_height, subpixel, make, model, transform);
}

void CWlOutput::sendMode(enum wl_output_mode flags, int32_t width, int32_t height, int32_t refresh) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, flags, width, height, refresh);
}

void CWlOutput::sendDone() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CWlOutput::sendScale(int32_t factor) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, factor);
}

void CWlOutput::sendName(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, name);
}

void CWlOutput::sendDescription(const char* description) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, description);
}

void CWlOutput::sendGeometryRaw(int32_t x, int32_t y, int32_t physical_width, int32_t physical_height, int32_t subpixel, const char* make, const char* model, int32_t transform) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, x, y, physical_width, physical_height, subpixel, make, model, transform);
}

void CWlOutput::sendModeRaw(enum wl_output_mode flags, int32_t width, int32_t height, int32_t refresh) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1, flags, width, height, refresh);
}

void CWlOutput::sendDoneRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 2);
}

void CWlOutput::sendScaleRaw(int32_t factor) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 3, factor);
}

void CWlOutput::sendNameRaw(const char* name) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 4, name);
}

void CWlOutput::sendDescriptionRaw(const char* description) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 5, description);
}
static const wl_interface* _CWlOutputGeometryTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlOutputModeTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlOutputScaleTypes[] = {
    nullptr,
};
static const wl_interface* _CWlOutputNameTypes[] = {
    nullptr,
};
static const wl_interface* _CWlOutputDescriptionTypes[] = {
    nullptr,
};

static const wl_message _CWlOutputRequests[] = {
    { .name = "release", .signature = "3", .types = wayland_dummyTypes + 0},
};

static const wl_message _CWlOutputEvents[] = {
    { .name = "geometry", .signature = "iiiiissi", .types = _CWlOutputGeometryTypes + 0},
    { .name = "mode", .signature = "uiii", .types = _CWlOutputModeTypes + 0},
    { .name = "done", .signature = "2", .types = wayland_dummyTypes + 0},
    { .name = "scale", .signature = "2i", .types = _CWlOutputScaleTypes + 0},
    { .name = "name", .signature = "4s", .types = _CWlOutputNameTypes + 0},
    { .name = "description", .signature = "4s", .types = _CWlOutputDescriptionTypes + 0},
};

const wl_interface wl_output_interface = {
    .name = "wl_output", .version = 4,
    .method_count = 1, .methods = _CWlOutputRequests,
    .event_count = 6, .events = _CWlOutputEvents,
};

CWlOutput::CWlOutput(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_output_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlOutput__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlOutputVTable, this, nullptr);
}

CWlOutput::~CWlOutput() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlOutput::onDestroyCalled() {
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

void CWlOutput::setRelease(F<void(CWlOutput*)> &&handler) {
    requests.release = std::move(handler);
}

static void _CWlRegionDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlRegion*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWlRegionAdd(wl_client* client, wl_resource* resource, int32_t x, int32_t y, int32_t width, int32_t height) {
    const auto PO = (CWlRegion*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.add)
        PO->requests.add(PO, x, y, width, height);
}

static void _CWlRegionSubtract(wl_client* client, wl_resource* resource, int32_t x, int32_t y, int32_t width, int32_t height) {
    const auto PO = (CWlRegion*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.subtract)
        PO->requests.subtract(PO, x, y, width, height);
}

static void _CWlRegion__DestroyListener(wl_listener* l, void* d) {
    CWlRegionDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlRegion* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlRegionVTable[] = {
    (void*)_CWlRegionDestroy,
    (void*)_CWlRegionAdd,
    (void*)_CWlRegionSubtract,
};
static const wl_interface* _CWlRegionAddTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};
static const wl_interface* _CWlRegionSubtractTypes[] = {
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};

static const wl_message _CWlRegionRequests[] = {
    { .name = "destroy", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "add", .signature = "iiii", .types = _CWlRegionAddTypes + 0},
    { .name = "subtract", .signature = "iiii", .types = _CWlRegionSubtractTypes + 0},
};

const wl_interface wl_region_interface = {
    .name = "wl_region", .version = 7,
    .method_count = 3, .methods = _CWlRegionRequests,
    .event_count = 0, .events = nullptr,
};

CWlRegion::CWlRegion(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_region_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlRegion__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlRegionVTable, this, nullptr);
}

CWlRegion::~CWlRegion() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlRegion::onDestroyCalled() {
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

void CWlRegion::setDestroy(F<void(CWlRegion*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWlRegion::setAdd(F<void(CWlRegion*, int32_t, int32_t, int32_t, int32_t)> &&handler) {
    requests.add = std::move(handler);
}

void CWlRegion::setSubtract(F<void(CWlRegion*, int32_t, int32_t, int32_t, int32_t)> &&handler) {
    requests.subtract = std::move(handler);
}

static void _CWlSubcompositorDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlSubcompositor*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWlSubcompositorGetSubsurface(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface, wl_resource* parent) {
    const auto PO = (CWlSubcompositor*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getSubsurface)
        PO->requests.getSubsurface(PO, id, surface, parent);
}

static void _CWlSubcompositor__DestroyListener(wl_listener* l, void* d) {
    CWlSubcompositorDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlSubcompositor* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlSubcompositorVTable[] = {
    (void*)_CWlSubcompositorDestroy,
    (void*)_CWlSubcompositorGetSubsurface,
};
static const wl_interface* _CWlSubcompositorGetSubsurfaceTypes[] = {
    &wl_subsurface_interface,
    &wl_surface_interface,
    &wl_surface_interface,
};

static const wl_message _CWlSubcompositorRequests[] = {
    { .name = "destroy", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "get_subsurface", .signature = "noo", .types = _CWlSubcompositorGetSubsurfaceTypes + 0},
};

const wl_interface wl_subcompositor_interface = {
    .name = "wl_subcompositor", .version = 1,
    .method_count = 2, .methods = _CWlSubcompositorRequests,
    .event_count = 0, .events = nullptr,
};

CWlSubcompositor::CWlSubcompositor(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_subcompositor_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlSubcompositor__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlSubcompositorVTable, this, nullptr);
}

CWlSubcompositor::~CWlSubcompositor() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlSubcompositor::onDestroyCalled() {
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

void CWlSubcompositor::setDestroy(F<void(CWlSubcompositor*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWlSubcompositor::setGetSubsurface(F<void(CWlSubcompositor*, uint32_t, wl_resource*, wl_resource*)> &&handler) {
    requests.getSubsurface = std::move(handler);
}

static void _CWlSubsurfaceDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlSubsurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWlSubsurfaceSetPosition(wl_client* client, wl_resource* resource, int32_t x, int32_t y) {
    const auto PO = (CWlSubsurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setPosition)
        PO->requests.setPosition(PO, x, y);
}

static void _CWlSubsurfacePlaceAbove(wl_client* client, wl_resource* resource, wl_resource* sibling) {
    const auto PO = (CWlSubsurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.placeAbove)
        PO->requests.placeAbove(PO, sibling);
}

static void _CWlSubsurfacePlaceBelow(wl_client* client, wl_resource* resource, wl_resource* sibling) {
    const auto PO = (CWlSubsurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.placeBelow)
        PO->requests.placeBelow(PO, sibling);
}

static void _CWlSubsurfaceSetSync(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlSubsurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setSync)
        PO->requests.setSync(PO);
}

static void _CWlSubsurfaceSetDesync(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlSubsurface*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setDesync)
        PO->requests.setDesync(PO);
}

static void _CWlSubsurface__DestroyListener(wl_listener* l, void* d) {
    CWlSubsurfaceDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlSubsurface* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlSubsurfaceVTable[] = {
    (void*)_CWlSubsurfaceDestroy,
    (void*)_CWlSubsurfaceSetPosition,
    (void*)_CWlSubsurfacePlaceAbove,
    (void*)_CWlSubsurfacePlaceBelow,
    (void*)_CWlSubsurfaceSetSync,
    (void*)_CWlSubsurfaceSetDesync,
};
static const wl_interface* _CWlSubsurfaceSetPositionTypes[] = {
    nullptr,
    nullptr,
};
static const wl_interface* _CWlSubsurfacePlaceAboveTypes[] = {
    &wl_surface_interface,
};
static const wl_interface* _CWlSubsurfacePlaceBelowTypes[] = {
    &wl_surface_interface,
};

static const wl_message _CWlSubsurfaceRequests[] = {
    { .name = "destroy", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "set_position", .signature = "ii", .types = _CWlSubsurfaceSetPositionTypes + 0},
    { .name = "place_above", .signature = "o", .types = _CWlSubsurfacePlaceAboveTypes + 0},
    { .name = "place_below", .signature = "o", .types = _CWlSubsurfacePlaceBelowTypes + 0},
    { .name = "set_sync", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "set_desync", .signature = "", .types = wayland_dummyTypes + 0},
};

const wl_interface wl_subsurface_interface = {
    .name = "wl_subsurface", .version = 1,
    .method_count = 6, .methods = _CWlSubsurfaceRequests,
    .event_count = 0, .events = nullptr,
};

CWlSubsurface::CWlSubsurface(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_subsurface_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlSubsurface__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlSubsurfaceVTable, this, nullptr);
}

CWlSubsurface::~CWlSubsurface() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlSubsurface::onDestroyCalled() {
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

void CWlSubsurface::setDestroy(F<void(CWlSubsurface*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWlSubsurface::setSetPosition(F<void(CWlSubsurface*, int32_t, int32_t)> &&handler) {
    requests.setPosition = std::move(handler);
}

void CWlSubsurface::setPlaceAbove(F<void(CWlSubsurface*, wl_resource*)> &&handler) {
    requests.placeAbove = std::move(handler);
}

void CWlSubsurface::setPlaceBelow(F<void(CWlSubsurface*, wl_resource*)> &&handler) {
    requests.placeBelow = std::move(handler);
}

void CWlSubsurface::setSetSync(F<void(CWlSubsurface*)> &&handler) {
    requests.setSync = std::move(handler);
}

void CWlSubsurface::setSetDesync(F<void(CWlSubsurface*)> &&handler) {
    requests.setDesync = std::move(handler);
}

static void _CWlFixesDestroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWlFixes*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWlFixesDestroyRegistry(wl_client* client, wl_resource* resource, wl_resource* registry) {
    const auto PO = (CWlFixes*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroyRegistry)
        PO->requests.destroyRegistry(PO, registry);
}

static void _CWlFixesAckGlobalRemove(wl_client* client, wl_resource* resource, wl_resource* registry, uint32_t name) {
    const auto PO = (CWlFixes*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.ackGlobalRemove)
        PO->requests.ackGlobalRemove(PO, registry, name);
}

static void _CWlFixes__DestroyListener(wl_listener* l, void* d) {
    CWlFixesDestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWlFixes* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWlFixesVTable[] = {
    (void*)_CWlFixesDestroy,
    (void*)_CWlFixesDestroyRegistry,
    (void*)_CWlFixesAckGlobalRemove,
};
static const wl_interface* _CWlFixesDestroyRegistryTypes[] = {
    &wl_registry_interface,
};
static const wl_interface* _CWlFixesAckGlobalRemoveTypes[] = {
    &wl_registry_interface,
    nullptr,
};

static const wl_message _CWlFixesRequests[] = {
    { .name = "destroy", .signature = "", .types = wayland_dummyTypes + 0},
    { .name = "destroy_registry", .signature = "o", .types = _CWlFixesDestroyRegistryTypes + 0},
    { .name = "ack_global_remove", .signature = "2ou", .types = _CWlFixesAckGlobalRemoveTypes + 0},
};

const wl_interface wl_fixes_interface = {
    .name = "wl_fixes", .version = 2,
    .method_count = 3, .methods = _CWlFixesRequests,
    .event_count = 0, .events = nullptr,
};

CWlFixes::CWlFixes(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wl_fixes_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWlFixes__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWlFixesVTable, this, nullptr);
}

CWlFixes::~CWlFixes() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWlFixes::onDestroyCalled() {
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

void CWlFixes::setDestroy(F<void(CWlFixes*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWlFixes::setDestroyRegistry(F<void(CWlFixes*, wl_resource*)> &&handler) {
    requests.destroyRegistry = std::move(handler);
}

void CWlFixes::setAckGlobalRemove(F<void(CWlFixes*, wl_resource*, uint32_t)> &&handler) {
    requests.ackGlobalRemove = std::move(handler);
}

#undef F

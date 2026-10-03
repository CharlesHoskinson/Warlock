// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// security_context_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2021 Simon Ser

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
#include "security-context-v1.hpp"
#undef private
#define F std::function

static const wl_interface* securityContextV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface wp_security_context_manager_v1_interface;
extern const wl_interface wp_security_context_v1_interface;

static void _CWpSecurityContextManagerV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpSecurityContextManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpSecurityContextManagerV1CreateListener(wl_client* client, wl_resource* resource, uint32_t id, int32_t listen_fd, int32_t close_fd) {
    const auto PO = (CWpSecurityContextManagerV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.createListener)
        PO->requests.createListener(PO, id, listen_fd, close_fd);
}

static void _CWpSecurityContextManagerV1__DestroyListener(wl_listener* l, void* d) {
    CWpSecurityContextManagerV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpSecurityContextManagerV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpSecurityContextManagerV1VTable[] = {
    (void*)_CWpSecurityContextManagerV1Destroy,
    (void*)_CWpSecurityContextManagerV1CreateListener,
};
static const wl_interface* _CWpSecurityContextManagerV1CreateListenerTypes[] = {
    &wp_security_context_v1_interface,
    nullptr,
    nullptr,
};

static const wl_message _CWpSecurityContextManagerV1Requests[] = {
    { .name = "destroy", .signature = "", .types = securityContextV1_dummyTypes + 0},
    { .name = "create_listener", .signature = "nhh", .types = _CWpSecurityContextManagerV1CreateListenerTypes + 0},
};

const wl_interface wp_security_context_manager_v1_interface = {
    .name = "wp_security_context_manager_v1", .version = 1,
    .method_count = 2, .methods = _CWpSecurityContextManagerV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpSecurityContextManagerV1::CWpSecurityContextManagerV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_security_context_manager_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpSecurityContextManagerV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpSecurityContextManagerV1VTable, this, nullptr);
}

CWpSecurityContextManagerV1::~CWpSecurityContextManagerV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpSecurityContextManagerV1::onDestroyCalled() {
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

void CWpSecurityContextManagerV1::setDestroy(F<void(CWpSecurityContextManagerV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpSecurityContextManagerV1::setCreateListener(F<void(CWpSecurityContextManagerV1*, uint32_t, int32_t, int32_t)> &&handler) {
    requests.createListener = std::move(handler);
}

static void _CWpSecurityContextV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpSecurityContextV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CWpSecurityContextV1SetSandboxEngine(wl_client* client, wl_resource* resource, const char* name) {
    const auto PO = (CWpSecurityContextV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setSandboxEngine)
        PO->requests.setSandboxEngine(PO, name);
}

static void _CWpSecurityContextV1SetAppId(wl_client* client, wl_resource* resource, const char* app_id) {
    const auto PO = (CWpSecurityContextV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setAppId)
        PO->requests.setAppId(PO, app_id);
}

static void _CWpSecurityContextV1SetInstanceId(wl_client* client, wl_resource* resource, const char* instance_id) {
    const auto PO = (CWpSecurityContextV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setInstanceId)
        PO->requests.setInstanceId(PO, instance_id);
}

static void _CWpSecurityContextV1Commit(wl_client* client, wl_resource* resource) {
    const auto PO = (CWpSecurityContextV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.commit)
        PO->requests.commit(PO);
}

static void _CWpSecurityContextV1__DestroyListener(wl_listener* l, void* d) {
    CWpSecurityContextV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CWpSecurityContextV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CWpSecurityContextV1VTable[] = {
    (void*)_CWpSecurityContextV1Destroy,
    (void*)_CWpSecurityContextV1SetSandboxEngine,
    (void*)_CWpSecurityContextV1SetAppId,
    (void*)_CWpSecurityContextV1SetInstanceId,
    (void*)_CWpSecurityContextV1Commit,
};
static const wl_interface* _CWpSecurityContextV1SetSandboxEngineTypes[] = {
    nullptr,
};
static const wl_interface* _CWpSecurityContextV1SetAppIdTypes[] = {
    nullptr,
};
static const wl_interface* _CWpSecurityContextV1SetInstanceIdTypes[] = {
    nullptr,
};

static const wl_message _CWpSecurityContextV1Requests[] = {
    { .name = "destroy", .signature = "", .types = securityContextV1_dummyTypes + 0},
    { .name = "set_sandbox_engine", .signature = "s", .types = _CWpSecurityContextV1SetSandboxEngineTypes + 0},
    { .name = "set_app_id", .signature = "s", .types = _CWpSecurityContextV1SetAppIdTypes + 0},
    { .name = "set_instance_id", .signature = "s", .types = _CWpSecurityContextV1SetInstanceIdTypes + 0},
    { .name = "commit", .signature = "", .types = securityContextV1_dummyTypes + 0},
};

const wl_interface wp_security_context_v1_interface = {
    .name = "wp_security_context_v1", .version = 1,
    .method_count = 5, .methods = _CWpSecurityContextV1Requests,
    .event_count = 0, .events = nullptr,
};

CWpSecurityContextV1::CWpSecurityContextV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &wp_security_context_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CWpSecurityContextV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CWpSecurityContextV1VTable, this, nullptr);
}

CWpSecurityContextV1::~CWpSecurityContextV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CWpSecurityContextV1::onDestroyCalled() {
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

void CWpSecurityContextV1::setDestroy(F<void(CWpSecurityContextV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CWpSecurityContextV1::setSetSandboxEngine(F<void(CWpSecurityContextV1*, const char*)> &&handler) {
    requests.setSandboxEngine = std::move(handler);
}

void CWpSecurityContextV1::setSetAppId(F<void(CWpSecurityContextV1*, const char*)> &&handler) {
    requests.setAppId = std::move(handler);
}

void CWpSecurityContextV1::setSetInstanceId(F<void(CWpSecurityContextV1*, const char*)> &&handler) {
    requests.setInstanceId = std::move(handler);
}

void CWpSecurityContextV1::setCommit(F<void(CWpSecurityContextV1*)> &&handler) {
    requests.commit = std::move(handler);
}

#undef F

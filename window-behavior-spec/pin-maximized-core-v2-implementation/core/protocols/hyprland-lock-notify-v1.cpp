// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// hyprland_lock_notify_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2025 Maximilian Seidler
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
#include "hyprland-lock-notify-v1.hpp"
#undef private
#define F std::function

static const wl_interface* hyprlandLockNotifyV1_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface hyprland_lock_notifier_v1_interface;
extern const wl_interface hyprland_lock_notification_v1_interface;

static void _CHyprlandLockNotifierV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandLockNotifierV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandLockNotifierV1GetLockNotification(wl_client* client, wl_resource* resource, uint32_t id) {
    const auto PO = (CHyprlandLockNotifierV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.getLockNotification)
        PO->requests.getLockNotification(PO, id);
}

static void _CHyprlandLockNotifierV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandLockNotifierV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandLockNotifierV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandLockNotifierV1VTable[] = {
    (void*)_CHyprlandLockNotifierV1Destroy,
    (void*)_CHyprlandLockNotifierV1GetLockNotification,
};
static const wl_interface* _CHyprlandLockNotifierV1GetLockNotificationTypes[] = {
    &hyprland_lock_notification_v1_interface,
};

static const wl_message _CHyprlandLockNotifierV1Requests[] = {
    { .name = "destroy", .signature = "", .types = hyprlandLockNotifyV1_dummyTypes + 0},
    { .name = "get_lock_notification", .signature = "n", .types = _CHyprlandLockNotifierV1GetLockNotificationTypes + 0},
};

const wl_interface hyprland_lock_notifier_v1_interface = {
    .name = "hyprland_lock_notifier_v1", .version = 1,
    .method_count = 2, .methods = _CHyprlandLockNotifierV1Requests,
    .event_count = 0, .events = nullptr,
};

CHyprlandLockNotifierV1::CHyprlandLockNotifierV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_lock_notifier_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandLockNotifierV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandLockNotifierV1VTable, this, nullptr);
}

CHyprlandLockNotifierV1::~CHyprlandLockNotifierV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandLockNotifierV1::onDestroyCalled() {
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

void CHyprlandLockNotifierV1::setDestroy(F<void(CHyprlandLockNotifierV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CHyprlandLockNotifierV1::setGetLockNotification(F<void(CHyprlandLockNotifierV1*, uint32_t)> &&handler) {
    requests.getLockNotification = std::move(handler);
}

static void _CHyprlandLockNotificationV1Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CHyprlandLockNotificationV1*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CHyprlandLockNotificationV1__DestroyListener(wl_listener* l, void* d) {
    CHyprlandLockNotificationV1DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CHyprlandLockNotificationV1* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CHyprlandLockNotificationV1VTable[] = {
    (void*)_CHyprlandLockNotificationV1Destroy,
};

void CHyprlandLockNotificationV1::sendLocked() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CHyprlandLockNotificationV1::sendUnlocked() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

void CHyprlandLockNotificationV1::sendLockedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CHyprlandLockNotificationV1::sendUnlockedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 1);
}

static const wl_message _CHyprlandLockNotificationV1Requests[] = {
    { .name = "destroy", .signature = "", .types = hyprlandLockNotifyV1_dummyTypes + 0},
};

static const wl_message _CHyprlandLockNotificationV1Events[] = {
    { .name = "locked", .signature = "", .types = hyprlandLockNotifyV1_dummyTypes + 0},
    { .name = "unlocked", .signature = "", .types = hyprlandLockNotifyV1_dummyTypes + 0},
};

const wl_interface hyprland_lock_notification_v1_interface = {
    .name = "hyprland_lock_notification_v1", .version = 1,
    .method_count = 1, .methods = _CHyprlandLockNotificationV1Requests,
    .event_count = 2, .events = _CHyprlandLockNotificationV1Events,
};

CHyprlandLockNotificationV1::CHyprlandLockNotificationV1(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &hyprland_lock_notification_v1_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CHyprlandLockNotificationV1__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CHyprlandLockNotificationV1VTable, this, nullptr);
}

CHyprlandLockNotificationV1::~CHyprlandLockNotificationV1() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CHyprlandLockNotificationV1::onDestroyCalled() {
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

void CHyprlandLockNotificationV1::setDestroy(F<void(CHyprlandLockNotificationV1*)> &&handler) {
    requests.destroy = std::move(handler);
}

#undef F

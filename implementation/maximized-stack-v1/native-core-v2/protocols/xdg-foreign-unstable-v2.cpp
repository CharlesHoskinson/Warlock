// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// xdg_foreign_unstable_v2

/*
 This protocol's authors' copyright notice is:


    Copyright © 2015-2016 Red Hat Inc.

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
#include "xdg-foreign-unstable-v2.hpp"
#undef private
#define F std::function

static const wl_interface* xdgForeignUnstableV2_dummyTypes[] = { nullptr };

// Reference all other interfaces.
// The reason why this is in snake is to
// be able to cooperate with existing
// wayland_scanner interfaces (they are interop)
extern const wl_interface zxdg_exporter_v2_interface;
extern const wl_interface zxdg_importer_v2_interface;
extern const wl_interface zxdg_exported_v2_interface;
extern const wl_interface zxdg_imported_v2_interface;
extern const wl_interface wl_surface_interface;

static void _CZxdgExporterV2Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZxdgExporterV2*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZxdgExporterV2ExportToplevel(wl_client* client, wl_resource* resource, uint32_t id, wl_resource* surface) {
    const auto PO = (CZxdgExporterV2*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.exportToplevel)
        PO->requests.exportToplevel(PO, id, surface);
}

static void _CZxdgExporterV2__DestroyListener(wl_listener* l, void* d) {
    CZxdgExporterV2DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZxdgExporterV2* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZxdgExporterV2VTable[] = {
    (void*)_CZxdgExporterV2Destroy,
    (void*)_CZxdgExporterV2ExportToplevel,
};
static const wl_interface* _CZxdgExporterV2ExportToplevelTypes[] = {
    &zxdg_exported_v2_interface,
    &wl_surface_interface,
};

static const wl_message _CZxdgExporterV2Requests[] = {
    { .name = "destroy", .signature = "", .types = xdgForeignUnstableV2_dummyTypes + 0},
    { .name = "export_toplevel", .signature = "no", .types = _CZxdgExporterV2ExportToplevelTypes + 0},
};

const wl_interface zxdg_exporter_v2_interface = {
    .name = "zxdg_exporter_v2", .version = 1,
    .method_count = 2, .methods = _CZxdgExporterV2Requests,
    .event_count = 0, .events = nullptr,
};

CZxdgExporterV2::CZxdgExporterV2(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zxdg_exporter_v2_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZxdgExporterV2__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZxdgExporterV2VTable, this, nullptr);
}

CZxdgExporterV2::~CZxdgExporterV2() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZxdgExporterV2::onDestroyCalled() {
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

void CZxdgExporterV2::setDestroy(F<void(CZxdgExporterV2*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZxdgExporterV2::setExportToplevel(F<void(CZxdgExporterV2*, uint32_t, wl_resource*)> &&handler) {
    requests.exportToplevel = std::move(handler);
}

static void _CZxdgImporterV2Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZxdgImporterV2*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZxdgImporterV2ImportToplevel(wl_client* client, wl_resource* resource, uint32_t id, const char* handle) {
    const auto PO = (CZxdgImporterV2*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.importToplevel)
        PO->requests.importToplevel(PO, id, handle);
}

static void _CZxdgImporterV2__DestroyListener(wl_listener* l, void* d) {
    CZxdgImporterV2DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZxdgImporterV2* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZxdgImporterV2VTable[] = {
    (void*)_CZxdgImporterV2Destroy,
    (void*)_CZxdgImporterV2ImportToplevel,
};
static const wl_interface* _CZxdgImporterV2ImportToplevelTypes[] = {
    &zxdg_imported_v2_interface,
    nullptr,
};

static const wl_message _CZxdgImporterV2Requests[] = {
    { .name = "destroy", .signature = "", .types = xdgForeignUnstableV2_dummyTypes + 0},
    { .name = "import_toplevel", .signature = "ns", .types = _CZxdgImporterV2ImportToplevelTypes + 0},
};

const wl_interface zxdg_importer_v2_interface = {
    .name = "zxdg_importer_v2", .version = 1,
    .method_count = 2, .methods = _CZxdgImporterV2Requests,
    .event_count = 0, .events = nullptr,
};

CZxdgImporterV2::CZxdgImporterV2(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zxdg_importer_v2_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZxdgImporterV2__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZxdgImporterV2VTable, this, nullptr);
}

CZxdgImporterV2::~CZxdgImporterV2() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZxdgImporterV2::onDestroyCalled() {
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

void CZxdgImporterV2::setDestroy(F<void(CZxdgImporterV2*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZxdgImporterV2::setImportToplevel(F<void(CZxdgImporterV2*, uint32_t, const char*)> &&handler) {
    requests.importToplevel = std::move(handler);
}

static void _CZxdgExportedV2Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZxdgExportedV2*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZxdgExportedV2__DestroyListener(wl_listener* l, void* d) {
    CZxdgExportedV2DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZxdgExportedV2* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZxdgExportedV2VTable[] = {
    (void*)_CZxdgExportedV2Destroy,
};

void CZxdgExportedV2::sendHandle(const char* handle) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, handle);
}

void CZxdgExportedV2::sendHandleRaw(const char* handle) {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0, handle);
}
static const wl_interface* _CZxdgExportedV2HandleTypes[] = {
    nullptr,
};

static const wl_message _CZxdgExportedV2Requests[] = {
    { .name = "destroy", .signature = "", .types = xdgForeignUnstableV2_dummyTypes + 0},
};

static const wl_message _CZxdgExportedV2Events[] = {
    { .name = "handle", .signature = "s", .types = _CZxdgExportedV2HandleTypes + 0},
};

const wl_interface zxdg_exported_v2_interface = {
    .name = "zxdg_exported_v2", .version = 1,
    .method_count = 1, .methods = _CZxdgExportedV2Requests,
    .event_count = 1, .events = _CZxdgExportedV2Events,
};

CZxdgExportedV2::CZxdgExportedV2(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zxdg_exported_v2_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZxdgExportedV2__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZxdgExportedV2VTable, this, nullptr);
}

CZxdgExportedV2::~CZxdgExportedV2() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZxdgExportedV2::onDestroyCalled() {
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

void CZxdgExportedV2::setDestroy(F<void(CZxdgExportedV2*)> &&handler) {
    requests.destroy = std::move(handler);
}

static void _CZxdgImportedV2Destroy(wl_client* client, wl_resource* resource) {
    const auto PO = (CZxdgImportedV2*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.destroy)
        PO->requests.destroy(PO);
}

static void _CZxdgImportedV2SetParentOf(wl_client* client, wl_resource* resource, wl_resource* surface) {
    const auto PO = (CZxdgImportedV2*)wl_resource_get_user_data(resource);
    if (PO && PO->requests.setParentOf)
        PO->requests.setParentOf(PO, surface);
}

static void _CZxdgImportedV2__DestroyListener(wl_listener* l, void* d) {
    CZxdgImportedV2DestroyWrapper *wrap = wl_container_of(l, wrap, listener);
    CZxdgImportedV2* pResource = wrap->parent;
    pResource->onDestroyCalled();
}

static const void* _CZxdgImportedV2VTable[] = {
    (void*)_CZxdgImportedV2Destroy,
    (void*)_CZxdgImportedV2SetParentOf,
};

void CZxdgImportedV2::sendDestroyed() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}

void CZxdgImportedV2::sendDestroyedRaw() {
    if (!pResource)
        return;
    wl_resource_post_event(pResource, 0);
}
static const wl_interface* _CZxdgImportedV2SetParentOfTypes[] = {
    &wl_surface_interface,
};

static const wl_message _CZxdgImportedV2Requests[] = {
    { .name = "destroy", .signature = "", .types = xdgForeignUnstableV2_dummyTypes + 0},
    { .name = "set_parent_of", .signature = "o", .types = _CZxdgImportedV2SetParentOfTypes + 0},
};

static const wl_message _CZxdgImportedV2Events[] = {
    { .name = "destroyed", .signature = "", .types = xdgForeignUnstableV2_dummyTypes + 0},
};

const wl_interface zxdg_imported_v2_interface = {
    .name = "zxdg_imported_v2", .version = 1,
    .method_count = 2, .methods = _CZxdgImportedV2Requests,
    .event_count = 1, .events = _CZxdgImportedV2Events,
};

CZxdgImportedV2::CZxdgImportedV2(wl_client* client, uint32_t version, uint32_t id) :
    pResource(wl_resource_create(client, &zxdg_imported_v2_interface, version, id)) {

    if (!pResource)
        return;

    wl_resource_set_user_data(pResource, this);
    wl_list_init(&resourceDestroyListener.listener.link);
    resourceDestroyListener.listener.notify = _CZxdgImportedV2__DestroyListener;
    resourceDestroyListener.parent = this;
    wl_resource_add_destroy_listener(pResource, &resourceDestroyListener.listener);

    wl_resource_set_implementation(pResource, _CZxdgImportedV2VTable, this, nullptr);
}

CZxdgImportedV2::~CZxdgImportedV2() {
    wl_list_remove(&resourceDestroyListener.listener.link);
    wl_list_init(&resourceDestroyListener.listener.link);

    // if we still own the wayland resource,
    // it means we need to destroy it.
    if (pResource && wl_resource_get_user_data(pResource) == this) {
        wl_resource_set_user_data(pResource, nullptr);
        wl_resource_destroy(pResource);
    }
}

void CZxdgImportedV2::onDestroyCalled() {
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

void CZxdgImportedV2::setDestroy(F<void(CZxdgImportedV2*)> &&handler) {
    requests.destroy = std::move(handler);
}

void CZxdgImportedV2::setSetParentOf(F<void(CZxdgImportedV2*, wl_resource*)> &&handler) {
    requests.setParentOf = std::move(handler);
}

#undef F

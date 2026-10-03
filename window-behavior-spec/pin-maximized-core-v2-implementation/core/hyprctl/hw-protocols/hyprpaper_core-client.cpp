// Generated with hyprwire-scanner 0.3.1. Made with vaxry's keyboard and ❤️.
// hyprpaper_core

/*
 This protocol's authors' copyright notice is:


    BSD 3-Clause License

    Copyright (c) 2025, Hypr Development

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
#include "hyprpaper_core-client.hpp"
#undef private

using namespace Hyprutils::Memory;
#define SP CSharedPointer
    
static void hyprpaperCoreManager_method0(Hyprwire::IObject* r, const char* monitor_name) {
    auto& fn = rc<CCHyprpaperCoreManagerObject*>(r->getData())->m_listeners.add_monitor;
    if (fn)
        fn(monitor_name);
}

static void hyprpaperCoreManager_method1(Hyprwire::IObject* r, const char* monitor_name) {
    auto& fn = rc<CCHyprpaperCoreManagerObject*>(r->getData())->m_listeners.remove_monitor;
    if (fn)
        fn(monitor_name);
}

CCHyprpaperCoreManagerObject::CCHyprpaperCoreManagerObject(Hyprutils::Memory::CSharedPointer<Hyprwire::IObject>&& object) : m_object(std::move(object)) {
    m_object->setData(this);
            
    m_object->listen(0, rc<void*>(::hyprpaperCoreManager_method0));
    m_object->listen(1, rc<void*>(::hyprpaperCoreManager_method1));
}

CCHyprpaperCoreManagerObject::~CCHyprpaperCoreManagerObject() {
    ; // TODO: call destructor if present
}

SP<Hyprwire::IObject> CCHyprpaperCoreManagerObject::sendGetWallpaperObject() {
    auto _seq = m_object->call(0);
    return m_object->clientSock()->objectForSeq(_seq);
}

void CCHyprpaperCoreManagerObject::sendDestroy() {
    m_object->call(1);
}


SP<Hyprwire::IObject> CCHyprpaperCoreManagerObject::sendGetStatusObject() {
    auto _seq = m_object->call(2);
    return m_object->clientSock()->objectForSeq(_seq);
}

void CCHyprpaperCoreManagerObject::setAddMonitor(std::function<void(const char*)>&& fn) {
    m_listeners.add_monitor = std::move(fn);
}

void CCHyprpaperCoreManagerObject::setRemoveMonitor(std::function<void(const char*)>&& fn) {
    m_listeners.remove_monitor = std::move(fn);
}

static void hyprpaperWallpaper_method0(Hyprwire::IObject* r) {
    auto& fn = rc<CCHyprpaperWallpaperObject*>(r->getData())->m_listeners.success;
    if (fn)
        fn();
}

static void hyprpaperWallpaper_method1(Hyprwire::IObject* r, uint32_t error) {
    auto& fn = rc<CCHyprpaperWallpaperObject*>(r->getData())->m_listeners.failed;
    if (fn)
        fn(error);
}

CCHyprpaperWallpaperObject::CCHyprpaperWallpaperObject(Hyprutils::Memory::CSharedPointer<Hyprwire::IObject>&& object) : m_object(std::move(object)) {
    m_object->setData(this);
            
    m_object->listen(0, rc<void*>(::hyprpaperWallpaper_method0));
    m_object->listen(1, rc<void*>(::hyprpaperWallpaper_method1));
}

CCHyprpaperWallpaperObject::~CCHyprpaperWallpaperObject() {
    ; // TODO: call destructor if present
}
void CCHyprpaperWallpaperObject::sendPath(const char* wallpaper) {
    m_object->call(0, wallpaper);
}

void CCHyprpaperWallpaperObject::sendFitMode(hyprpaperCoreWallpaperFitMode fit_mode) {
    m_object->call(1, fit_mode);
}

void CCHyprpaperWallpaperObject::sendMonitorName(const char* monitor_name) {
    m_object->call(2, monitor_name);
}

void CCHyprpaperWallpaperObject::sendApply() {
    m_object->call(3);
}

void CCHyprpaperWallpaperObject::sendDestroy() {
    m_object->call(4);
}

void CCHyprpaperWallpaperObject::setSuccess(std::function<void()>&& fn) {
    m_listeners.success = std::move(fn);
}

void CCHyprpaperWallpaperObject::setFailed(std::function<void(uint32_t)>&& fn) {
    m_listeners.failed = std::move(fn);
}

static void hyprpaperStatus_method0(Hyprwire::IObject* r, const char* monitor, const char* path) {
    auto& fn = rc<CCHyprpaperStatusObject*>(r->getData())->m_listeners.active_wallpaper;
    if (fn)
        fn(monitor, path);
}

CCHyprpaperStatusObject::CCHyprpaperStatusObject(Hyprutils::Memory::CSharedPointer<Hyprwire::IObject>&& object) : m_object(std::move(object)) {
    m_object->setData(this);
            
    m_object->listen(0, rc<void*>(::hyprpaperStatus_method0));
}

CCHyprpaperStatusObject::~CCHyprpaperStatusObject() {
    ; // TODO: call destructor if present
}
void CCHyprpaperStatusObject::sendDestroy() {
    m_object->call(0);
}

void CCHyprpaperStatusObject::setActiveWallpaper(std::function<void(const char*, const char*)>&& fn) {
    m_listeners.active_wallpaper = std::move(fn);
}

CCHyprpaperCoreImpl::CCHyprpaperCoreImpl(uint32_t ver) : m_version(ver) {
    ;
}

static auto hyprpaperCoreSpec = makeShared<CHyprpaperCoreProtocolSpec>();

SP<Hyprwire::IProtocolSpec> CCHyprpaperCoreImpl::protocol() {
    return hyprpaperCoreSpec;
}

std::vector<SP<Hyprwire::SClientObjectImplementation>> CCHyprpaperCoreImpl::implementation() {
    return {

            makeShared<Hyprwire::SClientObjectImplementation>(Hyprwire::SClientObjectImplementation{
                .objectName = "hyprpaper_core_manager",
                .version    = m_version,
            }),

            makeShared<Hyprwire::SClientObjectImplementation>(Hyprwire::SClientObjectImplementation{
                .objectName = "hyprpaper_wallpaper",
                .version    = m_version,
            }),

            makeShared<Hyprwire::SClientObjectImplementation>(Hyprwire::SClientObjectImplementation{
                .objectName = "hyprpaper_status",
                .version    = m_version,
            }),
};
}

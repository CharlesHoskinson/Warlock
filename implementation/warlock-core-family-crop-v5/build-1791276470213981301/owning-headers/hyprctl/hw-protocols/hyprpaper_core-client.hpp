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


#pragma once

#include <functional>
#include "hyprpaper_core-spec.hpp"
    
class CCHyprpaperCoreManagerObject {
  public:
    CCHyprpaperCoreManagerObject(Hyprutils::Memory::CSharedPointer<Hyprwire::IObject>&& object);
    ~CCHyprpaperCoreManagerObject();

    Hyprutils::Memory::CSharedPointer<Hyprwire::IObject> getObject() {
        return m_object;
    }


    Hyprutils::Memory::CSharedPointer<Hyprwire::IObject> sendGetWallpaperObject();
            
    void sendDestroy();
            
    Hyprutils::Memory::CSharedPointer<Hyprwire::IObject> sendGetStatusObject();
            
    void setAddMonitor(std::function<void(const char*)>&& fn);
            
    void setRemoveMonitor(std::function<void(const char*)>&& fn);
            
  private:
	struct {
 std::function<void(const char*)> add_monitor;
 std::function<void(const char*)> remove_monitor;
 } m_listeners;
        
    Hyprutils::Memory::CSharedPointer<Hyprwire::IObject> m_object;
};

class CCHyprpaperWallpaperObject {
  public:
    CCHyprpaperWallpaperObject(Hyprutils::Memory::CSharedPointer<Hyprwire::IObject>&& object);
    ~CCHyprpaperWallpaperObject();

    Hyprutils::Memory::CSharedPointer<Hyprwire::IObject> getObject() {
        return m_object;
    }


    void sendPath(const char* wallpaper);
            
    void sendFitMode(hyprpaperCoreWallpaperFitMode fit_mode);
            
    void sendMonitorName(const char* monitor_name);
            
    void sendApply();
            
    void sendDestroy();
            
    void setSuccess(std::function<void()>&& fn);
            
    void setFailed(std::function<void(uint32_t)>&& fn);
            
  private:
	struct {
 std::function<void()> success;
 std::function<void(uint32_t)> failed;
 } m_listeners;
        
    Hyprutils::Memory::CSharedPointer<Hyprwire::IObject> m_object;
};

class CCHyprpaperStatusObject {
  public:
    CCHyprpaperStatusObject(Hyprutils::Memory::CSharedPointer<Hyprwire::IObject>&& object);
    ~CCHyprpaperStatusObject();

    Hyprutils::Memory::CSharedPointer<Hyprwire::IObject> getObject() {
        return m_object;
    }


    void sendDestroy();
            
    void setActiveWallpaper(std::function<void(const char*, const char*)>&& fn);
            
  private:
	struct {
 std::function<void(const char*, const char*)> active_wallpaper;
 } m_listeners;
        
    Hyprutils::Memory::CSharedPointer<Hyprwire::IObject> m_object;
};

class CCHyprpaperCoreImpl : public Hyprwire::IProtocolClientImplementation {
  public:
    CCHyprpaperCoreImpl(uint32_t version);
    virtual ~CCHyprpaperCoreImpl() = default;

    virtual Hyprutils::Memory::CSharedPointer<Hyprwire::IProtocolSpec> protocol();

    virtual std::vector<Hyprutils::Memory::CSharedPointer<Hyprwire::SClientObjectImplementation>> implementation();

  private:
    uint32_t m_version = 0;
};

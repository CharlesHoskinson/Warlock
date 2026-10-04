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

#include <hyprwire/core/types/MessageMagic.hpp>
#include <hyprwire/hyprwire.hpp>
#include <hyprutils/memory/WeakPtr.hpp>
#include <vector>
    
enum hyprpaperCoreWallpaperFitMode : uint32_t {
	HYPRPAPER_CORE_WALLPAPER_FIT_MODE_STRETCH = 0,
	HYPRPAPER_CORE_WALLPAPER_FIT_MODE_COVER = 1,
	HYPRPAPER_CORE_WALLPAPER_FIT_MODE_CONTAIN = 2,
	HYPRPAPER_CORE_WALLPAPER_FIT_MODE_TILE = 3,
};

enum hyprpaperCoreWallpaperErrors : uint32_t {
	HYPRPAPER_CORE_WALLPAPER_ERRORS_INERT_WALLPAPER_OBJECT = 0,
};

enum hyprpaperCoreApplyingError : uint32_t {
	HYPRPAPER_CORE_APPLYING_ERROR_INVALID_PATH = 0,
	HYPRPAPER_CORE_APPLYING_ERROR_INVALID_MONITOR = 1,
	HYPRPAPER_CORE_APPLYING_ERROR_UNKNOWN_ERROR = 2,
};

class CHyprpaperCoreManagerSpec : public Hyprwire::IProtocolObjectSpec {
  public:
    CHyprpaperCoreManagerSpec() = default;
    virtual ~CHyprpaperCoreManagerSpec() = default;

    virtual std::string objectName() {
        return "hyprpaper_core_manager";
    }

        
	std::vector<Hyprwire::SMethod>                m_c2s = {
Hyprwire::SMethod{
.idx = 0,
.params = {  },
.returnsType = "hyprpaper_wallpaper",
.since = 0,
.isDestructor = false,
},
Hyprwire::SMethod{
.idx = 1,
.params = {  },
.returnsType = "",
.since = 0,
.isDestructor = true,
},
Hyprwire::SMethod{
.idx = 2,
.params = {  },
.returnsType = "hyprpaper_status",
.since = 2,
.isDestructor = false,
}
    };

    virtual const std::vector<Hyprwire::SMethod>& c2s() {
        return m_c2s;
    }

	std::vector<Hyprwire::SMethod>                m_s2c = {
Hyprwire::SMethod{
.idx = 0,
.params = { Hyprwire::HW_MESSAGE_MAGIC_TYPE_VARCHAR },
.since = 0,
.isDestructor = false,
},
Hyprwire::SMethod{
.idx = 1,
.params = { Hyprwire::HW_MESSAGE_MAGIC_TYPE_VARCHAR },
.since = 0,
.isDestructor = false,
}
    };

    virtual const std::vector<Hyprwire::SMethod>& s2c() {
        return m_s2c;
    }

};

class CHyprpaperWallpaperSpec : public Hyprwire::IProtocolObjectSpec {
  public:
    CHyprpaperWallpaperSpec() = default;
    virtual ~CHyprpaperWallpaperSpec() = default;

    virtual std::string objectName() {
        return "hyprpaper_wallpaper";
    }

        
	std::vector<Hyprwire::SMethod>                m_c2s = {
Hyprwire::SMethod{
.idx = 0,
.params = { Hyprwire::HW_MESSAGE_MAGIC_TYPE_VARCHAR },
.returnsType = "",
.since = 0,
.isDestructor = false,
},
Hyprwire::SMethod{
.idx = 1,
.params = { Hyprwire::HW_MESSAGE_MAGIC_TYPE_UINT },
.returnsType = "",
.since = 0,
.isDestructor = false,
},
Hyprwire::SMethod{
.idx = 2,
.params = { Hyprwire::HW_MESSAGE_MAGIC_TYPE_VARCHAR },
.returnsType = "",
.since = 0,
.isDestructor = false,
},
Hyprwire::SMethod{
.idx = 3,
.params = {  },
.returnsType = "",
.since = 0,
.isDestructor = false,
},
Hyprwire::SMethod{
.idx = 4,
.params = {  },
.returnsType = "",
.since = 0,
.isDestructor = true,
}
    };

    virtual const std::vector<Hyprwire::SMethod>& c2s() {
        return m_c2s;
    }

	std::vector<Hyprwire::SMethod>                m_s2c = {
Hyprwire::SMethod{
.idx = 0,
.params = {  },
.since = 0,
.isDestructor = false,
},
Hyprwire::SMethod{
.idx = 1,
.params = { Hyprwire::HW_MESSAGE_MAGIC_TYPE_UINT },
.since = 0,
.isDestructor = false,
}
    };

    virtual const std::vector<Hyprwire::SMethod>& s2c() {
        return m_s2c;
    }

};

class CHyprpaperStatusSpec : public Hyprwire::IProtocolObjectSpec {
  public:
    CHyprpaperStatusSpec() = default;
    virtual ~CHyprpaperStatusSpec() = default;

    virtual std::string objectName() {
        return "hyprpaper_status";
    }

        
	std::vector<Hyprwire::SMethod>                m_c2s = {
Hyprwire::SMethod{
.idx = 0,
.params = {  },
.returnsType = "",
.since = 0,
.isDestructor = true,
}
    };

    virtual const std::vector<Hyprwire::SMethod>& c2s() {
        return m_c2s;
    }

	std::vector<Hyprwire::SMethod>                m_s2c = {
Hyprwire::SMethod{
.idx = 0,
.params = { Hyprwire::HW_MESSAGE_MAGIC_TYPE_VARCHAR, Hyprwire::HW_MESSAGE_MAGIC_TYPE_VARCHAR },
.since = 0,
.isDestructor = false,
}
    };

    virtual const std::vector<Hyprwire::SMethod>& s2c() {
        return m_s2c;
    }

};

class CHyprpaperCoreProtocolSpec : public Hyprwire::IProtocolSpec {
  public:
    CHyprpaperCoreProtocolSpec()          = default;
    virtual ~CHyprpaperCoreProtocolSpec() = default;

    virtual std::string specName() {
        return "hyprpaper_core";
    }

    virtual uint32_t specVer() {
        return 2;
    }

    virtual std::vector<Hyprutils::Memory::CSharedPointer<Hyprwire::IProtocolObjectSpec>> objects() {
        return { Hyprutils::Memory::makeShared<CHyprpaperCoreManagerSpec>(), Hyprutils::Memory::makeShared<CHyprpaperWallpaperSpec>(), Hyprutils::Memory::makeShared<CHyprpaperStatusSpec>() };
    }
};

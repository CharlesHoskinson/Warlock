// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// linux_dmabuf_v1

/*
 This protocol's authors' copyright notice is:


    Copyright © 2014, 2015 Collabora, Ltd.

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

#pragma once

#include <functional>
#include <cstdint>
#include <string>
#include <wayland-client.h>

#define F std::function

struct wl_proxy;

enum zwpLinuxBufferParamsV1Error : uint32_t {
    ZWP_LINUX_BUFFER_PARAMS_V1_ERROR_ALREADY_USED = 0,
    ZWP_LINUX_BUFFER_PARAMS_V1_ERROR_PLANE_IDX = 1,
    ZWP_LINUX_BUFFER_PARAMS_V1_ERROR_PLANE_SET = 2,
    ZWP_LINUX_BUFFER_PARAMS_V1_ERROR_INCOMPLETE = 3,
    ZWP_LINUX_BUFFER_PARAMS_V1_ERROR_INVALID_FORMAT = 4,
    ZWP_LINUX_BUFFER_PARAMS_V1_ERROR_INVALID_DIMENSIONS = 5,
    ZWP_LINUX_BUFFER_PARAMS_V1_ERROR_OUT_OF_BOUNDS = 6,
    ZWP_LINUX_BUFFER_PARAMS_V1_ERROR_INVALID_WL_BUFFER = 7,
    ZWP_LINUX_BUFFER_PARAMS_V1_ERROR_INVALID_DEV_T_SIZE = 8,
};

enum zwpLinuxBufferParamsV1Flags : uint32_t {
    ZWP_LINUX_BUFFER_PARAMS_V1_FLAGS_Y_INVERT = 1,
    ZWP_LINUX_BUFFER_PARAMS_V1_FLAGS_INTERLACED = 2,
    ZWP_LINUX_BUFFER_PARAMS_V1_FLAGS_BOTTOM_FIRST = 4,
};

enum zwpLinuxDmabufFeedbackV1TrancheFlags : uint32_t {
    ZWP_LINUX_DMABUF_FEEDBACK_V1_TRANCHE_FLAGS_SCANOUT = 1,
    ZWP_LINUX_DMABUF_FEEDBACK_V1_TRANCHE_FLAGS_SAMPLING = 2,
};


class CCZwpLinuxDmabufV1;
class CCZwpLinuxBufferParamsV1;
class CCZwpLinuxDmabufFeedbackV1;
class CCZwpLinuxDmabufFeedbackV1;
class CCWlSurface;
class CCZwpLinuxBufferParamsV1;
class CCWlBuffer;
class CCWlBuffer;
class CCZwpLinuxDmabufFeedbackV1;

#ifndef HYPRWAYLAND_SCANNER_NO_INTERFACES
extern const wl_interface zwp_linux_dmabuf_v1_interface;
extern const wl_interface zwp_linux_buffer_params_v1_interface;
extern const wl_interface zwp_linux_dmabuf_feedback_v1_interface;

#endif


class CCZwpLinuxDmabufV1 {
  public:
    CCZwpLinuxDmabufV1(wl_proxy*);
    ~CCZwpLinuxDmabufV1();


    // set the data for this resource
    void setData(void* data) {{
        pData = data;
    }}

    // get the data for this resource
    void* data() {{
        return pData;
    }}

    // get the raw wl_resource (wl_proxy) ptr
    wl_proxy* resource() {{
        return pResource;
    }}

    // get the raw wl_proxy ptr
    wl_proxy* proxy() {{
        return pResource;
    }}

    // get the resource version
    int version() {{
        return wl_proxy_get_version(pResource);
    }}
            
    // --------------- Requests --------------- //

    void setFormat(F<void(CCZwpLinuxDmabufV1*, uint32_t)> &&handler);
    void setModifier(F<void(CCZwpLinuxDmabufV1*, uint32_t, uint32_t, uint32_t)> &&handler);

    // --------------- Events --------------- //

    void sendDestroy();
    wl_proxy* sendCreateParams();
    wl_proxy* sendGetDefaultFeedback();
    wl_proxy* sendGetSurfaceFeedback(wl_proxy*);

  private:
    struct {
        F<void(CCZwpLinuxDmabufV1*, uint32_t)> format;
        F<void(CCZwpLinuxDmabufV1*, uint32_t, uint32_t, uint32_t)> modifier;
    } requests;

    wl_proxy* pResource = nullptr;

    bool destroyed = false;

    void* pData = nullptr;
};



class CCZwpLinuxBufferParamsV1 {
  public:
    CCZwpLinuxBufferParamsV1(wl_proxy*);
    ~CCZwpLinuxBufferParamsV1();


    // set the data for this resource
    void setData(void* data) {{
        pData = data;
    }}

    // get the data for this resource
    void* data() {{
        return pData;
    }}

    // get the raw wl_resource (wl_proxy) ptr
    wl_proxy* resource() {{
        return pResource;
    }}

    // get the raw wl_proxy ptr
    wl_proxy* proxy() {{
        return pResource;
    }}

    // get the resource version
    int version() {{
        return wl_proxy_get_version(pResource);
    }}
            
    // --------------- Requests --------------- //

    void setCreated(F<void(CCZwpLinuxBufferParamsV1*, wl_proxy*)> &&handler);
    void setFailed(F<void(CCZwpLinuxBufferParamsV1*)> &&handler);

    // --------------- Events --------------- //

    void sendDestroy();
    void sendAdd(int32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
    void sendCreate(int32_t, int32_t, uint32_t, zwpLinuxBufferParamsV1Flags);
    wl_proxy* sendCreateImmed(int32_t, int32_t, uint32_t, zwpLinuxBufferParamsV1Flags);
    void sendSetSamplingDevice(wl_array*);

  private:
    struct {
        F<void(CCZwpLinuxBufferParamsV1*, wl_proxy*)> created;
        F<void(CCZwpLinuxBufferParamsV1*)> failed;
    } requests;

    wl_proxy* pResource = nullptr;

    bool destroyed = false;

    void* pData = nullptr;
};



class CCZwpLinuxDmabufFeedbackV1 {
  public:
    CCZwpLinuxDmabufFeedbackV1(wl_proxy*);
    ~CCZwpLinuxDmabufFeedbackV1();


    // set the data for this resource
    void setData(void* data) {{
        pData = data;
    }}

    // get the data for this resource
    void* data() {{
        return pData;
    }}

    // get the raw wl_resource (wl_proxy) ptr
    wl_proxy* resource() {{
        return pResource;
    }}

    // get the raw wl_proxy ptr
    wl_proxy* proxy() {{
        return pResource;
    }}

    // get the resource version
    int version() {{
        return wl_proxy_get_version(pResource);
    }}
            
    // --------------- Requests --------------- //

    void setDone(F<void(CCZwpLinuxDmabufFeedbackV1*)> &&handler);
    void setFormatTable(F<void(CCZwpLinuxDmabufFeedbackV1*, int32_t, uint32_t)> &&handler);
    void setMainDevice(F<void(CCZwpLinuxDmabufFeedbackV1*, wl_array*)> &&handler);
    void setTrancheDone(F<void(CCZwpLinuxDmabufFeedbackV1*)> &&handler);
    void setTrancheTargetDevice(F<void(CCZwpLinuxDmabufFeedbackV1*, wl_array*)> &&handler);
    void setTrancheFormats(F<void(CCZwpLinuxDmabufFeedbackV1*, wl_array*)> &&handler);
    void setTrancheFlags(F<void(CCZwpLinuxDmabufFeedbackV1*, zwpLinuxDmabufFeedbackV1TrancheFlags)> &&handler);

    // --------------- Events --------------- //

    void sendDestroy();

  private:
    struct {
        F<void(CCZwpLinuxDmabufFeedbackV1*)> done;
        F<void(CCZwpLinuxDmabufFeedbackV1*, int32_t, uint32_t)> formatTable;
        F<void(CCZwpLinuxDmabufFeedbackV1*, wl_array*)> mainDevice;
        F<void(CCZwpLinuxDmabufFeedbackV1*)> trancheDone;
        F<void(CCZwpLinuxDmabufFeedbackV1*, wl_array*)> trancheTargetDevice;
        F<void(CCZwpLinuxDmabufFeedbackV1*, wl_array*)> trancheFormats;
        F<void(CCZwpLinuxDmabufFeedbackV1*, zwpLinuxDmabufFeedbackV1TrancheFlags)> trancheFlags;
    } requests;

    wl_proxy* pResource = nullptr;

    bool destroyed = false;

    void* pData = nullptr;
};



#undef F

// Generated with hyprwayland-scanner 0.4.6. Made with vaxry's keyboard and ❤️.
// xdg_shell

/*
 This protocol's authors' copyright notice is:


    Copyright © 2008-2013 Kristian Høgsberg
    Copyright © 2013      Rafael Antognolli
    Copyright © 2013      Jasper St. Pierre
    Copyright © 2010-2013 Intel Corporation
    Copyright © 2015-2017 Samsung Electronics Co., Ltd
    Copyright © 2015-2017 Red Hat Inc.

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

enum xdgWmBaseError : uint32_t {
    XDG_WM_BASE_ERROR_ROLE = 0,
    XDG_WM_BASE_ERROR_DEFUNCT_SURFACES = 1,
    XDG_WM_BASE_ERROR_NOT_THE_TOPMOST_POPUP = 2,
    XDG_WM_BASE_ERROR_INVALID_POPUP_PARENT = 3,
    XDG_WM_BASE_ERROR_INVALID_SURFACE_STATE = 4,
    XDG_WM_BASE_ERROR_INVALID_POSITIONER = 5,
    XDG_WM_BASE_ERROR_UNRESPONSIVE = 6,
};

enum xdgPositionerError : uint32_t {
    XDG_POSITIONER_ERROR_INVALID_INPUT = 0,
};

enum xdgPositionerAnchor : uint32_t {
    XDG_POSITIONER_ANCHOR_NONE = 0,
    XDG_POSITIONER_ANCHOR_TOP = 1,
    XDG_POSITIONER_ANCHOR_BOTTOM = 2,
    XDG_POSITIONER_ANCHOR_LEFT = 3,
    XDG_POSITIONER_ANCHOR_RIGHT = 4,
    XDG_POSITIONER_ANCHOR_TOP_LEFT = 5,
    XDG_POSITIONER_ANCHOR_BOTTOM_LEFT = 6,
    XDG_POSITIONER_ANCHOR_TOP_RIGHT = 7,
    XDG_POSITIONER_ANCHOR_BOTTOM_RIGHT = 8,
};

enum xdgPositionerGravity : uint32_t {
    XDG_POSITIONER_GRAVITY_NONE = 0,
    XDG_POSITIONER_GRAVITY_TOP = 1,
    XDG_POSITIONER_GRAVITY_BOTTOM = 2,
    XDG_POSITIONER_GRAVITY_LEFT = 3,
    XDG_POSITIONER_GRAVITY_RIGHT = 4,
    XDG_POSITIONER_GRAVITY_TOP_LEFT = 5,
    XDG_POSITIONER_GRAVITY_BOTTOM_LEFT = 6,
    XDG_POSITIONER_GRAVITY_TOP_RIGHT = 7,
    XDG_POSITIONER_GRAVITY_BOTTOM_RIGHT = 8,
};

enum xdgPositionerConstraintAdjustment : uint32_t {
    XDG_POSITIONER_CONSTRAINT_ADJUSTMENT_NONE = 0,
    XDG_POSITIONER_CONSTRAINT_ADJUSTMENT_SLIDE_X = 1,
    XDG_POSITIONER_CONSTRAINT_ADJUSTMENT_SLIDE_Y = 2,
    XDG_POSITIONER_CONSTRAINT_ADJUSTMENT_FLIP_X = 4,
    XDG_POSITIONER_CONSTRAINT_ADJUSTMENT_FLIP_Y = 8,
    XDG_POSITIONER_CONSTRAINT_ADJUSTMENT_RESIZE_X = 16,
    XDG_POSITIONER_CONSTRAINT_ADJUSTMENT_RESIZE_Y = 32,
};

enum xdgSurfaceError : uint32_t {
    XDG_SURFACE_ERROR_NOT_CONSTRUCTED = 1,
    XDG_SURFACE_ERROR_ALREADY_CONSTRUCTED = 2,
    XDG_SURFACE_ERROR_UNCONFIGURED_BUFFER = 3,
    XDG_SURFACE_ERROR_INVALID_SERIAL = 4,
    XDG_SURFACE_ERROR_INVALID_SIZE = 5,
    XDG_SURFACE_ERROR_DEFUNCT_ROLE_OBJECT = 6,
};

enum xdgToplevelError : uint32_t {
    XDG_TOPLEVEL_ERROR_INVALID_RESIZE_EDGE = 0,
    XDG_TOPLEVEL_ERROR_INVALID_PARENT = 1,
    XDG_TOPLEVEL_ERROR_INVALID_SIZE = 2,
};

enum xdgToplevelResizeEdge : uint32_t {
    XDG_TOPLEVEL_RESIZE_EDGE_NONE = 0,
    XDG_TOPLEVEL_RESIZE_EDGE_TOP = 1,
    XDG_TOPLEVEL_RESIZE_EDGE_BOTTOM = 2,
    XDG_TOPLEVEL_RESIZE_EDGE_LEFT = 4,
    XDG_TOPLEVEL_RESIZE_EDGE_TOP_LEFT = 5,
    XDG_TOPLEVEL_RESIZE_EDGE_BOTTOM_LEFT = 6,
    XDG_TOPLEVEL_RESIZE_EDGE_RIGHT = 8,
    XDG_TOPLEVEL_RESIZE_EDGE_TOP_RIGHT = 9,
    XDG_TOPLEVEL_RESIZE_EDGE_BOTTOM_RIGHT = 10,
};

enum xdgToplevelState : uint32_t {
    XDG_TOPLEVEL_STATE_MAXIMIZED = 1,
    XDG_TOPLEVEL_STATE_FULLSCREEN = 2,
    XDG_TOPLEVEL_STATE_RESIZING = 3,
    XDG_TOPLEVEL_STATE_ACTIVATED = 4,
    XDG_TOPLEVEL_STATE_TILED_LEFT = 5,
    XDG_TOPLEVEL_STATE_TILED_RIGHT = 6,
    XDG_TOPLEVEL_STATE_TILED_TOP = 7,
    XDG_TOPLEVEL_STATE_TILED_BOTTOM = 8,
    XDG_TOPLEVEL_STATE_SUSPENDED = 9,
    XDG_TOPLEVEL_STATE_CONSTRAINED_LEFT = 10,
    XDG_TOPLEVEL_STATE_CONSTRAINED_RIGHT = 11,
    XDG_TOPLEVEL_STATE_CONSTRAINED_TOP = 12,
    XDG_TOPLEVEL_STATE_CONSTRAINED_BOTTOM = 13,
};

enum xdgToplevelWmCapabilities : uint32_t {
    XDG_TOPLEVEL_WM_CAPABILITIES_WINDOW_MENU = 1,
    XDG_TOPLEVEL_WM_CAPABILITIES_MAXIMIZE = 2,
    XDG_TOPLEVEL_WM_CAPABILITIES_FULLSCREEN = 3,
    XDG_TOPLEVEL_WM_CAPABILITIES_MINIMIZE = 4,
};

enum xdgPopupError : uint32_t {
    XDG_POPUP_ERROR_INVALID_GRAB = 0,
};


class CCXdgWmBase;
class CCXdgPositioner;
class CCXdgSurface;
class CCWlSurface;
class CCXdgPositioner;
class CCXdgSurface;
class CCXdgToplevel;
class CCXdgPopup;
class CCXdgSurface;
class CCXdgPositioner;
class CCXdgToplevel;
class CCXdgToplevel;
class CCWlSeat;
class CCWlSeat;
class CCWlSeat;
class CCWlOutput;
class CCXdgPopup;
class CCWlSeat;
class CCXdgPositioner;

#ifndef HYPRWAYLAND_SCANNER_NO_INTERFACES
extern const wl_interface xdg_wm_base_interface;
extern const wl_interface xdg_positioner_interface;
extern const wl_interface xdg_surface_interface;
extern const wl_interface xdg_toplevel_interface;
extern const wl_interface xdg_popup_interface;

#endif


class CCXdgWmBase {
  public:
    CCXdgWmBase(wl_proxy*);
    ~CCXdgWmBase();


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

    void setPing(F<void(CCXdgWmBase*, uint32_t)> &&handler);

    // --------------- Events --------------- //

    void sendDestroy();
    wl_proxy* sendCreatePositioner();
    wl_proxy* sendGetXdgSurface(wl_proxy*);
    void sendPong(uint32_t);

  private:
    struct {
        F<void(CCXdgWmBase*, uint32_t)> ping;
    } requests;

    wl_proxy* pResource = nullptr;

    bool destroyed = false;

    void* pData = nullptr;
};



class CCXdgPositioner {
  public:
    CCXdgPositioner(wl_proxy*);
    ~CCXdgPositioner();


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


    // --------------- Events --------------- //

    void sendDestroy();
    void sendSetSize(int32_t, int32_t);
    void sendSetAnchorRect(int32_t, int32_t, int32_t, int32_t);
    void sendSetAnchor(xdgPositionerAnchor);
    void sendSetGravity(xdgPositionerGravity);
    void sendSetConstraintAdjustment(xdgPositionerConstraintAdjustment);
    void sendSetOffset(int32_t, int32_t);
    void sendSetReactive();
    void sendSetParentSize(int32_t, int32_t);
    void sendSetParentConfigure(uint32_t);

  private:
    struct {
    } requests;

    wl_proxy* pResource = nullptr;

    bool destroyed = false;

    void* pData = nullptr;
};



class CCXdgSurface {
  public:
    CCXdgSurface(wl_proxy*);
    ~CCXdgSurface();


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

    void setConfigure(F<void(CCXdgSurface*, uint32_t)> &&handler);

    // --------------- Events --------------- //

    void sendDestroy();
    wl_proxy* sendGetToplevel();
    wl_proxy* sendGetPopup(CCXdgSurface*, CCXdgPositioner*);
    void sendSetWindowGeometry(int32_t, int32_t, int32_t, int32_t);
    void sendAckConfigure(uint32_t);

  private:
    struct {
        F<void(CCXdgSurface*, uint32_t)> configure;
    } requests;

    wl_proxy* pResource = nullptr;

    bool destroyed = false;

    void* pData = nullptr;
};



class CCXdgToplevel {
  public:
    CCXdgToplevel(wl_proxy*);
    ~CCXdgToplevel();


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

    void setConfigure(F<void(CCXdgToplevel*, int32_t, int32_t, wl_array*)> &&handler);
    void setClose(F<void(CCXdgToplevel*)> &&handler);
    void setConfigureBounds(F<void(CCXdgToplevel*, int32_t, int32_t)> &&handler);
    void setWmCapabilities(F<void(CCXdgToplevel*, wl_array*)> &&handler);

    // --------------- Events --------------- //

    void sendDestroy();
    void sendSetParent(CCXdgToplevel*);
    void sendSetTitle(const char*);
    void sendSetAppId(const char*);
    void sendShowWindowMenu(wl_proxy*, uint32_t, int32_t, int32_t);
    void sendMove(wl_proxy*, uint32_t);
    void sendResize(wl_proxy*, uint32_t, xdgToplevelResizeEdge);
    void sendSetMaxSize(int32_t, int32_t);
    void sendSetMinSize(int32_t, int32_t);
    void sendSetMaximized();
    void sendUnsetMaximized();
    void sendSetFullscreen(wl_proxy*);
    void sendUnsetFullscreen();
    void sendSetMinimized();

  private:
    struct {
        F<void(CCXdgToplevel*, int32_t, int32_t, wl_array*)> configure;
        F<void(CCXdgToplevel*)> close;
        F<void(CCXdgToplevel*, int32_t, int32_t)> configureBounds;
        F<void(CCXdgToplevel*, wl_array*)> wmCapabilities;
    } requests;

    wl_proxy* pResource = nullptr;

    bool destroyed = false;

    void* pData = nullptr;
};



class CCXdgPopup {
  public:
    CCXdgPopup(wl_proxy*);
    ~CCXdgPopup();


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

    void setConfigure(F<void(CCXdgPopup*, int32_t, int32_t, int32_t, int32_t)> &&handler);
    void setPopupDone(F<void(CCXdgPopup*)> &&handler);
    void setRepositioned(F<void(CCXdgPopup*, uint32_t)> &&handler);

    // --------------- Events --------------- //

    void sendDestroy();
    void sendGrab(wl_proxy*, uint32_t);
    void sendReposition(CCXdgPositioner*, uint32_t);

  private:
    struct {
        F<void(CCXdgPopup*, int32_t, int32_t, int32_t, int32_t)> configure;
        F<void(CCXdgPopup*)> popupDone;
        F<void(CCXdgPopup*, uint32_t)> repositioned;
    } requests;

    wl_proxy* pResource = nullptr;

    bool destroyed = false;

    void* pData = nullptr;
};



#undef F

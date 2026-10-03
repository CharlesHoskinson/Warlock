-- Windows-style snapping for floating windows.
--
-- Drag a window to the left/right screen edge to fill that half, into a corner
-- for a quarter, or to the top edge to maximize. Dragging a snapped window away
-- restores its previous size. SUPER + arrows do the same from the keyboard.
--
-- Title-bar drags: the patched hyprbars (~/src/hyprbars-dragend) calls
-- hypr_snap_drag_start()/hypr_snap_drag_end() via on_drag_start/on_drag_end, so the
-- window snaps the instant the mouse is released, and never while it's still held.
--
-- SUPER/ALT + drag has no release event in Hyprland's Lua API. These drags
-- restore a snapped window as it moves, but never guess when to snap it.

local EDGE = 6 -- px from a monitor edge that counts as touching it
local CORNER = 80 -- px from a corner that picks a quarter instead of a half
local GAP = 10 -- matches general.gaps_out
local TITLEBAR = 24 -- hyprbars bar_height (drawn above the window's origin)
local TICK_MS = 100

-- Pre-snap size per window address, so dragging away can restore it.
local snapped = {}

local function titlebar()
  return hl.plugin.hyprbars ~= nil and TITLEBAR or 0
end

-- Usable area of a monitor in layout coordinates, minus the bar and gaps.
local function work_area(m)
  local r = m.reserved or {}
  -- Hyprland reports reserved as [top, bottom, left, right]. Accept named
  -- fields too, for Lua wrappers that convert the JSON array to a record.
  local top, bottom = r.top or r[1] or 0, r.bottom or r[2] or 0
  local left, right = r.left or r[3] or 0, r.right or r[4] or 0
  local x = m.x + left + GAP
  local y = m.y + top + GAP + titlebar()
  local w = m.width / m.scale - left - right - 2 * GAP
  local h = m.height / m.scale - top - bottom - 2 * GAP - titlebar()
  return x, y, w, h
end

-- Geometry for a zone ("left", "right", "top_left", ...) on monitor m.
local function zone_rect(zone, m)
  local x, y, w, h = work_area(m)
  local half_w = math.floor((w - GAP) / 2)
  local half_h = math.floor((h - GAP - titlebar()) / 2)
  local right_x = x + half_w + GAP
  local lower_y = y + half_h + GAP + titlebar()

  local rects = {
    left = { x, y, half_w, h },
    right = { right_x, y, w - half_w - GAP, h },
    top_left = { x, y, half_w, half_h },
    top_right = { right_x, y, w - half_w - GAP, half_h },
    bottom_left = { x, lower_y, half_w, h - half_h - GAP - titlebar() },
    bottom_right = { right_x, lower_y, w - half_w - GAP, h - half_h - GAP - titlebar() },
  }
  return rects[zone]
end

-- Which snap zone the cursor is in, or nil when it isn't at an edge.
local function zone_at_cursor()
  local c = hl.get_cursor_pos()
  local m = hl.get_monitor_at_cursor()
  if not c or not m then
    return nil, nil
  end

  local mx, my = m.x, m.y
  local mw, mh = m.width / m.scale, m.height / m.scale
  local at_left, at_right = c.x <= mx + EDGE, c.x >= mx + mw - EDGE
  local near_top, near_bottom = c.y <= my + CORNER, c.y >= my + mh - CORNER

  if at_left or at_right then
    local side = at_left and "left" or "right"
    if near_top then
      return "top_" .. side, m
    elseif near_bottom then
      return "bottom_" .. side, m
    end
    return side, m
  elseif c.y <= my + EDGE then
    return "maximize", m
  end
  return nil, nil
end

local function target(w)
  return "address:" .. w.address
end

local function snap(w, zone, m)
  if zone == "maximize" then
    if w.fullscreen == 0 then
      hl.dispatch(hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle", window = target(w) }))
    end
    return
  end

  local rect = zone_rect(zone, m)
  if not rect then
    return
  end
  if not snapped[w.address] then
    snapped[w.address] = { w = w.size.x, h = w.size.y }
  end
  hl.dispatch(hl.dsp.window.resize({ x = rect[3], y = rect[4], window = target(w) }))
  hl.dispatch(hl.dsp.window.move({ x = rect[1], y = rect[2], window = target(w) }))
end

local function unsnap(w)
  local prev = snapped[w.address]
  if prev then
    snapped[w.address] = nil
    hl.dispatch(hl.dsp.window.resize({ x = prev.w, y = prev.h, window = target(w) }))
  end
  return prev
end

-- Watch the active floating window for movement and manual resizing.
local last = {}
local skip_address = nil -- ignore the geometry change dispatched by our own snap
local drag_address = nil -- title-bar release must belong to the same window

local function tick()
  local w = hl.get_active_window()
  if not w or not w.floating or w.fullscreen ~= 0 then
    last = {}
    return
  end

  local x, y, sw, sh = w.at.x, w.at.y, w.size.x, w.size.y
  local same_window = last.address == w.address
  local moved = same_window and (x ~= last.x or y ~= last.y)
  local resized = same_window and (sw ~= last.w or sh ~= last.h)
  last = { address = w.address, x = x, y = y, w = sw, h = sh }

  if skip_address then
    local skip_this = skip_address == w.address
    skip_address = nil
    if skip_this then return end
  end
  if not same_window or drag_address == w.address then
    return
  end

  if resized then
    -- A manual resize makes the old pre-snap size obsolete.
    snapped[w.address] = nil
  elseif moved then
    -- Moving a snapped window away restores its original dimensions.
    local prev = unsnap(w)
    if prev then last.w, last.h = prev.w, prev.h end
  end
end

-- Called by hyprbars (plugin:hyprbars:on_drag_start / on_drag_end).
function hypr_snap_drag_start(address)
  local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
  if w and w.floating and w.fullscreen == 0 then
    drag_address = w.address
    -- Dragging a snapped window away gives it its old size back right away.
    unsnap(w)
  else
    drag_address = nil
  end
end

function hypr_snap_drag_end(address)
  local started = drag_address
  drag_address = nil
  local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
  if not started or not w or w.address ~= started or not w.floating or w.fullscreen ~= 0 then
    return
  end
  local zone, m = zone_at_cursor()
  if zone then
    snap(w, zone, m)
    skip_address = w.address
  end
  last = {}
end

if omarchy_snap_timer then
  omarchy_snap_timer:set_enabled(false)
end
omarchy_snap_timer = hl.timer(tick, { timeout = TICK_MS, type = "repeat" })

-- Keyboard snapping, like Win + arrows.
local function snap_active(zone, address)
  return function()
    local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
    if not w then
      return
    end
    if not w.floating then
      hl.dispatch(hl.dsp.window.float({ action = "toggle", window = target(w) }))
    end
    if w.fullscreen ~= 0 then
      if zone == "maximize" then
        return
      end
      hl.dispatch(hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle", window = target(w) }))
    end
    snap(w, zone, w.monitor or hl.get_active_monitor())
    skip_address = w.address
  end
end

-- The SUPER+Z layout menu keeps the selected window's address while the menu
-- itself has focus, then calls this entry point after a zone is chosen.
function hypr_snap_zone(zone, address)
  local valid = {
    left = true, right = true, top_left = true, top_right = true,
    bottom_left = true, bottom_right = true, maximize = true,
  }
  if valid[zone] then snap_active(zone, address)() end
end

local function restore_active()
  local w = hl.get_active_window()
  if not w then
    return
  end
  if w.fullscreen ~= 0 then
    hl.dispatch(hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle", window = target(w) }))
    skip_address = w.address
  elseif snapped[w.address] then
    unsnap(w)
    hl.dispatch(hl.dsp.window.center({ window = target(w) }))
    skip_address = w.address
  else
    -- Win+Down minimizes a normal window after restore, as on Windows.
    hl.exec_cmd(os.getenv("HOME") .. "/.local/bin/hypr-windowctl minimize " .. w.address)
  end
end

-- These replace Omarchy's SUPER + arrow "focus left/right/up/down window".
hl.unbind("SUPER + LEFT")
hl.unbind("SUPER + RIGHT")
hl.unbind("SUPER + UP")
hl.unbind("SUPER + DOWN")
o.bind("SUPER + LEFT", "Snap window left", snap_active("left"))
o.bind("SUPER + RIGHT", "Snap window right", snap_active("right"))
o.bind("SUPER + UP", "Maximize window", snap_active("maximize"))
o.bind("SUPER + DOWN", "Restore or minimize window", restore_active)
o.bind("SUPER + Z", "Choose snap layout", os.getenv("HOME") .. "/.local/bin/hypr-snap-layout")
o.bind("SUPER + M", "Minimize all windows", os.getenv("HOME") .. "/.local/bin/hypr-windowctl minimize-all")
o.bind("SUPER + SHIFT + M", "Restore windows minimized together", os.getenv("HOME") .. "/.local/bin/hypr-windowctl restore-all")
-- Was Omarchy's "Restore window width"; Windows uses this to minimize others.
hl.unbind("SUPER + Home")
o.bind("SUPER + Home", "Minimize other windows", os.getenv("HOME") .. "/.local/bin/hypr-windowctl minimize-others")

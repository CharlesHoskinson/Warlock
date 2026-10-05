-- Windows-style snapping for floating windows.
--
-- Drag a window to the left/right screen edge to fill that half, into a corner
-- for a quarter, or to the top edge to maximize. Dragging a snapped window away
-- restores its previous size. SUPER + arrows do the same from the keyboard.
--
-- The native hyprbars bridge captures both titlebar and modifier drag ownership
-- before movement and finishes synchronously after compositor cleanup. The
-- legacy callbacks remain available for older plugin builds.

local EDGE = 6 -- px from a monitor edge that counts as touching it
local CORNER = 80 -- px from a corner that picks a quarter instead of a half
local GAP = 10 -- matches general.gaps_out
local TITLEBAR = 24 -- hyprbars bar_height (drawn above the window's origin)
local TICK_MS = 100

-- Pre-snap size per window address, so dragging away can restore it.
local snapped = {}
-- A release callback may launch Snap Bar selection asynchronously. Retain the
-- drag-start normal rectangle until that exact owner's snap is dispatched.
local release_normal = nil
local drag_normal = nil
local drag_source = nil
local controls_bin = os.getenv("HOME") .. "/.local/bin/"

local function mark_snapped(w, enabled)
  if hl.dsp.window.tag then
    hl.dispatch(hl.dsp.window.tag({ tag = enabled and "+win-snapped" or "-win-snapped", window = "address:" .. w.address }))
  end
  if hl.dsp.window.set_prop then
    hl.dispatch(hl.dsp.window.set_prop({ prop = "rounding", value = enabled and "0" or "8", window = "address:" .. w.address }))
  end
end

local function notify_snap(w, zone, assist)
  local command = controls_bin .. "hypr-snap-groups record " .. w.address .. " " .. zone
  local normal = snapped[w.address]
  if normal and zone ~= "maximize" then
    command = command .. " " .. normal.w .. " " .. normal.h
    if normal.x and normal.y then command = command .. " " .. normal.x .. " " .. normal.y end
  end
  if assist and zone ~= "maximize" then
    command = command .. " && " .. controls_bin .. "hypr-window-menu assist " .. w.address .. " " .. zone
  end
  hl.exec_cmd(command)
end

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
local function zone_area_rect(zone, x, y, w, h)
  local half_w = math.floor((w - GAP) / 2)
  local half_h = math.floor((h - GAP - titlebar()) / 2)
  local right_x = x + half_w + GAP
  local lower_y = y + half_h + GAP + titlebar()
  local third_w = math.floor((w - 2 * GAP) / 3)
  local third_x = x + third_w + GAP
  local last_third_x = x + 2 * (third_w + GAP)

  local rects = {
    left = { x, y, half_w, h },
    right = { right_x, y, w - half_w - GAP, h },
    top_left = { x, y, half_w, half_h },
    top_right = { right_x, y, w - half_w - GAP, half_h },
    bottom_left = { x, lower_y, half_w, h - half_h - GAP - titlebar() },
    bottom_right = { right_x, lower_y, w - half_w - GAP, h - half_h - GAP - titlebar() },
    third_left = { x, y, third_w, h },
    third_center = { third_x, y, third_w, h },
    third_right = { last_third_x, y, w - 2 * (third_w + GAP), h },
    two_thirds_left = { x, y, 2 * third_w + GAP, h },
    two_thirds_right = { third_x, y, w - third_w - GAP, h },
  }
  return rects[zone]
end

local function zone_rect(zone, m)
  return zone_area_rect(zone, work_area(m))
end

local function monitor_area(m)
  local x,y,w,h = work_area(m)
  return {x=x,y=y,w=w,h=h,id=m.id}
end

local function translated_rect(rect, old_area, new_area, proportional_size)
  local width = math.min(new_area.w, proportional_size and rect.w / old_area.w * new_area.w or rect.w)
  local height = math.min(new_area.h, proportional_size and rect.h / old_area.h * new_area.h or rect.h)
  local x = math.max(new_area.x, math.min(new_area.x + (rect.x-old_area.x)/old_area.w*new_area.w, new_area.x+new_area.w-width))
  local y = math.max(new_area.y, math.min(new_area.y + (rect.y-old_area.y)/old_area.h*new_area.h, new_area.y+new_area.h-height))
  return {x=math.floor(x+0.5),y=math.floor(y+0.5),w=math.floor(width+0.5),h=math.floor(height+0.5)}
end

local function translated_snap(rect, normal, old_area, new_area)
  if not normal.zone then return translated_rect(rect,old_area,new_area,true) end
  local old_zone = normal.zone and zone_area_rect(normal.zone,old_area.x,old_area.y,old_area.w,old_area.h)
  if old_zone and math.abs(rect.x-old_zone[1])<=2 and math.abs(rect.y-old_zone[2])<=2
    and math.abs(rect.w-old_zone[3])<=2 and math.abs(rect.h-old_zone[4])<=2 then
    local zone = zone_area_rect(normal.zone,new_area.x,new_area.y,new_area.w,new_area.h)
    return {x=zone[1],y=zone[2],w=zone[3],h=zone[4]}
  end
  -- Scale pane contents separately from fixed shared-boundary gutters, so
  -- neighboring custom ratios still have usable resize separators afterwards.
  local zone = normal.zone or ""
  local columns, column, span = 2, zone:find("right",1,true) and 1 or 0, 1
  if zone:find("third",1,true) then
    columns=3
    if zone=="third_center" then column=1 elseif zone=="third_right" then column=2 else column=0 end
    if zone=="two_thirds_left" or zone=="two_thirds_right" then span=2;column=zone=="two_thirds_right" and 1 or 0 end
  end
  local quarter = zone:sub(1,4)=="top_" or zone:sub(1,7)=="bottom_"
  local rows,row = quarter and 2 or 1,zone:sub(1,7)=="bottom_" and 1 or 0
  local gutter=GAP+titlebar()
  local xratio=(new_area.w-(columns-1)*GAP)/(old_area.w-(columns-1)*GAP)
  local yratio=(new_area.h-(rows-1)*gutter)/(old_area.h-(rows-1)*gutter)
  local width=math.min(new_area.w,(rect.w-(span-1)*GAP)*xratio+(span-1)*GAP)
  local height=math.min(new_area.h,rect.h*yratio)
  local x=new_area.x+(rect.x-old_area.x-column*GAP)*xratio+column*GAP
  local y=new_area.y+(rect.y-old_area.y-row*gutter)*yratio+row*gutter
  return {x=math.floor(math.max(new_area.x,math.min(x,new_area.x+new_area.w-width))+0.5),
          y=math.floor(math.max(new_area.y,math.min(y,new_area.y+new_area.h-height))+0.5),
          w=math.floor(width+0.5),h=math.floor(height+0.5)}
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

local function has_snap(w)
  if snapped[w.address] then return true end
  for _, tag in ipairs(w.tags or {}) do
    if tag == "win-snapped" or tag == "win-snapped*" then return true end
  end
  return false
end

local function snap(w, zone, m, assist)
  if zone == "maximize" then
    if release_normal and release_normal.address == w.address and release_normal.pid == w.pid then
      local normal = release_normal.normal
      if normal.area and normal.area.id ~= m.id then
        normal = translated_rect(normal, normal.area, monitor_area(m), false)
      end
      hl.dispatch(hl.dsp.window.resize({x=normal.w,y=normal.h,window=target(w)}))
      hl.dispatch(hl.dsp.window.move({x=normal.x,y=normal.y,window=target(w)}))
      release_normal = nil
    end
    snapped[w.address] = nil
    mark_snapped(w, false)
    notify_snap(w, zone, false)
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
    if release_normal and release_normal.address == w.address and release_normal.pid == w.pid then
      local normal = release_normal.normal
      if normal.area and normal.area.id ~= m.id then
        normal = translated_rect(normal, normal.area, monitor_area(m), false)
      end
      snapped[w.address] = {x=normal.x,y=normal.y,w=normal.w,h=normal.h}
      release_normal = nil
    else
      snapped[w.address] = { x = w.at.x, y = w.at.y, w = w.size.x, h = w.size.y }
    end
  end
  snapped[w.address].zone = zone
  snapped[w.address].area = monitor_area(m)
  snapped[w.address].rect = {x=rect[1],y=rect[2],w=rect[3],h=rect[4]}
  hl.dispatch(hl.dsp.window.resize({ x = rect[3], y = rect[4], window = target(w) }))
  hl.dispatch(hl.dsp.window.move({ x = rect[1], y = rect[2], window = target(w) }))
  mark_snapped(w, true)
  notify_snap(w, zone, assist)
end

local function unsnap(w, restore_position)
  local prev = snapped[w.address]
  if prev or has_snap(w) then
    snapped[w.address] = nil
    mark_snapped(w, false)
    hl.exec_cmd(controls_bin .. "hypr-snap-groups unsnap " .. w.address)
    if prev then hl.dispatch(hl.dsp.window.resize({ x = prev.w, y = prev.h, window = target(w) })) end
    if restore_position and prev and prev.x and prev.y then
      hl.dispatch(hl.dsp.window.move({ x = prev.x, y = prev.y, window = target(w) }))
    end
  end
  return prev
end

-- Watch the active floating window for movement and manual resizing.
local last = {}
local skip_address = nil -- ignore the geometry change dispatched by our own snap
local drag_address = nil -- title-bar release must belong to the same window
local snapbar_open = false
local shake = nil

local function drag_features(w, dx)
  local c, m = hl.get_cursor_pos(), hl.get_monitor_at_cursor()
  if c and m then
    if not snapbar_open and c.y <= m.y + 70 and c.x > m.x + CORNER and c.x < m.x + m.width / m.scale - CORNER then
      snapbar_open = true
      hl.exec_cmd(controls_bin .. "hypr-window-menu snapbar " .. w.address)
    elseif snapbar_open and c.y > m.y + 350 then
      snapbar_open = false
      hl.exec_cmd(controls_bin .. "hypr-window-menu hide")
    end
  end
  if shake and not shake.triggered then
    shake.ticks = shake.ticks + 1
    if shake.ticks > 12 then shake.ticks, shake.reversals, shake.direction = 0, 0, 0 end
    shake.distance = shake.distance + dx
    if math.abs(shake.distance) >= 35 then
      local direction = shake.distance > 0 and 1 or -1
      if shake.direction ~= 0 and direction ~= shake.direction then shake.reversals = shake.reversals + 1 end
      shake.direction, shake.distance = direction, 0
      if shake.reversals >= 3 then
        shake.triggered = true
        hl.exec_cmd(controls_bin .. "hypr-windowctl minimize-others " .. w.address)
      end
    end
  end
end

local file_drag_last = {}
local function relay_file_drag()
  local plugin = hl.plugin.hyprbars
  if not plugin or not plugin.file_drag_active then return end
  local active, stamp = plugin.file_drag_active()
  local c, m = hl.get_cursor_pos(), hl.get_monitor_at_cursor()
  local x, y, id = c and math.floor(c.x+0.5) or 0, c and math.floor(c.y+0.5) or 0, m and m.id or -1
  -- One inactive update, changed coordinates, or a heartbeat during a held
  -- drag. The monotonic stamp rejects delayed/out-of-order shell invocations.
  if file_drag_last.active ~= active or (active and (file_drag_last.x ~= x or file_drag_last.y ~= y
      or file_drag_last.id ~= id or stamp-file_drag_last.stamp >= 250)) then
    file_drag_last = {active=active,x=x,y=y,id=id,stamp=stamp}
    hl.exec_cmd(string.format("omarchy-shell hoskinson.windows fileDrag %s %d %d %d %d", tostring(active), x, y, id, stamp))
  end
end

local function tick()
  relay_file_drag()
  if release_normal then
    release_normal.ticks = release_normal.ticks + 1
    if release_normal.ticks > 50 then release_normal = nil end
  end
  -- Monitor removal and scale/reserved-area changes can affect inactive
  -- snapped windows too. Reconcile their stored geometry before watching a
  -- manual drag/resize, so the monitor change is not mistaken for user input.
  local reflowed = false
  for address, normal in pairs(snapped) do
    local window = hl.get_window("address:" .. address)
    if window and window.floating and window.fullscreen == 0 and normal.area and normal.rect then
      local area = monitor_area(window.monitor or hl.get_active_monitor())
      local old = normal.area
      if area.id~=old.id or area.x~=old.x or area.y~=old.y or area.w~=old.w or area.h~=old.h then
        local rect = translated_snap(normal.rect,normal,old,area)
        local restored = translated_rect({x=normal.x or old.x,y=normal.y or old.y,w=normal.w,h=normal.h},old,area,false)
        restored.zone,restored.area,restored.rect=normal.zone,area,rect
        snapped[address]=restored
        hl.dispatch(hl.dsp.window.resize({x=rect.w,y=rect.h,window=target(window)}))
        hl.dispatch(hl.dsp.window.move({x=rect.x,y=rect.y,window=target(window)}))
        mark_snapped(window,true)
        if normal.zone then notify_snap(window,normal.zone,false) end
        reflowed=true
      end
    end
  end
  if reflowed then last={} end
  local w = hl.get_active_window()
  if not w or not w.floating or w.fullscreen ~= 0 then
    last = {}
    return
  end

  local x, y, sw, sh = w.at.x, w.at.y, w.size.x, w.size.y
  local previous_geometry = last
  local same_window = last.address == w.address
  local dx = same_window and x - last.x or 0
  local moved = same_window and (x ~= last.x or y ~= last.y)
  local resized = same_window and (sw ~= last.w or sh ~= last.h)
  last = { address = w.address, x = x, y = y, w = sw, h = sh }

  if skip_address then
    local skip_this = skip_address == w.address
    skip_address = nil
    if skip_this then return end
  end
  if drag_address == w.address then
    drag_features(w, dx)
    return
  end
  if not same_window then
    return
  end

  if resized then
    -- Shared snap boundaries resize adjoining group members together. A single
    -- snapped window has no neighbours and the backend dissolves its snap state.
    if has_snap(w) then
      -- Preserve a manual resize immediately if another move happens before
      -- the asynchronous group controller finishes.
      local normal = snapped[w.address] or {}
      snapped[w.address] = { x = x, y = y, w = sw, h = sh, zone=normal.zone,
        area=monitor_area(w.monitor or hl.get_active_monitor()),rect={x=x,y=y,w=sw,h=sh} }
      hl.exec_cmd(string.format("%shypr-snap-groups resize %s %d %d %d %d", controls_bin, w.address,
        previous_geometry.x, previous_geometry.y, previous_geometry.w, previous_geometry.h))
    end
  elseif moved then
    -- Moving a snapped window away restores its original dimensions.
    local prev = unsnap(w)
    if prev then last.w, last.h = prev.w, prev.h end
  end
end

-- Native bridge callbacks; the older titlebar subprocess hooks use these too.
function hypr_snap_drag_start(address, anchor, press)
  local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
  if w and w.floating and (w.fullscreen == 0 or w.fullscreen == 1) then
    drag_address = w.address
    drag_source = {pid=w.pid,x=w.at.x,y=w.at.y,w=w.size.x,h=w.size.y,previous=snapped[w.address],maximized=w.fullscreen==1}
    if drag_source.maximized then
      hl.dispatch(hl.dsp.window.fullscreen({mode="maximized",action="toggle",window=target(w)}))
      w = hl.get_window(target(w)) or w
      drag_source.normal = {x=w.at.x,y=w.at.y,w=w.size.x,h=w.size.y}
    end
    shake = { ticks = 0, reversals = 0, direction = 0, distance = 0 }
    snapbar_open = false
    -- Dragging a snapped window away gives it its old size back right away.
    release_normal = nil
    local previous = unsnap(w)
    drag_normal = previous or {x=w.at.x,y=w.at.y,w=w.size.x,h=w.size.y}
    drag_normal.area = monitor_area(w.monitor or hl.get_active_monitor())
    if anchor and (previous or drag_source.maximized) then
      local c = press or hl.get_cursor_pos()
      if c then
        local fx = math.max(0, math.min(1, (c.x-drag_source.x)/drag_source.w))
        local dy = c.y-drag_source.y
        if dy >= 0 then dy = math.max(0, math.min(1, dy/drag_source.h))*drag_normal.h end
        hl.dispatch(hl.dsp.window.move({x=math.floor(c.x-fx*drag_normal.w+0.5),y=math.floor(c.y-dy+0.5),window=target(w)}))
      end
    end
  else
    drag_address = nil
    drag_normal = nil
    drag_source = nil
  end
end

function hypr_snap_drag_end(address)
  local started = drag_address
  drag_address = nil
  shake = nil
  local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
  local source = drag_source
  drag_source = nil
  if not started or not w or w.address ~= started or (source and source.pid ~= w.pid) or not w.floating or w.fullscreen ~= 0 then
    drag_normal = nil
    if snapbar_open then hl.exec_cmd(controls_bin .. "hypr-window-menu hide") end
    snapbar_open = false
    return
  end
  if drag_normal then release_normal = {address=w.address,pid=w.pid,normal=drag_normal,ticks=0} end
  drag_normal = nil
  if snapbar_open then
    snapbar_open = false
    hl.exec_cmd(controls_bin .. "hypr-window-menu snapbar-release " .. w.address)
    last = {}
    return
  end
  local zone, m = zone_at_cursor()
  if zone then
    snap(w, zone, m, true)
    skip_address = w.address
  else
    release_normal = nil
  end
  last = {}
end

function hypr_snap_drag_cancel(address)
  local source, started = drag_source, drag_address
  drag_source, drag_address, drag_normal, release_normal, shake = nil, nil, nil, nil, nil
  if snapbar_open then hl.exec_cmd(controls_bin .. "hypr-window-menu hide") end
  snapbar_open = false
  local w = address and hl.get_window("address:" .. address)
  if w and w.address == started and source and source.pid == w.pid and w.floating and w.fullscreen == 0 then
    local rect = source.normal or source
    hl.dispatch(hl.dsp.window.resize({x=rect.w,y=rect.h,window=target(w)}))
    hl.dispatch(hl.dsp.window.move({x=rect.x,y=rect.y,window=target(w)}))
    if source.maximized then
      hl.dispatch(hl.dsp.window.fullscreen({mode="maximized",action="toggle",window=target(w)}))
    end
    snapped[w.address] = source.previous
    mark_snapped(w, source.previous ~= nil)
    if source.previous and source.previous.zone then notify_snap(w,source.previous.zone,false) end
    skip_address = w.address
  end
  last = {}
end

if hl.plugin.hyprbars and hl.plugin.hyprbars.drag_bridge and hl.plugin.hyprbars.drag_bridge() then
  hl.on("hyprbars.drag_start",function(w,x,y)
    local press = type(x)=="number" and type(y)=="number" and {x=x,y=y} or nil
    hypr_snap_drag_start(w.address,true,press)
  end)
  hl.on("hyprbars.drag_finish",function(w,released)
    if released then hypr_snap_drag_end(w.address) else hypr_snap_drag_cancel(w.address) end
  end)
end

if omarchy_snap_timer then
  omarchy_snap_timer:set_enabled(false)
end
omarchy_snap_timer = hl.timer(tick, { timeout = TICK_MS, type = "repeat" })

-- Keyboard snapping, like Win + arrows.
local function snap_active(zone, address, assist)
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
    snap(w, zone, w.monitor or hl.get_active_monitor(), assist ~= false)
    skip_address = w.address
  end
end

-- The SUPER+Z layout menu keeps the selected window's address while the menu
-- itself has focus, then calls this entry point after a zone is chosen.
function hypr_snap_zone(zone, address, assist)
  local valid = {
    left = true, right = true, top_left = true, top_right = true,
    bottom_left = true, bottom_right = true, maximize = true,
    third_left = true, third_center = true, third_right = true,
    two_thirds_left = true, two_thirds_right = true,
  }
  if valid[zone] then snap_active(zone, address, assist)() end
end

function hypr_snap_restore(address)
  local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
  if not w then return end
  if w.fullscreen ~= 0 then
    hl.dispatch(hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle", window = target(w) }))
  else
    unsnap(w, true)
  end
  skip_address = w.address
end

function hypr_snap_discard_release(address)
  if release_normal and release_normal.address == address then release_normal = nil end
end

function hypr_snap_forget(address)
  local w = hl.get_window("address:" .. address)
  snapped[address] = nil
  if w then mark_snapped(w, false) end
  skip_address = address
end

function hypr_snap_set_geometry(address, x, y, width, height)
  local w = hl.get_window("address:" .. address)
  if not w or width < 1 or height < 1 then return end
  if not snapped[address] then snapped[address] = { w = w.size.x, h = w.size.y } end
  hl.dispatch(hl.dsp.window.resize({ x = width, y = height, window = target(w) }))
  hl.dispatch(hl.dsp.window.move({ x = x, y = y, window = target(w) }))
  mark_snapped(w, true)
  snapped[address].area = monitor_area(w.monitor or hl.get_active_monitor())
  snapped[address].rect = {x=x,y=y,w=width,h=height}
  skip_address = address
end

function hypr_snap_hydrate(address, width, height, x, y, zone)
  local w = hl.get_window("address:" .. address)
  if w and width > 0 and height > 0 then
    snapped[address] = { x = x, y = y, w = width, h = height, zone = zone,
      area=monitor_area(w.monitor or hl.get_active_monitor()),
      rect={x=w.at.x,y=w.at.y,w=w.size.x,h=w.size.y} }
    mark_snapped(w, true)
  end
end
-- Normal restore sizes live in session state, guarded by compositor stableId.
-- Rehydrate after a Lua reload so an in-flight customization keeps restore working.
hl.exec_cmd(controls_bin .. "hypr-snap-groups hydrate")
if hl.on then
  hl.on("window.close", function(w)
    if w then
      snapped[w.address] = nil
      if drag_address == w.address then hypr_snap_drag_cancel(w.address) end
      if release_normal and release_normal.address == w.address then release_normal = nil end
      hl.exec_cmd(controls_bin .. "hypr-snap-groups unsnap " .. w.address)
    end
  end)
  hl.on("window.fullscreen", function(w)
    if w and hl.dsp.window.set_prop then
      local square = w.fullscreen ~= 0 or has_snap(w)
      hl.dispatch(hl.dsp.window.set_prop({ prop = "rounding", value = square and "0" or "8", window = target(w) }))
    end
  end)
end

local function restore_active()
  local w = hl.get_active_window()
  if not w then
    return
  end
  if w.fullscreen ~= 0 then
    hl.dispatch(hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle", window = target(w) }))
    skip_address = w.address
  elseif has_snap(w) then
    unsnap(w, true)
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
o.bind("ALT + SPACE", "Window system menu", controls_bin .. "hypr-window-menu system")
o.bind("SUPER + CTRL + SHIFT + F12", "Toggle reduced motion", controls_bin .. "hypr-reduced-motion toggle")
-- Previously Display settings and grouped-window focus. These are Windows'
-- virtual desktop creation/close/navigation shortcuts.
hl.unbind("SUPER + CTRL + D")
hl.unbind("SUPER + CTRL + F4")
hl.unbind("SUPER + CTRL + LEFT")
hl.unbind("SUPER + CTRL + RIGHT")
o.bind("SUPER + CTRL + D", "New virtual desktop", controls_bin .. "hypr-desktops new")
o.bind("SUPER + CTRL + F4", "Close virtual desktop", controls_bin .. "hypr-desktops close")
o.bind("SUPER + CTRL + LEFT", "Previous virtual desktop", controls_bin .. "hypr-desktops switch prev")
o.bind("SUPER + CTRL + RIGHT", "Next virtual desktop", controls_bin .. "hypr-desktops switch next")

-- Previous shift-arrow bindings swapped tiles. Floating windows now use the
-- Windows shortcuts for moving to adjacent displays and vertical maximize.
local vertical = {}
function hypr_vertical_maximize(address)
  local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
  if not w or not w.floating or w.fullscreen ~= 0 then return end
  if not vertical[w.address] then
    vertical[w.address] = { x = w.at.x, y = w.at.y, w = w.size.x, h = w.size.y }
  end
  local _, y, _, h = work_area(w.monitor or hl.get_active_monitor())
  local width, x = w.size.x, w.at.x
  unsnap(w)
  hl.dispatch(hl.dsp.window.resize({ x = width, y = h, window = target(w) }))
  hl.dispatch(hl.dsp.window.move({ x = x, y = y, window = target(w) }))
  skip_address = w.address
end
function hypr_vertical_restore(address)
  local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
  if not w then return end
  local prev = vertical[w.address]
  if not prev then return end
  vertical[w.address] = nil
  hl.dispatch(hl.dsp.window.resize({ x = prev.w, y = prev.h, window = target(w) }))
  hl.dispatch(hl.dsp.window.move({ x = prev.x, y = prev.y, window = target(w) }))
  skip_address = w.address
end
-- Win+Shift+arrows retains snap state and relative geometry across displays.
-- Normal restore coordinates must move too, otherwise Restore returns to the
-- previous screen. Custom shared-boundary ratios use the current rectangle.
function hypr_monitor_transfer(direction, address)
  local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
  if not w or (direction ~= "+1" and direction ~= "-1") then return end
  local old_monitor = w.monitor or hl.get_active_monitor()
  local old_area = monitor_area(old_monitor)
  local geometry = { x = w.at.x, y = w.at.y, w = w.size.x, h = w.size.y }
  local normal = snapped[w.address]
  hl.dispatch(hl.dsp.window.move({ monitor = direction, window = target(w) }))
  w = hl.get_window(target(w)) or w
  local new_monitor = w.monitor or hl.get_active_monitor()
  if new_monitor.id == old_monitor.id then return end
  local area = monitor_area(new_monitor)
  local moved = normal and translated_snap(geometry,normal,old_area,area) or translated_rect(geometry,old_area,area,false)
  if w.fullscreen == 0 then
    hl.dispatch(hl.dsp.window.resize({ x = moved.w, y = moved.h, window = target(w) }))
    hl.dispatch(hl.dsp.window.move({ x = moved.x, y = moved.y, window = target(w) }))
  end
  if normal then
    local moved_normal = translated_rect({x = normal.x or old_area.x, y = normal.y or old_area.y, w = normal.w, h = normal.h},old_area,area,false)
    moved_normal.zone,moved_normal.area,moved_normal.rect = normal.zone,area,moved
    snapped[w.address] = moved_normal
    mark_snapped(w, true)
    if normal.zone then notify_snap(w, normal.zone, false) end
  end
  skip_address = w.address
end
for _, key in ipairs({"LEFT", "RIGHT", "UP", "DOWN"}) do hl.unbind("SUPER + SHIFT + " .. key) end
o.bind("SUPER + SHIFT + LEFT", "Move window to previous display", function() hypr_monitor_transfer("-1") end)
o.bind("SUPER + SHIFT + RIGHT", "Move window to next display", function() hypr_monitor_transfer("+1") end)
o.bind("SUPER + SHIFT + UP", "Maximize window vertically", function() hypr_vertical_maximize() end)
o.bind("SUPER + SHIFT + DOWN", "Restore vertical window size", function() hypr_vertical_restore() end)

-- These replace numeric workspace switching with Windows taskbar activation.
for number = 1, 9 do
  local index = tostring(number)
  for _, modifiers in ipairs({"SUPER", "SUPER + SHIFT", "SUPER + ALT"}) do
    hl.unbind(modifiers .. " + " .. index)
  end
  o.bind("SUPER + " .. index, "Activate taskbar app " .. index, "omarchy-shell hoskinson.windows activate " .. index)
  o.bind("SUPER + SHIFT + " .. index, "Launch taskbar app " .. index, "omarchy-shell hoskinson.windows launch " .. index)
  o.bind("SUPER + ALT + " .. index, "Taskbar Jump List " .. index, "omarchy-shell hoskinson.windows menu " .. index)
end
hl.unbind("SUPER + T")
hl.unbind("SUPER + SHIFT + T")
hl.unbind("SUPER + TAB")
o.bind("SUPER + T", "Next taskbar app", "omarchy-shell hoskinson.windows cycle 1")
o.bind("SUPER + SHIFT + T", "Previous taskbar app", "omarchy-shell hoskinson.windows cycle -1")
o.bind("SUPER + TAB", "Task View", "omarchy-shell shell toggle hoskinson.taskview")
-- Replace the immediate focus/reveal Alt+Tab bindings with a chooser that
-- commits on Alt release, including minimized windows on this desktop.
hl.unbind("ALT + TAB")
hl.unbind("ALT + SHIFT + TAB")
o.bind("ALT + TAB", "Switch windows", controls_bin .. "hypr-window-menu switcher")
o.bind("ALT + SHIFT + TAB", "Switch windows backwards", controls_bin .. "hypr-window-menu switcher -1")
o.bind("ALT + ALT_L", "Select switched window", controls_bin .. "hypr-window-menu switcher-commit", { release = true, non_consuming = true })
o.bind("ALT + ALT_R", "Select switched window", controls_bin .. "hypr-window-menu switcher-commit", { release = true, non_consuming = true })
-- Was Omarchy's "Restore window width"; Windows uses this to minimize others.
hl.unbind("SUPER + Home")
o.bind("SUPER + Home", "Minimize other windows", os.getenv("HOME") .. "/.local/bin/hypr-windowctl minimize-others")

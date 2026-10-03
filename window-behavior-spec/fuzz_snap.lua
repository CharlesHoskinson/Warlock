-- Run with: lua fuzz_snap.lua [path/to/snap.lua]
-- Loads the real snap script behind a small Hyprland mock. No desktop state changes.
local directory = debug.getinfo(1, "S").source:sub(2):match("(.*/)") or "./"
local script = arg[1] or os.getenv("HOME") .. "/.config/hypr/snap.lua"
local windows, binds, commands, exec_commands = {}, {}, {}, {}
local active, monitor, cursor, tick
local normal_sizes, listeners = {}, {}
local transfer_monitor
local file_drag_active, native_stamp = false, 0

local function window(address, width, height)
  local w = {
    address = address, floating = true, fullscreen = 0,
    at = { x = 300, y = 300 }, size = { x = width or 400, y = height or 300 },
    monitor = monitor,
  }
  windows[address] = w
  return w
end

local function command(kind)
  return function(params) return { kind = kind, params = params } end
end

hl = {
  plugin = { hyprbars = {drag_bridge=function() return true end,file_drag_active=function() return file_drag_active,native_stamp end} },
  dsp = { window = {
    resize = command("resize"), move = command("move"),
    fullscreen = command("fullscreen"), float = command("float"),
    center = command("center"), tag = command("tag"), set_prop = command("set_prop"),
  } },
  get_active_window = function() return active end,
  get_window = function(selector) return windows[selector:match("^address:(.*)$")] end,
  get_active_monitor = function() return monitor end,
  get_cursor_pos = function() return cursor end,
  get_monitor_at_cursor = function() return monitor end,
  timer = function(callback)
    tick = function() native_stamp=native_stamp+100;callback() end
    return { set_enabled = function() end }
  end,
  unbind = function() end,
  on = function(event, callback) listeners[event] = callback end,
  exec_cmd = function(cmd)
    exec_commands[#exec_commands + 1] = cmd
    local recorded, zone, width, height = cmd:match("hypr%-snap%-groups record (%S+) (%S+) (%S+) (%S+)")
    if recorded and tonumber(width) and tonumber(height) then
      local _, _, _, _, px, py = cmd:match("hypr%-snap%-groups record (%S+) (%S+) (%S+) (%S+) (%S+) (%S+)")
      normal_sizes[recorded] = { tonumber(width), tonumber(height), tonumber(px), tonumber(py), zone }
    end
    local forgotten = cmd:match("hypr%-snap%-groups unsnap (%S+)")
    if forgotten then normal_sizes[forgotten] = nil end
    if cmd:find("hypr-snap-groups hydrate", 1, true) and hypr_snap_hydrate then
      for address, size in pairs(normal_sizes) do
        if windows[address] then hypr_snap_hydrate(address, size[1], size[2], size[3], size[4], size[5]) end
      end
    end
    -- This harness has standalone windows; emulate the backend's no-group resize callback.
    local address = cmd:match("hypr%-snap%-groups resize (%S+)")
    if address and hypr_snap_forget then hypr_snap_forget(address) end
  end,
  dispatch = function(cmd)
    commands[#commands + 1] = cmd
    local address = cmd.params.window:match("^address:(.*)$")
    local w = assert(windows[address], "unknown dispatch target " .. address)
    if cmd.kind == "resize" then
      w.size.x, w.size.y = cmd.params.x, cmd.params.y
    elseif cmd.kind == "move" then
      if cmd.params.monitor then
        w.monitor = transfer_monitor or w.monitor
      else w.at.x, w.at.y = cmd.params.x, cmd.params.y end
    elseif cmd.kind == "fullscreen" then
      w.fullscreen = (w.fullscreen == 0) and 1 or 0
      if listeners["window.fullscreen"] then listeners["window.fullscreen"](w) end
    elseif cmd.kind == "tag" then
      w.snapped_tag = cmd.params.tag == "+win-snapped"
      w.tags = w.snapped_tag and {"win-snapped"} or {}
    elseif cmd.kind == "set_prop" then
      assert(cmd.params.prop == "rounding")
      w.rounding = tonumber(cmd.params.value)
    elseif cmd.kind == "float" then
      w.floating = not w.floating
    end
  end,
}
o = { bind = function(key, _, callback) binds[key] = callback end }
monitor = { x = 0, y = 0, width = 1600, height = 1000,
  scale = 1, reserved = { top = 28, bottom = 0, left = 0, right = 0 } }
cursor = { x = 400, y = 400 }
dofile(script)

local function near(actual, expected, label)
  assert(math.abs(actual - expected) < 0.0001,
    (label or "value") .. ": expected " .. expected .. ", got " .. actual)
end

-- The installed timer relays only transitions, movement, or held-drag heartbeat.
tick()
local relay_count=#exec_commands
for _=1,10 do tick() end
assert(#exec_commands==relay_count,"inactive drag relay spawned repeated shell calls")
file_drag_active=true;tick()
assert(exec_commands[#exec_commands]:find("fileDrag true",1,true),"active file drag not relayed")
relay_count=#exec_commands
tick();tick()
assert(#exec_commands==relay_count,"unchanged drag relayed before heartbeat")
tick()
assert(#exec_commands==relay_count+1,"held drag heartbeat missing")
file_drag_active=false;tick()
assert(exec_commands[#exec_commands]:find("fileDrag false",1,true),"drag end not relayed")

-- Native callbacks use a captured owner; cancellation restores source geometry
-- and snapped membership, with PID protection against address reuse.
local cancelled = window("cancelled",600,350)
cancelled.pid=101
active=cancelled
cursor={x=500,y=400}
listeners["hyprbars.drag_start"](cancelled)
cancelled.at.x,cancelled.at.y=900,500
listeners["hyprbars.drag_finish"](cancelled,false)
near(cancelled.at.x,300,"cancel source x")
near(cancelled.at.y,300,"cancel source y")
hypr_snap_zone("left",cancelled.address,false)
local source_x,source_y,source_w,source_h=cancelled.at.x,cancelled.at.y,cancelled.size.x,cancelled.size.y
cursor={x=source_x+source_w*.9,y=source_y+150}
listeners["hyprbars.drag_start"](cancelled)
assert(cancelled.at.x<=cursor.x and cancelled.at.x+cancelled.size.x>=cursor.x,"unsnap lost cursor anchor")
cancelled.at.x,cancelled.at.y=900,500
listeners["hyprbars.drag_finish"](cancelled,false)
near(cancelled.at.x,source_x,"cancel snapped source x")
near(cancelled.at.y,source_y,"cancel snapped source y")
near(cancelled.size.x,source_w,"cancel snapped width")
near(cancelled.size.y,source_h,"cancel snapped height")
assert(cancelled.snapped_tag,"cancel lost snap membership")
hypr_snap_restore(cancelled.address)
near(cancelled.at.x,300,"cancel lost normal restore x")
listeners["hyprbars.drag_start"](cancelled)
cancelled.pid=102
local before_cancel=#commands
listeners["hyprbars.drag_finish"](cancelled,false)
assert(#commands==before_cancel,"cancel dispatched to reused address")

local w = window("reserved", 400, 300)
active = w
binds["SUPER + LEFT"]()
near(w.at.y, 28 + 10 + 24, "top reserved area")
near(w.size.y, 1000 - 28 - 20 - 24, "available height")
tick() -- consume the resize and move dispatched by the snap script

-- A manual resize invalidates the saved pre-snap size.
w.size.x, w.size.y = 630, 390
tick()
w.at.x = w.at.x + 20
tick()
near(w.size.x, 630, "manual resize width retained on later move")
near(w.size.y, 390, "manual resize height retained on later move")
assert(not w.snapped_tag, "manual resize retained square snapped corner tag")

-- A held Alt/Super drag can pause for arbitrarily many ticks at an edge.
local held = window("held", 420, 320)
active = held
cursor = { x = 0, y = 500 }
tick()
held.at.x = 40
tick()
local before = #commands
for _ = 1, 30 do tick() end
assert(#commands == before, "paused held drag snapped without a release event")

-- A title-bar release cannot snap a different window after focus changes.
local original = window("original", 410, 310)
local other = window("other", 450, 350)
active = original
hypr_snap_drag_start(original.address)
active = other
before = #commands
hypr_snap_drag_end(original.address)
assert(#commands > before, "title-bar release lost its owning window")
for i = before + 1, #commands do
  assert(commands[i].params.window == "address:" .. original.address,
    "title-bar release dispatched to newly active window")
end

-- Session hydration restores normal size after config reload and keeps corner state.
local drag_origin = window("0xdragorigin", 600, 350)
active = drag_origin
drag_origin.at.x, drag_origin.at.y = 260, 300
hypr_snap_drag_start(drag_origin.address)
drag_origin.at.x, drag_origin.at.y = 1255, 55
cursor = {x=1595,y=75}
hypr_snap_drag_end(drag_origin.address)
hypr_snap_restore(drag_origin.address)
near(drag_origin.at.x,260,"corner release retained drag-start normal x")
near(drag_origin.at.y,300,"corner release retained drag-start normal y")
near(drag_origin.size.x,600,"corner release retained normal width")
near(drag_origin.size.y,350,"corner release retained normal height")

local reload_window = window("0xaabb", 455, 335)
active = reload_window
reload_window.at.x, reload_window.at.y = 123, 234
binds["SUPER + LEFT"]()
assert(reload_window.rounding == 0 and reload_window.snapped_tag, "snapped corners were not square")
dofile(script)
hypr_snap_restore(reload_window.address)
near(reload_window.size.x, 455, "reload retained normal width")
near(reload_window.size.y, 335, "reload retained normal height")
near(reload_window.at.x, 123, "reload/menu restore retained normal x")
near(reload_window.at.y, 234, "reload/menu restore retained normal y")
binds["SUPER + RIGHT"]()
binds["SUPER + DOWN"]()
near(reload_window.at.x, 123, "keyboard restore retained normal x")
near(reload_window.at.y, 234, "keyboard restore retained normal y")
assert(reload_window.rounding == 8 and not reload_window.snapped_tag, "restored corners did not become rounded")
binds["SUPER + UP"]()
assert(reload_window.rounding == 0, "maximized corners were not square")
hypr_snap_restore(reload_window.address)
assert(reload_window.rounding == 8, "restored maximized corners did not become rounded")
binds["SUPER + RIGHT"]()
reload_window.at.x, reload_window.at.y = 900, 250
hypr_snap_drag_start(reload_window.address)
near(reload_window.at.x, 900, "drag unsnap kept window under cursor x")
near(reload_window.at.y, 250, "drag unsnap kept window under cursor y")
near(reload_window.size.x, 455, "drag unsnap restored normal width")
cursor = { x = 500, y = 500 }
hypr_snap_drag_end(reload_window.address)
binds["SUPER + LEFT"]()
assert(normal_sizes[reload_window.address], "snapped window did not persist normal geometry")
if listeners["window.close"] then
  windows[reload_window.address] = nil
  listeners["window.close"](reload_window)
  assert(normal_sizes[reload_window.address] == nil, "closed window retained persisted size")
end

-- Random monitor sizes, scales, offsets, and all eleven rectangular zones. Every snapped
-- rectangle must fit the reserved, gap-adjusted monitor work area.
math.randomseed(10931)
local scales = { 1, 1.25, 1.5, 1.6, 2 }
local zones = { "left", "right", "top_left", "top_right", "bottom_left", "bottom_right",
  "third_left", "third_center", "third_right", "two_thirds_left", "two_thirds_right" }
for i = 1, 1000 do
  local scale = scales[math.random(#scales)]
  local logical_w = math.random(600, 3000)
  local logical_h = math.random(450, 1800)
  local top, bottom = math.random(0, 80), math.random(0, 40)
  local left, right = math.random(0, 40), math.random(0, 40)
  monitor = {
    x = math.random(-3000, 3000), y = math.random(-2000, 2000),
    width = logical_w * scale, height = logical_h * scale, scale = scale,
    reserved = (i % 2 == 0) and
      { top = top, bottom = bottom, left = left, right = right } or
      { top, bottom, left, right },
  }
  local min_x, min_y = monitor.x + left + 10, monitor.y + top + 10 + 24
  local max_x = monitor.x + logical_w - right - 10
  local max_y = monitor.y + logical_h - bottom - 10
  local results = {}
  for index, zone in ipairs(zones) do
    local id = i .. ":" .. zone
    active = window(id, 400, 300)
    local cx = zone:find("left") and monitor.x or monitor.x + logical_w - 1
    local cy = zone:find("top") and monitor.y or
      (zone:find("bottom") and monitor.y + logical_h - 1 or monitor.y + logical_h / 2)
    cursor = { x = cx, y = cy }
    if index <= 6 then
      hypr_snap_drag_start(active.address)
      hypr_snap_drag_end(active.address)
    else
      hypr_snap_zone(zone, active.address, false)
    end
    local x, y, width, height = active.at.x, active.at.y, active.size.x, active.size.y
    results[zone] = { x = x, y = y, width = width, height = height }
    assert(x >= min_x and y >= min_y and width > 0 and height > 0 and
      x + width <= max_x + 0.0001 and y + height <= max_y + 0.0001,
      "zone rectangle outside work area: " .. id)
  end
  local a, b, c = results.third_left, results.third_center, results.third_right
  near(a.x, min_x, "third left starts at work area")
  near(a.x + a.width + 10, b.x, "first third gutter")
  near(b.x + b.width + 10, c.x, "second third gutter")
  near(c.x + c.width, max_x, "third right ends at work area")
  assert(math.abs(a.width - b.width) <= 3.0001 and math.abs(b.width - c.width) <= 3.0001,
    "third rounding created unequal columns")
  local wide_left, wide_right = results.two_thirds_left, results.two_thirds_right
  near(wide_left.x, min_x, "two-thirds left starts at work area")
  near(wide_left.x + wide_left.width + 10, c.x, "two-thirds left complementary gutter")
  near(a.x + a.width + 10, wide_right.x, "two-thirds right complementary gutter")
  near(wide_right.x + wide_right.width, max_x, "two-thirds right ends at work area")
end
-- Live keyboard vertical maximize preserves the targeted width and restores geometry.
if hypr_vertical_maximize then
  monitor = { x = 0, y = 0, width = 1600, height = 1000,
    scale = 1, reserved = { top = 28, bottom = 0, left = 0, right = 0 } }
  local vertical_window = window("vertical", 420, 320)
  active = window("focus-after-menu", 500, 400)
  hypr_vertical_maximize(vertical_window.address)
  near(vertical_window.size.x, 420, "vertical maximize width")
  near(vertical_window.size.y, 1000 - 28 - 20 - 24, "vertical maximize height")
  hypr_vertical_restore(vertical_window.address)
  near(vertical_window.at.x, 300, "vertical restore x")
  near(vertical_window.at.y, 300, "vertical restore y")
  near(vertical_window.size.x, 420, "vertical restore width")
  near(vertical_window.size.y, 320, "vertical restore height")
  near(active.size.x, 500, "vertical command did not resize newly active window")
  active = vertical_window
  binds["SUPER + LEFT"]()
  local snapped_width, snapped_x = vertical_window.size.x, vertical_window.at.x
  hypr_vertical_maximize(vertical_window.address)
  near(vertical_window.size.x, snapped_width, "vertical maximize retained snapped width")
  near(vertical_window.at.x, snapped_x, "vertical maximize retained snapped x")
  hypr_vertical_restore(vertical_window.address)
  near(vertical_window.size.x, snapped_width, "vertical restore retained saved snapped width")
end
-- Titlebar Shake emits once per gesture and carries its owning address.
local function exec_count(fragment)
  local count = 0
  for _, cmd in ipairs(exec_commands) do
    if cmd:find(fragment, 1, true) then count = count + 1 end
  end
  return count
end
monitor = { x = 0, y = 0, width = 1600, height = 1000,
  scale = 1, reserved = { top = 28, bottom = 0, left = 0, right = 0 } }
cursor = { x = 500, y = 500 }
local shaking = window("0xface", 420, 320)
active = shaking
tick()
hypr_snap_drag_start(shaking.address)
local shakes_before = exec_count("hypr-windowctl minimize-others")
for _, dx in ipairs({50, -50, 50, -50, 50, -50, 50, -50}) do
  shaking.at.x = shaking.at.x + dx
  tick()
end
assert(exec_count("hypr-windowctl minimize-others") == shakes_before + 1, "Shake did not emit exactly once")
assert(exec_count("hypr-windowctl minimize-others " .. shaking.address) == 1, "Shake lost its owning address")
hypr_snap_drag_end(shaking.address)
for _ = 1, 8 do
  shaking.at.x = shaking.at.x + 50
  tick()
end
assert(exec_count("hypr-windowctl minimize-others") == shakes_before + 1, "Shake survived titlebar release")

-- Snap Bar opens once, hides below its threshold, and releases on the owner.
local bar_window = window("0xcafe", 430, 330)
active = bar_window
cursor = { x = 800, y = 20 }
tick()
hypr_snap_drag_start(bar_window.address)
local bar_before = exec_count("hypr-window-menu snapbar " .. bar_window.address)
local geometry_before = #commands
for _ = 1, 4 do tick() end
assert(exec_count("hypr-window-menu snapbar " .. bar_window.address) == bar_before + 1, "Snap Bar reopened during held drag")
assert(#commands == geometry_before, "Snap Bar preview applied geometry before release")
cursor = { x = 800, y = 500 }
local hides_before = exec_count("hypr-window-menu hide")
tick()
assert(exec_count("hypr-window-menu hide") == hides_before + 1, "Snap Bar did not hide after leaving activation area")
cursor = { x = 800, y = 20 }
tick()
active = window("0xbeef", 440, 340)
hypr_snap_drag_end(bar_window.address)
assert(exec_count("hypr-window-menu snapbar-release " .. bar_window.address) == 1, "Snap Bar release lost its owner")
assert(#commands == geometry_before, "Snap Bar release applied an unintended edge snap")
hypr_snap_zone("top_right",bar_window.address,false)
hypr_snap_restore(bar_window.address)
near(bar_window.at.x,300,"asynchronous Snap Bar preserved normal x")
near(bar_window.at.y,300,"asynchronous Snap Bar preserved normal y")

active = bar_window
cursor = {x=800,y=20}
hypr_snap_drag_start(bar_window.address)
tick()
bar_window.at.x,bar_window.at.y = 700,80
hypr_snap_drag_end(bar_window.address)
hypr_snap_discard_release(bar_window.address)
hypr_snap_zone("left",bar_window.address,false)
hypr_snap_restore(bar_window.address)
near(bar_window.at.x,700,"canceled Snap Bar did not reuse previous drag origin")
near(bar_window.at.y,80,"canceled Snap Bar did not reuse previous drag origin y")

-- Display transfer preserves preset zones, custom ratios, and restore geometry.
monitor = {id=0,x=0,y=0,width=1600,height=1000,scale=1,reserved={top=28}}
transfer_monitor = {id=1,x=1600,y=0,width=1920,height=1080,scale=1.5,reserved={top=26}}
local transferring = window("0xfeed",600,350)
active=transferring
hypr_snap_zone("left",transferring.address,false)
hypr_monitor_transfer("+1",transferring.address)
near(transferring.at.x,1610,"monitor transfer left x")
near(transferring.size.x,625,"monitor transfer half width")
assert(transferring.snapped_tag,"monitor transfer removed snapped tag")
tick();tick()
assert(transferring.snapped_tag,"monitor watcher dissolved transferred snap")
hypr_snap_restore(transferring.address)
near(transferring.size.x,600,"monitor normal restore width")
near(transferring.size.y,350,"monitor normal restore height")
assert(transferring.at.x>=1610 and transferring.at.x+600<=2870,"restore left destination display")
transfer_monitor=monitor
hypr_monitor_transfer("-1",transferring.address)
hypr_snap_zone("left",transferring.address,false)
dofile(script) -- session hydration must retain the zone for a later transfer.
transfer_monitor={id=1,x=-1280,y=100,width=1920,height=1080,scale=1.5,reserved={top=26}}
hypr_monitor_transfer("+1",transferring.address)
near(transferring.at.x,-1270,"reloaded transfer offset")
near(transferring.size.x,625,"reloaded transfer retained preset")
transfer_monitor=nil
local unchanged_x, unchanged_width=transferring.at.x,transferring.size.x
hypr_monitor_transfer("+1",transferring.address)
near(transferring.at.x,unchanged_x,"one display transfer x")
near(transferring.size.x,unchanged_width,"one display transfer width")
-- Inactive snaps reconcile display offset/size/scale/removal without focus theft.
monitor={id=0,x=0,y=0,width=1600,height=1000,scale=1,reserved={top=28}}
local custom_left,custom_right=window("0xcust1",400,300),window("0xcust2",400,300)
hypr_snap_zone("left",custom_left.address,false)
hypr_snap_zone("right",custom_right.address,false)
hypr_snap_set_geometry(custom_left.address,10,62,900,928)
hypr_snap_set_geometry(custom_right.address,920,62,670,928)
local custom_destination={id=1,x=-3840,y=100,width=3840,height=2160,scale=1,reserved={top=40}}
custom_left.monitor,custom_right.monitor=custom_destination,custom_destination
tick()
assert(math.abs(custom_right.at.x-custom_left.at.x-custom_left.size.x-10)<=1,"scaled custom separator gutter changed")
assert(custom_left.size.x>custom_right.size.x,"custom pane ratio was replaced by equal halves")
hypr_snap_restore(custom_left.address);hypr_snap_restore(custom_right.address)
for trial=1,2000 do
  monitor={id=0,x=math.random(-4000,4000),y=math.random(-1000,1000),
    width=math.random(1200,3840),height=math.random(900,2160),scale=1,reserved={top=28}}
  local reflow=window("0xreflow"..trial,400,300)
  active=reflow
  local zones={"left","right","top_left","top_right","bottom_left","bottom_right","third_left","third_center","third_right","two_thirds_left","two_thirds_right"}
  hypr_snap_zone(zones[math.random(#zones)],reflow.address,false)
  local other=window("0xother"..trial,400,300)
  active=other
  local scale=({1,1.25,1.5,2})[math.random(4)]
  local destination={id=1,x=math.random(-4000,4000),y=math.random(-1000,1000),
    width=math.random(1400,3840),height=math.random(1100,2160),scale=scale,reserved={top=math.random(0,40)}}
  reflow.monitor=destination
  tick()
  assert(reflow.snapped_tag,"inactive reflow lost snap state")
  assert(active==other,"inactive reflow stole focus")
  assert(reflow.at.x>=destination.x+10 and reflow.at.y>=destination.y+destination.reserved.top+34,"reflow before usable origin")
  assert(reflow.at.x+reflow.size.x<=destination.x+destination.width/scale-9 and reflow.at.y+reflow.size.y<=destination.y+destination.height/scale-9,"reflow beyond display")
  hypr_snap_restore(reflow.address)
  near(reflow.size.x,400,"reflow normal width")
  near(reflow.size.y,300,"reflow normal height")
  assert(reflow.at.x>=destination.x+10 and reflow.at.x+400<=destination.x+destination.width/scale-9,"restored reflow beyond display")
  windows[reflow.address],windows[other.address]=nil,nil
end
print("snap regression, monitor transfer/reflow, and 13,000 randomized geometry checks passed (" .. script .. ")")

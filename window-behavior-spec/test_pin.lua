-- Run with: lua test_pin.lua
local root = debug.getinfo(1, "S").source:sub(2):match("^(.*)/[^/]+$") or "."
local script = arg[1] or os.getenv("HOME") .. "/.config/hypr/pin.lua"
local timers, overrides, windows = {}, {}, {}
local active
local focus_callback
local raise_count = 0

local function target_window(target)
  local address = target:match("^address:(.+)$")
  assert(address and windows[address], "unknown window " .. tostring(target))
  return windows[address], address
end

hl = {
  dsp = { window = {} },
  get_active_window = function() return active end,
  get_window = function(selector) return windows[selector:match("^address:(.+)$")] end,
  get_windows = function() return windows end,
  on = function(event, callback)
    assert(event == "window.active")
    focus_callback = callback
  end,
  exec_cmd = function() end,
  timer = function(callback)
    local timer = { enabled = true, callback = callback }
    function timer:set_enabled(value) self.enabled = value end
    timers[#timers + 1] = timer
    return timer
  end,
  dispatch = function(action)
    local w, address = target_window(action.window)
    if action.kind == "set_prop" then
      assert(action.prop == "opacity")
      local value = tonumber(action.value)
      assert(value and value >= 0 and value <= 1)
      overrides[address] = value
    elseif action.kind == "float" then
      w.floating = true
    elseif action.kind == "pin" then
      w.pinned = not w.pinned
    elseif action.kind == "alter_zorder" then
      assert(action.mode == "top")
      raise_count = raise_count + 1
    else
      error("unexpected action " .. tostring(action.kind))
    end
  end,
}

local function dispatcher(kind)
  return function(args)
    args.kind = kind
    return args
  end
end
for _, kind in ipairs({ "set_prop", "float", "pin", "alter_zorder" }) do
  hl.dsp.window[kind] = dispatcher(kind)
end
o = { bind = function(key, _, callback)
  assert(key == "SUPER + P" or key == "SUPER + CTRL + T")
  assert(callback == hypr_pin_toggle)
end }

local function add_window(address)
  windows[address] = { address = address, floating = false, pinned = false }
  return windows[address]
end

local function tick(count)
  for _ = 1, count do
    local snapshot = { table.unpack(timers) }
    for _, timer in ipairs(snapshot) do
      if timer.enabled then timer.callback() end
    end
  end
end

local function assert_clear(address)
  assert(overrides[address] == 1, address .. " did not return to full opacity")
  assert(hypr_pin_fades[address] == nil, address .. " kept a fade state")
end

local a, b = add_window("0xa"), add_window("0xb")
dofile(script)

active = a
hypr_pin_toggle()
assert(a.floating and a.pinned and overrides[a.address] == 0.72)
tick(3)
active = b
hypr_pin_toggle()
assert(a.pinned and b.pinned)
assert(overrides[a.address] and overrides[b.address], "one fade stopped the other")
local before_focus = raise_count
focus_callback()
assert(raise_count == before_focus + 2, "focus change did not keep pinned windows above others")
tick(20)
assert_clear(a.address)
assert_clear(b.address)

-- Rapid toggles on one window replace only that window's timer.
active = a
hypr_pin_toggle()
tick(2)
hypr_pin_toggle()
assert(a.pinned and overrides[a.address] == 0.72)
tick(20)
assert_clear(a.address)

-- Reloading the config midway through an effect releases old overrides.
active = b
hypr_pin_toggle()
tick(2)
dofile(script)
assert_clear(b.address)
tick(20)
assert_clear(b.address)

-- Randomized interleavings of window switches, toggles, ticks, and reloads.
math.randomseed(20260930)
for _ = 1, 100 do
  for _ = 1, 40 do
    active = math.random(2) == 1 and a or b
    local operation = math.random(5)
    if operation <= 3 then hypr_pin_toggle()
    elseif operation == 4 then tick(math.random(0, 4))
    else dofile(script) end
  end
  tick(20)
  assert_clear(a.address)
  assert_clear(b.address)
end

-- Reduced motion cancels an in-flight custom fade and prevents new fade timers.
if hypr_motion_changed then
  active = a
  hypr_motion_changed(false)
  hypr_pin_toggle()
  tick(2)
  assert(hypr_pin_fades[a.address], "normal motion did not start a fade")
  hypr_motion_changed(true)
  assert_clear(a.address)
  assert_clear(b.address)
  local timers_before = #timers
  hypr_pin_toggle(a.address)
  assert(#timers == timers_before, "reduced motion created a fade timer")
  assert_clear(a.address)
  hypr_motion_changed(false)
end

active = nil
hypr_pin_toggle()
print("pin fade and 4,000 randomized operation tests passed (" .. script .. ")")

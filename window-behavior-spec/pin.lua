-- Always-on-top pin for SUPER+P and the hyprbars button.
-- Keep the short opacity effect separate for each window.

local STEP_MS = 16
local LIFT_MS = 220
local LIFT_FROM = 0.72
local DROP_FROM = 0.88

local function set_opacity(address, value)
  hl.dispatch(hl.dsp.window.set_prop({
    prop = "opacity",
    value = value,
    window = "address:" .. address,
  }))
end

-- A config reload can happen during a fade. Stop the old timers and release
-- their overrides before replacing the state table.
if hypr_pin_fades then
  for address, state in pairs(hypr_pin_fades) do
    if state.timer then state.timer:set_enabled(false) end
    set_opacity(address, "1.000")
  end
end
local fades = {}
hypr_pin_fades = fades

local function finish_fade(address)
  local state = fades[address]
  if not state then return end
  fades[address] = nil
  if state.timer then state.timer:set_enabled(false) end
  set_opacity(address, "1.000")
end

local function fade_in(address, from)
  -- Restart only this window's effect. Other windows keep their own timers.
  finish_fade(address)
  local state = { elapsed = 0 }
  fades[address] = state
  set_opacity(address, string.format("%.3f", from))
  state.timer = hl.timer(function()
    if fades[address] ~= state then return end
    state.elapsed = state.elapsed + STEP_MS
    local t = math.min(state.elapsed / LIFT_MS, 1)
    if t >= 1 then
      finish_fade(address)
    else
      local eased = 1 - (1 - t) ^ 3
      set_opacity(address, string.format("%.3f", from + (1 - from) * eased))
    end
  end, { timeout = STEP_MS, type = "repeat" })
end

function hypr_pin_toggle(address)
  local w = address and hl.get_window("address:" .. address) or hl.get_active_window()
  if not w then return end
  local target = "address:" .. w.address
  local pinning = not w.pinned

  if not w.floating then
    hl.dispatch(hl.dsp.window.float({ action = "set", window = target }))
  end
  hl.dispatch(hl.dsp.window.pin({ window = target }))

  if pinning then
    hl.dispatch(hl.dsp.window.alter_zorder({ mode = "top", window = target }))
    fade_in(w.address, LIFT_FROM)
    hl.exec_cmd([[omarchy-osd -m "📌  Pinned — always on top" -d 1200]])
  else
    fade_in(w.address, DROP_FROM)
    hl.exec_cmd([[omarchy-osd -m "Unpinned" -d 1000]])
  end
end

-- Hyprland's pin keeps a floating window on every workspace; it does not
-- guarantee that a later-focused floating window stays below it. Raise pinned
-- windows again after focus changes to provide actual always-on-top behavior.
hl.on("window.active", function()
  for _, w in pairs(hl.get_windows()) do
    if w.pinned and w.floating then
      hl.dispatch(hl.dsp.window.alter_zorder({ mode = "top", window = "address:" .. w.address }))
    end
  end
end)

o.bind("SUPER + P", "Pin window (always on top)", hypr_pin_toggle)
o.bind("SUPER + CTRL + T", "Pin window (PowerToys shortcut)", hypr_pin_toggle)

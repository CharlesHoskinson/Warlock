-- Candidate PRIVATE configuration only. Load after the V25 module is actually
-- registered. The keyboard event captures its public Lua owner synchronously.
local function toggle_current_pin()
  local owner = hl.get_active_window()
  if not owner then return false, "No captured native owner" end
  return hl.plugin.hyprbars.pin_window(owner)
end
hl.unbind("SUPER + P")
hl.unbind("SUPER + CTRL + T")
o.bind("SUPER + P", "Toggle pin (always on top)", toggle_current_pin)
o.bind("SUPER + CTRL + T", "Toggle pin (always on top)", toggle_current_pin)
-- Titlebar callers use the decoration's retained strong owner through this
-- reserved command. Never replace it with an asynchronous address lookup.
-- action = "hyprbars:pin-toggle"
function hypr_motion_changed(reduced)
  if type(reduced) ~= "boolean" then return false end
  return hl.plugin.hyprbars.pin_feedback_enabled(not reduced)
end
hypr_motion_changed(hypr_reduced_motion == true)

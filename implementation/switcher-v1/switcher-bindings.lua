-- Staged replacement for only the final Alt+Tab bindings in snap.lua.
-- Lua callbacks run in compositor event order; Python launches may reorder.
-- Global serial survives config reload and is advanced to invalidate old work.
hypr_switcher_serial = (hypr_switcher_serial or 0) + 1
local chord = nil
local session = os.getenv("HYPRLAND_INSTANCE_SIGNATURE") or ""
local helper = os.getenv("HOME") .. "/.local/bin/hypr-window-menu"
if session:match("^[A-Za-z0-9_.-]+$") then
  hl.exec_cmd(string.format("%s switcher-barrier %s %d", helper, session, hypr_switcher_serial))
end
local function step(direction)
  if not session:match("^[A-Za-z0-9_.-]+$") then return end
  if not chord then
    hypr_switcher_serial = hypr_switcher_serial + 1
    if hypr_switcher_serial > 2147483647 then return end
    chord = {generation=hypr_switcher_serial,ordinal=0}
  end
  chord.ordinal = chord.ordinal + 1
  if chord.ordinal > 4096 then return end
  hl.exec_cmd(string.format("%s switcher-step %s %d %d %d", helper, session, chord.generation, chord.ordinal, direction))
end
local function release()
  if not chord then return end
  local old=chord;chord=nil
  hl.exec_cmd(string.format("%s switcher-release %s %d %d", helper, session, old.generation, old.ordinal))
end
hl.unbind("ALT + TAB")
hl.unbind("ALT + SHIFT + TAB")
hl.unbind("ALT + ALT_L")
hl.unbind("ALT + ALT_R")
o.bind("ALT + TAB", "Switch windows", function()step(1)end)
o.bind("ALT + SHIFT + TAB", "Switch windows backwards", function()step(-1)end)
o.bind("ALT + ALT_L", "Select switched window", release, {release=true,non_consuming=true})
o.bind("ALT + ALT_R", "Select switched window", release, {release=true,non_consuming=true})

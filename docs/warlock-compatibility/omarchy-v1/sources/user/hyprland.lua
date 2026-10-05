-- Learn how to configure Hyprland: https://wiki.hypr.land/Configuring/Start/

-- Omarchy's bootstrap keeps path setup out of this user config.
dofile((os.getenv("OMARCHY_PATH") or "/usr/share/omarchy") .. "/default/hypr/bootstrap.lua")

-- Disable all Omarchy default bindings. Add your own in hypr/bindings.lua.
-- omarchy_default_bindings = false
--
-- Or disable only bindings for Omarchy's preinstalled apps/web apps while
-- keeping core window-manager bindings:
-- omarchy_preinstalled_bindings = false

-- Load Omarchy defaults.
require("default.hypr.omarchy")

-- Put your personal overrides in these files. They're loaded after Omarchy's
-- defaults so package updates can improve the defaults without rewriting your
-- ~/.config/hypr files.
require("hypr.monitors")
require("hypr.input")
require("hypr.bindings")
require("hypr.looknfeel")
require("hypr.autostart")

-- Toggle config flags dynamically.
require("default.hypr.toggles")

-- Add any other personal Hyprland configuration below.
-- o.window("qemu", { workspace = "5" })

-- Free-floating desktop: every window opens floating and can overlap others.
-- SUPER+T still toggles a window back to tiling.
o.window(".*", { float = true })
-- Omarchy tiles Chromium-based browsers (Brave included); a tiled window always sits
-- below floating ones, so it could never be clicked to the front. Float them too.
o.window({ tag = "chromium-based-browser" }, { float = true })

-- Keep disabled owners in pointer hit testing. The native bridge redirects
-- their focus and consumes clicks; packaged-plugin fallback retains core blocking.
local modal_focus_bridge = hl.plugin.hyprbars and hl.plugin.hyprbars.modal_focus_bridge
  and hl.plugin.hyprbars.modal_focus_bridge()
hl.config({ general = { modal_parent_blocking = not modal_focus_bridge } })

-- Click-to-focus: pointer input follows the hovered window without stealing
-- keyboard focus. Clicking focuses and raises that window.
hl.config({
  input = {
    follow_mouse = 2,
    float_switch_override_focus = 0,
  },
})

-- Windows-style snapping: drag to edges/corners, or SUPER + arrows.
require("hypr.snap")

-- Always-on-top pin with a smooth lift-in (SUPER+P and the hyprbars 📌 button).
require("hypr.pin")

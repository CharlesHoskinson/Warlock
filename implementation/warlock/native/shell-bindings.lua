-- Source only; activate with the matching Warlock authority in a candidate
-- session. These match the frozen Omarchy routes, flags and modifier masks.
-- Load user overrides after defaults. Other Omarchy routes remain unchanged.
hl.bind("SUPER + ALT + SPACE", function() hl.plugin.warlock.apps_menu() end,
        {description="Apps menu"})
hl.bind("SUPER + ESCAPE", function() hl.plugin.warlock.system_menu() end,
        {description="System menu"})
hl.bind("SUPER + SHIFT + ALT + comma", function() hl.plugin.warlock.notification_history() end,
        {description="Open notification history"})

-- Native controller owns move/resize throughout the pointer gesture.
-- Omarchy defaults; adopted user Alt additions remain available as well.
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), {mouse=true, description="Move window"})
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), {mouse=true, description="Resize window"})
hl.bind("ALT + mouse:272", hl.dsp.window.drag(), {mouse=true, description="Move window (Alt+drag)"})
hl.bind("ALT + mouse:273", hl.dsp.window.resize(), {mouse=true, description="Resize window (Alt+drag)"})

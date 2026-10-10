hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
-- Source only. Load with the matching native Warlock plugin in an explicitly
-- activated candidate session. Keep user overrides after these default bindings.
hl.bind("ALT + TAB", function() hl.plugin.warlock.switcher_forward() end,
        {description="Switch windows"})
hl.bind("ALT + SHIFT + TAB", function() hl.plugin.warlock.switcher_reverse() end,
        {description="Switch windows backwards"})
-- Source only: activate with the matching Warlock native authority.
-- The authority installs the three approved shell chords only when their live
-- bindings are free. Explicit persisted decisions are edited in Settings.
-- It never removes or disables existing/user bindings. Other Omarchy routes
-- and overrides keep their meaning; no Lua callbacks overwrite these chords.

-- Native controller owns move/resize throughout the pointer gesture.
-- Omarchy defaults; adopted user Alt additions remain available as well.
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), {mouse=true, description="Move window"})
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), {mouse=true, description="Resize window"})
hl.bind("ALT + mouse:272", hl.dsp.window.drag(), {mouse=true, description="Move window (Alt+drag)"})
hl.bind("ALT + mouse:273", hl.dsp.window.resize(), {mouse=true, description="Resize window (Alt+drag)"})

hl.bind("SUPER + ALT + SPACE", hl.dsp.focus({window="title:ELM-ACTIVATION-PEER"}), {description="Existing Apps shortcut"})
hl.bind("F12", function() hl.plugin.warlock.apps_menu() end, {description="User Apps shortcut"})

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })

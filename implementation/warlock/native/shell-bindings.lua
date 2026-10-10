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

hl.config({xwayland={enabled=false},animations={enabled=false},decoration={dim_modal=false},input={follow_mouse=2,float_switch_override_focus=0}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
hl.on("window.open",function(w) hl.dispatch(hl.dsp.window.float({action="enable",window="address:"..w.address})) end)

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })

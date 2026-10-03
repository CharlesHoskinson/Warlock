-- X11-only QA: select explicitly, never for ordinary Wayland cases.
hl.config({ xwayland = { enabled = true } })
hl.monitor({output="HEADLESS-1",mode="1600x1000@60",position="0x0",scale=1})
hl.monitor({output="WAYLAND-1",mode="1600x1000@60",position="0x0",scale=1})
hl.config({animations={enabled=false},input={follow_mouse=2},general={modal_parent_blocking=true},debug={disable_logs=false}})
hl.on("window.open",function(w)
  if not w.floating then hl.dispatch(hl.dsp.window.float({action="set",window="address:"..w.address})) end
end)
if hl.plugin.hyprbars and hl.plugin.hyprbars.modal_focus_bridge() then
  hl.config({general={modal_parent_blocking=false},plugin={hyprbars={bar_height=24}}})
end
o={bind=function()end}
dofile('/home/hoskinson/.config/hypr/pin.lua')
-- No notification is needed in this isolated QA compositor.
hl.exec_cmd=function()end

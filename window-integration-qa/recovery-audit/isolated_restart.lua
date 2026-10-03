-- Dedicated recovery QA compositor. No user autostart, shell or live plugins.
hl.config({ xwayland = { enabled = false } })
hl.monitor({output="WAYLAND-1",mode="1280x800@60",position="0x0",scale=1})
hl.config({animations={enabled=false},input={follow_mouse=0},debug={disable_logs=false}})
hl.on("window.open",function(w)
  if not w.floating then hl.dispatch(hl.dsp.window.float({action="set",window="address:"..w.address})) end
end)
-- Explicit fixture calls exercise the installed group helper in isolated state.
-- Automatic shell hooks remain captured here so they cannot launch UI helpers.
qa_commands={}
hl.exec_cmd=function(command) table.insert(qa_commands,command) end
o={bind=function()end}
dofile('/home/hoskinson/.config/hypr/snap.lua')

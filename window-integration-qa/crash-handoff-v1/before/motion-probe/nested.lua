hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
hl.config({animations={enabled=true},debug={disable_logs=false}})
hl.on("window.open",function(w)
  if not w.floating then hl.dispatch(hl.dsp.window.float({action="set",window="address:"..w.address})) end
end)

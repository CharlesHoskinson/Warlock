hl.monitor({output="WAYLAND-1",mode="1000x760@60",position="0x0",scale=1})
hl.config({animations={enabled=false},input={follow_mouse=2},debug={disable_logs=false},general={border_size=2},decoration={rounding=8,blur={enabled=false},shadow={enabled=false}}})
hl.on("window.open",function(w)
  if not w.floating then hl.dispatch(hl.dsp.window.float({action="set",window="address:"..w.address})) end
end)
-- No main-shell bindings, shared state, startup helpers or persistent user config.

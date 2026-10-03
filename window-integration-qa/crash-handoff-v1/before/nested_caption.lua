hl.monitor({output="DRAG-QA",mode="1600x1000@60",position="0x0",scale=1})
hl.monitor({output="WAYLAND-1",mode="1280x720@60",position="1600x0",scale=1})
hl.config({animations={enabled=false},input={follow_mouse=2,resolve_binds_by_sym=true},debug={disable_logs=false},general={border_size=2}})
hl.bind("SUPER + mouse:272",hl.dsp.window.drag(),{mouse=true})
hl.bind("ALT + mouse:272",hl.dsp.window.drag(),{mouse=true})
hl.bind("SUPER + mouse:273",hl.dsp.window.resize(),{mouse=true})
hl.on("window.open",function(w) if not w.floating then hl.dispatch(hl.dsp.window.float({action="toggle",window="address:"..w.address})) end end)
local modal_bridge=hl.plugin.hyprbars and hl.plugin.hyprbars.modal_focus_bridge and hl.plugin.hyprbars.modal_focus_bridge()
hl.config({general={modal_parent_blocking=not modal_bridge}})
qa_drag_events={}
if hl.plugin.hyprbars and hl.plugin.hyprbars.drag_bridge and hl.plugin.hyprbars.drag_bridge() then
  hl.config({plugin={hyprbars={bar_height=24}}})
  hl.on("hyprbars.drag_start",function(w)
    table.insert(qa_drag_events,{kind="begin",address=w.address,x=w.at.x,y=w.at.y,width=w.size.x,height=w.size.y})
  end)
  hl.on("hyprbars.drag_finish",function(w,released)
    table.insert(qa_drag_events,{kind=released and "release" or "cancel",address=w.address})
  end)
end
-- Isolated geometry integration: record shell effects without touching the
-- user's shared Snap Group/taskbar state.
qa_shell_commands={}
hl.exec_cmd=function(command) table.insert(qa_shell_commands,command) end
o={bind=function() end}
dofile('/home/hoskinson/window-integration-qa/snap_caption_candidate.lua')
dofile('/home/hoskinson/.config/hypr/pin.lua')

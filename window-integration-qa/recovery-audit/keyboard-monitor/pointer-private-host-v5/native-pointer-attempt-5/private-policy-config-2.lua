hl.monitor({output="WAYLAND-1",mode="1280x800@60",position="0x0",scale=1.25})
hl.config({animations={enabled=false},input={follow_mouse=0,repeat_delay=1000,virtualkeyboard={release_pressed_on_close=false}},ecosystem={enforce_permissions=true},misc={name_vk_after_proc=true},debug={disable_logs=false,enable_stdout_logs=true}})
hl.on("window.open",function(w) if not w.floating then hl.dispatch(hl.dsp.window.float({action="set",window="address:"..w.address})) end end)
hl.permission({binary="/home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/pointer-private-host-v5/native-pointer-attempt-5/native/libkeyboard-monitor-private-v8-host.so",type="plugin",mode="allow"})
hl.permission({binary="/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard",type="keyboard",mode="allow"})
hl.permission({binary="hl-virtual-keyboard-native-input",type="keyboard",mode="deny"})
hl.permission({binary="/home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/pointer-private-host-v5/native-pointer-attempt-5/native-fixture/native-input",type="keyboard",mode="allow"})
hl.bind("F12",function() local f=io.open(os.getenv("XDG_RUNTIME_DIR").."/shortcut-count","a");f:write("shortcut\n");f:close() end)

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })
hl.config({ecosystem={enforce_permissions=true}})
hl.device({name="hl-virtual-keyboard-native-input",enabled=true})

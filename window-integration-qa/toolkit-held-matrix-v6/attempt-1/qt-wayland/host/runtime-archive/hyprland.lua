-- Fresh private Qt compatibility fixture only. No include, startup or main callbacks.
hl.monitor({output="WAYLAND-1",mode="1600x1000@60",position="0x0",scale=1,transform=0})
hl.config({
  xwayland={enabled=false},
  animations={enabled=false},
  debug={disable_logs=false,enable_stdout_logs=true},
  misc={disable_hyprland_logo=true,disable_splash_rendering=true,disable_watchdog_warning=true},
})
-- The reviewed orchestrator loads the exact frozen production v18 plugin only
-- after private readiness, and unloads it only after all owned clients exit.

hl.permission({binary="/home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/production-native-proof-v4/native-fixture/native-input",type="keyboard",mode="allow"})

local heldConfig=os.getenv("WINDOW_QA_HELPER_CONFIG")
if heldConfig and heldConfig==os.getenv("XDG_RUNTIME_DIR").."/taskbar-home/helper-config.json" then
hl.config({plugin={hyprbars={enabled=true,bar_height=24,bar_part_of_window=true}}})
dofile("/usr/share/omarchy/default/hypr/helpers.lua")
dofile("/home/hoskinson/window-integration-qa/toolkit-interruption-v6/native-candidate/installed-snap.lua")
o.bind("SUPER + mouse:273","Resize window",hl.dsp.window.resize(),{mouse=true})
end

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })

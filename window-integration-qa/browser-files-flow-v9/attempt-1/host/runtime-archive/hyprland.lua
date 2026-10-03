-- Fresh private Qt compatibility fixture only. No include, startup or main callbacks.
hl.monitor({output="WAYLAND-1",mode="1600x1000@60",position="0x0",scale=1,transform=0})
hl.config({
  xwayland={enabled=false},
  animations={enabled=false},
  debug={disable_logs=false,enable_stdout_logs=true},
  misc={disable_hyprland_logo=true,disable_splash_rendering=true,disable_watchdog_warning=true},
})
-- The reviewed orchestrator loads the exact frozen candidate v21 plugin only
-- after private readiness, and unloads it only after all owned clients exit.

-- Private input-only flow: pointer movement must not itself focus the target.
hl.config({input={follow_mouse=0},ecosystem={enforce_permissions=false}})

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })

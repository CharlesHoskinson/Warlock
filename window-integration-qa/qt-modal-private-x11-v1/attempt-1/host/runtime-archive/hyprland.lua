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

-- Explicit isolated X11 compatibility campaign only.
hl.config({ xwayland={enabled=true,create_abstract_socket=false} })

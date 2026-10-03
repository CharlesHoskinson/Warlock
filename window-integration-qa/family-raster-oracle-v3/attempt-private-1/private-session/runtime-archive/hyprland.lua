hl.config({ xwayland = { enabled = false } })
hl.monitor({output="WAYLAND-1",mode="320x240@60",position="0x0",scale=1,transform=0})
hl.monitor({output="ORACLE-SECOND",mode="480x360@60",position="320x0",scale=1.5,transform=0})
hl.config({
  animations={enabled=false},
  general={border_size=0},
  decoration={rounding=0,blur={enabled=false},shadow={enabled=false}},
  misc={disable_watchdog_warning=true,disable_hyprland_logo=true,
        disable_splash_rendering=true,background_color=0xff000000},
  debug={disable_logs=false},
})
-- Only private monitors/background settings; no plugins, includes, bindings,
-- startup, native-window actions, or access to shared desktop catalogs.

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })

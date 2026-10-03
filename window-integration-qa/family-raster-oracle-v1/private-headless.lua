hl.monitor({output="HEADLESS-1",mode="320x240@60",position="0x0",scale=1,transform=0})
hl.config({
  animations={enabled=false},
  general={border_size=0},
  decoration={rounding=0,blur={enabled=false},shadow={enabled=false}},
  misc={disable_watchdog_warning=true,disable_hyprland_logo=true,
        disable_splash_rendering=true,background_color=0xff000000},
  debug={disable_logs=false},
})
-- Private headless backend only. No include, binding, startup, window callback,
-- plugin load, desktop helper or shared catalog access.

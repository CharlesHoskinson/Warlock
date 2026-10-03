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
-- Fresh private fixture configuration only. No external/async pin command.
if hl.plugin.hyprbars ~= nil then
  hl.config({plugin={hyprbars={enabled=true,bar_height=24,bar_part_of_window=true,
    bar_padding=10,bar_button_padding=8,bar_precedence_over_border=true,
    on_right_click="",on_maximize_hover="",on_drag_start="",on_drag_end=""}}})
  hl.plugin.hyprbars.add_button({bg_color="rgb(89b4fa)",fg_color="rgb(1e1e2e)",
    size=14,icon="P",action="hyprbars:pin-toggle"})
  -- Match the installed o.bind function's function-dispatch path in this
  -- isolated minimal config; no packaged startup/service is sourced.
  o={bind=function(keys,description,dispatcher,options)
    local opts=options or {};opts.description=description;hl.bind(keys,dispatcher,opts)
  end}
  dofile("/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend/pin_bindings.lua")
end

hl.permission({binary="/home/hoskinson/window-behavior-spec/pin-lifetime-v3/keyboard-chords/physical-keyboard",type="keyboard",mode="allow"})

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })

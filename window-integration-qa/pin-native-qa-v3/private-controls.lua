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

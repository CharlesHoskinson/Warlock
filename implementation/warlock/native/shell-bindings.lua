-- Source only; activate with the matching Warlock authority in a candidate
-- session. These match the frozen Omarchy routes, flags and modifier masks.
-- Load user overrides after defaults. Other Omarchy routes remain unchanged.
hl.bind("SUPER + ALT + SPACE", function() hl.plugin.warlock.apps_menu() end,
        {description="Apps menu"})
hl.bind("SUPER + ESCAPE", function() hl.plugin.warlock.system_menu() end,
        {description="System menu"})
hl.bind("SUPER + SHIFT + ALT + comma", function() hl.plugin.warlock.notification_history() end,
        {description="Open notification history"})

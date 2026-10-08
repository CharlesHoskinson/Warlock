-- Source only. Load with the matching native Warlock plugin in an explicitly
-- activated candidate session. Keep user overrides after these default bindings.
hl.bind("ALT + TAB", function() hl.plugin.warlock.switcher_forward() end,
        {description="Switch windows"})
hl.bind("ALT + SHIFT + TAB", function() hl.plugin.warlock.switcher_reverse() end,
        {description="Switch windows backwards"})

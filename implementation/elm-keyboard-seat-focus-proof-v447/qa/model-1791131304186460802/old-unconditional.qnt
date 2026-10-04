module focus {
 var s: { count: int, focus: int, desktop: int, keys: int, violations: int }
 action init = s' = { count: 0, focus: 2, desktop: 1, keys: 0, violations: 0 }
 val fallback = s.count == 0 and s.desktop != 0
 val result = if (fallback) s.desktop else s.focus
 action attach = s' = { ...s, count: s.count + 1, focus: result, violations: s.violations + (if (s.focus != 0 and result != s.focus) 1 else 0) }
 action remove = s' = { ...s, count: 0, keys: 0 }
 action expire = s' = { ...s, focus: 0 }
 action emptyDesktop = s' = { ...s, desktop: 0 }
 action ordinary = s' = { ...s, focus: 1 }
 action popup = s' = { ...s, focus: 2 }
 action press = s' = { ...s, keys: if (s.count > 0) 1 else 0 }
 action step = any { attach, remove, expire, emptyDesktop, ordinary, popup, press }
 val safety = s.violations == 0 and s.count >= 0 and (s.count > 0 or s.keys == 0)
 run popupPreservedTest = init.then(attach).then(all { assert(s.focus == 2), s' = s })
 run rootPreservedTest = init.then(ordinary).then(attach).then(all { assert(s.focus == 1), s' = s })
 run missingSeatFallsBackTest = init.then(expire).then(attach).then(all { assert(s.focus == 1), s' = s })
 run nullDesktopNoFocusTest = init.then(expire).then(emptyDesktop).then(attach).then(all { assert(s.focus == 0), s' = s })
 run additionalKeyboardNoFocusChangeTest = init.then(attach).then(expire).then(attach).then(all { assert(s.focus == 0), s' = s })
 run removalRestorationKeepsPopupTest = init.then(attach).then(press).then(remove).then(attach).then(all { assert(s.focus == 2 and s.keys == 0), s' = s })
 run expiredPopupRestorationFallsBackTest = init.then(attach).then(remove).then(expire).then(attach).then(all { assert(s.focus == 1 and s.keys == 0), s' = s })
}

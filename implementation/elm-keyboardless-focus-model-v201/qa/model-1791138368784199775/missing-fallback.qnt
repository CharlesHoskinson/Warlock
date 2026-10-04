module focus {
 var s: { count: int, focus: int, desktop: int, keys: int, violations: int, delivered: int }
 action init = s' = { count: 0, focus: 2, desktop: 1, keys: 0, violations: 0, delivered: 0 }
 val fallback = false
 val result = if (fallback) s.desktop else s.focus
 action attach = s' = { ...s, count: s.count + 1, focus: result, delivered: if (s.count == 0) result else s.delivered, violations: s.violations + (if (s.focus != 0 and result != s.focus) 1 else 0) }
 action remove = s' = { ...s, count: 0, keys: 0, delivered: 0 }
 action expire = s' = { ...s, focus: 0, delivered: 0 }
 action emptyDesktop = s' = { ...s, desktop: 0 }
 action ordinary = s' = { ...s, focus: 1 }
 action popup = s' = { ...s, focus: 2 }
 action press = s' = { ...s, keys: if (s.count > 0) 1 else 0 }
 action request(desired: int): bool = s' = { ...s, focus: desired, delivered: if (s.count > 0) desired else s.delivered }
 action bind(client: int): bool = s' = { ...s, delivered: if (s.count > 0 and s.focus != 0 and client == s.focus) s.focus else s.delivered }
 action step = any { attach, remove, expire, emptyDesktop, ordinary, popup, press, request(0), request(1), request(2), bind(1), bind(2) }
 val safety = s.violations == 0 and s.count >= 0 and (s.count > 0 or s.keys == 0)
 run popupPreservedTest = init.then(attach).then(all { assert(s.focus == 2), s' = s })
 run rootPreservedTest = init.then(ordinary).then(attach).then(all { assert(s.focus == 1), s' = s })
 run missingSeatFallsBackTest = init.then(expire).then(attach).then(all { assert(s.focus == 1), s' = s })
 run nullDesktopNoFocusTest = init.then(expire).then(emptyDesktop).then(attach).then(all { assert(s.focus == 0), s' = s })
 run additionalKeyboardNoFocusChangeTest = init.then(attach).then(expire).then(attach).then(all { assert(s.focus == 0), s' = s })
 run removalRestorationKeepsPopupTest = init.then(attach).then(press).then(remove).then(attach).then(all { assert(s.focus == 2 and s.keys == 0), s' = s })
 run expiredPopupRestorationFallsBackTest = init.then(attach).then(remove).then(expire).then(attach).then(all { assert(s.focus == 1 and s.keys == 0), s' = s })

 run keyboardlessPopupRequestTest = init.then(expire).then(request(2)).then(all { assert(s.count == 0 and s.focus == 2 and s.delivered == 0 and s.keys == 0), s' = s })
 run restoredKeyboardEntersRecordedPopupTest = init.then(expire).then(request(2)).then(attach).then(all { assert(s.focus == 2 and s.delivered == 2 and s.keys == 0), s' = s })
 run retiredKeyboardlessPopupFallsBackTest = init.then(request(2)).then(expire).then(attach).then(all { assert(s.focus == 1 and s.delivered == 1 and s.keys == 0), s' = s })
 run nullKeyboardlessFocusClearsIntentTest = init.then(request(2)).then(request(0)).then(attach).then(all { assert(s.focus == 1 and s.delivered == 1), s' = s })
 run latestKeyboardlessFocusWinsTest = init.then(request(2)).then(request(1)).then(attach).then(all { assert(s.focus == 1 and s.delivered == 1), s' = s })
 run additionalKeyboardPreservesLatestFocusTest = init.then(attach).then(request(1)).then(attach).then(all { assert(s.focus == 1 and s.delivered == 1), s' = s })
 run reopenPopupWhileKeyboardAbsentTest = init.then(attach).then(press).then(remove).then(expire).then(request(2)).then(attach).then(all { assert(s.focus == 2 and s.delivered == 2 and s.keys == 0), s' = s })
 run keyboardlessRequestNeverEntersTest = init.then(expire).then(request(2)).then(request(2)).then(bind(2)).then(all { assert(s.delivered == 0 and s.keys == 0), s' = s })
 run foreignKeyboardResourceCannotEnterTest = init.then(attach).then(request(2)).then(bind(1)).then(all { assert(s.focus == 2 and s.delivered == 2), s' = s })
 run destroyedFocusNeverEntersForeignResourceTest = init.then(attach).then(request(2)).then(expire).then(bind(1)).then(all { assert(s.focus == 0 and s.delivered == 0), s' = s })
}

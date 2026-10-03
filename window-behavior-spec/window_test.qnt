module window_test {
  import window.* from "./window"

  run snapOnlyOnReleaseTest =
    init.then(fire(StartDrag))
      .then(fire(MoveTo(Left)))
      .then(all {
        assert(w.dragging and w.mode == Normal and w.rect == HOME),
        assert(w.candidate == Left and snapsThisStep == 0 and noSnapBeforeRelease),
        fire(Release),
      })
      .then(all {
        assert(w.mode == Snapped and w.snapZone == Left and w.rect == zoneRect(Left)),
        assert(snapsThisStep == 1 and oneSnapOnRelease),
        fire(Blur),
      })

  run dragSnappedAwayTest =
    init.then(fire(Place(OTHER))).then(fire(StartDrag)).then(fire(MoveTo(Right))).then(fire(Release))
      .then(all { assert(w.mode == Snapped and w.normalRect == OTHER), fire(StartDrag) })
      .then(all {
        assert(w.mode == Normal and w.rect == OTHER and w.dragging),
        assert(snapsThisStep == 0),
        fire(MoveTo(Center)),
      })
      .then(fire(Release))
      .then(all { assert(w.mode == Normal and w.rect == OTHER and restoreGeometry), fire(Blur) })

  run dragMaximizedAwayTest =
    init.then(fire(Place(OTHER))).then(fire(Maximize))
      .then(all { assert(w.mode == Maximized and w.rect == FULL), fire(StartDrag) })
      .then(all {
        assert(w.mode == Normal and w.rect == OTHER and w.dragging),
        fire(MoveTo(Center)),
      })
      .then(fire(Release))
      .then(all { assert(w.mode == Normal and w.rect == OTHER), fire(Blur) })

  run focusChangeCancelsDragTest =
    init.then(fire(StartDrag)).then(fire(MoveTo(Left))).then(fire(Blur))
      .then(all {
        assert(not(w.dragging) and w.candidate == Center and snapsThisStep == 0),
        assert(not(canFire(w, activeWorkspace, Release))),
        fire(Focus),
      })
      .then(all { assert(noStaleDragAfterFocusChange), fire(StartDrag) })
      .then(fire(MoveTo(Right))).then(fire(SwitchTo(2)))
      .then(all { assert(not(w.dragging) and not(w.focused) and w.candidate == Center), fire(SwitchTo(1)) })

  run minimizeRestoresPriorModeTest =
    init.then(fire(StartDrag)).then(fire(MoveTo(Left))).then(fire(Release))
      .then(fire(Minimize))
      .then(all { assert(w.mode == Minimized and not(w.focused)), fire(Restore) })
      .then(all {
        assert(w.mode == Snapped and w.rect == zoneRect(Left) and w.normalRect == HOME),
        fire(Restore),
      })
      .then(all { assert(w.mode == Normal and w.rect == HOME), fire(Blur) })

  run pinnedAcrossWorkspacesTest =
    init.then(fire(TogglePin)).then(fire(SwitchTo(2)))
      .then(all {
        assert(w.pinned and w.focused and visible(w, activeWorkspace)),
        fire(TogglePin),
      })
      .then(all {
        assert(not(w.pinned) and not(w.focused) and not(visible(w, activeWorkspace))),
        fire(MoveWindowTo(2)),
      })
      .then(all { assert(visible(w, activeWorkspace) and workspaceAndPin), fire(Focus) })

  run thirdsGeometryTest = init.then(fire(Choose(ThirdLeft)))
    .then(all { assert(w.mode == Snapped and w.rect == zoneRect(ThirdLeft)), fire(Choose(ThirdCenter)) })
    .then(all {
      assert(w.rect.x == 33 and w.rect.width == 33),
      assert(zoneRect(ThirdLeft).width + zoneRect(ThirdCenter).width + zoneRect(ThirdRight).width == FULL.width),
      assert(zoneRect(ThirdRight).x + zoneRect(ThirdRight).width == FULL.width),
      fire(Choose(ThirdRight)),
    }).then(all { assert(allProps and w.normalRect == HOME), fire(Restore) })

  run asymmetricGeometryTest = init.then(fire(Choose(TwoThirdsLeft)))
    .then(all {
      assert(w.rect.x == 0 and w.rect.width == 66),
      assert(w.rect.width + zoneRect(ThirdRight).width == FULL.width),
      assert(w.rect.x + w.rect.width == zoneRect(ThirdRight).x),
      fire(Choose(TwoThirdsRight)),
    }).then(all {
      assert(w.rect.x == 33 and w.rect.width == 67),
      assert(zoneRect(ThirdLeft).width == w.rect.x and w.rect.x + w.rect.width == FULL.width),
      fire(Restore),
    })

  run layoutWidthBoundaryTest = init.then(fire(ResizeMonitor(1279)))
    .then(all {
      assert(availableFamilies(logicalWidth).size() == 4 and layoutFamilies),
      assert(not(canFireAt(w, activeWorkspace, logicalWidth, Choose(ThirdLeft)))),
      assert(not(canFireAt(w, activeWorkspace, logicalWidth, Choose(TwoThirdsRight)))),
      assert(canFireAt(w, activeWorkspace, logicalWidth, Choose(TopRight))),
      fire(ResizeMonitor(1280)),
    }).then(all {
      assert(availableFamilies(logicalWidth).size() == 7 and layoutFamilies),
      assert(canFireAt(w, activeWorkspace, logicalWidth, Choose(ThirdCenter))),
      assert(canFireAt(w, activeWorkspace, logicalWidth, Choose(TwoThirdsLeft))),
      fire(Choose(TwoThirdsLeft)),
    }).then(all { assert(layoutSelection and allProps), fire(ResizeMonitor(800)) })
    .then(all { assert(w.mode == Snapped and restoreGeometry), fire(Restore) })

  run chosenLayoutRestoresNormalTest = init.then(fire(Place(OTHER))).then(fire(Choose(ThirdCenter)))
    .then(fire(Minimize)).then(fire(Restore))
    .then(all { assert(w.rect == zoneRect(ThirdCenter) and w.normalRect == OTHER), fire(Focus) })
    .then(fire(StartDrag))
    .then(all { assert(w.rect == OTHER and w.mode == Normal and noSnapBeforeRelease), fire(Release) })
    .then(all { assert(w.rect == OTHER and w.normalRect == OTHER and allProps), fire(Blur) })
}

module desktop_test {
  import desktop.* from "./desktop"

  run appPinWithOpenWindowsTest = init.then(fire(PinApp(1)))
    .then(all { assert(pinnedApps.contains(1) and appWindows(1) == Set(1, 2)), fire(Close(1)) })
    .then(fire(Close(2)))
    .then(all { assert(taskbarApps.contains(1) and groupedTaskbar.get(1).size() == 0), fire(PinApp(1)) })
    .then(all { assert(not(taskbarApps.contains(1)) and pinDoesNotLaunch), fire(Open(1)) })

  run targetedFocusAndPinTest = init.then(fire(Focus(2)))
    .then(fire(PinWindow(1)))
    .then(all { assert(focused == 2 and windows.get(1).pinned and not(windows.get(2).pinned)), fire(Switch(2)) })
    .then(fire(Focus(1)))
    .then(fire(PinWindow(1)))
    .then(all { assert(focused == 0 and not(windows.get(1).pinned)), fire(Switch(1)) })

  run minimizeKeepsGroupingTest = init.then(fire(PinWindow(1))).then(fire(Snap((1, 1))))
    .then(fire(Snap((2, 2)))).then(fire(CreateGroup((1, 2))))
    .then(fire(Minimize(1))).then(fire(Minimize(2)))
    .then(all {
      assert(groups.keys().contains(1) and appWindows(1) == Set(1, 2)),
      assert(windows.get(1).pinned and windows.get(1).zone == 1),
      fire(Switch(3)),
    })
    .then(fire(Recall(1)))
    .then(all {
      assert(activeWorkspace == 1 and focused == 1),
      assert(not(windows.get(1).minimized) and not(windows.get(2).minimized)),
      assert(windows.get(1).pinned and allProps), fire(Focus(2)),
    })

  run closeDissolvesGroupTest = init.then(fire(Snap((1, 1)))).then(fire(Snap((2, 2))))
    .then(fire(CreateGroup((1, 2)))).then(fire(Close(2)))
    .then(all { assert(groups.keys().size() == 0 and not(canFire(Recall(1)))), fire(Open(2)) })
    .then(all { assert(windows.get(2).zone == 0 and groups.keys().size() == 0), fire(Focus(2)) })

  run movedAndResnappedMembersTest = init.then(fire(Snap((1, 1)))).then(fire(Snap((2, 2))))
    .then(fire(CreateGroup((1, 2)))).then(fire(Move((2, 2))))
    .then(all { assert(groups.keys().size() == 0 and not(canFire(CreateGroup((1, 2))))), fire(Move((2, 1))) })
    .then(fire(CreateGroup((1, 2)))).then(fire(Snap((1, 7))))
    .then(all { assert(groups.keys().size() == 0 and not(canFire(CreateGroup((1, 2))))), fire(Focus(1)) })

  run foreignWorkspaceRestoreTest = init.then(fire(Minimize(2))).then(fire(Switch(3)))
    .then(fire(Restore(2)))
    .then(all { assert(activeWorkspace == 1 and focused == 2 and not(windows.get(2).minimized)), fire(PinApp(1)) })

  run fourQuarterGroupTest = init.then(fire(Open(4)))
    .then(fire(Snap((1, 3)))).then(fire(Snap((2, 4))))
    .then(fire(Snap((3, 5)))).then(fire(Snap((4, 6))))
    .then(fire(CreateGroup((1, 2)))).then(fire(AddMember((1, 3)))).then(fire(AddMember((1, 4))))
    .then(all { assert(groups.get(1).members == Set(1, 2, 3, 4) and allProps), fire(Minimize(4)) })
    .then(fire(Recall(1)))
    .then(all { assert(not(windows.get(4).minimized) and groups.get(1).members.size() == 4), fire(Focus(4)) })

  run mixedHalfQuarterGroupTest = init.then(fire(Snap((1, 1))))
    .then(fire(Snap((2, 4)))).then(fire(Snap((3, 6))))
    .then(fire(CreateGroup((1, 2)))).then(fire(AddMember((1, 3))))
    .then(all { assert(groups.get(1).members == Set(1, 2, 3) and allProps), fire(Snap((3, 2))) })
    .then(all { assert(not(canFire(CreateGroup((2, 3))))), fire(Focus(3)) })

  run threeThirdsGroupTest = init.then(fire(Snap((1, 8)))).then(fire(Snap((2, 9)))).then(fire(Snap((3, 10))))
    .then(fire(CreateGroup((1, 2)))).then(fire(AddMember((1, 3))))
    .then(all { assert(groups.get(1).members == Set(1, 2, 3) and allProps), fire(Minimize(2)) })
    .then(fire(Recall(1)))
    .then(all { assert(not(windows.get(2).minimized) and windows.get(2).zone == 9 and allProps), fire(Focus(2)) })

  run asymmetricGroupAndOverlapTest = init.then(fire(Snap((1, 11)))).then(fire(Snap((2, 10))))
    .then(fire(CreateGroup((1, 2))))
    .then(all { assert(groups.get(1).members == Set(1, 2) and allProps), fire(Snap((3, 9))) })
    .then(all { assert(not(canFire(AddMember((1, 3))))), fire(Snap((1, 1))) })
    .then(all { assert(not(canFire(CreateGroup((1, 3)))) and not(complement(1, 9))), fire(Snap((3, 10))) })
    .then(all { assert(canFire(CreateGroup((1, 3))) and complement(1, 10)), fire(CreateGroup((1, 3))) })
}

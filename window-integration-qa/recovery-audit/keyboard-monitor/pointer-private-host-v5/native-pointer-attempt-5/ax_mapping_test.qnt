module ax_mapping_test {
  import ax_mapping.* from "./ax_mapping"
  action unique=init.then(fire(Native(1))).then(fire(Apps(1))).then(fire(Children(1))).then(fire(Role(true)))
  run realSingletonSucceedsTest=unique.then(fire(Reply)).then(all {assert(success),fire(Role(true))})
  run samePidMultipleNativeWindowsRefusedTest=unique.then(fire(Native(2))).then(fire(Reply))
    .then(all {assert(not(success)),fire(Role(true))})
  run multipleAxToplevelsRefusedTest=unique.then(fire(Children(2))).then(fire(Reply))
    .then(all {assert(not(success)),fire(Role(true))})
  run multipleAppPeersRefusedTest=unique.then(fire(Apps(2))).then(fire(Reply))
    .then(all {assert(not(success)),fire(Role(true))})
  run roleMustBeActualToplevelTest=unique.then(fire(Role(false))).then(fire(Reply))
    .then(all {assert(not(success)),fire(Role(true))})
  run staleHoverRejectedTest=unique.then(fire(HoverChanged)).then(fire(Reply))
    .then(all {assert(not(success)),fire(Role(true))})
  run staleOwnerRejectedTest=unique.then(fire(OwnerChanged)).then(fire(Reply))
    .then(all {assert(not(success)),fire(Role(true))})
  run retirementRejectedTest=unique.then(fire(Retire)).then(fire(Reply))
    .then(all {assert(not(success)),fire(Role(true))})
}

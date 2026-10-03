module monitor_owner_test {
  import monitor_owner.* from "./monitor_owner"
  run hiddenWorkspaceIsStorageTest = init.then(fire(Minimize))
    .then(all {assert(s.raw==0 and owner==1),fire(DeleteHome)})
    .then(all {assert(owner==1),fire(Restore)})
    .then(all {assert(s.raw==1 and not(s.minimized)),fire(Minimize)})
  run desktopMoveTest = init.then(fire(Minimize)).then(fire(MoveHome(0)))
    .then(all {assert(owner==0),fire(Restore)})
  run disconnectedOutputTest = init.then(fire(Minimize)).then(fire(DeleteHome))
    .then(fire(RemoveOutput)).then(all {assert(owner==0),fire(AddOutput("different"))})
    .then(all {assert(owner==0),fire(Restore)})
  run staleAddressTest = init.then(fire(Minimize)).then(fire(ReuseAddress))
    .then(all {assert(owner==0),fire(DeleteHome)})
    .then(all {assert(owner==0),fire(Restore)})
}

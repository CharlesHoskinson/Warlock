module native_drag_test {
  import native_drag.* from "./native_drag"
  run releaseUsesCapturedOwnerTest=init.then(fire(Begin(1))).then(fire(Focus(2))).then(fire(Release(true))).then(all{assert(s.lastTarget==1 and s.focus==2),fire(Release(true))}).then(all{assert(s.lastTarget==0),fire(Cancel)})
  run cancellationRestoresSnapTest=init.then(fire(Begin(1))).then(all{assert(not(s.snapped.contains(1))),fire(Cancel)}).then(all{assert(s.snapped.contains(1) and s.owner==0),fire(Release(true))}).then(all{assert(s.lastTarget==0),fire(Cancel)})
  run closeAndReuseRejectsReleaseTest=init.then(fire(Begin(1))).then(fire(Close(1))).then(fire(Open(1))).then(fire(Release(true))).then(all{assert(s.lastTarget==0 and not(s.snapped.contains(1))),fire(Cancel)})
  run reloadRejectsOldReleaseTest=init.then(fire(Begin(2))).then(fire(Reload)).then(fire(Release(true))).then(all{assert(s.lastTarget==0 and s.owner==0),fire(Begin(2))}).then(fire(Release(true))).then(all{assert(s.lastTarget==2),fire(Cancel)})
  run resizeNeverTriggersMoveSnapTest=init.then(fire(Resize(2))).then(fire(Release(true))).then(all{assert(s.lastTarget==0 and not(s.snapped.contains(2))),fire(Cancel)})
  run reloadRestoresSourceSnapAndRejectsReleaseTest=init.then(fire(Begin(1))).then(fire(Reload)).then(fire(Release(true)))
    .then(all{assert(s.snapped.contains(1) and s.owner==0 and s.lastTarget==0 and allProps),fire(Cancel)})
}

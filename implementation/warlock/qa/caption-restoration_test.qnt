module caption_restoration_test {
 import caption_restoration.* from "./caption-restoration"
 run maxFractionTest=init.then(fire(Maximize)).then(fire(Press(30))).then(fire(Motion(100))).then(all {assert(s.geom=={x:85,y:30,w:60,h:35}),s'=s})
 run snapFractionTest=init.then(fire(Snap)).then(fire(Press(20))).then(fire(Motion(100))).then(all {assert(s.geom=={x:85,y:30,w:60,h:35}),s'=s})
 run maxCancelTest=init.then(fire(Maximize)).then(fire(Press(30))).then(fire(Motion(100))).then(fire(Cancel)).then(all {assert(maxCancel and s.owner==0 and s.held),s'=s})
 run snapCancelTest=init.then(fire(Snap)).then(fire(Press(20))).then(fire(Motion(100))).then(fire(Cancel)).then(all {assert(snapCancel and s.owner==0 and s.held),s'=s})
 run releaseOnceTest=init.then(fire(Snap)).then(fire(Press(20))).then(fire(Motion(100))).then(fire(Release)).then(fire(Release)).then(all {assert(s.ends==1 and s.placement==0),s'=s})
 run cancelThenReleaseTest=init.then(fire(Maximize)).then(fire(Press(30))).then(fire(Motion(100))).then(fire(Cancel)).then(fire(Release)).then(all {assert(s.ends==1 and s.geom==MAX and s.placement==1),s'=s})
 run closeReplacementTest=init.then(fire(Snap)).then(fire(Press(20))).then(fire(Motion(100))).then(fire(Close)).then(fire(Reopen)).then(fire(Release)).then(all {assert(s.current==2 and s.owner==0 and s.geom==NORMAL and s.ends==1),s'=s})
 run maxClickKeepsPlacementTest=init.then(fire(Maximize)).then(fire(Press(30))).then(fire(Release)).then(all {assert(s.geom==MAX and s.placement==1 and s.ends==1),s'=s})
 run snapClickKeepsPlacementTest=init.then(fire(Snap)).then(fire(Press(20))).then(fire(Release)).then(all {assert(s.geom==SNAP and s.placement==2 and s.ends==1),s'=s})
 run cancelMaxThenRestoreOriginalTest=init.then(fire(Maximize)).then(fire(Press(30))).then(fire(Motion(100))).then(fire(Cancel)).then(fire(Release)).then(fire(RestoreOrdinary)).then(all {assert(s.geom==NORMAL and ordinaryRestored and s.ends==1),s'=s})
 run releasedMaxCanCaptureNewOrdinaryTest=init.then(fire(Maximize)).then(fire(Press(30))).then(fire(Motion(100))).then(fire(Release)).then(fire(Maximize)).then(all {assert(s.ordinary=={x:85,y:30,w:60,h:35} and s.geom==MAX),s'=s})
}

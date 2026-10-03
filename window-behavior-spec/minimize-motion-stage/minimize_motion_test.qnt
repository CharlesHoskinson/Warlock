module minimize_motion_test {
 import minimize_motion.* from "./minimize_motion"
 run readinessBeforeMinimizeTest=init.then(fire(Minimize)).then(all{assert(not(s.minimized) and s.overlay),fire(Ready(1))}).then(all{assert(s.minimized and allProps),fire(Finish(1))})
 run restoreAtEndpointTest=init.then(fire(Minimize)).then(fire(Ready(1))).then(fire(Finish(1))).then(fire(Restore)).then(fire(Ready(2))).then(all{assert(s.minimized and s.overlay),fire(Finish(2))}).then(all{assert(not(s.minimized) and allProps),fire(Reload)})
 run reverseRejectsOldCompletionTest=init.then(fire(Minimize)).then(fire(Ready(1))).then(fire(Restore)).then(fire(Finish(1))).then(all{assert(s.stale and s.minimized and s.overlay and allProps),fire(Finish(2))})
 run closeReuseRejectsOldCompletionTest=init.then(fire(Minimize)).then(fire(Close)).then(fire(Reuse)).then(fire(Finish(1))).then(all{assert(s.identity==2 and not(s.minimized) and s.stale and allProps),fire(Reload)})
 run shellReloadCommitsIntentTest=init.then(fire(Minimize)).then(fire(Ready(1))).then(fire(Restore)).then(fire(Reload)).then(all{assert(not(s.minimized) and not(s.overlay) and allProps),fire(Finish(2))})
 run reductionCommitsIntentTest=init.then(fire(Minimize)).then(fire(Ready(1))).then(fire(Restore)).then(fire(Reduce)).then(all{assert(not(s.minimized) and not(s.overlay) and allProps),fire(Minimize)})
 run rapidActivateUsesIntentTest=init.then(fire(Activate)).then(fire(Activate)).then(fire(Activate))
   .then(all{assert(s.intent and s.epoch==3 and allProps),fire(Ready(3))})
 run inactiveActivateRaisesTest=init.then(fire(Defocus)).then(fire(Activate))
   .then(all{assert(not(s.intent) and s.overlay and allProps),fire(Finish(1))})
 run foreignDesktopBeforeExpansionTest=init.then(fire(Minimize)).then(fire(Ready(1))).then(fire(Finish(1))).then(fire(OtherDesktop)).then(fire(Restore))
   .then(all{assert(s.desktop==s.homeDesktop and s.minimized and s.overlay and allProps),fire(Ready(2))})
}

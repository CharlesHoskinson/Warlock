module draft_focus_test {
 import draft_focus.* from "./draft_focus"
 run exposedFilesRaisesWithoutLosingDraftTest=init.then(fire(Type("sandbox-draft"))).then(fire(ClickFiles(1)))
 .then(all{assert(focus==1 and callbacks==1 and draft==List("sandbox-draft") and allProps),fire(ClickBrowser)})
 .then(fire(Type("-continued"))).then(all{assert(draft==List("sandbox-draft","-continued") and allProps),fire(Submit)})
 run privateReloadPreservesIndependentDraftTest=init.then(fire(Type("draft"))).then(fire(ClickFiles(1))).then(fire(Reload))
 .then(all{assert(focus==1 and callbacks==1 and draft==List("draft") and allProps),fire(ClickBrowser)})
 run staleFilesPeerCannotRaiseTest=init.then(fire(Type("draft"))).then(fire(RebuildFiles)).then(fire(ClickFiles(1)))
 .then(all{assert(focus==0 and callbacks==0 and draft==List("draft") and allProps),fire(ClickFiles(2))})
 .then(all{assert(focus==1 and callbacks==1 and allProps),fire(ClickBrowser)})
}

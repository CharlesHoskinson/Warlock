module shortcut_generation {
  // UI-019/outputs-return. Bounds are identical across replacement.
  // Correspondence: authority shellShortcut/refreshOutputs, OutputController
  // topology supersession, Shell correlated observations, Shortcuts admission.
  // Two roles communicate by separately delivered native observations and
  // shortcut replies. One held reply abstracts transport; no hardware/AT claim.
  var native: int
  var view: int
  var observed: int
  var ready: bool
  var held: int
  var seen: bool
  var opened: bool
  var retiredAdoption: bool
  action init = all {native'=1, view'=1, observed'=1, ready'=true,
    held'=0, seen'=false, opened'=false, retiredAdoption'=false}
  action press = all {held==0, native'=native, view'=view,
    observed'=observed, ready'=ready, held'=native, seen'=seen,
    opened'=opened, retiredAdoption'=retiredAdoption}
  action retire = all {native==1, native'=2, view'=view,
    observed'=observed, ready'=ready, held'=held, seen'=seen,
    opened'=opened, retiredAdoption'=retiredAdoption}
  action replace = all {native==2, view==1, native'=native, view'=2,
    observed'=observed, ready'=false, held'=held, seen'=seen,
    opened'=false, retiredAdoption'=retiredAdoption}
  // Old observations have retired request identity; they cannot make the new
  // topology ready. Current request correlation is grounded in existing Shell.
  action oldObservation = all {view==2, not(ready), native'=native,
    view'=view, observed'=observed, ready'=ready, held'=held,
    seen'=seen, opened'=opened, retiredAdoption'=retiredAdoption}
  action reconcile = all {view==2, not(ready), native'=native, view'=view,
    observed'=native, ready'=true, held'=held, seen'=seen,
    opened'=opened, retiredAdoption'=retiredAdoption}
  pure def admit(readyNow: bool, expected: int, pressed: int, consumed: bool): bool =
    readyNow and expected==pressed and pressed>0 and not(consumed)
  action deliver = all {held>0, native'=native, view'=view,
    observed'=observed, ready'=ready, held'=held, seen'=true,
    opened'=(opened or admit(ready,observed,held,seen)),
    retiredAdoption'=(retiredAdoption or (view==2 and held==1 and admit(ready,observed,held,seen)))}
  action deliverLegacy = all {held>0, native'=native, view'=view,
    observed'=observed, ready'=ready, held'=held, seen'=true,
    opened'=(opened or not(seen)),
    retiredAdoption'=(retiredAdoption or (view==2 and held==1 and not(seen)))}
  action freshPress = all {native==2, seen, held==1, native'=native,
    view'=view, observed'=observed, ready'=ready, held'=2, seen'=false,
    opened'=opened, retiredAdoption'=retiredAdoption}
  action step = any {press,retire,replace,oldObservation,reconcile,deliver,freshPress}
  val captured = held>0
  val nativeRetired = native==2
  val hostReplaced = view==2 and not(ready)
  val reconciled = view==2 and ready
  val staleConsumed = view==2 and held==1 and seen and not(opened)
  val freshOpened = view==2 and held==2 and opened
  val safety = not(retiredAdoption)
  // No fairness/liveness claim: delivery and reconciliation may be delayed
  // forever. Native observation-before-host-retirement races, transport limits,
  // counter exhaustion, multiple output transforms/AT/IME are outside this model.
}

module first_band_counterexample {
 import max_pin.* from "./retained-first-band-model/max_pin"
 run independentlyPinnedChildLosesNestedProtectionTest=init.then(pin(1)).then(fire(ChildOwnPin)).then(unpin(1)).then(check(s.windows.get(3).pinned and not(effective(4))))
}

module gesture_keys_test {
  import gesture_keys.* from "./gesture-keys"
  run ordinaryKeyTest=init.then(fire(Begin)).then(fire(Key)).then(all {assert(ordinaryRetains and safety),s'=s})
  run unrelatedChordTest=init.then(fire(Begin)).then(fire(Chord)).then(all {assert(chordRetains and safety),s'=s})
  run escapeReleaseTest=init.then(fire(Begin)).then(fire(EscapeRelease)).then(all {assert(releaseKeyRetains and safety),s'=s})
  run explicitCancelTest=init.then(fire(Begin)).then(fire(EscapePress)).then(all {assert(cancelled and safety),s'=s}).then(fire(PointerRelease)).then(all {assert(s.ends==1 and safety),s'=s})
  run nativeReleaseTest=init.then(fire(Begin)).then(fire(PointerRelease)).then(fire(Key)).then(fire(PointerRelease)).then(all {assert(s.ends==1 and s.owner==0 and safety),s'=s})
}

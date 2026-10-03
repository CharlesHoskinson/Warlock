module capture_lifecycle {
 var captures: int
 var uploaded: int
 var seeded: bool
 var pairs: int
 var retired: bool
 var bytesChanged: bool
 var accepted: bool
 action init = all {captures'=0,uploaded'=0,seeded'=false,pairs'=0,retired'=false,bytesChanged'=false,accepted'=false}
 action capture = all {not(retired),captures<3,captures'=captures+1,pairs'=pairs+1,uploaded'=uploaded,seeded'=seeded,retired'=retired,bytesChanged'=bytesChanged,accepted'=accepted}
 action upload = all {uploaded<captures,uploaded'=uploaded+1,captures'=captures,pairs'=pairs,seeded'=seeded,retired'=retired,bytesChanged'=bytesChanged,accepted'=accepted}
 action seed = all {captures==3,uploaded==3,seeded'=true,captures'=captures,pairs'=pairs,uploaded'=uploaded,retired'=retired,bytesChanged'=bytesChanged,accepted'=accepted}
 action retire = all {retired'=true,captures'=captures,pairs'=pairs,uploaded'=uploaded,seeded'=seeded,bytesChanged'=bytesChanged,accepted'=accepted}
 action changeBytes = all {bytesChanged'=true,accepted'=false,captures'=captures,pairs'=pairs,uploaded'=uploaded,seeded'=seeded,retired'=retired}
 action accept = all {retired,seeded,captures==3,uploaded==3,pairs==3,not(bytesChanged),accepted'=true,captures'=captures,pairs'=pairs,uploaded'=uploaded,seeded'=seeded,retired'=retired,bytesChanged'=bytesChanged}
 action idle = all {captures'=captures,pairs'=pairs,uploaded'=uploaded,seeded'=seeded,retired'=retired,bytesChanged'=bytesChanged,accepted'=accepted}
 action step = any {capture,upload,seed,retire,changeBytes,accept,idle}
 val invariant = all {captures>=0,captures<=3,pairs==captures,uploaded>=0,uploaded<=captures,seeded implies all {captures==3,uploaded==3},accepted implies all {retired,seeded,captures==3,pairs==3,not(bytesChanged)}}
 run fallbackCannotAcceptTest = init.then(retire).then(all {assert(not(accepted) and invariant),idle})
 run captureWithoutSeedCannotAcceptTest = init.then(capture).then(capture).then(capture).then(retire).then(all {assert(not(seeded) and not(accepted) and invariant),idle})
 run actualSeedAndPairsCanAcceptTest = init.then(capture).then(capture).then(capture).then(upload).then(upload).then(upload).then(seed).then(retire).then(accept).then(all {assert(accepted and invariant),idle})
 run changedPairsRevokeAcceptanceTest = init.then(capture).then(capture).then(capture).then(upload).then(upload).then(upload).then(seed).then(retire).then(accept).then(changeBytes).then(all {assert(not(accepted) and invariant),idle})
}

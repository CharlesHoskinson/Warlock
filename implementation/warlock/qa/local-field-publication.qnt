module local_field_publication {
  // UI-004 keyboard pin setup: Popup's owned field callbacks can arrive from
  // the preceding DOM paint in the same lease. External actions stay strict.
  // Abstract text as bounded integers; Elm event order is FIFO. Native paint,
  // input provenance, IME engines, AT and effect receipt acceptance are outside.
  var s: { pub: int, lease: int, domPub: int, domLease: int,
    draft: int, shown: int, pending: bool, effects: int }
  action init = s' = {pub:1,lease:1,domPub:1,domLease:1,
    draft:0,shown:0,pending:false,effects:0}
  action publish = all { s.pub < 20, s' = {...s,pub:s.pub+1} }
  action paint = s' = {...s,domPub:s.pub,domLease:s.lease,shown:s.draft}
  action localEdit(value:int,pub:int,lease:int): bool =
    if (lease==s.lease and pub>0 and pub<=s.pub and value>=0 and value<=4)
    s' = {...s,draft:value,pending:true}
    else s' = s
  action externalEdit(value:int,pub:int,lease:int): bool =
    if (lease==s.lease and pub==s.pub and value>=0 and value<=4)
    s' = {...s,draft:value,pending:true}
    else s' = s
  action activate(pub:int,lease:int): bool =
    if (lease==s.lease and pub==s.pub) s' = {...s,effects:s.effects+1}
    else s' = s
  action reopen = all { s.lease<10, s.pub<20,
    s'={...s,lease:s.lease+1,pub:s.pub+1,draft:0,pending:false} }
  action step = any {publish,paint,reopen,
    localEdit(3,s.domPub,s.domLease),externalEdit(4,s.domPub,s.domLease),
    activate(s.domPub,s.domLease)}
  val safety = s.pub >= s.domPub and s.lease >= s.domLease and
    s.draft>=0 and s.draft<=4 and s.effects>=0
  action check(ok:bool): bool = all { assert(ok), s'=s }
  run localPaintGapPreservesDraftTest = init.then(publish)
    .then(localEdit(3,1,1)).then(paint).then(check(s.shown==3 and s.pending and s.effects==0))
  run staleExternalEditRejectedTest = init.then(publish)
    .then(externalEdit(3,1,1)).then(paint).then(check(s.draft==0 and s.effects==0))
  run staleLocalButtonRejectedTest = init.then(publish)
    .then(activate(1,1)).then(check(s.effects==0))
  run retiredFieldCannotEditTest = init.then(reopen)
    .then(localEdit(3,1,1)).then(check(s.draft==0 and not(s.pending)))
  run futureFieldCannotEditTest = init.then(localEdit(3,2,1))
    .then(check(s.draft==0 and s.effects==0))
  run localFifoKeepsLatestDraftTest = init.then(publish)
    .then(localEdit(2,1,1)).then(localEdit(3,1,1)).then(publish)
    .then(paint).then(check(s.shown==3 and s.pending and s.effects==0))
  run currentActionStillWorksTest = init.then(publish).then(paint)
    .then(activate(2,1)).then(check(s.effects==1 and s.draft==0))
}

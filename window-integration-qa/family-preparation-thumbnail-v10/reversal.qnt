module reversal {
  type S = {receipt:int,visual:int,validated:int,presented:int,origin:int,
    sequence:int,pending:bool,uploads:int,sourceEpoch:int,closed:bool,
    effect:bool,effectReceipt:int}
  var s:S
  action init = s'={receipt:1,visual:1,validated:1,presented:0,origin:0,
    sequence:0,pending:false,uploads:3,sourceEpoch:1,closed:false,
    effect:false,effectReceipt:0}
  action show = all {not(s.closed),not(s.pending),s.visual==s.receipt,
    s'={...s,sequence:s.sequence+1,presented:s.sequence+1,effect:false}}
  action reserve = all {not(s.closed),s.presented>0,
    s'={...s,receipt:s.receipt+1,validated:0,pending:true,effect:false}}
  action oldFeedback = all {not(s.closed),s.pending,
    s'={...s,sequence:s.sequence+1,presented:s.sequence+1,effect:false}}
  action apply = all {not(s.closed),s.pending,s.presented>0,
    s'={...s,visual:s.receipt,origin:s.presented,pending:false,effect:false}}
  action validate(r:int):bool = s'=if(not(s.closed) and r==s.receipt and not(s.pending))
    {...s,validated:r,effect:false} else {...s,effect:false}
  action commit(r:int):bool = s'=if(not(s.closed) and not(s.pending) and
    r==s.receipt and s.visual==r and s.validated==r)
    {...s,effect:true,effectReceipt:r} else {...s,effect:false}
  action close = s'={...s,closed:true,visual:0,validated:0,pending:false,effect:false}
  action idle = s'=s
  action step = any {show,reserve,oldFeedback,apply,validate(s.receipt),
    validate(s.receipt-1),commit(s.receipt),commit(s.receipt-1),close,idle}
  val invariant = all {s.uploads==3,s.sourceEpoch==1,s.origin<=s.presented,
    s.presented<=s.sequence,s.effect implies all {not(s.closed),not(s.pending),
      s.effectReceipt==s.receipt,s.visual==s.receipt,s.validated==s.receipt}}
  run oldFeedbackBecomesDisplayedOriginTest = init.then(show).then(reserve)
    .then(oldFeedback).then(apply).then(all {assert(s.origin==2 and invariant),idle})
  run provisionalRetargetHasNoAuthorityTest = init.then(show).then(reserve)
    .then(apply).then(commit(2)).then(all {assert(not(s.effect) and invariant),idle})
  run oldReceiptCannotCommitTest = init.then(show).then(reserve).then(apply)
    .then(validate(2)).then(commit(1)).then(all {assert(not(s.effect) and invariant),idle})
  run currentValidatedReceiptCanCommitTest = init.then(show).then(reserve)
    .then(apply).then(validate(2)).then(commit(2)).then(all {assert(s.effect and invariant),idle})
  run secondReversalRetainsSourcesTest = init.then(show).then(reserve).then(apply)
    .then(show).then(reserve).then(apply).then(all {assert(s.receipt==3 and s.uploads==3 and s.sourceEpoch==1 and invariant),idle})
  run shutdownRevokesAuthorityTest = init.then(show).then(close).then(commit(1))
    .then(all {assert(not(s.effect) and invariant),idle})
}

module helper_boundary {
  type Event = Guard({exe:bool,argv:bool,owner:bool}) | Connect(bool)
    | Register(bool) | Send | Chunk({bounded:bool,durable:bool})
    | Eof(bool) | Receipt({valid:bool,nativeOk:bool}) | Publish(bool)
    | Tick(int) | ChangeAuthority | Idle
  type State = {clock:int,authority:bool,guarded:bool,peer:bool,registered:bool,
    sends:int,eof:bool,parsed:bool,nativeOk:bool,finalDurable:bool,outcome:str}
  var s:State
  pure val initial = {clock:0,authority:true,guarded:false,peer:false,
    registered:false,sends:0,eof:false,parsed:false,nativeOk:false,
    finalDurable:false,outcome:"pending"}
  action init = s'=initial
  pure def failure(b:State):State = {...b,outcome:if(b.sends==1)"uncertain" else "refused"}
  pure def evolve(b:State,e:Event):State = {
    if(b.outcome!="pending") b else {
      val timed = match e { | Tick(n) => {...b,clock:b.clock+n} | _ => b }
      if(timed.clock>=2) failure(timed) else match e {
        | Guard(v) => if(v.exe and v.argv and v.owner and b.authority)
            {...b,guarded:true} else failure(b)
        | Connect(v) => if(b.guarded and b.authority and v)
            {...b,peer:true} else failure(b)
        | Register(v) => if(v) {...b,registered:true} else failure(b)
        | Send => if(b.guarded and b.peer and b.registered and b.authority and b.sends==0)
            {...b,sends:1} else failure(b)
        | Chunk(v) => if(b.sends==1 and not(b.eof) and v.bounded and v.durable)
            b else failure(b)
        | Eof(v) => if(b.sends==1 and v) {...b,eof:true} else failure(b)
        | Receipt(v) => if(b.sends==1 and b.eof and v.valid and b.authority)
            {...b,parsed:true,nativeOk:v.nativeOk} else failure(b)
        | Publish(v) => if(b.parsed and v and b.authority)
            {...b,finalDurable:true,outcome:if(b.nativeOk)"complete" else "native-refused"}
            else failure(b)
        | ChangeAuthority => failure({...b,authority:false})
        | _ => timed
      }
    }
  }
  action fire(e:Event):bool = s'=evolve(s,e)
  val allProps = s.sends>=0 and s.sends<=1 and
    (s.outcome=="complete" implies s.sends==1 and s.eof and s.parsed and
      s.nativeOk and s.finalDurable and s.authority and s.clock<2) and
    (s.outcome=="uncertain" implies s.sends==1) and
    (s.outcome=="refused" implies s.sends==0)
  action step = {
    nondet b=Set(true,false).oneOf()
    nondet e=Set(Guard({exe:b,argv:true,owner:true}),Connect(b),Register(b),Send,
      Chunk({bounded:b,durable:true}),Chunk({bounded:true,durable:b}),Eof(b),
      Receipt({valid:b,nativeOk:true}),Receipt({valid:true,nativeOk:b}),
      Publish(b),Tick(1),ChangeAuthority,Idle).oneOf()
    fire(e)
  }
  action check(v:bool):bool = all {assert(v),s'=s}
  action prepared = fire(Guard({exe:true,argv:true,owner:true})).then(fire(Connect(true))).then(fire(Register(true)))
  action sent = prepared.then(fire(Send))
  action validReply = sent.then(fire(Eof(true))).then(fire(Receipt({valid:true,nativeOk:true})))
  run completionNeedsDurableReceiptTest = init.then(validReply).then(check(s.outcome=="pending")).then(fire(Publish(true))).then(check(s.outcome=="complete" and allProps))
  run wrongExecutableRefusesTest = init.then(fire(Guard({exe:false,argv:true,owner:true}))).then(check(s.outcome=="refused" and s.sends==0))
  run wrongArgvRefusesTest = init.then(fire(Guard({exe:true,argv:false,owner:true}))).then(check(s.outcome=="refused"))
  run wrongOwnerRefusesTest = init.then(fire(Guard({exe:true,argv:true,owner:false}))).then(check(s.outcome=="refused"))
  run wrongPeerRefusesTest = init.then(fire(Guard({exe:true,argv:true,owner:true}))).then(fire(Connect(false))).then(check(s.outcome=="refused"))
  run missingRegistrationRefusesTest = init.then(fire(Guard({exe:true,argv:true,owner:true}))).then(fire(Connect(true))).then(fire(Send)).then(check(s.outcome=="refused" and s.sends==0))
  run malformedCompletionIsUncertainTest = init.then(sent).then(fire(Eof(true))).then(fire(Receipt({valid:false,nativeOk:true}))).then(check(s.outcome=="uncertain"))
  run partialReplyCannotBecomeCompleteTest = init.then(sent).then(fire(Receipt({valid:true,nativeOk:true}))).then(fire(Eof(true))).then(fire(Receipt({valid:true,nativeOk:true}))).then(fire(Publish(true))).then(check(s.outcome=="uncertain"))
  run rawEvidenceFailureIsUncertainTest = init.then(sent).then(fire(Chunk({bounded:true,durable:false}))).then(check(s.outcome=="uncertain"))
  run eofEvidenceFailureIsUncertainTest = init.then(sent).then(fire(Eof(false))).then(check(s.outcome=="uncertain"))
  run finalEvidenceFailureIsUncertainTest = init.then(validReply).then(fire(Publish(false))).then(check(s.outcome=="uncertain"))
  run oversizeIsUncertainTest = init.then(sent).then(fire(Chunk({bounded:false,durable:true}))).then(check(s.outcome=="uncertain"))
  run deadlineBeforeSendRefusesTest = init.then(prepared).then(fire(Tick(2))).then(fire(Send)).then(check(s.outcome=="refused" and s.sends==0))
  run dripDoesNotResetDeadlineTest = init.then(sent).then(fire(Tick(1))).then(fire(Chunk({bounded:true,durable:true}))).then(fire(Tick(1))).then(fire(Eof(true))).then(check(s.outcome=="uncertain" and s.clock==2))
  run sourceChangeAfterSendIsUncertainTest = init.then(sent).then(fire(ChangeAuthority)).then(check(s.outcome=="uncertain"))
  run nativeRefusalIsDurableTest = init.then(sent).then(fire(Eof(true))).then(fire(Receipt({valid:true,nativeOk:false}))).then(fire(Publish(true))).then(check(s.outcome=="native-refused" and s.finalDurable))
  run uncertaintyCannotRetryTest = init.then(sent).then(fire(Tick(2))).then(prepared).then(fire(Send)).then(check(s.outcome=="uncertain" and s.sends==1))
  run secondSendCannotCompleteTest = init.then(sent).then(fire(Send)).then(fire(Eof(true))).then(fire(Receipt({valid:true,nativeOk:true}))).then(fire(Publish(true))).then(check(s.outcome=="uncertain" and s.sends==1))
}

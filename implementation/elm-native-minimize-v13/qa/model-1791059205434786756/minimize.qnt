module minimize {
  type Intent = { request: int, generation: int, target: int, minimize: bool, expected: int, output: int, epoch: int }
  type State = { minimized: Set[int], focus: int, mru: List[int], revision: int, output: int, epoch: int, last: Intent, status: str, workspace: List[int], geometry: List[int] }
  var s: State
  pure val emptyIntent = {request:0,generation:0,target:0,minimize:false,expected:0,output:0,epoch:0}
  pure def family(target: int): Set[int] = if(target==1 or target==2) Set(1,2) else Set(3)
  pure def eligible(minimized: Set[int], id: int): bool = (id==2 or id==3) and not(minimized.contains(id))
  pure def nextFocus(minimized: Set[int], mru: List[int]): int = mru.foldl(0,(acc,id)=>if(eligible(minimized,id)) id else acc)
  action init = s' = {minimized:Set(),focus:2,mru:List(3,2),revision:1,output:1,epoch:1,last:emptyIntent,status:"Idle",workspace:List(1,1,1),geometry:List(80,80,320,240)}
  def current(request: int, generation: int, target: int, minimize: bool): Intent = {request:request,generation:generation,target:target,minimize:minimize,expected:s.revision,output:s.output,epoch:s.epoch}
  action effect(intent: Intent): bool = {
    val members=family(intent.target)
    val validState=members.forall(id=>s.minimized.contains(id)==not(intent.minimize))
    val fresh=intent.expected==s.revision and intent.output==s.output and intent.epoch==s.epoch
    val valid=Set(1,2,3).contains(intent.target) and fresh and validState
    val minimized=if(intent.minimize) s.minimized.union(members) else s.minimized.exclude(members)
    val focus=if(intent.minimize) (if(members.contains(s.focus)) nextFocus(minimized,s.mru) else s.focus) else (if(intent.target==3) 3 else 2)
    val mru=if(focus==0) s.mru else s.mru.foldl(List(),(acc,id)=>if(id!=focus) acc.append(id) else acc).append(focus)
    s' = if(intent.request<=s.last.request or intent.generation<=s.last.generation) s
      else if(not(valid)) {...s,last:intent,status:"Refused"}
      else {...s,minimized:minimized,focus:focus,mru:mru,revision:s.revision+1,last:intent,status:"Committed"}
  }
  action focus(id: int): bool = s' = if(eligible(s.minimized,id)) {...s,focus:id,mru:s.mru.foldl(List(),(acc,x)=>if(x!=id) acc.append(x) else acc).append(id),revision:s.revision+1} else s
  action outputChange = s' = {...s,output:s.output+1,revision:s.revision+1}
  action step = any {
    effect(current(s.last.request+1,s.last.generation+1,1,true)),
    effect(current(s.last.request+1,s.last.generation+1,1,false)),
    effect(current(s.last.request+1,s.last.generation+1,2,true)),
    effect(current(s.last.request+1,s.last.generation+1,2,false)),
    effect(current(s.last.request+1,s.last.generation+1,3,true)),
    effect(current(s.last.request+1,s.last.generation+1,3,false)),
    effect({...current(s.last.request+1,s.last.generation+1,1,true),expected:s.revision+1}),
    effect({...current(s.last.request+1,s.last.generation+1,1,true),output:s.output+1}),
    effect({...current(s.last.request+1,s.last.generation+1,1,true),epoch:s.epoch+1}),
    effect(s.last),focus(2),focus(3),outputChange
  }
  val safety = (s.minimized.contains(1)==s.minimized.contains(2)) and
    (s.focus==0 or eligible(s.minimized,s.focus)) and s.workspace==List(1,1,1) and s.geometry==List(80,80,320,240)
  run focusSuccessorTest = init.then(effect(current(1,1,1,true))).then(all{assert(s.focus==3 and s.minimized==Set(1,2)),s'=s})
  run lastFocusTest = init.then(effect(current(1,1,1,true))).then(effect(current(2,2,3,true))).then(all{assert(s.focus==0 and s.minimized==Set(1,2,3)),s'=s})
  run unfocusedTest = init.then(focus(3)).then(effect(current(1,1,1,true))).then(all{assert(s.focus==3),s'=s})
  run modalRestoreTest = init.then(effect(current(1,1,1,true))).then(effect(current(2,2,1,false))).then(all{assert(s.focus==2 and s.minimized==Set()),s'=s})
  run staleRevisionTest = init.then(effect({...current(1,1,1,true),expected:2})).then(all{assert(s.status=="Refused" and s.focus==2 and s.minimized==Set()),s'=s})
  run staleOutputTest = init.then(effect({...current(1,1,1,true),output:2})).then(all{assert(s.status=="Refused" and s.minimized==Set()),s'=s})
  run staleEpochTest = init.then(effect({...current(1,1,1,true),epoch:2})).then(all{assert(s.status=="Refused" and s.minimized==Set()),s'=s})
  run retryTest = init.then(effect(current(1,1,1,true))).then(effect(s.last)).then(all{assert(s.revision==2 and s.focus==3 and s.status=="Committed"),s'=s})
  run minimizedFocusRefusedTest = init.then(effect(current(1,1,1,true))).then(focus(2)).then(all{assert(s.focus==3),s'=s})
}

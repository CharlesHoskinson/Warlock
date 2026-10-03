module lifecycle {
  type Intent = { request: int, generation: int, target: int, minimize: bool, expected: int, output: int, epoch: int }
  type State = { mapped: Set[int], minimized: Set[int], focus: int, mru: List[int], revision: int, output: int, epoch: int, last: Intent, status: str, workspace: List[int], geometry: List[int] }
  var s: State
  pure val emptyIntent = {request:0,generation:0,target:0,minimize:false,expected:0,output:0,epoch:0}
  def family(target: int): Set[int] = (if(target==1 or target==2 or target==4) Set(1,2,4) else Set(3)).intersect(s.mapped)
  pure def eligible(minimized: Set[int], id: int): bool = (id==2 or id==3 or id==4) and not(minimized.contains(id))
  pure def nextFocus(minimized: Set[int], mru: List[int]): int = mru.foldl(0,(acc,id)=>if(eligible(minimized,id)) id else acc)
  action init = s' = {mapped:Set(1,2,3),minimized:Set(),focus:2,mru:List(3,2),revision:1,output:1,epoch:1,last:emptyIntent,status:"Idle",workspace:List(1,1,1),geometry:List(80,80,320,240)}
  def current(request: int, generation: int, target: int, minimize: bool): Intent = {request:request,generation:generation,target:target,minimize:minimize,expected:s.revision,output:s.output,epoch:s.epoch}
  action effect(intent: Intent): bool = {
    val members=family(intent.target)
    val validState=members.forall(id=>s.minimized.contains(id)==not(intent.minimize))
    val fresh=intent.expected==s.revision and intent.output==s.output and intent.epoch==s.epoch
    val valid=s.mapped.contains(intent.target) and fresh and validState and (intent.minimize or intent.target==3 or not(s.mapped.contains(4)))
    val minimized=if(intent.minimize) s.minimized.union(members) else s.minimized.exclude(members)
    val focus=if(intent.minimize) (if(members.contains(s.focus)) nextFocus(minimized,s.mru) else s.focus) else (if(intent.target==3) 3 else 2)
    val mru=if(focus==0) s.mru else s.mru.foldl(List(),(acc,id)=>if(id!=focus) acc.append(id) else acc).append(focus)
    s' = if(intent.request<=s.last.request or intent.generation<=s.last.generation) s
      else if(not(valid)) {...s,last:intent,status:"Refused"}
      else {...s,minimized:minimized,focus:focus,mru:mru,revision:s.revision+1,last:intent,status:"Committed"}
  }
  action focus(id: int): bool = s' = if(s.mapped.contains(id) and eligible(s.minimized,id)) {...s,focus:id,mru:s.mru.foldl(List(),(acc,x)=>if(x!=id) acc.append(x) else acc).append(id),revision:s.revision+1} else s
  action birth = {
    val inherited=s.minimized.contains(1)
    s' = if(s.mapped.contains(4)) s else {...s,mapped:s.mapped.union(Set(4)),minimized:if(inherited) s.minimized.union(Set(4)) else s.minimized,focus:if(inherited) s.focus else 4,mru:if(inherited) s.mru else s.mru.append(4),revision:s.revision+1}
  }
  action retire = {
    val minimized=s.minimized.exclude(Set(4))
    val mru=s.mru.foldl(List(),(acc,id)=>if(id!=4) acc.append(id) else acc)
    s' = if(not(s.mapped.contains(4))) s else {...s,mapped:s.mapped.exclude(Set(4)),minimized:minimized,focus:if(s.focus==4) nextFocus(minimized,mru) else s.focus,mru:mru,revision:s.revision+1}
  }
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
    effect(s.last),focus(2),focus(3),focus(4),birth,retire,outputChange
  }
  val safety = (s.minimized.contains(1)==s.minimized.contains(2)) and (not(s.mapped.contains(4)) or s.minimized.contains(1)==s.minimized.contains(4)) and
    (s.focus==0 or (s.mapped.contains(s.focus) and eligible(s.minimized,s.focus))) and s.workspace==List(1,1,1) and s.geometry==List(80,80,320,240)
  run focusSuccessorTest = init.then(effect(current(1,1,1,true))).then(all{assert(s.focus==3 and s.minimized==Set(1,2)),s'=s})
  run lastFocusTest = init.then(effect(current(1,1,1,true))).then(effect(current(2,2,3,true))).then(all{assert(s.focus==0 and s.minimized==Set(1,2,3)),s'=s})
  run unfocusedTest = init.then(focus(3)).then(effect(current(1,1,1,true))).then(all{assert(s.focus==3),s'=s})
  run modalRestoreTest = init.then(effect(current(1,1,1,true))).then(effect(current(2,2,1,false))).then(all{assert(s.focus==2 and s.minimized==Set()),s'=s})
  run staleRevisionTest = init.then(effect({...current(1,1,1,true),expected:2})).then(all{assert(s.status=="Refused" and s.focus==2 and s.minimized==Set()),s'=s})
  run staleOutputTest = init.then(effect({...current(1,1,1,true),output:2})).then(all{assert(s.status=="Refused" and s.minimized==Set()),s'=s})
  run staleEpochTest = init.then(effect({...current(1,1,1,true),epoch:2})).then(all{assert(s.status=="Refused" and s.minimized==Set()),s'=s})
  run retryTest = init.then(effect(current(1,1,1,true))).then(effect(s.last)).then(all{assert(s.revision==2 and s.focus==3 and s.status=="Committed"),s'=s})
  run minimizedFocusRefusedTest = init.then(effect(current(1,1,1,true))).then(focus(2)).then(all{assert(s.focus==3),s'=s})
  run childBirthExcludedTest = init.then(effect(current(1,1,1,true))).then(birth).then(all{assert(s.minimized==Set(1,2,4) and s.focus==3),s'=s})
  run ambiguousRestoreRefusedTest = init.then(effect(current(1,1,1,true))).then(birth).then(effect(current(2,2,1,false))).then(all{assert(s.status=="Refused" and s.minimized==Set(1,2,4) and s.focus==3),s'=s})
  run childRetireRestoreRecoveryTest = init.then(effect(current(1,1,1,true))).then(birth).then(effect(current(2,2,1,false))).then(retire).then(effect(current(3,3,1,false))).then(all{assert(s.status=="Committed" and s.minimized==Set() and s.focus==2),s'=s})
  run childDirectFocusExcludedTest = init.then(effect(current(1,1,1,true))).then(birth).then(focus(4)).then(all{assert(s.focus==3),s'=s})
}

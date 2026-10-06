module retirement_async {
 type State={first:bool,pendingFirst:bool,knownFirst:bool,readyFirst:bool,
  second:bool,pendingSecond:bool,readySecond:bool,fresh:bool,cutoff:int,
  commands:List[str],history:List[str]}
 type Event=ObserveFirst|ObserveSecond|TerminalFirst|FinalFirst|FinalSecond|
  OldSeedFirst|OldSeedSecond|MidSeedFresh|FreshSeed|ForeignFinal|PrematureFinal|
  DuplicateTerminal|OldObservation
 var s:State
 pure def label(e:Event):str=match e{
  |ObserveFirst=>"ObserveFirst"|ObserveSecond=>"ObserveSecond"|TerminalFirst=>"TerminalFirst"
  |FinalFirst=>"FinalFirst"|FinalSecond=>"FinalSecond"|OldSeedFirst=>"OldSeedFirst"
  |OldSeedSecond=>"OldSeedSecond"|MidSeedFresh=>"MidSeedFresh"|FreshSeed=>"FreshSeed"
  |ForeignFinal=>"ForeignFinal"|PrematureFinal=>"PrematureFinal"
  |DuplicateTerminal=>"DuplicateTerminal"|OldObservation=>"OldObservation"}
 pure def reduce(st:State,e:Event):State={
  val base={...st,commands:[]}
  match e{
   |ObserveFirst=>if(st.first and not(st.pendingFirst))
      {...base,pendingFirst:true,commands:["first:cancel"]} else base
   |ObserveSecond=>if(st.second and not(st.pendingSecond))
      {...base,pendingSecond:true,readySecond:true,commands:["second:retire-ready"]} else base
   |TerminalFirst=>{...base,knownFirst:false,readyFirst:true,commands:["first:acknowledge","first:retire-ready"]}
   |FinalFirst=>if(st.first and st.readyFirst and not(st.pendingSecond))
      {...base,first:false,pendingFirst:false,readyFirst:false,cutoff:if(st.cutoff>102)st.cutoff else 102} else base
   |FinalSecond=>if(st.second and st.readySecond)
      {...base,second:false,pendingSecond:false,readySecond:false,cutoff:104} else base
   |MidSeedFresh=>if(st.cutoff<103){...base,fresh:true} else base
   |FreshSeed=>{...base,fresh:true}
   |_=>base
  }
 }
 action init=s'={first:true,pendingFirst:false,knownFirst:true,readyFirst:false,
  second:true,pendingSecond:false,readySecond:false,fresh:false,cutoff:0,commands:[],history:[]}
 action fire(e:Event):bool=all{
  match e{
   |TerminalFirst=>s.first and s.pendingFirst and s.knownFirst
   |OldSeedFirst=>not(s.first)
   |OldSeedSecond=>not(s.second)
   |MidSeedFresh=>not(s.fresh) and s.cutoff>0
   |FreshSeed=>not(s.fresh) and s.cutoff>0
   |PrematureFinal=>not(s.readyFirst)
   |DuplicateTerminal=>s.readyFirst or not(s.first)
   |_=>true
  },
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(ObserveFirst,ObserveSecond,TerminalFirst,FinalFirst,FinalSecond,
  OldSeedFirst,OldSeedSecond,MidSeedFresh,FreshSeed,ForeignFinal,PrematureFinal,DuplicateTerminal,OldObservation).oneOf();fire(e)}
 val safety=all{s.readyFirst implies (s.first and s.pendingFirst and not(s.knownFirst)),
  s.readySecond implies (s.second and s.pendingSecond),not(s.first) implies not(s.knownFirst),
  s.cutoff==0 or s.cutoff==102 or s.cutoff==104}
}

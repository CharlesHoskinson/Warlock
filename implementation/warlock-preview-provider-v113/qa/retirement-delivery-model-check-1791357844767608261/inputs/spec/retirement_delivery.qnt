module retirement_delivery {
 type State={channel:bool,first:bool,pendingFirst:bool,knownFirst:bool,readyFirst:bool,
  second:bool,pendingSecond:bool,readySecond:bool,processed:int,cutoff:int,
  commands:List[str],history:List[str]}
 type Event=Activate|ObserveFirst|ObserveSecond|TerminalFirst|DeliverFirst1|
  DeliverSecond1|DeliverFirst2|DeliverSecond2|GapFirst3|LegacyFirst|ForeignFirst1|
  Replacement|DuplicateTerminal|OldSeed
 var s:State
 pure def label(e:Event):str=match e{
  |Activate=>"Activate"|ObserveFirst=>"ObserveFirst"|ObserveSecond=>"ObserveSecond"
  |TerminalFirst=>"TerminalFirst"|DeliverFirst1=>"DeliverFirst1"|DeliverSecond1=>"DeliverSecond1"
  |DeliverFirst2=>"DeliverFirst2"|DeliverSecond2=>"DeliverSecond2"|GapFirst3=>"GapFirst3"
  |LegacyFirst=>"LegacyFirst"|ForeignFirst1=>"ForeignFirst1"|Replacement=>"Replacement"
  |DuplicateTerminal=>"DuplicateTerminal"|OldSeed=>"OldSeed"}
 pure def complete(st:State,first:bool,ordinal:int):State={
  val ready=if(first)st.readyFirst else st.readySecond
  val ack=if(first)(if(ordinal==1)["first:retire-delivery-ack:1"] else if(ordinal==2)["first:retire-delivery-ack:2"] else ["first:retire-delivery-ack:3"])
    else (if(ordinal==1)["second:retire-delivery-ack:1"] else ["second:retire-delivery-ack:2"])
  if(not(st.channel))st
  else if(ordinal<=st.processed){...st,commands:ack}
  else if(ordinal==st.processed+1 and ready)
   if(first){...st,first:false,pendingFirst:false,readyFirst:false,processed:ordinal,
    cutoff:if(st.cutoff>102)st.cutoff else 102,commands:ack}
   else {...st,second:false,pendingSecond:false,readySecond:false,processed:ordinal,
    cutoff:104,commands:ack}
  else st
 }
 pure def reduce(st:State,e:Event):State={
  val base={...st,commands:[]}
  match e{
   |Activate=>if(not(st.channel) and not(st.pendingFirst) and not(st.pendingSecond) and st.cutoff==0){...base,channel:true} else base
   |ObserveFirst=>if(st.first and not(st.pendingFirst)){...base,pendingFirst:true,commands:["first:cancel"]} else base
   |ObserveSecond=>if(st.second and not(st.pendingSecond)){...base,pendingSecond:true,readySecond:true,commands:["second:retire-ready"]} else base
   |TerminalFirst=>{...base,knownFirst:false,readyFirst:true,commands:["first:acknowledge","first:retire-ready"]}
   |DeliverFirst1=>complete(base,true,1)
   |DeliverSecond1=>complete(base,false,1)
   |DeliverFirst2=>complete(base,true,2)
   |DeliverSecond2=>complete(base,false,2)
   |GapFirst3=>complete(base,true,3)
   |LegacyFirst=>if(not(st.channel) and st.readyFirst){...base,first:false,pendingFirst:false,readyFirst:false,cutoff:if(st.cutoff>102)st.cutoff else 102} else base
   |_=>base
  }
 }
 action init=s'={channel:false,first:true,pendingFirst:false,knownFirst:true,readyFirst:false,
  second:true,pendingSecond:false,readySecond:false,processed:0,cutoff:0,commands:[],history:[]}
 action fire(e:Event):bool=all{
  match e{
   |TerminalFirst=>s.first and s.pendingFirst and s.knownFirst
   |DuplicateTerminal=>s.readyFirst or not(s.first)
   |OldSeed=>not(s.first)
   |_=>true
  },val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Activate,ObserveFirst,ObserveSecond,TerminalFirst,DeliverFirst1,
  DeliverSecond1,DeliverFirst2,DeliverSecond2,GapFirst3,LegacyFirst,ForeignFirst1,
  Replacement,DuplicateTerminal,OldSeed).oneOf();fire(e)}
 val safety=all{s.readyFirst implies (s.first and s.pendingFirst and not(s.knownFirst)),
  s.readySecond implies (s.second and s.pendingSecond),not(s.first) implies not(s.knownFirst),
  s.processed>=0 and s.processed<=2,s.processed>0 implies s.channel,
  s.cutoff==0 or s.cutoff==102 or s.cutoff==104}
}

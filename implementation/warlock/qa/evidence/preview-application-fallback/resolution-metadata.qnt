module metadata {
 type State = {revision:int,visible:bool,capturing:bool,cancels:int,history:List[str]}
 type Event = Fresh | Stale | Foreign | Lock | OtherDenial | ForeignLock | ObserveLocked | UnlockFresh | UnlockStale
 var s:State
 pure def label(event:Event):str=match event { |Fresh=>"Fresh" |Stale=>"Stale" |Foreign=>"Foreign" |Lock=>"Lock" |OtherDenial=>"OtherDenial" |ForeignLock=>"ForeignLock" |ObserveLocked=>"ObserveLocked" |UnlockFresh=>"UnlockFresh" |UnlockStale=>"UnlockStale" }
 pure def reduce(st:State,event:Event):State=match event {
  |Fresh=>{...st,revision:st.revision+1}
  |Lock=>if(st.capturing){...st,visible:false,capturing:false,cancels:st.cancels+1} else st
  |OtherDenial=>if(st.capturing){...st,capturing:false,cancels:st.cancels+1} else st
  |ObserveLocked=>{...st,visible:false,capturing:false,cancels:st.cancels+(if(st.capturing)1 else 0)}
  |UnlockFresh=>{...st,visible:true}
  |_=>st
 }
 action init=s'={revision:0,visible:true,capturing:true,cancels:0,history:[]}
 action fire(event:Event):bool={val updated=reduce(s,event);s'={...updated,history:s.history.append(label(event))}}
 action step={nondet event=Set(Fresh,Stale,Foreign,Lock,OtherDenial,ForeignLock,ObserveLocked,UnlockFresh,UnlockStale).oneOf();fire(event)}
 val safety=s.revision>=0 and s.cancels>=0 and s.cancels<=1 and (s.capturing==(s.cancels==0))
 val freshWitness=s.revision>0
 val concealedWitness=not(s.visible)
 val cancelledWitness=s.cancels==1
}

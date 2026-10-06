module metadata {
 type Event = Fresh | Stale | Foreign | Lock | OtherDenial | ForeignLock | ObserveLocked | UnlockFresh | UnlockStale
 var s: {revision:int,visible:bool,capturing:bool,cancels:int,history:List[str]}
 val events=Set(Fresh,Stale,Foreign,Lock,OtherDenial,ForeignLock,ObserveLocked,UnlockFresh,UnlockStale)
 val name(event:Event)=match event {Fresh=>"Fresh"|Stale=>"Stale"|Foreign=>"Foreign"|Lock=>"Lock"|OtherDenial=>"OtherDenial"|ForeignLock=>"ForeignLock"|ObserveLocked=>"ObserveLocked"|UnlockFresh=>"UnlockFresh"|UnlockStale=>"UnlockStale"}
 val after(event:Event)=match event {
  Fresh=>s.with("revision",s.revision+1)
  |Lock=>if(s.capturing)s.with("visible",false).with("capturing",false).with("cancels",s.cancels+1) else s
  |OtherDenial=>if(s.capturing)s.with("capturing",false).with("cancels",s.cancels+1) else s
  |ObserveLocked=>s.with("visible",false).with("capturing",false).with("cancels",s.cancels+(if(s.capturing)1 else 0))
  |UnlockFresh=>s.with("visible",true)
  |_=>s
 }
 action init=s'={revision:0,visible:true,capturing:true,cancels:0,history:[]}
 action fire(event:Event)=s'=after(event).with("history",s.history.append(name(event)))
 action step={nondet event=events.oneOf();fire(event)}
 val safety=s.revision>=0 and s.cancels>=0 and s.cancels<=1 and (s.capturing==(s.cancels==0))
}

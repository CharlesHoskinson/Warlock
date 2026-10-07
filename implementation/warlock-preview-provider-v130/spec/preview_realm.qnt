module preview_realm {
 type Event=Open|FailedOpen|ConcurrentOpen|Reconcile|Poll|AckJob|RetireActor|AckActor|ConfirmActor|Close|Legacy|OldTicket
 // phase and through are protocol-history ghosts. They are not a second policy
 // or native resource oracle. All other fields are compared with actual C data.
 type State={phase:int,through:int,epoch:int,closed:int,active:bool,records:int,actors:int,terminal:bool,proofs:int,ready:bool,last:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Open=>"Open"|FailedOpen=>"FailedOpen"|ConcurrentOpen=>"ConcurrentOpen"|Reconcile=>"Reconcile"|Poll=>"Poll"|AckJob=>"AckJob"|RetireActor=>"RetireActor"|AckActor=>"AckActor"|ConfirmActor=>"ConfirmActor"|Close=>"Close"|Legacy=>"Legacy"|OldTicket=>"OldTicket"}
 pure def reduce(st:State,e:Event):State=
  if(e==Open){...st,phase:1,through:st.through+1,epoch:st.through+1,active:true,records:1,actors:1,terminal:false,proofs:0,ready:false,last:1}
  else if(e==FailedOpen){...st,through:st.through+1,last: -1}
  else if(e==ConcurrentOpen or e==OldTicket){...st,last: -1}
  else if(e==Legacy){...st,last:if(st.through==0)1 else -1}
  else if(e==Reconcile){...st,phase:2,last:1}
  else if(e==Poll){...st,phase:3,terminal:true,proofs:2,last:1}
  else if(e==AckJob){...st,phase:4,records:0,terminal:false,proofs:0,last:1}
  else if(e==RetireActor){...st,phase:5,actors:0,last:1}
  else if(e==AckActor){...st,phase:6,last:1}
  else if(e==ConfirmActor){...st,phase:7,ready:true,last:1}
  else if(st.phase==7){...st,phase:0,active:false,closed:st.closed+1,ready:false,last:1}
  else {...st,last: -1}
 action init=s'={phase:0,through:0,epoch:0,closed:0,active:false,records:0,actors:0,terminal:false,proofs:0,ready:false,last:0,history:[]}
 action fire(e:Event):bool=all{
  match e {
   |Open=>s.phase==0
   |FailedOpen=>s.phase==0 and s.closed>0
   |ConcurrentOpen=>s.active
   |Reconcile=>s.phase==1
   |Poll=>s.phase==2
   |AckJob=>s.phase==3
   |RetireActor=>s.phase==4
   |AckActor=>s.phase==5
   |ConfirmActor=>s.phase==6
   |Close=>s.active
   |Legacy=>true
   |OldTicket=>s.phase==1 and s.closed>0
  },
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Open,FailedOpen,ConcurrentOpen,Reconcile,Poll,AckJob,RetireActor,AckActor,ConfirmActor,Close,Legacy,OldTicket).oneOf();fire(e)}
 val safety=all{s.active==(s.phase>0),s.epoch<=s.through,s.active implies s.epoch>0,
  s.terminal implies (s.records==1 and s.proofs==2),s.ready implies (s.active and s.actors==0 and s.records==0 and s.phase==7),
  not(s.active) implies (s.records==0 and s.actors==0 and not(s.ready)),s.closed<=s.epoch,s.proofs==0 or s.proofs==2}
}

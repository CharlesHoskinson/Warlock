module retirement_readiness {
 type State={retained:bool,ready:bool,complete:bool,finished:bool,
  issued:int,acked:int,last:bool,history:List[str]}
 type Event=Observe|Ready|Commit|Abandon|Ack|GapAck|WrongEpoch
 var s:State
 pure def label(e:Event):str=match e{|Observe=>"Observe"|Ready=>"Ready"|Commit=>"Commit"|Abandon=>"Abandon"|Ack=>"Ack"|GapAck=>"GapAck"|WrongEpoch=>"WrongEpoch"}
 pure def reduce(st:State,e:Event):State=match e{
  |Observe=>{...st,retained:true,last:true}
  |Ready=>{...st,ready:st.retained,last:st.retained}
  |Commit=>{...st,complete:true,issued:1,last:true}
  |Abandon=>{...st,last:true}
  |Ack=>if(st.complete){...st,retained:false,ready:false,complete:false,finished:true,acked:1,last:true}
    else {...st,last:st.acked==1}
  |_=>{...st,last:false}
 }
 action init=s'={retained:false,ready:false,complete:false,finished:false,issued:0,acked:0,last:false,history:[]}
 action fire(e:Event):bool=all{
  match e{|Observe=>not(s.finished) and not(s.complete)|Ready=>not(s.complete)
   |Commit=>s.retained and not(s.complete)|Abandon=>s.retained and not(s.complete)|_=>true},
  val next=reduce(s,e);s'={...next,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Observe,Ready,Commit,Abandon,Ack,GapAck,WrongEpoch).oneOf();fire(e)}
 val safety=all{s.acked<=s.issued,s.issued<=1,s.ready implies s.retained,
  s.complete implies (s.retained and s.issued==1 and s.acked==0),
  s.finished implies (not(s.retained) and s.acked==1)}
}

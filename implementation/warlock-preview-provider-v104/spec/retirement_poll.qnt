module retirement_poll {
 type Event=Observe(int)|Ready(int)|Complete(int)|Poll|WrongEpoch|Ack
 type State={retained:Set[int],ready:Set[int],complete:Set[int],order:List[int],
  issued:int,acked:int,after:int,selected:int,last:bool,history:List[str]}
 var s:State
 pure def suffix(e:int):str=if(e==1) "1" else if(e==2) "2" else "3"
 pure def label(e:Event):str=match e{
  |Observe(i)=>"Observe"++suffix(i)|Ready(i)=>"Ready"++suffix(i)
  |Complete(i)=>"Complete"++suffix(i)|Poll=>"Poll"|WrongEpoch=>"WrongEpoch"|Ack=>"Ack"}
 pure def first(es:Set[int]):int=if(es.contains(1)) 1 else if(es.contains(2)) 2 else if(es.contains(3)) 3 else 0
 pure def choose(st:State):int={
  val waiting=st.ready.exclude(st.complete)
  val later=waiting.filter(i=>i>st.after)
  if(later.size()>0) first(later) else first(waiting)
 }
 pure def reduce(st:State,e:Event):State=match e{
  |Observe(i)=>{...st,retained:st.retained.union(Set(i)),last:true}
  |Ready(i)=>{...st,ready:st.ready.union(Set(i)),last:true}
  |Complete(i)=>{...st,complete:st.complete.union(Set(i)),order:st.order.append(i),issued:st.issued+1,last:true}
  |Poll=>{val pick=choose(st);{...st,after:if(pick>0)pick else st.after,selected:pick,last:true}}
  |WrongEpoch=>{...st,last:false}
  |Ack=>if(st.order.length()>0){val i=st.order.nth(0);{...st,retained:st.retained.exclude(Set(i)),ready:st.ready.exclude(Set(i)),complete:st.complete.exclude(Set(i)),order:st.order.slice(1,st.order.length()),acked:st.acked+1,last:true}}else {...st,last:false}
 }
 action init=s'={retained:Set(),ready:Set(),complete:Set(),order:[],issued:0,acked:0,after:0,selected:0,last:false,history:[]}
 action fire(e:Event):bool=all{
  match e{|Observe(i)=>not(s.complete.contains(i))|Ready(i)=>s.retained.contains(i) and not(s.complete.contains(i))
   |Complete(i)=>s.ready.contains(i) and not(s.complete.contains(i))|Ack=>s.order.length()>0|_=>true},
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Observe(1),Observe(2),Observe(3),Ready(1),Ready(2),Ready(3),Complete(1),Complete(2),Complete(3),Poll,WrongEpoch,Ack).oneOf();fire(e)}
 val safety=all{s.retained.size()<=3,s.ready.subseteq(s.retained),s.complete.subseteq(s.ready),s.after>=0,s.after<=3,s.selected>=0,s.selected<=3,s.issued-s.acked==s.complete.size(),s.order.length()==s.complete.size()}
}

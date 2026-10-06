module feedback {
 type State={active:bool,owned:bool,cancelled:bool,publication:int,sequence:int,floor:int,outcome:str,acquires:int,cancels:int,acks:int,history:List[str]}
 type Event=Capacity|Expired|Waiting|Conflict|Exhausted|Duplicate|Older|WrongClock|WrongOwner|WrongSubject|WrongStamp|Close|Reopen|Issue|Proof
 var s:State
 pure def label(e:Event):str=match e{|Capacity=>"Capacity"|Expired=>"Expired"|Waiting=>"Waiting"|Conflict=>"Conflict"|Exhausted=>"Exhausted"|Duplicate=>"Duplicate"|Older=>"Older"|WrongClock=>"WrongClock"|WrongOwner=>"WrongOwner"|WrongSubject=>"WrongSubject"|WrongStamp=>"WrongStamp"|Close=>"Close"|Reopen=>"Reopen"|Issue=>"Issue"|Proof=>"Proof"}
 pure def local(e:Event):str=match e{|Capacity=>"capacity"|Expired=>"expired"|Waiting=>"waiting"|Conflict=>"conflict"|Exhausted=>"exhausted"|_=>""}
 pure def reduce(st:State,e:Event):State=match e{
  |Close=>{...st,active:false,outcome:"",cancelled:st.owned,cancels:st.cancels+(if(st.owned and not(st.cancelled))1 else 0)}
  |Reopen=>{...st,active:true,publication:st.publication+1}
  |Issue=>{...st,owned:true,cancelled:false,outcome:"",sequence:st.sequence+1,floor:st.sequence+1,acquires:st.acquires+1}
  |Proof=>{...st,owned:false,cancelled:false,acks:st.acks+1}
  |_=>if(local(e)!=""){...st,sequence:st.sequence+1,floor:if(st.active and not(st.owned))st.sequence+1 else st.floor,outcome:if(st.active and not(st.owned))local(e) else st.outcome} else st
 }
 action init=s'={active:true,owned:false,cancelled:false,publication:1,sequence:1,floor:0,outcome:"",acquires:0,cancels:0,acks:0,history:[]}
 action fire(e:Event):bool=all{
  if(e==Issue)s.active and not(s.owned) else if(e==Proof)s.owned else if(e==Reopen)not(s.active) else if(e==Duplicate or e==Older)s.floor>0 else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Capacity,Expired,Waiting,Conflict,Exhausted,Duplicate,Older,WrongClock,WrongOwner,WrongSubject,WrongStamp,Close,Reopen,Issue,Proof).oneOf();fire(e)}
 val safety=all{s.sequence>=s.floor,s.floor>=0,s.outcome=="" or (s.active and not(s.owned)),not(s.cancelled) or s.owned,s.acquires>=s.acks,s.cancels<=s.acquires}
}

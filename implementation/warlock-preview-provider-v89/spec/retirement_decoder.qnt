module retirement_decoder {
 type State={sequence:int,now:int,issued:int,accepted:int,status:str,history:List[str]}
 type Event=Active|Retired|FutureZero|WrongBinding|WrongClock|WrongRequest|WrongSubject|Replay|EarlierNow|EarlierFrontier|RetiredAbove|FutureBelow|Unknown
 var s:State
 pure def label(e:Event):str=match e{ |Active=>"Active" |Retired=>"Retired" |FutureZero=>"FutureZero" |WrongBinding=>"WrongBinding" |WrongClock=>"WrongClock" |WrongRequest=>"WrongRequest" |WrongSubject=>"WrongSubject" |Replay=>"Replay" |EarlierNow=>"EarlierNow" |EarlierFrontier=>"EarlierFrontier" |RetiredAbove=>"RetiredAbove" |FutureBelow=>"FutureBelow" |Unknown=>"Unknown" }
 pure def reduce(st:State,e:Event):State=match e{
  |Active=>{...st,sequence:st.sequence+1,now:st.now+10,issued:3+st.sequence,accepted:st.accepted+1,status:"Active"}
  |Retired=>{...st,sequence:st.sequence+1,now:st.now+10,issued:3+st.sequence,accepted:st.accepted+1,status:"Retired"}
  |FutureZero=>{...st,sequence:1,now:10,issued:0,accepted:1,status:"Future"}
  |_=>{...st,status:"Invalid"}
 }
 action init=s'={sequence:0,now:0,issued:0,accepted:0,status:"Ready",history:[]}
 action fire(e:Event):bool=all{
  if(e==FutureZero)s.sequence==0 else if(e==Replay or e==EarlierNow or e==EarlierFrontier)s.sequence>0 and s.issued>0 else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Active,Retired,FutureZero,WrongBinding,WrongClock,WrongRequest,WrongSubject,Replay,EarlierNow,EarlierFrontier,RetiredAbove,FutureBelow,Unknown).oneOf();fire(e)}
 val safety=all{s.sequence==s.accepted,s.now==10*s.accepted,s.issued==0 or s.issued==2+s.sequence,s.status=="Future" implies s.issued==0}
}

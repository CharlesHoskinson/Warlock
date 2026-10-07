module visual_channel {
 type Event=Attach|Offer|Retry|Ack|Current|Change|Invalidate|Detach|ForeignContext|ForeignThread|Destroy
 type State={held:bool,attached:bool,lease:int,sequence:int,version:int,pending:int,accepted:bool,code:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Attach=>"Attach"|Offer=>"Offer"|Retry=>"Retry"|Ack=>"Ack"|Current=>"Current"|Change=>"Change"|Invalidate=>"Invalidate"|Detach=>"Detach"|ForeignContext=>"ForeignContext"|ForeignThread=>"ForeignThread"|Destroy=>"Destroy"}
 pure def reduce(st:State,e:Event):State={
  val base={...st,code:0};
  if(e==Change){...base,version:st.version+1}
  else if(not(st.held)){...base,code:1}
  else if(e==ForeignThread){...base,code:2}
  else if(e==ForeignContext){...base,code:3}
  else if(e==Destroy){if(st.attached){...base,code:1}else{...base,held:false}}
  else if(e==Attach){if(st.attached){...base,code:1}else{...base,attached:true,lease:st.lease+1,pending:-1,accepted:false}}
  else if(not(st.attached)){...base,code:3}
  else if(e==Detach){...base,attached:false,pending:-1,accepted:false}
  else if(e==Invalidate){...base,pending:-1,accepted:false}
  else if(e==Offer){...base,sequence:st.sequence+1,pending:st.version,accepted:false}
  else if(st.pending==-1 or st.pending!=st.version){...base,pending:-1,accepted:false,code:4}
  else if(e==Ack){...base,accepted:true}
  else if(e==Current and not(st.accepted)){...base,code:4}
  else base
 }
 action init=s'={held:true,attached:false,lease:0,sequence:0,version:0,pending:-1,accepted:false,code:0,history:[]}
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Attach,Offer,Retry,Ack,Current,Change,Invalidate,Detach,ForeignContext,ForeignThread,Destroy).oneOf();fire(e)}
 val safety=all{s.accepted implies (s.held and s.attached and s.pending>=0),not(s.attached) implies (s.pending==-1 and not(s.accepted)),not(s.held) implies not(s.attached),s.lease>=0,s.sequence>=0,s.code>=0,s.code<=4}
}

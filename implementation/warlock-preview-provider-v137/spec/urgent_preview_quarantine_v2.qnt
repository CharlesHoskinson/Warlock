module urgent_preview_quarantine_v2 {
 type Event=Quarantine|Issue|Retry|ForeignQuarantine|Ordinary|ForeignTicket
 type State={pending:List[str],deferred:List[str],closing:bool,demand:bool,known:int,held:int,commands:List[str],history:List[str]}
 var s:State
 pure def takeOne(st:State,offered:List[str]):State={
  val slots=if(st.pending.length()==0 and offered.length()>0)1 else 0;
  val retained=st.pending.concat(offered.slice(0,slots));
  {...st,pending:retained,deferred:offered.slice(slots,offered.length()),commands:retained}
 }
 pure def reduce(st:State,e:Event):State={
  val base={...st,commands:[]};
  if(e==Issue){...base,pending:[]}
  else if(e==ForeignTicket)base
  else if(e==Retry)takeOne(base,st.deferred)
  else if(e==Quarantine and not(st.closing))takeOne({...base,closing:true,demand:false},st.deferred.concat(["reconcile:binding","cancel:first","cancel:neighbor"]))
  else if(st.deferred.length()>0)base
  else {...base,commands:st.pending}
 }
 action init=s'={pending:["acquire:first"],deferred:["acquire:neighbor"],closing:false,demand:true,known:2,held:2,commands:["acquire:first"],history:[]}
 pure def label(e:Event):str=match e{|Quarantine=>"Quarantine"|Issue=>"Issue"|Retry=>"Retry"|ForeignQuarantine=>"ForeignQuarantine"|Ordinary=>"Ordinary"|ForeignTicket=>"ForeignTicket"}
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Quarantine,Issue,Retry,ForeignQuarantine,Ordinary,ForeignTicket).oneOf();fire(e)}
 val safety=all{s.pending.length()<=1,s.deferred.length()<=4,s.known==2,s.held==2,s.closing implies not(s.demand)}
}

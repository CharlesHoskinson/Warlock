module control_reservations {
 type Event=ReserveA|ReserveB|IssueA1|IssueA2|IssueB1|IssueB2|ReleaseA|ReleaseB|Deliver|ForeignReserve|ChangedA1|OldA1|Boundary|CapacityProbe|SecondIssuer
 type State={a:int,b:int,ar:int,br:int,a1:int,a2:int,b1:int,b2:int,
  issued:int,delivered:int,confirmed:int,groups:int,last:int,lastOrdinal:int,history:List[str]}
 var s:State
 pure val maximum=18446744073709551615
 pure def label(e:Event):str=match e{|ReserveA=>"ReserveA"|ReserveB=>"ReserveB"|IssueA1=>"IssueA1"|IssueA2=>"IssueA2"|IssueB1=>"IssueB1"|IssueB2=>"IssueB2"|ReleaseA=>"ReleaseA"|ReleaseB=>"ReleaseB"|Deliver=>"Deliver"|ForeignReserve=>"ForeignReserve"|ChangedA1=>"ChangedA1"|OldA1=>"OldA1"|Boundary=>"Boundary"|CapacityProbe=>"CapacityProbe"|SecondIssuer=>"SecondIssuer"}
 pure def tickets(st:State):int=List(st.a1,st.a2,st.b1,st.b2).filter(i=>i>0).length()
 pure def reserveAllowed(st:State):bool=st.ar+st.br+2<=maximum-st.issued and st.ar+st.br+tickets(st)+2<=4
 pure def reduce(st:State,e:Event):State=
  if(e==Boundary){...st,issued:maximum-3,delivered:maximum-3,confirmed:maximum-3,last:1}
  else if(e==ReserveA){if(reserveAllowed(st)){...st,a:st.groups+1,ar:2,groups:st.groups+1,last:1}else {...st,last:0}}
  else if(e==ReserveB){if(reserveAllowed(st)){...st,b:st.groups+1,br:2,groups:st.groups+1,last:1}else {...st,last:0}}
  else if(e==IssueA1){if(st.a1>0){...st,last:1,lastOrdinal:st.a1}else {...st,a1:st.issued+1,issued:st.issued+1,ar:st.ar-1,last:1,lastOrdinal:st.issued+1}}
  else if(e==IssueA2){if(st.a2>0){...st,last:1,lastOrdinal:st.a2}else {...st,a2:st.issued+1,issued:st.issued+1,ar:st.ar-1,last:1,lastOrdinal:st.issued+1}}
  else if(e==IssueB1){if(st.b1>0){...st,last:1,lastOrdinal:st.b1}else {...st,b1:st.issued+1,issued:st.issued+1,br:st.br-1,last:1,lastOrdinal:st.issued+1}}
  else if(e==IssueB2){if(st.b2>0){...st,last:1,lastOrdinal:st.b2}else {...st,b2:st.issued+1,issued:st.issued+1,br:st.br-1,last:1,lastOrdinal:st.issued+1}}
  else if(e==CapacityProbe){...st,last:0}
  else if(e==Deliver){...st,delivered:st.issued,confirmed:st.issued,last:1}
  else if(e==ReleaseA){if(st.a1<=st.confirmed and st.a2<=st.confirmed){...st,a:0,ar:0,a1:0,a2:0,last:1}else {...st,last:0}}
  else if(e==ReleaseB){if(st.b1<=st.confirmed and st.b2<=st.confirmed){...st,b:0,br:0,b1:0,b2:0,last:1}else {...st,last:0}}
  else {...st,last:-1}
 action init=s'={a:0,b:0,ar:0,br:0,a1:0,a2:0,b1:0,b2:0,issued:0,delivered:0,confirmed:0,groups:0,last:0,lastOrdinal:0,history:[]}
 action fire(e:Event):bool=all{
  match e{|ReserveA=>s.a==0|ReserveB=>s.b==0|IssueA1=>s.a>0|IssueA2=>s.a>0|IssueB1=>s.b>0|IssueB2=>s.b>0|ReleaseA=>s.a>0|ReleaseB=>s.b>0|ChangedA1=>s.a1>0|OldA1=>s.a==0 and s.groups>0|Boundary=>s.history.length()==0|CapacityProbe=>s.ar+s.br+tickets(s)==4|_=>true},
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(ReserveA,ReserveB,IssueA1,IssueA2,IssueB1,IssueB2,ReleaseA,ReleaseB,Deliver,ForeignReserve,ChangedA1,CapacityProbe,SecondIssuer).oneOf();fire(e)}
 val safety=all{s.ar>=0,s.br>=0,s.ar+s.br+tickets(s)<=4,s.ar+s.br<=maximum-s.issued,s.confirmed<=s.delivered,s.delivered<=s.issued,s.issued<=maximum}
}

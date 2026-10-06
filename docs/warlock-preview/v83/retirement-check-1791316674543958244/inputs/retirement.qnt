module retirement {
 type State={issued:int,owned:Set[int],minimized:bool,status:str,history:List[str]}
 type Event=Birth|CloseFirst|MinimizeFirst|QueryFirst|QueryFuture|QueryZero|QueryIncoherent
 var s:State
 pure def label(e:Event):str=match e{ |Birth=>"Birth" |CloseFirst=>"CloseFirst" |MinimizeFirst=>"MinimizeFirst" |QueryFirst=>"QueryFirst" |QueryFuture=>"QueryFuture" |QueryZero=>"QueryZero" |QueryIncoherent=>"QueryIncoherent" }
 pure def reduce(st:State,e:Event):State=match e{
  |Birth=>{...st,issued:st.issued+1,owned:st.owned.union(Set(st.issued+1)),status:"Born"}
  |CloseFirst=>{...st,owned:st.owned.exclude(Set(1)),status:"Closed"}
  |MinimizeFirst=>{...st,minimized:true,status:"Minimized"}
  |QueryFirst=>{...st,status:if(st.issued==0)"Future" else if(st.owned.contains(1))"Active" else "Retired"}
  |QueryFuture=>{...st,status:"Future"}
  |QueryZero=>{...st,status:"Invalid"}
  |QueryIncoherent=>{...st,status:"Invalid"}
 }
 action init=s'={issued:0,owned:Set(),minimized:false,status:"Ready",history:[]}
 action fire(e:Event):bool=all{
  if(e==Birth)s.issued<16 else if(e==CloseFirst or e==MinimizeFirst)s.owned.contains(1) else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Birth,CloseFirst,MinimizeFirst,QueryFirst,QueryFuture,QueryZero,QueryIncoherent).oneOf();fire(e)}
 val safety=all{s.issued>=0,s.issued<=16,s.owned.forall(id=>id>0 and id<=s.issued),s.status=="Retired" implies s.issued>0 and not(s.owned.contains(1)),s.status=="Active" implies s.owned.contains(1)}
}

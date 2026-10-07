module uri_callback_lifetime {
 type Event=Open|Read|CloseReader|DestroyEndpoint|ReplaceReceiver|Bind|Clear|NewRealm|Expire|ForeignBind|DropOwner
 // through and route are retained protocol ghosts, not pixel/resource oracles.
 type State={live:bool,epoch:int,through:int,route:int,expired:bool,reader:bool,readerEpoch:int,offset:int,physical:bool,allowed:bool,owner:bool,last:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Open=>"Open"|Read=>"Read"|CloseReader=>"CloseReader"|DestroyEndpoint=>"DestroyEndpoint"|ReplaceReceiver=>"ReplaceReceiver"|Bind=>"Bind"|Clear=>"Clear"|NewRealm=>"NewRealm"|Expire=>"Expire"|ForeignBind=>"ForeignBind"|DropOwner=>"DropOwner"}
 pure def reduce(st:State,e:Event):State=
  if(e==Open){...st,reader:st.allowed,readerEpoch:if(st.allowed)st.epoch else 0,offset:0,last:if(st.allowed)1 else -1}
  else if(e==Read){if(st.live and st.readerEpoch==st.epoch and not(st.expired)){...st,offset:if(st.offset<16)st.offset+1 else st.offset,last:if(st.offset<16)1 else 0}else {...st,last: -1}}
  else if(e==CloseReader){...st,reader:false,readerEpoch:0,offset:0,last:1}
  else if(e==DestroyEndpoint){...st,live:false,last:1}
  else if(e==ReplaceReceiver){...st,epoch:st.epoch+1,last:1}
  else if(e==Bind){if(st.epoch>st.through){...st,through:st.epoch,route:st.epoch,last:1}else if(st.route==st.epoch){...st,last:1}else {...st,last: -1}}
  else if(e==Clear){...st,route:0,last:1}
  else if(e==NewRealm){...st,live:true,epoch:st.epoch+1,expired:false,last:1}
  else if(e==Expire){...st,expired:true,last:1}
  else if(e==ForeignBind){...st,last: -1}
  else {...st,owner:false,last:1}
 action init=s'={live:true,epoch:1,through:1,route:1,expired:false,reader:false,readerEpoch:0,offset:0,physical:true,allowed:true,owner:true,last:0,history:[]}
 action fire(e:Event):bool=all{
  match e{
   |Open=>not(s.reader)
   |Read=>s.reader
   |CloseReader=>s.reader
   |DestroyEndpoint=>s.live
   |ReplaceReceiver=>s.live
   |Bind=>s.live
   |Clear=>true
   |NewRealm=>not(s.live) and not(s.reader)
   |Expire=>s.live
   |ForeignBind=>true
   |DropOwner=>s.owner
  },
  val updated=reduce(s,e);
  s'={...updated,physical:updated.live or updated.reader,allowed:updated.live and updated.route==updated.epoch and not(updated.expired),history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Open,Read,CloseReader,DestroyEndpoint,ReplaceReceiver,Bind,Clear,NewRealm,Expire,ForeignBind,DropOwner).oneOf();fire(e)}
 val safety=all{s.physical==(s.live or s.reader),s.allowed implies(s.live and not(s.expired)),not(s.live) implies not(s.allowed),s.readerEpoch<=s.epoch,s.epoch>0,s.through<=s.epoch,s.route<=s.through,s.reader or s.readerEpoch==0,s.last>= -1 and s.last<=1,s.offset>=0 and s.offset<=16}
}

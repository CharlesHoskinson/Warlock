module feedback {
 type Pending={seq:int,generation:int,token:int,x:int,output:int}
 type State={generation:int,token:int,x:int,next:int,pending:List[Pending],records:List[Pending],last:int,before:int,accepted:bool,validOrigin:bool}
 type Event=Request | Tick | Reverse | Replace | Presented((int,int)) | Discard(int)
 var s:State
 action init=s'={generation:1,token:1,x:0,next:1,pending:List(),records:List(),last:0,before:0,accepted:false,validOrigin:false}
 action fire(e:Event):bool={
  val b={...s,before:s.records.length(),accepted:false,validOrigin:false}
  s'=match e {
   | Request=>if(s.pending.length()>=4)b else {...b,next:s.next+1,pending:s.pending.append({seq:s.next,generation:s.generation,token:s.token,x:s.x,output:1})}
   | Tick=>{...b,x:s.x+1}
   | Reverse=>{...b,token:s.token+1}
   | Replace=>{...b,generation:s.generation+1,pending:List(),last:0}
   | Discard(n)=>{...b,pending:s.pending.select(p=>p.seq!=n)}
   | Presented(pair)=>{
    val n=pair._1
    val o=pair._2
    val found=s.pending.select(p=>p.seq==n)
    if(found.length()!=1)b else {
     val f=found.nth(0)
     val clean={...b,pending:s.pending.select(p=>p.seq!=n)}
     if(f.generation!=s.generation or f.output!=o or n<=s.last)clean else {...clean,records:s.records.append(f).slice(if(s.records.length()>=8)s.records.length()-7 else 0,s.records.length()+1),last:n,accepted:true,validOrigin:true}
    }
   }
  }
 }
 val noSyntheticOrigin=s.accepted implies s.validOrigin
 val rejectedCannotRecord=not(s.accepted) implies s.records.length()==s.before
 val bounded=s.pending.length()<=4 and s.records.length()<=8
 val allProps=noSyntheticOrigin and rejectedCannotRecord and bounded
 action step={nondet e=Set(Request,Tick,Reverse,Replace,Presented((s.next-1,1)),Presented((s.next-2,1)),Presented((s.next-1,2)),Discard(s.next-1)).oneOf();fire(e)}
}

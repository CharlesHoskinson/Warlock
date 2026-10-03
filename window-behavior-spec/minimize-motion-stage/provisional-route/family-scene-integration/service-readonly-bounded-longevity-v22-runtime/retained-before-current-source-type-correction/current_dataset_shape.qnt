module current_dataset_shape {
 type Header={version:int,versionTyped:bool,faultFalse:bool,serial:int,serialTyped:bool,epoch:int,epochTyped:bool,fieldsComplete:bool,binding:int,directory:int,predecessor:int,countConsistent:bool}
 type Event=Check(Header)|Connect|Reply|Confirm(Header)|Consume|Invalidate
 type State={phase:int,fault:bool,bytesNow:bool,currentHeader:Header,nativeEffects:int}
 val header={version:2,versionTyped:true,faultFalse:true,serial:0,serialTyped:true,epoch:0,epochTyped:true,fieldsComplete:true,binding:1,directory:1,predecessor:1,countConsistent:true}
 var s:State
 def valid(h:Header):bool=h.version==2 and h.versionTyped and h.faultFalse and h.serial>=0 and h.serialTyped and h.epoch>=0 and h.epochTyped and h.fieldsComplete and h.binding==1 and h.directory==1 and h.predecessor==1 and h.countConsistent
 action init=s'={phase:0,fault:false,bytesNow:false,currentHeader:header,nativeEffects:0}
 action fire(e:Event):bool={val b={...s,bytesNow:false};s'=if(s.fault)b else match e {
 | Check(h)=>if(s.phase==0 and valid(h)){...b,phase:1,currentHeader:h} else {...b,fault:true}
 | Connect=>if(s.phase==1){...b,phase:2} else {...b,fault:true}
 | Reply=>if(s.phase==2){...b,phase:3} else {...b,fault:true}
 | Confirm(h)=>if(s.phase==3 and valid(h)){...b,phase:4,currentHeader:h} else {...b,fault:true}
 | Consume=>if(s.phase==4 and valid(s.currentHeader)){...b,phase:5,bytesNow:true} else {...b,fault:true}
 | Invalidate=>{...b,fault:true}
 }}
 val allProps=s.nativeEffects==0 and (s.bytesNow implies(s.phase==5 and not(s.fault) and valid(s.currentHeader)))
 action step={nondet good=Set(true,false).oneOf();nondet n=Set(0,1,2).oneOf();val h={...header,epoch:n,epochTyped:good,serialTyped:good,countConsistent:good};nondet e=Set(Check(h),Connect,Reply,Confirm(h),Consume,Invalidate).oneOf();fire(e)}
}

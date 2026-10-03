module current_dataset_shape {
 type Header={version:int,versionTyped:bool,faultFalse:bool,serial:int,serialTyped:bool,epoch:int,epochTyped:bool,fieldsComplete:bool,binding:int,bindingTyped:bool,directory:int,predecessor:int,countConsistent:bool}
 type Event=Check(Header)|Connect|Reply|Confirm(Header)|Consume|HistoricalProjection(Header)|Invalidate
 type State={phase:int,fault:bool,bytesNow:bool,currentHeader:Header,historicalShapeAccepted:bool,nativeEffects:int}
 val header={version:2,versionTyped:true,faultFalse:true,serial:0,serialTyped:true,epoch:0,epochTyped:true,fieldsComplete:true,binding:1,bindingTyped:true,directory:1,predecessor:1,countConsistent:true}
 var s:State
 def valid(h:Header):bool=h.version==2 and h.versionTyped and h.faultFalse and h.serial>=0 and h.serialTyped and h.epoch>=0 and h.epochTyped and h.fieldsComplete and h.binding==1 and h.bindingTyped and h.directory==1 and h.predecessor==1 and h.countConsistent
 action init=s'={phase:0,fault:false,bytesNow:false,currentHeader:header,historicalShapeAccepted:false,nativeEffects:0}
 action fire(e:Event):bool={val b={...s,bytesNow:false,historicalShapeAccepted:false};s'=if(s.fault)b else match e {
 | Check(h)=>if(s.phase==0 and valid(h)){...b,phase:1,currentHeader:h} else {...b,fault:true}
 | Connect=>if(s.phase==1){...b,phase:2} else {...b,fault:true}
 | Reply=>if(s.phase==2){...b,phase:3} else {...b,fault:true}
 | Confirm(h)=>if(s.phase==3 and valid(h)){...b,phase:4,currentHeader:h} else {...b,fault:true}
 | Consume=>if(s.phase==4 and valid(s.currentHeader)){...b,phase:5,bytesNow:true} else {...b,fault:true}
 | HistoricalProjection(h)=>if(valid(h)){...b,currentHeader:h,historicalShapeAccepted:true} else {...b,fault:true}
 | Invalidate=>{...b,fault:true}
 }}
 val allProps=(s.historicalShapeAccepted implies(not(s.fault) and valid(s.currentHeader))) and s.nativeEffects==0 and (s.bytesNow implies(s.phase==5 and not(s.fault) and valid(s.currentHeader)))
 action step={nondet good=Set(true,false).oneOf();nondet n=Set(0,1,2).oneOf();val h={...header,epoch:n,epochTyped:good,bindingTyped:good,serialTyped:good,countConsistent:good};nondet e=Set(Check(h),Connect,Reply,Confirm(h),Consume,HistoricalProjection(h),Invalidate).oneOf();fire(e)}
}

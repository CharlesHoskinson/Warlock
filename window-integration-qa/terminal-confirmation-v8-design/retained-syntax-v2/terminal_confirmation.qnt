module terminal_confirmation {
 type Failure=NoFailure|OwnerFailure|ModuleFailure|ServiceFailure|LedgerFailure|RetainedFailure|ActorFailure|SourceFailure|BatchFailure
 type Event=Observe(Failure)|Publish|Confirm(bool,bool,bool)|Return
 type State={observed:bool,rawOk:bool,rawBatch:bool,rawError:bool,disk:bool,confirmed:bool,confirmationOk:bool,confirmationError:bool,freshSource:bool,freshBatch:bool,current:bool,accepted:bool}
 var s:State
 action init=s'={observed:false,rawOk:false,rawBatch:false,rawError:false,disk:false,confirmed:false,confirmationOk:false,confirmationError:false,freshSource:false,freshBatch:false,current:false,accepted:false}
 action fire(e:Event):bool={s'=match e {
 |Observe(f)=>if(s.observed)s else {...s,observed:true,rawOk:f==NoFailure,rawBatch:f==NoFailure,rawError:f!=NoFailure}
 |Publish=>if(s.observed){...s,disk:true}else s
 |Confirm(source,batch,current)=>if(s.disk){...s,confirmed:true,freshSource:source,freshBatch:batch,current:current,confirmationOk:s.rawOk and s.rawBatch and source and batch and current,confirmationError:not(s.rawOk and s.rawBatch and source and batch and current)}else s
 |Return=>{...s,accepted:s.observed and s.rawOk and s.rawBatch and s.disk and s.confirmed and s.confirmationOk and s.freshSource and s.freshBatch and s.current and not(s.rawError) and not(s.confirmationError)}
 }}
 val allProps=all{
 s.accepted implies s.rawOk and s.rawBatch and s.disk and s.confirmed and s.freshSource and s.freshBatch and s.current and not(s.rawError) and not(s.confirmationError),
 s.confirmed and s.rawError implies s.confirmationError and not(s.confirmationOk),
 s.rawError implies not(s.accepted)
 }
 action step={nondet f=Set(NoFailure,OwnerFailure,ModuleFailure,ServiceFailure,LedgerFailure,RetainedFailure,ActorFailure,SourceFailure,BatchFailure).oneOf();nondet source=Set(true,false).oneOf();nondet batch=Set(true,false).oneOf();nondet current=Set(true,false).oneOf();nondet e=Set(Observe(f),Publish,Confirm(source,batch,current),Return).oneOf();fire(e)}
}

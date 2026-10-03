module close_identity {
 type Identity={epoch:int,pid:int}
 type Event=Record|QueueClose(Identity)|RunClose|UserUnsnap|Sync
 var live:Identity
 var record:Identity
 var queued:Identity
 var stored:bool
 var stale:bool
 var before:Identity
 var beforeStored:bool
 pure val NONE={epoch:0,pid:0}
 action init=all{live'={epoch:1,pid:10},record'={epoch:1,pid:10},queued'=NONE,stored'=true,stale'=false,before'=NONE,beforeStored'=false}
 action fire(e:Event):bool=all{
  before'=record,beforeStored'=stored,
  match e {
   | Record=>all{live'={epoch:live.epoch+1,pid:live.pid+1},record'={epoch:live.epoch+1,pid:live.pid+1},stored'=true,queued'=queued,stale'=false}
   | QueueClose(id)=>all{live'=live,record'=record,stored'=stored,queued'=id,stale'=false}
   | RunClose=>all{live'=live,record'=record,stored'=if(queued==record)false else stored,queued'=NONE,stale'=queued!=record}
   | UserUnsnap=>all{live'=live,record'=record,stored'=false,queued'=queued,stale'=false}
   | Sync=>all{live'=live,record'=record,stored'=(stored and record==live),queued'=queued,stale'=false}
  }
 }
 val staleClosePreservesNewRecord=stale implies (record==before and stored==beforeStored)
 action step={nondet e=Set(Record,QueueClose(live),QueueClose({epoch:live.epoch-1,pid:live.pid-1}),RunClose,UserUnsnap,Sync).oneOf();fire(e)}
}

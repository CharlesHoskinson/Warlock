module capture_finalization {
 type State={inode:int,finalized:bool,staged:int,returned:bool,returnWitness:bool,published:bool,publishWitness:bool,refused:bool}
 type Event=Finalize|Stage|OldStage|Mutation|Return|Publish
 var s:State
 action init=s'={inode:1,finalized:false,staged:0,returned:false,returnWitness:false,published:false,publishWitness:false,refused:false}
 action fire(e:Event):bool={s'=match e {
 | Finalize=>if(s.staged==0){...s,inode:s.inode+1,finalized:true}else {...s,refused:true}
 | Stage=>if(s.finalized and s.staged==0){...s,staged:s.inode}else {...s,refused:true}
 | OldStage=>{...s,staged:s.inode}
 | Mutation=>{...s,inode:s.inode+1}
 | Return=>if(s.finalized and s.staged==s.inode and not(s.refused)){...s,returned:true,returnWitness:true}else {...s,refused:true}
 | Publish=>if(s.returned and s.finalized and s.staged==s.inode and not(s.refused)){...s,published:true,publishWitness:true}else {...s,refused:true}
 }}
 val allProps=(s.staged>0 implies s.finalized) and (s.returned implies s.returnWitness) and (s.published implies s.returned and s.publishWitness)
 action step={nondet e=Set(Finalize,Stage,Mutation,Return,Publish).oneOf();fire(e)}
}

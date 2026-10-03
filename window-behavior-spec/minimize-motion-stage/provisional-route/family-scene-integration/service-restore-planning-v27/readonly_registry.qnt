module readonly_registry {
 type Row={id:int,closed:bool,refused:bool,published:bool}
 type Event=Begin({id:int,durable:bool})|Refuse(int)|Close(int)|Publish({id:int,durable:bool})|Return({id:int,connectionProof:bool})|Fail
 type State={rows:Set[Row],usable:Set[int],fault:bool}
 var s:State
 val capacity=4
 action init=s'={rows:Set(),usable:Set(),fault:false}
 pure def update(rows:Set[Row],row:Row):Set[Row]=rows.filter(r=>r.id!=row.id).union(Set(row))
 action fire(e:Event):bool=s'=match e {
 | Begin(p)=>if(not(s.fault) and p.id>0 and s.rows.size()<capacity and not(s.rows.exists(r=>r.id==p.id or r.refused and not(r.closed and r.published)))){if(p.durable){...s,rows:s.rows.union(Set({id:p.id,closed:false,refused:false,published:false}))} else {...s,fault:true,usable:Set()}} else s
 | Refuse(id)=>{...s,rows:s.rows.map(r=>if(r.id==id){...r,refused:true,published:false} else r),usable:s.usable.exclude(Set(id))}
 | Close(id)=>{...s,rows:s.rows.map(r=>if(r.id==id){...r,closed:true} else r)}
 | Publish(p)=>if(not(s.fault) and s.rows.exists(r=>r.id==p.id and r.closed)){if(p.durable){...s,rows:s.rows.map(r=>if(r.id==p.id){...r,published:true} else r)} else {...s,fault:true,usable:Set()}} else s
 | Return(p)=>if(not(s.fault) and p.connectionProof and s.rows.exists(r=>r.id==p.id and r.closed and r.published and not(r.refused))){...s,usable:s.usable.union(Set(p.id))} else {...s,usable:s.usable.exclude(Set(p.id))}
 | Fail=>{...s,fault:true,usable:Set()}
 }
 val allProps=s.rows.size()<=capacity and s.rows.map(r=>r.id).size()==s.rows.size() and (s.fault implies s.usable.size()==0) and s.usable.forall(id=>s.rows.exists(r=>r.id==id and r.closed and r.published and not(r.refused)))
 action step={nondet id=1.to(5).oneOf();nondet e=Set(Begin({id:id,durable:true}),Begin({id:id,durable:false}),Refuse(id),Close(id),Publish({id:id,durable:true}),Publish({id:id,durable:false}),Return({id:id,connectionProof:true}),Return({id:id,connectionProof:false}),Fail).oneOf();fire(e)}
}

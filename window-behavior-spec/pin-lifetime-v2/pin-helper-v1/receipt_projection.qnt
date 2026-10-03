module receipt_projection {
 type Field=Number(int)|Boolean(bool)|Text(str)|Null
 type Projection={pid:Field,floating:Field,pinned:Field}
 type Event=Complete({before:Projection,after:Projection,desired:Field})|Idle
 var accepted:bool
 var refused:bool
 var received:{before:Projection,after:Projection,desired:Field}
 pure val good={before:{pid:Number(1),floating:Boolean(false),pinned:Boolean(false)},after:{pid:Number(1),floating:Boolean(true),pinned:Boolean(true)},desired:Boolean(true)}
 pure def boolean(f:Field):bool=f==Boolean(true)or f==Boolean(false)
 pure def valid(r:{before:Projection,after:Projection,desired:Field}):bool=
  r.before.pid==Number(1)and r.after.pid==Number(1)and boolean(r.before.floating)and
  boolean(r.before.pinned)and r.after.floating==Boolean(true)and boolean(r.desired)and
  r.after.pinned==r.desired and r.before.pinned!=r.desired
 action init=all{accepted'=false,refused'=false,received'=good}
 action fire(e:Event):bool=match e{
  |Complete(r)=>all{received'=r,accepted'=(not(refused)and valid(r)),refused'=(refused or not(valid(r)))}
  |Idle=>all{received'=received,accepted'=accepted,refused'=refused}
 }
 val allProps=accepted implies valid(received)and not(refused)
 action step={nondet f=Set(Number(1),Number(0),Boolean(true),Boolean(false),Null,Text("1")).oneOf();nondet e=Set(Complete(good),Complete({...good,before:{...good.before,pid:f}}),Complete({...good,before:{...good.before,floating:f}}),Complete({...good,after:{...good.after,pinned:f}}),Complete({...good,desired:f}),Idle).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),accepted'=accepted,refused'=refused,received'=received}
 run actualIntegerPidTest=init.then(fire(Complete(good))).then(check(accepted))
 run booleanCannotAliasIntegerPidTest=init.then(fire(Complete({...good,before:{...good.before,pid:Boolean(true)}}))).then(check(refused and not(accepted)))
 run nullFloatingCannotCompleteTest=init.then(fire(Complete({...good,before:{...good.before,floating:Null}}))).then(check(refused and not(accepted)))
 run booleanBeforeFloatingCanBeFalseTest=init.then(fire(Complete(good))).then(check(accepted))
 run booleanBeforeFloatingCanBeTrueTest=init.then(fire(Complete({...good,before:{...good.before,floating:Boolean(true)}}))).then(check(accepted))
 run numericPinCannotAliasBooleanTest=init.then(fire(Complete({...good,after:{...good.after,pinned:Number(1)}}))).then(check(refused and not(accepted)))
 run pinMustActuallyToggleTest=init.then(fire(Complete({...good,before:{...good.before,pinned:Boolean(true)}}))).then(check(refused and not(accepted)))
 run malformedReceiptCannotBeClearedTest=init.then(fire(Complete({...good,before:{...good.before,floating:Null}}))).then(fire(Complete(good))).then(check(refused and not(accepted)))
}

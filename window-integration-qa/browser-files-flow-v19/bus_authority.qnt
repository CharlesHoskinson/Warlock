module bus_authority {
 type Proof={preExecSelectors:bool,sameExec:bool,sameLifetime:bool,ownedScope:bool,privateDaemon:bool,sameSocket:bool,realClientPid:bool,realClientUid:bool}
 var observed:Proof
 var accepted:bool
 pure val blank={preExecSelectors:false,sameExec:false,sameLifetime:false,ownedScope:false,privateDaemon:false,sameSocket:false,realClientPid:false,realClientUid:false}
 pure def authority(p:Proof):bool=p.preExecSelectors and p.sameExec and p.sameLifetime and p.ownedScope and p.privateDaemon and p.sameSocket and p.realClientPid and p.realClientUid
 action init=all{observed'=blank,accepted'=false}
 action observe(p:Proof):bool=all{observed'=p,accepted'=authority(p)}
 val allProps=accepted implies authority(observed)
 action step={
  nondet pre=Bool.oneOf();nondet exe=Bool.oneOf();nondet life=Bool.oneOf();nondet scope=Bool.oneOf();nondet daemon=Bool.oneOf();nondet sock=Bool.oneOf();nondet pid=Bool.oneOf();nondet uid=Bool.oneOf()
  observe({preExecSelectors:pre,sameExec:exe,sameLifetime:life,ownedScope:scope,privateDaemon:daemon,sameSocket:sock,realClientPid:pid,realClientUid:uid})
 }
}

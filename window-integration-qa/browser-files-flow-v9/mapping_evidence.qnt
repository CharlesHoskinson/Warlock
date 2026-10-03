module mapping_evidence {
 var captured: bool
 var persisted: bool
 var accepted: bool
 var checked: bool
 var readable: bool
 var sameLifetime: bool
 var authorized: bool
 action init = all {captured'=false,persisted'=false,accepted'=false,checked'=false,readable'=false,sameLifetime'=false,authorized'=false}
 action capture(read:bool,live:bool,auth:bool): bool = all {captured'=true,persisted'=false,accepted'=false,checked'=false,readable'=read,sameLifetime'=live,authorized'=auth}
 action save = all {captured, persisted'=true, captured'=captured,accepted'=accepted,checked'=checked,readable'=readable,sameLifetime'=sameLifetime,authorized'=authorized}
 action validate = all {captured,persisted,checked'=true,accepted'=(readable and sameLifetime and authorized),captured'=captured,persisted'=persisted,readable'=readable,sameLifetime'=sameLifetime,authorized'=authorized}
 val capturedBeforeCheck = checked implies captured and persisted
 val exactAuthority = accepted implies readable and sameLifetime and authorized and persisted
 val failureRetained = checked and not(accepted) implies captured and persisted
 val allProps = capturedBeforeCheck and exactAuthority and failureRetained
 action step = any {
  {nondet read=Bool.oneOf();nondet live=Bool.oneOf();nondet auth=Bool.oneOf();capture(read,live,auth)},
  save,validate
 }
}

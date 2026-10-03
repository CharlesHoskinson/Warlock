module runtime_authority {
 type Mapping = {owned: bool, frozen: bool, sameBytes: bool, sameMode: bool, deleted: bool, runtime: bool, cache: bool, executable: bool, regular: bool}
 var accepted: bool
 var observed: Mapping
 pure val blank = {owned:false, frozen:false, sameBytes:false, sameMode:false, deleted:false, runtime:false, cache:false, executable:false, regular:false}
 pure def authority(m: Mapping): bool = m.owned and m.regular and not(m.deleted) and
   (if(m.runtime) m.cache and not(m.executable) else m.frozen and m.sameBytes and m.sameMode)
 action init = all { observed'=blank, accepted'=false }
 action observe(m: Mapping): bool = all { observed'=m, accepted'=authority(m) }
 val noRuntimeExecution = accepted and observed.runtime implies observed.cache and not(observed.executable)
 val exactExternal = accepted and not(observed.runtime) implies observed.frozen and observed.sameBytes and observed.sameMode
 val ownedRegularLive = accepted implies observed.owned and observed.regular and not(observed.deleted)
 val allProps = noRuntimeExecution and exactExternal and ownedRegularLive
 action step = {
  nondet own=Bool.oneOf(); nondet frozen=Bool.oneOf(); nondet bytes=Bool.oneOf(); nondet mode=Bool.oneOf()
  nondet deleted=Bool.oneOf(); nondet runtime=Bool.oneOf(); nondet cache=Bool.oneOf(); nondet executable=Bool.oneOf(); nondet regular=Bool.oneOf()
  observe({owned:own,frozen:frozen,sameBytes:bytes,sameMode:mode,deleted:deleted,runtime:runtime,cache:cache,executable:executable,regular:regular})
 }
}

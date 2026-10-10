module ShortcutChoices {
 var fingerprint: int
 var expected: int
 var conflict: bool
 var foreign: int
 var owned: bool
 var phase: str
 var submissions: int
 action init = all {fingerprint'=1,expected'=1,conflict'=false,foreign'=1,owned'=false,phase'="idle",submissions'=0}
 action verify(condition: bool): bool = all {assert(condition),fingerprint'=fingerprint,expected'=expected,conflict'=conflict,foreign'=foreign,owned'=owned,phase'=phase,submissions'=submissions}
 action submit = all {phase=="idle",not(conflict),expected'=fingerprint,phase'="pending",submissions'=submissions+1,fingerprint'=fingerprint,conflict'=conflict,foreign'=foreign,owned'=owned}
 action change = all {fingerprint'=fingerprint+1,conflict'=true,expected'=expected,foreign'=foreign,owned'=owned,phase'=phase,submissions'=submissions}
 action apply = all {phase=="pending",fingerprint==expected,not(conflict),owned'=true,phase'="idle",fingerprint'=fingerprint,expected'=expected,conflict'=conflict,foreign'=foreign,submissions'=submissions}
 action refuse = all {phase=="pending",any {fingerprint!=expected,conflict},owned'=owned,phase'="idle",fingerprint'=fingerprint,expected'=expected,conflict'=conflict,foreign'=foreign,submissions'=submissions}
 action loseReceipt = all {phase=="pending",phase'="unknown",owned'=owned,fingerprint'=fingerprint,expected'=expected,conflict'=conflict,foreign'=foreign,submissions'=submissions}
 action read = all {phase=="unknown",phase'="idle",owned'=owned,fingerprint'=fingerprint,expected'=expected,conflict'=conflict,foreign'=foreign,submissions'=submissions}
 action step = any {submit,change,apply,refuse,loseReceipt,read}
 val safety = foreign==1 and submissions>=0
 run exactApplyPreservesForeignTest = init.then(submit).then(apply).then(verify(owned and foreign==1 and submissions==1))
 run changedFingerprintRefusesTest = init.then(submit).then(change).then(refuse).then(verify(not(owned) and foreign==1))
 run unknownCannotSubmitTest = init.then(submit).then(loseReceipt).then(verify(phase=="unknown" and submissions==1)).then(read).then(verify(submissions==1 and not(owned)))
}

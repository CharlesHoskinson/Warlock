module layerAppearance {
  // UX-030 + WARLOCK-LAYER-010. Flags 0..3 abstract two Boolean preferences.
  // One bounded transaction projection; no native pixels, deadlines or transport refinement.
  var s: {stored:int, applied:int, draft:int, nativeRevision:int, knownRevision:int, expected:int, phase:str, request:int, writes:int, confirmed:int}
  pure val flags = Set(0,1,2,3)
  val canSave = s.phase=="idle" and s.draft!=s.applied
  action init = s'={stored:0,applied:0,draft:0,nativeRevision:1,knownRevision:1,expected:0,phase:"idle",request:0,writes:0,confirmed:0}
  action edit(value:int):bool = all {s.phase=="idle",flags.contains(value),s'={...s,draft:value}}
  action save = all {canSave,s'={...s,phase:"pending",expected:s.knownRevision,request:s.request+1,writes:s.writes+1}}
  action delivered = all {s.phase=="pending",s.expected==s.nativeRevision,s'={...s,stored:s.draft,applied:s.draft,confirmed:s.draft,nativeRevision:s.nativeRevision+1,knownRevision:s.nativeRevision+1,phase:"idle"}}
  action lost = all {s.phase=="pending",s.expected==s.nativeRevision,s'={...s,stored:s.draft,nativeRevision:s.nativeRevision+1,phase:"unknown"}}
  action compete = all {s.phase=="pending",s'={...s,stored:3,nativeRevision:s.nativeRevision+1}}
  action refuse = all {s.phase=="pending",s.expected!=s.nativeRevision,s'={...s,phase:"idle"}}
  action refresh = all {s.phase!="pending",s'={...s,applied:s.stored,confirmed:s.stored,draft:s.stored,knownRevision:s.nativeRevision,phase:"idle"}}
  action staleReceipt = s'=s
  action step = any {edit(0),edit(1),edit(2),edit(3),save,delivered,lost,compete,refuse,refresh,staleReceipt}
  val safety = flags.contains(s.stored) and flags.contains(s.applied) and flags.contains(s.draft) and s.applied==s.confirmed and s.writes==s.request and s.knownRevision<=s.nativeRevision
  val bothCommitted = s.applied==3 and s.phase=="idle" and s.writes>0
  val unknownHeld = s.phase=="unknown" and s.applied!=s.stored and not(canSave)
  val staleRefused = s.phase=="idle" and s.nativeRevision>s.knownRevision and s.writes>0
}

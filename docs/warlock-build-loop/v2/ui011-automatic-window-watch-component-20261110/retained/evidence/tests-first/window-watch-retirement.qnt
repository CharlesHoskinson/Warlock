module window_watch_retirement {
  // Finite source correspondence, not a native/AT or IO qualification.
  // A timer schedules a current authenticated read; it does not reset D.
  var s: { live: bool, capability: bool, open: bool, keyboard: bool,
    currentScope: bool, fallback: bool, pending: int, next: int,
    observedOrigin: int, realOrigin: int, observedContent: int, realContent: int,
    revision: int, publication: int, lease: int, menu: int,
    scheduled: bool, delivered: Set[int], violations: int }
  action init = s' = { live:true, capability:true, open:true, keyboard:true,
    currentScope:true, fallback:true, pending:0, next:1,
    observedOrigin:1, realOrigin:1, observedContent:1, realContent:1,
    revision:1, publication:1, lease:1, menu:1,
    scheduled:true, delivered:Set(), violations:0 }
  action tick = if (s.live and s.capability and s.open and s.keyboard and s.currentScope
    and s.scheduled and s.pending==0 and s.next<=8) {
    s' = {...s, pending:s.next, next:s.next+1, scheduled:false}
  } else s'=s
  action closeOrigin = s' = {...s, realOrigin:0, realContent:s.realContent+1}
  action replaceOrigin = s' = {...s, realOrigin:2, realContent:s.realContent+1}
  action harmlessMetadata = s' = {...s, realContent:s.realContent+1}
  action deliverCurrent = if (s.pending>0 and s.live and s.capability and s.open and s.currentScope) {
    if (s.realOrigin==s.observedOrigin and s.realContent==s.observedContent) {
      s' = {...s, pending:0, scheduled:true}
    } else if (s.realOrigin==s.observedOrigin) {
      s' = {...s, pending:0, scheduled:true, observedContent:s.realContent,
        revision:s.revision+1, publication:s.publication+1}
    } else {
      s' = {...s, pending:0, scheduled:false, open:false,
        observedOrigin:s.realOrigin, observedContent:s.realContent,
        revision:s.revision+1, publication:s.publication+1,
        delivered:if (s.keyboard and s.fallback) s.delivered.union(Set(s.menu)) else s.delivered,
        violations:s.violations+(if (s.keyboard and s.fallback and s.delivered.contains(s.menu)) 1 else 0)}
    }
  } else s'=s
  action staleOrForeign = s'=s
  action counterOnlyChanged = s'=s
  action unknown = s'={...s,pending:0,scheduled:false,capability:false}
  action scopeClose = s'={...s,open:false,pending:0,scheduled:false}
  action supersede = s'={...s,currentScope:false,pending:0,scheduled:false}
  action expire = s'={...s,live:false,pending:0,scheduled:false}
  action noFallback = s'={...s,fallback:false}
  action pointer = s'={...s,keyboard:false,scheduled:false}
  action absentCapability = s'={...s,capability:false,scheduled:false}
  action step = any {tick,closeOrigin,replaceOrigin,harmlessMetadata,deliverCurrent,
    staleOrForeign,counterOnlyChanged,unknown,scopeClose,supersede,expire,noFallback}
  val safety = s.violations==0 and s.pending>=0 and s.pending<s.next
    and (s.pending==0 or (s.live and s.capability and s.open and s.currentScope))
  run unchangedKeepsScopeTest = init.then(tick).then(deliverCurrent).then(all {
    assert(s.open and s.menu==1 and s.lease==1 and s.publication==1 and s.revision==1 and s.delivered==Set()), s'=s })
  run closureReturnsFallbackOnceTest = init.then(tick).then(closeOrigin).then(deliverCurrent).then(deliverCurrent).then(all {
    assert(not(s.open) and s.delivered==Set(1) and s.violations==0), s'=s })
  run replacementNeverReceivesOldFocusTest = init.then(tick).then(replaceOrigin).then(deliverCurrent).then(all {
    assert(s.observedOrigin==2 and s.delivered==Set(1) and not(s.open)), s'=s })
  run harmlessMetadataPreservesMenuTest = init.then(tick).then(harmlessMetadata).then(deliverCurrent).then(all {
    assert(s.open and s.menu==1 and s.lease==1 and s.delivered==Set() and s.scheduled), s'=s })
  run counterAloneNeverClosesTest = init.then(tick).then(counterOnlyChanged).then(all {assert(s.open and s.delivered==Set()),s'=s})
  run expiredReplyCannotRestoreTest = init.then(tick).then(closeOrigin).then(expire).then(deliverCurrent).then(all {assert(s.delivered==Set()),s'=s})
  run supersededReplyCannotRestoreTest = init.then(tick).then(closeOrigin).then(supersede).then(deliverCurrent).then(all {assert(s.delivered==Set()),s'=s})
  run unknownNeverGrantsFallbackTest = init.then(tick).then(closeOrigin).then(unknown).then(deliverCurrent).then(all {assert(s.delivered==Set() and not(s.scheduled)),s'=s})
  run closedScopeIgnoresLateResultTest = init.then(tick).then(scopeClose).then(closeOrigin).then(deliverCurrent).then(all {assert(s.delivered==Set()),s'=s})
  run noEligibleFallbackNoFocusTest = init.then(tick).then(noFallback).then(closeOrigin).then(deliverCurrent).then(all {assert(s.delivered==Set()),s'=s})
  run pointerDoesNotArmTest = init.then(pointer).then(tick).then(all {assert(s.pending==0 and s.delivered==Set()),s'=s})
  run absentCapabilityDoesNotArmTest = init.then(absentCapability).then(tick).then(all {assert(s.pending==0),s'=s})
  run duplicateTickOneRequestTest = init.then(tick).then(tick).then(all {assert(s.pending==1 and s.next==2),s'=s})
}

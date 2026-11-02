// Finite abstraction of Sol Store acquisition/retirement v3 bdaa2f8b:
// runtime/src/Warlock/Backend/Store.hsc post 8a46bb60ec5815df1aced28ec8b24c0ebf52de7e8daecc008fb49ef56178a68d.
// runOwned uses a same-owner gate; tracked publishes Acquiring BEFORE acquire;
// only NotAcquired establishes Closed without a close. A successful value is
// stored before Open; exception or failed value publication leaves Acquiring.
// closeResource owns a single Open->Closing attempt, then Closed or Uncertain.
// retireStoreOwnerIfSettled uses tryTakeMVar, seals on any acquired scan, and
// observes rather than closes. Separate legacy retireStoreOwner is not modeled.
// Two fixed, single-use resource slots model nested acquisitions; actual
// resource lists are unbounded over time and filter Closed entries. A slot is
// never reused here. Busy probe is a failed attempt, NOT a retirement seal.
// endRun while Closing is a conservative overapprox of masked close unwind.
// possibleOwned is independent ghost evidence: a successful raw acquire or
// an ambiguous acquisition failure may have produced a resource even when no
// value was published. Successful modeled close clears it. This is a safety
// abstraction, not observed FD identity, physical close, timing or StopD.
module store_retirement {
  type Phase = Absent | Acquiring | Open | Closing | Closed | Uncertain
  type Gate = Free | Busy | Sealed
  type Observation = None | BusyRefusal | Settled | Unsettled | ScanThrew
  type Resource = {phase:Phase, retained:bool, possibleOwned:bool, failed:bool, noResource:bool,
    closeAttempts:int, closeConfirmed:bool}
  type State = {gate:Gate, r1:Resource, r2:Resource, observation:Observation}
  var s:State
  pure val empty:Resource = {phase:Absent,retained:false,possibleOwned:false,failed:false,
    noResource:false,closeAttempts:0,closeConfirmed:false}
  pure def selected(st:State,i:int):Resource = if(i==1) st.r1 else st.r2
  pure def setResource(st:State,i:int,r:Resource):State =
    if(i==1) {...st,r1:r} else {...st,r2:r}
  pure def isSettled(r:Resource):bool = r.phase==Absent or r.phase==Closed
  pure def clean(st:State):bool = isSettled(st.r1) and isSettled(st.r2)
  action init:bool = s'={gate:Free,r1:empty,r2:empty,observation:None}
  action begin:bool = all {s.gate==Free,s'={...s,gate:Busy,observation:None}}
  // Published record exists before invoking acquire.
  action register(i:int):bool = all {s.gate==Busy,(i==1 or i==2),selected(s,i).phase==Absent,
    s'=setResource(s,i,{...selected(s,i),phase:Acquiring})}
  // Explicit source-proven negative receipt; not an exception-name guess.
  action notAcquired(i:int):bool = all {s.gate==Busy,(i==1 or i==2),
    selected(s,i).phase==Acquiring,not(selected(s,i).failed),not(selected(s,i).retained),
    not(selected(s,i).possibleOwned),
    s'=setResource(s,i,{...selected(s,i),phase:Closed,noResource:true})}
  // Independent raw acquisition can succeed before value publication.
  action acquireRaw(i:int):bool = all {s.gate==Busy,(i==1 or i==2),
    selected(s,i).phase==Acquiring,not(selected(s,i).failed),not(selected(s,i).possibleOwned),
    s'=setResource(s,i,{...selected(s,i),possibleOwned:true})}
  action retainValue(i:int):bool = all {s.gate==Busy,(i==1 or i==2),
    selected(s,i).phase==Acquiring,selected(s,i).possibleOwned,not(selected(s,i).failed),not(selected(s,i).retained),
    s'=setResource(s,i,{...selected(s,i),retained:true})}
  action markOpen(i:int):bool = all {s.gate==Busy,(i==1 or i==2),
    selected(s,i).phase==Acquiring,selected(s,i).retained,not(selected(s,i).failed),
    s'=setResource(s,i,{...selected(s,i),phase:Open})}
  // Covers acquisition exception and failed publication before or after value
  // retention. Aborting leaves the record Acquiring, never fabricates Closed.
  action acquisitionUnknown(i:int,mayOwn:bool):bool = all {s.gate==Busy,(i==1 or i==2),
    selected(s,i).phase==Acquiring,not(selected(s,i).failed),
    s'=setResource(s,i,{...selected(s,i),failed:true,possibleOwned:selected(s,i).possibleOwned or mayOwn})}
  action closeBegin(i:int):bool = all {s.gate==Busy,(i==1 or i==2),selected(s,i).phase==Open,
    s'=setResource(s,i,{...selected(s,i),phase:Closing,closeAttempts:selected(s,i).closeAttempts+1})}
  action closeSuccess(i:int):bool = all {s.gate==Busy,(i==1 or i==2),selected(s,i).phase==Closing,
    s'=setResource(s,i,{...selected(s,i),phase:Closed,closeConfirmed:true,possibleOwned:false})}
  action closeUnknown(i:int):bool = all {s.gate==Busy,(i==1 or i==2),selected(s,i).phase==Closing,
    s'=setResource(s,i,{...selected(s,i),phase:Uncertain})}
  // After action/error unwinds, any non-Closed resource poisons runOwned.
  action endRun:bool = all {s.gate==Busy,
    s'={...s,gate:if(clean(s)) Free else Sealed}}
  action probeBusy:bool = all {s.gate==Busy,s'={...s,observation:BusyRefusal}}
  // Acquiring the same gate seals even when rows are unsettled. Empty list is
  // vacuously settled; exceptions during scan also seal and do not claim clean.
  action sealScan:bool = all {s.gate!=Busy,
    s'={...s,gate:Sealed,observation:if(clean(s)) Settled else Unsettled}}
  action scanException:bool = all {s.gate!=Busy,s'={...s,gate:Sealed,observation:ScanThrew}}
  action step:bool = any {begin,register(1),register(2),notAcquired(1),notAcquired(2),
    acquireRaw(1),acquireRaw(2),retainValue(1),retainValue(2),markOpen(1),markOpen(2),
    acquisitionUnknown(1,true),acquisitionUnknown(1,false),acquisitionUnknown(2,true),acquisitionUnknown(2,false),
    closeBegin(1),closeBegin(2),closeSuccess(1),closeSuccess(2),closeUnknown(1),closeUnknown(2),
    endRun,probeBusy,sealScan,scanException}
  pure def resourceSafe(r:Resource):bool = all {r.closeAttempts<=1,
    (r.phase==Open or r.phase==Closing or r.phase==Uncertain) implies r.retained,
    (r.phase==Closed) implies (r.noResource or r.closeConfirmed),
    (r.phase==Closed) implies not(r.possibleOwned),
    (r.phase==Open or r.phase==Closing or r.phase==Uncertain) implies r.possibleOwned,
    r.noResource implies (not(r.retained) and r.closeAttempts==0),
    r.closeConfirmed implies (r.retained and r.closeAttempts==1),
    r.failed implies r.phase==Acquiring}
  val safety = resourceSafe(s.r1) and resourceSafe(s.r2) and
    (s.observation==Settled implies s.gate==Sealed and clean(s) and
      not(s.r1.possibleOwned) and not(s.r2.possibleOwned))
  val witnessTwoClosed = s.r1.closeConfirmed and s.r2.closeConfirmed and s.observation==Settled
  val witnessBusy = s.gate==Busy and s.observation==BusyRefusal
  val witnessUnknown = s.gate==Sealed and (s.r1.phase==Uncertain or s.r2.phase==Uncertain)
  val witnessUnconfirmedAcquire = s.gate==Sealed and s.r1.phase==Acquiring and s.r1.failed and s.r1.possibleOwned
}

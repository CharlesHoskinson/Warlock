// ELM-UI-020 offline-recovery, ARCHITECTURE.md packaged preference copies.
// One recovery manager coordinates local files through an exclusive profile
// lock. No host messages, network, window effects or implicit restart.
// Atomic grain: staging is private; selection publication is one rename.
// Filesystem/hash validation and native presentation need real-code evidence.
module offline_recovery {
  type Route = Predecessor | Candidate
  type Host = NoHost | PredecessorHost | CandidateHost
  type Phase = Idle | Staged | Applied | Unknown
  type Preferences = Compatible | CandidateValues
  type State = {route:Route, host:Host, phase:Phase, preferences:Preferences,
    priorValid:bool, candidateValid:bool, generation:int, rollbacks:int,
    starts:int, recovered:bool}
  var s:State
  action init = s'={route:Predecessor,host:NoHost,phase:Idle,
    preferences:Compatible,priorValid:true,candidateValid:true,
    generation:1,rollbacks:0,starts:0,recovered:false}
  pure def canStart(st:State):bool = st.host==NoHost and
    st.phase!=Staged and st.phase!=Unknown and
    (if(st.route==Predecessor) st.priorValid else st.candidateValid)
  pure def start(st:State):State = {...st,
    host:if(st.route==Predecessor) PredecessorHost else CandidateHost,
    starts:st.starts+1}
  action startSelected = all {canStart(s),s'=start(s)}
  action hostExit = all {s.host!=NoHost,s'={...s,host:NoHost}}
  action activate = all {s.host==NoHost,s.phase!=Staged,
    s.phase!=Unknown,s.route==Predecessor,s.candidateValid,s.priorValid,
    s'={...s,route:Candidate,preferences:CandidateValues,recovered:false,
      phase:Idle,generation:s.generation+1}}
  pure def canStage(st:State):bool = st.host==NoHost and
    st.route==Candidate and st.priorValid and st.phase==Idle
  action stageRollback = all {canStage(s),s'={...s,phase:Staged}}
  pure def commit(st:State,result:Phase):State = {...st,route:Predecessor,
    preferences:Compatible,phase:result,generation:st.generation+1,
    rollbacks:st.rollbacks+1,recovered:true}
  action commitRollback(result:Phase):bool = all {s.phase==Staged,
    Set(Applied,Unknown).contains(result),s'=commit(s,result)}
  action crashBeforeCommit = all {s.phase==Staged,s'={...s,phase:Idle}}
  action observe = all {s.phase==Unknown,s'={...s,phase:Applied}}
  action damageCandidate = all {s.candidateValid,s'={...s,candidateValid:false}}
  action damagePrior = all {s.priorValid,s.phase!=Staged,
    s'={...s,priorValid:false}}
  val safety = (s.host!=PredecessorHost or s.route==Predecessor) and
    (s.host!=CandidateHost or s.route==Candidate) and
    (not(s.recovered) or s.preferences==Compatible)
  val predecessorStarted = s.host==PredecessorHost and s.starts>0
  val failedHostRecovered = s.recovered and s.host==PredecessorHost
  val damagedCandidateRecovered = s.recovered and not(s.candidateValid)
  val uncertainSelectionObserved = s.phase==Unknown and s.recovered
  val stagingCrashRetainsCandidate = s.generation==2 and s.route==Candidate
    and s.phase==Idle and s.rollbacks==0 and s.starts>0
  action step = any {startSelected,hostExit,activate,stageRollback,
    commitRollback(Applied),commitRollback(Unknown),crashBeforeCommit,
    observe,damageCandidate,damagePrior}
}

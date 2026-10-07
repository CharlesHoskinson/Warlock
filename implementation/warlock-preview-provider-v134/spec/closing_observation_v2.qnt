module closing_observation_v2 {
 // Original duties settlement includes independent physical/journal/confirmation
 // settlement. It is never inferred from popup readiness or an empty job list.
 type State={popup:bool,closing:bool,reader:bool,jobs:bool,dutiesSettled:bool,observed:bool,detached:bool,unknown:bool,pollStamp:int}
 var s:State
 action init=s'={popup:true,closing:false,reader:true,jobs:true,dutiesSettled:false,observed:false,detached:false,unknown:false,pollStamp:1}
 action close=s'={...s,popup:false,closing:true}
 action reopen=s'={...s,popup:true}
 action release=s'={...s,reader:false}
 action physicalDone=if(not(s.reader))s'={...s,jobs:false}else s'=s
 action independentDrain=if(s.closing and not(s.reader) and not(s.jobs) and not(s.unknown))s'={...s,dutiesSettled:true}else s'=s
 action fault=s'={...s,unknown:true}
 pure def producer(st:State,sticky:bool):State={
  val observes=st.closing and (sticky or not(st.popup)) and not(st.unknown);
  {...st,pollStamp:if(st.closing and sticky)0 else if(st.popup)1 else 0,observed:st.observed or observes,detached:st.detached or (observes and st.dutiesSettled)}
 }
 action pulse(sticky:bool):bool=s'=producer(s,sticky)
 action step=any{close,reopen,release,physicalDone,independentDrain,fault,pulse(true)}
 val safety=all{s.detached implies (s.closing and not(s.reader) and not(s.jobs) and s.dutiesSettled),s.dutiesSettled implies (not(s.reader) and not(s.jobs))}
}

// ELM-UI-004 explicit New instance; ELM-UI-008 labeled menu invocation.
// One Elm reducer; callbacks and catalog/receipt changes are atomic inputs.
// Models selection/duplicate/no-replay policy, not GIO, native input, grants,
// custody, AT, pixels, transport timing or UInt64 exhaustion.
module new_instance {
  type Phase = Idle | Pending | Submitted | Refused | Unknown
  type Origin = WindowMenu | ApplicationActions | Closed
  type State = {phase:Phase, origin:Origin, stamp:int, generation:int,
    identity:int, matches:int, ready:bool, launches:int, windowEffects:int,
    request:int, issuedGeneration:int, issuedIdentity:int}
  var s:State
  action init = s'={phase:Idle,origin:WindowMenu,stamp:1,generation:1,
    identity:1,matches:1,ready:true,launches:0,windowEffects:0,
    request:0,issuedGeneration:0,issuedIdentity:0}
  val safety = s.launches==s.request and s.launches>=0 and
    (s.phase!=Pending or s.origin==Closed)
  pure def canLaunch(st:State,stamp:int,id:int):bool =
    st.stamp==stamp and st.identity==id and id>0 and st.ready and
    (st.origin==ApplicationActions or
      (st.origin==WindowMenu and st.matches==1)) and
    st.phase!=Pending and st.phase!=Unknown
  pure def launch(st:State):State = {...st,phase:Pending,origin:Closed,
    stamp:st.stamp+1,launches:st.launches+1,request:st.request+1,
    issuedGeneration:st.generation,issuedIdentity:st.identity}
  action explicit(stamp:int,id:int):bool =
    s'=if(canLaunch(s,stamp,id)) launch(s) else s
  action ordinaryPrimary = s'=if(s.ready)
    {...s,windowEffects:s.windowEffects+1} else s
  action open(origin:Origin):bool = all {s.phase!=Pending,
    s'={...s,origin:origin,stamp:s.stamp+1}}
  action catalog(id:int,matches:int):bool = s'={...s,identity:id,
    matches:matches,generation:s.generation+1,stamp:s.stamp+1,
    phase:if(s.phase==Submitted or s.phase==Refused) Idle else s.phase}
  action unavailable = s'={...s,ready:false,stamp:s.stamp+1}
  action receipt(request:int,result:Phase):bool =
    s'=if(s.phase==Pending and s.request==request and
      Set(Submitted,Refused,Unknown).contains(result))
      {...s,phase:result,stamp:s.stamp+1} else s
  val windowMenuLaunch = s.launches>0 and s.issuedIdentity==1 and s.issuedGeneration==1
  val applicationActionsLaunch = s.launches>0 and s.issuedIdentity==2
  val ordinaryWithoutLaunch = s.windowEffects>0 and s.launches==0
  val unknownRetained = s.phase==Unknown and s.launches>0
  action step = any {explicit(s.stamp,s.identity),explicit(s.stamp-1,s.identity),
    explicit(s.stamp,s.identity+1),ordinaryPrimary,open(WindowMenu),
    open(ApplicationActions),catalog(1,1),catalog(2,1),catalog(1,2),catalog(0,0),
    unavailable,receipt(s.request,Submitted),receipt(s.request,Refused),
    receipt(s.request,Unknown),receipt(s.request-1,Submitted),s'=s}
}

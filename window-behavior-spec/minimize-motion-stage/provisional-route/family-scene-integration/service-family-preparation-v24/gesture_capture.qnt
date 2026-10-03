module gesture_capture {
 type State={receipt:int,worker:int,phase:str,capable:bool,scope:Set[int],fresh:Set[int],retired:Set[int],captured:Set[int],currentGeometry:int,sourceGeometry:int}
 var s:State
 action init=s'={receipt:1,worker:1,phase:"observed",capable:true,scope:Set(0,1,2),fresh:Set(0,1,2),retired:Set(),captured:Set(),currentGeometry:5,sourceGeometry:-1}
 action newer=s'={...s,receipt:s.receipt+1}
 action reserve=all{s.worker==s.receipt,s.fresh==s.scope,s'={...s,phase:"reserved"}}
 action retire(n:int):bool=all{s.phase=="reserved",s.worker==s.receipt,s.capable,s.scope.contains(n),s'={...s,retired:s.retired.union(Set(n)),currentGeometry:7}}
 action refusal=all{s.phase=="observed" or s.phase=="reserved",s'={...s,phase:"failed"}}
 action replace=s'={...s,fresh:Set(0,1,3)}
 action unavailable=s'={...s,capable:false}
 action refresh=all{s.phase=="reserved",s.worker==s.receipt,s.retired==s.scope,s.fresh==s.scope,s'={...s,phase:"refreshed"}}
 action capture(n:int):bool=all{s.phase=="refreshed",s.worker==s.receipt,s.scope.contains(n),s'={...s,captured:s.captured.union(Set(n)),sourceGeometry:s.currentGeometry}}
 val captureAfterWholeRetirement=s.captured.size()==0 or s.retired==s.scope
 val captureUsesCurrentGeometry=s.captured.size()==0 or s.sourceGeometry==s.currentGeometry
 val noCaptureAfterRefusal=if(s.phase=="failed") s.captured.size()==0 else true
 val allProps=captureAfterWholeRetirement and captureUsesCurrentGeometry and noCaptureAfterRefusal
 action step={nondet n=0.to(3).oneOf();any{newer,reserve,retire(n),refusal,replace,unavailable,refresh,capture(n)}}
}

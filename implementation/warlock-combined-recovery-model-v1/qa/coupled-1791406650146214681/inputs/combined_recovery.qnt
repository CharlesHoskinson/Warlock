module combined_recovery {
 type State={reader:bool,closing:bool,closed:bool,previewUnknown:bool,rendererFailed:bool,recovery:bool,host:int,lifetime:int,admitted:bool,nativeWindowCommitted:bool,oldUnknown:bool,historyUnknown:bool,scene:bool,bindingRetired:bool,reservationReleased:bool,request:int,generation:int,newCommand:bool,replays:int,freshPreview:bool,freshOwner:int,freshReader:bool,freshClosed:bool}
 type Event=ClosePreview|AdmitWindow|NativeWindowCommit|LoseReceipt|RendererFailure|CloseReader|NativeStrictClose|Recovery|Restart|Scene|WindowBindingRetired|ReleaseReservation|ExplicitNewCommand|RetryOldWindow|FreshCapture|CloseFreshReader|FreshStrictClose|PreviewUnknown
 var s:State
 pure val initial={reader:true,closing:false,closed:false,previewUnknown:false,rendererFailed:false,recovery:false,host:1,lifetime:1,admitted:false,nativeWindowCommitted:false,oldUnknown:false,historyUnknown:false,scene:false,bindingRetired:false,reservationReleased:false,request:1,generation:1,newCommand:false,replays:0,freshPreview:false,freshOwner:1,freshReader:false,freshClosed:false}
 pure def reduce(st:State,e:Event):State=match e {
  | ClosePreview => if(st.host==1 and not(st.closed)){...st,closing:true} else st
  | AdmitWindow => if(st.host==1 and st.closing and not(st.admitted)){...st,admitted:true} else st
  | NativeWindowCommit => if(st.admitted and st.host==1 and not(st.oldUnknown)){...st,nativeWindowCommitted:true} else st
  | LoseReceipt => if(st.admitted and st.host==1){...st,oldUnknown:true,historyUnknown:true} else st
  | RendererFailure => if(st.host==1){...st,rendererFailed:true,closing:if(st.closed)false else true} else st
  | CloseReader => if(st.closing){...st,reader:false} else st
  // This event is an independently observed native proof, never inferred from
  // reader disposal, renderer death or the GUI's displayed operation status.
  | NativeStrictClose => if(st.closing and not(st.reader or st.previewUnknown)){...st,closed:true,closing:false} else st
  | Recovery => if(st.rendererFailed and st.closed and not(st.reader or st.previewUnknown)){...st,recovery:true} else st
  | Restart => if(st.host==1 and st.recovery){...st,host:2,scene:false} else st
  | Scene => if(st.host==2){...st,scene:true} else st
  | WindowBindingRetired => if(st.host==2 and st.oldUnknown){...st,bindingRetired:true} else st
  | ReleaseReservation => if(st.host==2 and st.scene and st.bindingRetired and st.oldUnknown){...st,reservationReleased:true} else st
  | ExplicitNewCommand => if(st.host==2 and st.scene and st.reservationReleased and not(st.newCommand)){...st,newCommand:true,request:st.request+1,generation:st.generation+1} else st
  | RetryOldWindow => st
  | FreshCapture => if(st.host==2 and st.scene and not(st.freshPreview)){...st,freshPreview:true,freshOwner:2,freshReader:true} else st
  | CloseFreshReader => if(st.freshPreview){...st,freshReader:false} else st
  | FreshStrictClose => if(st.freshPreview and not(st.freshReader)){...st,freshClosed:true} else st
  | PreviewUnknown => if(st.host==1 and not(st.closed)){...st,previewUnknown:true,closing:true} else st
 }
 pure def unsafeRestart(st:State):State={...st,host:2,recovery:true}
 pure def unsafeEraseHistory(st:State):State={...st,historyUnknown:false}
 pure def unsafeReplay(st:State):State={...st,replays:st.replays+1}
 pure def unsafeReuseOwner(st:State):State={...st,freshPreview:true,freshOwner:1}
 pure def safe(st:State):bool=all{
  st.lifetime==1,st.replays==0,
  st.closed implies not(st.reader or st.previewUnknown),
  st.recovery implies (st.rendererFailed and st.closed and not(st.reader or st.previewUnknown)),
  st.host==2 implies (st.closed and not(st.reader or st.previewUnknown)),
  st.oldUnknown implies st.historyUnknown,
  st.reservationReleased implies (st.oldUnknown and st.historyUnknown and st.bindingRetired and st.scene),
  st.newCommand implies (st.host==2 and st.scene and st.reservationReleased and st.request==2 and st.generation==2),
  not(st.newCommand) implies (st.request==1 and st.generation==1),
  st.freshPreview implies (st.host==2 and st.closed and st.freshOwner==2),
  st.freshClosed implies (st.freshPreview and not(st.freshReader))
 }
 action init=s'=initial
 action fire(e:Event):bool=s'=reduce(s,e)
 action step={nondet e=Set(ClosePreview,AdmitWindow,NativeWindowCommit,LoseReceipt,RendererFailure,CloseReader,NativeStrictClose,Recovery,Restart,Scene,WindowBindingRetired,ReleaseReservation,ExplicitNewCommand,RetryOldWindow,FreshCapture,CloseFreshReader,FreshStrictClose,PreviewUnknown).oneOf();fire(e)}
 val safety=safe(s)
}

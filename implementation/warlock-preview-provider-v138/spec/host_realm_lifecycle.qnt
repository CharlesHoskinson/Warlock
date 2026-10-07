module host_realm_lifecycle {
 // Presentation/realm lifetime abstraction. Native Drain is an independent
 // physical/journal/confirmation gate, never inferred from a UI close or receipt.
 type Event=OpenIntent|DOMReady|Admit|Initialize|Apply|ClosePopup|Drain|Retire|Replace|StaleCallback|Unknown
 type State={epoch:int,context:int,policy:int,lease:int,popup:bool,dom:bool,native:bool,initialized:bool,closing:bool,duty:bool,retired:bool,current:bool,uncertain:bool,reveal:bool,code:int,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e {|OpenIntent=>"OpenIntent"|DOMReady=>"DOMReady"|Admit=>"Admit"|Initialize=>"Initialize"|Apply=>"Apply"|ClosePopup=>"ClosePopup"|Drain=>"Drain"|Retire=>"Retire"|Replace=>"Replace"|StaleCallback=>"StaleCallback"|Unknown=>"Unknown"}
 pure def reduce(st:State,e:Event):State={
  val base={...st,code:0};
  if(st.uncertain){...base,code:1}
  else if(e==Unknown){...base,uncertain:true,current:false}
  else if(e==StaleCallback){...base,code:1}
  else if(e==OpenIntent){...base,popup:true,lease:st.lease+1,dom:false,current:false}
  else if(e==DOMReady){...base,dom:true}
  else if(e==Admit){if(not(st.popup) or not(st.dom) or st.native or st.retired){...base,code:1}else{...base,epoch:st.epoch+1,native:true,duty:true}}
  else if(e==Initialize){if(not(st.native) or st.closing or st.initialized){...base,code:1}else{...base,initialized:true}}
  else if(e==Apply){if(not(st.native) or not(st.popup) or not(st.dom) or not(st.initialized) or st.closing){...base,code:1}else{...base,current:true}}
  else if(e==ClosePopup){...base,popup:false,dom:false,current:false,closing:st.native or st.closing}
  else if(e==Drain){if(not(st.closing)){...base,code:1}else{...base,duty:false}}
  else if(e==Retire){if(not(st.native) or not(st.closing) or st.duty){...base,code:1}else{...base,native:false,retired:true,current:false}}
  else if(e==Replace){if(not(st.retired) or st.native or st.duty){...base,code:1}else{...base,context:st.context+1,dom:false,initialized:false,closing:false,retired:false,current:false}}
  else base
 }
 action init=s'={epoch:0,context:1,policy:1,lease:0,popup:false,dom:false,native:false,initialized:false,closing:false,duty:false,retired:false,current:false,uncertain:false,reveal:false,code:0,history:[]}
 action fire(e:Event):bool={val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(OpenIntent,DOMReady,Admit,Initialize,Apply,ClosePopup,Drain,Retire,Replace,StaleCallback,Unknown).oneOf();fire(e)}
 val safety=all{s.policy==1,s.context>=1,s.epoch>=0,s.lease>=0,not(s.reveal),s.retired implies (not(s.native) and not(s.duty)),s.current implies (s.native and s.popup and s.dom and s.initialized and not(s.closing) and not(s.uncertain))}
}

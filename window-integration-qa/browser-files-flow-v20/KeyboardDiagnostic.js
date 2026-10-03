// Additive private DOM diagnostics only; never changes event/default/input state.
(() => {
 const state={entries:[],sequence:0,eventSequence:0,dropped:0,exhausted:false,limit:512};
 window.qaKeyboardDiagnostic=state;
 const identities=new WeakMap();
 const text=value=>typeof value==='string'?value:null;
 const number=value=>typeof value==='number'&&Number.isFinite(value)?value:null;
 const boolean=value=>typeof value==='boolean'?value:null;
 function observe(event,phase) {
  if(state.exhausted)return;
  if(!Number.isSafeInteger(state.sequence)||state.sequence<0||state.sequence>=Number.MAX_SAFE_INTEGER||
     !Number.isSafeInteger(state.eventSequence)||state.eventSequence<0||state.eventSequence>=Number.MAX_SAFE_INTEGER){state.exhausted=true;return;}
  const target=event.target;
  const current={type:text(event.type),target:target?text(target.id):null,key:text(event.key),code:text(event.code),timestamp:number(event.timeStamp)};
  let identity;
  if(phase==='capture'){
   identity=Object.freeze({token:++state.eventSequence,page:performance.timeOrigin,type:current.type,target:current.target,key:current.key,code:current.code,timestamp:current.timestamp});
   identities.set(event,identity);
  }else identity=identities.get(event)||null;
  const sameCapture=identity!==null&&identity.page===performance.timeOrigin&&
   ['type','target','key','code','timestamp'].every(key=>identity[key]===current[key]);
  const row=Object.freeze({sequence:++state.sequence,eventToken:identity?identity.token:null,
   phase,captureExists:identity!==null,captureIdentityMatches:sameCapture,
   timeOrigin:number(performance.timeOrigin),timestamp:current.timestamp,handled:number(performance.now()),
   type:current.type,target:current.target,trusted:boolean(event.isTrusted),key:current.key,code:current.code,
   keyCode:number(event.keyCode),which:number(event.which),charCode:number(event.charCode),
   modifiers:Object.freeze([boolean(event.altKey),boolean(event.ctrlKey),boolean(event.metaKey),boolean(event.shiftKey)]),
   repeat:boolean(event.repeat),isComposing:boolean(event.isComposing),defaultPrevented:boolean(event.defaultPrevented),
   data:text(event.data),inputType:text(event.inputType),
   value:target&&target.id==='draft'?text(target.value):null,
   selection:target&&target.id==='draft'?Object.freeze([number(target.selectionStart),number(target.selectionEnd)]):null});
  state.entries.push(row);
  if(state.entries.length>512){state.entries.shift();state.dropped++;}
 }
 for(const type of ['keydown','keyup','beforeinput','input','compositionstart','compositionupdate','compositionend']){
  document.addEventListener(type,event=>observe(event,'capture'),true);
  document.addEventListener(type,event=>observe(event,'bubble'),false);
 }
})();

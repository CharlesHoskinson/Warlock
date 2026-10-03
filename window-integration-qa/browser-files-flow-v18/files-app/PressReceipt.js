.pragma library

function integer(value) { return typeof value === "number" && isFinite(value) && value % 1 === 0 }
function newState(item,area,ownerToken) {
  return {item:item,area:area,ownerToken:ownerToken,generation:0,press:null,
    valid:item !== null && area !== null && integer(ownerToken) && ownerToken>0}
}
function invalidate(state) { state.press=null;state.valid=false }
function cancel(state) { state.press=null }
function capture(state,item,area,mouse,viewMode) {
  state.press=null
  if(!state.valid || state.item!==item || state.area!==area || state.generation>=65536) { state.valid=false;return null }
  state.generation++
  if(item.visible!==true || item.enabled!==true || item.enabled2!==true ||
     typeof item.accessibleName!=="string" || !item.accessibleName.length ||
     typeof item.actionIdentity!=="string" || !item.actionIdentity.length ||
     !mouse || !integer(mouse.button) || mouse.button!==1 || !integer(mouse.modifiers) || mouse.modifiers!==0) return null
  state.press=Object.freeze({name:item.accessibleName,identity:item.actionIdentity,
    ownerToken:state.ownerToken,generation:state.generation,button:mouse.button,
    modifiers:mouse.modifiers,visible:item.visible,enabled:item.enabled,enabled2:item.enabled2,
    viewMode:String(viewMode)})
  return state.press
}
function consume(state,item,area,mouse,viewMode) {
  var press=state.press;state.press=null
  var valid=state.valid && state.item===item && state.area===area && press!==null &&
    press.ownerToken===state.ownerToken && press.generation===state.generation &&
    mouse && integer(mouse.button) && integer(mouse.modifiers) &&
    mouse.button===press.button && mouse.modifiers===press.modifiers
  return {name:valid?press.name:"",identity:valid?press.identity:"",
    button:mouse?mouse.button:null,modifiers:mouse?mouse.modifiers:null,viewMode:String(viewMode),time:Date.now(),
    accepted:!!valid,press:press,ownerToken:state.ownerToken,generation:state.generation,
    postHandlerName:String(item.accessibleName),postHandlerIdentity:String(item.actionIdentity),
    refusal:valid?"":"Missing/canceled/stale/mismatched exact MouseArea press capture"}
}

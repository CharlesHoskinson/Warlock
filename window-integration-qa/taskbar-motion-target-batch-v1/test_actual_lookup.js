var passed=0
function assert(v,label){if(!v)throw new Error(label);passed++}
function refused(fn,label){var caught=false;try{fn()}catch(e){caught=true}assert(caught,label)}
var id={address:"0x123",stableId:"18000000",pid:7}
var item={visible:true,motionDelegateGeneration:2,width:32,height:40}, icon={width:19,height:19,mapToItem:function(target){return {x:20,y:10}}}
item.motionIcon=icon
var root={visible:true,motionWidgetGeneration:1,currentMonitor:0}, bar={position:"bottom",shell:{bar:{barHidden:false}}}, barWindow={visible:true,width:1600,height:40,contentItem:{}},barScreen={name:"HEADLESS-1",width:1600,height:1000},monitors=[{id:0,x:100,y:-30,width:1600,height:1000,scale:1}],groups=[{windows:[{address:id.address,stableId:id.stableId,pid:id.pid,homeMonitor:0}]}],tasksFlickable={width:600,height:40},taskRepeater={itemAt:function(){return item}}
root.barWindow=barWindow;root.barScreen=barScreen;root.monitors=monitors;root.groups=groups;root.bar=bar
var r=motionTargetObservation(id)
assert(r.target.rect.x===120&&r.target.rect.y===940,"actual copied translation")
assert(r.witness.widgetGeneration===1&&r.witness.delegateGeneration===2,"actual object generations")
assert(validateObservation(r)===r,"witness agrees old delegate")
barWindow.visible=false;assert(motionTargetObservation(id)===null,"actual hidden window");barWindow.visible=true
item.visible=false;assert(motionTargetObservation(id)===null,"actual hidden delegate");item.visible=true
icon.mapToItem=function(){return {x:590,y:10}};assert(motionTargetObservation(id)===null,"actual clip refusal")
icon.mapToItem=function(){return {x:20,y:10}}
assert(motionTargetObservation({address:id.address,stableId:"18000001",pid:7})===null,"same address stale id")
assert(motionTargetObservation({address:id.address,stableId:id.stableId,pid:8})===null,"same address wrong pid")
var n=0;icon.mapToItem=function(){if(++n===5)item.motionDelegateGeneration=3;return {x:20,y:10}}
refused(function(){motionTargetObservation(id)},"real observation changed generation")
item.motionDelegateGeneration=2;n=0;icon.mapToItem=function(){if(++n===5)root.barScreen={name:barScreen.name,width:1600,height:1000};return {x:20,y:10}}
refused(function(){motionTargetObservation(id)},"screen reference replaced same values")
root.barScreen=barScreen;n=0;icon.mapToItem=function(){if(++n===5)groups[0].windows[0]={address:id.address,stableId:id.stableId,pid:id.pid,homeMonitor:0};return {x:20,y:10}}
refused(function(){motionTargetObservation(id)},"member reference replaced same values")
"actual extracted lookup assertions: "+passed

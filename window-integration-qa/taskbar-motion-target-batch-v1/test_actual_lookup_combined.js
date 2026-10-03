  function motionTargetFor(identity) {
    if(!barWindow || !barWindow.visible || !root.visible || !barScreen || bar && bar.shell && bar.shell.bar && bar.shell.bar.barHidden)return null
    var monitor=monitors.find(function(m) { return m.id===root.currentMonitor })
    if(!monitor)return null
    for(var i=0;i<groups.length;i++) {
      var w=groups[i].windows.find(function(w) {return w.address===identity.address && String(w.stableId)===identity.stableId && w.pid===identity.pid})
      if(!w)continue
      var item=taskRepeater.itemAt(i)
      if(!item || !item.visible || !item.motionIcon)return null
      var icon=item.motionIcon
      var clip=icon.mapToItem(tasksFlickable,0,0)
      if(clip.x<0 || clip.y<0 || clip.x+icon.width>tasksFlickable.width || clip.y+icon.height>tasksFlickable.height)return null
      var point=icon.mapToItem(barWindow.contentItem,0,0)
      var bx=bar && bar.position==="right" ? barScreen.width-barWindow.width : 0
      var by=bar && bar.position==="bottom" ? barScreen.height-barWindow.height : 0
      return {visible:true,home:w.homeMonitor===root.currentMonitor,screenName:barScreen.name,monitorX:monitor.x,monitorY:monitor.y,
        rect:{x:monitor.x+bx+point.x,y:monitor.y+by+point.y,width:icon.width,height:icon.height}}
    }
    return null
  }
  function motionTargetObservation(identity) {
    var target=motionTargetFor(identity)
    if(!target)return null
    var capturedWindow=barWindow, capturedScreen=barScreen
    var capturedMonitor=monitors.find(function(m){return m.id===root.currentMonitor})
    for(var n=0;n<groups.length;n++) {
      var group=groups[n]
      var member=group.windows.find(function(w){return w.address===identity.address && String(w.stableId)===identity.stableId && w.pid===identity.pid})
      if(!member)continue
      var item=taskRepeater.itemAt(n), icon=item ? item.motionIcon : null
      if(!capturedWindow || !capturedScreen || !capturedMonitor || !item || !icon)throw new Error("observation-owner-missing")
      function snapshot() {
        var point=icon.mapToItem(capturedWindow.contentItem,0,0), clip=icon.mapToItem(tasksFlickable,0,0)
        var position=root.bar ? root.bar.position : "top"
        return {widgetGeneration:root.motionWidgetGeneration,delegateGeneration:item.motionDelegateGeneration,
          screen:{name:capturedScreen.name,width:capturedScreen.width,height:capturedScreen.height},
          monitor:{id:capturedMonitor.id,x:capturedMonitor.x,y:capturedMonitor.y,width:capturedMonitor.width,height:capturedMonitor.height,scale:capturedMonitor.scale},
          bar:{position:position,x:position==="right"?capturedScreen.width-capturedWindow.width:0,y:position==="bottom"?capturedScreen.height-capturedWindow.height:0,width:capturedWindow.width,height:capturedWindow.height},
          icon:{x:point.x,y:point.y,width:icon.width,height:icon.height},
          clip:{x:clip.x,y:clip.y,width:tasksFlickable.width,height:tasksFlickable.height},allocation:{width:item.width,height:item.height}}
      }
      var before=snapshot(), afterTarget=motionTargetFor(identity), after=snapshot()
      if(root.barWindow!==capturedWindow || root.barScreen!==capturedScreen || root.monitors.find(function(m){return m.id===root.currentMonitor})!==capturedMonitor || root.groups[n]!==group || group.windows.find(function(w){return w.address===identity.address && String(w.stableId)===identity.stableId && w.pid===identity.pid})!==member || taskRepeater.itemAt(n)!==item || item.motionIcon!==icon || JSON.stringify(before)!==JSON.stringify(after) || JSON.stringify(target)!==JSON.stringify(afterTarget))throw new Error("observation-owner-changed")
      return {target:target,witness:before}
    }
    throw new Error("observation-member-missing")
  }
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

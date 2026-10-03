pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import Quickshell.Wayland
import Quickshell.Io

// Pixels move; the native window's geometry is never used as a tween target.
PanelWindow {
  id: root
  required property var owner
  property var requests: []
  property var objects: ({})
  property var epochs: ({})
  readonly property var barState: owner.bar && owner.bar.shell ? owner.bar.shell.bar : owner.bar
  readonly property string helper: owner.homeDir + "/.local/bin/hypr-window-motion"
  screen: owner.barScreen
  visible: requests.length > 0
  anchors { top: true; bottom: true; left: true; right: true }
  color: "transparent"
  exclusionMode: ExclusionMode.Ignore
  WlrLayershell.namespace: "hoskinson-window-motion"
  WlrLayershell.layer: WlrLayer.Overlay
  WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
  mask: Region {}
  function signal(method, token) { Quickshell.execDetached([helper, method, token]) }
  function intent(w) {
    for(var i=0;i<requests.length;i++) {
      var r=requests[i]
      if(r.identity[0]===w.address && r.identity[1]===String(w.stableId) && r.identity[2]===w.pid) return r.operation
    }
    return ""
  }
  function visualState() {
    return requests.map(function(r) {
      var item=objects[r.identity[0]]
      return {token:r.token,identity:r.identity,operation:r.operation,screenName:r.target.screenName,
        visible:root.visible && item && item.visible,imageReady:item && item.imageStatus===Image.Ready,
        heldFor:item ? item.heldFor : "",localHold:item ? item.localHold : false,routeProgress:item ? item.routeProgress : 0,rect:item ? item.currentRect() : null,from:r.from,to:r.to}
    })
  }
  function sameIdentity(a,b) { return a && b && a[0]===b[0] && a[1]===b[1] && a[2]===b[2] }
  function liveIdentity(identity) {
    return (owner.appGroups || []).some(function(group) {
      return (group.windows || []).some(function(w) {
        return root.sameIdentity(identity,[w.address,String(w.stableId),w.pid])
      })
    })
  }
  function collectEpochs() {
    Object.keys(epochs).forEach(function(address) {
      if(!objects[address] && !root.liveIdentity(epochs[address].identity))delete epochs[address]
    })
  }
  function epochAllows(request,beginning) {
    var epoch=epochs[request.identity[0]]
    if(!epoch || !sameIdentity(epoch.identity,request.identity))return true
    if(request.token===epoch.token)return beginning && epoch.phase==="held"
    var current=epoch.token.split("-"),next=request.token.split("-")
    if(current[0]===next[0])return Number(next[1])>Number(current[1])
    return epoch.retired.indexOf(next[0])<0
  }
  function remember(request,phase) {
    var previous=epochs[request.identity[0]]
    var retired=previous && sameIdentity(previous.identity,request.identity) ? previous.retired.slice() : []
    if(previous && sameIdentity(previous.identity,request.identity) && previous.token.split("-")[0]!==request.token.split("-")[0])retired.push(previous.token.split("-")[0])
    epochs[request.identity[0]]={token:request.token,identity:request.identity,phase:phase,retired:retired}
  }
  function freeze(request) {
    if(!liveIdentity(request.identity) || !epochAllows(request,false))return null
    var item=objects[request.identity[0]]
    if(item && !sameIdentity(item.modelData.identity,request.identity))return null
    // A previous begin may still be waiting for its snapshot. Remember the
    // reservation even when no image exists, rejecting that late old begin.
    if(item && item.modelData.token!==request.previousToken && item.heldFor!==request.previousToken)return null
    remember(request,"held")
    if(!item)return {accepted:true,visible:false}
    item.stop();item.localHold=false;item.holdTimeout.stop();item.heldFor=request.token
    var source=item
    while(source && source.imageStatus!==Image.Ready)source=source.previousFrame
    var snapshot=source ? {image:source.modelData.image,rect:source.modelData.rect,
      nativeRect:source.modelData.nativeRect,whole:Boolean(source.modelData.wholeWindow),identity:source.modelData.identity} : null
    return {accepted:true,snapshot:snapshot,visible:!!source && source.visible,token:request.token,previousToken:request.previousToken,
      routeProgress:item.routeProgress,rect:item.currentRect(),sourceToken:item.modelData.token}
  }
  function holdCaptured(w) {
    var item=objects[w.address]
    if(!item || !sameIdentity(item.modelData.identity,[w.address,String(w.stableId),w.pid]))return false
    item.stop();item.localHold=true;item.holdTimeout.restart();return true
  }
  function begin(request) {
    if(!owner.barScreen || request.target.screenName!==owner.barScreen.name || owner.reducedMotion) return false
    if(!liveIdentity(request.identity) || !epochAllows(request,true))return false
    var address=request.identity[0]
    var previous=objects[address] || null
    var same=previous && previous.modelData.identity[1]===request.identity[1] && previous.modelData.identity[2]===request.identity[2]
    var rect=same ? previous.currentRect() : null
    if(previous)previous.stop()
    var next=Object.assign({},request)
    next.from=rect || (request.operation==="minimize" ? request.rect : request.target.rect)
    next.to=request.operation==="minimize" ? request.target.rect : request.rect
    var item=motionFrame.createObject(root.contentItem,{modelData:next,previousFrame:previous})
    if(!item)return false
    remember(request,"begun")
    objects[address]=item
    requests=requests.filter(function(r) { return r.identity[0]!==address }).concat([next])
    return true
  }
  function start(request) {
    var item=objects[request.identity[0]]
    if(!item || item.modelData.token!==request.token || item.heldFor || item.localHold || owner.reducedMotion || item.imageStatus!==Image.Ready)return false
    item.play();return true
  }
  function cancel(request) {
    var address=request.identity[0]
    var item=objects[address]
    var matches=item && (item.heldFor ? item.heldFor===request.token : item.modelData.token===request.token)
    if(matches) {item.dispose();delete objects[address]}
    if(epochs[address] && epochs[address].token===request.token)epochs[address].phase="cancelled"
    requests=requests.filter(function(r) { return matches ? r.identity[0]!==address : r.token!==request.token })
  }
  function reduce() {
    var previous=requests
    previous.forEach(function(r) {
      var item=objects[r.identity[0]]
      var current=Object.assign({},r,{token:item && item.heldFor ? item.heldFor : r.token})
      root.cancel(current);root.signal("fail",current.token)
    })
  }
  Component.onDestruction: requests.forEach(function(r) {
    var item=objects[r.identity[0]]
    root.signal("fail",item && item.heldFor ? item.heldFor : r.token)
  })
  Timer {
    interval: 2000;running:true;repeat:true
    onTriggered: root.collectEpochs()
  }
  FileView {
    path: root.owner.homeDir + "/.config/hypr/reduced-motion"
    watchChanges: true
    printErrors: false
    onFileChanged: reload()
    onLoaded: { if(text().trim()==="1")root.reduce() }
  }
  Connections { target: root.barState; ignoreUnknownSignals: true; function onBarHiddenChanged() { if(root.barState && root.barState.barHidden)root.reduce() } }
  Connections { target: root.owner; function onReducedMotionChanged() { if(root.owner.reducedMotion)root.reduce() } }
  Component {
    id: motionFrame
    Image {
      id: frame
      required property var modelData
      property var previousFrame: null
      property real routeProgress: 0
      property bool signaled: false
      property string heldFor: ""
      property bool localHold: false
      property alias holdTimeout: localTimeout
      readonly property int imageStatus: status
      readonly property real originX: modelData.target.monitorX
      readonly property real originY: modelData.target.monitorY
      x: modelData.from.x + (modelData.to.x-modelData.from.x)*routeProgress-originX
      y: modelData.from.y + (modelData.to.y-modelData.from.y)*routeProgress-originY
      width: modelData.from.width + (modelData.to.width-modelData.from.width)*routeProgress
      height: modelData.from.height + (modelData.to.height-modelData.from.height)*routeProgress
      source: "file://" + modelData.image
      asynchronous: true
      cache: false
      fillMode: Image.Stretch
      smooth: true
      visible: status===Image.Ready
      function currentRect() { return {x:x+originX,y:y+originY,width:width,height:height} }
      function stop() { readiness.stop();tween.stop() }
      function dispose() { stop();localTimeout.stop();if(previousFrame) {previousFrame.dispose();previousFrame=null};destroy() }
      function play() { if(tween.running)return; tween.start() }
      onStatusChanged: {
        if(status===Image.Ready && !signaled && !heldFor && !localHold) {
          if(previousFrame) {previousFrame.dispose();previousFrame=null}
          readiness.restart()
        }
        else if(status===Image.Error)root.signal("fail",heldFor || modelData.token)
      }
      Timer {
        id: localTimeout; interval: 1600
        onTriggered: {
          // Rejected/failed helper startup cannot strand a local input hold.
          if(frame.localHold) {root.cancel(frame.modelData);root.signal("fail",frame.modelData.token)}
        }
      }
      // Give the ready image a presentation opportunity before hiding native.
      Timer { id: readiness; interval: 17; onTriggered: {if(!frame.heldFor && !frame.localHold && root.objects[frame.modelData.identity[0]]===frame) {frame.signaled=true;root.signal("ready",frame.modelData.token)}} }
      NumberAnimation {
        id: tween
        target: frame; property: "routeProgress"; from: 0; to: 1
        duration: frame.modelData.operation==="minimize" ? 190 : 230
        easing.type: Easing.InOutCubic
        onFinished: root.signal("done",frame.modelData.token)
      }
    }
  }
}

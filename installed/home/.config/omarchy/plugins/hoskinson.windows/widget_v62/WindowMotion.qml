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
        routeProgress:item ? item.routeProgress : 0,rect:item ? item.currentRect() : null,from:r.from,to:r.to}
    })
  }
  function begin(request) {
    if(!owner.barScreen || request.target.screenName!==owner.barScreen.name || owner.reducedMotion) return false
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
    objects[address]=item
    requests=requests.filter(function(r) { return r.identity[0]!==address }).concat([next])
    return true
  }
  function start(request) {
    var item=objects[request.identity[0]]
    if(!item || item.modelData.token!==request.token || owner.reducedMotion || item.imageStatus!==Image.Ready)return false
    item.play();return true
  }
  function cancel(request) {
    var address=request.identity[0]
    var item=objects[address]
    if(item && item.modelData.token===request.token) {item.dispose();delete objects[address]}
    requests=requests.filter(function(r) { return r.token!==request.token })
  }
  function reduce() {
    var previous=requests
    previous.forEach(function(r) { root.cancel(r);root.signal("fail",r.token) })
  }
  Component.onDestruction: requests.forEach(function(r) { root.signal("fail",r.token) })
  FileView {
    path: root.owner.homeDir + "/.config/hypr/reduced-motion"
    watchChanges: true
    printErrors: false
    onFileChanged: reload()
    onLoaded: { if(text().trim()==="1")root.reduce() }
  }
  Connections { target: root.owner.bar; function onBarHiddenChanged() { if(root.owner.bar.barHidden)root.reduce() } }
  Connections { target: root.owner; function onReducedMotionChanged() { if(root.owner.reducedMotion)root.reduce() } }
  Component {
    id: motionFrame
    Image {
      id: frame
      required property var modelData
      property var previousFrame: null
      property real routeProgress: 0
      property bool signaled: false
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
      function dispose() { stop();if(previousFrame) {previousFrame.dispose();previousFrame=null};destroy() }
      function play() { if(tween.running)return; tween.start() }
      onStatusChanged: {
        if(status===Image.Ready && !signaled) {
          if(previousFrame) {previousFrame.dispose();previousFrame=null}
          readiness.restart()
        }
        else if(status===Image.Error)root.signal("fail",modelData.token)
      }
      // Give the ready image a presentation opportunity before hiding native.
      Timer { id: readiness; interval: 17; onTriggered: {frame.signaled=true;root.signal("ready",frame.modelData.token)} }
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

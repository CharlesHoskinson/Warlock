import QtQuick
import "file:///home/hoskinson/.local/share/hypr-window-controls/qml/WindowAccessibilityV4"
import QtQuick.Layouts
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "hoskinson.windows"
  Accessible.role: Accessible.ToolBar
  Accessible.name: "Taskbar"
  Component.onCompleted: root.runArgs([root.homeDir + "/.local/bin/hypr-desktop", "peek-off"])
  property var appGroups: []
  property var taskbarSettings: ({})
  property var monitors: []
  property bool keyboardMode: false
  property bool popupAccessibilityReady: false
  property int diagnosticPopupEpoch: 0
  // Owned QA terminal evidence; never grants feature/native completion.
  property bool qaTerminalQuiesced: false
  property string qaTerminalNonce: Quickshell.env("WINDOW_QA_TERMINAL_NONCE") || ""
  property string qaTerminalError: ""
  property int qaTerminalQueuedBudget: 0
  property var qaProcessGenerations: ({snapshot:0,action:0,capture:0,allCapture:0})
  property var qaProcessCurrent: ({})
  property var qaProcessRecords: []
  function qaRecord(record) {
    if (qaProcessRecords.length >= 8192) { qaTerminalError="Process evidence limit"; return }
    qaProcessRecords=qaProcessRecords.concat([Object.assign({utcMs:Date.now()},record)])
  }
  function qaRequested(kind,command) {
    if (qaTerminalQuiesced) {
      if(kind!=="action" || qaTerminalQueuedBudget<=0) qaTerminalError="New process after terminal scheduling barrier"
      else qaTerminalQueuedBudget--
    }
    if(qaProcessCurrent[kind]) qaTerminalError="Overlapping Process request generation"
    var generations=Object.assign({},qaProcessGenerations)
    generations[kind]++;qaProcessGenerations=generations
    var current=Object.assign({},qaProcessCurrent)
    current[kind]={generation:generations[kind],command:Array.from(command),pid:0,started:false}
    qaProcessCurrent=current
    qaRecord({event:"requested",kind:kind,generation:generations[kind],command:Array.from(command)})
  }
  function qaStarted(kind,process) {
    var current=Object.assign({},qaProcessCurrent),entry=current[kind]
    var pid=Number(process.processId)
    if(!entry || entry.started || !Number.isInteger(pid) || pid<=0 || pid>=2147483648 || JSON.stringify(entry.command)!==JSON.stringify(Array.from(process.command))) {
      qaTerminalError="Process started without exact request";return
    }
    entry=Object.assign({},entry,{pid:pid,started:true});current[kind]=entry;qaProcessCurrent=current
    qaRecord({event:"started",kind:kind,generation:entry.generation,pid:pid,command:entry.command})
  }
  function qaExited(kind,code,status) {
    var current=Object.assign({},qaProcessCurrent),entry=current[kind]
    if(!entry || !entry.started) { qaTerminalError="Process exited without exact start";return }
    qaRecord({event:"exited",kind:kind,generation:entry.generation,pid:entry.pid,code:code,status:status})
    if(code!==0 || status!==0) qaTerminalError="Process abnormal terminal receipt"
    delete current[kind];qaProcessCurrent=current
  }
  function qaTerminalValid(nonce) {
    return /^[0-9a-f]{32}$/.test(nonce) && nonce===qaTerminalNonce
  }
  function qaTerminalBegin(nonce) {
    if(!qaTerminalValid(nonce) || qaTerminalQuiesced) return false
    qaTerminalQueuedBudget=actionQueue.length
    qaTerminalQuiesced=true
    qaSnapshotPoll.stop();qaCapturePoll.stop();qaAllCapturePoll.stop();captureDelay.stop()
    qaRecord({event:"quiesced",nonce:nonce,queuedActions:qaTerminalQueuedBudget})
    return true
  }
  function qaTerminalState(nonce) {
    if(!qaTerminalValid(nonce)) return {error:"Exact terminal nonce required"}
    var processes={snapshot:snapshotProcess,action:actionProcess,capture:captureProcess,allCapture:allCaptureProcess},states={}
    Object.keys(processes).forEach(function(kind) { var p=processes[kind];states[kind]={running:p.running,pid:p.processId===null ? null : Number(p.processId),command:Array.from(p.command)} })
    return {screenName:root.barScreen ? root.barScreen.name : "",currentMonitor:root.currentMonitor,nonce:nonce,
      quiesced:qaTerminalQuiesced,error:qaTerminalError,queuedActions:actionQueue.length,queuedBudget:qaTerminalQueuedBudget,
      timers:{snapshot:qaSnapshotPoll.running,capture:qaCapturePoll.running,allCapture:qaAllCapturePoll.running,captureDelay:captureDelay.running,queueDelay:queueDelay.running},
      generations:qaProcessGenerations,current:qaProcessCurrent,processes:states,records:qaProcessRecords}
  }
  onPopupOpenChanged: { diagnosticPopupEpoch++; if (!popupOpen) popupAccessibilityReady = false }
  property bool reducedMotion: false
  property int selectedWindowIndex: 0
  readonly property var groups: displayGroups()
  readonly property bool uncombined: taskbarSettings.combineMode === "never" || taskbarSettings.combineMode === "when-full" && appGroups.reduce(function(n,g) { return n + Math.max(1,g.windows.length) * 130 },0) <= maxWidth
  readonly property var barWindow: root.QsWindow.window
  readonly property var barScreen: barWindow ? barWindow.screen : null
  readonly property int currentMonitor: monitors.filter(function(m) { return root.barScreen && m.name === root.barScreen.name })[0] ? monitors.filter(function(m) { return root.barScreen && m.name === root.barScreen.name })[0].id : -1
  readonly property bool ipcOwner: currentMonitor < 0 || monitors.some(function(m) { return m.id === root.currentMonitor && m.focused })
  readonly property string currentDesktop: String((monitors.filter(function(m) { return m.focused })[0] || {}).activeWorkspace ? monitors.filter(function(m) { return m.focused })[0].activeWorkspace.name : "1")
  function displayGroups() {
    var result = []
    appGroups.forEach(function(g) {
      var windows = g.windows.filter(function(w) {
        return (root.taskbarSettings.displayMode !== "monitor" || root.currentMonitor < 0 || w.homeMonitor === root.currentMonitor)
          && (root.taskbarSettings.desktopScope !== "current" || w.homeWorkspace === root.currentDesktop || w.homePinned)
      })
      if (!windows.length && !g.pinned) return
      if (root.uncombined && windows.length) windows.forEach(function(w) { var item = Object.assign({}, g); item.windows = [w]; item.displayKey = g.key + "@" + w.address; result.push(item) })
      else { var item = Object.assign({},g); item.windows = windows; item.displayKey = g.key; result.push(item) }
    })
    return result
  }
  function widthFor(g) { return uncombined && g.windows.length ? 130 : buttonWidth }
  function positionFor(index) { var x=0; for(var i=0;i<index && i<groups.length;i++) x += widthFor(groups[i])+row.spacing; return x }
  function activateIndex(index) {
    if(index<0 || index>=groups.length) return
    var g=groups[index]
    if(!g.windows.length) { if(g.desktopId) taskbarAction("launch",g.desktopId); return }
    if(g.windows.length>1) { var focused=g.windows.findIndex(function(w) { return w.address===root.focusedAddress }); windowAction("restore",g.windows[(focused+1)%g.windows.length].address); return }
    var w=g.windows[0]
    windowAction("activate",w.address)
  }
  function activateGroup(index) {
    var g = groups[index]
    if (!g) return
    if (g.windows.length > 1) { openGroup(index, false); return }
    activateIndex(index)
  }
  // Diagnostics only: inspecting other outputs must not move focus or activate a window.
  function diagnosticPopupViewport() {
    var point=popupFlickable.mapToItem(null,0,0)
    return {coordinateSpace:"layer-window",x:point.x,y:point.y,width:popupFlickable.width,height:popupFlickable.height,
      clip:popupFlickable.clip,contentY:popupFlickable.contentY,contentHeight:popupFlickable.contentHeight}
  }
  function diagnosticState() {
    var monitor=root.monitors.find(function(m) { return m.id===root.currentMonitor })
    var bx=root.bar && root.bar.position==="right" && root.barScreen && root.barWindow ? root.barScreen.width-root.barWindow.width : 0
    var by=root.bar && root.bar.position==="bottom" && root.barScreen && root.barWindow ? root.barScreen.height-root.barWindow.height : 0
    return {screenName:root.barScreen ? root.barScreen.name : "", monitorGeometry:monitor ? {x:monitor.x,y:monitor.y,width:monitor.width/monitor.scale,height:monitor.height/monitor.scale} : null, barOffset:{x:bx,y:by}, barSize:{width:root.barWindow ? root.barWindow.width : 0,height:root.barWindow ? root.barWindow.height : 0}, fileDragActive:root.fileDragActive,fileDragOnTaskbar:root.fileDragOnTaskbar,fileDragStamp:root.fileDragStamp,filePreviewKey:root.filePreviewKey,dropSize:[taskDrop.width,taskDrop.height],dragEntries:root.dragEntries, dragGroupKey:root.dragGroupKey, dragActivated:root.dragActivated, taskbarItems:root.groups.map(function(g,i) { var item=taskRepeater.itemAt(i); var pos=item && root.barWindow ? item.mapToItem(root.barWindow.contentItem,0,0) : {x:0,y:0}; return {key:g.displayKey,x:pos.x,y:pos.y,width:root.widthFor(g),height:item ? item.height : 0,windows:g.windows.map(function(w) { return w.address })} }), previewItems:!root.menuMode && root.popupGroup ? root.popupGroup.windows.map(function(w,i) { var item=windowRepeater.itemAt(i); var pos=item && item.QsWindow.window ? item.mapToItem(null,0,0) : {x:0,y:0}; return {address:w.address,stableId:w.stableId,pid:w.pid,x:pos.x,y:pos.y,width:item ? item.width : 0,height:item ? item.height : 0} }) : [], groups:root.groups.length, wheelEvents:root.wheelEvents, currentMonitor:root.currentMonitor, selectedWindowIndex:root.selectedWindowIndex, popupScrollY:popupFlickable.contentY, popupViewportHeight:popupFlickable.height, popupContentHeight:popupFlickable.contentHeight, menuLabels:root.menuItems.map(function(item) { return item.label }), currentDesktop:root.currentDesktop, indicators:root.groups.map(function(g) { return {key:g.key, windows:g.windows.map(function(w) { return w.address }), launcher:g.launcher || {}, urgent:g.windows.some(function(w) { return w.urgent === true })} }), diagnosticPopupEpoch:root.diagnosticPopupEpoch, popupKey:root.popupKey, popupGeometry:previewCard.diagnosticBounds(), popupViewportBounds:root.diagnosticPopupViewport(), popupOpen:root.popupOpen, popupIndex:root.popupIndex, menuMode:root.menuMode, keyboardMode:root.keyboardMode, keyboardFocus:popupKeyCatcher.activeFocus, combineMode:root.taskbarSettings.combineMode || "always", displayMode:root.taskbarSettings.displayMode || "all", desktopScope:root.taskbarSettings.desktopScope || "all", switcherScope:root.taskbarSettings.switcherScope || "current"}
  }
  function diagnosticStates() {
    var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
    return items.filter(function(item) { return item && typeof item.diagnosticState==="function" }).map(function(item) { return item.diagnosticState() })
  }
  IpcHandler {
    target: "hoskinson.windows"
    enabled: root.ipcOwner
    function qaTerminalQuiesce(nonce:string):string {
      var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
      if(!items.length || items.some(function(item) { return !item || typeof item.qaTerminalBegin!=="function" || !item.qaTerminalValid(nonce) || item.qaTerminalQuiesced }))
        return JSON.stringify({version:1,nonce:nonce,ack:false,error:"Exact fresh terminal widget set required"})
      var ack=items.every(function(item) { return item.qaTerminalBegin(nonce) })
      return JSON.stringify({version:1,nonce:nonce,ack:ack,states:items.map(function(item) { return item.qaTerminalState(nonce) })})
    }
    function qaTerminalRead(nonce:string):string {
      var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
      return JSON.stringify({version:1,nonce:nonce,ack:items.length>0 && items.every(function(item) { return item && item.qaTerminalValid(nonce) && item.qaTerminalQuiesced }),states:items.map(function(item) { return item.qaTerminalState(nonce) })})
    }
    function motionRefresh(encoded:string):bool { root.broadcast("refresh"); return true }
    function motionTarget(encoded:string):string {
      var identity=JSON.parse(encoded)
      var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
      var candidates=[]
      items.forEach(function(item) { if(item && item.motionTargetFor) {var target=item.motionTargetFor(identity);if(target)candidates.push(target)} })
      candidates.sort(function(a,b) { return (a.home ? 0 : 1)-(b.home ? 0 : 1) })
      return JSON.stringify(candidates[0] || null)
    }
    function motionFreeze(encoded:string):string {
      var request=JSON.parse(encoded)
      var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
      var ack=null
      items.forEach(function(item) { if(item && item.motionReceive) {var value=item.motionReceive("freeze",request);if(value)ack=value} })
      return JSON.stringify(ack)
    }
    function motionBegin(encoded:string):bool { return root.motionDispatch("begin",JSON.parse(encoded)) }
    function motionStart(encoded:string):bool { return root.motionDispatch("start",JSON.parse(encoded)) }
    function motionCancel(encoded:string):bool { return root.motionDispatch("cancel",JSON.parse(encoded)) }
    function motionState():string { return JSON.stringify(windowMotion.requests) }
    function motionVisualState():string {
      var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
      var result=[]
      items.forEach(function(item) { if(item && item.motionVisualStateFor)result=result.concat(item.motionVisualStateFor()) })
      return JSON.stringify(result)
    }
    function dismiss(): void { root.filePreviewDelayReset(); root.stopDragHover(); root.popupOpen=false; root.keyboardMode=false; root.menuMode=false }
    function fileDrag(active:bool,x:real,y:real,monitor:int,stamp:real):void {
      var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
      items.forEach(function(item) {if(item && item.externalFileDrag) item.externalFileDrag(active,x,y,monitor,stamp)})
    }
    function state(): string { return JSON.stringify(root.diagnosticState()) }
    function stateAll(): string { return JSON.stringify(root.diagnosticStates()) }
    function stateForMonitor(monitor: int): string {
      var states=root.diagnosticStates()
      return JSON.stringify(states.find(function(item) { return item.currentMonitor===monitor }) || null)
    }
    function activate(number: int): void { root.activateIndex(number-1) }
    function launch(number: int): void { var g=root.groups[number-1]; if(g && g.desktopId) root.taskbarAction("launch",g.desktopId) }
    function menu(number: int): void { root.openGroup(number-1,true); root.keyboardMode=true }
    function cycle(step: int): void { if(!root.groups.length) return; var i=root.popupOpen ? root.popupIndex : -1; root.openGroup((i+step+root.groups.length)%root.groups.length,false); root.keyboardMode=true }
  }
  property var snapGroups: []
  property string focusedAddress: ""
  property string signature: ""
  property string popupKey: ""
  property int popupIndex: -1
  property bool popupOpen: false
  property bool menuMode: false
  property string captureAddress: ""
  property int previewRevision: 0
  property var actionQueue: []
  readonly property string homeDir: Quickshell.env("HOME")
  readonly property string previewDir: (Quickshell.env("XDG_RUNTIME_DIR") || homeDir + "/.cache") + "/hypr-window-previews"
  readonly property int buttonWidth: 38
  readonly property int maxWidth: 460
  readonly property var popupGroup: groups.filter(function(g) { return g.displayKey === root.popupKey })[0] || null
  ListModel { id: taskCards }
  ListModel { id: previewCards }
  ListModel { id: menuCards }
  readonly property var previewWindows: !menuMode && popupGroup ? popupGroup.windows : []
  function syncPopupCards(model, values, kind) {
    for (var i = 0; i < values.length; i++) {
      var entry = values[i]
      var identity = kind === "group" ? String(entry.displayKey) : kind === "window" ? String(entry.stableId) : JSON.stringify([entry.command || "", entry.key || "", entry.extra || "", entry.snap || ""])
      var found = -1
      for (var j = i; j < model.count; j++) {
        if (model.get(j).identity === identity) { found = j; break }
      }
      var payload = JSON.stringify(entry)
      if (found < 0) model.insert(i, {identity: identity, payload: payload})
      else {
        if (found !== i) model.move(found, i, 1)
        if (model.get(i).payload !== payload) model.setProperty(i, "payload", payload)
      }
    }
    if (model.count > values.length) model.remove(values.length, model.count - values.length)
  }
  onGroupsChanged: syncPopupCards(taskCards, groups, "group")
  onPreviewWindowsChanged: syncPopupCards(previewCards, previewWindows, "window")
  onMenuItemsChanged: syncPopupCards(menuCards, menuItems, "menu")
  readonly property var relatedSnaps: popupGroup ? snapGroups.filter(function(s) {
    return s.addresses.some(function(a) { return root.popupGroup.windows.some(function(w) { return w.address === a }) })
  }) : []
  readonly property var menuItems: makeMenu()
  property bool fileDragActive: false
  property bool fileDragOnTaskbar: false
  property real fileDragStamp: -1
  property var filePreviewWindow: null
  property string filePreviewKey: ""
  function externalFileDrag(active,x,y,monitor,stamp) {
    if(stamp <= fileDragStamp) return
    fileDragStamp=stamp
    var wasActive=fileDragActive
    fileDragActive=active
    if(!active) {
      fileDragWatchdog.stop()
      fileDragOnTaskbar=false
      stopDragHover()
      filePreviewDelay.stop()
      filePreviewWindow=null; filePreviewKey=""
      if(wasActive) popupOpen=false
      return
    }
    fileDragWatchdog.restart()
    var m=root.monitors.find(function(m) { return m.id===root.currentMonitor })
    var lx=x-(m ? m.x : 0), ly=y-(m ? m.y : 0)
    var bx=root.bar && root.bar.position==="right" ? (root.barScreen ? root.barScreen.width : 0)-(root.barWindow ? root.barWindow.width : 0) : 0
    var by=root.bar && root.bar.position==="bottom" ? (root.barScreen ? root.barScreen.height : 0)-(root.barWindow ? root.barWindow.height : 0) : 0
    var pos=root.barWindow ? tasksFlickable.mapToItem(root.barWindow.contentItem,0,0) : {x:0,y:0}
    var overTask=monitor===root.currentMonitor && lx>=pos.x+bx && lx<pos.x+bx+tasksFlickable.width && ly>=pos.y+by && ly<pos.y+by+tasksFlickable.height
    if(overTask) {
      if(!fileDragOnTaskbar) dragEntries++
      fileDragOnTaskbar=true
      filePreviewDelay.stop();filePreviewKey="";filePreviewWindow=null
      beginDragGroup(lx-pos.x-bx)
      closeDelay.stop()
      return
    }
    fileDragOnTaskbar=false
    stopDragHover()
    var preview=null
    if(monitor===root.currentMonitor && popupOpen && !menuMode) {
      for(var i=0;i<windowRepeater.count;i++) {
        var item=windowRepeater.itemAt(i)
        var win=item ? item.QsWindow.window : null
        if(!win) continue
        var p=item.mapToItem(null,0,0)
        if(lx>=p.x && lx<p.x+item.width && ly>=p.y && ly<p.y+item.height) {preview=item.modelData;break}
      }
    }
    if(preview) {
      var key=preview.address+":"+preview.pid+":"+preview.stableId
      if(filePreviewKey!==key) {
        filePreviewKey=key;filePreviewWindow=Object.assign({},preview)
        filePreviewDelay.restart()
      }
      closeDelay.stop()
    } else {
      filePreviewDelay.stop();filePreviewKey="";filePreviewWindow=null
      if(popupOpen && !menuMode && !keyboardMode) closeDelay.restart()
    }
  }
  Timer {id:filePreviewDelay;interval:600;onTriggered:if(root.fileDragActive && root.filePreviewWindow) root.activateDraggedWindow(root.filePreviewWindow)}
  Timer {id:fileDragWatchdog;interval:700;onTriggered:root.externalFileDrag(false,0,0,-1,root.fileDragStamp+1)}
  property int dragEntries: 0
  property string dragGroupKey: ""
  property var dragWindow: null
  property bool dragActivated: false
  function beginDragGroup(x) {
    var index = taskHover.indexAt(x)
    var key = index >= 0 ? root.groups[index].displayKey : ""
    if (key === dragGroupKey) return
    stopDragHover()
    if (!key) return
    dragGroupKey = key
    dragActivated = false
    var g = root.groups[index]
    dragWindow = g.windows.length === 1 ? Object.assign({},g.windows[0]) : null
    dragOpenDelay.restart()
  }
  function previewDragActive() {
    for(var i=0;i<windowRepeater.count;i++) {
      var item=windowRepeater.itemAt(i)
      if(item && item.fileDragActive) return true
    }
    return false
  }
  function filePreviewDelayReset() {filePreviewDelay.stop();filePreviewWindow=null;filePreviewKey=""}
  function stopDragHover() {
    dragOpenDelay.stop()
    dragActivateDelay.stop()
    dragGroupKey = ""
    dragWindow = null
  }
  function activateDraggedWindow(w) {
    if (!w || !/^0x[0-9a-fA-F]+$/.test(w.address)) return
    var current = root.groups.some(function(g) { return g.windows.some(function(candidate) {
      return candidate.address===w.address && candidate.pid===w.pid && candidate.stableId===w.stableId
    }) })
    if (!current) return
    dragActivated = true
    runArgs([homeDir + "/.local/bin/hypr-windowctl", "restore", w.address, String(w.stableId || ""), String(w.pid)])
    popupOpen = false
  }
  Timer {
    id: dragOpenDelay; interval: 400
    onTriggered: {
      if (!taskDrop.containsDrag && !root.fileDragOnTaskbar) return
      var index = root.groups.findIndex(function(g) { return g.displayKey===root.dragGroupKey })
      if (index < 0 || !root.groups[index].windows.length) return
      root.openGroup(index,false)
      if (root.dragWindow) dragActivateDelay.restart()
    }
  }
  Timer { id: dragActivateDelay; interval: 400; onTriggered: if((taskDrop.containsDrag || root.fileDragOnTaskbar) && !root.dragActivated) root.activateDraggedWindow(root.dragWindow) }
  property int wheelEvents: 0
  function scrollPopup(event) {
    wheelEvents++
    var delta = event.pixelDelta.y || event.angleDelta.y / 3
    popupFlickable.contentY = Math.max(0,Math.min(Math.max(0,popupFlickable.contentHeight-popupFlickable.height),popupFlickable.contentY-delta))
    event.accepted = true
  }
  onSelectedWindowIndexChanged: Qt.callLater(root.revealSelection)
  function revealSelection() {
    var count = root.menuMode ? root.menuItems.length : root.popupGroup ? root.popupGroup.windows.length : 0
    if(!count) return
    var item = root.menuMode ? menuRepeater.itemAt(root.selectedWindowIndex % count) : windowRepeater.itemAt(root.selectedWindowIndex % count)
    if(!item) return
    if(item.y < popupFlickable.contentY) popupFlickable.contentY = item.y
    else if(item.y + item.height > popupFlickable.contentY + popupFlickable.height)
      popupFlickable.contentY = Math.min(Math.max(0,popupFlickable.contentHeight-popupFlickable.height),item.y+item.height-popupFlickable.height)
  }

  function iconSource(group) {
    return bar && bar.shell && bar.shell.appLibrary ? bar.shell.appLibrary.iconSource(group.icon) : Quickshell.iconPath(group.icon, true)
  }
  function refresh() { if (!root.qaTerminalQuiesced && !snapshotProcess.running) { root.qaRequested("snapshot",snapshotProcess.command); snapshotProcess.running = true } }
  function runArgs(args) {
    // Other CLI callers retain synchronous completion; the taskbar can reverse
    // an accepted motion request while its snapshot is still moving.
    if(args[0]===homeDir + "/.local/bin/hypr-windowctl" && ["minimize","restore","toggle","activate"].indexOf(args[1])>=0)
      args=["env","HYPR_WINDOWCTL_ASYNC=1"].concat(args)
    if(root.qaTerminalQuiesced) root.qaTerminalError="New action queue after terminal barrier"
    actionQueue = actionQueue.concat([args])
    drainQueue()
  }
  function drainQueue() {
    if (actionProcess.running || !actionQueue.length) return
    actionProcess.command = actionQueue[0]
    actionQueue = actionQueue.slice(1)
    root.qaRequested("action",actionProcess.command)
    actionProcess.running = true
  }
  function taskbarAction(command, key, extra) {
    var args = [homeDir + "/.local/bin/hypr-taskbar", command, key]
    if (extra !== undefined) args.push(extra)
    runArgs(args)
    popupOpen = false
  }
  function windowAction(command, address) {
    if (!/^0x[0-9a-fA-F]+$/.test(address)) return
    var w = null
    for (var i=0; i<groups.length && !w; i++) w=groups[i].windows.filter(function(c) { return c.address === address })[0]
    if (!w) return
    if (command === "close") runArgs([homeDir + "/.local/bin/hypr-window-menu", "act", address, "close", String(w.stableId || ""), String(w.pid || "")])
    else {
      if(["minimize","restore","toggle","activate"].indexOf(command)>=0)windowMotion.holdCaptured(w)
      runArgs([homeDir + "/.local/bin/hypr-windowctl", command, address, String(w.stableId || ""), String(w.pid || "")])
    }
    popupOpen = false
  }
  function recall(id) {
    runArgs([homeDir + "/.local/bin/hypr-snap-groups", "recall", id])
    popupOpen = false
  }
  function makeMenu() {
    var g = popupGroup
    if (!g) return []
    var result = []
    if (g.desktopId) {
      result.push({label: "Open " + g.name, command: "launch", key: g.desktopId})
      result.push({label: g.pinned ? "Unpin from taskbar" : "Pin to taskbar", command: g.pinned ? "unpin" : "pin", key: g.desktopId})
    }
    if (g.windows.length > 1) result.push({label: "Restore all " + g.windows.length + " windows", command: "restore-group", key: g.key})
    g.actions.forEach(function(a) { result.push({label: a.name, command: "launch", key: g.desktopId, extra: a.id}) })
    if(g.launcher && g.launcher.quicklistItems) g.launcher.quicklistItems.forEach(function(a) { result.push({label:a.label, enabled:a.enabled, command:"quicklist", key:g.desktopId, extra:String(a.id)}) })
    g.recent.forEach(function(r) { result.push({label: "Recent: " + r.name, command: "recent", key: g.desktopId, extra: r.uri}) })
    relatedSnaps.forEach(function(s) { result.push({label: "Recall " + s.name, snap: s.id}) })
    result.push({label: "Pin another application…", command: "pin-chooser", key: ""})
    result.push({label: "Combine: Always", command: "config", key: "combineMode", extra: "always"})
    result.push({label: "Combine: When taskbar is full", command: "config", key: "combineMode", extra: "when-full"})
    result.push({label: "Combine: Never", command: "config", key: "combineMode", extra: "never"})
    result.push({label: "Show windows on all displays", command: "config", key: "displayMode", extra: "all"})
    result.push({label: "Show windows on this display", command: "config", key: "displayMode", extra: "monitor"})
    result.push({label: "Taskbar: Current desktop", command: "config", key: "desktopScope", extra: "current"})
    result.push({label: "Taskbar: All desktops", command: "config", key: "desktopScope", extra: "all"})
    result.push({label: "Alt+Tab: Current desktop", command: "config", key: "switcherScope", extra: "current"})
    result.push({label: "Alt+Tab: All desktops", command: "config", key: "switcherScope", extra: "all"})
    return result
  }
  function openGroup(index, menu) {
    diagnosticPopupEpoch++
    if (index < 0 || index >= groups.length) return
    popupIndex = index
    popupKey = groups[index].displayKey
    keyboardMode = false
    selectedWindowIndex = 0
    menuMode = menu
    popupOpen = true
    popupFlickable.contentY = 0
    if(menu && groups[index].desktopId && groups[index].launcher && groups[index].launcher.quicklist)
      runArgs([homeDir + "/.local/bin/hypr-taskbar", "quicklist-show", groups[index].desktopId])
    closeDelay.stop()
    if (bar) bar.hideTooltip(stableAnchor)
  }
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
  function motionDispatch(method,request) {
    var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
    var accepted=false
    items.forEach(function(item) { if(item && item.motionReceive && item.motionReceive(method,request))accepted=true })
    return accepted
  }
  function motionVisualStateFor() { return windowMotion.visualState() }
  function motionReceive(method,request) {
    if(!barScreen || !request.target || request.target.screenName!==barScreen.name)return false
    if(method==="freeze")return windowMotion.freeze(request)
    if(method==="begin")return windowMotion.begin(request)
    if(method==="start")return windowMotion.start(request)
    windowMotion.cancel(request);return true
  }
  WindowMotion { id: windowMotion; owner: root }
  function update(output) {
    try {
      var data = JSON.parse(output)
      reducedMotion = Boolean(data.reducedMotion)
      taskbarSettings = data.settings || {}
      monitors = data.monitors || []
      var next = JSON.stringify(data.groups.map(function(g) {
        return [g.key, g.desktopId, g.name, g.icon, g.pinned, g.actions, g.recent, g.launcher, g.windows.map(function(w) { return [w.address, w.pid, w.stableId, w.title, w.workspace.name, w.homeWorkspace, w.homePinned, w.homeMonitor, w.monitor, w.previewReady, w.urgent] })]
      })) + JSON.stringify(data.snapGroups)
      if (signature !== next) {
        signature = next
        appGroups = data.groups
        snapGroups = data.snapGroups
      }
      if (!popupGroup) popupOpen = false
      else popupIndex = groups.findIndex(function(g) { return g.displayKey === root.popupKey })
      if (data.focusedAddress !== focusedAddress) {
        focusedAddress = data.focusedAddress
        captureAddress = focusedAddress
        if(captureAddress) captureDelay.restart()
      }
    } catch (e) { console.warn("Taskbar snapshot: " + e) }
  }

  function handleKeyboard(event) {
        if(event.key===Qt.Key_Escape) { root.popupOpen=false; root.keyboardMode=false; event.accepted=true }
        else if(event.key===Qt.Key_Left || event.key===Qt.Key_Right) { var step=event.key===Qt.Key_Left ? -1 : 1; root.openGroup((root.popupIndex+step+root.groups.length)%root.groups.length,false); root.keyboardMode=true; event.accepted=true }
        else if(event.key===Qt.Key_Up || event.key===Qt.Key_Down) {
          var count = root.menuMode ? root.menuItems.length : root.popupGroup ? root.popupGroup.windows.length : 0
          if(count) {
            var step = event.key===Qt.Key_Up ? -1 : 1
            var next = root.selectedWindowIndex
            for(var tried=0;tried<count;tried++) { next=(next+step+count)%count; if(!root.menuMode || root.menuItems[next].enabled !== false) break }
            root.selectedWindowIndex=next
          }
          event.accepted=true
        }
        else if(event.key===Qt.Key_Return || event.key===Qt.Key_Enter) {
          if(root.menuMode) { var item=root.menuItems[root.selectedWindowIndex%root.menuItems.length]; if(item && item.enabled !== false) { if(item.snap) root.recall(item.snap); else root.taskbarAction(item.command,item.key,item.extra) } }
          else if(root.popupGroup.windows.length) root.windowAction("restore",root.popupGroup.windows[root.selectedWindowIndex%root.popupGroup.windows.length].address)
          else if(root.popupGroup.desktopId) root.taskbarAction("launch",root.popupGroup.desktopId)
          event.accepted=true
        }
      }
  implicitWidth: Math.min(maxWidth, row.implicitWidth) + 43
  implicitHeight: barSize

  Process {
    id: snapshotProcess
    onStarted: root.qaStarted("snapshot",snapshotProcess)
    onExited: function(code,status) { root.qaExited("snapshot",code,status) }
    command: [root.homeDir + "/.local/bin/hypr-taskbar", "snapshot"]
    stdout: StdioCollector { waitForEnd: true; onStreamFinished: root.update(text) }
  }
  Process {
    id: actionProcess
    onStarted: root.qaStarted("action",actionProcess)
    onExited: function(code,status) {
      root.qaExited("action",code,status)
      if (code !== 0) console.warn("Taskbar action failed with code " + code)
      root.refresh()
      queueDelay.restart()
    }
  }
  Timer { id: queueDelay; interval: 10; onTriggered: root.drainQueue() }
  Process {
    id: captureProcess
    onStarted: root.qaStarted("capture",captureProcess)
    command: [root.homeDir + "/.local/bin/hypr-window-preview", "capture-both", root.captureAddress, String((root.previewRevision + 1) % 2)]
    onExited: function(code,status) { root.qaExited("capture",code,status); root.previewRevision++; root.refresh() }
  }
  Process {
    id: allCaptureProcess
    onStarted: root.qaStarted("allCapture",allCaptureProcess)
    command: [root.homeDir + "/.local/bin/hypr-window-preview", "capture-all"]
    onExited: function(code,status) { root.qaExited("allCapture",code,status); root.previewRevision++; root.refresh() }
  }
  Timer { id: qaAllCapturePoll; interval: 10000; repeat: true; running: root.ipcOwner && !root.qaTerminalQuiesced; triggeredOnStart: true; onTriggered: if (!root.qaTerminalQuiesced && !allCaptureProcess.running) { root.qaRequested("allCapture",allCaptureProcess.command); allCaptureProcess.running = true } }
  Timer { id: captureDelay; interval: 450; onTriggered: if (!root.qaTerminalQuiesced && !captureProcess.running && root.captureAddress) { root.qaRequested("capture",captureProcess.command); captureProcess.running = true } }
  Timer {
    id: closeDelay
    interval: 250
    onTriggered: if (!previewCard.containsMouse && !taskHover.containsMouse && !taskDrop.containsDrag && !root.fileDragOnTaskbar && !root.filePreviewWindow && !root.previewDragActive() && !root.menuMode && !root.keyboardMode) root.popupOpen = false
  }
  Timer { id: qaCapturePoll; interval: 3000; repeat: true; running: !root.qaTerminalQuiesced; onTriggered: if (!root.qaTerminalQuiesced && root.focusedAddress && !captureProcess.running) { root.captureAddress=root.focusedAddress; root.qaRequested("capture",captureProcess.command); captureProcess.running=true } }
  Timer { id: qaSnapshotPoll; interval: 900; repeat: true; running: !root.qaTerminalQuiesced; triggeredOnStart: true; onTriggered: root.refresh() }

  Flickable {
    id: tasksFlickable
    anchors.left: taskViewButton.right; anchors.top: parent.top; anchors.bottom: parent.bottom; anchors.right: desktopButton.left
    contentWidth: row.implicitWidth
    contentHeight: height
    clip: true
    interactive: contentWidth > width
    boundsBehavior: Flickable.StopAtBounds
    Row {
      id: row
      spacing: 3
      height: root.barSize
      Repeater {
        id: taskRepeater
        model: taskCards
        Item {
          id: taskItem
          property alias motionIcon: appIcon
          required property string payload
          readonly property var modelData: JSON.parse(payload)
          required property int index
          Accessible.role: Accessible.Button
          Accessible.id: "taskbar-app:" + modelData.displayKey
          Accessible.name: modelData.name
          Accessible.description: modelData.windows.length + " windows" + (modelData.pinned ? ", pinned to taskbar" : "") + (active ? ", active" : minimized ? ", minimized" : ", running") + (modelData.windows.some(function(w) { return w.urgent }) ? ", needs attention" : "")
          Accessible.selectable: true
          Accessible.selected: active
          Accessible.onPressAction: {
            if (!visible) return
            root.activateGroup(index)
            if (root.popupOpen) root.keyboardMode = true
          }
          function accessibleShowMenu() {
            if (!visible) return
            root.openGroup(index, true)
            root.keyboardMode = true
          }
          readonly property bool active: modelData.windows.some(function(w) { return w.address === root.focusedAddress && w.workspace.name !== "special:win-minimized" })
          readonly property bool minimized: modelData.windows.length > 0 && modelData.windows.every(function(w) { return w.workspace.name === "special:win-minimized" })
          width: root.widthFor(modelData)
          height: root.barSize
          Image {
            id: appIcon
            width: 19; height: 19
            x: root.uncombined ? 8 : (parent.width-width)/2
            anchors.verticalCenter: parent.verticalCenter
            source: root.iconSource(taskItem.modelData)
            sourceSize.width: width * Screen.devicePixelRatio
            sourceSize.height: height * Screen.devicePixelRatio
            fillMode: Image.PreserveAspectFit
            asynchronous: true
            opacity: taskItem.minimized ? 0.55 : 1
          }
          Rectangle {
            width: 7; height: 7; radius: 4
            x: appIcon.x + appIcon.width - 2
            y: appIcon.y - 2
            visible: taskItem.modelData.windows.some(function(w) { return w.urgent === true }) || Boolean(taskItem.modelData.launcher && taskItem.modelData.launcher.urgent)
            color: Color.urgent
          }
          Rectangle {
            id: countBadge
            visible: Boolean(taskItem.modelData.launcher && taskItem.modelData.launcher["count-visible"]) && taskItem.modelData.launcher.count > 0
            anchors.right: parent.right; anchors.top: parent.top
            anchors.rightMargin: 1; anchors.topMargin: 1
            width: badgeText.implicitWidth + 6; height: 13; radius: 6
            color: Color.accent
            Text {
              id: badgeText
              anchors.centerIn: parent
              text: !countBadge.visible ? "" : taskItem.modelData.launcher.count > 99 ? "99+" : String(taskItem.modelData.launcher.count)
              color: Color.background; font.pixelSize: 9; font.bold: true
            }
          }
          Rectangle {
            visible: Boolean(taskItem.modelData.launcher && taskItem.modelData.launcher["progress-visible"])
            width: parent.width - 12; height: 3; radius: 1
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom; anchors.bottomMargin: 4
            color: Qt.alpha(Color.accent, 0.25)
            Rectangle {
              width: parent.width * Math.max(0, Math.min(1, taskItem.modelData.launcher.progress || 0))
              height: parent.height; radius: parent.radius; color: Color.accent
            }
          }
          Text {
            anchors.centerIn: parent
            visible: appIcon.status !== Image.Ready
            text: taskItem.modelData.name.substring(0, 1).toUpperCase()
            color: root.bar ? root.bar.barForeground : Color.foreground
            font.pixelSize: 13
          }
          Text {
            visible: root.uncombined && taskItem.modelData.windows.length > 0
            anchors.left: appIcon.right; anchors.leftMargin: 6; anchors.right: parent.right; anchors.rightMargin: 6; anchors.verticalCenter: parent.verticalCenter
            text: taskItem.modelData.windows.length ? taskItem.modelData.windows[0].title : taskItem.modelData.name
            elide: Text.ElideRight; textFormat: Text.PlainText; color: Color.foreground; font.pixelSize: 11
          }
          Text {
            anchors.right: parent.right; anchors.top: parent.top
            anchors.topMargin: 2
            visible: taskItem.modelData.windows.length > 1 && !countBadge.visible
            text: String(taskItem.modelData.windows.length)
            color: Color.foreground
            font.pixelSize: 9
          }
          Rectangle {
            width: parent.width - 12; height: 2; radius: 1
            visible: taskItem.modelData.windows.length > 0
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            color: Color.accent
            opacity: taskItem.active ? 1 : taskItem.minimized ? 0.15 : 0.45
          }
        }
      }
    }
    DropArea {
      id: taskDrop
      anchors.fill: parent
      onEntered: function(drag) { root.dragEntries++; root.beginDragGroup(drag.x); closeDelay.stop() }
      onPositionChanged: function(drag) { root.beginDragGroup(drag.x) }
      onExited: { root.stopDragHover(); closeDelay.restart() }
      onDropped: function(drop) { drop.accepted=false; root.stopDragHover(); root.popupOpen=false }
    }
    MouseArea {
      id: taskHover
      anchors.fill: parent
      hoverEnabled: true
      acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
      cursorShape: Qt.PointingHandCursor
      property int pressedIndex: -1
      property real pressedX: 0
      property bool reordered: false
      function indexAt(x) {
        var px=x+tasksFlickable.contentX
        for(var i=0;i<root.groups.length;i++) if(px>=root.positionFor(i) && px<root.positionFor(i)+root.widthFor(root.groups[i])) return i
        return -1
      }
      function hoverAt(x) {
        if (root.menuMode && root.popupOpen || pressed) return
        var index = indexAt(x)
        if (index < 0) { closeDelay.restart(); return }
        if (root.popupKey !== root.groups[index].displayKey || !root.popupOpen) root.openGroup(index, false)
        else closeDelay.stop()
      }
      onEntered: hoverAt(mouseX)
      onPositionChanged: function(mouse) { hoverAt(mouse.x) }
      onExited: if (!root.menuMode) closeDelay.restart()
      onPressed: function(mouse) { pressedIndex = indexAt(mouse.x); pressedX = mouse.x; reordered = false }
      onReleased: function(mouse) {
        var target = indexAt(mouse.x)
        if (mouse.button === Qt.LeftButton && pressedIndex >= 0 && target >= 0 && target !== pressedIndex && Math.abs(mouse.x - pressedX) > 10) {
          reordered = true
          root.taskbarAction("reorder", root.groups[pressedIndex].key, root.groups[target].key)
        }
      }
      onClicked: function(mouse) {
        if (reordered) return
        var index = indexAt(mouse.x)
        if (index < 0) return
        var g = root.groups[index]
        if (mouse.button === Qt.RightButton) { root.openGroup(index, true); return }
        if (mouse.button === Qt.MiddleButton || !g.windows.length) {
          if (g.desktopId) root.taskbarAction("launch", g.desktopId)
          return
        }
        if (g.windows.length > 1) { root.openGroup(index, false); return }
        var w = g.windows[0]
        root.windowAction("activate", w.address)
      }
    }
  }
  Rectangle {
    id: taskViewButton
    Accessible.role: Accessible.Button
    Accessible.name: "Task View"
    Accessible.onPressAction: { root.popupOpen=false; root.runArgs(["omarchy-shell","shell","toggle","hoskinson.taskview"]) }
    anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom
    width: 26; radius: 4; color: taskViewMouse.containsMouse ? Color.accent : "transparent"
    Text { anchors.centerIn: parent; text: "▦"; color: Color.foreground; font.pixelSize: 16 }
    MouseArea {
      id: taskViewMouse
      anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
      onClicked: { root.popupOpen=false; root.runArgs(["omarchy-shell","shell","toggle","hoskinson.taskview"]) }
    }
  }
  Rectangle {
    id: desktopButton
    Accessible.role: Accessible.Button
    Accessible.name: "Show desktop"
    Accessible.onPressAction: { peekDelay.stop(); root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","peek-off"]); root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","toggle"]) }
    anchors.right: parent.right; anchors.top: parent.top; anchors.bottom: parent.bottom
    width: 14; color: desktopMouse.containsMouse ? Color.accent : "transparent"
    Rectangle { width: 1; height: parent.height-12; anchors.centerIn: parent; color: Color.foreground; opacity: 0.4 }
    MouseArea {
      id: desktopMouse
      anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
      onEntered: peekDelay.restart()
      onExited: { peekDelay.stop(); root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","peek-off"]) }
      onClicked: { peekDelay.stop(); root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","peek-off"]); root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","toggle"]) }
    }
    Timer { id: peekDelay; interval: 600; onTriggered: root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","peek-on"]) }
  }
  Item {
    id: stableAnchor
    x: taskViewButton.width + root.positionFor(Math.max(0,root.popupIndex)) - tasksFlickable.contentX
    width: root.popupGroup ? root.widthFor(root.popupGroup) : root.buttonWidth; height: root.barSize
    opacity: 0; enabled: false
  }
  TaskbarPopup {
    id: previewCard
    keyboardMode: root.keyboardMode
    reducedMotion: root.reducedMotion
    anchorItem: stableAnchor
    bar: root.bar
    owner: QtObject { function close() { root.popupOpen = false; root.menuMode = false; root.keyboardMode = false } }
    triggerMode: root.menuMode || root.keyboardMode ? "click" : "hover"

    open: root.popupOpen && root.popupGroup !== null
    contentWidth: 320
    contentHeight: Math.min(460, 44 + (root.menuMode ? root.menuItems.length * 32 : Math.max(1, root.popupGroup ? root.popupGroup.windows.length : 0) * 155 + (root.relatedSnaps.length ? 32 : 0)))
    onKeyboardModeChanged: { root.popupAccessibilityReady = false; if (keyboardMode) Qt.callLater(function() { popupKeyCatcher.forceActiveFocus(); root.popupAccessibilityReady = true }) }
    onContainsMouseChanged: {
      if (containsMouse || taskHover.containsMouse || taskDrop.containsDrag) closeDelay.stop()
      else if (root.popupOpen && !root.menuMode && !root.keyboardMode) closeDelay.restart()
    }
    Flickable {
      id: popupFlickable
      Accessible.role: Accessible.Dialog
      Accessible.name: root.menuMode ? "App actions" : "Window previews"
      Accessible.focused: false
      Accessible.ignored: !root.popupOpen
      anchors.fill: parent
      Item {
        id: popupKeyCatcher
        anchors.fill: parent
        Accessible.ignored: true
        focus: root.keyboardMode
        Keys.onPressed: function(event) { root.handleKeyboard(event) }
      }
      contentWidth: width
      contentHeight: popupColumn.implicitHeight
      clip: true
      boundsBehavior: Flickable.StopAtBounds
      MouseArea {
        anchors.fill: parent
        z: 10
        acceptedButtons: Qt.NoButton
        onWheel: function(event) { root.scrollPopup(event) }
      }
      Column {
        id: popupColumn
        width: parent.width
        spacing: 6
        Text {
          width: parent.width
          text: root.popupGroup ? root.popupGroup.name + (root.popupGroup.pinned ? " · Pinned" : "") : ""
          color: Color.foreground; font.pixelSize: 12
          elide: Text.ElideRight; textFormat: Text.PlainText
        }
        Repeater {
          id: menuRepeater
          model: root.menuMode ? menuCards : null
          Rectangle {
            required property string payload
            readonly property var modelData: JSON.parse(payload)
            required property int index
            enabled: modelData.enabled !== false
            Accessible.role: Accessible.MenuItem
            Accessible.name: modelData.label
            Accessible.focused: root.popupAccessibilityReady && root.popupOpen && root.keyboardMode && index === root.selectedWindowIndex
            Accessible.ignored: !root.popupOpen
            Accessible.checkable: modelData.command === "config" || modelData.command === "pin" || modelData.command === "unpin"
            Accessible.checked: modelData.command === "unpin" || (modelData.command === "config" && (root.taskbarSettings[modelData.key] || (modelData.key === "combineMode" ? "always" : modelData.key === "switcherScope" ? "current" : "all")) === modelData.extra)
            Accessible.onPressAction: {
              if (!root.popupOpen || !root.menuMode || !enabled) return
              if (modelData.snap) root.recall(modelData.snap)
              else root.taskbarAction(modelData.command, modelData.key, modelData.extra)
            }
            width: popupColumn.width; height: 26; radius: 4
            color: root.keyboardMode && root.selectedWindowIndex % root.menuItems.length === index || menuMouse.containsMouse ? Color.accent : "transparent"
            Text { anchors.fill: parent; anchors.leftMargin: 5; verticalAlignment: Text.AlignVCenter; text: modelData.label; color: Color.foreground; opacity: modelData.enabled === false ? 0.4 : 1; font.pixelSize: 11; elide: Text.ElideRight; textFormat: Text.PlainText }
            MouseArea {
              id: menuMouse
              onWheel: function(event) { root.scrollPopup(event) }
              anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
              enabled: modelData.enabled !== false
              onClicked: { if (modelData.snap) root.recall(modelData.snap); else root.taskbarAction(modelData.command, modelData.key, modelData.extra) }
            }
          }
        }
        Repeater {
          id: windowRepeater
          model: previewCards
          Rectangle {
            id: windowPreview
            required property string payload
            readonly property var modelData: JSON.parse(payload)
            required property int index
            Accessible.role: Accessible.Button
            Accessible.id: "taskbar-window:" + modelData.stableId
            Accessible.name: modelData.title || modelData.class || "Window"
            Accessible.description: (modelData.workspace.name === "special:win-minimized" ? "Minimized window" : "Open window") + (modelData.previewReady ? ", preview available" : ", preview unavailable")
            Accessible.focused: root.popupAccessibilityReady && root.popupOpen && root.keyboardMode && index === root.selectedWindowIndex
            Accessible.ignored: !root.popupOpen
            Accessible.onPressAction: if (root.popupOpen && !root.menuMode) root.windowAction("restore", modelData.address)
            readonly property bool fileDragActive: previewDrop.containsDrag
            width: popupColumn.width; height: 149; radius: 4
            color: root.keyboardMode && root.selectedWindowIndex % root.popupGroup.windows.length === index || windowMouse.containsMouse ? Color.accent : "transparent"
            Text {
              anchors.left: parent.left; anchors.right: closeButton.left; anchors.top: parent.top
              height: 24; anchors.leftMargin: 4
              text: (modelData.workspace.name === "special:win-minimized" ? "↓ " : "") + (modelData.title || "Window")
              color: Color.foreground; font.pixelSize: 11; elide: Text.ElideRight; textFormat: Text.PlainText
            }
            Image {
              anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
              height: 120; fillMode: Image.PreserveAspectFit
              source: windowPreview.modelData.previewReady ? "file://" + root.previewDir + "/" + windowPreview.modelData.address + "-" + (root.previewRevision % 2) + ".png" : ""
              cache: false; asynchronous: true
              Text { anchors.centerIn: parent; visible: parent.status !== Image.Ready; text: "Preview appears after window is focused"; color: Color.foreground; font.pixelSize: 10 }
            }
            MouseArea {
              id: windowMouse
              anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
              onWheel: function(event) { root.scrollPopup(event) }
              onClicked: root.windowAction("restore", windowPreview.modelData.address)
            }
            DropArea {
              id: previewDrop
              anchors.fill: parent
              property var capturedWindow: null
              onEntered: {
                capturedWindow=Object.assign({},windowPreview.modelData)
                closeDelay.stop()
                previewActivateDelay.restart()
              }
              onExited: { previewActivateDelay.stop(); capturedWindow=null; closeDelay.restart() }
              onDropped: function(drop) { drop.accepted=false; previewActivateDelay.stop(); capturedWindow=null; root.popupOpen=false }
              Timer { id: previewActivateDelay; interval: 600; onTriggered: if(previewDrop.containsDrag) root.activateDraggedWindow(previewDrop.capturedWindow) }
            }
            Rectangle {
              id: closeButton
              Accessible.role: Accessible.Button
              Accessible.name: "Close " + (windowPreview.modelData.title || windowPreview.modelData.class || "window")
              Accessible.ignored: !root.popupOpen
              Accessible.onPressAction: if (root.popupOpen && !root.menuMode) root.windowAction("close", windowPreview.modelData.address)
              anchors.right: parent.right; anchors.top: parent.top
              width: 24; height: 24; radius: 4
              color: closeMouse.containsMouse ? "#b73333" : "transparent"
              Text { anchors.centerIn: parent; text: "×"; color: Color.foreground; font.pixelSize: 16 }
              MouseArea {
                id: closeMouse
                onWheel: function(event) { root.scrollPopup(event) }
                anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                onClicked: root.windowAction("close", windowPreview.modelData.address)
              }
            }
          }
        }
        Repeater {
          model: !root.menuMode ? root.relatedSnaps : []
          Rectangle {
            required property var modelData
            Accessible.role: Accessible.Button
            Accessible.name: "Recall " + modelData.name
            Accessible.ignored: !root.popupOpen
            Accessible.onPressAction: if (root.popupOpen && !root.menuMode) root.recall(modelData.id)
            width: popupColumn.width; height: 26; radius: 4
            color: snapMouse.containsMouse ? Color.accent : "transparent"
            Text { anchors.fill: parent; verticalAlignment: Text.AlignVCenter; text: "Recall " + modelData.name; color: Color.foreground; font.pixelSize: 11; elide: Text.ElideRight; textFormat: Text.PlainText }
            MouseArea { id: snapMouse; onWheel: function(event) { root.scrollPopup(event) }; anchors.fill: parent; hoverEnabled: true; onClicked: root.recall(modelData.id) }
          }
        }
        Text {
          visible: !root.menuMode && root.popupGroup !== null && !root.popupGroup.windows.length
          width: parent.width; height: visible ? 30 : 0
          text: "Click to open · Right-click for actions"
          color: Color.foreground; font.pixelSize: 11
        }
      }
    }
  }
}

import QtQuick
import "file:///home/hoskinson/.local/share/omarchy-files-native/WindowAccessibilityV6_routing_20261001"
import Quickshell
import Quickshell.Io
import "explorer"
import "widget"
import qs.Commons

// Thin host: the desktop widget (panel plugin) + the explorer (window plugin).
// Run:  qs -p <this dir>      Drive:  qs -p <dir> ipc call files open ~/Documents
ShellRoot {
  // All initialization runs in reload order, before backing windows map.
  property bool uiReady: false
  property string migrationError: ""
  property var initializationState: ({})
  FileView { id: uiMigration; path: Quickshell.shellPath("ui-migration.json"); blockLoading: true; printErrors: false }
  PersistentProperties {
    id: uiPersist
    reloadableId: "files-ui-persistence-v1"
    property string uiJson: ""
    property string entriesJson: "[]"
    property string shownJson: "[]"
    onLoaded: {
      var resumed = uiJson.length > 0, restored = null
      try {
        if (resumed) restored = JSON.parse(uiJson)
        else {
          var text = uiMigration.text()
          if (text) {
            var m = JSON.parse(text)
            if (m.targetPid === Quickshell.processId && m.targetInstance === Quickshell.instanceId) {
              var s = m.legacyState
              if (!s || s.view !== "home" || s.entries !== 0 || s.count !== 0 || s.sel.length || s.clip.length || s.lb || m.promptInfo !== "none" || m.visible !== false)
                throw new Error("Legacy migration requires idle hidden Home, empty selection/clipboard, and no prompt")
              restored = { version:2, view:s.view, cwd:s.cwd, history:s.hist, hIdx:s.hIdx,
                filter:s.filter, searchLabel:s.searchLabel, errorText:"", showHidden:s.hidden,
                sortKey:s.sort.slice(0,-1), sortAsc:s.sort.slice(-1)==="+", viewMode:s.mode, collId:s.coll,
                zoom:s.zoom, detailOpen:s.detail, sel:({}), nsel:0, cur:s.cur, anchorIdx:-1, kbd:false,
                clip:({paths:[],cut:s.cut}), lbIdx:-1, lbOpen:false, visible:false,
                windowWidth:m.windowWidth || 1320, windowHeight:m.windowHeight || 800,
                sidebarRequested:false, detailOverlayRequested:false }
              resumed = true
            }
          }
        }
        explorer.initializeUi(restored, entriesJson, shownJson)
        initializationState = { resumed:resumed, visible:explorer.visible, backingVisible:explorer.backingWindowVisible, historyLength:explorer.history.length, historyIndex:explorer.hIdx }
        uiReady = true
        if (!resumed) {
          var o = Quickshell.env("FILES_OPEN")
          if (o) explorer.openAt(o === "home" ? "" : o, "")
        }
      } catch (e) { migrationError = String(e); explorer.visible = false; console.error("[files] UI migration failed: " + e) }
    }
  }
  Binding { target: uiPersist; property: "uiJson"; when: uiReady; value: explorer.exportUi() }
  Binding { target: uiPersist; property: "entriesJson"; when: uiReady; value: JSON.stringify(explorer.entries) }
  Binding { target: uiPersist; property: "shownJson"; when: uiReady; value: JSON.stringify(explorer.shown) }
  Connections { target: Quickshell; function onReloadCompleted() { Quickshell.inhibitReloadPopup() } }

  Widget {
    id: widget
    visible: Quickshell.env("FILES_WIDGET") === "1"
    onOpenRequested: (p, q) => explorer.openAt(p, q)
    onFileRequested: (p) => explorer.openFile(p)
    onSearchRequested: (q) => { explorer.openAt("", ""); explorer.go(Fs.home); explorer.deepSearch(q) }
  }
  Explorer { id: explorer }

  IpcHandler {
    target: "files"
    function open(path: string): void { explorer.openAt(path === "home" ? "" : (path.indexOf("coll:") === 0 ? path : Fs.norm(Fs.expand(path))), "") }
    function toggle(): void { explorer.visible = !explorer.visible }
    function act(name: string, arg: string): string { return explorer.act(name, arg) }
    function shot(which: string, path: string): void { if (which === "widget") widget.grab(path); else explorer.grab(path) }
    function state(): string { return explorer.state() }
    function uiState(): string { return explorer.exportUi() }
    function qaButtons(): string { return qaCollect() }
    function migrationStatus(): string { return JSON.stringify({ready:uiReady,error:migrationError,pid:Quickshell.processId,instance:Quickshell.instanceId,initialization:initializationState}) }
  }



  // QA-only read-only observations. Signal listener does not replace/delegate handlers.
  // Additional listeners can perturb timing: no cadence/raster claim.
  property var qaObservedItems: []
  property var qaClickEvents: []
  function qaCollect() {
    var rows=[], content=explorer.contentItem
    function walk(o) {
      if(o.accessibleName !== undefined && o.actionIdentity !== undefined && o.clicked !== undefined) {
        if(qaObservedItems.indexOf(o)<0) {
          qaObservedItems.push(o)
          o.clicked.connect(function(mouse){
            qaClickEvents.push({name:String(o.accessibleName),identity:String(o.actionIdentity),button:mouse.button,modifiers:mouse.modifiers,viewMode:explorer.viewMode,time:Date.now()})
          })
        }
        var point=o.mapToItem(content,0,0)
        rows.push({name:String(o.accessibleName),identity:String(o.actionIdentity),rect:[point.x,point.y,o.width,o.height],visible:o.visible,enabled:o.enabled,enabled2:o.enabled2,objectName:String(o.objectName)})
      }
      var children=o.children || [];for(var i=0;i<children.length;i++)walk(children[i])
    }
    walk(content)
    return JSON.stringify({pid:Quickshell.processId,instance:Quickshell.instanceId,client:[content.width,content.height],visible:explorer.visible,backingVisible:explorer.backingWindowVisible,viewMode:explorer.viewMode,buttons:rows,clicks:qaClickEvents})
  }
}

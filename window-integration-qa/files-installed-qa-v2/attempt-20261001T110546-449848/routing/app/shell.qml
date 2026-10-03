import QtQuick
import "file:///home/hoskinson/window-integration-qa/files-installed-qa-v2/attempt-20261001T110546-449848/routing/app/FixtureKeys"
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
  FileView { id: uiMigration; objectName: "shell.uiMigration"; path: Quickshell.shellPath("ui-migration.json"); blockLoading: true; printErrors: false }
  PersistentProperties {
    id: uiPersist; objectName: "shell.uiPersist"
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

  Explorer { id: explorer; objectName: "shell.explorer" }

  IpcHandler {
    target: "files-keyboard-qa"
    function open(path: string): void { explorer.openAt(path === "home" ? "" : (path.indexOf("coll:") === 0 ? path : Fs.norm(Fs.expand(path))), "") }
    function toggle(): void { explorer.visible = !explorer.visible }
    function act(name: string, arg: string): string { return explorer.act(name, arg) }
    function shot(which: string, path: string): void { explorer.grab(path) }

    property var retainedItem:null
    function key(key:int,mods:int):bool {return FixtureKeys.tap(explorer,key,mods)}
    function locus():string {return FixtureKeys.focus(explorer)}
    function focus(name:string):bool {
      function find(o) {if(o.objectName===name || o.accessibleName===name)return o;var a=o.children || [];for(var i=0;i<a.length;i++){var x=find(a[i]);if(x)return x};return null}
      var item=find(explorer.contentItem);if(!item)return false;item.forceActiveFocus();return true
    }
    function retain(name:string):string {
      function find(o) {if(o.objectName===name || o.accessibleName===name)return o;var a=o.children || [];for(var i=0;i<a.length;i++){var x=find(a[i]);if(x)return x};return null}
      retainedItem=find(explorer.contentItem);return FixtureKeys.retain(retainedItem)
    }
    function prepareText(text:string):bool {return FixtureKeys.prepareText(text)}
    function controlProperty(key:string,value:string):bool {return FixtureKeys.controlProperty(key,value)}
    function mutate(operation:string):string {return FixtureKeys.mutate(operation)}
    function dispatch(action:string):string {return FixtureKeys.dispatch(action)}
    function rawToggle():bool {return FixtureKeys.rawAttachedToggle()}
    function mappedSet(value:string):void {explorer.visible=value==="true"}
    function editorLifetime(value:string):void {explorer.qaEditorAlive=value==="true"}
    function resize(w:string,h:string):void {explorer.qaResize(w,h)}
    function scenario(name:string):void {explorer.qaScenario(name)}

    function state(): string { return explorer.state() }
    function uiState(): string { return explorer.exportUi() }
    function migrationStatus(): string { return JSON.stringify({ready:uiReady,error:migrationError,pid:Quickshell.processId,instance:Quickshell.instanceId,initialization:initializationState}) }
  }


}

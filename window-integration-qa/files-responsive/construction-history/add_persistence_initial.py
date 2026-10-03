from pathlib import Path
B=Path(__file__).parent/'app'
p=B/'explorer/Explorer.qml';s=p.read_text();s=s.replace('  title: "Files"','  reloadableId: "files-explorer-window-v1"\n  title: "Files"',1)
s=s.replace('  property string view: "home"','  property bool restoringUi: false\n  property string view: "home"',1)
s=s.replace('onFilterChanged: { if (view === "folder") rebuild();','onFilterChanged: { if (!restoringUi && view === "folder") rebuild();',1)
s=s.replace('onShowHiddenChanged: { rebuild(); tree.showHidden = showHidden; tree.init(function () { tree.reveal(cwd) }) }','onShowHiddenChanged: { tree.showHidden = showHidden; if (!restoringUi) { rebuild(); tree.init(function () { tree.reveal(cwd) }) } }',1)
s=s.replace('  Component.onCompleted: { tree.init(null) }','''  function initializeUi(snapshot, storedEntries, storedShown) {
    restoringUi = true
    if (snapshot) {
      view = snapshot.view; cwd = snapshot.cwd; history = snapshot.history; hIdx = snapshot.hIdx
      filter = snapshot.filter; searchLabel = snapshot.searchLabel; errorText = snapshot.errorText || ""
      showHidden = snapshot.showHidden; sortKey = snapshot.sortKey; sortAsc = snapshot.sortAsc; viewMode = snapshot.viewMode
      collId = snapshot.collId; zoom = snapshot.zoom; detailOpen = snapshot.detailOpen
      entries = JSON.parse(storedEntries || "[]"); shown = JSON.parse(storedShown || "[]")
      sel = snapshot.sel; nsel = snapshot.nsel; cur = snapshot.cur; anchorIdx = snapshot.anchorIdx; kbd = snapshot.kbd
      clip = snapshot.clip; lbIdx = snapshot.lbIdx; lbOpen = snapshot.lbOpen
      pendingSelect = snapshot.pendingSelect || ""; hiddenCount = snapshot.hiddenCount || 0
      sidebarRequested = snapshot.sidebarRequested && !sidebarDocked
      detailOverlayRequested = snapshot.detailOverlayRequested && !detailDocked
      if (snapshot.prompt) prompt.restoreUi(snapshot.prompt)
      if (snapshot.menu) { ctxTarget = snapshot.ctxTarget; ctx.restoreUi(snapshot.menu) }
      visible = snapshot.visible
      if (snapshot.windowWidth) implicitWidth = snapshot.windowWidth
      if (snapshot.windowHeight) implicitHeight = snapshot.windowHeight
      Qt.callLater(function () {
        area.scrollTo(snapshot.fileScroll || 0); dashboard.restoreScroll(snapshot.dashboardScroll || 0)
        if (snapshot.path) pathbar.restoreUi(snapshot.path)
        if (snapshot.focus === "filter") filterInput.forceActiveFocus()
        else if (snapshot.focus === "path" && snapshot.path && snapshot.path.editing) pathbar.restoreFocus()
        else if (!prompt.visible && !ctx.visible && snapshot.visible) focusMain()
      })
    }
    loading = false
    tree.init(function () { if (win.view === "folder" && !win.collId) tree.reveal(win.cwd) })
    restoringUi = false
  }
  function exportUi() {
    return JSON.stringify({ version: 2, view: view, cwd: cwd, history: history, hIdx: hIdx,
      filter: filter, searchLabel: searchLabel, errorText: errorText, showHidden: showHidden,
      sortKey: sortKey, sortAsc: sortAsc, viewMode: viewMode, collId: collId, zoom: zoom, detailOpen: detailOpen,
      sel: sel, nsel: nsel, cur: cur, anchorIdx: anchorIdx, kbd: kbd, clip: clip,
      lbIdx: lbIdx, lbOpen: lbOpen, pendingSelect: pendingSelect, hiddenCount: hiddenCount,
      sidebarRequested: sidebarRequested, detailOverlayRequested: detailOverlayRequested,
      visible: visible, windowWidth: width, windowHeight: height,
      fileScroll: area.scrollPosition(), dashboardScroll: dashboard.scrollPosition(),
      focus: filterInput.activeFocus ? "filter" : pathbar.editing ? "path" : "main",
      path: pathbar.exportUi(), prompt: prompt.exportUi(), menu: ctx.exportUi(), ctxTarget: ctxTarget })
  }''',1)
p.write_text(s)
p=B/'explorer/FileArea.qml';s=p.read_text().replace('  function scrollTo(y) {','  function scrollPosition() { return grid ? gridList.contentY : listView.contentY }\n\n  function scrollTo(y) {',1);p.write_text(s)
p=B/'explorer/Dashboard.qml';s=p.read_text().replace('  property string kindFilter: "all"','  function scrollPosition() { return fl.contentY }\n  function restoreScroll(y) { fl.contentY = y }\n  property string kindFilter: "all"',1);p.write_text(s)
p=B/'explorer/PathBar.qml';s=p.read_text().replace('  function startEdit() {','''  function exportUi() { return { editing: editing, text: input.text, cursor: input.cursorPosition, cands: cands, candIdx: candIdx, completing: completing } }
  function restoreUi(s) { input.text = s.text; cands = s.cands; candIdx = s.candIdx; completing = s.completing; editing = s.editing; input.cursorPosition = s.cursor }
  function restoreFocus() { input.forceActiveFocus() }

  function startEdit() {''',1);p.write_text(s)
p=B/'Ui/Prompt.qml';s=p.read_text().replace('  function ask(mode, title, initial, payload, opts) {','''  function exportUi() { return { visible: visible, title: title, hint: hint, confirmOnly: confirmOnly, danger: danger, okLabel: okLabel, mode: mode, payload: payload, text: input.text, scroll: promptScroll.contentY } }
  function restoreUi(s) { title=s.title; hint=s.hint; confirmOnly=s.confirmOnly; danger=s.danger; okLabel=s.okLabel; mode=s.mode; payload=s.payload; input.text=s.text; visible=s.visible; if(visible) Qt.callLater(function(){promptScroll.contentY=s.scroll; (root.confirmOnly ? card : input).forceActiveFocus()}) }

  function ask(mode, title, initial, payload, opts) {''',1);p.write_text(s)
p=B/'Ui/ContextMenu.qml';s=p.read_text().replace('  function openAt(x, y, its) {','''  function exportUi() { return { visible: visible, items: items, px: px, py: py, hi: hi, scroll: menuScroll.contentY } }
  function restoreUi(s) { items=s.items; px=s.px; py=s.py; hi=s.hi; visible=s.visible; if(visible) Qt.callLater(function(){menuScroll.contentY=s.scroll;card.forceActiveFocus()}) }

  function openAt(x, y, its) {''',1);p.write_text(s)
p=B/'shell.qml';s=p.read_text();a=s.index('  Component.onCompleted: {');s=s[:a]+'''  // All initialization runs in reload order, before backing windows map.
  property bool uiReady: false
  property string migrationError: ""
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
}
'''
# PersistentProperties must reload before Explorer, even though every object is already constructed.
a=s.index('  // All initialization runs');persist=s[a:s.rfind('\n}')];s=s[:a]+s[s.rfind('\n}'):];at=s.index('  Widget {');s=s[:at]+persist+'\n\n'+s[at:]
s=s.replace('    function state(): string { return explorer.state() }','''    function state(): string { return explorer.state() }
    function uiState(): string { return explorer.exportUi() }
    function migrationStatus(): string { return JSON.stringify({ready:uiReady,error:migrationError,pid:Quickshell.processId,instance:Quickshell.instanceId}) }''',1);p.write_text(s)
print('Staged scalar-JSON persistence and guarded idle legacy migration')

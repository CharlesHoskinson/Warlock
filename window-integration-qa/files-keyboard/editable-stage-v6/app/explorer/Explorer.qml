import "file:///home/hoskinson/window-integration-qa/files-keyboard/editable-stage-v6/WindowAccessibilityV6"
import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

// The explorer. A regular toplevel (FloatingWindow), deliberately:
//  - it is a document-style app the user alt-tabs / tiles / workspace-moves like any other,
//    which layer-shell surfaces cannot do (no tiling, no focus stacking, no window rules);
//  - Hyprland draws the native 2px accent border around it, so it looks first-party for free;
//  - keyboard focus is normal (no exclusive grab), so it never traps input.
FloatingWindow {
  id: win
  reloadableId: "files-explorer-window-v1"
  title: "Files"
  implicitWidth: 1320
  implicitHeight: 800
  minimumSize: Qt.size(330, 320)
  color: Theme.bg
  visible: false
  // Closing the window (X / compositor close) must reset `visible`, otherwise
  // the next `visible = true` is a no-op and the launcher can never reopen it.
  onClosed: visible = false

  // ------------------------------------------------------------------ state
  property bool restoringUi: false
  property string view: "home"            // "home" | "folder"
  property string cwd: Fs.home
  property var history: [""]               // "" = Home dashboard
  property int hIdx: 0
  property var entries: []
  property var shown: []
  property bool loading: false
  property string errorText: ""
  property string filter: ""
  property string searchLabel: ""          // non-empty => showing deep-search results
  property bool showHidden: false
  property string sortKey: "name"
  property bool sortAsc: true
  property string viewMode: "grid"
  property string collId: ""              // non-empty => showing a smart collection
  property int zoom: 200                  // grid card width
  property bool detailOpen: true
  property bool sidebarRequested: false
  property bool detailOverlayRequested: false
  readonly property bool narrowToolbar: content.width < 600
  readonly property bool compactToolbar: content.width < 1000
  readonly property bool sidebarDocked: content.width >= 900
  readonly property bool detailDocked: main.width >= 650
  onSidebarDockedChanged: if (!restoringUi) sidebarRequested = false
  onDetailDockedChanged: if (!restoringUi) detailOverlayRequested = false
  onNselChanged: if (!nsel) detailOverlayRequested = false
  property bool lbOpen: false
  property int lbIdx: -1
  property var sel: ({})
  property int nsel: 0
  property int cur: -1
  property int anchorIdx: -1
  property bool kbd: false
  property var clip: ({ paths: [], cut: false })
  property int loadSeq: 0
  readonly property bool dry: Quickshell.env("FILES_DRYRUN") === "1"

  readonly property string curPath: (view === "home" || collId) ? "" : cwd
  readonly property bool canWrite: view === "folder" && !collId && !searchLabel
  readonly property var collInfo: collId ? Data.collInfo(collId) : null
  readonly property string areaTitle: collId ? (collInfo ? collInfo.name : collId) : (searchLabel ? "Search" : (cwd === Fs.home ? "Home" : Fs.base(cwd)))
  readonly property string areaSub: {
    var nd = 0, nf = 0, bytes = 0
    for (var i = 0; i < shown.length; i++) { if (shown[i].isDir) nd++; else { nf++; bytes += shown[i].size } }
    var s = shown.length + (shown.length === 1 ? " item" : " items") + (nf ? "  ·  " + Fs.size(bytes) : "")
    if (collId) return "Smart collection  ·  live  ·  " + s
    if (searchLabel) return searchLabel.replace(/^Search “/, "“") + "  ·  " + s
    return Fs.tilde(cwd) + "  ·  " + s
  }

  function toast(msg) { toastText.text = msg; toastBox.opacity = 1; toastTimer.restart() }
  function log(m) { console.log("[files] " + m) }

  // -------------------------------------------------------------- navigation
  function openAt(path, query) {
    visible = true
    if (!path) go("", false)
    else go(path, false)
    if (query) { filter = query; rebuild() }
    win.requestActivate && win.requestActivate()
  }
  function go(target, fromHistory) {
    sidebarRequested = false; detailOverlayRequested = false
    target = target === undefined || target === "" ? "" : (String(target).indexOf("coll:") === 0 ? target : Fs.norm(target))
    if (fromHistory !== true) {
      var h = history.slice(0, hIdx + 1)
      if (h[h.length - 1] !== target || searchLabel) h.push(target)
      history = h; hIdx = h.length - 1
    }
    filter = ""; searchLabel = ""; errorText = ""; lbOpen = false
    clearSel()
    if (target.indexOf("coll:") === 0) { openColl(target.slice(5)); return }
    collId = ""
    if (target === "") { view = "home"; entries = []; shown = []; tree.current = ""; focusMain(); return }
    view = "folder"
    loadDir(target, null)
  }
  function openColl(id) {
    var info = Data.collInfo(id)
    if (!info) return
    view = "folder"; collId = id; loading = false; errorText = ""; cur = -1
    sortKey = info.bySize ? "size" : "modified"; sortAsc = false
    viewMode = "grid"
    entries = Data.collEntries(id).slice()
    tree.current = ""
    rebuild(); focusMain()
  }
  Connections {
    target: Data
    function onCollRevChanged() { if (win.collId) { win.entries = Data.collEntries(win.collId).slice(); win.rebuild() } }
  }
  function loadDir(path, then) {
    var seq = ++loadSeq
    loading = true
    Fs.list(path, function (es) {
      if (seq !== loadSeq) return
      loading = false
      if (es === null) {
        errorText = "Cannot open " + Fs.tilde(path)
        if (view === "folder" && entries.length === 0 && path !== cwd) {}
        toast("Cannot open " + Fs.tilde(path))
        return
      }
      cwd = path; entries = es; errorText = ""
      tree.current = path; tree.reveal(path)
      rebuild()
      if (then) then()
      focusMain()
    })
  }
  function openFile(p) { visible = true; go(Fs.parent(p)); pendingSelect = p; win.requestActivate && win.requestActivate() }
  function refresh(then) { if (collId) { Data.refreshCollections(); return } if (view === "folder") { var keep = Object.keys(sel); loadDir(cwd, function () { reselect(keep); if (then) then() }) } }
  function reselect(paths) {
    var o = {}, n = 0
    for (var i = 0; i < shown.length; i++) if (paths.indexOf(shown[i].path) >= 0) { o[shown[i].path] = true; n++ }
    sel = o; nsel = n
  }
  function back() { if (hIdx > 0) { hIdx--; go(history[hIdx], true) } }
  function forward() { if (hIdx < history.length - 1) { hIdx++; go(history[hIdx], true) } }
  function up() { if (collId) go(""); else if (view === "folder" && !searchLabel) { if (cwd === "/") return; var from = cwd; go(Fs.parent(cwd)); pendingSelect = from } else if (searchLabel) go(cwd) }
  property string pendingSelect: ""

  function deepSearch(q) {
    if (!q.length) return
    var base = (view === "folder" && !collId) ? cwd : Fs.home
    if (view !== "folder" || collId) { view = "folder"; if (collId) { collId = ""; cwd = Fs.home; base = Fs.home } else cwd = base; tree.current = base }
    loading = true; searchLabel = "Search “" + q + "” in " + Fs.tilde(base); filter = ""
    var seq = ++loadSeq
    Fs.search(base, q, function (es) {
      if (seq !== loadSeq) return
      loading = false; entries = es; rebuild(); clearSel()
    })
  }

  // ----------------------------------------------------------- list building
  function rebuild() {
    var f = filter.toLowerCase(), arr = []
    for (var i = 0; i < entries.length; i++) {
      var e = entries[i]
      if (!showHidden && e.hidden) continue
      if (f && e.name.toLowerCase().indexOf(f) < 0) continue
      arr.push(e)
    }
    Fs.sortEntries(arr, sortKey, sortAsc)
    shown = arr
    var keep = Object.keys(sel)
    if (pendingSelect) {
      for (var k = 0; k < arr.length; k++) if (arr[k].path === pendingSelect) { selectOnly(k); area.ensure(k); break }
      pendingSelect = ""
    } else {
      reselect(keep)
      if (cur >= arr.length) cur = arr.length - 1
      if (filter && arr.length) { if (cur < 0 || nsel === 0) { cur = 0 } }
    }
    hiddenCount = 0
    for (var j = 0; j < entries.length; j++) if (entries[j].hidden) hiddenCount++
  }
  property int hiddenCount: 0
  onFilterChanged: { if (!restoringUi && view === "folder") rebuild(); if (filter.length === 0) filterInput.text = ""; else if (filterInput.text !== filter) filterInput.text = filter }
  onShowHiddenChanged: { tree.showHidden = showHidden; if (!restoringUi) { rebuild(); tree.init(function () { tree.reveal(cwd) }) } }
  function setSort(k) { if (sortKey === k) sortAsc = !sortAsc; else { sortKey = k; sortAsc = k === "name" || k === "kind" } rebuild() }

  // --------------------------------------------------------------- selection
  function clearSel() { sel = ({}); nsel = 0 }
  function selectOnly(i) {
    if (i < 0 || i >= shown.length) { clearSel(); return }
    var o = {}; o[shown[i].path] = true; sel = o; nsel = 1; cur = i; anchorIdx = i
  }
  function selectRange(a, b) {
    var o = {}, lo = Math.min(a, b), hi = Math.max(a, b)
    for (var i = lo; i <= hi; i++) o[shown[i].path] = true
    sel = o; nsel = hi - lo + 1; cur = b
  }
  function clickItem(i, mods) {
    kbd = false
    if (mods & Qt.ControlModifier) {
      var o = Object.assign({}, sel), p = shown[i].path
      if (o[p]) delete o[p]; else o[p] = true
      sel = o; nsel = Object.keys(o).length; cur = i; anchorIdx = i
    } else if (mods & Qt.ShiftModifier && anchorIdx >= 0) selectRange(anchorIdx, i)
    else selectOnly(i)
    focusMain()
  }
  function rightClick(i) { if (!sel[shown[i].path]) selectOnly(i) }
  function moveCur(d, extend) {
    if (!shown.length) return
    kbd = true
    var ni = Math.max(0, Math.min(shown.length - 1, (cur < 0 ? (d > 0 ? -1 : shown.length) : cur) + d))
    if (extend) { if (anchorIdx < 0) anchorIdx = cur < 0 ? 0 : cur; selectRange(anchorIdx, ni) }
    else selectOnly(ni)
    area.ensure(ni)
    if(!filterInput.activeFocus) area.focusEntry(ni)
  }
  function selectAll() { if (shown.length) { selectRange(0, shown.length - 1); anchorIdx = 0 } }
  function selectedEntries() { return shown.filter(function (e) { return sel[e.path] }) }
  function selectedPaths() { return selectedEntries().map(function (e) { return e.path }) }

  // ------------------------------------------------------------------ actions
  function openPath(p) {
    if (dry) { log("xdg-open " + p); return }
    Quickshell.execDetached(["xdg-open", p])
  }
  function openEntry(e) { if (e.isDir) go(e.path); else openPath(e.path) }
  function openSelection() {
    var s = selectedEntries()
    if (!s.length && cur >= 0) s = [shown[cur]]
    if (s.length === 1) openEntry(s[0])
    else for (var i = 0; i < s.length; i++) if (!s[i].isDir) openPath(s[i].path)
  }
  function revealEntry(e) { go(Fs.parent(e.path)); pendingSelect = e.path }

  // elevated: run through scripts/elevate.sh (sudo-askpass popup, root-owned ops.sh)
  function runOp(args, done, elevated) {
    log((elevated ? "op(root) " : "op ") + args.join(" "))
    Fs.run(["bash", Fs.script(elevated ? "elevate.sh" : "ops.sh")].concat(args), function (txt, code) {
      if (code === 13 && !elevated) { askElevate(args, done); return }
      if (code === 77) toast("Authorization cancelled — nothing was changed")
      else if (code === 126) toast("Administrator helper missing (/usr/local/lib/omarchy-files/ops.sh)")
      else if (code !== 0) toast(opError(args[0], code))
      else if (elevated) toast("Done as administrator")
      if (done) done(txt, code)
    })
  }
  function askElevate(args, done) {
    var trash = args[0] === "trash"
    prompt.ask("elevate", "Administrator access needed", "", { args: args, done: done }, {
      confirm: true, danger: trash, ok: "Authorize…",
      hint: "You don’t have permission for this. Run it as administrator? Your password is asked in a popup."
        + (trash ? " Items go to root’s trash." : "")
    })
    refresh()
  }
  // ops.sh exit codes (see scripts/ops.sh and spec/fileops.qnt)
  function opError(op, code) {
    switch (code) {
      case 2: return "A file with that name already exists"
      case 3: return "Can’t put a folder inside itself"
      case 4: return "That name isn’t allowed"
      case 13: return "Permission denied — this folder needs administrator access"
      default: return "Operation failed (" + op + ")"
    }
  }
  function copySel(cut) {
    var p = selectedPaths(); if (!p.length) return
    clip = { paths: p, cut: cut }
    toast((cut ? "Cut " : "Copied ") + p.length + (p.length > 1 ? " items" : " item"))
  }
  function paste() {
    if (!canWrite || !clip.paths.length) return
    var c = clip, op = c.cut ? "move" : "copy"
    runOp([op, cwd].concat(c.paths), function (t, code) {
      if (code === 0) toast((c.cut ? "Moved " : "Pasted ") + c.paths.length + (c.paths.length > 1 ? " items" : " item"))
      if (c.cut) clip = ({ paths: [], cut: false })
      refresh()
    })
  }
  function duplicate() {
    var p = selectedPaths(); if (!p.length || !canWrite) return
    runOp(["copy", cwd].concat(p), function () { refresh(); toast("Duplicated") })
  }
  function newFolder() { if (canWrite) prompt.ask("mkdir", "New folder", "New folder", null, { hint: "in " + Fs.tilde(cwd), ok: "Create" }) }
  function newFile() { if (canWrite) prompt.ask("newfile", "New file", "Untitled.txt", null, { hint: "in " + Fs.tilde(cwd), ok: "Create" }) }
  function renameSel() {
    var s = selectedEntries(); if (s.length !== 1) return
    prompt.ask("rename", "Rename", s[0].name, s[0], { hint: "Renaming " + (s[0].isDir ? "folder" : "file"), ok: "Rename" })
  }
  function trashSel() {
    var s = selectedEntries(); if (!s.length) return
    var t = s.length === 1 ? "Move “" + s[0].name + "” to Trash?" : "Move " + s.length + " items to Trash?"
    prompt.ask("trash", t, "", s.map(function (e) { return e.path }), { confirm: true, danger: true, ok: "Move to Trash", hint: "Recoverable from the trash (gio trash)." })
  }
  function copyPathText() {
    var s = selectedPaths(); var t = s.length ? s.join("\n") : cwd
    if (dry) { log("copy-path " + t); return }
    Quickshell.execDetached(["wl-copy", t]); toast("Path copied")
  }
  function termHere() { if (!dry) Quickshell.execDetached({ command: ["xdg-terminal-exec"], workingDirectory: cwd }); else log("terminal " + cwd) }

  function promptDone(mode, text, payload) {
    text = text.trim()
    if (mode === "mkdir" || mode === "newfile") {
      if (!text.length) return
      runOp([mode, cwd, text], function (out) { var np = out.trim(); refresh(function () { for (var i = 0; i < shown.length; i++) if (shown[i].path === np) { selectOnly(i); area.ensure(i) } }) })
    } else if (mode === "rename") {
      if (!text.length || text === payload.name || text.indexOf("/") >= 0) return
      var np = Fs.parent(payload.path) + "/" + text
      runOp(["rename", payload.path, np], function (o, code) { if (code === 2) toast("“" + text + "” already exists"); refresh(function () { for (var i = 0; i < shown.length; i++) if (shown[i].path === np) { selectOnly(i); area.ensure(i) } }) })
    } else if (mode === "elevate") {
      runOp(payload.args, payload.done, true)
    } else if (mode === "trash") {
      runOp(["trash"].concat(payload), function (o, code) { if (code === 0) toast("Moved " + payload.length + (payload.length > 1 ? " items" : " item") + " to Trash"); clearSel(); refresh() })
    }
    focusMain()
  }

  // ---------------------------------------------------------------- lightbox
  function openLightbox() {
    if (view !== "folder" || !shown.length) return
    var i = cur >= 0 ? cur : (nsel ? shown.findIndex(function (e) { return sel[e.path] }) : 0)
    if (i < 0) i = 0
    lbIdx = i; lbOpen = true
    if (!sel[shown[i].path]) selectOnly(i)
  }
  function lbMove(d) {
    if (!shown.length) return
    lbIdx = Math.max(0, Math.min(shown.length - 1, lbIdx + d))
    selectOnly(lbIdx); area.ensure(lbIdx)
  }
  function toggleDetail() {
    if (detailDocked) detailOpen = !detailOpen
    else { detailOverlayRequested = !detailOverlayRequested; if (detailOverlayRequested) detailOpen = true }
  }
  function closeDetail() { detailOpen = false; detailOverlayRequested = false }

  // ----------------------------------------------------------------- menus
  function menuFor(idx) {
    var one = nsel === 1, any = nsel > 0, res = !!(collId || searchLabel)
    if (view !== "folder") return []
    if (!any && res) return [ { label: "Refresh", icon: "\uf021", action: "refresh", hint: "F5" } ]
    if (!any) return [
      { label: "New folder", icon: "", action: "mkdir", hint: "Ctrl+Shift+N" },
      { label: "New file", icon: "\uf15b", action: "newfile", hint: "Ctrl+Alt+N" },
      { label: "Paste", icon: "", action: "paste", hint: "Ctrl+V", disabled: !clip.paths.length },
      { sep: true },
      { label: "Open terminal here", icon: "", action: "term" },
      { label: Data.isPinned(cwd) ? "Unpin this folder" : "Pin to Home", icon: "", action: "pincwd" },
      { label: "Refresh", icon: "", action: "refresh", hint: "F5" }
    ]
    return [
      { label: "Open", icon: "", action: "open", hint: "Enter" },
      { label: "Preview", icon: "\uf06e", action: "preview", hint: "Space", disabled: !one },
      { label: "Show in folder", icon: "\uf07c", action: "reveal", disabled: !one || !res },
      { label: "Rename", icon: "", action: "rename", hint: "F2", disabled: !one },
      { sep: true },
      { label: "Copy", icon: "", action: "copy", hint: "Ctrl+C" },
      { label: "Cut", icon: "", action: "cut", hint: "Ctrl+X" },
      { label: "Paste", icon: "", action: "paste", hint: "Ctrl+V", disabled: !clip.paths.length },
      { label: "Duplicate", icon: "", action: "dup" },
      { sep: true },
      { label: "Copy path", icon: "", action: "copypath" },
      { label: (one && shown[cur] && shown[cur].isDir && Data.isPinned(shown[cur].path)) ? "Unpin from Home" : "Pin to Home", icon: "", action: "pinsel", disabled: !(one && shown[cur] && shown[cur].isDir) },
      { sep: true },
      { label: "Move to Trash", icon: "", action: "trash", hint: "Del", danger: true }
    ]
  }
  function pinMenu(path, x, y) { ctxTarget = path; ctx.openAt(x + main.x, y + main.y, [
    { label: "Open", icon: "", action: "t_open" },
    { label: path === Fs.home ? "Home is always pinned" : "Unpin", icon: "", action: "t_unpin", disabled: path === Fs.home }
  ]) }
  function recentMenu(e, x, y) { ctxTarget = e; ctx.openAt(x + main.x, y + main.y, [
    { label: "Open", icon: "", action: "r_open" },
    { label: "Show in folder", icon: "", action: "r_reveal" },
    { label: "Copy path", icon: "", action: "r_copy" }
  ]) }
  property var ctxTarget: null
  function menuAction(a) {
    switch (a) {
      case "open": openSelection(); break
      case "rename": renameSel(); break
      case "copy": copySel(false); break
      case "cut": copySel(true); break
      case "paste": paste(); break
      case "dup": duplicate(); break
      case "trash": trashSel(); break
      case "mkdir": newFolder(); break
      case "newfile": newFile(); break
      case "term": termHere(); break
      case "refresh": refresh(); break
      case "copypath": copyPathText(); break
      case "pincwd": Data.togglePin(cwd); break
      case "pinsel": if (cur >= 0) Data.togglePin(shown[cur].path); break
      case "preview": openLightbox(); break
      case "reveal": if (cur >= 0) revealEntry(shown[cur]); break
      case "t_open": go(ctxTarget); break
      case "t_unpin": Data.togglePin(ctxTarget); break
      case "r_open": openEntry(ctxTarget); break
      case "r_reveal": revealEntry(ctxTarget); break
      case "r_copy": if (dry) log("copy-path " + ctxTarget.path); else Quickshell.execDetached(["wl-copy", ctxTarget.path]); break
      case "sort_name": setSort("name"); break
      case "sort_modified": setSort("modified"); break
      case "sort_size": setSort("size"); break
      case "sort_kind": setSort("kind"); break
    }
  }
  function sortMenu(x, y) {
    function it(k, l, ic) { return { label: l, icon: sortKey === k ? (sortAsc ? "" : "") : "", action: "sort_" + k } }
    ctx.openAt(x, y, [it("name", "Name"), it("modified", "Modified"), it("size", "Size"), it("kind", "Kind")])
  }

  // --------------------------------------------------- test / script hook (IPC)
  function act(name, arg) {
    switch (name) {
      case "go": go(arg === "home" ? "" : Fs.norm(Fs.expand(arg))); return "ok"
      case "filter": filter = arg; return "ok"
      case "hidden": showHidden = !showHidden; return String(showHidden)
      case "view": viewMode = arg || (viewMode === "list" ? "grid" : "list"); return viewMode
      case "sort": setSort(arg); return sortKey + (sortAsc ? "+" : "-")
      case "select": { var i = -1; for (var k = 0; k < shown.length; k++) if (shown[k].name === arg) i = k; if (i >= 0) selectOnly(i); return String(i) }
      case "selectall": selectAll(); return String(nsel)
      case "copy": copySel(false); return "ok"
      case "cut": copySel(true); return "ok"
      case "paste": paste(); return "ok"
      case "mkdir": runOp(["mkdir", cwd, arg || "New folder"], function () { refresh() }); return "ok"
      case "newfile": runOp(["newfile", cwd, arg || "Untitled.txt"], function () { refresh() }); return "ok"
      case "rename": { var s = selectedEntries(); if (s.length !== 1) return "need 1"; promptDone("rename", arg, s[0]); return "ok" }
      case "trash": promptDone("trash", "", selectedPaths()); return "ok"
      case "open": openSelection(); return "ok"
      case "back": back(); return "ok"
      case "forward": forward(); return "ok"
      case "up": up(); return "ok"
      case "search": deepSearch(arg); return "ok"
      case "pathedit": pathbar.startEdit(); return "ok"
      case "pathtype": pathbar.startEdit(); return "ok"
      case "menu": ctx.openAt(500, 300, menuFor(0)); return "ok"
      case "prompt": prompt.ask("mkdir", "New folder", "New folder", null, { hint: "in " + Fs.tilde(cwd), ok: "Create" }); return "ok"
      case "kind": { dashboard.kindFilter = arg; return arg }
      case "refresh": refresh(); return "ok"
      case "coll": go("coll:" + arg); return "ok"
      case "zoom": zoom = Math.max(110, Math.min(300, Number(arg))); return String(zoom)
      case "lightbox": if (arg === "off") lbOpen = false; else openLightbox(); return String(lbOpen)
      case "detail": detailOpen = arg ? arg === "on" : !detailOpen; detailOverlayRequested = detailOpen && !detailDocked; return String(detailOpen)
      case "selidx": selectOnly(Number(arg)); area.ensure(Number(arg)); return "ok"
      case "scroll": area.scrollTo(Number(arg)); return "ok"
      case "close": ctx.close(); prompt.close(); return "ok"
      case "accept": if (!prompt.visible) return "no prompt"; prompt.accept(); return "ok"   // = clicking the prompt's OK button
      case "promptinfo": return prompt.visible ? (prompt.mode + " | " + prompt.title) : "none"
    }
    return "unknown"
  }
  function state() {
    return JSON.stringify({ view: view, cwd: cwd, count: shown.length, entries: entries.length, names: shown.slice(0, 40).map(function (e) { return e.name }),
      sel: Object.keys(sel).map(Fs.base), cur: cur, filter: filter, hidden: showHidden, sort: sortKey + (sortAsc ? "+" : "-"), mode: viewMode,
      clip: clip.paths.map(Fs.base), cut: clip.cut, coll: collId, zoom: zoom, cols: area.columns, lb: lbOpen, detail: detailOpen, hist: history, hIdx: hIdx, searchLabel: searchLabel })
  }

  function grab(path) { content.grabToImage(function (r) { r.saveToFile(path); console.log('[files] saved ' + path) }, Qt.size(content.width * 1.6, content.height * 1.6)) }
  function focusMain() { keys.forceActiveFocus() }
  function ensureSidebarItem(item) {
    var y=item.mapToItem(sideBody,0,0).y
    sidebarScroll.contentY=Math.max(0,Math.min(sidebarScroll.contentHeight-sidebarScroll.height,
      y<sidebarScroll.contentY ? y : Math.max(sidebarScroll.contentY,y+item.height-sidebarScroll.height)))
  }
  function toggleSidebar() {
    sidebarRequested=!sidebarRequested
    if(sidebarRequested) Qt.callLater(function(){var first=collRepeater.itemAt(0);if(first) first.forceActiveFocus()})
    else focusMain()
  }

  // ------------------------------------------------------------------ layout
  function containsActionItem(scope,item) { while(item) {if(item===scope)return true;item=item.parent};return false }
  function permitsAction(item) {
    if(!visible || !backingWindowVisible)return false
    if(prompt.visible)return containsActionItem(prompt,item)
    if(ctx.visible)return containsActionItem(ctx,item)
    if(lbOpen)return containsActionItem(lightbox,item)
    return true
  }
  readonly property var focusedItem:contentItem.Window.window ? contentItem.Window.window.activeFocusItem : null
  property string currentFocusIdentity:""
  onFocusedItemChanged: {if(visible && backingWindowVisible){var key=ActionState.focusIdentity(contentItem);if(key)currentFocusIdentity=key}}
  property string pendingFocusIdentity:""
  Connections {target:ActionState;function onFocusRestored(identity,ok) {if(win.pendingFocusIdentity===identity)win.pendingFocusIdentity=""}}
  function initializeUi(snapshot, storedEntries, storedShown) {
    restoringUi = true
    if (snapshot) {
      currentFocusIdentity=snapshot.focusIdentity || ""
      if (snapshot.windowWidth) implicitWidth = snapshot.windowWidth
      if (snapshot.windowHeight) implicitHeight = snapshot.windowHeight
      view = snapshot.view; cwd = snapshot.cwd; history = snapshot.history; hIdx = snapshot.hIdx
      filter = snapshot.filter; searchLabel = snapshot.searchLabel; errorText = snapshot.errorText || ""
      showHidden = snapshot.showHidden; sortKey = snapshot.sortKey; sortAsc = snapshot.sortAsc; viewMode = snapshot.viewMode
      collId = snapshot.collId; zoom = snapshot.zoom; detailOpen = snapshot.detailOpen
      entries = JSON.parse(storedEntries || "[]"); shown = JSON.parse(storedShown || "[]")
      sel = snapshot.sel; nsel = snapshot.nsel; cur = snapshot.cur; anchorIdx = snapshot.anchorIdx; kbd = snapshot.kbd
      clip = snapshot.clip; lbIdx = snapshot.lbIdx; lbOpen = snapshot.lbOpen
      pendingSelect = snapshot.pendingSelect || ""; hiddenCount = snapshot.hiddenCount || 0
      sidebarRequested = !!snapshot.sidebarRequested
      detailOverlayRequested = !!snapshot.detailOverlayRequested
      if (snapshot.prompt) prompt.restoreUi(snapshot.prompt)
      if (snapshot.menu) { ctxTarget = snapshot.ctxTarget; ctx.restoreUi(snapshot.menu) }
      visible = snapshot.visible
      Qt.callLater(function () {
        area.scrollTo(snapshot.fileScroll || 0); dashboard.restoreScroll(snapshot.dashboardScroll || 0)
        sidebarScroll.contentY = snapshot.sidebarScroll || 0; detail.restoreScroll(snapshot.detailScroll || 0)
        dashboard.kindFilter = snapshot.dashboardKind || "all"
        sidebarRequested = !!snapshot.sidebarRequested && !sidebarDocked
        detailOverlayRequested = !!snapshot.detailOverlayRequested && !detailDocked
        if (snapshot.path) pathbar.restoreUi(snapshot.path)
        if (snapshot.focus === "filter") filterInput.forceActiveFocus()
        else if (snapshot.focus === "path" && snapshot.path && snapshot.path.editing) pathbar.restoreFocus()
        else if (!prompt.visible && !ctx.visible && snapshot.visible) focusMain()
        if(snapshot.visible && snapshot.focusIdentity) {pendingFocusIdentity=snapshot.focusIdentity;ActionState.restoreLater(contentItem,pendingFocusIdentity)}
        restoringUi = false
      })
    }
    loading = false
    tree.init(function () { if (win.view === "folder" && !win.collId) tree.reveal(win.cwd) })
    if (!snapshot) restoringUi = false
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
      sidebarScroll: sidebarScroll.contentY, detailScroll: detail.scrollPosition(), dashboardKind: dashboard.kindFilter,
      focusIdentity: currentFocusIdentity,
      focus: filterInput.activeFocus ? "filter" : pathbar.editing ? "path" : "main",
      path: pathbar.exportUi(), prompt: prompt.exportUi(), menu: ctx.exportUi(), ctxTarget: ctxTarget })
  }

  Item {
    id: content
    property var actionOwner:win
    Keys.forwardTo: [keys]
    anchors.fill: parent
    Rectangle { anchors.fill: parent; color: Theme.bg; z: -10 }

    // ---- toolbar
    Item {
      id: toolbar
      z: 20
      width: parent.width; height: win.narrowToolbar ? 128 : (win.compactToolbar ? 92 : 52)
      Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.line }
      Row {
        id: nav
        x: 14; y: 11; spacing: 4
        Btn { visible: !win.sidebarDocked; icon: ""; tip: "Collections and tree (Ctrl+B)"; active: win.sidebarRequested; onClicked: win.toggleSidebar() }
        Btn { accessibleName: "Home"; icon: ""; active: win.view === "home"; onClicked: win.go("") }
        Rectangle { width: 1; height: 18; color: Theme.line; anchors.verticalCenter: parent.verticalCenter }
        Btn { accessibleName: "Back"; icon: ""; enabled2: win.hIdx > 0; onClicked: win.back() }
        Btn { accessibleName: "Forward"; icon: ""; enabled2: win.hIdx < win.history.length - 1; onClicked: win.forward() }
        Btn { accessibleName: "Up"; icon: ""; enabled2: win.view === "folder" && win.cwd !== "/"; onClicked: win.up() }
      }
      Row {
        id: tools
        anchors { right: parent.right; rightMargin: 14 }
        y: 11
        spacing: 4
        Btn { accessibleName: win.viewMode === "list" ? "Show grid" : "Show list"; icon: win.viewMode === "list" ? "" : ""; enabled2: win.view === "folder"; onClicked: win.viewMode = win.viewMode === "list" ? "grid" : "list" }
        Btn { accessibleName: "Sort"; icon: ""; enabled2: win.view === "folder"; onClicked: (m) => win.sortMenu(tools.x + x, toolbar.height) }
        Btn { accessibleName: "Details"; icon: "\uf05a"; enabled2: win.view === "folder"; active: (win.detailDocked ? win.detailOpen : win.detailOverlayRequested) && win.view === "folder"; onClicked: win.toggleDetail() }

      }
      Row {
        id: extraTools
        x: win.narrowToolbar ? toolbar.width - width - 14 : tools.x - width - 4
        y: win.narrowToolbar ? 87 : 11; spacing: 4
        Btn { accessibleName: "Show hidden files"; icon: win.showHidden ? "" : ""; active: win.showHidden; onClicked: win.showHidden = !win.showHidden }
        Btn { accessibleName: win.view === "folder" ? (Data.isPinned(win.cwd) ? "Unpin folder" : "Pin folder") : "Refresh Home"; icon: win.view === "folder" ? (Data.isPinned(win.cwd) ? "" : "") : ""; active: win.view === "folder" && Data.isPinned(win.cwd)
          onClicked: { if (win.view === "folder") Data.togglePin(win.cwd); else Data.refreshAll() } }
      }
      Rectangle {
        id: filterBox
        x: win.narrowToolbar ? 14 : (win.compactToolbar ? toolbar.width - width - 14 : extraTools.x - width - 12)
        y: win.narrowToolbar ? 87 : (win.compactToolbar ? 49 : 10)
        width: win.narrowToolbar ? toolbar.width - extraTools.width - 40 : (win.compactToolbar ? Math.min(250, (toolbar.width - 40) / 2) : (filterInput.activeFocus || win.filter.length ? 250 : 190)); height: 32
        color: filterInput.activeFocus ? Theme.bgDark : "transparent"
        border.width: 1; border.color: filterInput.activeFocus ? Theme.accent : Theme.line
        Behavior on width { NumberAnimation { duration: Theme.dMed; easing.type: Easing.OutCubic } }
        Ico { x: 8; width: 18; height: parent.height; text: ""; size: 12; color: filterInput.activeFocus ? Theme.accent : Theme.fgDim }
        TextInput {
          id: filterInput
          readonly property string actionIdentity:"input:filter"
          Accessible.name: "Filter files"
          Accessible.description: "Control Return searches below this folder"
          anchors { left: parent.left; leftMargin: 30; right: parent.right; rightMargin: 8; verticalCenter: parent.verticalCenter }
          font.family: Theme.font; font.pixelSize: Theme.fsBody; color: Theme.fgBright
          selectionColor: Theme.accent; selectedTextColor: Theme.bg; clip: true
          onTextEdited: win.filter = text
          Keys.onPressed: (e) => {
            if (e.key === Qt.Key_Escape) { win.filter = ""; win.focusMain(); e.accepted = true }
            else if (e.key === Qt.Key_Down) { win.moveCur(win.viewMode === "grid" ? area.columns : 1, false); e.accepted = true }
            else if (e.key === Qt.Key_Up) { win.moveCur(win.viewMode === "grid" ? -area.columns : -1, false); e.accepted = true }
            else if ((e.key === Qt.Key_Return || e.key === Qt.Key_Enter) && (e.modifiers & Qt.ControlModifier)) { win.deepSearch(text); win.focusMain(); e.accepted = true }
            else if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) {
              if (win.view === "home") {
                var t = text.trim()
                if (t.charAt(0) === "/" || t.charAt(0) === "~") win.go(Fs.norm(Fs.expand(t)))
                else if (win.pinList0()) win.go(win.pinList0())
                else if (win.recent0()) win.openEntry(win.recent0())
              } else { if (win.cur < 0 && win.shown.length) win.selectOnly(0); win.openSelection(); win.focusMain() }
              e.accepted = true
            }
          }
        }
        Label { visible: filterInput.text.length === 0; x: 30; width: parent.width - 38; height: parent.height; text: win.view === "home" ? "Search pinned & recent" : "Filter  ·  Ctrl+↵ deep"; color: Theme.fgDim; font.pixelSize: Theme.fsSmall + 1 }
      }
      PathBar {
        id: pathbar
        x: win.compactToolbar ? 14 : nav.x + nav.width + 14
        y: win.compactToolbar ? 49 : 10
        width: win.narrowToolbar ? toolbar.width - 28 : filterBox.x - x - 12
        popupMaxHeight: content.height - (toolbar.y + y + height) - status.height - 8
        path: win.curPath; label: win.collId ? "Collections   ›   " + (win.collInfo ? win.collInfo.name : "") : win.searchLabel
        icon: win.collId && win.collInfo ? win.collInfo.glyph : ""
        onNavigate: (p) => win.go(p)
        onEditDone: win.focusMain()
      }
    }

    // ---- sidebar
    Rectangle {
      id: side
      y: toolbar.height; width: Math.min(244, content.width - 24); height: parent.height - toolbar.height - status.height
      z: win.sidebarDocked ? 0 : 30
      visible: win.sidebarDocked || win.sidebarRequested
      color: Theme.bgDark
      Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: Theme.line }
      Flickable {
        id: sidebarScroll
        anchors.fill: parent; contentWidth: width; contentHeight: sideBody.height
        clip: true; boundsBehavior: Flickable.StopAtBounds
        Item { id: sideBody; width: parent.width; height: Math.max(side.height, treeHead.y + treeHead.height + 126)
      Label { x: 16; y: 14; height: 16; text: "COLLECTIONS"; font.pixelSize: Theme.fsLabel; font.letterSpacing: 1.6; font.bold: true; color: Theme.fgDim }
      Column {
        id: colls
        y: 36; width: parent.width - 1
        Repeater {
          id: collRepeater
          model: Data.collections
          delegate: Item {
            id: cr
            readonly property string actionIdentity:"sidebar-collection:"+modelData.id
            activeFocusOnTab: true
            Accessible.role: Accessible.Button
            Accessible.name: modelData.name
            Accessible.description: "Collection, " + Data.collCount(modelData.id) + " items"
            Accessible.onPressAction: { if(!ActionState.allowed(cr))return;var id=modelData.id; win.go("coll:"+id) }
            Keys.onPressed: (e) => {
              if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space) { if(!e.isAutoRepeat) win.go("coll:"+modelData.id); e.accepted=true }
              else if(e.key===Qt.Key_Up || e.key===Qt.Key_Down) {var i=index+(e.key===Qt.Key_Down ? 1 : -1);if(i>=collRepeater.count)tree.focusRow(0);else{var row=collRepeater.itemAt(Math.max(0,i));if(row)row.forceActiveFocus()};e.accepted=true}
            }
            onActiveFocusChanged: if(activeFocus) win.ensureSidebarItem(cr)
            Rectangle { anchors.fill:parent; color:"transparent"; border.width:cr.activeFocus ? 2 : 0; border.color:Theme.accent; z:2 }
            required property var modelData
            readonly property bool on: win.collId === modelData.id
            readonly property color kc: Theme.byKey(modelData.color)
            width: colls.width; height: 28
            Rectangle { anchors.fill: parent; color: cr.on ? Theme.selection : (cma.containsMouse ? Theme.hover : "transparent") }
            Rectangle { visible: cr.on; width: 2; height: parent.height; color: cr.kc }
            Ico { x: 14; width: 20; height: parent.height; text: cr.modelData.glyph; size: 12; color: cr.kc }
            Label { x: 42; width: parent.width - 42 - 50; height: parent.height; text: cr.modelData.name; color: cr.on ? Theme.fgBright : Theme.fg; font.bold: cr.on }
            Label { anchors.right: parent.right; anchors.rightMargin: 12; height: parent.height; text: Data.collCount(cr.modelData.id)
              font.pixelSize: Theme.fsSmall; color: cr.on ? cr.kc : Theme.fgDim }
            MouseArea { id: cma; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: win.go("coll:" + cr.modelData.id) }
          }
        }
      }
      Item {
        id: treeHead
        y: colls.y + colls.height + 8; width: parent.width - 1; height: 26
        Rectangle { width: parent.width; height: 1; color: Theme.line }
        Label { x: 16; y: 10; height: 16; text: "TREE"; font.pixelSize: Theme.fsLabel; font.letterSpacing: 1.6; font.bold: true; color: Theme.fgDim }
      }
      Tree {
        onFocusRequested:(item)=>win.ensureSidebarItem(item)
        id: tree
        anchors { top: treeHead.bottom; left: parent.left; right: parent.right; rightMargin: 1; bottom: parent.bottom; bottomMargin: 6 }
        onNavigate: (p) => win.go(p)
      }
        }
      }
      ScrollBar_ { view: sidebarScroll; visible: sidebarScroll.contentHeight > sidebarScroll.height }
    }

    Rectangle {
      x: 0; y: toolbar.height; width: content.width; height: side.height; z: 25
      visible: !win.sidebarDocked && win.sidebarRequested
      color: Theme.alpha(Theme.bgDarker, 0.55)
      MouseArea { anchors.fill: parent; onClicked: win.sidebarRequested = false }
    }

    // ---- main area
    Item {
      id: main
      x: win.sidebarDocked ? side.width : 0; y: toolbar.height; width: parent.width - x; height: side.height
      clip: true
      Dashboard { id: dashboard; anchors.fill: parent; ex: win; visible: win.view === "home"; opacity: visible ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: Theme.dMed } } }
      FileArea {
        id: area
        ex: win
        anchors { left: parent.left; top: parent.top; bottom: parent.bottom }
        width: main.width - (win.detailDocked && win.view === "folder" ? detail.width * detail.prog : 0)
        visible: win.view === "folder"
        opacity: win.loading && win.entries.length === 0 ? 0.4 : 1
        Behavior on opacity { NumberAnimation { duration: Theme.dFast } }
        onContextRequested: (x, y, i) => ctx.openAt(x + main.x, y + main.y, win.menuFor(i))
      }
      Rectangle {
        anchors.fill: parent; z: 1
        visible: !win.detailDocked && detail.visible
        color: Theme.alpha(Theme.bgDarker, 0.55)
        MouseArea { anchors.fill: parent; onClicked: win.detailOverlayRequested = false }
      }
      Detail {
        id: detail; z: 2
        ex: win
        width: Math.min(300, main.width - 20); height: parent.height
        x: main.width - width * prog
        property real prog: (win.detailOpen && (win.detailDocked || win.detailOverlayRequested) && win.nsel > 0 && win.view === "folder") ? 1 : 0
        Behavior on prog { NumberAnimation { duration: Theme.dMed; easing.type: Easing.OutCubic } }
        visible: prog > 0
      }
    }

    // ---- status line
    Rectangle {
      id: status
      y: parent.height - height; width: parent.width; height: 26; color: Theme.bgDark
      Rectangle { width: parent.width; height: 1; color: Theme.line }
      Row {
        id: statusLeft; x: 14; width: status.width - statusExtra.width - 42; height: parent.height; spacing: 14
        Label { width: Math.max(100, statusLeft.width - (filterStatus.visible ? filterStatus.width + 14 : 0) - (clipboardStatus.visible ? clipboardStatus.width + 14 : 0)); height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.fg
          text: {
            if (win.view === "home") return Data.pins.length + " pinned  ·  " + Data.recents.length + " recent files"
            var nd = 0, nf = 0, bytes = 0
            for (var i = 0; i < win.shown.length; i++) { if (win.shown[i].isDir) nd++; else { nf++; bytes += win.shown[i].size } }
            if (win.nsel > 0) {
              var sb = 0, s = win.selectedEntries()
              for (var k = 0; k < s.length; k++) if (!s[k].isDir) sb += s[k].size
              return win.nsel + " selected" + (sb ? "  ·  " + Fs.size(sb) : "")
            }
            return win.shown.length + " items  ·  " + nd + " folders, " + nf + " files" + (nf ? "  ·  " + Fs.size(bytes) : "")
          } }
        Label { id: filterStatus; width: Math.min(160, implicitWidth); visible: status.width >= 1100 && win.filter.length > 0 && win.view === "folder"; height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.accent; text: "filter: " + win.filter }
        Label { id: clipboardStatus; width: Math.min(150, implicitWidth); visible: status.width >= 1000 && win.clip.paths.length > 0; height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.yellow
          text: (win.clip.cut ? " " : " ") + win.clip.paths.length + " on clipboard" }
      }
      Row {
        id: statusExtra
        anchors.right: parent.right; anchors.rightMargin: 14; height: parent.height; spacing: 14
        Label { visible: status.width >= 900 && win.view === "folder" && win.hiddenCount > 0; height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim
          text: win.showHidden ? win.hiddenCount + " hidden shown" : win.hiddenCount + " hidden" }
        Label { visible: status.width >= 700 && win.view === "folder"; height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim
          text: "sort " + win.sortKey + (win.sortAsc ? " ↑" : " ↓") }
        Label { visible: status.width >= 600; height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim
          text: Fs.size(Math.max(0, Data.diskSize - Data.diskUsed)) + " free" }
      }
    }

    // ---- toast
    Rectangle {
      id: toastBox
      anchors { horizontalCenter: parent.horizontalCenter; bottom: status.top; bottomMargin: 14 }
      width: Math.min(parent.width - 24, toastText.implicitWidth + 32); height: 34; opacity: 0
      color: Theme.bg; border.color: Theme.accent; border.width: 1; z: 150
      Behavior on opacity { NumberAnimation { duration: Theme.dMed } }
      Label { id: toastText; anchors.centerIn: parent; width: Math.min(implicitWidth, parent.width - 32); color: Theme.fgBright }
      Timer { id: toastTimer; interval: 2400; onTriggered: toastBox.opacity = 0 }
    }

    Lightbox { id: lightbox; ex: win; visible: win.lbOpen }
    ContextMenu { id: ctx; onChosen: (a) => { win.menuAction(a); win.focusMain() } onVisibleChanged: if (!visible) win.focusMain() }
    Prompt { id: prompt; onAccepted: (m, t, p) => win.promptDone(m, t, p); onVisibleChanged: if (!visible) win.focusMain() }
  }

  function pinList0() { return dashboard.pinList.length ? dashboard.pinList[0] : "" }
  function recent0() { return dashboard.recentList.length ? dashboard.recentList[0] : null }

  // ---------------------------------------------------------------- keyboard
  Item {
    id: keys
    readonly property string actionIdentity:"main"
    Accessible.ignored: true
    anchors.fill: parent
    focus: true
    Keys.onPressed: (e) => {
      if(prompt.visible || ctx.visible) {e.accepted=true;return}
      var ctrl = e.modifiers & Qt.ControlModifier, shift = e.modifiers & Qt.ShiftModifier, alt = e.modifiers & Qt.AltModifier
      var grid = win.viewMode === "grid"
      if (win.lbOpen) {
        if (e.key === Qt.Key_Escape || e.key === Qt.Key_Space) win.lbOpen = false
        else if (e.key === Qt.Key_Left || e.key === Qt.Key_Up) win.lbMove(-1)
        else if (e.key === Qt.Key_Right || e.key === Qt.Key_Down) win.lbMove(1)
        else if (e.key === Qt.Key_Home) win.lbMove(-1e6)
        else if (e.key === Qt.Key_End) win.lbMove(1e6)
        else if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) { win.openEntry(win.shown[win.lbIdx]); if (win.shown[win.lbIdx].isDir) win.lbOpen = false }
        e.accepted = true; return
      }
      if(e.key===Qt.Key_Menu || (shift && e.key===Qt.Key_F10)) {
        if(win.view==="folder") {if(win.cur>=0) win.rightClick(win.cur);ctx.openAt(14,toolbar.height+78,win.menuFor(win.cur))}
        e.accepted=true;return
      }
      if (e.key === Qt.Key_Space && !ctrl && win.view === "folder") { win.openLightbox(); e.accepted = true; return }
      if (e.key === Qt.Key_B && ctrl) { if (!win.sidebarDocked) win.toggleSidebar(); e.accepted = true; return }
      if (e.key === Qt.Key_I && ctrl) { win.toggleDetail(); e.accepted = true; return }
      if ((e.key === Qt.Key_Plus || e.key === Qt.Key_Equal) && ctrl) { win.zoom = Math.min(300, win.zoom + 20); e.accepted = true; return }
      if (e.key === Qt.Key_Minus && ctrl) { win.zoom = Math.max(110, win.zoom - 20); e.accepted = true; return }
      if (ctrl && e.key === Qt.Key_L || (e.key === Qt.Key_Slash && !ctrl && win.view === "folder" && false)) { pathbar.startEdit(); e.accepted = true; return }
      if (ctrl && e.key === Qt.Key_F) { filterInput.forceActiveFocus(); filterInput.selectAll(); e.accepted = true; return }
      if (ctrl && e.key === Qt.Key_H) { win.showHidden = !win.showHidden; e.accepted = true; return }
      if (alt && e.key === Qt.Key_Left) { win.back(); e.accepted = true; return }
      if (alt && e.key === Qt.Key_Right) { win.forward(); e.accepted = true; return }
      if (alt && e.key === Qt.Key_Up) { win.up(); e.accepted = true; return }
      if (alt && e.key === Qt.Key_Home) { win.go(""); e.accepted = true; return }
      if (e.key === Qt.Key_F5) { win.refresh(); Data.refreshAll(); e.accepted = true; return }
      if (e.key === Qt.Key_Escape) {
        if (win.sidebarRequested) { win.sidebarRequested = false; win.focusMain() }
        else if (win.detailOverlayRequested) { win.detailOverlayRequested = false; win.focusMain() }
        else if (win.filter.length) win.filter = ""
        else if (win.nsel) win.clearSel()
        else if (win.searchLabel) win.go(win.cwd)
        e.accepted = true; return
      }
      if (win.view === "folder") {
        if (ctrl && e.key === Qt.Key_A) { win.selectAll(); e.accepted = true; return }
        if (ctrl && e.key === Qt.Key_C) { win.copySel(false); e.accepted = true; return }
        if (ctrl && e.key === Qt.Key_X) { win.copySel(true); e.accepted = true; return }
        if (ctrl && e.key === Qt.Key_V) { win.paste(); e.accepted = true; return }
        if (ctrl && e.key === Qt.Key_D) { win.duplicate(); e.accepted = true; return }
        if (ctrl && (e.modifiers & Qt.AltModifier) && e.key === Qt.Key_N) { win.newFile(); e.accepted = true; return }
        if (ctrl && shift && e.key === Qt.Key_N) { win.newFolder(); e.accepted = true; return }
        if (e.key === Qt.Key_F2) { win.renameSel(); e.accepted = true; return }
        if (e.key === Qt.Key_Delete) { win.trashSel(); e.accepted = true; return }
        if (e.key === Qt.Key_Down) { win.moveCur(grid ? area.columns : 1, shift); e.accepted = true; return }
        if (e.key === Qt.Key_Up) { win.moveCur(grid ? -area.columns : -1, shift); e.accepted = true; return }
        if (e.key === Qt.Key_Right) { if (grid) win.moveCur(1, shift); else if (win.cur >= 0 && win.shown[win.cur].isDir) win.openEntry(win.shown[win.cur]); e.accepted = true; return }
        if (e.key === Qt.Key_Left) { if (grid) win.moveCur(-1, shift); else win.up(); e.accepted = true; return }
        if (e.key === Qt.Key_Home) { win.moveCur(-1e6, shift); e.accepted = true; return }
        if (e.key === Qt.Key_End) { win.moveCur(1e6, shift); e.accepted = true; return }
        if (e.key === Qt.Key_PageDown) { win.moveCur(12, shift); e.accepted = true; return }
        if (e.key === Qt.Key_PageUp) { win.moveCur(-12, shift); e.accepted = true; return }
        if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) { win.openSelection(); e.accepted = true; return }
        if (e.key === Qt.Key_Backspace) { if (win.filter.length) win.filter = win.filter.slice(0, -1); else win.up(); e.accepted = true; return }
      }
      // type-to-filter
      if (!ctrl && !alt && e.text.length === 1 && e.text >= " " && e.key !== Qt.Key_Delete) {
        filterInput.forceActiveFocus()
        win.filter = win.filter + e.text
        filterInput.cursorPosition = filterInput.text.length
        e.accepted = true
      }
    }
  }
}

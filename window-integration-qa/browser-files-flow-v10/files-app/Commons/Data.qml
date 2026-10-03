pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

// Shared data for the widget and the Home dashboard: pinned folders (persisted),
// recent files, home-directory usage tree (du, async, cached) and disk stats.
QtObject {
  id: root
  readonly property string home: Fs.home
  readonly property string stateDir: (Quickshell.env("FILES_STATE") || (Quickshell.env("XDG_STATE_HOME") || (home + "/.local/state")) + "/omarchy-files")
  readonly property string stateFile: stateDir + "/dashboard.json"

  property var pins: []
  property var recents: []
  property var usage: []        // [{name,path,size,children:[{name,path,size}]}]
  property real usageTotal: 0
  property real diskSize: 0
  property real diskUsed: 0
  property bool usageLoading: false
  property bool pinsLoaded: false

  function defaultPins() {
    var names = ["Documents", "Downloads", "Pictures", "Videos", "Music", "Projects", "src", "Work"]
    var out = [home]
    for (var i = 0; i < names.length; i++) out.push(home + "/" + names[i])
    return out
  }

  function isPinned(p) { return pins.indexOf(p) >= 0 }
  function togglePin(p) {
    var a = pins.slice(), i = a.indexOf(p)
    if (i >= 0) a.splice(i, 1); else a.push(p)
    pins = a; save()
  }
  function save() {
    _saver.command = ["bash", "-c", "mkdir -p \"$1\" && printf '%s' \"$3\" > \"$2\"", "_", stateDir, stateFile, JSON.stringify({ pins: pins })]
    _saver.running = true
  }
  property Process _saver: Process {}

  property FileView _state: FileView {
    path: root.stateFile
    printErrors: false
    onLoaded: {
      try {
        var o = JSON.parse(text())
        // drop pins that no longer exist lazily; keep as-is
        root.pins = o.pins || root.defaultPins()
      } catch (e) { root.pins = root.defaultPins() }
      root.pinsLoaded = true
    }
    onLoadFailed: { root.pins = root.defaultPins(); root.pinsLoaded = true }
  }
  property FileView _duCache: FileView {
    path: root.stateDir + "/du.json"
    printErrors: false
    onLoaded: {
      try { var o = JSON.parse(text()); if (!root.usage.length) { root.usage = o.usage; root.usageTotal = o.total } } catch (e) {}
    }
  }

  function refreshRecents() {
    Fs.run(["bash", Fs.script("recent.sh"), "80"], function (txt) {
      var out = [], lines = txt.split("\n")
      for (var i = 0; i < lines.length; i++) {
        var f = lines[i].split("\t"); if (f.length < 3) continue
        var path = home + f[2].slice(1)
        var name = Fs.base(path), dot = name.lastIndexOf(".")
        out.push({ name: name, path: path, isDir: false, size: Number(f[1]), mtime: Number(f[0]),
                   ext: dot > 0 ? name.slice(dot + 1).toLowerCase() : "", hidden: false })
      }
      root.recents = out
    })
  }

  function refreshUsage() {
    usageLoading = true
    Fs.run(["bash", Fs.script("du.sh"), home], function (txt) {
      var lines = txt.split("\n"), top = {}, total = 0
      for (var i = 0; i < lines.length; i++) {
        var t = lines[i].indexOf("\t"); if (t < 0) continue
        var size = Number(lines[i].slice(0, t)), p = lines[i].slice(t + 1)
        if (p === root.home) { total = size; continue }
        var rel = p.slice(root.home.length + 1), parts = rel.split("/")
        if (parts.length === 1) {
          top[parts[0]] = top[parts[0]] || { name: parts[0], path: p, size: 0, children: [] }
          top[parts[0]].size = size
        } else {
          top[parts[0]] = top[parts[0]] || { name: parts[0], path: root.home + "/" + parts[0], size: 0, children: [] }
          top[parts[0]].children.push({ name: parts[1], path: p, size: size })
        }
      }
      var arr = [], sum = 0
      for (var k in top) { arr.push(top[k]); sum += top[k].size }
      for (var j = 0; j < arr.length; j++) {
        var cs = 0, ch = arr[j].children
        for (var m = 0; m < ch.length; m++) cs += ch[m].size
        if (arr[j].size - cs > arr[j].size * 0.02 && ch.length) ch.push({ name: "(files)", path: arr[j].path, size: arr[j].size - cs })
        ch.sort(function (a, b) { return b.size - a.size })
      }
      if (total - sum > 0) arr.push({ name: "(files)", path: root.home, size: total - sum, children: [] })
      arr.sort(function (a, b) { return b.size - a.size })
      root.usage = arr; root.usageTotal = total; root.usageLoading = false
      Fs.run(["bash", "-c", "mkdir -p \"$1\" && printf '%s' \"$2\" > \"$1/du.json\"", "_", root.stateDir, JSON.stringify({ usage: arr, total: total })], null)
    })
    Fs.run(["bash", "-c", "df -B1 --output=size,used \"$HOME\" | tail -1"], function (txt) {
      var f = txt.trim().split(/\s+/); root.diskSize = Number(f[0]); root.diskUsed = Number(f[1])
    })
  }

  // ---- smart collections (live `find`, computed async one after another)
  readonly property var collections: [
    { id: "recent",      name: "Recent activity", glyph: "\uf017", color: "accent",  timeline: true },
    { id: "images",      name: "Images",          glyph: "\uf03e", color: "green" },
    { id: "videos",      name: "Videos",          glyph: "\uf03d", color: "magenta" },
    { id: "documents",   name: "Documents",       glyph: "\uf15c", color: "orange" },
    { id: "downloads",   name: "Downloads",       glyph: "\uf019", color: "cyan" },
    { id: "large",       name: "Large files",     glyph: "\uf1c0", color: "yellow", bySize: true },
    { id: "screenshots", name: "Screenshots",     glyph: "\uf030", color: "red" }
  ]
  property var collData: ({})
  property var collCounts: ({})
  property int collRev: 0
  property var _collQueue: []
  property bool _collBusy: false
  function collInfo(id) { for (var i = 0; i < collections.length; i++) if (collections[i].id === id) return collections[i]; return null }
  function collEntries(id) { collRev; return collData[id] || [] }
  function collCount(id) { collRev; var n = collCounts[id]; return n === undefined ? "\u2013" : (n >= 800 ? "800+" : String(n)) }
  function refreshCollections() {
    if (_collBusy) return
    _collBusy = true
    _collQueue = collections.map(function (c) { return c.id })
    _collNext()
  }
  function _collNext() {
    if (!_collQueue.length) { _collBusy = false; return }
    var id = _collQueue.shift()
    Fs.run(["bash", Fs.script("collect.sh"), id], function (txt) {
      var out = [], lines = txt.split("\n")
      for (var i = 0; i < lines.length; i++) {
        var f = lines[i].split("\t"); if (f.length < 4) continue
        var path = f.slice(3).join("\t"), name = Fs.base(path), dot = name.lastIndexOf(".")
        out.push({ name: name, path: path, isDir: false, isLink: false, size: Number(f[1]), mtime: Math.floor(Number(f[2])),
                   ext: dot > 0 ? name.slice(dot + 1).toLowerCase() : "", hidden: false })
      }
      var d = collData, c = collCounts
      d[id] = out; c[id] = out.length
      collData = d; collCounts = c; collRev++
      root._collNext()
    })
  }
  // newest thumbnailable items for the Home/widget mosaics
  readonly property var recentMedia: {
    collRev
    var out = [], seen = {}
    var srcs = ["recent", "images", "videos"]
    for (var pass = 0; pass < 2; pass++)
      for (var s = 0; s < srcs.length; s++) {
        var l = collData[srcs[s]] || []
        for (var i = 0; i < l.length && out.length < 8; i++) {
          var ok = pass === 0 ? Fs.isThumbImage(l[i]) : Fs.isMedia(l[i])
          if (!seen[l[i].path] && ok) { seen[l[i].path] = 1; out.push(l[i]) }
        }
      }
    return out
  }

  function refreshAll() { refreshRecents(); refreshUsage(); refreshCollections() }
  Component.onCompleted: refreshAll()
}

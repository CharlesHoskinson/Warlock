pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

QtObject {
  id: root; objectName:"Fs.root"
  readonly property string home: Quickshell.env("HOME")
  function script(n) { return Quickshell.shellPath("scripts/" + n) }
  property Component _lister: Lister {}

  // Run a command; cb(stdoutText, exitCode).
  function run(cmd, cb) {
    var p = _lister.createObject(root, { command: cmd, callback: cb })
    p.running = true
    return p
  }

  function parseRecords(txt, dir, full) {
    var out = [], recs = txt.split("\x1e")
    for (var i = 0; i < recs.length; i++) {
      var r = recs[i]; if (!r.length) continue
      var f = r.split("\t"); if (f.length < 5) continue
      var name = f.slice(4).join("\t")
      var path = full ? norm(dir + "/" + name) : (dir === "/" ? "" : dir) + "/" + name
      if (full) name = base(path)
      var isDir = f[0] === "d"
      var dot = name.lastIndexOf(".")
      out.push({
        name: name, path: path,
        isDir: isDir, isLink: f[1] === "l", size: Number(f[2]), mtime: Number(f[3]),
        ext: (!isDir && dot > 0) ? name.slice(dot + 1).toLowerCase() : "",
        hidden: name.charAt(0) === "."
      })
    }
    return out
  }
  function list(path, cb) {
    run(["bash", script("list.sh"), path], function (txt, code) {
      cb(code !== 0 ? null : parseRecords(txt, path, false))
    })
  }
  function search(dir, q, cb) {
    run(["bash", script("search.sh"), dir, q], function (txt, code) { cb(parseRecords(txt, dir, true)) })
  }

  function sortEntries(arr, key, asc) {
    var dir = asc ? 1 : -1
    var coll = Qt.locale()
    arr.sort(function (a, b) {
      if (a.isDir !== b.isDir) return a.isDir ? -1 : 1
      var r = 0
      if (key === "modified") r = a.mtime - b.mtime
      else if (key === "size") r = a.size - b.size
      else if (key === "kind") r = a.ext < b.ext ? -1 : (a.ext > b.ext ? 1 : 0)
      if (r === 0) r = a.name.toLowerCase().localeCompare(b.name.toLowerCase(), undefined, { numeric: true })
      else return r * dir
      return r * (key === "name" ? dir : 1)
    })
    return arr
  }

  function entryOf(path) {
    var name = base(path), dot = name.lastIndexOf(".")
    return { name: name, path: path, isDir: false, isLink: false, size: 0, mtime: 0, ext: dot > 0 ? name.slice(dot + 1).toLowerCase() : "", hidden: false }
  }
  function isMedia(e) { return !e.isDir && (isThumbImage(e) || isThumbGen(e)) }
  function longDate(ts) { return Qt.formatDateTime(new Date(ts * 1000), "ddd, MMM d, yyyy  HH:mm") }
  function dayBucket(ts) {
    var now = new Date(), d = new Date(ts * 1000)
    var t0 = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime() / 1000
    if (ts >= t0) return "Today"
    if (ts >= t0 - 86400) return "Yesterday"
    if (ts >= t0 - 86400 * 6) return "This week"
    if (ts >= t0 - 86400 * 30) return "Earlier this month"
    return "Older"
  }

  // ---- path helpers
  function base(p) { if (p === "/") return "/"; var i = p.lastIndexOf("/"); return p.slice(i + 1) }
  function parent(p) { if (p === "/" || p === "") return "/"; var i = p.lastIndexOf("/"); return i <= 0 ? "/" : p.slice(0, i) }
  function tilde(p) { return p === home ? "~" : (p.indexOf(home + "/") === 0 ? "~" + p.slice(home.length) : p) }
  function expand(p) {
    p = String(p).trim()
    if (p === "~") return home
    if (p.indexOf("~/") === 0) return home + p.slice(1)
    return p
  }
  function norm(p) {
    var parts = p.split("/"), out = []
    for (var i = 0; i < parts.length; i++) {
      if (parts[i] === "" || parts[i] === ".") continue
      if (parts[i] === "..") out.pop(); else out.push(parts[i])
    }
    return "/" + out.join("/")
  }
  function url(p) { return "file://" + p.split("/").map(encodeURIComponent).join("/") }

  // ---- formatting
  function size(b) {
    if (b < 1024) return b + " B"
    var u = ["KB", "MB", "GB", "TB"], i = -1
    do { b /= 1024; i++ } while (b >= 1024 && i < 3)
    return (b >= 100 ? b.toFixed(0) : b.toFixed(1)) + " " + u[i]
  }
  function ago(ts) {
    var s = Date.now() / 1000 - ts
    if (s < 60) return "now"
    if (s < 3600) return Math.floor(s / 60) + "m ago"
    if (s < 86400) return Math.floor(s / 3600) + "h ago"
    if (s < 86400 * 14) return Math.floor(s / 86400) + "d ago"
    return Qt.formatDate(new Date(ts * 1000), "d MMM yyyy")
  }
  function date(ts) {
    var d = new Date(ts * 1000), n = new Date()
    if (d.getFullYear() === n.getFullYear()) return Qt.formatDateTime(d, "d MMM  HH:mm")
    return Qt.formatDate(d, "d MMM yyyy")
  }

  // ---- kinds & icons (Nerd Font, Font Awesome range)
  readonly property var kinds: ({
    image: ["png","jpg","jpeg","gif","webp","bmp","svg","avif","tiff","ico","heic"],
    video: ["mp4","mkv","webm","mov","avi","m4v","flv"],
    audio: ["mp3","flac","ogg","wav","m4a","opus","aac"],
    archive: ["zip","tar","gz","xz","zst","bz2","7z","rar","tgz","iso"],
    document: ["pdf","doc","docx","odt","txt","md","rtf","epub","xls","xlsx","ods","ppt","pptx","csv"],
    code: ["js","ts","py","rs","go","c","h","cpp","qml","sh","json","toml","yaml","yml","html","css","lua","java","nix","conf","ini","xml","sql"]
  })
  function kindOf(e) {
    if (e.isDir) return "folder"
    for (var k in kinds) if (kinds[k].indexOf(e.ext) >= 0) return k
    return "file"
  }
  function kindLabel(e) {
    var k = kindOf(e)
    if (k === "folder") return "Folder"
    return e.ext ? e.ext.toUpperCase() : (k === "file" ? "File" : k)
  }
  function iconFor(e) {
    if (e.isDir) return ""
    if (e.ext === "pdf") return ""
    switch (kindOf(e)) {
      case "image": return ""
      case "video": return ""
      case "audio": return ""
      case "archive": return ""
      case "code": return ""
      case "document": return ""
    }
    return ""
  }
  function colorFor(e) {
    if (e.isDir) return Theme.accent
    switch (kindOf(e)) {
      case "image": return Theme.magenta
      case "video": return Theme.red
      case "audio": return Theme.yellow
      case "archive": return Theme.orange
      case "code": return Theme.green
      case "document": return Theme.cyan
    }
    return Theme.fgDim
  }
  function isThumbImage(e) { return ["png","jpg","jpeg","gif","webp","bmp","svg","avif"].indexOf(e.ext) >= 0 }
  function isThumbGen(e) { return e.ext === "pdf" || kinds.video.indexOf(e.ext) >= 0 }
  function folderIcon(name) {
    switch (name) {
      case "Documents": return ""
      case "Downloads": return ""
      case "Pictures": return ""
      case "Videos": return ""
      case "Music": return ""
      case "Desktop": return ""
      case "Projects": case "src": return ""
      case "Work": return ""
    }
    return ""
  }
}

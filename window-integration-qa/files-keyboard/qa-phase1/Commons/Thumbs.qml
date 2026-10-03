pragma Singleton
import QtQuick

// Serial-ish queue (2 workers) for generated thumbnails (pdf/video).
QtObject {
  id: root; objectName:"Thumbs.root"
  property var queue: []
  property var done: ({})
  property int active: 0

  function request(path, cb) {
    if (done[path] !== undefined) { if (done[path]) cb(done[path]); return }
    queue.push({ path: path, cb: cb }); pump()
  }
  function pump() {
    while (active < 2 && queue.length) {
      var job = queue.shift()
      if (done[job.path] !== undefined) { if (done[job.path]) job.cb(done[job.path]); continue }
      active++
      Fs.run(["bash", Fs.script("thumb.sh"), job.path], (function (j) { return function (txt) {
        var p = txt.trim()
        done[j.path] = p
        if (p) j.cb(p)
        root.active--; root.pump()
      } })(job))
    }
  }

  // ---- folder mosaics: cheap top-level scan for up to 4 media files (3 workers)
  property var pvDone: ({})
  property var pvQueue: []
  property int pvActive: 0
  function preview(dir, cb) {
    if (pvDone[dir]) { cb(pvDone[dir]); return }
    pvQueue.push({ dir: dir, cb: cb }); pvPump()
  }
  function pvPump() {
    while (pvActive < 3 && pvQueue.length) {
      var job = pvQueue.shift()
      if (pvDone[job.dir]) { job.cb(pvDone[job.dir]); continue }
      pvActive++
      Fs.run(["bash", Fs.script("preview.sh"), job.dir], (function (j) { return function (txt) {
        var f = txt.trim().split("\t")
        var r = { count: Number(f[0]) || 0, paths: f.slice(1).filter(function (x) { return x.length }) }
        pvDone[j.dir] = r
        try { j.cb(r) } catch (e) {}
        root.pvActive--; root.pvPump()
      } })(job))
    }
  }
}

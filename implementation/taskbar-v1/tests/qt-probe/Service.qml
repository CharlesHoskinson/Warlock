import QtQuick
import Quickshell
import Quickshell.Io
import "SnapshotStream.js" as Stream

// One observation process for all taskbar outputs. Window actions retain their
// existing owning-window authority; this service supplies presentation data.
Item {
  id: root
  property var shell: null
  property var manifest: null
  property string helper: Quickshell.env("HOME") + "/.local/share/hypr-taskbar-v1/hypr-taskbar"
  property string snapshotText: JSON.stringify(Stream.empty())
  property var streamState: Stream.initial()
  property bool online: false
  property string lastError: ""
  property bool wanted: true
  property bool closing: false
  property int restartDelay: 1000
  property int acceptedSnapshots: 0
  property int rejectedSnapshots: 0

  function refresh() {
    if (backend.running) {
      backend.write("refresh\n")
      return true
    }
    return false
  }
  function receive(line) {
    if (!backend.running) return
    var result = Stream.decode(line, streamState)
    if (!result) {
      rejectedSnapshots++
      lastError = "Invalid or stale taskbar snapshot"
      return
    }
    streamState = result.state
    snapshotText = JSON.stringify(result.snapshot)
    online = true
    lastError = ""
    restartDelay = 1000
    acceptedSnapshots++
  }
  function invalidate() {
    online = false
    streamState = Stream.initial()
    snapshotText = JSON.stringify(Stream.empty())
  }
  function stopped(message) {
    wanted = false
    invalidate()
    lastError = message
    if (closing) return
    retry.interval = restartDelay
    restartDelay = Math.min(30000, restartDelay * 2)
    retry.restart()
  }
  function stop() { closing = true; wanted = false; retry.stop() }
  Component.onDestruction: root.stop()

  Process {
    id: backend
    command: [root.helper, "observe"]
    running: root.wanted
    stdinEnabled: true
    stdout: SplitParser { onRead: data => root.receive(data) }
    stderr: SplitParser { onRead: data => { root.lastError = data.slice(0, 1024); console.warn("Taskbar observer: " + root.lastError) } }
    onStarted: root.invalidate()
    onRunningChanged: if (!running && root.wanted) root.stopped("Taskbar observer failed to start")
    onExited: function(code) {
      root.stopped("Taskbar observer exited: " + code)
    }
  }
  Timer { id: retry; onTriggered: root.wanted = true }
}

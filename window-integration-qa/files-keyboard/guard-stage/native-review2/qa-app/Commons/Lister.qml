import QtQuick
import Quickshell.Io

// One-shot async process runner. Create via Fs.run(); calls back once both
// stdout and the exit status are known, then self-destroys.
Process {
  id: p; objectName: "Lister.p"
  property var callback: null
  property string _out: ""
  property int _code: -1
  property bool _gotOut: false
  property bool _gotExit: false
  function _maybe() {
    if (!_gotOut || !_gotExit) return
    if (callback) callback(_out, _code)
    callback = null
    p.destroy(200)
  }
  stdout: StdioCollector {
    onStreamFinished: { p._out = text; p._gotOut = true; p._maybe() }
  }
  onExited: (code, st) => { p._code = code; p._gotExit = true; p._maybe() }
}

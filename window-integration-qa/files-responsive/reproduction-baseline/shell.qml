import QtQuick
import Quickshell
import Quickshell.Io
import "explorer"
import "widget"
import qs.Commons

// Thin host: the desktop widget (panel plugin) + the explorer (window plugin).
// Run:  qs -p <this dir>      Drive:  qs -p <dir> ipc call files open ~/Documents
ShellRoot {
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
  }

  Component.onCompleted: {
    var o = Quickshell.env("FILES_OPEN")
    if (o) explorer.openAt(o === "home" ? "" : (o.indexOf("coll:") === 0 ? o : o), "")
  }
}

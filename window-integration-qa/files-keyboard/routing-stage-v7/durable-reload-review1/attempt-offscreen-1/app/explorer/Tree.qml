import QtQuick
import qs.Commons
import qs.Ui

// Collapsible directory tree with lazy (async) expansion.
Item {
  id: root
  property bool showHidden: false
  property string current: ""
  signal navigate(string path)

  ListModel { id: tm }
  property alias model: tm

  function indexOfPath(p) { for (var i = 0; i < tm.count; i++) if (tm.get(i).path === p) return i; return -1 }

  function init(then) {
    tm.clear()
    tm.append({ path: Fs.home, name: "Home", depth: 0, expanded: false, loading: false, leaf: false, isRoot: true, glyph: "" })
    tm.append({ path: "/", name: "Filesystem", depth: 0, expanded: false, loading: false, leaf: false, isRoot: true, glyph: "" })
    expand(0, then)
  }
  function expand(i, cb) {
    var row = tm.get(i)
    if (!row || row.expanded) { if (cb) cb(); return }
    var p = row.path, d = row.depth
    tm.setProperty(i, "loading", true)
    Fs.list(p, function (es) {
      var idx = root.indexOfPath(p)
      if (idx < 0) return
      var dirs = (es || []).filter(function (e) { return e.isDir && (root.showHidden || !e.hidden) })
      dirs.sort(function (a, b) { return a.name.toLowerCase().localeCompare(b.name.toLowerCase(), undefined, { numeric: true }) })
      for (var k = 0; k < dirs.length; k++)
        tm.insert(idx + 1 + k, { path: dirs[k].path, name: dirs[k].name, depth: d + 1, expanded: false, loading: false, leaf: false, isRoot: false, glyph: "" })
      tm.setProperty(idx, "expanded", true)
      tm.setProperty(idx, "loading", false)
      tm.setProperty(idx, "leaf", dirs.length === 0)
      if (cb) cb()
    })
  }
  function collapse(i) {
    var d = tm.get(i).depth
    while (i + 1 < tm.count && tm.get(i + 1).depth > d) tm.remove(i + 1)
    tm.setProperty(i, "expanded", false)
  }
  function toggle(i) { if (tm.get(i).expanded) collapse(i); else expand(i, null) }

  function reveal(path) {
    if (!path) return
    var step = function () {
      var p = path, idx = -1
      while (true) {
        idx = root.indexOfPath(p)
        if (idx >= 0) break
        if (p === "/" || p === "") return
        p = Fs.parent(p)
      }
      if (p === path) { list.positionViewAtIndex(idx, ListView.Contain); return }
      if (tm.get(idx).expanded) return
      root.expand(idx, step)
    }
    step()
  }

  ListView {
    id: list
    anchors.fill: parent
    clip: true
    model: tm
    boundsBehavior: Flickable.StopAtBounds
    delegate: Item {
      id: row
      required property int index
      required property string path
      required property string name
      required property int depth
      required property bool expanded
      required property bool loading
      required property bool leaf
      required property bool isRoot
      required property string glyph
      width: list.width; height: 26
      readonly property bool isCur: root_.current === path
      Rectangle { anchors.fill: parent; color: row.isCur ? Theme.selection : (ma.containsMouse ? Theme.hover : "transparent") }
      Rectangle { visible: row.isCur; width: 2; height: parent.height; color: Theme.accent }
      Item {
        id: chev
        x: 10 + row.depth * 14; width: 18; height: parent.height
        Ico { anchors.centerIn: parent; visible: !row.leaf && !row.loading; text: ""; size: 8; color: Theme.fgDim
          rotation: row.expanded ? 90 : 0; Behavior on rotation { NumberAnimation { duration: Theme.dFast } } }
        Ico { anchors.centerIn: parent; visible: row.loading; text: ""; size: 9; color: Theme.accent
          RotationAnimator on rotation { running: row.loading; from: 0; to: 360; duration: 700; loops: Animation.Infinite } }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root_.toggle(row.index) }
      }
      Ico { x: chev.x + 20; width: 18; height: parent.height
        text: row.glyph !== "" ? row.glyph : (row.expanded ? "" : "")
        size: 12; color: row.isCur ? Theme.accent : (row.isRoot ? Theme.fgBright : Theme.fgDim) }
      Label { x: chev.x + 42; width: parent.width - x - 8; height: parent.height
        text: row.name; color: row.isCur ? Theme.fgBright : Theme.fg; font.bold: row.isCur || row.isRoot }
      MouseArea { id: ma; anchors.fill: parent; anchors.leftMargin: chev.x + 18; hoverEnabled: true
        onClicked: root_.navigate(row.path)
        onDoubleClicked: root_.toggle(row.index) }
    }
  }
  property alias view: list
  readonly property var root_: root
}

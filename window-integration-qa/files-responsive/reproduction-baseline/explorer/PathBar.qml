import QtQuick
import qs.Commons
import qs.Ui

// Breadcrumb bar that turns into a typeable path field (click empty space,
// Ctrl+L or "/"). Tab completes directories (longest common prefix, then cycles).
Item {
  id: root
  property string path: ""          // "" = Home dashboard
  property string icon: ""
  property string label: ""         // overrides breadcrumbs (search results)
  property bool editing: false
  signal navigate(string path)
  signal editDone()
  implicitHeight: 32

  property var cands: []
  property int candIdx: -1
  property string completing: ""    // the prefix candidates were computed for

  function startEdit() {
    input.text = root.path ? root.path + (root.path === "/" ? "" : "/") : Fs.home + "/"
    editing = true
    input.forceActiveFocus(); input.selectAll()
    refreshCands()
  }
  function stopEdit() { editing = false; cands = []; candIdx = -1; root.editDone() }

  function splitPrefix(t) {   // -> [dir, partial]
    t = Fs.expand(t)
    var i = t.lastIndexOf("/")
    return [i <= 0 ? "/" : t.slice(0, i), t.slice(i + 1)]
  }
  function refreshCands() {
    var sp = splitPrefix(input.text), dir = sp[0], part = sp[1].toLowerCase()
    completing = input.text
    Fs.list(dir, function (es) {
      if (!root.editing || root.completing !== input.text) return
      var out = []
      if (es) for (var i = 0; i < es.length; i++)
        if (es[i].isDir && es[i].name.toLowerCase().indexOf(part) === 0 && (part.length > 0 || !es[i].hidden)) out.push(es[i].name)
      out.sort(function (a, b) { return a.toLowerCase().localeCompare(b.toLowerCase()) })
      root.cands = out; root.candIdx = -1
    })
  }
  function lcp(arr) {
    if (!arr.length) return ""
    var p = arr[0]
    for (var i = 1; i < arr.length; i++) { var j = 0; while (j < p.length && j < arr[i].length && p[j].toLowerCase() === arr[i][j].toLowerCase()) j++; p = p.slice(0, j) }
    return p
  }
  function complete(back) {
    if (!cands.length) return
    var sp = splitPrefix(input.text), dir = sp[0] === "/" ? "" : sp[0]
    var common = lcp(cands)
    if (candIdx < 0 && common.length > sp[1].length) {
      input.text = dir + "/" + common + (cands.length === 1 ? "/" : "")
      input.cursorPosition = input.text.length
      if (cands.length === 1) refreshCands()
      return
    }
    var n = cands.length
    candIdx = back ? (candIdx <= 0 ? n - 1 : candIdx - 1) : (candIdx + 1) % n
    var keep = completing
    input.text = dir + "/" + cands[candIdx] + "/"
    input.cursorPosition = input.text.length
    completing = keep
  }
  function commit() {
    var t = Fs.norm(Fs.expand(input.text))
    stopEdit(); navigate(t)
  }

  Rectangle {
    anchors.fill: parent
    color: root.editing ? Theme.bgDark : "transparent"
    border.width: 1
    border.color: root.editing ? Theme.accent : (hoverMa.containsMouse ? Theme.lineStrong : Theme.line)
    radius: Theme.radius
    Behavior on border.color { ColorAnimation { duration: Theme.dFast } }
  }

  // breadcrumb mode
  MouseArea { id: hoverMa; anchors.fill: parent; hoverEnabled: true; visible: !root.editing
    cursorShape: Qt.IBeamCursor; onClicked: root.startEdit() }
  Item {
    visible: !root.editing
    anchors { fill: parent; leftMargin: 1; rightMargin: 1 }
    clip: true
  Row {
    id: crumbs
    x: Math.min(10, parent.width - width - 10)
    height: parent.height
    spacing: 0
    Ico { text: root.icon.length ? root.icon : (root.path === "" ? "\uf015" : "\uf07b"); size: 13; color: Theme.accent; anchors.verticalCenter: parent.verticalCenter; width: 28 }
    Label { visible: root.path === "" || root.label.length; leftPadding: 0; text: root.label.length ? root.label : "Home"; color: Theme.fgBright; font.bold: true; anchors.verticalCenter: parent.verticalCenter }
    Repeater {
      model: root.path === "" || root.label.length ? [] : segs
      delegate: Row {
        required property var modelData
        required property int index
        height: crumbs.height
        Ico { visible: index > 0; text: ""; size: 8; color: Theme.fgDim; width: 16; anchors.verticalCenter: parent.verticalCenter }
        Rectangle {
          anchors.verticalCenter: parent.verticalCenter
          width: seg.implicitWidth + 10; height: 22
          color: segMa.containsMouse ? Theme.hover : "transparent"
          Label { id: seg; anchors.centerIn: parent; text: modelData.name
            color: index === segs.length - 1 ? Theme.fgBright : Theme.fg; font.bold: index === segs.length - 1 }
          MouseArea { id: segMa; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
            onClicked: root.navigate(modelData.path) }
        }
      }
    }
  }
  }
  readonly property var segs: {
    var out = [], p = root.path
    if (!p) return out
    if (p === Fs.home || p.indexOf(Fs.home + "/") === 0) {
      out.push({ name: "~", path: Fs.home })
      var rest = p.slice(Fs.home.length).split("/").filter(function (x) { return x.length })
      var acc = Fs.home
      for (var i = 0; i < rest.length; i++) { acc += "/" + rest[i]; out.push({ name: rest[i], path: acc }) }
    } else {
      out.push({ name: "/", path: "/" })
      var r2 = p.split("/").filter(function (x) { return x.length }), a2 = ""
      for (var j = 0; j < r2.length; j++) { a2 += "/" + r2[j]; out.push({ name: r2[j], path: a2 }) }
    }
    return out
  }

  // edit mode
  Ico { visible: root.editing; text: ""; size: 12; color: Theme.accent; x: 10; anchors.verticalCenter: parent.verticalCenter }
  TextInput {
    id: input
    visible: root.editing
    anchors { left: parent.left; leftMargin: 32; right: parent.right; rightMargin: 10; verticalCenter: parent.verticalCenter }
    font.family: Theme.font; font.pixelSize: Theme.fsBody + 1
    color: Theme.fgBright; selectionColor: Theme.accent; selectedTextColor: Theme.bg
    clip: true
    onTextEdited: if (root.editing) root.refreshCands()
    Keys.priority: Keys.BeforeItem
    Keys.onPressed: (e) => {
      if (e.key === Qt.Key_Tab) { root.complete(false); e.accepted = true }
      else if (e.key === Qt.Key_Backtab) { root.complete(true); e.accepted = true }
      else if (e.key === Qt.Key_Escape) { root.stopEdit(); e.accepted = true }
      else if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) { root.commit(); e.accepted = true }
      else if (e.key === Qt.Key_Down) { root.complete(false); e.accepted = true }
      else if (e.key === Qt.Key_Up) { root.complete(true); e.accepted = true }
    }
    onActiveFocusChanged: if (!activeFocus && root.editing) root.stopEdit()
  }

  // completion popup
  Rectangle {
    visible: root.editing && root.cands.length > 0
    y: root.height + 2; x: 0
    width: Math.min(root.width, 420)
    height: Math.min(root.cands.length, 8) * 26 + 8
    color: Theme.bg; border.color: Theme.accent; border.width: 1
    z: 50
    Column {
      x: 4; y: 4; width: parent.width - 8
      Repeater {
        model: root.cands.slice(0, 8)
        delegate: Rectangle {
          required property string modelData
          required property int index
          width: parent.width; height: 26
          color: index === root.candIdx ? Theme.alpha(Theme.accent, 0.18) : "transparent"
          Row { x: 8; spacing: 8; anchors.verticalCenter: parent.verticalCenter
            Ico { text: ""; size: 12; color: Theme.accent; anchors.verticalCenter: parent.verticalCenter }
            Label { text: modelData; color: Theme.fgBright; anchors.verticalCenter: parent.verticalCenter } }
        }
      }
    }
    Label { visible: root.cands.length > 8; anchors { right: parent.right; rightMargin: 8; bottom: parent.bottom; bottomMargin: 4 }
      text: "+" + (root.cands.length - 8); color: Theme.fgDim; font.pixelSize: Theme.fsSmall }
  }
}

import QtQuick
import qs.Commons
import qs.Ui

// Space-bar preview: full-window scrim, big image / poster frame / cover, arrows to browse the folder.
Item {
  id: root
  required property var ex
  anchors.fill: parent
  z: 120
  readonly property var e: (ex.lbIdx >= 0 && ex.lbIdx < ex.shown.length) ? ex.shown[ex.lbIdx] : null
  readonly property string kind: e ? (e.isDir ? "folder" : Fs.kindOf(e)) : ""
  property string gen: ""
  onEChanged: {
    gen = ""
    if (e && !e.isDir && Fs.isThumbGen(e)) { var p = e.path; Thumbs.request(p, function (g) { if (root && root.e && root.e.path === p) root.gen = g }) }
  }
  opacity: visible ? 1 : 0
  Behavior on opacity { NumberAnimation { duration: 150 } }

  Rectangle { anchors.fill: parent; color: Theme.alpha(Theme.bgDarker, 0.97) }
  MouseArea { anchors.fill: parent; onClicked: root.ex.lbOpen = false }

  Item {
    id: stage
    anchors { fill: parent; topMargin: 64; bottomMargin: 76; leftMargin: root.width < 600 ? 62 : 90; rightMargin: root.width < 600 ? 62 : 90 }
    Image {
      id: big
      anchors.fill: parent
      visible: root.kind === "image" || (root.gen.length > 0)
      source: root.kind === "image" ? Fs.url(root.e.path) : (root.gen ? "file://" + root.gen : "")
      asynchronous: true; smooth: true; mipmap: true
      fillMode: Image.PreserveAspectFit
      sourceSize: Qt.size(2000, 2000)
      opacity: status === Image.Ready ? 1 : 0
      Behavior on opacity { NumberAnimation { duration: 200 } }
    }
    Ico { anchors.centerIn: parent; visible: !big.visible || big.status !== Image.Ready
      text: root.e ? Fs.iconFor(root.e) : ""; size: 96; color: root.e ? Theme.alpha(Fs.colorFor(root.e), 0.7) : Theme.fgDim }
    Rectangle { visible: root.kind === "video" && big.status === Image.Ready; anchors.centerIn: parent; width: 64; height: 64
      color: Theme.alpha(Theme.bgDarker, 0.7); border.width: 2; border.color: Theme.fgBright
      Ico { anchors.centerIn: parent; text: ""; size: 24; color: Theme.fgBright } }
  }

  // top bar
  Item {
    width: parent.width; height: 52
    Row { x: 24; width: parent.width - 98; anchors.verticalCenter: parent.verticalCenter; spacing: 12
      Ico { text: root.e ? Fs.iconFor(root.e) : ""; size: 16; color: root.e ? Fs.colorFor(root.e) : Theme.fg; anchors.verticalCenter: parent.verticalCenter }
      Label { width: parent.width - 28; text: root.e ? root.e.name : ""; font.pixelSize: 15; font.bold: true; color: Theme.fgBright; anchors.verticalCenter: parent.verticalCenter }
    }
    Btn { anchors { right: parent.right; rightMargin: 20; verticalCenter: parent.verticalCenter } icon: ""; onClicked: root.ex.lbOpen = false }
  }
  // bottom bar
  Item {
    anchors.bottom: parent.bottom; width: parent.width; height: 60
    Label { x: 24; y: 0; width: parent.width - 48; height: 24; color: Theme.fgDim
      text: root.e ? (root.e.isDir ? "Folder" : Fs.size(root.e.size)) + "  ·  " + Fs.longDate(root.e.mtime) + "  ·  " + Fs.tilde(Fs.parent(root.e.path)) : "" }
    Label { x: 24; y: 30; text: (root.ex.lbIdx + 1) + " / " + root.ex.shown.length; color: Theme.fgBright; font.bold: true }
    Label { anchors { right: parent.right; rightMargin: 24 } y: 30; width: Math.max(0, parent.width - 130); color: Theme.fgDim; text: root.width < 600 ? "← → browse · Esc close" : "←  →  browse    Enter  open    Space / Esc  close" }
  }
  // arrows
  Btn { x: 24; anchors.verticalCenter: parent.verticalCenter; icon: ""; enabled2: root.ex.lbIdx > 0; onClicked: root.ex.lbMove(-1) }
  Btn { anchors { right: parent.right; rightMargin: 24; verticalCenter: parent.verticalCenter } icon: ""; enabled2: root.ex.lbIdx < root.ex.shown.length - 1; onClicked: root.ex.lbMove(1) }
}

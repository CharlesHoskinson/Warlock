import "file:///home/hoskinson/.local/share/omarchy-files-native/WindowAccessibilityV6_editable_20261001"
import QtQuick
import qs.Commons
import qs.Ui

// Gallery card: adaptive thumbnail (media cover / folder mosaic / tinted glyph) + name + meta.
// Chrome stays Omarchy-square: hairline frames, 2px accent selection ring.
Item {
  id: cell
  readonly property string actionIdentity:e ? "file:"+e.path : ""
  property var e: ({})
  property real cw: 200
  property real th: 148
  property bool sel: false
  property bool cur: false
  Accessible.role: Accessible.ListItem
  Accessible.name: e.name || ""
  Accessible.description: e.path || ""
  Accessible.focusable: true
  Accessible.selectable: true
  Accessible.selected: sel
  Accessible.onPressAction: if(ActionState.allowed(cell)) activated()
  Accessible.onToggleAction: toggled()
  signal pressed(int modifiers, int button, real x, real y)
  signal activated()
  signal toggled()

  width: cw
  height: th + 46
  readonly property bool hov: ma.containsMouse || activeFocus
  readonly property string kind: e.isDir ? "folder" : Fs.kindOf(e)
  readonly property color kcolor: Fs.colorFor(e)
  property var pv: ({ count: -1, paths: [] })

  Component.onCompleted: if (e.isDir) Thumbs.preview(e.path, function (r) { cell.pv = r })

  Rectangle {
    id: tile
    width: cell.cw; height: cell.th
    color: Theme.bgDark
    radius: Theme.radius
    border.width: 1; border.color: cell.hov ? Theme.lineStrong : Theme.line
    clip: true

    Item {
      anchors.fill: parent
      scale: cell.hov ? 1.05 : 1
      Behavior on scale { NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }
      Loader {
        anchors.fill: parent
        sourceComponent: cell.e.isDir ? folderC : (Fs.isMedia(cell.e) ? mediaC : fileC)
      }
    }

    Rectangle {
      anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
      height: parent.height * 0.42
      opacity: cell.hov || cell.sel ? 1 : 0
      Behavior on opacity { NumberAnimation { duration: 180 } }
      gradient: Gradient {
        GradientStop { position: 0; color: "transparent" }
        GradientStop { position: 1; color: Theme.alpha(Theme.bgDarker, 0.6) }
      }
    }
    Rectangle { anchors.fill: parent; color: Theme.alpha(Theme.accent, 0.18); opacity: cell.sel ? 1 : 0
      Behavior on opacity { NumberAnimation { duration: 140 } } }
    Rectangle {
      anchors.fill: parent; color: "transparent"; radius: Theme.radius
      border.width: cell.sel ? 2 : (cell.cur ? 1 : 0)
      border.color: cell.sel ? Theme.accent : Theme.alpha(Theme.accent, 0.7)
    }

    // checkbox
    Rectangle {
      x: 8; y: 8; width: 20; height: 20
      color: (cell.sel ? Theme.accent : Theme.alpha(Theme.bgDarker, 0.6))
      border.width: 1; border.color: cell.sel ? Theme.accent : Theme.alpha(Theme.fgBright, 0.6)
      opacity: cell.hov || cell.sel ? 1 : 0
      Behavior on opacity { NumberAnimation { duration: 140 } }
      Ico { anchors.centerIn: parent; text: ""; visible: cell.sel; size: 11; color: Theme.bgDarker }
    }

    // badges
    Rectangle {
      visible: cell.kind === "video"
      anchors { left: parent.left; bottom: parent.bottom; margins: 8 }
      width: 26; height: 22; color: Theme.alpha(Theme.bgDarker, 0.75)
      Ico { anchors.centerIn: parent; text: ""; size: 10; color: Theme.fgBright }
    }
    Rectangle {
      visible: cell.e.ext === "pdf" || cell.e.ext === "gif"
      anchors { left: parent.left; bottom: parent.bottom; margins: 8 }
      width: badge.implicitWidth + 12; height: 20; color: Theme.alpha(Theme.bgDarker, 0.75)
      Label { id: badge; anchors.centerIn: parent; text: (cell.e.ext || "").toUpperCase(); font.pixelSize: 10; font.bold: true; color: Theme.fgBright }
    }
  }

  Column {
    anchors.top: tile.bottom; anchors.topMargin: 7
    width: cell.cw
    spacing: 1
    Label {
      width: parent.width; height: 17
      text: cell.e.name || ""
      elide: Text.ElideMiddle
      font.bold: cell.sel
      color: cell.sel ? Theme.accent : (cell.e.hidden ? Theme.fgDim : Theme.fgBright)
    }
    Label {
      width: parent.width; height: 14
      font.pixelSize: Theme.fsSmall
      color: Theme.fgDim
      text: cell.e.isDir ? (cell.pv.count >= 0 ? cell.pv.count + (cell.pv.count === 1 ? " item" : " items") : "Folder")
            : Fs.size(cell.e.size) + (cell.cw >= 150 ? "  ·  " + Fs.ago(cell.e.mtime) : "")
    }
  }

  Component {
    id: mediaC
    Item {
      Thumb { anchors.fill: parent; entry: cell.e; fill: true; size: 40 }
    }
  }
  Component {
    id: fileC
    Rectangle {
      gradient: Gradient {
        GradientStop { position: 0; color: Theme.alpha(cell.kcolor, 0.16) }
        GradientStop { position: 1; color: Theme.alpha(cell.kcolor, 0.04) }
      }
      Ico { anchors.centerIn: parent; anchors.verticalCenterOffset: -6; text: Fs.iconFor(cell.e); size: cell.th * 0.34; color: cell.kcolor }
      Label { anchors.horizontalCenter: parent.horizontalCenter; anchors.bottom: parent.bottom; anchors.bottomMargin: 8
        text: cell.e.ext ? cell.e.ext.toUpperCase() : ""; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1.5
        color: Theme.alpha(cell.kcolor, 0.9) }
    }
  }
  Component {
    id: folderC
    Item {
      readonly property var paths: cell.pv.paths
      Rectangle { anchors.fill: parent; visible: paths.length === 0
        gradient: Gradient { GradientStop { position: 0; color: Theme.alpha(Theme.accent, 0.20) } GradientStop { position: 1; color: Theme.alpha(Theme.accent, 0.05) } } }
      Ico { visible: paths.length === 0; anchors.centerIn: parent; text: Fs.folderIcon(cell.e.name); size: cell.th * 0.38; color: Theme.accent }
      Item {
        id: mosaic
        anchors.fill: parent; visible: paths.length > 0
        readonly property real hw: width / 2
        readonly property real hh: height / 2
        Repeater {
          model: paths.length
          delegate: Thumb {
            readonly property int n: paths.length
            readonly property bool isLeft: n === 4 ? index % 2 === 0 : index === 0
            x: n === 1 ? 0 : (isLeft ? 0 : mosaic.hw + 1)
            y: n === 4 ? (index < 2 ? 0 : mosaic.hh + 1) : (n === 3 && index === 2 ? mosaic.hh + 1 : 0)
            width: n === 1 ? mosaic.width : mosaic.hw - 1
            height: (n === 1 || n === 2 || (n === 3 && index === 0)) ? mosaic.height : mosaic.hh - 1
            entry: Fs.entryOf(paths[index]); fill: true; size: 30
          }
        }
      }
      Rectangle {
        visible: paths.length > 0
        anchors { left: parent.left; bottom: parent.bottom }
        width: fl.implicitWidth + 16; height: 24; color: Theme.alpha(Theme.bgDarker, 0.8)
        Row { id: fl; anchors.centerIn: parent; spacing: 6
          Ico { text: ""; size: 12; color: Theme.accent; anchors.verticalCenter: parent.verticalCenter }
          Label { text: cell.pv.count >= 0 ? cell.pv.count : ""; font.pixelSize: 11; color: Theme.fgBright; anchors.verticalCenter: parent.verticalCenter } }
      }
    }
  }

  MouseArea {
    id: ma
    z: 10
    anchors.fill: parent
    property bool onCheck: mouseX >= 6 && mouseX <= 30 && mouseY >= 6 && mouseY <= 30
    cursorShape: onCheck ? Qt.PointingHandCursor : Qt.ArrowCursor
    hoverEnabled: true
    acceptedButtons: Qt.LeftButton | Qt.RightButton
    onPressed: (m) => { if (m.button === Qt.LeftButton && m.x >= 6 && m.x <= 30 && m.y >= 6 && m.y <= 30) cell.toggled(); else cell.pressed(m.modifiers, m.button, m.x, m.y) }
    onDoubleClicked: (m) => { if (m.button === Qt.LeftButton) cell.activated() }
  }
}

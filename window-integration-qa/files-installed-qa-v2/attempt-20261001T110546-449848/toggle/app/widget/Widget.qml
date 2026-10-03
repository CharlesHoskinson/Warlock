import QtQuick
import Quickshell
import Quickshell.Wayland
import qs.Commons
import qs.Ui

// Desktop entry-point widget (BOTTOM layer, no exclusive zone, anchored top-right so the
// compositor keeps it clear of the bar). Clock + go-to/search + recent-media mosaic +
// pinned folders + smart-collection counters + storage strip. Everything opens the explorer.
PanelWindow {
  id: win; objectName: "Widget.win"
  signal openRequested(string path, string query)
  signal fileRequested(string path)
  signal searchRequested(string query)

  WlrLayershell.namespace: "files-fusion-a-widget"
  WlrLayershell.layer: WlrLayer.Bottom
  WlrLayershell.keyboardFocus: WlrKeyboardFocus.OnDemand
  exclusionMode: ExclusionMode.Ignore
  anchors { top: true; right: true }
  margins { top: 36; right: 10 }
  implicitWidth: 400
  implicitHeight: col.y + col.implicitHeight + 20
  color: "transparent"

  readonly property var media: Data.recentMedia
  readonly property var pinned: Data.pins.slice(0, 6)
  readonly property var tiles: ["images", "videos", "documents", "large"]

  function submit() {
    var t = field.text.trim()
    if (!t.length) { openRequested("", ""); return }
    if (t.charAt(0) === "/" || t.charAt(0) === "~") openRequested(Fs.norm(Fs.expand(t)), "")
    else searchRequested(t)
    field.text = ""
  }
  function grab(path) { card.grabToImage(function (r) { r.saveToFile(path); console.log('[files] saved ' + path) }, Qt.size(card.width * 1.6, card.height * 1.6)) }

  component MediaTile: Rectangle {
    id: mt; objectName: "Widget.mt"
    property var e: null
    color: Theme.bgDark
    border.width: 1; border.color: tma.containsMouse ? Theme.accent : Theme.line
    clip: true
    Item {
      anchors.fill: parent
      scale: tma.containsMouse ? 1.07 : 1
      Behavior on scale { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
      Thumb { anchors.fill: parent; entry: mt.e; fill: true; size: 30 }
    }
    Rectangle {
      anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
      height: 34; opacity: tma.containsMouse ? 1 : 0
      Behavior on opacity { NumberAnimation { duration: 160 } }
      gradient: Gradient { GradientStop { position: 0; color: "transparent" } GradientStop { position: 1; color: Theme.alpha(Theme.bgDarker, 0.88) } }
      Label { x: 8; anchors.bottom: parent.bottom; anchors.bottomMargin: 5; width: parent.width - 16; height: 14; text: mt.e ? mt.e.name : ""; font.pixelSize: Theme.fsSmall; color: Theme.fgBright }
    }
    Rectangle { visible: !!mt.e && Fs.kindOf(mt.e) === "video"; x: 5; y: 5; width: 20; height: 16; color: Theme.alpha(Theme.bgDarker, 0.75)
      Ico { anchors.centerIn: parent; text: ""; size: 8; color: Theme.fgBright } }
    MouseArea { id: tma; objectName: "Widget.tma"; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: if (mt.e) win.fileRequested(mt.e.path) }
  }

  Rectangle {
    id: card; objectName: "Widget.card"
    anchors.fill: parent
    color: Theme.alpha(Theme.bg, 0.94)
    border.width: 2
    border.color: Theme.accent
    radius: Theme.radius

    Column {
      id: col; objectName: "Widget.col"
      x: 20; y: 18; width: parent.width - 40
      spacing: 14

      // header
      Item {
        id: hdr; objectName: "Widget.hdr"
        width: parent.width; height: 52
        Column {
          Label { text: Qt.formatTime(clock.date, "HH:mm"); font.pixelSize: 30; font.bold: true; color: Theme.fgBright; height: 34 }
          Label { text: Qt.formatDate(clock.date, "dddd, d MMMM"); font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim; height: 16 }
        }
        Rectangle {
          anchors.right: parent.right; anchors.top: parent.top
          width: openLbl.implicitWidth + 24 + 20; height: 28
          color: openMa.containsMouse ? Theme.accent : "transparent"; border.width: 1; border.color: Theme.accent
          Behavior on color { ColorAnimation { duration: Theme.dFast } }
          Row { anchors.centerIn: parent; spacing: 7
            Ico { text: ""; size: 12; color: openMa.containsMouse ? Theme.bg : Theme.accent; anchors.verticalCenter: parent.verticalCenter }
            Label { id: openLbl; objectName: "Widget.openLbl"; text: "Files"; font.bold: true; color: openMa.containsMouse ? Theme.bg : Theme.accent; anchors.verticalCenter: parent.verticalCenter } }
          MouseArea { id: openMa; objectName: "Widget.openMa"; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: win.openRequested("", "") }
        }
      }
      SystemClock { id: clock; objectName: "Widget.clock"; precision: SystemClock.Minutes }

      // path / search field
      Rectangle {
        width: parent.width; height: 36
        color: field.activeFocus ? Theme.bgDark : Theme.alpha(Theme.fg, 0.04)
        border.width: 1; border.color: field.activeFocus ? Theme.accent : Theme.line
        Behavior on border.color { ColorAnimation { duration: Theme.dFast } }
        Ico { x: 10; width: 18; height: parent.height; text: ""; size: 12; color: field.activeFocus ? Theme.accent : Theme.fgDim }
        TextInput {
          id: field; objectName: "Widget.field"
          anchors { left: parent.left; leftMargin: 34; right: parent.right; rightMargin: 10; verticalCenter: parent.verticalCenter }
          font.family: Theme.font; font.pixelSize: Theme.fsBody; color: Theme.fgBright; clip: true
          selectionColor: Theme.accent; selectedTextColor: Theme.bg
          Keys.onPressed: (e) => { if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) { win.submit(); e.accepted = true } }
        }
        Label { visible: !field.text.length; x: 34; height: parent.height; text: "Go to path or search files…"; color: Theme.fgDim }
      }

      // recent media
      Item {
        width: parent.width; height: 22
        Section { anchors.fill: parent; text: "Recent"; note: "Timeline  ›" }
        MouseArea { anchors.right: parent.right; width: 90; height: parent.height; cursorShape: Qt.PointingHandCursor; onClicked: win.openRequested("coll:recent", "") }
      }
      Item {
        id: mos; objectName: "Widget.mos"
        width: parent.width; height: win.media.length > 0 ? 150 + 6 + 54 : 40
        readonly property real rw: 128
        Label { visible: win.media.length === 0; anchors.centerIn: parent; text: "Scanning your library…"; color: Theme.fgDim }
        MediaTile { visible: win.media.length > 0; e: win.media[0] || null; width: mos.width - mos.rw - 6; height: 150 }
        MediaTile { visible: win.media.length > 1; e: win.media[1] || null; x: mos.width - mos.rw; width: mos.rw; height: 72 }
        MediaTile { visible: win.media.length > 2; e: win.media[2] || null; x: mos.width - mos.rw; y: 78; width: mos.rw; height: 72 }
        Repeater {
          model: Math.max(0, Math.min(5, win.media.length - 3))
          delegate: MediaTile { e: win.media[3 + index]; x: index * ((mos.width - 24) / 5 + 6); y: 156; width: (mos.width - 24) / 5; height: 54 }
        }
      }

      // pinned
      Section { width: parent.width; text: "Pinned" }
      Grid {
        columns: 3; spacing: 6
        Repeater {
          model: win.pinned
          delegate: Item {
            id: pt; objectName: "Widget.pt"
            required property string modelData
            width: Math.floor((col.width - 12) / 3); height: 38
            Rectangle { anchors.fill: parent; color: pm.containsMouse ? Theme.alpha(Theme.accent, 0.12) : Theme.alpha(Theme.fg, 0.035)
              border.width: 1; border.color: pm.containsMouse ? Theme.accent : Theme.line
              Behavior on color { ColorAnimation { duration: Theme.dFast } } }
            Row { anchors.centerIn: parent; spacing: 8
              Ico { text: pt.modelData === Fs.home ? "" : Fs.folderIcon(Fs.base(pt.modelData)); size: 14; color: Theme.accent; anchors.verticalCenter: parent.verticalCenter }
              Label { text: pt.modelData === Fs.home ? "Home" : Fs.base(pt.modelData); elide: Text.ElideNone; color: Theme.fgBright; anchors.verticalCenter: parent.verticalCenter } }
            MouseArea { id: pm; objectName: "Widget.pm"; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: win.openRequested(pt.modelData, "") }
          }
        }
      }

      // smart collections
      Section { width: parent.width; text: "Smart collections" }
      Row {
        spacing: 6
        readonly property real cwid: (col.width - 18) / 4
        Repeater {
          model: win.tiles
          delegate: Rectangle {
            id: cc; objectName: "Widget.cc"
            required property string modelData
            readonly property var info: Data.collInfo(modelData)
            readonly property color kc: Theme.byKey(info.color)
            width: parent.cwid; height: 58
            color: cma.containsMouse ? Theme.alpha(kc, 0.16) : Theme.alpha(Theme.fg, 0.035)
            border.width: 1; border.color: cma.containsMouse ? Theme.alpha(kc, 0.8) : Theme.line
            Behavior on color { ColorAnimation { duration: Theme.dFast } }
            Rectangle { width: 2; height: parent.height; color: cc.kc }
            Ico { x: 10; y: 8; width: 14; height: 18; text: cc.info.glyph; size: 12; color: cc.kc }
            Label { anchors.right: parent.right; anchors.rightMargin: 8; y: 6; height: 22; text: Data.collCount(cc.modelData); font.pixelSize: 16; font.bold: true; color: Theme.fgBright }
            Label { x: 10; anchors.bottom: parent.bottom; anchors.bottomMargin: 6; width: parent.width - 14; height: 14; text: cc.info.name; font.pixelSize: Theme.fsSmall; color: Theme.fg }
            MouseArea { id: cma; objectName: "Widget.cma"; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: win.openRequested("coll:" + cc.modelData, "") }
          }
        }
      }

      // storage glance
      Item {
        id: sg; objectName: "Widget.sg"
        width: parent.width; height: 74
        Section { width: parent.width; text: "Storage"; note: Fs.size(Math.max(0, Data.diskSize - Data.diskUsed)) + " free" }
        Row {
          y: 30; width: parent.width; height: 8; spacing: 1
          Repeater {
            model: Data.usage.slice(0, 6)
            delegate: Rectangle {
              required property var modelData
              required property int index
              width: Math.max(2, (sg.width - 6) * modelData.size / Math.max(1, Data.usageTotal)); height: 8
              color: Theme.palette[index % Theme.palette.length]
            }
          }
        }
        Row {
          y: 46; spacing: 14
          Repeater {
            model: Data.usage.slice(0, 3)
            delegate: Row {
              required property var modelData
              required property int index
              spacing: 5
              Rectangle { width: 6; height: 6; y: 5; color: Theme.palette[index % Theme.palette.length] }
              Label { text: modelData.name + " " + Fs.size(modelData.size); font.pixelSize: Theme.fsSmall; color: Theme.fg; elide: Text.ElideNone }
            }
          }
        }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: win.openRequested("", "") }
      }
    }
  }
}

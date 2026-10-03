import QtQuick
import qs.Commons
import qs.Ui

// "Home" view: pinned tiles, storage treemap, recent files, quick filters.
Item {
  id: root; objectName:"Dashboard.root"
  required property var ex
  function scrollPosition() { return fl.contentY }
  function restoreScroll(y) { fl.contentY = y }
  property string kindFilter: "all"
  readonly property string q: ex.filter.toLowerCase()

  readonly property var filters: [
    { id: "all", label: "All", icon: "" },
    { id: "document", label: "Documents", icon: "" },
    { id: "image", label: "Images", icon: "" },
    { id: "video", label: "Video", icon: "" },
    { id: "audio", label: "Audio", icon: "" },
    { id: "code", label: "Code", icon: "" },
    { id: "archive", label: "Archives", icon: "" }
  ]
  readonly property var pinList: Data.pins.filter(function (p) { return !q || Fs.base(p).toLowerCase().indexOf(q) >= 0 })
  readonly property var recentList: Data.recents.filter(function (e) {
    return (kindFilter === "all" || Fs.kindOf(e) === kindFilter) && (!q || e.name.toLowerCase().indexOf(q) >= 0)
  })

  readonly property bool compact: width < 900
  readonly property int pad: compact ? 14 : 28
  readonly property real cw: width - pad * 2
  readonly property var media: Data.recentMedia

  component MediaTile: Rectangle {
    id: mt; objectName:"Dashboard.mt"
    property var e: null
    property bool big: false
    color: Theme.bgDark
    border.width: 1; border.color: tma.containsMouse ? Theme.accent : Theme.line
    clip: true
    Item {
      anchors.fill: parent
      scale: tma.containsMouse ? 1.06 : 1
      Behavior on scale { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
      Thumb { anchors.fill: parent; entry: mt.e; fill: true; size: 36 }
    }
    Rectangle {
      anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
      height: mt.big ? 64 : 42; opacity: tma.containsMouse || mt.big ? 1 : 0
      Behavior on opacity { NumberAnimation { duration: 160 } }
      gradient: Gradient { GradientStop { position: 0; color: "transparent" } GradientStop { position: 1; color: Theme.alpha(Theme.bgDarker, 0.88) } }
      Label { x: 10; anchors.bottom: sub.top; width: parent.width - 20; height: 16; text: mt.e ? mt.e.name : ""; color: Theme.fgBright; font.bold: mt.big }
      Label { id: sub; objectName:"Dashboard.sub"; visible: mt.big; x: 10; anchors.bottom: parent.bottom; anchors.bottomMargin: 8; width: parent.width - 20; height: 14
        text: mt.e ? Fs.tilde(Fs.parent(mt.e.path)) + "  ·  " + Fs.ago(mt.e.mtime) : ""; font.pixelSize: Theme.fsSmall; color: Theme.fg }
    }
    Rectangle { visible: !!mt.e && Fs.kindOf(mt.e) === "video"; x: 6; y: 6; width: 22; height: 18; color: Theme.alpha(Theme.bgDarker, 0.75)
      Ico { anchors.centerIn: parent; text: "\uf04b"; size: 9; color: Theme.fgBright } }
    MouseArea { id: tma; objectName:"Dashboard.tma"; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; acceptedButtons: Qt.LeftButton | Qt.RightButton
      onClicked: (m) => { if (!mt.e) return
        if (m.button === Qt.RightButton) { var p = mt.mapToItem(root, m.x, m.y); root.ex.recentMenu(mt.e, p.x, p.y) }
        else root.ex.revealEntry(mt.e) } }
  }

  Flickable {
    id: fl; objectName:"Dashboard.fl"
    anchors.fill: parent
    contentWidth: width; contentHeight: lower.y + lower.height + 24
    clip: true
    boundsBehavior: Flickable.StopAtBounds

    // ---- header
    Column {
      id: head; objectName:"Dashboard.head"
      x: root.pad; y: 16; width: root.compact ? root.cw : Math.max(150, root.cw - filters.width - 20)
      spacing: 2
      Label { width: parent.width; text: "Home"; font.pixelSize: root.compact ? 24 : Theme.fsTitle + 4; font.bold: true; color: Theme.fgBright }
      Label { width: parent.width; text: (envq.user) + "  ·  " + Qt.formatDate(new Date(), "dddd d MMMM"); font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim }
    }
    QtObject { id: envq; objectName:"Dashboard.envq"; readonly property string user: Fs.home.split("/").pop() }
    Flow {
      id: filters; objectName:"Dashboard.filters"
      x: root.compact ? root.pad : fl.width - width - root.pad
      y: root.compact ? head.y + head.height + 12 : head.y + 10
      width: root.compact ? root.cw : 690
      spacing: 6
      Repeater {
        model: root.filters
        delegate: Chip { required property var modelData; text: modelData.label; icon: modelData.icon; active: root.kindFilter === modelData.id
          onClicked: root.kindFilter = modelData.id }
      }
    }

    // ---- recent media mosaic + smart collection counters
    Item {
      id: hero; objectName:"Dashboard.hero"
      x: root.pad; y: Math.max(head.y + head.height, filters.y + filters.height) + 20; width: root.cw
      readonly property real leftW: root.compact ? width : Math.round(width * 0.60)
      readonly property real rightW: root.compact ? width : width - leftW - 16
      height: root.compact ? 504 : 240
      Section { width: hero.leftW; text: "Recent media"; note: "timeline  ›" }
      MouseArea { x: hero.leftW - 90; width: 90; height: 22; cursorShape: Qt.PointingHandCursor; onClicked: root.ex.go("coll:recent") }
      Section { x: root.compact ? 0 : hero.leftW + 16; y: root.compact ? 264 : 0; width: hero.rightW; text: "Smart collections" }

      Item {
        id: mos; objectName:"Dashboard.mos"
        y: 32; width: hero.leftW; height: 208
        readonly property real c1: Math.round(width * 0.46)
        readonly property real c2: Math.round((width - c1 - 16) / 2)
        Label { visible: root.media.length === 0; anchors.centerIn: parent; text: "Scanning your library…"; color: Theme.fgDim }
        MediaTile { visible: root.media.length > 0; e: root.media[0] || null; big: true; width: mos.c1; height: 208 }
        MediaTile { visible: root.media.length > 1; e: root.media[1] || null; x: mos.c1 + 8; width: mos.c2; height: 100 }
        MediaTile { visible: root.media.length > 2; e: root.media[2] || null; x: mos.c1 + 8; y: 108; width: mos.c2; height: 100 }
        MediaTile { visible: root.media.length > 3; e: root.media[3] || null; x: mos.c1 + 16 + mos.c2; width: mos.width - x; height: 100 }
        MediaTile { visible: root.media.length > 4; e: root.media[4] || null; x: mos.c1 + 16 + mos.c2; y: 108; width: mos.width - x; height: 100 }
      }
      Column {
        id: cg; objectName:"Dashboard.cg"
        x: root.compact ? 0 : hero.leftW + 16; y: root.compact ? 296 : 32; width: hero.rightW; spacing: 8
        readonly property real cwid: (width - 8) / 2
        readonly property real chgt: (208 - 3 * 8) / 4
        component CollCard: Rectangle {
          id: cc; objectName:"Dashboard.cc"
          property var info: null
          readonly property color kc: Theme.byKey(info.color)
          height: cg.chgt
          color: cma.containsMouse ? Theme.alpha(kc, 0.16) : Theme.alpha(Theme.fg, 0.03)
          border.width: 1; border.color: cma.containsMouse ? Theme.alpha(kc, 0.8) : Theme.line
          Behavior on color { ColorAnimation { duration: Theme.dFast } }
          Rectangle { width: 2; height: parent.height; color: cc.kc }
          Ico { x: 12; width: 18; height: parent.height; text: cc.info.glyph; size: 13; color: cc.kc }
          Label { x: 38; width: Math.max(25, parent.width - 38 - 40); height: parent.height; text: cc.info.name; color: Theme.fgBright }
          Label { anchors.right: parent.right; anchors.rightMargin: 12; height: parent.height; text: Data.collCount(cc.info.id)
            font.pixelSize: 16; font.bold: true; color: Theme.fgBright }
          MouseArea { id: cma; objectName:"Dashboard.cma"; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.ex.go("coll:" + cc.info.id) }
        }
        CollCard { width: cg.width; info: Data.collections[0] }
        Grid {
          columns: 2; spacing: 8
          Repeater {
            model: Data.collections.slice(1)
            delegate: CollCard { required property var modelData; width: cg.cwid; info: modelData }
          }
        }
      }
    }

    // ---- pinned
    Section { id: pinHdr; objectName:"Dashboard.pinHdr"; x: root.pad; y: hero.y + hero.height + 22; width: root.cw; text: "Pinned"; note: root.pinList.length + " folders   ·   right-click to unpin" }
    Flow {
      id: pins; objectName:"Dashboard.pins"
      x: root.pad; y: pinHdr.y + 32; width: root.cw
      spacing: 8
      Repeater {
        model: root.pinList
        delegate: Item {
          id: tile; objectName:"Dashboard.tile"
          required property string modelData
          required property int index
          readonly property int cols: Math.max(1, Math.floor((pins.width + pins.spacing) / 150))
          width: Math.floor((pins.width - (cols - 1) * pins.spacing) / cols); height: 56
          Rectangle { anchors.fill: parent; color: tma.containsMouse ? Theme.alpha(Theme.accent, 0.10) : Theme.alpha(Theme.fg, 0.03)
            border.width: 1; border.color: tma.containsMouse ? Theme.accent : Theme.line
            Behavior on color { ColorAnimation { duration: Theme.dFast } } Behavior on border.color { ColorAnimation { duration: Theme.dFast } } }
          Rectangle { width: 2; height: parent.height; color: tile.modelData === Fs.home ? Theme.accent : "transparent" }
          Ico { x: 14; y: 10; width: 22; text: tile.modelData === Fs.home ? "\uf015" : Fs.folderIcon(Fs.base(tile.modelData)); size: 18; color: Theme.accent }
          Label { x: 46; y: 9; width: parent.width - 58; text: tile.modelData === Fs.home ? "Home" : Fs.base(tile.modelData); font.bold: true; color: Theme.fgBright }
          Label { x: 46; y: 30; width: parent.width - 58; text: Fs.tilde(tile.modelData); font.pixelSize: Theme.fsSmall; color: Theme.fgDim }
          MouseArea { id: tma; objectName:"Dashboard.tma"; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; acceptedButtons: Qt.LeftButton | Qt.RightButton
            onClicked: (m) => { if (m.button === Qt.RightButton) { var p = tile.mapToItem(root, m.x, m.y); root.ex.pinMenu(tile.modelData, p.x, p.y) } else root.ex.go(tile.modelData) } }
        }
      }
    }

    // ---- storage + recent files
    Item {
      id: lower; objectName:"Dashboard.lower"
      x: root.pad; y: pins.y + pins.height + 22
      width: root.cw; height: root.compact ? 352 + recentPanel.height : 330
      readonly property real leftW: root.compact ? width : Math.round(width * 0.56)

      Item {
        id: stor; objectName:"Dashboard.stor"
        width: root.compact ? lower.width : lower.leftW - 14; height: 330
        Section { width: parent.width; text: "Storage"; note: Data.usageLoading && !Data.usage.length ? "scanning…" : "Home · " + Fs.size(Data.usageTotal) }
        Treemap {
          id: tmap; objectName:"Dashboard.tmap"
          y: 32; width: parent.width; height: parent.height - 32 - 52
          usage: Data.usage; total: Data.usageTotal
          onOpen: (p) => root.ex.go(p)
          Label { visible: !Data.usage.length; anchors.centerIn: parent; text: "Measuring home directory…"; color: Theme.fgDim }
        }
        Item {
          y: parent.height - 44; width: parent.width; height: 44
          Label { width: parent.width; height: 18
            text: tmap.hovered ? (Fs.tilde(tmap.hovered.path) + "   ·   " + Fs.size(tmap.hovered.size) + "   ·   " + (Data.usageTotal ? (100 * tmap.hovered.size / Data.usageTotal).toFixed(1) : 0) + "% of home") : "Click any block to open it"
            color: tmap.hovered ? Theme.fgBright : Theme.fgDim; font.pixelSize: Theme.fsSmall + 1 }
          Rectangle { y: 24; width: parent.width; height: 4; color: Theme.alpha(Theme.fg, 0.10)
            Rectangle { width: parent.width * (Data.diskSize ? Data.diskUsed / Data.diskSize : 0); height: parent.height; color: Theme.accent } }
          Label { y: 30; width: parent.width; height: 14; font.pixelSize: Theme.fsLabel + 1; color: Theme.fgDim
            text: "Disk  " + Fs.size(Data.diskUsed) + " used of " + Fs.size(Data.diskSize) }
        }
      }

      Item {
        id: recentPanel; objectName:"Dashboard.recentPanel"
        x: root.compact ? 0 : lower.leftW; y: root.compact ? 352 : 0; width: root.compact ? lower.width : parent.width - lower.leftW; height: root.compact ? Math.max(80, Math.min(330, 32 + root.recentList.length * 38)) : 330
        Section { width: parent.width; text: "Recent files"; note: root.recentList.length + " files · 30 days" }
        ListView {
          id: rl; objectName:"Dashboard.rl"
          y: 32; width: parent.width; height: parent.height - 32
          clip: true; model: root.recentList; boundsBehavior: Flickable.StopAtBounds
          interactive: contentHeight > height
          delegate: Item {
            id: rr; objectName:"Dashboard.rr"
            required property var modelData
            required property int index
            width: rl.width; height: 38
            Rectangle { anchors.fill: parent; color: rma.containsMouse ? Theme.hover : "transparent" }
            Thumb { x: 6; anchors.verticalCenter: parent.verticalCenter; width: 28; height: 28; entry: rr.modelData; size: 28 }
            Label { x: 44; y: 4; width: parent.width - 44 - 76; height: 16; text: rr.modelData.name; color: Theme.fgBright }
            Label { x: 44; y: 20; width: parent.width - 44 - 76; height: 13; text: Fs.tilde(Fs.parent(rr.modelData.path)); font.pixelSize: Theme.fsLabel + 1; color: Theme.fgDim }
            Label { anchors.right: parent.right; anchors.rightMargin: 6; height: parent.height; text: Fs.ago(rr.modelData.mtime); font.pixelSize: Theme.fsSmall; color: Theme.fgDim }
            MouseArea { id: rma; objectName:"Dashboard.rma"; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; acceptedButtons: Qt.LeftButton | Qt.RightButton
              onClicked: (m) => { if (m.button === Qt.RightButton) { var p = rr.mapToItem(root, m.x, m.y); root.ex.recentMenu(rr.modelData, p.x, p.y) } else root.ex.openEntry(rr.modelData) } }
          }
          Label { visible: rl.count === 0; anchors.centerIn: parent; text: q ? "No matches" : "Nothing here yet"; color: Theme.fgDim }
        }
        ScrollBar_ { view: rl; visible: rl.contentHeight > rl.height }
      }
    }
  }
  ScrollBar_ { view: fl; visible: fl.contentHeight > fl.height }
}

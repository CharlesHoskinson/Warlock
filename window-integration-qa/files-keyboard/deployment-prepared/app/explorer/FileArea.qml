import QtQuick
import qs.Commons
import qs.Ui

// Folder header + list view (columns, sortable) + gallery grid (adaptive cards, zoom, day-grouped timeline).
Item {
  id: area
  required property var ex
  readonly property bool grid: ex.viewMode === "grid"
  readonly property int pad: width < 560 ? 14 : 20
  readonly property bool compactHeader: width < 760
  readonly property int gap: 12
  readonly property real gw: Math.max(200, gridList.width)
  readonly property int columns: Math.max(1, Math.floor((gw - 2 * pad + gap) / (ex.zoom + gap)))
  readonly property real cw: Math.floor((gw - 2 * pad + gap) / columns - gap)
  readonly property real th: Math.max(30, Math.min(Math.round(cw * 0.72), gridList.height - 52))
  readonly property bool timeline: ex.collId === "recent"
  signal contextRequested(real x, real y, int index)

  // rows for the grid ListView: {h:"Today", n} headers and {idx:[...]} cell rows
  readonly property var rows: {
    var out = [], s = ex.shown, cols = columns, lastB = "", cur = null, hdr = null
    for (var i = 0; i < s.length; i++) {
      if (timeline) {
        var b = Fs.dayBucket(s[i].mtime)
        if (b !== lastB) { hdr = { h: b, n: 0 }; out.push(hdr); lastB = b; cur = null }
        hdr.n++
      }
      if (!cur || cur.idx.length >= cols) { cur = { idx: [] }; out.push(cur) }
      cur.idx.push(i)
    }
    return out
  }

  function ensure(i) {
    if (i < 0) return
    if (grid) {
      for (var r = 0; r < rows.length; r++) if (rows[r].idx && rows[r].idx.indexOf(i) >= 0) { gridList.positionViewAtIndex(r, ListView.Contain); break }
    } else listView.positionViewAtIndex(i, ListView.Contain)
  }

  function focusEntry(i) {
    if(i<0 || i>=ex.shown.length) return
    var path=ex.shown[i].path
    ensure(i)
    Qt.callLater(function(){
      if(i>=ex.shown.length || ex.shown[i].path!==path) return
      if(grid) {
        gridList.forceLayout()
        for(var r=0;r<rows.length;r++) if(rows[r].idx && rows[r].idx.indexOf(i)>=0) {
          var row=gridList.itemAtIndex(r);if(row) row.focusEntry(i);break
        }
      } else { listView.forceLayout();var item=listView.itemAtIndex(i);if(item) item.forceActiveFocus() }
    })
  }
  function scrollPosition() { return grid ? gridList.contentY : listView.contentY }

  function scrollTo(y) { if (grid) gridList.contentY = y; else listView.contentY = y }

  // ---- header: title, facts, zoom
  Item {
    id: fhead
    width: parent.width; height: area.compactHeader ? 78 : 62
    Column {
      x: area.pad; y: area.compactHeader ? 5 : 10; width: area.compactHeader ? parent.width - 2 * area.pad : Math.max(100, parent.width - headerActions.width - 3 * area.pad); spacing: 2
      Label { width: parent.width; text: area.ex.areaTitle; font.pixelSize: area.compactHeader ? 18 : Theme.fsHead + 6; font.bold: true; color: Theme.fgBright; height: area.compactHeader ? 22 : 26 }
      Label { width: parent.width; text: area.ex.areaSub; font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim; height: 14 }
    }
    Row {
      id: headerActions
      x: area.compactHeader ? area.pad : parent.width - width - area.pad
      y: area.compactHeader ? 43 : 16
      spacing: 10
      Ico { visible: area.grid && area.width >= 560; anchors.verticalCenter: parent.verticalCenter; text: "\uf03e"; size: 10; color: Theme.fgDim }
      Slider { visible: area.grid && area.width >= 560; anchors.verticalCenter: parent.verticalCenter; width: 120; from: 110; to: 300; value: area.ex.zoom
        onMoved: (v) => area.ex.zoom = Math.round(v) }
      Ico { visible: area.grid && area.width >= 560; anchors.verticalCenter: parent.verticalCenter; text: "\uf03e"; size: 16; color: Theme.fgDim }
      Btn { visible: area.ex.canWrite; anchors.verticalCenter: parent.verticalCenter; icon: "\uf067"; text: "Folder"; onClicked: area.ex.newFolder() }
      Btn { visible: area.ex.canWrite; anchors.verticalCenter: parent.verticalCenter; icon: "\uf067"; text: "File"; onClicked: area.ex.newFile() }
    }
    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.line }
  }

  // ---- column header (list mode)
  readonly property int wDate: width >= 650 ? 140 : 0
  readonly property int wSize: 84
  readonly property int wKind: width >= 480 ? 72 : 0
  Item {
    id: header
    visible: !area.grid
    y: fhead.height
    height: visible ? 28 : 0
    width: parent.width
    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.line }
    Repeater {
      model: [
        { key: "name", label: "NAME", x: 52, right: -1, w: 0 },
        { key: "modified", label: "MODIFIED", w: area.wDate, off: area.wDate + area.wSize + area.wKind + 16 },
        { key: "size", label: "SIZE", w: area.wSize, off: area.wSize + area.wKind + 16, r: true },
        { key: "kind", label: "KIND", w: area.wKind, off: area.wKind + 16 - 12 }
      ]
      delegate: Item {
        required property var modelData
        activeFocusOnTab: true
        Accessible.role: Accessible.Button
        Accessible.name: "Sort by " + modelData.key
        Rectangle {anchors.fill:parent;color:"transparent";border.width:parent.activeFocus ? 1 : 0;border.color:Theme.accent;z:2}
        Accessible.onPressAction: area.ex.setSort(modelData.key)
        Keys.onPressed: (e) => { if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space) {if(!e.isAutoRepeat) area.ex.setSort(modelData.key);e.accepted=true} }
        height: header.height
        visible: modelData.key === "name" || modelData.w > 0
        x: modelData.key === "name" ? 52 : header.width - modelData.off
        width: modelData.key === "name" ? header.width - 52 - (area.wDate + area.wSize + area.wKind + 16) : modelData.w
        Row {
          anchors.verticalCenter: parent.verticalCenter
          anchors.right: modelData.r ? parent.right : undefined
          spacing: 5
          Label { text: modelData.label; font.pixelSize: Theme.fsLabel; font.letterSpacing: 1.2
            color: area.ex.sortKey === modelData.key ? Theme.accent : Theme.fgDim; font.bold: true }
          Ico { visible: area.ex.sortKey === modelData.key; text: area.ex.sortAsc ? "" : ""; size: 9; color: Theme.accent; anchors.verticalCenter: parent.verticalCenter }
        }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: area.ex.setSort(modelData.key) }
      }
    }
  }

  // ---- list
  ListView {
    id: listView
    visible: !area.grid
    anchors { top: header.bottom; left: parent.left; right: parent.right; bottom: parent.bottom }
    clip: true
    model: area.grid ? [] : area.ex.shown
    boundsBehavior: Flickable.StopAtBounds
    reuseItems: false
    highlightMoveDuration: 0
    add: Transition { NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 140 } }
    delegate: Item {
      id: row
      activeFocusOnTab: index===Math.max(0,area.ex.cur)
      Accessible.role: Accessible.ListItem
      Accessible.name: modelData.name
      Accessible.description: modelData.path
      Accessible.selectable: true
      Accessible.selected: sel
      Rectangle {anchors.fill:parent;color:"transparent";border.width:row.activeFocus ? 1 : 0;border.color:Theme.accent;z:2}
      Accessible.onPressAction: {var entry=modelData;area.ex.openEntry(entry)}
      onActiveFocusChanged: if(activeFocus) {area.ex.cur=index;area.ex.kbd=true;area.ensure(index)}
      required property var modelData
      required property int index
      width: listView.width; height: 34
      readonly property bool sel: area.ex.sel[modelData.path] === true
      readonly property bool isCur: area.ex.cur === index
      Rectangle { anchors.fill: parent; color: row.sel ? Theme.alpha(Theme.accent, 0.20) : (ma.containsMouse ? Theme.hover : (row.index % 2 ? Theme.alpha(Theme.fg, 0.018) : "transparent")) }
      Rectangle { visible: row.sel; width: 2; height: parent.height; color: Theme.accent }
      Rectangle { visible: row.isCur && area.ex.kbd; anchors.fill: parent; color: "transparent"; border.width: 1; border.color: Theme.alpha(Theme.accent, 0.7) }
      Thumb { x: 14; anchors.verticalCenter: parent.verticalCenter; width: 26; height: 26; entry: row.modelData; size: 26 }
      Label {
        x: 52; width: parent.width - 52 - (area.wDate + area.wSize + area.wKind + 16) - 8; height: parent.height
        text: row.modelData.name + (row.modelData.isLink ? "  " : "")
        color: row.modelData.hidden ? Theme.fgDim : (row.modelData.isDir ? Theme.fgBright : Theme.fg)
        font.bold: row.modelData.isDir && false
      }
      Label { visible: area.wDate > 0; x: parent.width - (area.wDate + area.wSize + area.wKind + 16); width: area.wDate; height: parent.height
        text: Fs.date(row.modelData.mtime); color: Theme.fgDim; font.pixelSize: Theme.fsSmall + 1 }
      Label { x: parent.width - (area.wSize + area.wKind + 16); width: area.wSize; height: parent.height
        text: row.modelData.isDir ? "—" : Fs.size(row.modelData.size); color: Theme.fgDim; font.pixelSize: Theme.fsSmall + 1; horizontalAlignment: Text.AlignRight }
      Label { visible: area.wKind > 0; x: parent.width - (area.wKind + 16) + 12; width: Math.max(0, area.wKind - 12); height: parent.height
        text: Fs.kindLabel(row.modelData); color: Theme.fgDim; font.pixelSize: Theme.fsSmall + 1 }
      MouseArea {
        id: ma; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.LeftButton | Qt.RightButton
        onPressed: (m) => { if (m.button === Qt.RightButton) { area.ex.rightClick(row.index); area.contextRequested(row.x + m.x, listView.y + row.y - listView.contentY + m.y, row.index) }
                            else area.ex.clickItem(row.index, m.modifiers) }
        onDoubleClicked: (m) => { if (m.button === Qt.LeftButton) area.ex.openEntry(row.modelData) }
      }
    }
  }
  ScrollBar_ { view: listView; visible: !area.grid && listView.contentHeight > listView.height }

  // ---- grid
  ListView {
    id: gridList
    visible: area.grid
    anchors { top: fhead.bottom; left: parent.left; right: parent.right; bottom: parent.bottom }
    clip: true
    model: area.grid ? area.rows : []
    boundsBehavior: Flickable.StopAtBounds
    topMargin: 6; bottomMargin: 14
    delegate: Item {
      id: gr
      function focusEntry(i) { var offset=modelData.idx ? modelData.idx.indexOf(i) : -1;var cell=offset<0 ? null : cellRepeater.itemAt(offset);if(cell) cell.forceActiveFocus() }
      required property var modelData
      required property int index
      readonly property bool isHdr: modelData.h !== undefined
      width: gridList.width
      height: isHdr ? 42 : area.th + 46 + area.gap
      Row {
        visible: gr.isHdr; x: area.pad; y: 14; spacing: 10
        Label { text: (gr.modelData.h || "").toUpperCase(); font.pixelSize: Theme.fsLabel; font.bold: true; font.letterSpacing: 1.6; color: Theme.accent; height: 16 }
        Label { text: gr.modelData.n + (gr.modelData.n === 1 ? " item" : " items"); font.pixelSize: Theme.fsLabel; color: Theme.fgDim; height: 16 }
      }
      Rectangle { visible: gr.isHdr; x: area.pad + 130; y: 22; width: parent.width - area.pad * 2 - 130; height: 1; color: Theme.line }
      Row {
        visible: !gr.isHdr
        x: area.pad; y: 0; spacing: area.gap
        Repeater {
          id: cellRepeater
          model: gr.modelData.idx || []
          delegate: Cell {
            id: cl
            activeFocusOnTab: modelData===Math.max(0,area.ex.cur)
            onActiveFocusChanged: if(activeFocus) {area.ex.cur=modelData;area.ex.kbd=true;area.ensure(modelData)}
            required property int modelData
            readonly property var ent: area.ex.shown[modelData]
            e: ent
            cw: area.cw; th: area.th
            sel: !!ent && area.ex.sel[ent.path] === true
            cur: area.ex.cur === modelData && area.ex.kbd
            onPressed: (mods, btn, mx, my) => {
              if (btn === Qt.RightButton) { area.ex.rightClick(modelData); var p = cl.mapToItem(area, mx, my); area.contextRequested(p.x, p.y, modelData) }
              else area.ex.clickItem(modelData, mods)
            }
            onToggled: area.ex.clickItem(modelData, Qt.ControlModifier)
            onActivated: area.ex.openEntry(ent)
          }
        }
      }
    }
  }
  ScrollBar_ { view: gridList; visible: area.grid && gridList.contentHeight > gridList.height }

  // Empty space right-click / click-to-deselect
  MouseArea {
    z: -1; anchors.fill: parent; acceptedButtons: Qt.LeftButton | Qt.RightButton
    onPressed: (m) => { if (m.button === Qt.RightButton) { area.ex.clearSel(); area.contextRequested(m.x, m.y, -1) } else area.ex.clearSel() }
  }

  // Empty state
  Column {
    visible: area.ex.shown.length === 0 && !area.ex.loading
    anchors.centerIn: parent; width: parent.width - 28; spacing: 10
    Ico { anchors.horizontalCenter: parent.horizontalCenter; text: area.ex.filter.length ? "" : ""; size: 34; color: Theme.muted }
    Label { width: parent.width; horizontalAlignment: Text.AlignHCenter; color: Theme.fgDim
      text: area.ex.errorText.length ? area.ex.errorText : (area.ex.filter.length ? "No matches for “" + area.ex.filter + "”" : "This folder is empty") }
  }
}

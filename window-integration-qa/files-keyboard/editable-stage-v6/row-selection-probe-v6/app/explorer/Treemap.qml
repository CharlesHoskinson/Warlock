import "file:///home/hoskinson/window-integration-qa/files-keyboard/editable-stage-v6/WindowAccessibilityV6"
import QtQuick
import qs.Commons
import qs.Ui

// Two-level squarified treemap of the home directory (du -d 2).
Item {
  id: root; objectName: "Treemap.root"
  property var usage: []
  property real total: 0
  property var hovered: null
  signal open(string path)
  signal ensureVisible(var item)

  function worst(row, side) {
    var s = 0, mx = 0, mn = 1e18
    for (var i = 0; i < row.length; i++) { s += row[i]; mx = Math.max(mx, row[i]); mn = Math.min(mn, row[i]) }
    return Math.max(side * side * mx / (s * s), (s * s) / (side * side * mn))
  }
  // vals sorted desc -> [{x,y,w,h,i}]
  function squarify(vals, x, y, w, h) {
    var sum = 0, i
    for (i = 0; i < vals.length; i++) sum += vals[i]
    var out = []
    if (sum <= 0 || w <= 0 || h <= 0) return out
    var k = w * h / sum, areas = vals.map(function (v) { return v * k })
    i = 0
    while (i < areas.length) {
      var side = Math.min(w, h), row = [], rs = 0, wr = 1e18, j = i
      while (j < areas.length) {
        var t = row.concat([areas[j]]), nw = worst(t, side)
        if (row.length && nw > wr) break
        row = t; rs += areas[j]; wr = nw; j++
      }
      if (w >= h) {
        var cw = rs / h, yy = y
        for (var a = 0; a < row.length; a++) { out.push({ x: x, y: yy, w: cw, h: row[a] / cw, i: i + a }); yy += row[a] / cw }
        x += cw; w -= cw
      } else {
        var rh = rs / w, xx = x
        for (var b = 0; b < row.length; b++) { out.push({ x: xx, y: y, w: row[b] / rh, h: rh, i: i + b }); xx += row[b] / rh }
        y += rh; h -= rh
      }
      i = j
    }
    return out
  }

  readonly property var tiles: {
    var res = []
    if (!usage || !usage.length || width < 20 || height < 20) return res
    var minShare = total * 0.004
    var tops = usage.filter(function (u) { return u.size >= minShare })
    var rects = squarify(tops.map(function (u) { return u.size }), 0, 0, width, height)
    for (var r = 0; r < rects.length; r++) {
      var rc = rects[r], u = tops[rc.i], col = Theme.palette[r % Theme.palette.length]
      var hdr = (rc.w > 70 && rc.h > 46) ? 20 : 0
      res.push({ level: 0, name: u.name, path: u.path, size: u.size, x: rc.x, y: rc.y, w: rc.w, h: rc.h, color: col, hdr: hdr })
      var kids = (u.children || []).filter(function (c) { return c.size >= u.size * 0.03 })
      if (hdr && kids.length) {
        var inner = squarify(kids.map(function (c) { return c.size }), rc.x + 3, rc.y + hdr, rc.w - 6, rc.h - hdr - 3)
        for (var q = 0; q < inner.length; q++) {
          var ic = inner[q], c = kids[ic.i]
          res.push({ level: 1, name: c.name, path: c.path, size: c.size, x: ic.x, y: ic.y, w: ic.w, h: ic.h, color: col, hdr: 0, parentName: u.name })
        }
      }
    }
    return res
  }

  Repeater {
    model: root.tiles
    delegate: Rectangle {
      id: t; objectName: "Treemap.t"
      readonly property string actionIdentity:"storage:"+modelData.path
      activeFocusOnTab:true
      Accessible.role:Accessible.Button
      Accessible.name:modelData.name
      Accessible.description:modelData.path + ", " + Fs.size(modelData.size)
      Accessible.onPressAction:{if(!ActionState.allowed(t))return;var path=modelData.path;root.open(path)}
      onActiveFocusChanged:if(activeFocus){root.hovered=modelData;root.ensureVisible(t)}
      Keys.onPressed:(e)=>{if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space){if(!e.isAutoRepeat)root.open(modelData.path);e.accepted=true}}
      required property var modelData
      readonly property bool hot: root.hovered === modelData
      x: Math.round(modelData.x) + (modelData.level === 0 ? 0 : 0)
      y: Math.round(modelData.y)
      width: Math.max(1, Math.round(modelData.w) - 1)
      height: Math.max(1, Math.round(modelData.h) - 1)
      z: modelData.level
      color: modelData.level === 0 ? Theme.alpha(modelData.color, hot ? 0.24 : 0.13)
                                   : Theme.alpha(modelData.color, hot ? 0.55 : 0.30)
      border.width:activeFocus ? 2 : (modelData.level === 0 ? 1 : 0)
      border.color: Theme.alpha(modelData.color, hot ? 0.9 : 0.5)
      Behavior on color { ColorAnimation { duration: Theme.dFast } }
      Label {
        visible: modelData.level === 0 ? modelData.hdr > 0 : (modelData.w > 62 && modelData.h > 30)
        x: modelData.level === 0 ? 6 : 5; y: modelData.level === 0 ? 2 : 3
        width: parent.width - 10; height: modelData.level === 0 ? 16 : 14
        text: modelData.level === 0 ? modelData.name + "  " + Fs.size(modelData.size) : modelData.name
        font.pixelSize: modelData.level === 0 ? Theme.fsSmall + 1 : Theme.fsLabel + 1
        font.bold: modelData.level === 0
        color: modelData.level === 0 ? Theme.fgBright : Theme.alpha(Theme.fgBright, 0.85)
      }
      Label {
        visible: modelData.level === 1 && modelData.w > 62 && modelData.h > 46
        x: 5; y: 17; width: parent.width - 10; height: 12
        text: Fs.size(modelData.size); font.pixelSize: Theme.fsLabel; color: Theme.alpha(Theme.fgBright, 0.55)
      }
      MouseArea {
        anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
        onEntered: root.hovered = t.modelData
        onExited: if (root.hovered === t.modelData) root.hovered = null
        onClicked: root.open(t.modelData.path)
      }
    }
  }
}

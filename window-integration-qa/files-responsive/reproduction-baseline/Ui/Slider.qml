import QtQuick
import qs.Commons

// Minimal flat horizontal slider (grid zoom). Square diamond knob, accent fill.
Item {
  id: root
  property real from: 0
  property real to: 1
  property real value: 0
  signal moved(real v)
  implicitWidth: 120; implicitHeight: 24
  readonly property real frac: (value - from) / (to - from)

  Rectangle { anchors.verticalCenter: parent.verticalCenter; width: parent.width; height: 2; color: Theme.alpha(Theme.fg, 0.2); radius: Theme.radius
    Rectangle { width: parent.width * root.frac; height: parent.height; color: Theme.accent } }
  Rectangle {
    id: knob
    width: 10; height: 10
    rotation: 45
    x: root.frac * (root.width - width); anchors.verticalCenter: parent.verticalCenter
    color: ma.pressed || ma.containsMouse ? Theme.fgBright : Theme.accent
    scale: ma.pressed ? 1.25 : 1
    Behavior on scale { NumberAnimation { duration: 100 } }
  }
  MouseArea {
    id: ma
    anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
    function upd(mx) { var f = Math.max(0, Math.min(1, (mx - knob.width / 2) / (root.width - knob.width))); root.moved(root.from + f * (root.to - root.from)) }
    onPressed: (m) => upd(m.x)
    onPositionChanged: (m) => { if (pressed) upd(m.x) }
  }
}

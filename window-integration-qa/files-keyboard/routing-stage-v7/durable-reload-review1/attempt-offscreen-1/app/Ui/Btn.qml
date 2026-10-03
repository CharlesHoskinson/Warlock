import QtQuick
import qs.Commons

// Square, flat icon/text button in the Omarchy control idiom: 1px hairline,
// fill on hover, accent when active.
Item {
  id: root
  property string icon: ""
  property string text: ""
  property bool active: false
  property bool enabled2: true
  property bool bordered: true
  property color tint: "transparent"
  property bool primary: false
  readonly property bool tinted: tint.a > 0
  property string tip: ""
  signal clicked(var mouse)
  implicitWidth: text.length ? caption.implicitWidth + (icon.length ? 19 : 0) + 20 : 30
  implicitHeight: 30
  opacity: enabled2 ? 1 : 0.35

  Rectangle {
    anchors.fill: parent
    radius: Theme.radius
    color: root.primary ? (ma.containsMouse ? Theme.fgBright : Theme.accent) : (root.active ? Theme.alpha(Theme.accent, 0.16) : (ma.containsMouse && root.enabled2 ? (root.tinted ? Theme.alpha(root.tint, 0.14) : Theme.hover) : "transparent"))
    border.width: root.bordered ? 1 : 0
    border.color: root.primary ? Theme.accent : (root.active ? Theme.accent : (root.tinted ? Theme.alpha(root.tint, ma.containsMouse ? 0.9 : 0.5) : (ma.containsMouse ? Theme.lineStrong : Theme.line)))
    Behavior on color { ColorAnimation { duration: Theme.dFast } }
    Behavior on border.color { ColorAnimation { duration: Theme.dFast } }
  }
  Row {
    id: row
    anchors.centerIn: parent
    width: Math.max(0, Math.min(caption.implicitWidth + (root.icon.length ? 19 : 0), root.width - 20))
    spacing: 6
    Ico { visible: root.icon.length; text: root.icon; size: 13; color: root.primary ? Theme.bg : (root.active ? Theme.accent : (root.tinted ? root.tint : Theme.fg)); anchors.verticalCenter: parent.verticalCenter }
    Label { id: caption; visible: root.text.length; width: Math.max(0, row.width - (root.icon.length ? 19 : 0)); text: root.text; font.bold: root.primary; color: root.primary ? Theme.bg : (root.active ? Theme.accent : (root.tinted ? root.tint : Theme.fg)); anchors.verticalCenter: parent.verticalCenter }
  }
  MouseArea {
    id: ma
    anchors.fill: parent
    hoverEnabled: true
    cursorShape: Qt.PointingHandCursor
    onClicked: (m) => { if (root.enabled2) root.clicked(m) }
  }
}

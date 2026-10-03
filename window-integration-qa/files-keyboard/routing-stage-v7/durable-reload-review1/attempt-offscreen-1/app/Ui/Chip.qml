import QtQuick
import qs.Commons

Item {
  id: root
  property string text: ""
  property string icon: ""
  property bool active: false
  signal clicked()
  implicitWidth: r.implicitWidth + 22
  implicitHeight: 26
  Rectangle {
    anchors.fill: parent
    radius: Theme.radius
    color: root.active ? Theme.accent : (ma.containsMouse ? Theme.hover : "transparent")
    border.width: 1
    border.color: root.active ? Theme.accent : Theme.line
    Behavior on color { ColorAnimation { duration: Theme.dFast } }
  }
  Row {
    id: r
    anchors.centerIn: parent
    spacing: 6
    Ico { visible: root.icon.length; text: root.icon; size: 11; color: root.active ? Theme.bg : Theme.fgDim; anchors.verticalCenter: parent.verticalCenter }
    Label { text: root.text; font.pixelSize: Theme.fsSmall + 1; color: root.active ? Theme.bg : Theme.fg; font.bold: root.active; anchors.verticalCenter: parent.verticalCenter }
  }
  MouseArea { id: ma; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.clicked() }
}

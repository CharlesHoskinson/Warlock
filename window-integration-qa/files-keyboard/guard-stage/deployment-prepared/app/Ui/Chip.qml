import "file:///home/hoskinson/.local/share/omarchy-files-native/WindowAccessibilityV5_guard_20261001"
import QtQuick
import qs.Commons

Item {
  id: root
  property string text: ""
  property string icon: ""
  property bool active: false
  activeFocusOnTab: true
  readonly property string actionIdentity: "chip:"+text
  Accessible.role: Accessible.Button
  Accessible.name: text
  Accessible.checkable: true
  Accessible.checked: active
  Accessible.focused: activeFocus
  Accessible.onPressAction: if(ActionState.allowed(root)) clicked()
  Keys.onPressed: (e) => { if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space) { if(!e.isAutoRepeat && ActionState.allowed(root)) clicked(); e.accepted=true } }
  signal clicked()
  implicitWidth: r.implicitWidth + 22
  implicitHeight: 26
  Rectangle {
    anchors.fill: parent
    radius: Theme.radius
    color: root.active ? Theme.accent : (ma.containsMouse ? Theme.hover : "transparent")
    border.width: root.activeFocus ? 2 : 1
    border.color: root.activeFocus || root.active ? Theme.accent : Theme.line
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

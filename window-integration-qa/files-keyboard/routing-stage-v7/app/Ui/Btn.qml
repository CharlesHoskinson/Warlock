import "file:///home/hoskinson/window-integration-qa/files-keyboard/routing-stage-v7/WindowAccessibilityV6"
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
  property string accessibleName: text.length ? text : tip
  readonly property string actionIdentity: "control:"+accessibleName
  property bool keyboardPressed: false
  enabled: enabled2
  activeFocusOnTab: true
  Accessible.role: Accessible.Button
  Accessible.name: accessibleName
  Accessible.focusable: enabled2
  Accessible.focused: activeFocus
  Accessible.pressed: ma.pressed || keyboardPressed
  Accessible.onPressAction: activate()
  function activate() { if (enabled2 && ActionState.allowed(root)) clicked({button:Qt.LeftButton,modifiers:Qt.NoModifier,x:width/2,y:height/2}) }
  Keys.onPressed: (e) => {
    if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) { if (!e.isAutoRepeat) activate(); e.accepted=true }
    else if (e.key === Qt.Key_Space) { keyboardPressed=true; e.accepted=true }
  }
  Keys.onReleased: (e) => { if (e.key === Qt.Key_Space) { if (keyboardPressed && !e.isAutoRepeat) { keyboardPressed=false; activate() }; e.accepted=true } }
  onActiveFocusChanged: if (!activeFocus) keyboardPressed=false
  signal clicked(var mouse)
  implicitWidth: text.length ? caption.implicitWidth + (icon.length ? 19 : 0) + 20 : 30
  implicitHeight: 30
  opacity: enabled2 ? 1 : 0.35

  Rectangle {
    anchors.fill: parent
    radius: Theme.radius
    color: root.primary ? (ma.containsMouse ? Theme.fgBright : Theme.accent) : (root.active ? Theme.alpha(Theme.accent, 0.16) : (ma.containsMouse && root.enabled2 ? (root.tinted ? Theme.alpha(root.tint, 0.14) : Theme.hover) : "transparent"))
    border.width: root.activeFocus ? 2 : (root.bordered ? 1 : 0)
    border.color: root.activeFocus ? Theme.accent : root.primary ? Theme.accent : (root.active ? Theme.accent : (root.tinted ? Theme.alpha(root.tint, ma.containsMouse ? 0.9 : 0.5) : (ma.containsMouse ? Theme.lineStrong : Theme.line)))
    Behavior on color { ColorAnimation { duration: Theme.dFast } }
    Behavior on border.color { ColorAnimation { duration: Theme.dFast } }
  }
  Row {
    id: row
    anchors.centerIn: parent
    width: Math.max(0, Math.min(caption.implicitWidth + (root.icon.length ? 19 : 0), root.width - 20))
    spacing: 6
    Ico { Accessible.ignored:true; visible: root.icon.length; text: root.icon; size: 13; color: root.primary ? Theme.bg : (root.active ? Theme.accent : (root.tinted ? root.tint : Theme.fg)); anchors.verticalCenter: parent.verticalCenter }
    Label { id: caption; Accessible.ignored:true; visible: root.text.length; width: Math.max(0, row.width - (root.icon.length ? 19 : 0)); text: root.text; font.bold: root.primary; color: root.primary ? Theme.bg : (root.active ? Theme.accent : (root.tinted ? root.tint : Theme.fg)); anchors.verticalCenter: parent.verticalCenter }
  }
  MouseArea {
    id: ma
    anchors.fill: parent
    hoverEnabled: true
    cursorShape: Qt.PointingHandCursor
    onPressed: root.forceActiveFocus()
    onClicked: (m) => { if (root.enabled2) root.clicked(m) }
  }
}

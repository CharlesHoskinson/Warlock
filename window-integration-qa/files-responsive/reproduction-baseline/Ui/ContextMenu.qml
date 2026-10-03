import QtQuick
import qs.Commons

// Square popup menu. items: [{label, icon, action:"id", danger, sep, disabled}]
Item {
  id: root
  property var items: []
  property real px: 0
  property real py: 0
  signal chosen(string action)
  visible: false
  anchors.fill: parent
  z: 100

  function openAt(x, y, its) {
    items = its; px = x; py = y; visible = true; hi = -1
    card.forceActiveFocus()
  }
  function close() { visible = false }
  property int hi: -1

  MouseArea { anchors.fill: parent; acceptedButtons: Qt.AllButtons; onPressed: root.close() }

  Rectangle {
    id: card
    x: Math.max(4, Math.min(root.px, root.width - width - 4))
    y: Math.max(4, Math.min(root.py, root.height - height - 4))
    width: 232
    height: col.implicitHeight + 8
    color: Theme.bg
    border.color: Theme.accent
    border.width: 1
    radius: Theme.radius
    focus: root.visible
    Keys.onPressed: (e) => {
      if (e.key === Qt.Key_Escape) { root.close(); e.accepted = true }
      else if (e.key === Qt.Key_Down || e.key === Qt.Key_Up) {
        var d = e.key === Qt.Key_Down ? 1 : -1, n = root.items.length, i = root.hi
        for (var k = 0; k < n; k++) { i = (i + d + n) % n; if (!root.items[i].sep && !root.items[i].disabled) break }
        root.hi = i; e.accepted = true
      } else if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) {
        if (root.hi >= 0) { root.close(); root.chosen(root.items[root.hi].action) }
        e.accepted = true
      }
    }
    Column {
      id: col
      x: 4; y: 4; width: parent.width - 8
      Repeater {
        model: root.items
        delegate: Item {
          required property var modelData
          required property int index
          width: col.width
          height: (!!modelData.sep) ? 9 : 28
          Rectangle { visible: !!(!!modelData.sep); anchors.centerIn: parent; width: parent.width - 12; height: 1; color: Theme.line }
          Rectangle {
            visible: !(!!modelData.sep)
            anchors.fill: parent
            color: (ma.containsMouse || root.hi === index) && !(!!modelData.disabled) ? Theme.alpha(Theme.accent, 0.16) : "transparent"
          }
          Row {
            visible: !(!!modelData.sep)
            anchors.verticalCenter: parent.verticalCenter
            x: 10; spacing: 10
            opacity: (!!modelData.disabled) ? 0.35 : 1
            Ico { width: 16; text: modelData.icon || ""; size: 12; color: (!!modelData.danger) ? Theme.red : Theme.fgDim; anchors.verticalCenter: parent.verticalCenter }
            Label { text: modelData.label || ""; color: (!!modelData.danger) ? Theme.red : Theme.fgBright; anchors.verticalCenter: parent.verticalCenter }
          }
          Label {
            visible: !(!!modelData.sep) && !!modelData.hint
            anchors { right: parent.right; rightMargin: 10; verticalCenter: parent.verticalCenter }
            text: modelData.hint || ""; color: Theme.fgDim; font.pixelSize: Theme.fsSmall
          }
          MouseArea {
            id: ma; anchors.fill: parent; hoverEnabled: true; enabled: !(!!modelData.sep) && !(!!modelData.disabled)
            onEntered: root.hi = index
            onClicked: { root.close(); root.chosen(modelData.action) }
          }
        }
      }
    }
  }
}

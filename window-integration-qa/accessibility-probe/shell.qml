import QtQuick
import "../../.local/share/hypr-window-controls/qml/WindowAccessibility"
import Quickshell
ShellRoot {
  FloatingWindow {
    title: "Accessibility probe"
    implicitWidth: 160
    implicitHeight: 80
    Rectangle {
      anchors.fill: parent
      color: "#24283b"
      Accessible.role: Accessible.Button
      Accessible.name: "Probe action"
      Accessible.onPressAction: console.log("Probe action invoked")
      Text { anchors.centerIn: parent; text: "Probe action"; color: "white" }
    }
  }
}

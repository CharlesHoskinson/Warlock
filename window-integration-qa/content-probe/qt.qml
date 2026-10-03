import QtQuick
import Quickshell
ShellRoot {
    FloatingWindow {
        title: "Content repaint QA Qt"
        implicitWidth: 600
        implicitHeight: 350
        color: "#162033"
        Repeater {
            model: 16
            Rectangle {
                required property int index
                width: parent.width / 16 + 1
                height: parent.height
                x: index * parent.width / 16
                color: Qt.hsla((index / 16 + dot.x / Math.max(1, dot.parent.width)) % 1, .75, .45, 1)
            }
        }
        Rectangle {
            id: dot
            y: 40
            width: 25
            height: 100
            color: "white"
            NumberAnimation on x { from: 20; to: Math.max(20, dot.parent.width - 30); duration: 1200; loops: Animation.Infinite }
        }
    }
}

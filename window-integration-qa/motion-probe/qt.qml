import QtQuick
import Quickshell
ShellRoot {
    FloatingWindow {
        title: "Motion QA Qt"
        implicitWidth: 600
        implicitHeight: 350
        color: "#24283b"
        Text {
            anchors.centerIn: parent
            text: "Disposable motion measurement window"
            color: "white"
        }
    }
}

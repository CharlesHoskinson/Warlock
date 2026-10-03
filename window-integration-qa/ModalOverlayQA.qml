import QtQuick
import Quickshell
import Quickshell.Wayland
import Quickshell.Io

Scope {
    id: root
    property int clicks: 0
    property bool shown: false
    PanelWindow {
        visible: root.shown
        screen: {
            for (const candidate of Quickshell.screens)
                if (candidate.name === "DRAG-QA") return candidate;
            return Quickshell.screens[0];
        }
        anchors { left: true; top: true }
        margins { left: 120; top: 500 }
        implicitWidth: 200
        implicitHeight: 100
        exclusionMode: ExclusionMode.Ignore
        WlrLayershell.namespace: "modal-overlay-qa"
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
        color: "#303040"
        MouseArea { anchors.fill: parent; onClicked: root.clicks++ }
    }
    IpcHandler {
        target: "modalOverlayQA"
        function openPanel(): void { root.shown = true }
        function closePanel(): void { root.shown = false }
        function count(): string { return String(root.clicks) }
    }
}

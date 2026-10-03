import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Hyprland
import Quickshell.Wayland
import qs.Commons

Item {
  id: root
  property var shell: null
  property var manifest: null
  property bool opened: false
  property var desktops: []
  property string activeId: "1"
  property string moveAddress: ""
  property bool moveMenuOpen: false
  readonly property string homeDir: Quickshell.env("HOME")
  readonly property var focusedScreen: {
    var name = Hyprland.focusedMonitor ? String(Hyprland.focusedMonitor.name || "") : ""
    for (var i = 0; i < Quickshell.screens.length; i++)
      if (Quickshell.screens[i].name === name) return Quickshell.screens[i]
    return Quickshell.screens.length ? Quickshell.screens[0] : null
  }
  readonly property var activeDesktop: {
    for (var i = 0; i < desktops.length; i++) if (desktops[i].id === activeId) return desktops[i]
    return desktops.length ? desktops[0] : null
  }

  function refresh() {
    if (!listProcess.running) listProcess.running = true
  }
  function applyList(raw) {
    try {
      var result = JSON.parse(raw)
      desktops = result.desktops || []
      activeId = String(result.active || "1")
    } catch (e) { console.warn("Task View: invalid desktop list: " + e) }
  }
  function action(args) {
    var command = [homeDir + "/.local/bin/hypr-desktops"].concat(args)
    Quickshell.execDetached(command)
    refreshLater.restart()
  }
  function open() {
    opened = true
    refresh()
    Qt.callLater(function() { keyCatcher.forceActiveFocus() })
  }
  function close() { opened = false; moveMenuOpen = false }
  function toggle() { if (opened) close(); else open() }
  function dismiss() {
    close()
    if (shell && typeof shell.hide === "function") shell.hide("hoskinson.taskview")
  }
  function focusWindow(address) {
    if (!/^0x[0-9a-fA-F]+$/.test(address)) return
    Quickshell.execDetached([homeDir + "/.local/bin/hypr-windowctl", "restore", address])
    dismiss()
  }
  function closeWindow(address) {
    if (!/^0x[0-9a-fA-F]+$/.test(address)) return
    Quickshell.execDetached(["hyprctl", "dispatch", "hl.dsp.window.close({ window = \"address:" + address + "\" })"])
    refreshLater.restart()
  }

  Process {
    id: listProcess
    command: [root.homeDir + "/.local/bin/hypr-desktops", "list"]
    stdout: StdioCollector { waitForEnd: true; onStreamFinished: root.applyList(text) }
  }
  Timer { id: refreshLater; interval: 320; onTriggered: root.refresh() }
  Timer { interval: 1200; repeat: true; running: root.opened; onTriggered: root.refresh() }

  IpcHandler {
    target: "hoskinson.taskview"
    function open(): void { root.open() }
    function close(): void { root.dismiss() }
    function toggle(): void { root.toggle() }
  }

  PanelWindow {
    id: panel
    visible: root.opened && !!root.focusedScreen
    screen: root.focusedScreen
    anchors { top: true; bottom: true; left: true; right: true }
    color: "transparent"
    WlrLayershell.namespace: "hoskinson-taskview"
    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive
    exclusionMode: ExclusionMode.Ignore

    Rectangle { anchors.fill: parent; color: Color.menu.scrim }
    MouseArea { anchors.fill: parent; onClicked: root.dismiss() }

    Rectangle {
      id: card
      width: Math.min(1100, panel.width - 64)
      height: Math.min(740, panel.height - 72)
      anchors.centerIn: parent
      radius: 12
      color: Color.menu.background
      border.color: Color.menu.border
      border.width: 1
      MouseArea { anchors.fill: parent; onClicked: {} }

      Item {
        id: keyCatcher
        anchors.fill: parent
        focus: true
        Keys.onPressed: function(event) {
          if (event.key === Qt.Key_Escape) {
            if (root.moveMenuOpen) root.moveMenuOpen = false
            else root.dismiss()
            event.accepted = true
          }
        }

        Text {
          id: heading
          x: 22; y: 18
          text: "Task view"
          color: Color.menu.text
          font.pixelSize: 23
          font.bold: true
        }

        Rectangle {
          id: newDesktop
          width: 138; height: 32
          anchors.right: parent.right
          anchors.rightMargin: 22
          y: 17
          radius: 6
          color: newMouse.containsMouse ? Color.accent : Color.menu.border
          Text { anchors.centerIn: parent; text: "+ New desktop"; color: Color.menu.background; font.pixelSize: 12 }
          MouseArea { id: newMouse; anchors.fill: parent; hoverEnabled: true; onClicked: { root.action(["new"]); root.dismiss() } }
        }

        Text {
          x: 22; y: 66
          text: root.activeDesktop ? root.activeDesktop.name + " · " + root.activeDesktop.windows.length + " windows" : "Windows"
          color: Color.menu.text
          font.pixelSize: 13
        }

        Flickable {
          id: windowScroll
          x: 22; y: 94
          width: parent.width - 44
          height: parent.height - 274
          contentHeight: windowFlow.implicitHeight
          clip: true
          boundsBehavior: Flickable.StopAtBounds

          Flow {
            id: windowFlow
            width: windowScroll.width
            spacing: 12
            Repeater {
              model: root.activeDesktop ? root.activeDesktop.windows : []
              Rectangle {
                id: windowCard
                required property var modelData
                width: Math.max(185, Math.floor((windowFlow.width - 36) / 4))
                height: 174
                radius: 7
                color: windowMouse.containsMouse ? Color.menu.selectedBackground : Color.menu.background
                border.color: Color.menu.border
                border.width: 1

                Image {
                  x: 8; y: 8; width: parent.width - 16; height: 132
                  source: windowCard.modelData.preview ? "file://" + windowCard.modelData.preview : ""
                  cache: false; asynchronous: true
                  fillMode: Image.PreserveAspectFit
                  Text {
                    anchors.centerIn: parent
                    visible: parent.status !== Image.Ready
                    text: windowCard.modelData.class || "Window"
                    color: Color.menu.text
                    font.pixelSize: 14
                  }
                }
                Text {
                  x: 9; y: 145; width: parent.width - 45
                  text: windowCard.modelData.title || windowCard.modelData.class || "Window"
                  color: Color.menu.text; font.pixelSize: 12
                  elide: Text.ElideRight
                }
                MouseArea {
                  id: windowMouse
                  anchors.fill: parent; hoverEnabled: true
                  acceptedButtons: Qt.LeftButton | Qt.RightButton
                  onClicked: function(mouse) {
                    if (mouse.button === Qt.RightButton) {
                      root.moveAddress = windowCard.modelData.address
                      root.moveMenuOpen = true
                    } else root.focusWindow(windowCard.modelData.address)
                  }
                }
                Rectangle {
                  width: 22; height: 22; radius: 11
                  anchors.right: parent.right; anchors.rightMargin: 5; y: 5
                  color: Color.menu.border
                  Text { anchors.centerIn: parent; text: "×"; color: Color.menu.background; font.pixelSize: 14 }
                  MouseArea { anchors.fill: parent; onClicked: root.closeWindow(windowCard.modelData.address) }
                }
              }
            }
          }
        }

        Text {
          x: 22; y: parent.height - 167
          text: "Desktops · double-click a name to rename · right-click a window to move it"
          color: Color.menu.text; opacity: 0.75; font.pixelSize: 12
        }
        Flickable {
          id: desktopScroll
          x: 22; y: parent.height - 143
          width: parent.width - 44; height: 115
          contentWidth: desktopRow.implicitWidth
          clip: true; interactive: contentWidth > width
          Row {
            id: desktopRow
            spacing: 10
            Repeater {
              model: root.desktops
              Rectangle {
                id: desktopCard
                required property var modelData
                required property int index
                property bool editing: false
                width: 170; height: 99; radius: 6
                color: modelData.active ? Color.menu.selectedBackground : Color.menu.background
                border.color: modelData.active ? Color.accent : Color.menu.border
                border.width: modelData.active ? 2 : 1

                Text {
                  x: 12; y: 15; width: parent.width - 36
                  visible: !desktopCard.editing
                  text: desktopCard.modelData.name
                  color: Color.menu.text; font.bold: desktopCard.modelData.active
                  elide: Text.ElideRight; font.pixelSize: 13
                }
                TextInput {
                  id: renameField
                  x: 12; y: 15; width: parent.width - 36
                  visible: desktopCard.editing
                  text: desktopCard.modelData.name
                  color: Color.menu.text; selectByMouse: true
                  onAccepted: {
                    root.action(["rename", desktopCard.modelData.id, text])
                    desktopCard.editing = false
                  }
                  Keys.onEscapePressed: desktopCard.editing = false
                }
                Text {
                  x: 12; y: 51
                  text: desktopCard.modelData.windows.length + " windows"
                  color: Color.menu.text; opacity: 0.7; font.pixelSize: 11
                }
                Text {
                  x: 12; y: 73
                  z: 2
                  visible: desktopCard.index > 0
                  text: "◀"; color: Color.menu.text; font.pixelSize: 12
                  MouseArea {
                    anchors.fill: parent
                    onClicked: root.action(["reorder", desktopCard.modelData.id, root.desktops[desktopCard.index - 1].id])
                  }
                }
                Text {
                  x: 35; y: 73
                  z: 2
                  visible: desktopCard.index < root.desktops.length - 1
                  text: "▶"; color: Color.menu.text; font.pixelSize: 12
                  MouseArea {
                    anchors.fill: parent
                    onClicked: root.action(["reorder", root.desktops[desktopCard.index + 1].id, desktopCard.modelData.id])
                  }
                }
                MouseArea {
                  anchors.fill: parent
                  acceptedButtons: Qt.LeftButton
                  onClicked: { root.action(["switch", desktopCard.modelData.id]); root.dismiss() }
                  onDoubleClicked: {
                    desktopCard.editing = true
                    renameField.selectAll()
                    renameField.forceActiveFocus()
                  }
                }
                Rectangle {
                  visible: root.desktops.length > 1
                  width: 21; height: 21; radius: 11
                  anchors.right: parent.right; anchors.rightMargin: 4; y: 4
                  color: Color.menu.border
                  Text { anchors.centerIn: parent; text: "×"; color: Color.menu.background; font.pixelSize: 13 }
                  MouseArea { anchors.fill: parent; onClicked: root.action(["close", desktopCard.modelData.id]) }
                }
              }
            }
          }
        }

        Rectangle {
          visible: root.moveMenuOpen
          anchors.centerIn: parent
          width: 300; height: Math.min(310, 68 + root.desktops.length * 36)
          radius: 8; color: Color.menu.background
          border.color: Color.accent; border.width: 1
          z: 10
          Column {
            anchors.fill: parent; anchors.margins: 12; spacing: 7
            Text { text: "Move window to desktop"; color: Color.menu.text; font.pixelSize: 14; font.bold: true }
            Repeater {
              model: root.desktops
              Rectangle {
                required property var modelData
                width: 276; height: 29; radius: 4
                color: menuMouse.containsMouse ? Color.menu.selectedBackground : Color.menu.background
                Text { x: 8; anchors.verticalCenter: parent.verticalCenter; text: modelData.name; color: Color.menu.text; font.pixelSize: 12 }
                MouseArea {
                  id: menuMouse; anchors.fill: parent; hoverEnabled: true
                  onClicked: {
                    root.action(["move", root.moveAddress, modelData.id])
                    root.moveMenuOpen = false
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "hoskinson.windows"

  property var windows: []
  property string signature: ""
  property string focusedAddress: ""
  property string captureAddress: ""
  property int previewRevision: 0
  property var previewWindow: null
  property var previewAnchor: null
  property bool previewOpen: false
  readonly property int buttonWidth: 38
  readonly property int maxWidth: 460
  readonly property string previewDir: (Quickshell.env("XDG_RUNTIME_DIR") || homeDir + "/.cache") + "/hypr-window-previews"

  function iconName(w) {
    var appClass = String(w.class || "")
    if (appClass === "org.quickshell" && w.title === "Files") return "system-file-manager"
    var apps = DesktopEntries.applications.values || []
    for (var i = 0; i < apps.length; i++) {
      var entry = apps[i]
      if (String(entry.id || "").toLowerCase() === appClass.toLowerCase()) return String(entry.icon || appClass)
    }
    return appClass || "application-x-executable"
  }

  function iconSource(w) {
    var name = iconName(w)
    return bar && bar.shell && bar.shell.appLibrary
      ? bar.shell.appLibrary.iconSource(name)
      : Quickshell.iconPath(name, true)
  }

  function showPreview(w, anchor) {
    previewWindow = w
    previewAnchor = anchor
    previewOpen = true
    previewClose.stop()
    if (bar) bar.hideTooltip(anchor)
  }

  function hidePreviewSoon() { previewClose.restart() }

  function refresh() {
    if (!clientProcess.running) clientProcess.running = true
  }

  function updateWindows(output) {
    try {
      var all = JSON.parse(output)
      var visible = all.filter(function(w) {
        var ws = w.workspace && w.workspace.name || ""
        return w.mapped && (/^[0-9]+$/.test(ws) || ws === "special:win-minimized")
      })
      visible.sort(function(a, b) {
        if (a.workspace.name === "special:win-minimized" && b.workspace.name !== "special:win-minimized") return 1
        if (b.workspace.name === "special:win-minimized" && a.workspace.name !== "special:win-minimized") return -1
        return a.focusHistoryID - b.focusHistoryID
      })
      var next = JSON.stringify(visible.map(function(w) { return [w.address, w.title, w.focusHistoryID, w.workspace.name] }))
      if (next !== root.signature) {
        root.signature = next
        root.windows = visible
      }
      var focused = ""
      for (var j = 0; j < visible.length; j++) {
        if (visible[j].focusHistoryID === 0 && visible[j].workspace.name !== "special:win-minimized") {
          focused = visible[j].address
          break
        }
      }
      if (focused && focused !== root.focusedAddress) {
        root.focusedAddress = focused
        root.captureAddress = focused
        captureDelay.restart()
      }
    } catch (e) {
      console.warn("Windows widget: invalid Hyprland window list: " + e)
    }
  }

  implicitWidth: Math.min(maxWidth, row.implicitWidth)
  implicitHeight: barSize

  Process {
    id: clientProcess
    command: ["hyprctl", "clients", "-j"]
    stdout: StdioCollector { waitForEnd: true; onStreamFinished: root.updateWindows(text) }
  }

  Process {
    id: captureProcess
    command: [root.homeDir + "/.local/bin/hypr-window-preview", "capture", root.captureAddress]
    onExited: root.previewRevision++
  }

  Timer {
    id: captureDelay
    interval: 450
    onTriggered: if (!captureProcess.running && root.captureAddress) captureProcess.running = true
  }

  Timer {
    id: previewClose
    interval: 250
    onTriggered: if (!previewCard.containsMouse) root.previewOpen = false
  }

  Timer {
    interval: 650
    repeat: true
    running: true
    triggeredOnStart: true
    onTriggered: root.refresh()
  }

  Flickable {
    anchors.fill: parent
    contentWidth: row.implicitWidth
    contentHeight: height
    clip: true
    interactive: contentWidth > width
    boundsBehavior: Flickable.StopAtBounds

    Row {
      id: row
      spacing: 3
      height: root.barSize

      Repeater {
        model: root.windows

        Item {
          required property var modelData
          readonly property bool minimized: modelData.workspace.name === "special:win-minimized"
          readonly property bool active: modelData.focusHistoryID === 0 && !minimized
          width: root.buttonWidth
          height: root.barSize

          WidgetButton {
            anchors.fill: parent
            bar: root.bar
            text: " "
            labelVisible: false
            fixedWidth: root.buttonWidth
            fixedHeight: root.barSize
            opacity: minimized ? 0.55 : 1
            onPressed: function(button) {
              if (!root.bar) return
              var address = String(modelData.address || "")
              if (!/^0x[0-9a-fA-F]+$/.test(address)) return
              root.bar.run(root.homeDir + "/.local/bin/hypr-windowctl " + (active && button === Qt.LeftButton ? "minimize " : "restore ") + address)
            }
          }

          Image {
            id: appIcon
            width: 19
            height: 19
            anchors.centerIn: parent
            source: root.iconSource(modelData)
            sourceSize.width: width * Screen.devicePixelRatio
            sourceSize.height: height * Screen.devicePixelRatio
            fillMode: Image.PreserveAspectFit
            asynchronous: true
          }

          Text {
            anchors.centerIn: parent
            visible: appIcon.status !== Image.Ready
            text: (modelData.class || "?").substring(0, 1).toUpperCase()
            color: root.bar ? root.bar.barForeground : Color.foreground
            font.pixelSize: 13
          }

          HoverHandler {
            onHoveredChanged: {
              if (hovered) root.showPreview(modelData, parent)
              else root.hidePreviewSoon()
            }
          }

          Rectangle {
            width: parent.width - 12
            height: 2
            radius: 1
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            color: Color.accent
            opacity: active ? 1 : (minimized ? 0.15 : 0.45)
          }
        }
      }
    }
  }

  PopupCard {
    id: previewCard
    anchorItem: root.previewAnchor
    bar: root.bar
    triggerMode: "hover"
    open: root.previewOpen && root.previewWindow !== null
    contentWidth: 300
    contentHeight: 225
    onContainsMouseChanged: if (containsMouse) previewClose.stop(); else if (root.previewOpen) root.hidePreviewSoon()

    Column {
      width: 300
      spacing: 7

      Text {
        width: parent.width
        text: root.previewWindow ? (root.previewWindow.title || root.previewWindow.class || "Window") : ""
        color: Color.foreground
        font.pixelSize: 12
        elide: Text.ElideRight
        textFormat: Text.PlainText
      }

      Image {
        width: parent.width
        height: 180
        fillMode: Image.PreserveAspectFit
        source: root.previewWindow ? "file://" + root.previewDir + "/" + root.previewWindow.address + ".png?rev=" + root.previewRevision : ""
        asynchronous: true

        Text {
          anchors.centerIn: parent
          visible: parent.status !== Image.Ready
          text: root.previewWindow && root.previewWindow.workspace.name === "special:win-minimized" ? "Minimized" : "Preview appears after window is focused"
          color: Color.foreground
          font.pixelSize: 11
        }
      }
    }
  }

  readonly property string homeDir: Quickshell.env("HOME")
}

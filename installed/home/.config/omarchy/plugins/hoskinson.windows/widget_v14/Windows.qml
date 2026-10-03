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
  property var windowOrder: ({})
  property int nextWindowOrder: 0
  property string focusedAddress: ""
  property string captureAddress: ""
  property int previewRevision: 0
  property var previewWindow: null
  property var previewAnchor: null
  property bool previewOpen: false
  property bool previewReady: false
  property string previewCheckAddress: ""
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
    console.log("show preview", w.address, w.title)
    previewWindow = w
    previewAnchor = anchor
    previewOpen = true
    previewReady = false
    previewCheckAddress = String(w.address || "")
    if (!previewCheck.running) previewCheck.running = true
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
      for (var i = 0; i < visible.length; i++) {
        if (root.windowOrder[visible[i].address] === undefined)
          root.windowOrder[visible[i].address] = root.nextWindowOrder++
      }
      visible.sort(function(a, b) { return root.windowOrder[a.address] - root.windowOrder[b.address] })
      var next = JSON.stringify(visible.map(function(w) { return [w.address, w.title, w.workspace.name] }))
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
    command: [root.homeDir + "/.local/bin/hypr-window-preview", "capture-both", root.captureAddress, String((root.previewRevision + 1) % 2)]
    onExited: function(exitCode) {
      root.previewRevision++
      if (exitCode === 0 && root.previewWindow && root.previewWindow.address === root.captureAddress)
        root.previewReady = true
    }
  }

  Process {
    id: previewCheck
    command: ["test", "-s", root.previewDir + "/" + root.previewCheckAddress + "-0.png"]
    onExited: function(exitCode) {
      if (root.previewWindow && root.previewWindow.address === root.previewCheckAddress)
        root.previewReady = exitCode === 0
    }
  }

  Timer {
    id: captureDelay
    interval: 450
    onTriggered: if (!captureProcess.running && root.captureAddress) captureProcess.running = true
  }

  Timer {
    id: previewClose
    interval: 250
    onTriggered: { console.log("close preview", previewCard.containsMouse, taskHover.containsMouse); if (!previewCard.containsMouse && !taskHover.containsMouse) root.previewOpen = false }
  }

  Timer {
    interval: 650
    repeat: true
    running: true
    triggeredOnStart: true
    onTriggered: root.refresh()
  }

  Flickable {
    id: tasksFlickable
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
        id: taskRepeater
        model: root.windows

        Item {
          id: taskItem
          required property var modelData
          readonly property bool minimized: modelData.workspace.name === "special:win-minimized"
          readonly property bool active: root.focusedAddress === modelData.address && !minimized
          width: root.buttonWidth
          height: root.barSize

          Image {
            id: appIcon
            width: 19
            height: 19
            anchors.centerIn: parent
            source: root.iconSource(taskItem.modelData)
            sourceSize.width: width * Screen.devicePixelRatio
            sourceSize.height: height * Screen.devicePixelRatio
            fillMode: Image.PreserveAspectFit
            asynchronous: true
            opacity: taskItem.minimized ? 0.55 : 1
          }

          Text {
            anchors.centerIn: parent
            visible: appIcon.status !== Image.Ready
            text: (taskItem.modelData.class || "?").substring(0, 1).toUpperCase()
            color: root.bar ? root.bar.barForeground : Color.foreground
            font.pixelSize: 13
          }

          Rectangle {
            width: parent.width - 12
            height: 2
            radius: 1
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            color: Color.accent
            opacity: taskItem.active ? 1 : (taskItem.minimized ? 0.15 : 0.45)
          }
        }
      }
    }

    MouseArea {
      id: taskHover
      anchors.fill: parent
      hoverEnabled: true
      acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
      cursorShape: Qt.PointingHandCursor

      function indexAt(x) {
        var stride = root.buttonWidth + row.spacing
        var index = Math.floor((x + tasksFlickable.contentX) / stride)
        return index >= 0 && index < root.windows.length ? index : -1
      }

      function hoverAt(x) {
        var index = indexAt(x)
        console.log("hover", x, index)
        if (index < 0) { root.hidePreviewSoon(); return }
        var w = root.windows[index]
        if (!root.previewWindow || root.previewWindow.address !== w.address || !root.previewOpen)
          root.showPreview(w, taskRepeater.itemAt(index))
      }

      onEntered: hoverAt(mouseX)
      onPositionChanged: function(mouse) { hoverAt(mouse.x) }
      onExited: root.hidePreviewSoon()
      onClicked: function(mouse) {
        var index = indexAt(mouse.x)
        if (index < 0 || !root.bar) return
        var w = root.windows[index]
        var address = String(w.address || "")
        if (!/^0x[0-9a-fA-F]+$/.test(address)) return
        var active = root.focusedAddress === address && w.workspace.name !== "special:win-minimized"
        root.bar.run(root.homeDir + "/.local/bin/hypr-windowctl " + (active && mouse.button === Qt.LeftButton ? "minimize " : "restore ") + address)
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
    onContainsMouseChanged: {
      if (containsMouse || taskHover.containsMouse) previewClose.stop()
      else if (root.previewOpen) root.hidePreviewSoon()
    }

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
        source: root.previewReady && root.previewWindow ? "file://" + root.previewDir + "/" + root.previewWindow.address + "-" + (root.previewRevision % 2) + ".png" : ""
        cache: false
        asynchronous: true

        Text {
          anchors.centerIn: parent
          visible: parent.status !== Image.Ready
          text: "Preview appears after window is focused"
          color: Color.foreground
          font.pixelSize: 11
        }
      }
    }
  }

  readonly property string homeDir: Quickshell.env("HOME")
}

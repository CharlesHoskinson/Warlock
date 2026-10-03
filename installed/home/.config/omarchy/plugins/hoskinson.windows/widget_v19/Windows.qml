import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "hoskinson.windows"
  property var groups: []
  property var snapGroups: []
  property string focusedAddress: ""
  property string signature: ""
  property string popupKey: ""
  property int popupIndex: -1
  property bool popupOpen: false
  property bool menuMode: false
  property string captureAddress: ""
  property int previewRevision: 0
  property var actionQueue: []
  readonly property string homeDir: Quickshell.env("HOME")
  readonly property string previewDir: (Quickshell.env("XDG_RUNTIME_DIR") || homeDir + "/.cache") + "/hypr-window-previews"
  readonly property int buttonWidth: 38
  readonly property int maxWidth: 460
  readonly property var popupGroup: groups.filter(function(g) { return g.key === root.popupKey })[0] || null
  readonly property var relatedSnaps: popupGroup ? snapGroups.filter(function(s) {
    return s.addresses.some(function(a) { return root.popupGroup.windows.some(function(w) { return w.address === a }) })
  }) : []
  readonly property var menuItems: makeMenu()

  function iconSource(group) {
    return bar && bar.shell && bar.shell.appLibrary ? bar.shell.appLibrary.iconSource(group.icon) : Quickshell.iconPath(group.icon, true)
  }
  function refresh() { if (!snapshotProcess.running) snapshotProcess.running = true }
  function runArgs(args) {
    actionQueue = actionQueue.concat([args])
    drainQueue()
  }
  function drainQueue() {
    if (actionProcess.running || !actionQueue.length) return
    actionProcess.command = actionQueue[0]
    actionQueue = actionQueue.slice(1)
    actionProcess.running = true
  }
  function taskbarAction(command, key, extra) {
    var args = [homeDir + "/.local/bin/hypr-taskbar", command, key]
    if (extra !== undefined) args.push(extra)
    runArgs(args)
    popupOpen = false
  }
  function windowAction(command, address) {
    if (!/^0x[0-9a-fA-F]+$/.test(address)) return
    runArgs([homeDir + "/.local/bin/hypr-windowctl", command, address])
    popupOpen = false
  }
  function recall(id) {
    runArgs([homeDir + "/.local/bin/hypr-snap-groups", "recall", id])
    popupOpen = false
  }
  function makeMenu() {
    var g = popupGroup
    if (!g) return []
    var result = []
    if (g.desktopId) {
      result.push({label: "Open " + g.name, command: "launch", key: g.desktopId})
      result.push({label: g.pinned ? "Unpin from taskbar" : "Pin to taskbar", command: g.pinned ? "unpin" : "pin", key: g.desktopId})
    }
    if (g.windows.length > 1) result.push({label: "Restore all " + g.windows.length + " windows", command: "restore-group", key: g.key})
    g.actions.forEach(function(a) { result.push({label: a.name, command: "launch", key: g.desktopId, extra: a.id}) })
    g.recent.forEach(function(r) { result.push({label: "Recent: " + r.name, command: "recent", key: g.desktopId, extra: r.uri}) })
    relatedSnaps.forEach(function(s) { result.push({label: "Recall " + s.name, snap: s.id}) })
    return result
  }
  function openGroup(index, menu) {
    if (index < 0 || index >= groups.length) return
    popupIndex = index
    popupKey = groups[index].key
    menuMode = menu
    popupOpen = true
    closeDelay.stop()
    if (bar) bar.hideTooltip(stableAnchor)
  }
  function update(output) {
    try {
      var data = JSON.parse(output)
      var next = JSON.stringify(data.groups.map(function(g) {
        return [g.key, g.pinned, g.actions, g.recent, g.windows.map(function(w) { return [w.address, w.title, w.workspace.name, w.previewReady] })]
      })) + JSON.stringify(data.snapGroups)
      if (signature !== next) {
        signature = next
        groups = data.groups
        snapGroups = data.snapGroups
      }
      if (!popupGroup) popupOpen = false
      else popupIndex = groups.findIndex(function(g) { return g.key === root.popupKey })
      if (data.focusedAddress && data.focusedAddress !== focusedAddress) {
        focusedAddress = data.focusedAddress
        captureAddress = focusedAddress
        captureDelay.restart()
      }
    } catch (e) { console.warn("Taskbar snapshot: " + e) }
  }

  implicitWidth: Math.min(maxWidth, row.implicitWidth)
  implicitHeight: barSize

  Process {
    id: snapshotProcess
    command: [root.homeDir + "/.local/bin/hypr-taskbar", "snapshot"]
    stdout: StdioCollector { waitForEnd: true; onStreamFinished: root.update(text) }
  }
  Process {
    id: actionProcess
    onExited: function(code) {
      if (code !== 0) console.warn("Taskbar action failed with code " + code)
      root.refresh()
      queueDelay.restart()
    }
  }
  Timer { id: queueDelay; interval: 10; onTriggered: root.drainQueue() }
  Process {
    id: captureProcess
    command: [root.homeDir + "/.local/bin/hypr-window-preview", "capture-both", root.captureAddress, String((root.previewRevision + 1) % 2)]
    onExited: { root.previewRevision++; root.refresh() }
  }
  Timer { id: captureDelay; interval: 450; onTriggered: if (!captureProcess.running && root.captureAddress) captureProcess.running = true }
  Timer {
    id: closeDelay
    interval: 250
    onTriggered: if (!previewCard.containsMouse && !taskHover.containsMouse && !root.menuMode) root.popupOpen = false
  }
  Timer { interval: 900; repeat: true; running: true; triggeredOnStart: true; onTriggered: root.refresh() }

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
        model: root.groups
        Item {
          id: taskItem
          required property var modelData
          readonly property bool active: modelData.windows.some(function(w) { return w.address === root.focusedAddress && w.workspace.name !== "special:win-minimized" })
          readonly property bool minimized: modelData.windows.length > 0 && modelData.windows.every(function(w) { return w.workspace.name === "special:win-minimized" })
          width: root.buttonWidth
          height: root.barSize
          Image {
            id: appIcon
            width: 19; height: 19
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
            text: taskItem.modelData.name.substring(0, 1).toUpperCase()
            color: root.bar ? root.bar.barForeground : Color.foreground
            font.pixelSize: 13
          }
          Text {
            anchors.right: parent.right; anchors.top: parent.top
            anchors.topMargin: 2
            visible: taskItem.modelData.windows.length > 1
            text: String(taskItem.modelData.windows.length)
            color: Color.foreground
            font.pixelSize: 9
          }
          Rectangle {
            width: parent.width - 12; height: 2; radius: 1
            visible: taskItem.modelData.windows.length > 0
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            color: Color.accent
            opacity: taskItem.active ? 1 : taskItem.minimized ? 0.15 : 0.45
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
      property int pressedIndex: -1
      property real pressedX: 0
      property bool reordered: false
      function indexAt(x) {
        var index = Math.floor((x + tasksFlickable.contentX) / (root.buttonWidth + row.spacing))
        return index >= 0 && index < root.groups.length ? index : -1
      }
      function hoverAt(x) {
        if (root.menuMode && root.popupOpen || pressed) return
        var index = indexAt(x)
        if (index < 0) { closeDelay.restart(); return }
        if (root.popupKey !== root.groups[index].key || !root.popupOpen) root.openGroup(index, false)
        else closeDelay.stop()
      }
      onEntered: hoverAt(mouseX)
      onPositionChanged: function(mouse) { hoverAt(mouse.x) }
      onExited: if (!root.menuMode) closeDelay.restart()
      onPressed: function(mouse) { pressedIndex = indexAt(mouse.x); pressedX = mouse.x; reordered = false }
      onReleased: function(mouse) {
        var target = indexAt(mouse.x)
        if (mouse.button === Qt.LeftButton && pressedIndex >= 0 && target >= 0 && target !== pressedIndex && Math.abs(mouse.x - pressedX) > 10) {
          reordered = true
          root.taskbarAction("reorder", root.groups[pressedIndex].key, root.groups[target].key)
        }
      }
      onClicked: function(mouse) {
        if (reordered) return
        var index = indexAt(mouse.x)
        if (index < 0) return
        var g = root.groups[index]
        if (mouse.button === Qt.RightButton) { root.openGroup(index, true); return }
        if (mouse.button === Qt.MiddleButton || !g.windows.length) {
          if (g.desktopId) root.taskbarAction("launch", g.desktopId)
          return
        }
        if (g.windows.length > 1) { root.openGroup(index, false); return }
        var w = g.windows[0]
        root.windowAction(root.focusedAddress === w.address && w.workspace.name !== "special:win-minimized" ? "minimize" : "restore", w.address)
      }
    }
  }
  Item {
    id: stableAnchor
    x: Math.max(0, root.popupIndex) * (root.buttonWidth + row.spacing) - tasksFlickable.contentX
    width: root.buttonWidth; height: root.barSize
    opacity: 0; enabled: false
  }
  PopupCard {
    id: previewCard
    anchorItem: stableAnchor
    bar: root.bar
    owner: QtObject { function close() { root.popupOpen = false; root.menuMode = false } }
    triggerMode: root.menuMode ? "click" : "hover"
    open: root.popupOpen && root.popupGroup !== null
    contentWidth: 320
    contentHeight: Math.min(460, 44 + (root.menuMode ? root.menuItems.length * 32 : Math.max(1, root.popupGroup ? root.popupGroup.windows.length : 0) * 155 + (root.relatedSnaps.length ? 32 : 0)))
    onContainsMouseChanged: {
      if (containsMouse || taskHover.containsMouse) closeDelay.stop()
      else if (root.popupOpen && !root.menuMode) closeDelay.restart()
    }
    Flickable {
      anchors.fill: parent
      contentWidth: width
      contentHeight: popupColumn.implicitHeight
      clip: true
      boundsBehavior: Flickable.StopAtBounds
      Column {
        id: popupColumn
        width: parent.width
        spacing: 6
        Text {
          width: parent.width
          text: root.popupGroup ? root.popupGroup.name + (root.popupGroup.pinned ? " · Pinned" : "") : ""
          color: Color.foreground; font.pixelSize: 12
          elide: Text.ElideRight; textFormat: Text.PlainText
        }
        Repeater {
          model: root.menuMode ? root.menuItems : []
          Rectangle {
            required property var modelData
            width: popupColumn.width; height: 26; radius: 4
            color: menuMouse.containsMouse ? Color.accent : "transparent"
            Text { anchors.fill: parent; anchors.leftMargin: 5; verticalAlignment: Text.AlignVCenter; text: modelData.label; color: Color.foreground; font.pixelSize: 11; elide: Text.ElideRight; textFormat: Text.PlainText }
            MouseArea {
              id: menuMouse
              anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
              onClicked: { if (modelData.snap) root.recall(modelData.snap); else root.taskbarAction(modelData.command, modelData.key, modelData.extra) }
            }
          }
        }
        Repeater {
          model: !root.menuMode && root.popupGroup ? root.popupGroup.windows : []
          Rectangle {
            id: windowPreview
            required property var modelData
            width: popupColumn.width; height: 149; radius: 4
            color: windowMouse.containsMouse ? Color.accent : "transparent"
            Text {
              anchors.left: parent.left; anchors.right: closeButton.left; anchors.top: parent.top
              height: 24; anchors.leftMargin: 4
              text: (modelData.workspace.name === "special:win-minimized" ? "↓ " : "") + (modelData.title || "Window")
              color: Color.foreground; font.pixelSize: 11; elide: Text.ElideRight; textFormat: Text.PlainText
            }
            Image {
              anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
              height: 120; fillMode: Image.PreserveAspectFit
              source: windowPreview.modelData.previewReady ? "file://" + root.previewDir + "/" + windowPreview.modelData.address + "-" + (root.previewRevision % 2) + ".png" : ""
              cache: false; asynchronous: true
              Text { anchors.centerIn: parent; visible: parent.status !== Image.Ready; text: "Preview appears after window is focused"; color: Color.foreground; font.pixelSize: 10 }
            }
            MouseArea {
              id: windowMouse
              anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
              onClicked: root.windowAction("restore", windowPreview.modelData.address)
            }
            Rectangle {
              id: closeButton
              anchors.right: parent.right; anchors.top: parent.top
              width: 24; height: 24; radius: 4
              color: closeMouse.containsMouse ? "#b73333" : "transparent"
              Text { anchors.centerIn: parent; text: "×"; color: Color.foreground; font.pixelSize: 16 }
              MouseArea {
                id: closeMouse
                anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                onClicked: { root.runArgs(["hyprctl", "dispatch", 'hl.dsp.window.close({ window = "address:' + windowPreview.modelData.address + '" })']); root.popupOpen = false }
              }
            }
          }
        }
        Repeater {
          model: !root.menuMode ? root.relatedSnaps : []
          Rectangle {
            required property var modelData
            width: popupColumn.width; height: 26; radius: 4
            color: snapMouse.containsMouse ? Color.accent : "transparent"
            Text { anchors.fill: parent; verticalAlignment: Text.AlignVCenter; text: "Recall " + modelData.name; color: Color.foreground; font.pixelSize: 11; elide: Text.ElideRight; textFormat: Text.PlainText }
            MouseArea { id: snapMouse; anchors.fill: parent; hoverEnabled: true; onClicked: root.recall(modelData.id) }
          }
        }
        Text {
          visible: !root.menuMode && root.popupGroup !== null && !root.popupGroup.windows.length
          width: parent.width; height: visible ? 30 : 0
          text: "Click to open · Right-click for actions"
          color: Color.foreground; font.pixelSize: 11
        }
      }
    }
  }
}

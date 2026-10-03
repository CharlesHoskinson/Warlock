import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "hoskinson.windows"
  property var appGroups: []
  property var taskbarSettings: ({})
  property var monitors: []
  property bool keyboardMode: false
  property int selectedWindowIndex: 0
  readonly property var groups: displayGroups()
  readonly property bool uncombined: taskbarSettings.combineMode === "never" || taskbarSettings.combineMode === "when-full" && appGroups.reduce(function(n,g) { return n + Math.max(1,g.windows.length) * 130 },0) <= maxWidth
  readonly property int currentMonitor: monitors.filter(function(m) { return root.bar && root.bar.screen && m.name === root.bar.screen.name })[0] ? monitors.filter(function(m) { return root.bar && root.bar.screen && m.name === root.bar.screen.name })[0].id : -1
  readonly property bool ipcOwner: currentMonitor < 0 || monitors.some(function(m) { return m.id === root.currentMonitor && m.focused })
  function displayGroups() {
    var result = []
    appGroups.forEach(function(g) {
      var windows = g.windows.filter(function(w) { return root.taskbarSettings.displayMode !== "monitor" || root.currentMonitor < 0 || w.monitor === root.currentMonitor })
      if (!windows.length && !g.pinned) return
      if (root.uncombined && windows.length) windows.forEach(function(w) { var item = Object.assign({}, g); item.windows = [w]; item.displayKey = g.key + "@" + w.address; result.push(item) })
      else { var item = Object.assign({},g); item.windows = windows; item.displayKey = g.key; result.push(item) }
    })
    return result
  }
  function widthFor(g) { return uncombined && g.windows.length ? 130 : buttonWidth }
  function positionFor(index) { var x=0; for(var i=0;i<index && i<groups.length;i++) x += widthFor(groups[i])+row.spacing; return x }
  function activateIndex(index) {
    if(index<0 || index>=groups.length) return
    var g=groups[index]
    if(!g.windows.length) { if(g.desktopId) taskbarAction("launch",g.desktopId); return }
    if(g.windows.length>1) { openGroup(index,false); keyboardMode=true; return }
    var w=g.windows[0]
    windowAction(w.address===focusedAddress && w.workspace.name!=="special:win-minimized" ? "minimize" : "restore",w.address)
  }
  IpcHandler {
    target: "hoskinson.windows"
    enabled: root.ipcOwner
    function dismiss(): void { root.popupOpen=false; root.keyboardMode=false; root.menuMode=false }
    function state(): string { return JSON.stringify({groups:root.groups.length, popupOpen:root.popupOpen, popupIndex:root.popupIndex, menuMode:root.menuMode, keyboardMode:root.keyboardMode, keyboardFocus:popupFlickable.activeFocus, combineMode:root.taskbarSettings.combineMode || "always", displayMode:root.taskbarSettings.displayMode || "all"}) }
    function activate(number: int): void { root.activateIndex(number-1) }
    function launch(number: int): void { var g=root.groups[number-1]; if(g && g.desktopId) root.taskbarAction("launch",g.desktopId) }
    function menu(number: int): void { root.openGroup(number-1,true); root.keyboardMode=true }
    function cycle(step: int): void { if(!root.groups.length) return; var i=root.popupOpen ? root.popupIndex : -1; root.openGroup((i+step+root.groups.length)%root.groups.length,false); root.keyboardMode=true }
  }
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
  readonly property var popupGroup: groups.filter(function(g) { return g.displayKey === root.popupKey })[0] || null
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
    result.push({label: "Combine: Always", command: "config", key: "combineMode", extra: "always"})
    result.push({label: "Combine: When taskbar is full", command: "config", key: "combineMode", extra: "when-full"})
    result.push({label: "Combine: Never", command: "config", key: "combineMode", extra: "never"})
    result.push({label: "Show windows on all displays", command: "config", key: "displayMode", extra: "all"})
    result.push({label: "Show windows on this display", command: "config", key: "displayMode", extra: "monitor"})
    return result
  }
  function openGroup(index, menu) {
    if (index < 0 || index >= groups.length) return
    popupIndex = index
    popupKey = groups[index].displayKey
    keyboardMode = false
    selectedWindowIndex = 0
    menuMode = menu
    popupOpen = true
    closeDelay.stop()
    if (bar) bar.hideTooltip(stableAnchor)
  }
  function update(output) {
    try {
      var data = JSON.parse(output)
      taskbarSettings = data.settings || {}
      monitors = data.monitors || []
      var next = JSON.stringify(data.groups.map(function(g) {
        return [g.key, g.pinned, g.actions, g.recent, g.windows.map(function(w) { return [w.address, w.title, w.workspace.name, w.previewReady] })]
      })) + JSON.stringify(data.snapGroups)
      if (signature !== next) {
        signature = next
        appGroups = data.groups
        snapGroups = data.snapGroups
      }
      if (!popupGroup) popupOpen = false
      else popupIndex = groups.findIndex(function(g) { return g.displayKey === root.popupKey })
      if (data.focusedAddress !== focusedAddress) {
        focusedAddress = data.focusedAddress
        captureAddress = focusedAddress
        if(captureAddress) captureDelay.restart()
      }
    } catch (e) { console.warn("Taskbar snapshot: " + e) }
  }

  implicitWidth: Math.min(maxWidth, row.implicitWidth) + 43
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
    onTriggered: if (!previewCard.containsMouse && !taskHover.containsMouse && !root.menuMode && !root.keyboardMode) root.popupOpen = false
  }
  Timer { interval: 900; repeat: true; running: true; triggeredOnStart: true; onTriggered: root.refresh() }

  Flickable {
    id: tasksFlickable
    anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom; anchors.right: taskViewButton.left
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
          width: root.widthFor(modelData)
          height: root.barSize
          Image {
            id: appIcon
            width: 19; height: 19
            x: root.uncombined ? 8 : (parent.width-width)/2
            anchors.verticalCenter: parent.verticalCenter
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
            visible: root.uncombined && taskItem.modelData.windows.length > 0
            anchors.left: appIcon.right; anchors.leftMargin: 6; anchors.right: parent.right; anchors.rightMargin: 6; anchors.verticalCenter: parent.verticalCenter
            text: taskItem.modelData.windows.length ? taskItem.modelData.windows[0].title : taskItem.modelData.name
            elide: Text.ElideRight; textFormat: Text.PlainText; color: Color.foreground; font.pixelSize: 11
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
        var px=x+tasksFlickable.contentX
        for(var i=0;i<root.groups.length;i++) if(px>=root.positionFor(i) && px<root.positionFor(i)+root.widthFor(root.groups[i])) return i
        return -1
      }
      function hoverAt(x) {
        if (root.menuMode && root.popupOpen || pressed) return
        var index = indexAt(x)
        if (index < 0) { closeDelay.restart(); return }
        if (root.popupKey !== root.groups[index].displayKey || !root.popupOpen) root.openGroup(index, false)
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
  Rectangle {
    id: taskViewButton
    anchors.right: desktopButton.left; anchors.top: parent.top; anchors.bottom: parent.bottom
    width: 26; radius: 4; color: taskViewMouse.containsMouse ? Color.accent : "transparent"
    Text { anchors.centerIn: parent; text: "▦"; color: Color.foreground; font.pixelSize: 16 }
    MouseArea {
      id: taskViewMouse
      anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
      onClicked: { root.popupOpen=false; root.runArgs(["omarchy-shell","shell","toggle","hoskinson.taskview"]) }
    }
  }
  Rectangle {
    id: desktopButton
    anchors.right: parent.right; anchors.top: parent.top; anchors.bottom: parent.bottom
    width: 14; color: desktopMouse.containsMouse ? Color.accent : "transparent"
    Rectangle { width: 1; height: parent.height-12; anchors.centerIn: parent; color: Color.foreground; opacity: 0.4 }
    MouseArea {
      id: desktopMouse
      anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
      onEntered: peekDelay.restart()
      onExited: { peekDelay.stop(); root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","peek-off"]) }
      onClicked: { peekDelay.stop(); root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","peek-off"]); root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","toggle"]) }
    }
    Timer { id: peekDelay; interval: 600; onTriggered: root.runArgs([root.homeDir+"/.local/bin/hypr-desktop","peek-on"]) }
  }
  Item {
    id: stableAnchor
    x: root.positionFor(Math.max(0,root.popupIndex)) - tasksFlickable.contentX
    width: root.popupGroup ? root.widthFor(root.popupGroup) : root.buttonWidth; height: root.barSize
    opacity: 0; enabled: false
  }
  PopupCard {
    id: previewCard
    anchorItem: stableAnchor
    bar: root.bar
    owner: QtObject { function close() { root.popupOpen = false; root.menuMode = false; root.keyboardMode = false } }
    triggerMode: root.menuMode || root.keyboardMode ? "click" : "hover"
    open: root.popupOpen && root.popupGroup !== null
    contentWidth: 320
    contentHeight: Math.min(460, 44 + (root.menuMode ? root.menuItems.length * 32 : Math.max(1, root.popupGroup ? root.popupGroup.windows.length : 0) * 155 + (root.relatedSnaps.length ? 32 : 0)))
    onContainsMouseChanged: {
      if (containsMouse || taskHover.containsMouse) closeDelay.stop()
      else if (root.popupOpen && !root.menuMode && !root.keyboardMode) closeDelay.restart()
    }
    Flickable {
      id: popupFlickable
      anchors.fill: parent
      focus: root.keyboardMode
      Keys.onPressed: function(event) {
        if(event.key===Qt.Key_Escape) { root.popupOpen=false; root.keyboardMode=false; event.accepted=true }
        else if(event.key===Qt.Key_Left || event.key===Qt.Key_Right) { var step=event.key===Qt.Key_Left ? -1 : 1; root.openGroup((root.popupIndex+step+root.groups.length)%root.groups.length,false); root.keyboardMode=true; event.accepted=true }
        else if(event.key===Qt.Key_Up || event.key===Qt.Key_Down) { root.selectedWindowIndex=Math.max(0,root.selectedWindowIndex+(event.key===Qt.Key_Up ? -1 : 1)); event.accepted=true }
        else if(event.key===Qt.Key_Return || event.key===Qt.Key_Enter) {
          if(root.menuMode) { var item=root.menuItems[root.selectedWindowIndex%root.menuItems.length]; if(item.snap) root.recall(item.snap); else root.taskbarAction(item.command,item.key,item.extra) }
          else if(root.popupGroup.windows.length) root.windowAction("restore",root.popupGroup.windows[root.selectedWindowIndex%root.popupGroup.windows.length].address)
          else if(root.popupGroup.desktopId) root.taskbarAction("launch",root.popupGroup.desktopId)
          event.accepted=true
        }
      }
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
            required property int index
            width: popupColumn.width; height: 26; radius: 4
            color: root.keyboardMode && root.selectedWindowIndex % root.menuItems.length === index || menuMouse.containsMouse ? Color.accent : "transparent"
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
            required property int index
            width: popupColumn.width; height: 149; radius: 4
            color: root.keyboardMode && root.selectedWindowIndex % root.popupGroup.windows.length === index || windowMouse.containsMouse ? Color.accent : "transparent"
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

import QtQuick
import "file:///home/hoskinson/.local/share/hypr-window-controls/qml/WindowAccessibilityV4"
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
  property bool accessibilityReady: false
  property var desktops: []
  property string activeId: "1"
  property string viewedId: ""
  property int selectedWindow: 0
  property bool desktopKeys: false
  property string moveAddress: ""
  property bool moveMenuOpen: false
  property bool desktopMenuOpen: false
  property string desktopMenuId: ""
  property int contextSelected: 0
  readonly property var desktopMenuItems: [
    {label:"Rename desktop",action:"rename",enabled:true},
    {label:"Move desktop left",action:"left",enabled:desktops.findIndex(function(d) { return d.id===root.desktopMenuId })>0},
    {label:"Move desktop right",action:"right",enabled:desktops.findIndex(function(d) { return d.id===root.desktopMenuId })<desktops.length-1},
    {label:"Close desktop",action:"close",enabled:desktops.length>1}
  ]
  property string errorMessage: ""
  property var actionQueue: []
  property string listSignature: ""
  property bool editing: false
  property bool pointerDown: false
  property string dragKind: ""
  property string dragValue: ""
  property string dragTitle: ""
  property string dragPreview: ""
  property real dragX: 0
  property real dragY: 0
  property real pressX: 0
  property real pressY: 0
  property bool dragging: false
  property int dropIndex: -1
  property bool dropAfter: false
  readonly property string homeDir: Quickshell.env("HOME")
  readonly property var focusedScreen: {
    var name = Hyprland.focusedMonitor ? String(Hyprland.focusedMonitor.name || "") : ""
    for (var i = 0; i < Quickshell.screens.length; i++)
      if (Quickshell.screens[i].name === name) return Quickshell.screens[i]
    return Quickshell.screens.length ? Quickshell.screens[0] : null
  }
  readonly property var viewedDesktop: {
    var id = viewedId || activeId
    for (var i = 0; i < desktops.length; i++) if (desktops[i].id === id) return desktops[i]
    return desktops.length ? desktops[0] : null
  }
  readonly property var windows: viewedDesktop ? viewedDesktop.windows : []

  // Updating a title or preview must preserve the actual accessible object.
  // Replacing a JavaScript array Repeater recreates every card on each poll.
  ListModel { id: windowCards }
  ListModel { id: desktopCards }
  function syncCards(model, entries, identityProperty) {
    for (var i = 0; i < entries.length; i++) {
      var key = String(entries[i][identityProperty])
      var found = -1
      for (var j = i; j < model.count; j++) {
        if (model.get(j).identity === key) { found = j; break }
      }
      var payload = JSON.stringify(entries[i])
      if (found < 0) model.insert(i, {identity: key, payload: payload})
      else {
        if (found !== i) model.move(found, i, 1)
        if (model.get(i).payload !== payload) model.setProperty(i, "payload", payload)
      }
    }
    if (model.count > entries.length) model.remove(entries.length, model.count - entries.length)
  }
  onWindowsChanged: syncCards(windowCards, windows, "stableId")
  onDesktopsChanged: syncCards(desktopCards, desktops, "id")

  function iconSource(window) {
    var appClass = String(window.class || "")
    var apps = DesktopEntries.applications.values || []
    var name = appClass || "application-x-executable"
    for (var i = 0; i < apps.length; i++) {
      if (String(apps[i].id || "").toLowerCase() === appClass.toLowerCase()) {
        name = String(apps[i].icon || name)
        break
      }
    }
    return shell && shell.appLibrary ? shell.appLibrary.iconSource(name) : Quickshell.iconPath(name, true)
  }
  function refresh() {
    if (!listProcess.running && !actionProcess.running && !pointerDown && !editing)
      listProcess.running = true
  }
  function applyList(raw) {
    if (pointerDown || editing) return
    try {
      var result = JSON.parse(raw)
      var signature = JSON.stringify(result)
      if (signature === listSignature) { if (!viewedId) viewedId = activeId; return }
      listSignature = signature
      var selectedIdentity = windows[selectedWindow] ? String(windows[selectedWindow].stableId) : ""
      desktops = result.desktops || []
      activeId = String(result.active || "1")
      if (!desktops.some(function(d) { return d.id === viewedId })) viewedId = activeId
      var preservedIndex = windows.findIndex(function(w) { return String(w.stableId) === selectedIdentity })
      selectedWindow = preservedIndex >= 0 ? preservedIndex : Math.max(0, Math.min(selectedWindow, windows.length - 1))
    } catch (e) { errorMessage = "Could not load desktops"; console.warn("Task View: " + e) }
  }
  function action(args) {
    if (args[0] === "move" || args[0] === "new-move") {
      var w = capturedWindow(args[1])
      if (!w) return
      args = args.concat([String(w.stableId || ""), String(w.pid || "")])
    }
    errorMessage = ""
    actionQueue = actionQueue.concat([args])
    runNextAction()
  }
  function runNextAction() {
    if (actionProcess.running || !actionQueue.length) return
    var queue = actionQueue.slice()
    var args = queue.shift()
    actionQueue = queue
    actionProcess.command = [homeDir + "/.local/bin/hypr-desktops"].concat(args)
    actionProcess.running = true
  }
  function open() {
    accessibilityReady = false
    opened = true
    viewedId = ""
    selectedWindow = 0
    desktopKeys = false
    errorMessage = ""
    refresh()
    focusLater.restart()
  }
  function cancelDrag() {
    pointerDown = false
    dragging = false
    dragKind = ""
    dropIndex = -1
  }
  function close() {
    accessibilityReady = false
    opened = false
    moveMenuOpen = false
    desktopMenuOpen = false
    editing = false
    cancelDrag()
    desktopClick.stop()
  }
  function toggle() { if (opened) dismiss(); else open() }
  function dismiss() {
    close()
    if (shell && typeof shell.hide === "function") shell.hide("hoskinson.taskview")
  }
  function capturedWindow(address) {
    for (var i=0; i<desktops.length; i++) {
      var w=desktops[i].windows.filter(function(c) { return c.address === address })[0]
      if (w) return w
    }
    return null
  }
  function desktopMenuAction(command) {
    var index = desktops.findIndex(function(d) { return d.id === root.desktopMenuId })
    if (index < 0) { desktopMenuOpen = false; return }
    if (command === "rename") {
      var card = desktopRepeater.itemAt(index)
      desktopMenuOpen = false
      if (card) card.beginRename()
      return
    }
    if (command === "close" && desktops.length > 1) action(["close", desktopMenuId])
    else if (command === "left" && index > 0) action(["reorder", desktopMenuId, desktops[index-1].id])
    else if (command === "right" && index < desktops.length-1) action(["reorder", desktopMenuId, index+2 < desktops.length ? desktops[index+2].id : "end"])
    desktopMenuOpen = false
  }
  function focusWindow(address) {
    if (!/^0x[0-9a-fA-F]+$/.test(address)) return
    var w = capturedWindow(address)
    if (!w) return
    // A detached process survives a plugin reload while the layer releases focus.
    Quickshell.execDetached(["bash", "-c", 'sleep 0.06; exec "$1" restore "$2" "$3" "$4"', "task-view-focus", homeDir + "/.local/bin/hypr-windowctl", address, String(w.stableId || ""), String(w.pid || "")])
    dismiss()
  }
  function closeWindow(address) {
    if (!/^0x[0-9a-fA-F]+$/.test(address)) return
    var w = capturedWindow(address)
    if (!w) return
    Quickshell.execDetached([homeDir + "/.local/bin/hypr-window-menu", "act", address, "close", String(w.stableId || ""), String(w.pid || "")])
    refreshLater.restart()
  }
  function previewDesktop(id) {
    if (pointerDown || editing || moveMenuOpen || desktopMenuOpen) return
    viewedId = id
    selectedWindow = 0
  }
  function press(source, mouse, kind, value, title, preview) {
    var point = source.mapToItem(panel.contentItem, mouse.x, mouse.y)
    pointerDown = true
    dragging = false
    pressX = dragX = point.x
    pressY = dragY = point.y
    dragKind = kind
    dragValue = value
    dragTitle = title
    dragPreview = preview || ""
    dropIndex = -1
  }
  function motion(source, mouse) {
    if (!pointerDown) return
    var point = source.mapToItem(panel.contentItem, mouse.x, mouse.y)
    dragX = point.x
    dragY = point.y
    if (!dragging && Math.abs(dragX - pressX) + Math.abs(dragY - pressY) > 10) {
      dragging = true
      desktopClick.stop()
      moveMenuOpen = false
    }
    if (!dragging) return
    dropIndex = -1
    var region = desktopScroll.mapToItem(panel.contentItem, 0, 0)
    if (dragY < region.y || dragY > region.y + desktopScroll.height || dragX < region.x || dragX > region.x + desktopScroll.width) return
    for (var i = 0; i < desktopRepeater.count; i++) {
      var item = desktopRepeater.itemAt(i)
      var at = item.mapToItem(panel.contentItem, 0, 0)
      if (dragX >= at.x && dragX <= at.x + item.width && dragY >= at.y && dragY <= at.y + item.height) {
        dropIndex = i
        dropAfter = dragX > at.x + item.width / 2
        break
      }
    }
    if (dropIndex < 0 && dragKind === "window") {
      var addAt = newDesktopCard.mapToItem(panel.contentItem, 0, 0)
      if (dragX >= addAt.x && dragX <= addAt.x + newDesktopCard.width && dragY >= addAt.y && dragY <= addAt.y + newDesktopCard.height)
        dropIndex = desktops.length
    }
  }
  function release() {
    var wasDrag = dragging
    if (dragging && dropIndex >= 0) {
      var target = desktops[dropIndex]
      if (dragKind === "window") {
        if (dropIndex === desktops.length) {
          viewedId = ""
          action(["new-move", dragValue])
        } else if (!viewedDesktop || target.id !== viewedDesktop.id) action(["move", dragValue, target.id])
      } else if (dragKind === "desktop" && target.id !== dragValue) {
        var before = target.id
        if (dropAfter) {
          before = "end"
          for (var i = dropIndex + 1; i < desktops.length; i++) {
            if (desktops[i].id !== dragValue) { before = desktops[i].id; break }
          }
        }
        if (before !== dragValue) action(["reorder", dragValue, before])
      }
    }
    cancelDrag()
    return wasDrag
  }
  function desktopIndex() {
    for (var i = 0; i < desktops.length; i++) if (desktops[i].id === (viewedId || activeId)) return i
    return 0
  }

  Process {
    id: listProcess
    command: [root.homeDir + "/.local/bin/hypr-desktops", "list"]
    stdout: StdioCollector { waitForEnd: true; onStreamFinished: root.applyList(text) }
  }
  Process {
    id: actionProcess
    stdout: StdioCollector { waitForEnd: true; onStreamFinished: root.applyList(text) }
    stderr: StdioCollector { waitForEnd: true; onStreamFinished: { if (text.trim()) root.errorMessage = text.trim().replace(/^hypr-desktops: /, "") } }
    onExited: { root.runNextAction(); refreshLater.restart() }
  }
  Timer { id: refreshLater; interval: 250; onTriggered: root.refresh() }
  Timer { id: focusLater; interval: 80; onTriggered: { keyCatcher.forceActiveFocus(); root.accessibilityReady = true } }
  Timer { interval: 1200; repeat: true; running: root.opened; onTriggered: root.refresh() }
  Timer {
    id: desktopClick
    property string targetId: ""
    interval: 260
    onTriggered: { root.action(["switch", targetId]); root.dismiss() }
  }
  Timer {
    interval: 45; repeat: true; running: root.dragging
    onTriggered: {
      var region = desktopScroll.mapToItem(panel.contentItem, 0, 0)
      if (root.dragY < region.y || root.dragY > region.y + desktopScroll.height) return
      if (root.dragX < region.x + 32) desktopScroll.contentX = Math.max(0, desktopScroll.contentX - 12)
      else if (root.dragX > region.x + desktopScroll.width - 32)
        desktopScroll.contentX = Math.min(Math.max(0, desktopScroll.contentWidth - desktopScroll.width), desktopScroll.contentX + 12)
    }
  }
  IpcHandler {
    target: "hoskinson.taskview"
    function open(): void { root.open() }
    function close(): void { root.dismiss() }
    function toggle(): void { root.toggle() }
    function state(): string { return JSON.stringify({opened: root.opened, viewed: root.viewedId, selectedWindow: root.selectedWindow, desktopKeys: root.desktopKeys, dragging: root.dragging}) }
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

    Rectangle { anchors.fill: parent; color: "#d51b2029" }
    MouseArea { anchors.fill: parent; onClicked: root.dismiss() }
    Rectangle {
      id: card
      Accessible.role: Accessible.Dialog
      Accessible.name: "Task View"
      Accessible.ignored: !root.opened
      width: Math.min(1240, panel.width - 64)
      height: Math.min(820, panel.height - 72)
      anchors.centerIn: parent
      radius: 16
      color: Color.menu.background
      border.color: Color.menu.border
      MouseArea { anchors.fill: parent; onClicked: keyCatcher.forceActiveFocus() }
      Item {
        id: keyCatcher
        Accessible.ignored: true
        anchors.fill: parent
        focus: true
        Keys.onPressed: function(event) {
          if (root.desktopMenuOpen || root.moveMenuOpen) {
            var items = root.desktopMenuOpen ? root.desktopMenuItems : root.desktops
            if (event.key === Qt.Key_Escape) { root.desktopMenuOpen=false; root.moveMenuOpen=false }
            else if (event.key === Qt.Key_Up || event.key === Qt.Key_Down) {
              var step=event.key === Qt.Key_Up ? -1 : 1
              for(var tried=0; tried<items.length; tried++) {
                root.contextSelected=(root.contextSelected+step+items.length)%items.length
                if(items[root.contextSelected].enabled !== false) break
              }
            } else if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter) && items[root.contextSelected]) {
              if (root.desktopMenuOpen) root.desktopMenuAction(items[root.contextSelected].action)
              else { root.action(["move", root.moveAddress, items[root.contextSelected].id]); root.moveMenuOpen=false }
            }
            event.accepted=true
            return
          }
          if (event.key === Qt.Key_Escape) {
            if (root.dragging) root.cancelDrag()
            else if (root.moveMenuOpen) root.moveMenuOpen = false
            else if (root.desktopMenuOpen) root.desktopMenuOpen = false
            else root.dismiss()
          } else if (event.key === Qt.Key_Tab) {
            root.desktopKeys = !root.desktopKeys
          } else if (event.key === Qt.Key_Left || event.key === Qt.Key_Right || event.key === Qt.Key_Up || event.key === Qt.Key_Down) {
            var delta = event.key === Qt.Key_Left ? -1 : event.key === Qt.Key_Right ? 1 : event.key === Qt.Key_Up ? -windowFlow.columns : windowFlow.columns
            if (root.desktopKeys && root.desktops.length) {
              var index = (root.desktopIndex() + (delta < 0 ? -1 : 1) + root.desktops.length) % root.desktops.length
              root.previewDesktop(root.desktops[index].id)
              var desktopItem = desktopRepeater.itemAt(index)
              desktopScroll.contentX = Math.max(0, Math.min(desktopItem.x, desktopScroll.contentWidth - desktopScroll.width))
            } else if (root.windows.length) {
              root.selectedWindow = Math.max(0, Math.min(root.windows.length - 1, root.selectedWindow + delta))
              var item = windowRepeater.itemAt(root.selectedWindow)
              windowScroll.contentY = Math.max(0, Math.min(item.y, windowScroll.contentHeight - windowScroll.height))
            }
          } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
            if (root.desktopKeys && root.viewedDesktop) { root.action(["switch", root.viewedDesktop.id]); root.dismiss() }
            else if (root.windows[root.selectedWindow]) root.focusWindow(root.windows[root.selectedWindow].address)
          } else if (event.key === Qt.Key_Delete && !root.desktopKeys && root.windows[root.selectedWindow]) {
            root.closeWindow(root.windows[root.selectedWindow].address)
          } else if (event.key === Qt.Key_Menu) {
            var item=root.desktopKeys ? desktopRepeater.itemAt(root.desktopIndex()) : windowRepeater.itemAt(root.selectedWindow)
            if (item) item.accessibleShowMenu()
          } else { return }
          event.accepted = true
        }
        Text { x: 28; y: 23; text: "Task view"; color: Color.menu.text; font.pixelSize: 25; font.bold: true }
        Text {
          x: 28; y: 60
          text: root.viewedDesktop ? root.viewedDesktop.name + "  ·  " + root.windows.length + (root.windows.length === 1 ? " window" : " windows") : "Windows"
          color: Color.menu.text; opacity: 0.7; font.pixelSize: 13
        }
        Rectangle {
          width: 34; height: 34; radius: 7; x: parent.width - 60; y: 22
          Accessible.role: Accessible.Button
          Accessible.name: "Dismiss Task View"
          Accessible.ignored: !root.opened || !visible
          Accessible.onPressAction: if (root.opened) root.dismiss()
          color: dismissMouse.containsMouse ? Color.menu.selectedBackground : "transparent"
          Text { anchors.centerIn: parent; text: "×"; color: Color.menu.text; font.pixelSize: 24 }
          MouseArea { id: dismissMouse; anchors.fill: parent; hoverEnabled: true; onClicked: root.dismiss() }
        }
        Flickable {
          id: windowScroll
          x: 28; y: 98; width: parent.width - 56; height: parent.height - 332
          contentHeight: windowFlow.implicitHeight
          clip: true; boundsBehavior: Flickable.StopAtBounds
          interactive: !root.pointerDown
          Flow {
            id: windowFlow
            width: windowScroll.width
            property int columns: Math.max(1, Math.floor((width + 18) / 268))
            spacing: 18
            Repeater {
              id: windowRepeater
              model: windowCards
              Rectangle {
                id: windowCard
                required property string payload
                readonly property var modelData: JSON.parse(payload)
                required property int index
                Accessible.role: Accessible.Button
                Accessible.id: "taskview-window:" + modelData.stableId
                Accessible.name: modelData.title || modelData.class || "Window"
                Accessible.description: modelData.minimized ? "Minimized window" : "Open window"
                Accessible.focused: root.accessibilityReady && root.opened && !root.desktopKeys && !root.editing && !root.moveMenuOpen && !root.desktopMenuOpen && index === root.selectedWindow
                Accessible.ignored: !root.opened || !visible
                Accessible.onPressAction: if (root.opened && !root.dragging && !root.moveMenuOpen && !root.desktopMenuOpen && !root.editing) root.focusWindow(modelData.address)
                function accessibleShowMenu() {
                  if (!root.opened || root.dragging) return
                  root.moveAddress = modelData.address
                  root.desktopMenuOpen = false
                  root.contextSelected = 0
                  root.moveMenuOpen = true
                }
                property bool draggedClick: false
                width: (windowFlow.width - 18 * (windowFlow.columns - 1)) / windowFlow.columns
                height: 208; radius: 9
                color: windowMouse.containsMouse ? Color.menu.selectedBackground : Color.menu.background
                border.color: !root.desktopKeys && root.selectedWindow === index ? Color.accent : Color.menu.border
                border.width: !root.desktopKeys && root.selectedWindow === index ? 2 : 1
                opacity: root.dragging && root.dragValue === modelData.address ? 0.35 : 1
                Rectangle {
                  x: 7; y: 7; width: parent.width - 14; height: 162; radius: 5; color: "#202630"
                  Image {
                    anchors.fill: parent; anchors.margins: 2
                    source: windowCard.modelData.preview ? "file://" + windowCard.modelData.preview : ""
                    cache: false; asynchronous: true; fillMode: Image.PreserveAspectFit
                    Column {
                      anchors.centerIn: parent; spacing: 12
                      visible: parent.status !== Image.Ready
                      Image { width: 54; height: 54; anchors.horizontalCenter: parent.horizontalCenter; source: root.iconSource(windowCard.modelData) }
                      Text { anchors.horizontalCenter: parent.horizontalCenter; text: windowCard.modelData.class || "Window"; color: Color.menu.text; font.pixelSize: 13 }
                    }
                  }
                }
                Text {
                  x: 12; y: 178; width: parent.width - 24
                  text: (modelData.minimized ? "▁  " : "") + (modelData.title || modelData.class || "Window")
                  color: Color.menu.text; font.pixelSize: 12; elide: Text.ElideRight
                }
                MouseArea {
                  id: windowMouse
                  anchors.fill: parent; hoverEnabled: true; preventStealing: true
                  acceptedButtons: Qt.LeftButton | Qt.RightButton
                  cursorShape: root.dragging ? Qt.ClosedHandCursor : Qt.PointingHandCursor
                  onPressed: function(mouse) {
                    windowCard.draggedClick = false
                    root.selectedWindow = windowCard.index
                    root.desktopKeys = false
                    if (mouse.button === Qt.LeftButton) root.press(windowMouse, mouse, "window", windowCard.modelData.address, windowCard.modelData.title, windowCard.modelData.preview)
                  }
                  onPositionChanged: function(mouse) { root.motion(windowMouse, mouse) }
                  onReleased: function(mouse) { if (mouse.button === Qt.LeftButton) windowCard.draggedClick = root.release() }
                  onCanceled: root.cancelDrag()
                  onClicked: function(mouse) {
                    if (windowCard.draggedClick) return
                    if (mouse.button === Qt.RightButton) windowCard.accessibleShowMenu()
                    else root.focusWindow(windowCard.modelData.address)
                  }
                }
                Rectangle {
                  visible: root.opened
                  opacity: windowMouse.containsMouse || closeMouse.containsMouse ? 1 : 0.35
                  Accessible.role: Accessible.Button
                  Accessible.name: "Close " + (windowCard.modelData.title || windowCard.modelData.class || "window")
                  Accessible.ignored: !root.opened || !visible
                  Accessible.onPressAction: if (root.opened && !root.moveMenuOpen && !root.desktopMenuOpen && !root.editing) root.closeWindow(windowCard.modelData.address)
                  width: 26; height: 26; radius: 6
                  anchors.right: parent.right; anchors.rightMargin: 8; y: 8
                  color: closeMouse.containsMouse ? "#c84444" : "#dd303641"
                  Text { anchors.centerIn: parent; text: "×"; color: "white"; font.pixelSize: 20 }
                  MouseArea { id: closeMouse; anchors.fill: parent; hoverEnabled: true; onClicked: root.closeWindow(windowCard.modelData.address) }
                }
              }
            }
          }
          Text {
            visible: !root.windows.length; anchors.centerIn: parent
            text: "No windows on this desktop"; color: Color.menu.text; opacity: 0.65; font.pixelSize: 19
          }
        }
        Rectangle { x: 28; y: parent.height - 211; width: parent.width - 56; height: 1; color: Color.menu.border }
        Text {
          x: 28; y: parent.height - 192
          text: root.dragging ? (root.dragKind === "window" ? "Drop on a desktop to move this window" : "Drop between desktops to change their order") : "Desktops"
          color: Color.menu.text; font.pixelSize: 14; font.bold: true
        }
        Text {
          x: 28; y: parent.height - 29
          text: root.errorMessage || "Drag windows to desktops · Drag desktops to reorder · Double-click a name to rename · Tab and arrows to navigate"
          color: root.errorMessage ? "#ef8686" : Color.menu.text
          opacity: root.errorMessage ? 1 : 0.55; font.pixelSize: 11
        }
        Flickable {
          id: desktopScroll
          x: 28; y: parent.height - 164; width: parent.width - 56; height: 124
          contentWidth: desktopRow.implicitWidth
          clip: true; boundsBehavior: Flickable.StopAtBounds
          interactive: contentWidth > width && !root.pointerDown
          Row {
            id: desktopRow
            spacing: 14
            Repeater {
              id: desktopRepeater
              model: desktopCards
              Rectangle {
                id: desktopCard
                required property string payload
                readonly property var modelData: JSON.parse(payload)
                required property int index
                Accessible.role: Accessible.PageTab
                Accessible.id: "taskview-desktop:" + modelData.id
                Accessible.name: modelData.name
                Accessible.description: modelData.windows.length + " windows" + (modelData.active ? ", active desktop" : "")
                Accessible.selectable: true
                Accessible.selected: root.viewedId === modelData.id
                Accessible.focused: root.accessibilityReady && root.opened && root.desktopKeys && !root.editing && !root.desktopMenuOpen && !root.moveMenuOpen && root.viewedId === modelData.id
                Accessible.ignored: !root.opened || !visible
                Accessible.onPressAction: if (root.opened && !root.dragging && !root.moveMenuOpen && !root.desktopMenuOpen && !root.editing) { root.action(["switch", modelData.id]); root.dismiss() }
                function accessibleShowMenu() {
                  if (!root.opened || root.dragging) return
                  root.desktopMenuId = modelData.id
                  root.moveMenuOpen = false
                  root.contextSelected = 0
                  root.desktopMenuOpen = true
                }
                function beginRename() {
                  desktopClick.stop()
                  editingName = true
                  root.editing = true
                  renameField.text = modelData.name
                  renameField.forceActiveFocus()
                  renameField.selectAll()
                }
                property bool editingName: false
                property bool doubleClicked: false
                property bool draggedClick: false
                width: 184; height: 118; radius: 7
                color: desktopMouse.containsMouse || root.viewedId === modelData.id ? Color.menu.selectedBackground : Color.menu.background
                border.color: root.dragging && root.dragKind === "window" && root.dropIndex === index ? Color.accent : modelData.active ? Color.accent : Color.menu.border
                border.width: modelData.active || (root.dragging && root.dropIndex === index) ? 2 : 1
                opacity: root.dragging && root.dragKind === "desktop" && root.dragValue === modelData.id ? 0.4 : 1
                Rectangle {
                  x: 7; y: 7; width: parent.width - 14; height: 74; radius: 4; color: "#26313b"
                  Row {
                    anchors.fill: parent; anchors.margins: 5; spacing: 3
                    Repeater {
                      model: desktopCard.modelData.windows.slice(0, 3)
                      Rectangle {
                        required property var modelData
                        width: (desktopCard.width - 30) / Math.max(1, Math.min(3, desktopCard.modelData.windows.length)); height: 64
                        radius: 2; color: "#394451"
                        Image { id: miniPreview; anchors.fill: parent; source: modelData.preview ? "file://" + modelData.preview : ""; fillMode: Image.PreserveAspectFit; asynchronous: true }
                        Image { visible: miniPreview.status !== Image.Ready; width: 24; height: 24; anchors.centerIn: parent; source: root.iconSource(modelData) }
                      }
                    }
                  }
                  Text {
                    visible: !desktopCard.modelData.windows.length; anchors.centerIn: parent
                    text: "Empty desktop"; color: Color.menu.text; opacity: 0.35; font.pixelSize: 11
                  }
                }
                Text {
                  x: 9; y: 91; width: parent.width - 39
                  visible: !desktopCard.editingName
                  text: modelData.name; color: Color.menu.text; font.pixelSize: 12
                  font.bold: modelData.active; elide: Text.ElideRight
                }
                Text { x: parent.width - 27; y: 91; text: modelData.windows.length; color: Color.menu.text; opacity: 0.5; font.pixelSize: 11 }
                MouseArea {
                  id: desktopMouse
                  anchors.fill: parent; hoverEnabled: true; preventStealing: true
                  acceptedButtons: Qt.LeftButton | Qt.RightButton
                  cursorShape: root.dragging ? Qt.ClosedHandCursor : Qt.PointingHandCursor
                  onEntered: desktopHover.restart()
                  onExited: desktopHover.stop()
                  onPressed: function(mouse) {
                    desktopCard.draggedClick = false
                    desktopCard.doubleClicked = false
                    if (mouse.button === Qt.LeftButton) root.press(desktopMouse, mouse, "desktop", desktopCard.modelData.id, desktopCard.modelData.name, "")
                  }
                  onPositionChanged: function(mouse) { root.motion(desktopMouse, mouse) }
                  onReleased: function(mouse) { if (mouse.button === Qt.LeftButton) desktopCard.draggedClick = root.release() }
                  onCanceled: root.cancelDrag()
                  onClicked: function(mouse) {
                    if (mouse.button === Qt.RightButton) { desktopCard.accessibleShowMenu(); return }
                    if (desktopCard.draggedClick || desktopCard.doubleClicked || desktopCard.editingName) return
                    desktopClick.targetId = desktopCard.modelData.id
                    desktopClick.restart()
                  }
                  onDoubleClicked: function(mouse) {
                    desktopCard.doubleClicked = true
                    desktopClick.stop()
                    if (mouse.y < 83) { root.action(["switch", desktopCard.modelData.id]); root.dismiss(); return }
                    desktopCard.beginRename()
                  }
                }
                Timer { id: desktopHover; interval: 250; onTriggered: root.previewDesktop(desktopCard.modelData.id) }
                TextInput {
                  id: renameField
                  Accessible.ignored: !root.opened || !visible
                  Accessible.name: "Desktop name"
                  x: 9; y: 91; width: parent.width - 18; z: 3
                  visible: desktopCard.editingName; color: Color.menu.text
                  selectByMouse: true; maximumLength: 64; font.pixelSize: 12
                  function finish(save) {
                    if (save && text.trim()) root.action(["rename", desktopCard.modelData.id, text.trim()])
                    desktopCard.editingName = false
                    root.editing = false
                    keyCatcher.forceActiveFocus()
                  }
                  onAccepted: finish(true)
                  Keys.onReturnPressed: { finish(true); event.accepted = true }
                  Keys.onEnterPressed: { finish(true); event.accepted = true }
                  Keys.onEscapePressed: { finish(false); event.accepted = true }
                  onActiveFocusChanged: { if (!activeFocus && desktopCard.editingName) finish(true) }
                }
                Rectangle {
                  visible: root.desktops.length > 1
                  opacity: desktopMouse.containsMouse || closeDesktopMouse.containsMouse ? 1 : 0.35
                  Accessible.role: Accessible.Button
                  Accessible.name: "Close " + desktopCard.modelData.name
                  Accessible.ignored: !root.opened || !visible
                  Accessible.onPressAction: if (root.opened && root.desktops.length > 1 && !root.moveMenuOpen && !root.desktopMenuOpen && !root.editing) root.action(["close", desktopCard.modelData.id])
                  width: 22; height: 22; radius: 5; x: parent.width - 29; y: 7
                  color: closeDesktopMouse.containsMouse ? "#c84444" : "#dd303641"
                  Text { anchors.centerIn: parent; text: "×"; color: "white"; font.pixelSize: 17 }
                  MouseArea { id: closeDesktopMouse; anchors.fill: parent; hoverEnabled: true; onClicked: root.action(["close", desktopCard.modelData.id]) }
                }
                Rectangle {
                  visible: root.dragging && root.dragKind === "desktop" && root.dropIndex === desktopCard.index && root.dragValue !== desktopCard.modelData.id
                  x: root.dropAfter ? parent.width - 3 : 0; y: 0; width: 3; height: parent.height
                  radius: 1; color: Color.accent
                }
              }
            }
            Rectangle {
              id: newDesktopCard
              Accessible.role: Accessible.Button
              Accessible.name: "New desktop"
              Accessible.ignored: !root.opened || !visible
              Accessible.onPressAction: if (root.opened && !root.moveMenuOpen && !root.desktopMenuOpen && !root.editing) { root.action(["new"]); root.dismiss() }
              readonly property bool dropTarget: root.dragging && root.dragKind === "window" && root.dropIndex === root.desktops.length
              width: 145; height: 118; radius: 7
              color: dropTarget || newMouse.containsMouse ? Color.menu.selectedBackground : "transparent"
              border.color: dropTarget ? Color.accent : Color.menu.border
              border.width: dropTarget ? 2 : 1
              Text { anchors.centerIn: parent; text: "+\nNew desktop"; horizontalAlignment: Text.AlignHCenter; color: Color.menu.text; font.pixelSize: 14; lineHeight: 1.5 }
              MouseArea { id: newMouse; anchors.fill: parent; hoverEnabled: true; onClicked: { root.action(["new"]); root.dismiss() } }
            }
          }
        }
        MouseArea {
          anchors.fill: parent; visible: root.moveMenuOpen || root.desktopMenuOpen; z: 10
          onClicked: { root.moveMenuOpen = false; root.desktopMenuOpen = false; keyCatcher.forceActiveFocus() }
        }
        Rectangle {
          visible: root.moveMenuOpen; z: 11; anchors.centerIn: parent
          Accessible.role: Accessible.Dialog
          Accessible.name: "Move window to desktop"
          width: 310; height: Math.min(360, 64 + root.desktops.length * 38)
          radius: 9; color: Color.menu.background; border.color: Color.accent
          Text { x: 15; y: 15; text: "Move window to desktop"; color: Color.menu.text; font.pixelSize: 14; font.bold: true }
          Flickable {
            x: 12; y: 48; width: parent.width - 24; height: parent.height - 60
            clip: true; contentHeight: moveColumn.implicitHeight
            Column {
              id: moveColumn; width: parent.width; spacing: 5
              Repeater {
                model: root.desktops
                Rectangle {
                  required property var modelData
                  required property int index
                  Accessible.role: Accessible.MenuItem
                  Accessible.name: "Move window to " + modelData.name
                  Accessible.focused: root.accessibilityReady && root.opened && root.moveMenuOpen && root.contextSelected === index
                  Accessible.ignored: !root.opened || !visible
                  Accessible.onPressAction: if (root.opened && root.moveMenuOpen) { root.action(["move", root.moveAddress, modelData.id]); root.moveMenuOpen = false }
                  width: moveColumn.width; height: 33; radius: 4
                  color: moveMouse.containsMouse ? Color.menu.selectedBackground : Color.menu.background
                  Text { x: 8; anchors.verticalCenter: parent.verticalCenter; text: modelData.name; color: Color.menu.text; font.pixelSize: 12 }
                  MouseArea { id: moveMouse; anchors.fill: parent; hoverEnabled: true; onClicked: { root.action(["move", root.moveAddress, modelData.id]); root.moveMenuOpen = false } }
                }
              }
            }
          }
        }
        Rectangle {
          visible: root.desktopMenuOpen; z: 11; anchors.centerIn: parent
          width: 310; height: 200; radius: 9
          color: Color.menu.background; border.color: Color.accent
          Accessible.role: Accessible.Dialog
          Accessible.name: "Desktop actions"
          Column {
            anchors.fill: parent; anchors.margins: 12; spacing: 5
            Text { text:"Desktop actions"; color:Color.menu.text; font.pixelSize:14; font.bold:true; height:28 }
            Repeater {
              model: root.desktopMenuItems
              Rectangle {
                required property var modelData
                required property int index
                enabled: modelData.enabled
                width: parent.width; height: 30; radius: 4
                color: root.contextSelected === index || desktopActionMouse.containsMouse ? Color.menu.selectedBackground : Color.menu.background
                Accessible.role: Accessible.MenuItem
                Accessible.name: modelData.label
                Accessible.focused: root.accessibilityReady && root.opened && root.desktopMenuOpen && root.contextSelected === index
                Accessible.ignored: !root.opened || !visible
                Accessible.onPressAction: if (root.opened && root.desktopMenuOpen && enabled) root.desktopMenuAction(modelData.action)
                Text { x:8; anchors.verticalCenter:parent.verticalCenter; text:parent.modelData.label; color:Color.menu.text; opacity:parent.enabled ? 1 : 0.4; font.pixelSize:12 }
                MouseArea { id:desktopActionMouse; anchors.fill:parent; hoverEnabled:true; onClicked:root.desktopMenuAction(parent.modelData.action) }
              }
            }
          }
        }
      }
    }
    Rectangle {
      visible: root.dragging; z: 100
      x: Math.min(panel.width - width, Math.max(0, root.dragX + 16))
      y: Math.min(panel.height - height, Math.max(0, root.dragY + 16))
      width: 190; height: root.dragKind === "window" && root.dragPreview ? 130 : 52
      radius: 8; color: Color.menu.background; opacity: 0.93; border.color: Color.accent; border.width: 2
      Image { x: 5; y: 5; width: parent.width - 10; height: parent.height - 34; visible: root.dragKind === "window" && !!root.dragPreview; source: visible ? "file://" + root.dragPreview : ""; fillMode: Image.PreserveAspectFit }
      Text { x: 10; width: parent.width - 20; anchors.bottom: parent.bottom; anchors.bottomMargin: 12; text: root.dragTitle; color: Color.menu.text; font.pixelSize: 12; elide: Text.ElideRight }
    }
  }
}

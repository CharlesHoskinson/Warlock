import QtQuick
import "file:///home/hoskinson/.local/share/hypr-window-controls/qml/WindowAccessibilityV3"
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Wayland

ShellRoot {
  id: root
  property var request: ({})
  property bool opened: false
  property int selected: 0
  property string assistZone: ""
  property var zoneItems: []
  property string hoverZone: ""
  readonly property var layoutZones: ["left","right","top_left","top_right","bottom_left","bottom_right"].concat(request.extendedLayouts ? ["third_left","third_center","third_right","two_thirds_left","two_thirds_right"] : [])
  function zoneName(zone) {
    var labels={left:"Left half",right:"Right half",top_left:"Upper left quarter",top_right:"Upper right quarter",bottom_left:"Lower left quarter",bottom_right:"Lower right quarter",third_left:"Left third",third_center:"Center third",third_right:"Right third",two_thirds_left:"Left two thirds",two_thirds_right:"Right two thirds"}
    return labels[zone] || String(zone).replace(/_/g," ")
  }
  function registerZone(item, zone) { zoneItems.push({item:item, zone:zone}) }
  function zoneAt(x,y) {
    for (var i = 0; i < zoneItems.length; i++) {
      var z = zoneItems[i]
      if (!z.item || !z.item.visible) continue
      var pos = z.item.mapToItem(overlay.contentItem, 0, 0)
      if (x >= pos.x && x < pos.x + z.item.width && y >= pos.y && y < pos.y + z.item.height) return z.zone
    }
    return ""
  }
  readonly property var entries: request.mode === "system" ? [
    {label:"Restore", action:"restore"}, {label:"Move", action:"move"},
    {label:"Size", action:"resize"}, {label:"Minimize", action:"minimize"},
    {label:"Maximize", action:"maximize"}, {label:"Snap layouts", action:"layouts"},
    {label:request.pinned ? "Unpin always on top" : "Pin always on top", action:"pin"},
    {label:request.reducedMotion ? "Enable animations" : "Reduce motion", action:"motion"},
    {label:"Close   Alt+F4", action:"close"}
  ] : request.mode === "assist" || request.mode === "switcher" ? (request.candidates || []).map(function(c) {
    return {label:c.title || c.class, subtitle:c.class, action:request.mode === "switcher" ? "switcher:" + c.address : "assist:" + c.address + ":" + root.assistZone}
  }) : []

  function show(payload) {
    request = JSON.parse(payload); selected = 0
    assistZone = (request.zones || [""])[0]
    if (request.mode === "switcher" && entries.length > 1) selected = request.reverse ? entries.length - 1 : 1
    opened = true; expire.restart(); keyCatcher.forceActiveFocus()
  }
  function activate(action) {
    var address = request.address
    opened = false
    if (action.indexOf("switcher:") === 0) {
      var candidate = (root.request.candidates || []).filter(function(c) { return c.address === action.slice(9) })[0]
      if(candidate) Quickshell.execDetached([Quickshell.env("HOME") + "/.local/bin/hypr-window-menu", "switcher-restore", JSON.stringify(candidate)])
      return
    }
    Quickshell.execDetached([Quickshell.env("HOME") + "/.local/bin/hypr-window-menu", "act", address, action, String(request.stableId || ""), String(request.pid || "")])
  }
  IpcHandler {
    target: "controls"
    function open(payload: string): void { root.show(payload) }
    function hide(): void { root.opened = false }
    function state(): string { return JSON.stringify({opened:root.opened, request:root.request, selected:root.selected}) }
    function cycle(step: int): void { if (root.request.mode === "switcher" && root.entries.length) root.selected = (root.selected + step + root.entries.length) % root.entries.length }
    function pick(x: int, y: int): string { return root.request.mode === "snapbar" ? root.zoneAt(x,y) : "" }
  }
  Timer { id: expire; interval: 30000; onTriggered: root.opened = false }
  Timer {
    interval:100; repeat:true
    running:root.opened && root.request.mode === "snapbar"
    onTriggered: { if (!cursorPosition.running) cursorPosition.running = true }
  }
  Process {
    id:cursorPosition
    command:["hyprctl","cursorpos","-j"]
    stdout:StdioCollector {
      onStreamFinished: {
        try {
          var cursor = JSON.parse(text)
          root.hoverZone = root.zoneAt(cursor.x - (root.request.monitorX || 0), cursor.y - (root.request.monitorY || 0))
        } catch (e) {}
      }
    }
  }
  Component.onCompleted: {
    var payload = Quickshell.env("HYPR_WINDOW_MENU")
    if (payload) show(payload)
  }
  PanelWindow {
    id: overlay
    screen: Quickshell.screens.find(function(s) { return s.name === root.request.screen }) || Quickshell.screens[0]
    visible: root.opened
    anchors { top:true; bottom:true; left:true; right:true }
    color: "transparent"
    exclusionMode: ExclusionMode.Ignore
    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.namespace: "hypr-window-controls"
    WlrLayershell.keyboardFocus: root.request.mode === "snapbar" ? WlrKeyboardFocus.None : WlrKeyboardFocus.Exclusive
    mask: Region { item: root.request.mode === "snapbar" ? null : overlay.contentItem }
    MouseArea { anchors.fill:parent; onClicked:root.opened = false }
    Rectangle {
      id: panel
      Accessible.role: Accessible.Dialog
      Accessible.name: root.request.mode === "layouts" ? "Snap layouts" : root.request.mode === "assist" ? "Snap Assist" : root.request.mode === "switcher" ? "Switch windows" : "Window controls"
      Accessible.ignored: !root.opened
      Accessible.focused: false
      x: Math.max(12, Math.min(root.request.x || 12, overlay.width - width - 12))
      y: Math.max(12, Math.min(root.request.y || 12, overlay.height - height - 12))
      width: root.request.mode === "layouts" ? 330 : 360
      height: content.implicitHeight + 24
      radius: 12
      color: "#ee24283b"
      border.color: "#565f89"
      border.width: 1
      Item {
        id: keyCatcher
        anchors.fill: parent
        Accessible.ignored: true
        focus: true
        Keys.onEscapePressed: root.opened = false
        Keys.onDownPressed: root.selected = Math.min(root.entries.length - 1, root.selected + 1)
        Keys.onUpPressed: root.selected = Math.max(0, root.selected - 1)
        Keys.onReturnPressed: {
          if (root.request.mode === "layouts") root.activate("zone:" + root.layoutZones[root.selected])
          else if (root.entries[root.selected]) root.activate(root.entries[root.selected].action)
        }
        Keys.onLeftPressed: root.selected = Math.max(0, root.selected - 1)
        Keys.onRightPressed: root.selected = Math.min(root.layoutZones.length - 1, root.selected + 1)
        Keys.onReleased: function(event) {
          if (root.request.mode === "switcher" && event.key === Qt.Key_Alt) {
            if (root.entries[root.selected]) root.activate(root.entries[root.selected].action)
            event.accepted = true
          }
        }
      }
      MouseArea { anchors.fill:parent; onClicked: {} }
      ColumnLayout {
        id: content
        anchors { top:parent.top; left:parent.left; right:parent.right; margins:12 }
        spacing:8
        Text {
          text: root.request.mode === "snapbar" ? "Drop into a region to snap" : root.request.mode === "layouts" ? "Snap layouts" : root.request.mode === "assist" ? "Choose a window for the remaining space" : root.request.mode === "switcher" ? "Switch windows · release Alt to select" : root.request.title || "Window"
          color:"#cdd6f4"; font.pixelSize:13; font.bold:true
          elide:Text.ElideRight; Layout.fillWidth:true
        }
        RowLayout {
          visible: root.request.mode === "layouts" || root.request.mode === "snapbar"
          spacing:10
          ColumnLayout {
            Text { Accessible.ignored: !visible; text:"Halves"; color:"#a9b1d6"; font.pixelSize:11 }
            Row {
              spacing:3
              Repeater {
                model:["left", "right"]
                Rectangle {
                  required property string modelData
                  Accessible.ignored: !root.opened || !visible
              Accessible.role: root.request.mode === "snapbar" ? Accessible.StaticText : Accessible.Button
                  Accessible.name: root.zoneName(modelData)
                  Accessible.focusable: root.request.mode === "layouts"
                  Accessible.focused: root.opened && root.request.mode === "layouts" && root.layoutZones[root.selected] === modelData
                  Accessible.onPressAction: if (root.opened && root.request.mode === "layouts") root.activate("zone:" + modelData)
                  Component.onCompleted: root.registerZone(this, modelData)
                  width:63; height:78; radius:3
                  color:halfMouse.containsMouse || root.hoverZone === modelData || (root.request.mode === "layouts" && root.layoutZones[root.selected] === modelData) ? "#7aa2f7" : "#414868"
                  MouseArea { id:halfMouse; anchors.fill:parent; hoverEnabled:true; onClicked:root.activate("zone:" + parent.modelData) }
                }
              }
            }
          }
          ColumnLayout {
            Text { Accessible.ignored: !visible; text:"Quarters"; color:"#a9b1d6"; font.pixelSize:11 }
            Grid {
              columns:2; spacing:3
              Repeater {
                model:["top_left", "top_right", "bottom_left", "bottom_right"]
                Rectangle {
                  required property string modelData
                  Accessible.ignored: !root.opened || !visible
              Accessible.role: root.request.mode === "snapbar" ? Accessible.StaticText : Accessible.Button
                  Accessible.name: root.zoneName(modelData)
                  Accessible.focusable: root.request.mode === "layouts"
                  Accessible.focused: root.opened && root.request.mode === "layouts" && root.layoutZones[root.selected] === modelData
                  Accessible.onPressAction: if (root.opened && root.request.mode === "layouts") root.activate("zone:" + modelData)
                  Component.onCompleted: root.registerZone(this, modelData)
                  width:63; height:37.5; radius:3
                  color:quarterMouse.containsMouse || root.hoverZone === modelData || (root.request.mode === "layouts" && root.layoutZones[root.selected] === modelData) ? "#7aa2f7" : "#414868"
                  MouseArea { id:quarterMouse; anchors.fill:parent; hoverEnabled:true; onClicked:root.activate("zone:" + parent.modelData) }
                }
              }
            }
          }
        }
        Text {
          visible:root.request.mode === "layouts"
          text:"Select a region · Esc to dismiss"; color:"#a9b1d6"; font.pixelSize:11
        }
        ColumnLayout {
          visible:(root.request.mode === "layouts" || root.request.mode === "snapbar") && !!root.request.extendedLayouts
          Text { Accessible.ignored: !visible; text:"Thirds"; color:"#a9b1d6"; font.pixelSize:11 }
          Row {
            spacing:3
            Repeater {
              model:["third_left", "third_center", "third_right"]
              Rectangle {
                required property string modelData
                Accessible.ignored: !root.opened || !visible
              Accessible.role: root.request.mode === "snapbar" ? Accessible.StaticText : Accessible.Button
                Accessible.name: root.zoneName(modelData)
                Accessible.focusable: root.request.mode === "layouts"
                Accessible.focused: root.opened && root.request.mode === "layouts" && root.layoutZones[root.selected] === modelData
                Accessible.onPressAction: if (root.opened && root.request.mode === "layouts") root.activate("zone:" + modelData)
                Component.onCompleted: root.registerZone(this, modelData)
                width:95; height:46; radius:3
                color:thirdMouse.containsMouse || root.hoverZone === modelData || (root.request.mode === "layouts" && root.layoutZones[root.selected] === modelData) ? "#7aa2f7" : "#414868"
                MouseArea { id:thirdMouse; anchors.fill:parent; hoverEnabled:true; onClicked:root.activate("zone:" + parent.modelData) }
              }
            }
          }
          Text { Accessible.ignored: !visible; text:"Wide pane + narrow pane"; color:"#a9b1d6"; font.pixelSize:11 }
          Row {
            spacing:3
            Repeater {
              model:[{zone:"two_thirds_left",width:95},{zone:"third_right",width:46},{zone:"third_left",width:46},{zone:"two_thirds_right",width:95}]
              Rectangle {
                required property var modelData
                Accessible.ignored: !root.opened || !visible
              Accessible.role: root.request.mode === "snapbar" ? Accessible.StaticText : Accessible.Button
                Accessible.name: root.zoneName(modelData.zone)
                Accessible.focusable: root.request.mode === "layouts"
                Accessible.focused: root.opened && root.request.mode === "layouts" && modelData.zone.indexOf("two_thirds_") === 0 && root.layoutZones[root.selected] === modelData.zone
                Accessible.onPressAction: if (root.opened && root.request.mode === "layouts") root.activate("zone:" + modelData.zone)
                Component.onCompleted: root.registerZone(this, modelData.zone)
                width:modelData.width; height:46; radius:3
                color:wideMouse.containsMouse || root.hoverZone === modelData.zone || (root.request.mode === "layouts" && root.layoutZones[root.selected] === modelData.zone) ? "#7aa2f7" : "#414868"
                MouseArea { id:wideMouse; anchors.fill:parent; hoverEnabled:true; onClicked:root.activate("zone:" + parent.modelData.zone) }
              }
            }
          }
        }
        Row {
          visible:root.request.mode === "assist" && (root.request.zones || []).length > 1
          spacing:4
          Repeater {
            model:root.request.zones || []
            Rectangle {
              required property string modelData
              Accessible.ignored: !root.opened || !visible
              Accessible.role: Accessible.RadioButton
              Accessible.name: root.zoneName(modelData)
              Accessible.checkable: true
              Accessible.checked: root.assistZone === modelData
              Accessible.onPressAction: if (root.opened && visible) root.assistZone = modelData
              width:78; height:28; radius:5
              color:root.assistZone === modelData ? "#7aa2f7" : "#414868"
              Text { Accessible.ignored: !visible; anchors.centerIn:parent; text:parent.modelData.replace("_", " "); color:"#cdd6f4"; font.pixelSize:10 }
              MouseArea { anchors.fill:parent; onClicked:root.assistZone = parent.modelData }
            }
          }
        }
        ScrollView {
          visible:root.entries.length > 0
          Layout.fillWidth:true
          Layout.preferredHeight:Math.min(400, rows.implicitHeight)
          contentWidth:availableWidth
          clip:true
          Column {
            id:rows
            width:parent.width
            spacing:3
            Repeater {
              model:root.entries
              Rectangle {
                required property var modelData
                required property int index
                Accessible.ignored: !root.opened || !visible
              Accessible.role: root.request.mode === "system" ? Accessible.MenuItem : Accessible.Button
                Accessible.name: modelData.label
                Accessible.description: modelData.subtitle || ""
                Accessible.focusable: true
                Accessible.focused: root.opened && index === root.selected
                Accessible.selectable: true
                Accessible.selected: index === root.selected
                Accessible.checkable: modelData.action === "pin" || modelData.action === "motion"
                Accessible.checked: modelData.action === "pin" ? !!root.request.pinned : modelData.action === "motion" && !!root.request.reducedMotion
                Accessible.onPressAction: if (root.opened && visible) root.activate(modelData.action)
                width:rows.width; height:modelData.subtitle ? 46 : 32; radius:6
                color:rowMouse.containsMouse || index === root.selected ? "#414868" : "transparent"
                Column {
                  anchors { left:parent.left; right:parent.right; verticalCenter:parent.verticalCenter; margins:10 }
                  Text { Accessible.ignored: !visible; width:parent.width; text:modelData.label; color:"#cdd6f4"; font.pixelSize:12; elide:Text.ElideRight }
                  Text { Accessible.ignored: !visible; visible:!!modelData.subtitle; width:parent.width; text:modelData.subtitle || ""; color:"#a9b1d6"; font.pixelSize:10; elide:Text.ElideRight }
                }
                MouseArea { id:rowMouse; anchors.fill:parent; hoverEnabled:true; onClicked:root.activate(parent.modelData.action) }
              }
            }
          }
        }
      }
    }
  }
}

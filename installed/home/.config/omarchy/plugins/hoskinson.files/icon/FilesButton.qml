import QtQuick
import qs.Commons
import qs.Ui

// Files launcher: a drawn, layered folder. At rest two accent sheets peek out
// of the folder; on hover they rise and the front flap tips open.
BarWidget {
  id: root
  moduleName: "hoskinson.files"

  readonly property color fg: root.bar ? root.bar.barForeground : Color.foreground
  readonly property color accent: Color.accent
  readonly property bool hot: button.tooltipHovered
  property real open: hot ? 1 : 0
  Behavior on open { NumberAnimation { duration: 260; easing.type: Easing.OutBack; easing.overshoot: 1.6 } }

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: " "                       // keeps the slot; the label itself is hidden
    labelVisible: false
    fixedWidth: icon.width + Style.spaceReal(7.5) * 2
    tooltipText: "Files  ·  right-click: Recent"
    onPressed: function(button) {
      if (!root.bar) return
      bounce.restart()
      if (button === Qt.RightButton) root.bar.run("omarchy-files coll:recent")
      else root.bar.run("omarchy-files home")
    }
  }

  Item {
    id: icon
    width: Math.round(height * 1.28)
    height: Math.round(Style.font.body * 0.96)
    anchors.centerIn: parent
    transformOrigin: Item.Bottom

    SequentialAnimation {
      id: bounce
      NumberAnimation { target: icon; property: "scale"; to: 0.82; duration: 70; easing.type: Easing.OutQuad }
      NumberAnimation { target: icon; property: "scale"; to: 1.0; duration: 260; easing.type: Easing.OutBack; easing.overshoot: 2.2 }
    }

    readonly property real u: height / 14   // design grid: 18 x 14 units

    // back panel + tab
    Rectangle {
      x: 0; y: 0
      width: 7 * icon.u; height: 3 * icon.u
      radius: 0.8 * icon.u
      color: root.fg; opacity: 0.55
    }
    Rectangle {
      x: 0; y: 1.8 * icon.u
      width: icon.width; height: icon.height - 1.8 * icon.u
      radius: 1 * icon.u
      color: root.fg; opacity: 0.55
    }

    // sheets peeking out, rising on hover
    Rectangle {
      x: 3.2 * icon.u
      y: (2.6 - 2.4 * root.open) * icon.u
      width: icon.width - 5.4 * icon.u; height: 8 * icon.u
      radius: 0.6 * icon.u
      color: Qt.darker(root.accent, 1.35)
      rotation: -5 * root.open
    }
    Rectangle {
      x: 2 * icon.u
      y: (4.0 - 1.8 * root.open) * icon.u
      width: icon.width - 5.4 * icon.u; height: 8 * icon.u
      radius: 0.6 * icon.u
      color: root.accent
      rotation: 4 * root.open
    }

    // front flap, hinged at the bottom
    Rectangle {
      id: flap
      x: 0; y: 6.6 * icon.u
      width: icon.width; height: icon.height - 6.6 * icon.u
      radius: 1 * icon.u
      color: root.fg
      transform: Rotation {
        origin.x: flap.width / 2; origin.y: flap.height
        axis { x: 1; y: 0; z: 0 }
        angle: 38 * root.open
      }
      // accent hairline along the flap's top edge
      Rectangle {
        x: 1.2 * icon.u; y: 1.3 * icon.u
        width: parent.width - 2.4 * icon.u; height: Math.max(1, 0.9 * icon.u)
        radius: height / 2
        color: root.accent; opacity: 0.35 + 0.65 * root.open
      }
    }
  }
}

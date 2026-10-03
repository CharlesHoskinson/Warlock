import QtQuick
import Quickshell
import Quickshell.Wayland
import qs.Commons
import qs.Ui

PanelWindow {
  id: root

  required property Item anchorItem
  required property QtObject bar
  property var owner: null
  property bool keyboardMode: false
  property bool reducedMotion: false
  property int margin: Style.gapsOut
  property int padding: Style.spacing.popupPadding
  property int contentWidth: Style.space(280)
  property int contentHeight: Style.space(200)
  property color borderColor: Color.popups.border
  property var borderSpec: Border.localOrSurfaceSpec("popups", "border", borderColor, Color.popups.border, Math.max(1, Style.space(2)))
  property bool open: false
  property bool centerOnBar: false
  // "click" — captures outside clicks on this surface to dismiss the menu.
  // "hover" — passive overlay; the owning widget controls open via hover.
  property string triggerMode: "click"

  readonly property var coordinatorKey: owner || root
  readonly property var anchorWindow: anchorItem ? anchorItem.QsWindow.window : null
  readonly property var popupScreen: anchorWindow ? anchorWindow.screen : null
  readonly property bool containsMouse: cardHover.hovered
  readonly property real screenW: popupScreen ? popupScreen.width : 0
  readonly property real screenH: popupScreen ? popupScreen.height : 0
  readonly property real barW: anchorWindow ? anchorWindow.width : 0
  readonly property real barH: anchorWindow ? anchorWindow.height : 0
  readonly property real availableCardWidth: screenW > 0
    ? Math.max(120, screenW - ((bar && (bar.position === "left" || bar.position === "right")) ? barW : 0) - root.margin * 2)
    : 0
  readonly property real availableCardHeight: screenH > 0
    ? Math.max(120, screenH - ((bar && (bar.position === "top" || bar.position === "bottom")) ? barH : 0) - root.margin * 2)
    : 0
  readonly property real verticalContentInset: padding * 2 + Border.top(borderSpec) + Border.bottom(borderSpec)

  function fittedContentWidth(width, cap) {
    var desired = Math.max(1, Number(width) || 1)
    var maxWidth = root.availableCardWidth > 0 ? root.availableCardWidth : desired
    if (cap !== undefined && Number(cap) > 0) maxWidth = Math.min(maxWidth, Number(cap))
    return Math.round(Math.min(desired, maxWidth))
  }

  function fittedContentHeight(implicitHeight, cap) {
    var desired = Math.max(root.verticalContentInset, (Number(implicitHeight) || 0) + root.verticalContentInset)
    var maxHeight = root.availableCardHeight > 0 ? root.availableCardHeight : desired
    if (cap !== undefined && Number(cap) > 0) maxHeight = Math.min(maxHeight, Number(cap))
    return Math.round(Math.min(desired, maxHeight))
  }

  function cappedContentHeight(height) {
    var desired = Math.max(root.padding * 2, Number(height) || root.padding * 2)
    var maxHeight = root.availableCardHeight > 0 ? root.availableCardHeight : desired
    return Math.round(Math.min(desired, maxHeight))
  }

  function close() {
    if (owner && "close" in owner) owner.close()
    else root.open = false
  }

  default property alias contentItem: contentHolder.children

  visible: open || card.opacity > 0
  color: "transparent"
  implicitWidth: screenW
  implicitHeight: screenH
  screen: popupScreen
  anchors { top: true; left: true }
  exclusiveZone: 0
  WlrLayershell.namespace: "hoskinson-taskbar-popup"
  WlrLayershell.layer: WlrLayer.Overlay
  WlrLayershell.keyboardFocus: open && keyboardMode ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None
  readonly property var popupPosition: positionPopup()
  mask: Region { item: root.open ? (root.triggerMode === "click" ? inputSurface : card) : null }
  Item {
    id: inputSurface
    anchors.fill: parent
    MouseArea {
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
      onClicked: root.close()
    }
  }

  function positionPopup() {
    if (!anchorItem || !anchorWindow || !bar) return {x: 0, y: 0}
    // Explicit dependencies keep the layer position synced with the task row.
    var anchorX = anchorItem.x, anchorY = anchorItem.y
    var pw = contentWidth, ph = contentHeight
    var x = anchorItem.width / 2 - pw / 2
    var y = anchorItem.height + margin
    var originX = bar.position === "right" ? screenW - barW : 0
    var originY = bar.position === "bottom" ? screenH - barH : 0
    if (bar.position === "bottom") y = -ph - margin
    else if (bar.position === "left") { x = anchorItem.width + margin; y = anchorItem.height / 2 - ph / 2 }
    else if (bar.position === "right") { x = -pw - margin; y = anchorItem.height / 2 - ph / 2 }
    var point = anchorWindow.contentItem.mapFromItem(anchorItem, x, y)
    if (centerOnBar) {
      if (bar.position === "top" || bar.position === "bottom") point.x = (barW - pw) / 2
      else point.y = (barH - ph) / 2
    }
    return {x: Math.round(Math.max(margin, Math.min(point.x + originX, screenW - pw - margin))),
            y: Math.round(Math.max(margin, Math.min(point.y + originY, screenH - ph - margin)))}
  }

  onOpenChanged: {
    if (!bar) return
    if (open) bar.requestPopout(coordinatorKey)
    else if (bar.activePopout === coordinatorKey) bar.releasePopout(coordinatorKey)
  }

  BorderSurface {
    id: card
    x: root.popupPosition.x
    y: root.popupPosition.y
    width: root.contentWidth
    height: root.contentHeight
    color: Color.popups.background
    borderSpec: root.borderSpec
    padding: root.padding
    radius: Style.cornerRadius
    opacity: root.open ? 1.0 : 0

    Behavior on opacity {
      NumberAnimation { duration: root.reducedMotion ? 0 : 140; easing.type: Easing.OutCubic }
    }

    MouseArea { anchors.fill: parent; acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton }
    Item {
      id: contentHolder
      anchors.fill: parent
      anchors.topMargin: card.contentTopInset
      anchors.rightMargin: card.contentRightInset
      anchors.bottomMargin: card.contentBottomInset
      anchors.leftMargin: card.contentLeftInset
    }

    HoverHandler {
      id: cardHover
    }
  }
}

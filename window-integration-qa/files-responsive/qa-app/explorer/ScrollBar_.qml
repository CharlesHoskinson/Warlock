import QtQuick
import qs.Commons

// Slim square scroll indicator.
Rectangle {
  id: sb; objectName: "ScrollBar_.sb"
  property Flickable view
  anchors { right: parent.right; rightMargin: 1 }
  width: 4
  z: 5
  y: view ? view.y + (view.height - height) * (view.contentY / Math.max(1, view.contentHeight - view.height)) : 0
  height: view ? Math.max(28, view.height * view.height / Math.max(1, view.contentHeight)) : 0
  color: Theme.alpha(Theme.fg, 0.28)
  opacity: view && (view.moving || view.flicking) ? 1 : 0.55
}

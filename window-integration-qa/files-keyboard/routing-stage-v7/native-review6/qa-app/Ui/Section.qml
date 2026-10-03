import QtQuick
import qs.Commons

// Small-caps section label with a hairline rule and an optional right-hand note.
Item {
  id: root; objectName: "Section.root"
  property string text: ""
  property string note: ""
  height: 22
  Label { id: t; objectName: "Section.t"; width: Math.min(implicitWidth, root.width); text: root.text.toUpperCase(); font.pixelSize: Theme.fsLabel; font.letterSpacing: 1.6; font.bold: true; color: Theme.fgDim; height: parent.height }
  Rectangle { x: t.width + 10; width: Math.max(0, n.x - x - 10); anchors.verticalCenter: parent.verticalCenter; height: 1; color: Theme.line }
  Label { id: n; objectName: "Section.n"; width: Math.max(0, Math.min(implicitWidth, root.width - t.width - 24)); anchors.right: parent.right; text: root.note; font.pixelSize: Theme.fsSmall; color: Theme.fgDim; height: parent.height }
}

import QtQuick
import qs.Commons

// Small-caps section label with a hairline rule and an optional right-hand note.
Item {
  id: root
  property string text: ""
  property string note: ""
  height: 22
  Label { id: t; text: root.text.toUpperCase(); font.pixelSize: Theme.fsLabel; font.letterSpacing: 1.6; font.bold: true; color: Theme.fgDim; height: parent.height }
  Rectangle { anchors { left: t.right; leftMargin: 10; right: n.left; rightMargin: root.note ? 10 : 0; verticalCenter: parent.verticalCenter } height: 1; color: Theme.line }
  Label { id: n; anchors.right: parent.right; text: root.note; font.pixelSize: Theme.fsSmall; color: Theme.fgDim; height: parent.height }
}

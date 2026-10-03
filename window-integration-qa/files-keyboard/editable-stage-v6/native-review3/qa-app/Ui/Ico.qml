import QtQuick
import qs.Commons

// Nerd Font glyph.
Text {
  Accessible.ignored: true
  property int size: 14
  font.family: Theme.font
  font.pixelSize: size
  color: Theme.fg
  horizontalAlignment: Text.AlignHCenter
  verticalAlignment: Text.AlignVCenter
  renderType: Text.NativeRendering
}

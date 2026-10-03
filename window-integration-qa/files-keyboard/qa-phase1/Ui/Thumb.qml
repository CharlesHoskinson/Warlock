import QtQuick
import qs.Commons

// Icon-or-thumbnail. Images load directly (async, downscaled); PDFs/videos go
// through thumb.sh (freedesktop cache, then ffmpegthumbnailer/pdftoppm).
Item {
  id: root; objectName:"Thumb.root"
  property var entry: null
  property int size: 32
  property bool fill: false      // cover-crop thumbnail to the whole item (grid)
  property bool wantThumb: true
  property string genPath: ""
  readonly property bool isImg: entry && Fs.isThumbImage(entry)
  readonly property bool isGen: entry && Fs.isThumbGen(entry)
  readonly property string src: !wantThumb || !entry ? "" : (isImg ? Fs.url(entry.path) : (genPath ? "file://" + genPath : ""))
  function req() {
    genPath = ""
    if (!entry || !isGen || !wantThumb) return
    var path = entry.path
    Thumbs.request(path, function (p) { if (root && root.entry && root.entry.path === path) root.genPath = p })
  }
  Component.onCompleted: req()
  onEntryChanged: req()
  onWantThumbChanged: req()

  Rectangle { anchors.fill: parent; visible: root.fill && img.status !== Image.Ready; color: Theme.bgDark }
  Ico {
    anchors.centerIn: parent
    visible: img.status !== Image.Ready
    text: root.entry ? Fs.iconFor(root.entry) : ""
    size: root.fill ? Math.min(root.width, root.height) * 0.4 : root.size * 0.72
    color: root.entry ? Fs.colorFor(root.entry) : Theme.fg
  }
  Image {
    id: img; objectName:"Thumb.img"
    anchors.fill: parent
    anchors.margins: root.fill ? 0 : 1
    source: root.src
    asynchronous: true
    cache: true
    fillMode: root.fill ? Image.PreserveAspectCrop : Image.PreserveAspectFit
    sourceSize.width: root.fill ? 512 : 96
    sourceSize.height: root.fill ? 512 : 96
    opacity: status === Image.Ready ? 1 : 0
    Behavior on opacity { NumberAnimation { duration: Theme.dMed } }
  }
}

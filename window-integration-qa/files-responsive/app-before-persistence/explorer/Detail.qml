import QtQuick
import qs.Commons
import qs.Ui

// Slide-in inspector: large preview, facts (dimensions / duration / pages via meta.sh), quick actions.
Rectangle {
  id: root
  required property var ex
  color: Theme.bgDark
  clip: true

  readonly property var entries: { ex.sel; ex.shown; return ex.selectedEntries() }
  readonly property var e: entries.length === 1 ? entries[0] : null
  readonly property bool multi: entries.length > 1
  readonly property string kind: e ? (e.isDir ? "folder" : (e.ext === "pdf" ? "pdf" : Fs.kindOf(e))) : ""
  property var meta: ({})
  property var pv: ({ count: -1, paths: [] })
  readonly property bool inResults: !!(ex.collId || ex.searchLabel)

  Rectangle { width: 1; height: parent.height; color: Theme.line }

  onEChanged: {
    meta = {}; pv = ({ count: -1, paths: [] })
    if (!e) return
    var p = e.path
    if (e.isDir) { Thumbs.preview(p, function (r) { if (root.e && root.e.path === p) root.pv = r }); return }
    if (kind === "image" || kind === "video" || kind === "pdf")
      Fs.run(["bash", Fs.script("meta.sh"), p, kind], function (out) {
        if (!root.e || root.e.path !== p) return
        var m = {}, l = out.split("\n")
        for (var i = 0; i < l.length; i++) { var kv = l[i].split("="); if (kv.length === 2) m[kv[0]] = kv[1] }
        root.meta = m
      })
  }
  function totalSize() { var s = 0; for (var i = 0; i < entries.length; i++) if (!entries[i].isDir) s += entries[i].size; return s }
  function breakdown() {
    var c = {}, out = []
    for (var i = 0; i < entries.length; i++) { var k = Fs.kindLabel(entries[i]); c[k] = (c[k] || 0) + 1 }
    for (var k2 in c) out.push(c[k2] + " " + k2.toLowerCase())
    return out.join(", ")
  }
  function dur(s) { s = Math.round(parseFloat(s)); if (!isFinite(s)) return ""; return Math.floor(s / 60) + ":" + (s % 60 < 10 ? "0" : "") + (s % 60) }

  Flickable {
    id: detailScroll
    anchors.fill: parent; anchors.leftMargin: 1
    contentHeight: col.implicitHeight + 28
    clip: true
    boundsBehavior: Flickable.StopAtBounds
    Column {
      id: col
      x: 16; y: 14
      width: parent.width - 32
      spacing: 14

      Item {
        width: parent.width; height: 24
        Label { text: "DETAILS"; height: parent.height; font.pixelSize: Theme.fsLabel; font.letterSpacing: 1.6; font.bold: true; color: Theme.fgDim }
        Btn { anchors.right: parent.right; width: 24; height: 24; icon: ""; bordered: false; onClicked: root.ex.closeDetail() }
      }

      // preview
      Rectangle {
        width: parent.width; height: root.height < 420 ? 130 : 210
        color: Theme.bgDarker
        border.width: 1; border.color: Theme.line
        clip: true
        Ico { anchors.centerIn: parent; visible: !hero.ready && !root.multi && !root.ex.lbOpen; text: root.e ? Fs.iconFor(root.e) : ""; size: 60
          color: root.e ? Theme.alpha(Fs.colorFor(root.e), 0.6) : Theme.accent }
        Image {
          id: hero
          readonly property bool ready: status === Image.Ready
          anchors.fill: parent; anchors.margins: 1
          visible: root.kind === "image"
          source: root.kind === "image" ? Fs.url(root.e.path) : ""
          asynchronous: true; fillMode: Image.PreserveAspectFit; smooth: true
          sourceSize: Qt.size(720, 720)
          opacity: status === Image.Ready ? 1 : 0
          Behavior on opacity { NumberAnimation { duration: 240 } }
        }
        Thumb { anchors.fill: parent; visible: root.kind === "video" || root.kind === "pdf"; wantThumb: visible; entry: visible ? root.e : null; size: 60 }
        Rectangle { visible: root.kind === "video"; anchors.centerIn: parent; width: 44; height: 44; color: Theme.alpha(Theme.bgDarker, 0.7); border.width: 1; border.color: Theme.fgBright
          Ico { anchors.centerIn: parent; text: ""; size: 16; color: Theme.fgBright } }
        // folder mosaic
        Item {
          anchors.fill: parent; visible: root.kind === "folder"
          readonly property var paths: root.pv.paths
          Ico { visible: parent.paths.length === 0; anchors.centerIn: parent; text: ""; size: 72; color: Theme.accent }
          Grid {
            visible: parent.paths.length > 0
            anchors.fill: parent; columns: 2; spacing: 1
            Repeater {
              model: parent.parent.paths.length
              delegate: Thumb { width: parent.width / 2 - 0.5; height: parent.height / 2 - 0.5; entry: Fs.entryOf(root.pv.paths[index]); fill: true; size: 30 }
            }
          }
        }
        // multi: fanned stack
        Item {
          anchors.fill: parent; visible: root.multi
          Repeater {
            model: root.multi ? Math.min(3, root.entries.length) : 0
            delegate: Rectangle {
              readonly property var it: root.entries[2 - index < root.entries.length ? 2 - index : 0]
              width: 120; height: 120
              anchors.centerIn: parent
              anchors.horizontalCenterOffset: (index - 1) * 34
              anchors.verticalCenterOffset: (index - 1) * 6
              rotation: (index - 1) * 8
              color: Theme.bgLight; border.width: 2; border.color: Theme.bg
              Thumb { anchors.fill: parent; anchors.margins: 2; entry: parent.it; fill: Fs.isMedia(parent.it); size: 44 }
            }
          }
        }
      }

      Column {
        width: parent.width; spacing: 4
        Label {
          width: parent.width; height: implicitHeight; wrapMode: Text.WrapAnywhere; maximumLineCount: 3; elide: Text.ElideRight
          text: root.e ? root.e.name : (root.multi ? root.entries.length + " items selected" : "")
          font.pixelSize: 15; font.bold: true; color: Theme.fgBright
        }
        Label {
          width: parent.width; height: 16
          text: root.e ? Fs.kindLabel(root.e) + (root.e.isLink ? "  ·  link" : "") : (root.multi ? root.breakdown() : "")
          font.pixelSize: Theme.fsBody; color: Theme.accent
        }
      }

      Rectangle { width: parent.width; height: 1; color: Theme.line }

      Column {
        width: parent.width; spacing: 9
        Repeater {
          model: {
            var r = []
            if (root.e) {
              var x = root.e
              if (x.isDir) r.push(["Contains", root.pv.count >= 0 ? root.pv.count + " items" : "…"])
              else r.push(["Size", Fs.size(x.size)])
              if (root.meta.dims) r.push(["Dimensions", root.meta.dims.replace("x", " × ")])
              if (root.meta.width) r.push(["Dimensions", root.meta.width + " × " + root.meta.height])
              if (root.meta.duration) r.push(["Duration", root.dur(root.meta.duration)])
              if (root.meta.pages) r.push(["Pages", root.meta.pages])
              r.push(["Modified", Fs.longDate(x.mtime)])
              r.push(["Location", Fs.tilde(Fs.parent(x.path))])
            } else if (root.multi) {
              r.push(["Total size", Fs.size(root.totalSize())])
              r.push(["Selected", root.entries.length + " items"])
            }
            return r
          }
          delegate: Row {
            required property var modelData
            width: col.width; spacing: 10
            Label { width: 78; height: 16; text: modelData[0]; font.pixelSize: Theme.fsSmall; color: Theme.fgDim }
            Label { width: parent.width - 88; height: implicitHeight; text: modelData[1]; wrapMode: Text.WrapAnywhere; elide: Text.ElideNone; verticalAlignment: Text.AlignTop; color: Theme.fg }
          }
        }
      }

      Rectangle { width: parent.width; height: 1; color: Theme.line }

      Grid {
        width: parent.width; columns: 2; spacing: 8
        readonly property real bw: (width - 8) / 2
        Btn { width: parent.bw; height: 32; primary: true; icon: ""; text: "Open"; onClicked: root.ex.openSelection() }
        Btn { width: parent.bw; height: 32; icon: root.inResults ? "" : ""; text: root.inResults ? "Show in folder" : "Preview"; enabled2: root.e !== null
          onClicked: root.inResults ? root.ex.revealEntry(root.e) : root.ex.openLightbox() }
        Btn { width: parent.bw; height: 32; icon: ""; text: "Copy path"; onClicked: root.ex.copyPathText() }
        Btn { width: parent.bw; height: 32; icon: ""; text: "Rename"; enabled2: root.e !== null; onClicked: root.ex.renameSel() }
        Btn { width: parent.bw; height: 32; icon: ""; text: "Trash"; tint: Theme.red; onClicked: root.ex.trashSel() }
      }
    }
  }
  ScrollBar_ { view: detailScroll; visible: detailScroll.contentHeight > detailScroll.height }
}

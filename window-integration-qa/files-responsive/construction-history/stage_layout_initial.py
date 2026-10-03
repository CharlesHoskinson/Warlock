from pathlib import Path
P=Path(__file__).parent/'app'
def edit(path,old,new):
 p=P/path;s=p.read_text();assert old in s,(path,old[:80]);p.write_text(s.replace(old,new,1))
p=P/'explorer/Explorer.qml';s=p.read_text().replace('minimumSize: Qt.size(900, 560)','minimumSize: Qt.size(330, 320)')
s=s.replace('property bool detailOpen: true','''property bool detailOpen: true
  property bool sidebarRequested: false
  property bool detailOverlayRequested: false
  readonly property bool narrowToolbar: content.width < 600
  readonly property bool compactToolbar: content.width < 1000
  readonly property bool sidebarDocked: content.width >= 900
  readonly property bool detailDocked: main.width >= 650
  onSidebarDockedChanged: sidebarRequested = false
  onDetailDockedChanged: detailOverlayRequested = false
  onNselChanged: if (!nsel) detailOverlayRequested = false''')
s=s.replace('function go(target, fromHistory) {','function go(target, fromHistory) {\n    sidebarRequested = false; detailOverlayRequested = false')
s=s.replace('function toggleDetail() { detailOpen = !detailOpen }','''function toggleDetail() {
    if (detailDocked) detailOpen = !detailOpen
    else { detailOverlayRequested = !detailOverlayRequested; if (detailOverlayRequested) detailOpen = true }
  }
  function closeDetail() { detailOpen = false; detailOverlayRequested = false }''')
s=s.replace('case "detail": detailOpen = arg ? arg === "on" : !detailOpen; return String(detailOpen)','case "detail": detailOpen = arg ? arg === "on" : !detailOpen; detailOverlayRequested = detailOpen && !detailDocked; return String(detailOpen)')
s=s.replace('width: parent.width; height: 52','width: parent.width; height: win.narrowToolbar ? 128 : (win.compactToolbar ? 92 : 52)',1)
s=s.replace('x: 14; anchors.verticalCenter: parent.verticalCenter; spacing: 4','x: 14; y: 11; spacing: 4',1)
s=s.replace('Btn { icon: ""; active:', 'Btn { visible: !win.sidebarDocked; icon: ""; tip: "Collections and tree (Ctrl+B)"; active: win.sidebarRequested; onClicked: win.sidebarRequested = !win.sidebarRequested }\n        Btn { icon: ""; active:',1)
s=s.replace('anchors { right: parent.right; rightMargin: 14; verticalCenter: parent.verticalCenter }\n        spacing: 4','anchors { right: parent.right; rightMargin: 14 }; y: 11\n        spacing: 4',1)
s=s.replace('active: win.detailOpen && win.view === "folder"','active: (win.detailDocked ? win.detailOpen : win.detailOverlayRequested) && win.view === "folder"',1)
# Keep hidden/pin actions, move their existing Row into the search row below600.
a=s.index('        Btn { icon: win.showHidden ?');b=s.index('\n      }\n      Rectangle {\n        id: filterBox',a)
extras=s[a:b];s=s[:a]+s[b:]
s=s.replace('\n      Rectangle {\n        id: filterBox','''
      Row {
        id: extraTools
        x: win.narrowToolbar ? toolbar.width - width - 14 : tools.x - width - 4
        y: win.narrowToolbar ? 87 : 11; spacing: 4
'''+extras+'''
      }
      Rectangle {
        id: filterBox''',1)
# Wide controls extras before tools, preserving row order while no overlaps.
s=s.replace('anchors { right: tools.left; rightMargin: 12; verticalCenter: parent.verticalCenter }\n        width: filterInput.activeFocus || win.filter.length ? 250 : 190; height: 32','''x: win.narrowToolbar ? 14 : (win.compactToolbar ? toolbar.width - width - 14 : extraTools.x - width - 12)
        y: win.narrowToolbar ? 87 : (win.compactToolbar ? 49 : 10)
        width: win.narrowToolbar ? toolbar.width - extraTools.width - 40 : (win.compactToolbar ? Math.min(250, (toolbar.width - 40) / 2) : (filterInput.activeFocus || win.filter.length ? 250 : 190)); height: 32''')
s=s.replace('Label { visible: filterInput.text.length === 0; x: 30; height: parent.height;','Label { visible: filterInput.text.length === 0; x: 30; width: parent.width - 38; height: parent.height;',1)
s=s.replace('anchors { left: nav.right; leftMargin: 14; right: filterBox.left; rightMargin: 12; verticalCenter: parent.verticalCenter }','''x: win.compactToolbar ? 14 : nav.x + nav.width + 14
        y: win.compactToolbar ? 49 : 10
        width: win.narrowToolbar ? toolbar.width - 28 : filterBox.x - x - 12
        popupMaxHeight: content.height - (toolbar.y + y + height) - status.height - 8''',1)
s=s.replace('y: toolbar.height; width: 244; height: parent.height - toolbar.height - status.height','''y: toolbar.height; width: Math.min(244, content.width - 24); height: parent.height - toolbar.height - status.height
      z: win.sidebarDocked ? 0 : 30
      visible: win.sidebarDocked || win.sidebarRequested''',1)
# Wrap sidebar contents in a scroll viewport. Inner item leaves tree >=120 at short height.
a=s.index('      Label { x: 16; y: 14; height: 16; text: "COLLECTIONS"');b=s.index('\n    }\n\n    // ---- main area',a)
s=s[:a]+'''      Flickable {
        anchors.fill: parent; contentWidth: width; contentHeight: sideBody.height
        clip: true; boundsBehavior: Flickable.StopAtBounds
        Item { id: sideBody; width: parent.width; height: Math.max(side.height, treeHead.y + treeHead.height + 126)
'''+s[a:b]+'''\n        }
      }'''+s[b:]
s=s.replace('x: side.width; y: toolbar.height; width: parent.width - side.width; height: side.height','x: win.sidebarDocked ? side.width : 0; y: toolbar.height; width: parent.width - x; height: side.height',1)
s=s.replace('width: main.width - (win.view === "folder" ? detail.width * detail.prog : 0)','width: main.width - (win.detailDocked && win.view === "folder" ? detail.width * detail.prog : 0)',1)
s=s.replace('      Detail {\n        id: detail','''      Rectangle {
        anchors.fill: parent; z: 1
        visible: !win.detailDocked && detail.visible
        color: Theme.alpha(Theme.bgDarker, 0.55)
        MouseArea { anchors.fill: parent; onClicked: win.detailOverlayRequested = false }
      }
      Detail {
        id: detail; z: 2''',1)
s=s.replace('width: 300; height: parent.height','width: Math.min(300, main.width - 20); height: parent.height',1)
s=s.replace('(win.detailOpen && win.nsel > 0 && win.view === "folder") ? 1 : 0','(win.detailOpen && (win.detailDocked || win.detailOverlayRequested) && win.nsel > 0 && win.view === "folder") ? 1 : 0',1)
s=s.replace('    // ---- main area','''    Rectangle {
      x: 0; y: toolbar.height; width: content.width; height: side.height; z: 25
      visible: !win.sidebarDocked && win.sidebarRequested
      color: Theme.alpha(Theme.bgDarker, 0.55)
      MouseArea { anchors.fill: parent; onClicked: win.sidebarRequested = false }
    }

    // ---- main area''',1)
s=s.replace('x: 14; height: parent.height; spacing: 14\n        Label { height: parent.height;','x: 14; height: parent.height; spacing: 14\n        Label { width: Math.max(100, status.width - statusExtra.width - 42); height: parent.height;',1)
s=s.replace('visible: win.filter.length > 0 && win.view === "folder"','visible: false /* filter is shown in its bounded toolbar field */',1)
s=s.replace('visible: win.clip.paths.length > 0; height: parent.height;','visible: false /* clipboard remains available through shortcuts and menus */; height: parent.height;',1)
s=s.replace('anchors.right: parent.right; anchors.rightMargin: 14; height: parent.height; spacing: 14','id: statusExtra\n        anchors.right: parent.right; anchors.rightMargin: 14; height: parent.height; spacing: 14',1)
s=s.replace('visible: win.view === "folder" && win.hiddenCount > 0','visible: status.width >= 900 && win.view === "folder" && win.hiddenCount > 0',1)
s=s.replace('Label { visible: win.view === "folder"; height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim\n          text: "sort','Label { visible: status.width >= 700 && win.view === "folder"; height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim\n          text: "sort',1)
s=s.replace('Label { height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim\n          text: Fs.size','Label { visible: status.width >= 600; height: parent.height; font.pixelSize: Theme.fsSmall + 1; color: Theme.fgDim\n          text: Fs.size',1)
s=s.replace('width: toastText.implicitWidth + 32; height: 34','width: Math.min(parent.width - 24, toastText.implicitWidth + 32); height: 34',1)
s=s.replace('Label { id: toastText; anchors.centerIn: parent; color: Theme.fgBright }','Label { id: toastText; anchors.centerIn: parent; width: Math.min(implicitWidth, parent.width - 32); color: Theme.fgBright }',1)
s=s.replace('if (e.key === Qt.Key_I && ctrl)', 'if (e.key === Qt.Key_B && ctrl) { if (!win.sidebarDocked) win.sidebarRequested = !win.sidebarRequested; e.accepted = true; return }\n      if (e.key === Qt.Key_I && ctrl)',1)
s=s.replace('if (win.filter.length) win.filter = ""\n        else if (win.nsel)', 'if (win.sidebarRequested) win.sidebarRequested = false\n        else if (win.detailOverlayRequested) win.detailOverlayRequested = false\n        else if (win.filter.length) win.filter = ""\n        else if (win.nsel)',1)
p.write_text(s)
# File header and adaptive list columns.
edit('explorer/FileArea.qml','readonly property int pad: 20','readonly property int pad: width < 560 ? 14 : 20\n  readonly property bool compactHeader: width < 760')
edit('explorer/FileArea.qml','width: parent.width; height: 62','width: parent.width; height: area.compactHeader ? 78 : 62')
edit('explorer/FileArea.qml','x: area.pad; anchors.verticalCenter: parent.verticalCenter; spacing: 2','x: area.pad; y: area.compactHeader ? 5 : 10; width: area.compactHeader ? parent.width - 2 * area.pad : Math.max(100, parent.width - headerActions.width - 3 * area.pad); spacing: 2')
edit('explorer/FileArea.qml','Label { text: area.ex.areaTitle;','Label { width: parent.width; text: area.ex.areaTitle;')
edit('explorer/FileArea.qml','Label { text: area.ex.areaSub;','Label { width: parent.width; text: area.ex.areaSub;')
edit('explorer/FileArea.qml','anchors { right: parent.right; rightMargin: area.pad; verticalCenter: parent.verticalCenter }\n      spacing: 10','id: headerActions\n      x: area.compactHeader ? area.pad : parent.width - width - area.pad\n      y: area.compactHeader ? 43 : 16\n      spacing: 10')
p=P/'explorer/FileArea.qml';s=p.read_text().replace('visible: area.grid;','visible: area.grid && area.width >= 560;',3).replace('readonly property int wDate: 140','readonly property int wDate: width >= 650 ? 140 : 0').replace('readonly property int wKind: 72','readonly property int wKind: width >= 480 ? 72 : 0')
s=s.replace('height: header.height\n        x:', 'height: header.height\n        visible: modelData.key === "name" || modelData.w > 0\n        x:',1)
s=s.replace('Label { x: parent.width - (area.wDate + area.wSize + area.wKind + 16);','Label { visible: area.wDate > 0; x: parent.width - (area.wDate + area.wSize + area.wKind + 16);',1)
s=s.replace('Label { x: parent.width - (area.wKind + 16) + 12; width: area.wKind - 12;','Label { visible: area.wKind > 0; x: parent.width - (area.wKind + 16) + 12; width: Math.max(0, area.wKind - 12);',1)
s=s.replace('anchors.centerIn: parent; spacing: 10','anchors.centerIn: parent; width: parent.width - 28; spacing: 10',1).replace('Label { anchors.horizontalCenter: parent.horizontalCenter; color: Theme.fgDim','Label { width: parent.width; horizontalAlignment: Text.AlignHCenter; color: Theme.fgDim',1)
p.write_text(s)
# Compact home sections retain all existing callbacks.
p=P/'explorer/Dashboard.qml';s=p.read_text().replace('readonly property int pad: 28','readonly property bool compact: width < 720\n  readonly property int pad: compact ? 14 : 28')
s=s.replace('x: root.pad; y: 22\n      spacing: 2','x: root.pad; y: 16; width: root.compact ? root.cw : Math.max(150, root.cw - filters.width - 20)\n      spacing: 2',1).replace('Label { text: "Home";','Label { width: parent.width; text: "Home";',1).replace('Label { text: (envq.user)','Label { width: parent.width; text: (envq.user)',1)
s=s.replace('    Row {\n      anchors { right: parent.right; rightMargin: root.pad; verticalCenter: head.verticalCenter }\n      spacing: 6','''    Flow {
      id: filters
      x: root.compact ? root.pad : fl.width - width - root.pad
      y: root.compact ? head.y + head.height + 12 : head.y + 10
      width: root.compact ? root.cw : implicitWidth
      spacing: 6''',1)
# Flow's implicitWidth isn't natural row length; choose sum known chip widths via childrenRect? Wide740 overlaps head; use breakpoint1000 filters wrap too.
s=s.replace('readonly property bool compact: width < 720','readonly property bool compact: width < 900',1)
s=s.replace('width: root.compact ? root.cw : implicitWidth','width: root.compact ? root.cw : 690',1)
s=s.replace('x: root.pad; y: 86; width: root.cw','x: root.pad; y: Math.max(head.y + head.height, filters.y + filters.height) + 20; width: root.cw',1)
s=s.replace('readonly property real leftW: Math.round(width * 0.60)','readonly property real leftW: root.compact ? width : Math.round(width * 0.60)',1).replace('readonly property real rightW: width - leftW - 16','readonly property real rightW: root.compact ? width : width - leftW - 16',1).replace('height: 32 + 208','height: root.compact ? 504 : 240',1)
s=s.replace('Section { x: hero.leftW + 16; width: hero.rightW; text: "Smart collections" }','Section { x: root.compact ? 0 : hero.leftW + 16; y: root.compact ? 264 : 0; width: hero.rightW; text: "Smart collections" }',1)
s=s.replace('x: hero.leftW + 16; y: 32; width: hero.rightW; spacing: 8','x: root.compact ? 0 : hero.leftW + 16; y: root.compact ? 296 : 32; width: hero.rightW; spacing: 8',1)
s=s.replace('Label { x: 38; width: parent.width - 38 - 50;','Label { x: 38; width: Math.max(25, parent.width - 38 - 40);',1)
s=s.replace('Math.max(2, Math.floor((pins.width + pins.spacing) / 150))','Math.max(1, Math.floor((pins.width + pins.spacing) / 150))',1)
s=s.replace('width: root.cw; height: 330','width: root.cw; height: root.compact ? 682 : 330',1).replace('readonly property real leftW: Math.round(width * 0.56)','readonly property real leftW: root.compact ? width : Math.round(width * 0.56)',1).replace('width: lower.leftW - 14; height: parent.height','width: root.compact ? lower.width : lower.leftW - 14; height: 330',1)
s=s.replace('x: lower.leftW; width: parent.width - lower.leftW; height: parent.height','x: root.compact ? 0 : lower.leftW; y: root.compact ? 352 : 0; width: root.compact ? lower.width : parent.width - lower.leftW; height: 330',1)
p.write_text(s)
edit('explorer/Detail.qml','onClicked: root.ex.detailOpen = false','onClicked: root.ex.closeDetail()')
edit('explorer/Detail.qml','width: parent.width; height: 210','width: parent.width; height: root.height < 420 ? 130 : 210')
# Fixed-width button labels must not protrude from action cells.
edit('Ui/Btn.qml','implicitWidth: text.length ? row.implicitWidth + 20 : 30','implicitWidth: text.length ? caption.implicitWidth + (icon.length ? 19 : 0) + 20 : 30')
edit('Ui/Btn.qml','spacing: 6\n    Ico','width: Math.min(implicitWidth, root.width - 20)\n    spacing: 6\n    Ico')
edit('Ui/Btn.qml','Label { visible: root.text.length; text: root.text;','Label { id: caption; visible: root.text.length; width: Math.max(0, row.width - (root.icon.length ? 19 : 0)); text: root.text;')
# Section note gives title priority, with bounded rule.
p=P/'Ui/Section.qml';s=p.read_text().replace('Label { id: t; text:', 'Label { id: t; width: Math.min(implicitWidth, root.width); text:',1).replace('Label { id: n; anchors.right: parent.right; text:', 'Label { id: n; width: Math.max(0, Math.min(implicitWidth, root.width - t.width - 24)); anchors.right: parent.right; text:',1)
s=s.replace('Rectangle { anchors { left: t.right; leftMargin: 10; right: n.left; rightMargin: root.note ? 10 : 0; verticalCenter: parent.verticalCenter } height: 1;', 'Rectangle { x: t.width + 10; width: Math.max(0, n.x - x - 10); anchors.verticalCenter: parent.verticalCenter; height: 1;',1);p.write_text(s)
# Viewport-bounded prompt and scrolling content preserve existing accept/cancel.
edit('Ui/Prompt.qml','width: 460; height: body.implicitHeight + 36','width: Math.min(460, root.width - 24); height: Math.min(root.height - 24, body.implicitHeight + 36)')
edit('Ui/Prompt.qml','    Column {\n      id: body\n      x: 18; y: 18; width: parent.width - 36; spacing: 12','''    Flickable {
      anchors.fill: parent; anchors.margins: 18; clip: true
      contentWidth: width; contentHeight: body.implicitHeight; boundsBehavior: Flickable.StopAtBounds
    Column {
      id: body
      width: parent.width; spacing: 12''')
p=P/'Ui/Prompt.qml';s=p.read_text();s=s.rsplit('    }\n  }\n}',1)[0]+'    }\n    }\n  }\n}\n';p.write_text(s)
# Scroll menus and track keyboard highlight within viewport.
edit('Ui/ContextMenu.qml','items = its; px = x; py = y; visible = true; hi = -1','items = its; px = x; py = y; visible = true; hi = -1; menuScroll.contentY = 0')
edit('Ui/ContextMenu.qml','property int hi: -1','''property int hi: -1
  onHiChanged: {
    var y = 0
    for (var i = 0; i < hi; i++) y += items[i].sep ? 9 : 28
    if (hi >= 0) menuScroll.contentY = Math.max(0, Math.min(menuScroll.contentHeight - menuScroll.height, y < menuScroll.contentY ? y : Math.max(menuScroll.contentY, y + 28 - menuScroll.height)))
  }''')
edit('Ui/ContextMenu.qml','width: 232\n    height: col.implicitHeight + 8','width: Math.min(280, root.width - 8)\n    height: Math.min(root.height - 8, col.implicitHeight + 8)')
edit('Ui/ContextMenu.qml','    Column {\n      id: col\n      x: 4; y: 4; width: parent.width - 8','''    Flickable {
      id: menuScroll; anchors.fill: parent; anchors.margins: 4; clip: true
      contentWidth: width; contentHeight: col.implicitHeight; boundsBehavior: Flickable.StopAtBounds
    Column {
      id: col
      width: parent.width''')
p=P/'Ui/ContextMenu.qml';s=p.read_text();s=s.rsplit('    }\n  }\n}',1)[0]+'    }\n    }\n  }\n}\n';p.write_text(s)
# Completions: scrolling full model keeps active candidate visible at short heights.
edit('explorer/PathBar.qml','property bool editing: false','property bool editing: false\n  property real popupMaxHeight: 216')
edit('explorer/PathBar.qml','height: Math.min(root.cands.length, 8) * 26 + 8','height: Math.min(Math.min(root.cands.length, 8) * 26 + 8, Math.max(34, root.popupMaxHeight))\n    clip: true')
edit('explorer/PathBar.qml','    Column {\n      x: 4; y: 4; width: parent.width - 8','''    Flickable {
      id: completions; anchors.fill: parent; anchors.margins: 4
      contentWidth: width; contentHeight: root.cands.length * 26; clip: true; boundsBehavior: Flickable.StopAtBounds
      Connections { target: root; function onCandIdxChanged() { if (root.candIdx >= 0) completions.contentY = Math.max(0, Math.min(completions.contentHeight - completions.height, root.candIdx * 26)) } }
    Column {
      width: parent.width''')
edit('explorer/PathBar.qml','model: root.cands.slice(0, 8)','model: root.cands')
p=P/'explorer/PathBar.qml';s=p.read_text().replace('Label { text: modelData; color: Theme.fgBright;', 'Label { width: parent.parent.width - 44; text: modelData; color: Theme.fgBright;',1)
a=s.index('    Label { visible: root.cands.length > 8;');s=s[:a]+'    }\n  }\n}\n';p.write_text(s)
# Preview bars retain controls and bounded text.
p=P/'explorer/Lightbox.qml';s=p.read_text().replace('leftMargin: 90; rightMargin: 90','leftMargin: root.width < 600 ? 62 : 90; rightMargin: root.width < 600 ? 62 : 90',1)
s=s.replace('Row { x: 24; anchors.verticalCenter: parent.verticalCenter; spacing: 12','Row { x: 24; width: parent.width - 98; anchors.verticalCenter: parent.verticalCenter; spacing: 12',1).replace('Label { text: root.e ? root.e.name : "";', 'Label { width: parent.width - 28; text: root.e ? root.e.name : "";',1)
s=s.replace('Label { x: 24; height: parent.height; color: Theme.fgDim','Label { x: 24; y: 0; width: parent.width - 48; height: 24; color: Theme.fgDim',1)
s=s.replace('Label { anchors.centerIn: parent; text: (root.ex.lbIdx + 1)', 'Label { x: 24; y: 30; text: (root.ex.lbIdx + 1)',1).replace('height: parent.height; color: Theme.fgDim; text: "←  →  browse    Enter  open    Space / Esc  close"','y: 30; width: Math.max(0, parent.width - 130); color: Theme.fgDim; text: root.width < 600 ? "← → browse · Esc close" : "←  →  browse    Enter  open    Space / Esc  close"',1)
p.write_text(s)
print('Staged GUI only')

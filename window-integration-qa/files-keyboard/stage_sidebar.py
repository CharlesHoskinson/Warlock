from pathlib import Path
P=Path(__file__).resolve().parent/'app'
def edit(path,old,new):
 p=P/path;s=p.read_text();assert old in s,(path,old[:70]);p.write_text(s.replace(old,new,1))
edit('explorer/Explorer.qml','  function focusMain() { keys.forceActiveFocus() }', '''  function focusMain() { keys.forceActiveFocus() }
  function ensureSidebarItem(item) {
    var y=item.mapToItem(sideBody,0,0).y
    sidebarScroll.contentY=Math.max(0,Math.min(sidebarScroll.contentHeight-sidebarScroll.height,
      y<sidebarScroll.contentY ? y : Math.max(sidebarScroll.contentY,y+item.height-sidebarScroll.height)))
  }
  function toggleSidebar() {
    sidebarRequested=!sidebarRequested
    if(sidebarRequested) Qt.callLater(function(){var first=collRepeater.itemAt(0);if(first) first.forceActiveFocus()})
    else focusMain()
  }''')
edit('explorer/Explorer.qml','onClicked: win.sidebarRequested = !win.sidebarRequested','onClicked: win.toggleSidebar()')
edit('explorer/Explorer.qml','if (!win.sidebarDocked) win.sidebarRequested = !win.sidebarRequested','if (!win.sidebarDocked) win.toggleSidebar()')
edit('explorer/Explorer.qml','if (win.sidebarRequested) win.sidebarRequested = false','if (win.sidebarRequested) { win.sidebarRequested = false; win.focusMain() }')
edit('explorer/Explorer.qml','else if (win.detailOverlayRequested) win.detailOverlayRequested = false','else if (win.detailOverlayRequested) { win.detailOverlayRequested = false; win.focusMain() }')
edit('explorer/Explorer.qml','          model: Data.collections\n','          id: collRepeater\n          model: Data.collections\n')
edit('explorer/Explorer.qml','            id: cr\n','''            id: cr
            activeFocusOnTab: true
            Accessible.role: Accessible.Button
            Accessible.name: modelData.name
            Accessible.description: "Collection, " + Data.collCount(modelData.id) + " items"
            Accessible.onPressAction: { var id=modelData.id; win.go("coll:"+id) }
            Keys.onPressed: (e) => { if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space) { if(!e.isAutoRepeat) win.go("coll:"+modelData.id); e.accepted=true } }
            onActiveFocusChanged: if(activeFocus) win.ensureSidebarItem(cr)
            Rectangle { anchors.fill:parent; color:"transparent"; border.width:cr.activeFocus ? 2 : 0; border.color:Theme.accent; z:2 }
''')
edit('explorer/Tree.qml','  function indexOfPath(p)', '''  function focusRow(i) {
    if(i<0 || i>=tm.count) return
    list.currentIndex=i; list.positionViewAtIndex(i,ListView.Contain)
    Qt.callLater(function(){var row=list.itemAtIndex(i);if(row) row.forceActiveFocus()})
  }
  function indexOfPath(p)''')
edit('explorer/Tree.qml','    id: list\n','    id: list\n    Accessible.role: Accessible.Tree\n    Accessible.name: "Folders"\n    currentIndex: 0\n')
edit('explorer/Tree.qml','      id: row\n','''      id: row
      activeFocusOnTab: index===list.currentIndex
      Accessible.role: Accessible.TreeItem
      Accessible.name: name
      Accessible.description: path + (expanded ? ", expanded" : ", collapsed")
      Accessible.selectable: true
      Accessible.selected: isCur
      Accessible.onPressAction: { var p=path; root_.navigate(p) }
      onActiveFocusChanged: if(activeFocus) { list.currentIndex=index;list.positionViewAtIndex(index,ListView.Contain) }
      Rectangle {anchors.fill:parent;color:"transparent";border.width:row.activeFocus ? 2 : 0;border.color:Theme.accent;z:2}
      Keys.onPressed: (e) => {
        if(e.key===Qt.Key_Up) root_.focusRow(index-1)
        else if(e.key===Qt.Key_Down) root_.focusRow(index+1)
        else if(e.key===Qt.Key_Home) root_.focusRow(0)
        else if(e.key===Qt.Key_End) root_.focusRow(tm.count-1)
        else if(e.key===Qt.Key_Right) { if(!expanded) root_.expand(index,null);else root_.focusRow(index+1) }
        else if(e.key===Qt.Key_Left) {
          if(expanded) root_.collapse(index)
          else { for(var i=index-1;i>=0;i--) if(tm.get(i).depth<depth) {root_.focusRow(i);break} }
        }
        else if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space) { if(!e.isAutoRepeat) root_.navigate(path) }
        else return
        e.accepted=true
      }
''')
edit('explorer/Tree.qml','        id: chev\n','''        id: chev
        Accessible.role: Accessible.Button
        Accessible.name: (row.expanded ? "Collapse " : "Expand ") + row.name
        Accessible.onPressAction: { var i=root_.indexOfPath(row.path); if(i>=0) root_.toggle(i) }
''')

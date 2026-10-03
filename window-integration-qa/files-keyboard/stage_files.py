from pathlib import Path
P=Path(__file__).resolve().parent/'app'
def edit(path,old,new):
 p=P/path;s=p.read_text();assert old in s,(path,old[:70]);p.write_text(s.replace(old,new,1))
edit('Ui/ContextMenu.qml','    id: card\n','    id: card\n    Accessible.role: Accessible.Menu\n    Accessible.name: "Actions"\n')
edit('Ui/ContextMenu.qml','    if (hi >= 0) menuScroll.contentY =','    if (hi >= 0) Qt.callLater(function(){var row=menuRows.itemAt(hi);if(row && !row.modelData.disabled && !row.modelData.sep) row.forceActiveFocus()})\n    if (hi >= 0) menuScroll.contentY =')
edit('Ui/ContextMenu.qml','        model: root.items\n','        id: menuRows\n        model: root.items\n')
edit('Ui/ContextMenu.qml','        delegate: Item {\n','''        delegate: Item {
          id: menuRow
          enabled: !modelData.disabled && !modelData.sep
          Accessible.role: Accessible.MenuItem
          Accessible.name: modelData.label || ""
          Accessible.ignored: !!modelData.sep
          Accessible.onPressAction: { var action=modelData.action; root.close();root.chosen(action) }
          onActiveFocusChanged: if(activeFocus && root.hi!==index) root.hi=index
''')
edit('Ui/ContextMenu.qml','root.close(); root.chosen(root.items[root.hi].action)','var action=root.items[root.hi].action; root.close(); root.chosen(action)')
edit('Ui/ContextMenu.qml','root.close(); root.chosen(modelData.action)','var action=modelData.action; root.close(); root.chosen(action)')
edit('explorer/FileArea.qml','  function scrollPosition()', '''  function focusEntry(i) {
    if(i<0 || i>=ex.shown.length) return
    var path=ex.shown[i].path
    ensure(i)
    Qt.callLater(function(){
      if(i>=ex.shown.length || ex.shown[i].path!==path) return
      if(grid) {
        gridList.forceLayout()
        for(var r=0;r<rows.length;r++) if(rows[r].idx && rows[r].idx.indexOf(i)>=0) {
          var row=gridList.itemAtIndex(r);if(row) row.focusEntry(i);break
        }
      } else { listView.forceLayout();var item=listView.itemAtIndex(i);if(item) item.forceActiveFocus() }
    })
  }
  function scrollPosition()''')
edit('explorer/FileArea.qml','        required property var modelData\n        height: header.height','''        required property var modelData
        activeFocusOnTab: true
        Accessible.role: Accessible.Button
        Accessible.name: "Sort by " + modelData.key
        Accessible.onPressAction: area.ex.setSort(modelData.key)
        Keys.onPressed: (e) => { if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space) {if(!e.isAutoRepeat) area.ex.setSort(modelData.key);e.accepted=true} }
        height: header.height''')
edit('explorer/FileArea.qml','      id: row\n','''      id: row
      activeFocusOnTab: index===Math.max(0,area.ex.cur)
      Accessible.role: Accessible.ListItem
      Accessible.name: modelData.name
      Accessible.description: modelData.path
      Accessible.selectable: true
      Accessible.selected: sel
      Accessible.onPressAction: {var entry=modelData;area.ex.openEntry(entry)}
      onActiveFocusChanged: if(activeFocus) {area.ex.cur=index;area.ex.kbd=true;area.ensure(index)}
''')
edit('explorer/FileArea.qml','      id: gr\n','''      id: gr
      function focusEntry(i) { var offset=modelData.idx ? modelData.idx.indexOf(i) : -1;var cell=offset<0 ? null : cellRepeater.itemAt(offset);if(cell) cell.forceActiveFocus() }
''')
edit('explorer/FileArea.qml','          model: gr.modelData.idx || []','          id: cellRepeater\n          model: gr.modelData.idx || []')
edit('explorer/FileArea.qml','            id: cl\n','''            id: cl
            activeFocusOnTab: modelData===Math.max(0,area.ex.cur)
            onActiveFocusChanged: if(activeFocus) {area.ex.cur=modelData;area.ex.kbd=true;area.ensure(modelData)}
''')
edit('explorer/Cell.qml','  signal pressed(','''  Accessible.role: Accessible.ListItem
  Accessible.name: e.name || ""
  Accessible.description: e.path || ""
  Accessible.focusable: true
  Accessible.selectable: true
  Accessible.selected: sel
  Accessible.onPressAction: activated()
  Accessible.onToggleAction: toggled()
  signal pressed(''')
edit('explorer/Cell.qml','readonly property bool hov: ma.containsMouse','readonly property bool hov: ma.containsMouse || activeFocus')
edit('explorer/Explorer.qml','    area.ensure(ni)\n','    area.ensure(ni)\n    if(!filterInput.activeFocus) area.focusEntry(ni)\n')
edit('explorer/Explorer.qml','      if (e.key === Qt.Key_Space && !ctrl','''      if(e.key===Qt.Key_Menu || (shift && e.key===Qt.Key_F10)) {
        if(win.view==="folder") {if(win.cur>=0) win.rightClick(win.cur);ctx.openAt(14,toolbar.height+78,win.menuFor(win.cur))}
        e.accepted=true;return
      }
      if (e.key === Qt.Key_Space && !ctrl''')

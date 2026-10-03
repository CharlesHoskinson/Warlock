from pathlib import Path
P=Path(__file__).resolve().parent/'app'
def edit(path,old,new):
 p=P/path;s=p.read_text();assert old in s,(path,old[:70]);p.write_text(s.replace(old,new,1))
edit('explorer/Dashboard.qml','  function scrollPosition()', '''  function ensureItem(item) {
    var y=item.mapToItem(fl.contentItem,0,0).y
    fl.contentY=Math.max(0,Math.min(fl.contentHeight-fl.height,y<fl.contentY ? y : Math.max(fl.contentY,y+item.height-fl.height)))
  }
  function scrollPosition()''')
edit('explorer/Dashboard.qml','    id: mt\n','''    id: mt
    activeFocusOnTab: true
    enabled: !!e
    Accessible.role: Accessible.Button
    Accessible.name: e ? e.name : ""
    Accessible.description: e ? e.path : ""
    Accessible.onPressAction: {var entry=e;if(entry) root.ex.revealEntry(entry)}
    onActiveFocusChanged: if(activeFocus) root.ensureItem(mt)
    Keys.onPressed: (event) => {
      if(event.key===Qt.Key_Return || event.key===Qt.Key_Enter || event.key===Qt.Key_Space) {if(!event.isAutoRepeat && e) root.ex.revealEntry(e);event.accepted=true}
      else if(event.key===Qt.Key_Menu || (event.key===Qt.Key_F10 && (event.modifiers & Qt.ShiftModifier))) {var p=mapToItem(root,0,height);root.ex.recentMenu(e,p.x,p.y);event.accepted=true}
    }
''')
edit('explorer/Dashboard.qml','border.width: 1; border.color: tma.containsMouse','border.width: activeFocus ? 2 : 1; border.color: (activeFocus || tma.containsMouse)')
edit('explorer/Dashboard.qml','onClicked: root.kindFilter = modelData.id','onActiveFocusChanged: if(activeFocus) root.ensureItem(this)\n          onClicked: root.kindFilter = modelData.id')
edit('explorer/Dashboard.qml','      MouseArea { x: hero.leftW - 90;','''      Item {
        x:hero.leftW-90;width:90;height:22;activeFocusOnTab:true
        Accessible.role:Accessible.Button;Accessible.name:"Recent media timeline"
        Accessible.onPressAction:root.ex.go("coll:recent")
        Keys.onPressed:(e)=>{if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space){if(!e.isAutoRepeat)root.ex.go("coll:recent");e.accepted=true}}
        onActiveFocusChanged:if(activeFocus)root.ensureItem(this)
        Rectangle{anchors.fill:parent;color:"transparent";border.width:parent.activeFocus ? 2 : 0;border.color:Theme.accent}
      MouseArea { anchors.fill:parent;''')
edit('explorer/Dashboard.qml','onClicked: root.ex.go("coll:recent") }','onClicked: root.ex.go("coll:recent") }\n      }')
edit('explorer/Dashboard.qml','          id: cc\n','''          id: cc
          activeFocusOnTab: true
          Accessible.role: Accessible.Button
          Accessible.name: info ? info.name : ""
          Accessible.description: info ? Data.collCount(info.id)+" items" : ""
          Accessible.onPressAction: {var id=info.id;root.ex.go("coll:"+id)}
          onActiveFocusChanged: if(activeFocus) root.ensureItem(cc)
          Keys.onPressed:(e)=>{if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space){if(!e.isAutoRepeat)root.ex.go("coll:"+info.id);e.accepted=true}}
''')
edit('explorer/Dashboard.qml','border.width: 1; border.color: cma.containsMouse','border.width: activeFocus ? 2 : 1; border.color: (activeFocus || cma.containsMouse)')
edit('explorer/Dashboard.qml','          id: tile\n','''          id: tile
          activeFocusOnTab: true
          Accessible.role: Accessible.Button
          Accessible.name: modelData===Fs.home ? "Home" : Fs.base(modelData)
          Accessible.description: modelData
          Accessible.onPressAction: {var path=modelData;root.ex.go(path)}
          onActiveFocusChanged: if(activeFocus) root.ensureItem(tile)
          Keys.onPressed:(e)=>{
            if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space){if(!e.isAutoRepeat)root.ex.go(modelData);e.accepted=true}
            else if(e.key===Qt.Key_Menu || (e.key===Qt.Key_F10 && (e.modifiers & Qt.ShiftModifier))){var p=mapToItem(root,0,height);root.ex.pinMenu(modelData,p.x,p.y);e.accepted=true}
          }
          Rectangle{anchors.fill:parent;color:"transparent";border.width:tile.activeFocus ? 2 : 0;border.color:Theme.accent;z:2}
''')
edit('explorer/Dashboard.qml','          id: rl\n','          id: rl\n          currentIndex:0\n')
edit('explorer/Dashboard.qml','            id: rr\n','''            id: rr
            activeFocusOnTab:index===rl.currentIndex
            Accessible.role:Accessible.ListItem
            Accessible.name:modelData.name
            Accessible.description:modelData.path
            Accessible.onPressAction:{var entry=modelData;root.ex.openEntry(entry)}
            onActiveFocusChanged:if(activeFocus){rl.currentIndex=index;rl.positionViewAtIndex(index,ListView.Contain);root.ensureItem(rr)}
            Rectangle{anchors.fill:parent;color:"transparent";border.width:rr.activeFocus ? 2 : 0;border.color:Theme.accent;z:2}
            Keys.onPressed:(e)=>{
              if(e.key===Qt.Key_Up || e.key===Qt.Key_Down){var i=Math.max(0,Math.min(rl.count-1,index+(e.key===Qt.Key_Down ? 1 : -1)));rl.currentIndex=i;rl.positionViewAtIndex(i,ListView.Contain);Qt.callLater(function(){rl.forceLayout();var r=rl.itemAtIndex(i);if(r)r.forceActiveFocus()});e.accepted=true}
              else if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space){if(!e.isAutoRepeat)root.ex.openEntry(modelData);e.accepted=true}
              else if(e.key===Qt.Key_Menu || (e.key===Qt.Key_F10 && (e.modifiers & Qt.ShiftModifier))){var p=mapToItem(root,0,height);root.ex.recentMenu(modelData,p.x,p.y);e.accepted=true}
            }
''')
edit('explorer/Treemap.qml','      id: t\n','''      id: t
      activeFocusOnTab:true
      Accessible.role:Accessible.Button
      Accessible.name:modelData.name
      Accessible.description:modelData.path + ", " + Fs.size(modelData.size)
      Accessible.onPressAction:{var path=modelData.path;root.open(path)}
      onActiveFocusChanged:if(activeFocus){root.hovered=modelData;root.ensureVisible(t)}
      Keys.onPressed:(e)=>{if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space){if(!e.isAutoRepeat)root.open(modelData.path);e.accepted=true}}
''')
edit('explorer/Treemap.qml','  signal open(string path)','  signal open(string path)\n  signal ensureVisible(var item)')
edit('explorer/Treemap.qml','border.width: modelData.level === 0 ? 1 : 0','border.width:activeFocus ? 2 : (modelData.level === 0 ? 1 : 0)')
edit('explorer/Dashboard.qml','          onOpen: (p) => root.ex.go(p)','          onOpen: (p) => root.ex.go(p)\n          onEnsureVisible: (item) => root.ensureItem(item)')

from pathlib import Path
P=Path(__file__).resolve().parent/'app'
def edit(path,old,new):
 p=P/path;s=p.read_text();assert old in s,(path,old[:70]);p.write_text(s.replace(old,new,1))
edit('shell.qml','import QtQuick','import QtQuick\nimport "WindowAccessibilityV4"')
edit('Ui/Btn.qml','  signal clicked(var mouse)', '''  property string accessibleName: text.length ? text : tip
  property bool keyboardPressed: false
  enabled: enabled2
  activeFocusOnTab: true
  Accessible.role: Accessible.Button
  Accessible.name: accessibleName
  Accessible.focusable: enabled2
  Accessible.focused: activeFocus
  Accessible.pressed: ma.pressed || keyboardPressed
  Accessible.onPressAction: activate()
  function activate() { if (enabled2) clicked({button:Qt.LeftButton,modifiers:Qt.NoModifier,x:width/2,y:height/2}) }
  Keys.onPressed: (e) => {
    if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) { if (!e.isAutoRepeat) activate(); e.accepted=true }
    else if (e.key === Qt.Key_Space) { keyboardPressed=true; e.accepted=true }
  }
  Keys.onReleased: (e) => { if (e.key === Qt.Key_Space) { if (keyboardPressed && !e.isAutoRepeat) { keyboardPressed=false; activate() }; e.accepted=true } }
  onActiveFocusChanged: if (!activeFocus) keyboardPressed=false
  signal clicked(var mouse)''')
edit('Ui/Btn.qml','border.width: root.bordered ? 1 : 0','border.width: root.activeFocus ? 2 : (root.bordered ? 1 : 0)')
edit('Ui/Btn.qml','border.color: root.primary ? Theme.accent','border.color: root.activeFocus ? Theme.accent : root.primary ? Theme.accent')
edit('Ui/Btn.qml','onClicked: (m) => { if (root.enabled2) root.clicked(m) }','onPressed: root.forceActiveFocus()\n    onClicked: (m) => { if (root.enabled2) root.clicked(m) }')
edit('Ui/Btn.qml','    Ico { visible:','    Ico { Accessible.ignored:true; visible:')
edit('Ui/Btn.qml','Label { id: caption;','Label { id: caption; Accessible.ignored:true;')
edit('Ui/Chip.qml','  signal clicked()', '''  activeFocusOnTab: true
  Accessible.role: Accessible.Button
  Accessible.name: text
  Accessible.checkable: true
  Accessible.checked: active
  Accessible.focused: activeFocus
  Accessible.onPressAction: clicked()
  Keys.onPressed: (e) => { if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space) { if(!e.isAutoRepeat) clicked(); e.accepted=true } }
  signal clicked()''')
edit('Ui/Chip.qml','border.width: 1','border.width: root.activeFocus ? 2 : 1')
edit('Ui/Chip.qml','border.color: root.active ? Theme.accent','border.color: root.activeFocus || root.active ? Theme.accent')
edit('explorer/Explorer.qml','    id: content\n','    id: content\n    Keys.forwardTo: [keys]\n')
edit('explorer/Explorer.qml','    id: keys\n','    id: keys\n    Accessible.ignored: true\n')
names=[('icon: ""; active:','accessibleName: "Home"; icon: ""; active:'),('icon: ""; enabled2:','accessibleName: "Back"; icon: ""; enabled2:'),('icon: ""; enabled2:','accessibleName: "Forward"; icon: ""; enabled2:'),('icon: ""; enabled2:','accessibleName: "Up"; icon: ""; enabled2:'),('icon: win.viewMode ===','accessibleName: win.viewMode === "list" ? "Show grid" : "Show list"; icon: win.viewMode ==='),('icon: ""; enabled2:','accessibleName: "Sort"; icon: ""; enabled2:'),('icon: "\\uf05a"; enabled2:','accessibleName: "Details"; icon: "\\uf05a"; enabled2:'),('icon: win.showHidden ?','accessibleName: "Show hidden files"; icon: win.showHidden ?'),('icon: win.view === "folder" ?','accessibleName: win.view === "folder" ? (Data.isPinned(win.cwd) ? "Unpin folder" : "Pin folder") : "Refresh Home"; icon: win.view === "folder" ?')]
for old,new in names: edit('explorer/Explorer.qml',old,new)
edit('explorer/Explorer.qml','          id: filterInput\n','          id: filterInput\n          Accessible.name: "Filter files"\n          Accessible.description: "Control Return searches below this folder"\n')
edit('explorer/PathBar.qml','    id: input\n','    id: input\n    Accessible.name: "Location"\n')
edit('explorer/Detail.qml','icon: ""; bordered:','accessibleName: "Close details"; icon: ""; bordered:')
edit('explorer/Lightbox.qml','icon: ""; onClicked:','accessibleName: "Close preview"; icon: ""; onClicked:')
edit('explorer/Lightbox.qml','icon: ""; enabled2:','accessibleName: "Previous file"; icon: ""; enabled2:')
edit('explorer/Lightbox.qml','icon: ""; enabled2:','accessibleName: "Next file"; icon: ""; enabled2:')
edit('Ui/Prompt.qml','  function close() {', '''  function cycleFocus(backward) {
    var controls = confirmOnly ? [cancelBtn,acceptBtn] : [input,cancelBtn,acceptBtn]
    var i=0; for(var k=0;k<controls.length;k++) if(controls[k].activeFocus) { i=k; break }
    controls[(i+(backward ? controls.length-1 : 1))%controls.length].forceActiveFocus()
  }
  Keys.onPressed: (e) => {
    if(e.key===Qt.Key_Tab || e.key===Qt.Key_Backtab) { cycleFocus(e.key===Qt.Key_Backtab || !!(e.modifiers & Qt.ShiftModifier)); e.accepted=true }
  }
  function close() {''')
edit('Ui/Prompt.qml','    id: card\n','    id: card\n    Accessible.role: Accessible.Dialog\n    Accessible.name: root.title\n')
edit('Ui/Prompt.qml','          id: input\n','          id: input\n          Accessible.name: root.title\n          Accessible.description: root.hint\n')
edit('Ui/Prompt.qml','Btn { text: "Cancel";','Btn { id: cancelBtn; text: "Cancel";')
edit('Ui/Prompt.qml','        Rectangle {\n          width: okl.', '''        Rectangle {
          id: acceptBtn
          activeFocusOnTab: true
          Accessible.role: Accessible.Button
          Accessible.name: root.okLabel
          Accessible.onPressAction: root.accept()
          border.width: activeFocus ? 2 : 0; border.color: Theme.fgBright
          Keys.onPressed: (e) => { if(e.key===Qt.Key_Return || e.key===Qt.Key_Enter || e.key===Qt.Key_Space) { if(!e.isAutoRepeat) root.accept(); e.accepted=true } }
          width: okl.''')

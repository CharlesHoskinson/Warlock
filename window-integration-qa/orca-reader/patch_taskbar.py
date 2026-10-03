from pathlib import Path

root=Path.home()
model_block=(root/'window-behavior-spec/minimize-motion-stage/widget_v62/Windows.qml').read_text()
a=model_block.index('  ListModel { id: previewCards }')
b=model_block.index('  readonly property var relatedSnaps:',a)
model_block=model_block[a:b]
for p in [root/'.config/omarchy/plugins/hoskinson.windows/widget_reader_v1/Windows.qml',root/'window-behavior-spec/minimize-motion-stage/widget_v62/Windows.qml']:
 s=p.read_text().replace('qml/WindowAccessibilityV2','qml/WindowAccessibilityV3')
 s=s.replace('popupFlickable.activeFocus','popupKeyCatcher.activeFocus').replace('popupFlickable.forceActiveFocus()','popupKeyCatcher.forceActiveFocus()')
 if 'id: popupKeyCatcher' not in s:
  s=s.replace('      focus: root.keyboardMode\n      Keys.onPressed: function(event) { root.handleKeyboard(event) }','      Item {\n        id: popupKeyCatcher\n        anchors.fill: parent\n        Accessible.ignored: true\n        focus: root.keyboardMode\n        Keys.onPressed: function(event) { root.handleKeyboard(event) }\n      }')
 if 'id: previewCards' not in s:
  s=s.replace('  readonly property var relatedSnaps:',model_block+'  readonly property var relatedSnaps:')
  s=s.replace('          id: windowRepeater\n          model: !root.menuMode && root.popupGroup ? root.popupGroup.windows : []','          id: windowRepeater\n          model: previewCards')
  s=s.replace('            id: windowPreview\n            required property var modelData','            id: windowPreview\n            required property string payload\n            readonly property var modelData: JSON.parse(payload)')
  s=s.replace('          id: menuRepeater\n          model: root.menuMode ? root.menuItems : []','          id: menuRepeater\n          model: root.menuMode ? menuCards : null')
  a=s.index('          id: menuRepeater');b=s.index('            required property var modelData',a)
  s=s[:b]+s[b:].replace('            required property var modelData','            required property string payload\n            readonly property var modelData: JSON.parse(payload)',1)
 if 'property bool popupAccessibilityReady' not in s:
  s=s.replace('  property bool keyboardMode: false','  property bool keyboardMode: false\n  property bool popupAccessibilityReady: false\n  onPopupOpenChanged: if (!popupOpen) popupAccessibilityReady = false')
  s=s.replace('onKeyboardModeChanged: { if (keyboardMode) Qt.callLater(function() { popupKeyCatcher.forceActiveFocus() }) }','onKeyboardModeChanged: { root.popupAccessibilityReady = false; if (keyboardMode) Qt.callLater(function() { popupKeyCatcher.forceActiveFocus(); root.popupAccessibilityReady = true }) }')
  s=s.replace('Accessible.focused: root.popupOpen && root.keyboardMode &&','Accessible.focused: root.popupAccessibilityReady && root.popupOpen && root.keyboardMode &&')
 p.write_text(s)

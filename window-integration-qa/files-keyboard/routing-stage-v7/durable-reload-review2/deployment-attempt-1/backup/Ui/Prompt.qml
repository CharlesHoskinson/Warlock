import QtQuick
import qs.Commons

// Modal single-line prompt / confirm card. Enter accepts, Escape cancels.
Item {
  id: root
  property string title: ""
  property string hint: ""
  property bool confirmOnly: false
  property bool danger: false
  property string okLabel: "OK"
  property string mode: ""
  property var payload: null
  signal accepted(string mode, string text, var payload)
  visible: false
  anchors.fill: parent
  z: 200

  function exportUi() { return { visible: visible, title: title, hint: hint, confirmOnly: confirmOnly, danger: danger, okLabel: okLabel, mode: mode, payload: payload, text: input.text, cursor: input.cursorPosition, selectionStart: input.selectionStart, selectionEnd: input.selectionEnd, scroll: promptScroll.contentY } }
  function restoreUi(s) { title=s.title; hint=s.hint; confirmOnly=s.confirmOnly; danger=s.danger; okLabel=s.okLabel; mode=s.mode; payload=s.payload; input.text=s.text; visible=s.visible; if(visible) Qt.callLater(function(){promptScroll.contentY=s.scroll; (root.confirmOnly ? card : input).forceActiveFocus(); if(!root.confirmOnly) {input.cursorPosition=s.cursor;input.select(s.selectionStart,s.selectionEnd)}}) }

  function ask(mode, title, initial, payload, opts) {
    root.mode = mode; root.title = title; root.payload = payload
    root.hint = (opts && opts.hint) || ""; root.confirmOnly = !!(opts && opts.confirm)
    root.danger = !!(opts && opts.danger); root.okLabel = (opts && opts.ok) || "OK"
    input.text = initial || ""
    visible = true;
    (confirmOnly ? card : input).forceActiveFocus()
    if (!confirmOnly) {
      // select the stem, not the extension
      var dot = input.text.lastIndexOf(".")
      input.select(0, dot > 0 ? dot : input.text.length)
    }
  }
  function close() { visible = false }
  function accept() { var t = input.text; close(); accepted(mode, t, payload) }

  Rectangle { anchors.fill: parent; color: Theme.alpha(Theme.bgDarker, 0.72)
    MouseArea { anchors.fill: parent; onClicked: root.close() } }

  Rectangle {
    id: card
    anchors.centerIn: parent
    width: Math.min(460, root.width - 24); height: Math.min(root.height - 24, body.implicitHeight + 36)
    color: Theme.bg; border.color: root.danger ? Theme.red : Theme.accent; border.width: 1
    radius: Theme.radius
    focus: root.visible && root.confirmOnly
    Keys.onPressed: (e) => {
      if (e.key === Qt.Key_Escape) { root.close(); e.accepted = true }
      else if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) { root.accept(); e.accepted = true }
    }
    MouseArea { anchors.fill: parent }
    Flickable {
      id: promptScroll
      anchors.fill: parent; anchors.margins: 18; clip: true
      contentWidth: width; contentHeight: body.implicitHeight; boundsBehavior: Flickable.StopAtBounds
    Column {
      id: body
      width: parent.width; spacing: 12
      Label { width: parent.width; text: root.title; font.pixelSize: Theme.fsHead; color: Theme.fgBright; font.bold: true; wrapMode: Text.Wrap; elide: Text.ElideNone }
      Label { visible: root.hint.length; width: parent.width; text: root.hint; color: Theme.fgDim; wrapMode: Text.Wrap; elide: Text.ElideNone }
      Rectangle {
        visible: !root.confirmOnly
        width: parent.width; height: 34; color: Theme.bgDark
        border.width: 1; border.color: input.activeFocus ? Theme.accent : Theme.line
        TextInput {
          id: input
          anchors { fill: parent; leftMargin: 10; rightMargin: 10 }
          verticalAlignment: TextInput.AlignVCenter
          font.family: Theme.font; font.pixelSize: Theme.fsBody + 1
          color: Theme.fgBright; selectionColor: Theme.accent; selectedTextColor: Theme.bg
          clip: true
          Keys.onPressed: (e) => {
            if (e.key === Qt.Key_Escape) { root.close(); e.accepted = true }
            else if (e.key === Qt.Key_Return || e.key === Qt.Key_Enter) { root.accept(); e.accepted = true }
          }
        }
      }
      Row {
        anchors.right: parent.right; spacing: 8
        Btn { text: "Cancel"; onClicked: root.close() }
        Rectangle {
          width: okl.implicitWidth + 28; height: 30; color: root.danger ? Theme.red : Theme.accent
          radius: Theme.radius
          Label { id: okl; anchors.centerIn: parent; text: root.okLabel; color: Theme.bg; font.bold: true }
          MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.accept() }
        }
      }
    }
    }
    Rectangle {
      anchors.right: parent.right; anchors.rightMargin: 4; width: 3
      visible: promptScroll.contentHeight > promptScroll.height
      height: Math.max(24, promptScroll.height * promptScroll.height / Math.max(1, promptScroll.contentHeight))
      y: promptScroll.y + (promptScroll.height - height) * promptScroll.contentY / Math.max(1, promptScroll.contentHeight - promptScroll.height)
      color: Theme.alpha(Theme.fg, 0.28)
    }
  }
}

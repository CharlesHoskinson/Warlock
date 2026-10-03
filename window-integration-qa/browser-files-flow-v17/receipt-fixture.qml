import QtQml
import "files-app/PressReceipt.js" as PressReceipt
QtObject {
  id: root
  property var explorer: root
  property var win: root
  property string viewMode: "grid"
  property string accessibleName: win.viewMode === "list" ? "Show grid" : "Show list"
  readonly property string actionIdentity: "control:"+accessibleName
  property bool visible: true
  property bool enabled: true
  property bool enabled2: true
  property var qaClickEvents: []
  property int focusCalls: 0
  function forceActiveFocus() { focusCalls++ }
  signal clicked(var mouse)
  onClicked: win.viewMode = win.viewMode === "list" ? "grid" : "list"
  property QtObject area: QtObject {
    signal pressed(var mouse)
    signal clicked(var mouse)
    signal canceled()
    onPressed: root.forceActiveFocus()
    onClicked: (m) => { if (root.enabled2) root.clicked(m) }
  }
  property Component observerComponent: Component {
    Connections {
      property var buttonItem
      property var mouseArea
      property int ownerToken
      property var captureState: null
      target: mouseArea
      Component.onCompleted: captureState=PressReceipt.newState(buttonItem,mouseArea,ownerToken)
      Component.onDestruction: if(captureState) PressReceipt.invalidate(captureState)
      function onPressed(mouse) {
        PressReceipt.capture(captureState,buttonItem,mouseArea,mouse,explorer.viewMode)
      }
      function onCanceled() { PressReceipt.cancel(captureState) }
      function onClicked(mouse) {
        qaClickEvents.push(PressReceipt.consume(captureState,buttonItem,mouseArea,mouse,explorer.viewMode))
      }
    }
  }
  property var observer: null
  Component.onCompleted: observer=observerComponent.createObject(root,{buttonItem:root,mouseArea:area,ownerToken:1})
  function require(value,message) { if(!value)throw new Error(message) }
  function runCase(name) {
    var mouse={button:1,modifiers:0}
    if(name==="qtSignalOrder") {
      area.pressed(mouse);area.clicked(mouse)
      var receipt=qaClickEvents[0]
      require(focusCalls===1 && viewMode==="list" && qaClickEvents.length===1,"Original projected callback route")
      require(receipt.accepted && receipt.identity==="control:Show list" && receipt.postHandlerIdentity==="control:Show grid","Immutable receipt before reactive mutation")
      require(Object.isFrozen(receipt.press),"Actual Qt JavaScript immutable primitive snapshot")
      return {ok:true,scope:"CPU-only QObject/Connections and exact copied callback bodies; not actual MouseArea/physical input",receipt:receipt}
    }
    if(name==="keyboardCannotProducePointerReceipt") {
      root.clicked(mouse);require(viewMode==="list" && qaClickEvents.length===0,"Original keyboard route has no pointer receipt")
      return {ok:true}
    }
    if(name==="qtCancellation") {
      area.pressed(mouse);area.canceled();area.clicked(mouse)
      require(qaClickEvents.length===1 && !qaClickEvents[0].accepted && qaClickEvents[0].identity==="","Canceled QObject signal route")
      return {ok:true}
    }
    var item={visible:true,enabled:true,enabled2:true,accessibleName:"Show list",actionIdentity:"control:Show list"}
    var pointer={};var state=PressReceipt.newState(item,pointer,1)
    if(name==="noPress")require(!PressReceipt.consume(state,item,pointer,mouse,"grid").accepted,"No fabricated capture")
    else {
      if(name==="invisible")item.visible=false
      if(name==="disabled")item.enabled=false
      if(name==="disabled2")item.enabled2=false
      if(name==="emptyName")item.accessibleName=""
      if(name==="emptyIdentity")item.actionIdentity=""
      if(name==="badPressButton")mouse.button=2
      if(name==="badPressModifiers")mouse.modifiers=1
      if(name==="booleanPressMetadata")mouse.button=true
      if(name==="fractionalPressMetadata")mouse.button=1.5
      if(name==="boundedGeneration")state.generation=65536
      if(name==="badOwnerToken")state=PressReceipt.newState(item,pointer,true)
      var press=PressReceipt.capture(state,item,pointer,mouse,"grid")
      if(name==="immutable") {
        require(Object.isFrozen(press),"Object.freeze")
        press.identity="corrupt";require(press.identity==="control:Show list","Primitive identity cannot mutate")
        return {ok:true}
      }
      if(name==="cancel")PressReceipt.cancel(state)
      if(name==="destroy")PressReceipt.invalidate(state)
      if(name==="newPress") {
        item.actionIdentity="control:Show grid";var fresh=PressReceipt.capture(state,item,pointer,mouse,"list")
        require(fresh.generation===2 && fresh!==press,"New actual press replaces generation")
        var newer=PressReceipt.consume(state,item,pointer,mouse,"list")
        require(newer.accepted && newer.identity==="control:Show grid","Own newer capture")
        return {ok:true}
      }
      if(name==="replacedItem")item={visible:true,enabled:true,enabled2:true,accessibleName:"Show list",actionIdentity:"control:Show list"}
      if(name==="replacedArea")pointer={}
      if(name==="changedOwnerToken")state.ownerToken=2
      if(name==="changedGeneration")state.generation++
      if(name==="badClickButton")mouse={button:2,modifiers:0}
      if(name==="badClickModifiers")mouse={button:1,modifiers:1}
      if(name==="booleanClickMetadata")mouse={button:true,modifiers:0}
      if(name==="reactiveMutation") { item.accessibleName="Show grid";item.actionIdentity="control:Show grid" }
      var result=PressReceipt.consume(state,item,pointer,mouse,"list")
      if(name==="reactiveMutation"||name==="duplicateClick") {
        require(result.accepted && result.identity==="control:Show list","Exact actual press identity")
        if(name==="reactiveMutation")require(result.postHandlerIdentity==="control:Show grid","Current label only diagnostic")
        if(name==="duplicateClick")require(!PressReceipt.consume(state,item,pointer,mouse,"list").accepted,"Exactly once")
      }else require(!result.accepted && result.identity==="","Refuse absent/canceled/stale/malformed capture:"+name)
    }
    return {ok:true,name:name}
  }
}

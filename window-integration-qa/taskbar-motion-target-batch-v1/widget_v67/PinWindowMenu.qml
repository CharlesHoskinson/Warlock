import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import qs.Commons
import "PinMenu.js" as Policy

Item {
    id: root
    required property Item anchorItem
    required property QtObject bar
    required property string homeDir
    property bool reducedMotion: false
    property var menuState: Policy.create()
    property bool menuOpen: false
    property string status: "closed"
    property bool keyboardMode: false
    property var lastReceipt: null
    property real captureNonce: 0
    property var captureTarget: null
    property bool captureExitSeen: false
    property bool captureOutDone: false
    property bool captureErrDone: false
    property int captureCode: -1
    property var invocation: null
    property bool actionExitSeen: false
    property bool actionOutDone: false
    property bool actionErrDone: false
    property int actionCode: -1
    signal operationFinished(bool complete)
    function diagnosticState() {
        var window=toggleButton.QsWindow.window;
        var position=window?toggleButton.mapToItem(window.contentItem,0,0):null;
        return {nonce:menuState.nonce,open:menuState.open,status:menuState.status,
            publicIdentity:menuState.target,captured:menuState.token,sent:menuState.sent,
            invocation:invocation,receipt:lastReceipt,
            layerNamespace:"hoskinson-pin-window-menu",
            button:position?{x:position.x,y:position.y,width:toggleButton.width,height:toggleButton.height,
                visible:toggleButton.visible,enabled:toggleMouse.enabled,label:"Toggle pin"}:null};
    }
    function sync() { menuOpen=menuState.open;status=menuState.status; }
    function close() { Policy.dismiss(menuState);keyboardMode=false;sync(); }
    function openWindow(w) {
        // Busy capture is refused locally. Its eventual old reply cannot enable
        // the new generation; no automatic queued query or action is inserted.
        try {
            Policy.open(menuState,w);keyboardMode=true;sync();
            if(captureProcess.running || actionProcess.running) { menuState.status="capture-refused";sync();return; }
            captureNonce=menuState.nonce;captureTarget=menuState.target;
            captureExitSeen=false;captureOutDone=false;captureErrDone=false;captureCode=-1;
            captureProcess.command=[homeDir+"/.local/bin/hypr-pin-capture","capture",JSON.stringify(captureTarget)];captureProcess.running=true;
        } catch(e) { close(); }
    }
    function captureFinished() {
        if(!captureExitSeen || !captureOutDone || !captureErrDone) return;
        var receipt=null;try { receipt=JSON.parse(captureOut.text); } catch(e) {}
        Policy.captured(menuState,captureNonce,captureTarget,captureCode,receipt);sync();
    }
    function toggle() {
        if(actionProcess.running) return;
        invocation=Policy.invoke(menuState);if(!invocation) return;sync();
        actionExitSeen=false;actionOutDone=false;actionErrDone=false;actionCode=-1;
        actionProcess.command=[homeDir+"/.local/bin/hypr-pin-toggle","toggle",JSON.stringify(invocation.token)];actionProcess.running=true;
    }
    function actionFinished() {
        if(!actionExitSeen || !actionOutDone || !actionErrDone) return;
        var receipt=null;try { receipt=JSON.parse(actionOut.text || actionErr.text); } catch(e) {}
        lastReceipt=receipt;var complete=Policy.completed(menuState,invocation,actionCode,receipt);sync();operationFinished(complete);
    }
    Process {
        id: captureProcess
        stdout: StdioCollector { id:captureOut; waitForEnd:true; onStreamFinished:{ root.captureOutDone=true;root.captureFinished(); } }
        stderr: StdioCollector { id:captureErr; waitForEnd:true; onStreamFinished:{ root.captureErrDone=true;root.captureFinished(); } }
        onExited:function(code){root.captureCode=code;root.captureExitSeen=true;root.captureFinished();}
    }
    Process {
        id: actionProcess
        stdout: StdioCollector { id:actionOut; waitForEnd:true; onStreamFinished:{root.actionOutDone=true;root.actionFinished();} }
        stderr: StdioCollector { id:actionErr; waitForEnd:true; onStreamFinished:{root.actionErrDone=true;root.actionFinished();} }
        onExited:function(code){root.actionCode=code;root.actionExitSeen=true;root.actionFinished();}
    }
    TaskbarPopup {
        anchorItem:root.anchorItem;bar:root.bar;owner:root
        WlrLayershell.namespace:"hoskinson-pin-window-menu"
        open:root.menuOpen;keyboardMode:root.keyboardMode;reducedMotion:root.reducedMotion
        contentWidth:220;contentHeight:80
        Column {
            width:220;spacing:6
            Rectangle {
                id:toggleButton
                width:220;height:30;radius:4;color:toggleMouse.containsMouse?Color.accent:"transparent"
                Accessible.role:Accessible.Button;Accessible.name:"Toggle pin";Accessible.ignored:!root.menuOpen
                Accessible.onPressAction:root.toggle()
                Text { anchors.centerIn:parent;text:"Toggle pin";color:Color.foreground;opacity:root.status==="ready"?1:0.4 }
                MouseArea { id:toggleMouse;anchors.fill:parent;hoverEnabled:true;enabled:root.status==="ready";onClicked:root.toggle() }
                Keys.onPressed:function(event){if(event.key===Qt.Key_Return || event.key===Qt.Key_Enter || event.key===Qt.Key_Space){root.toggle();event.accepted=true;}else if(event.key===Qt.Key_Escape){root.close();event.accepted=true;}}
                focus:root.menuOpen && root.keyboardMode
            }
            Text { width:220;text:root.status==="complete"?"Pin changed":root.status==="refused-or-uncertain"?"Pin action could not be confirmed":root.status==="capture-refused"?"Could not check this window":root.status==="capturing"?"Checking window…":"";color:Color.foreground;font.pixelSize:11;wrapMode:Text.Wrap }
        }
    }
}

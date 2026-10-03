import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import WindowObjectLifetimeV1 1.0 as NativeLifetime
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
    property real captureLease: 0
    property real actionLease: 0
    property bool capturePublished: false
    property bool actionPublished: false
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
    function close() {
        if(captureLease>0) NativeLifetime.Lifetime.cancelProcess(captureProcess,Quickshell);
        if(actionLease>0) NativeLifetime.Lifetime.cancelProcess(actionProcess,Quickshell);
        Policy.dismiss(menuState);keyboardMode=false;sync();
    }
    function retirePrevious(process,out,err,lease) {
        if(lease===0) return true;
        var result=NativeLifetime.Lifetime.retireProcess(root,toggleButton,pinPopup,process,out,err,lease,Quickshell);
        return result && !result.error && result.schema==="qml-pin-process-lifecycle-v1" &&
            result.lease===lease && result.terminalRetired===true && result.normalLifecycle===true &&
            result.current===false && result.kernelBound===false && result.complete===false;
    }
    function armActual(process,out,err,role,originalJSON) {
        var result=NativeLifetime.Lifetime.armProcess(root,toggleButton,pinPopup,process,out,err,role,originalJSON,Quickshell);
        if(!result || result.error || result.schema!=="qml-pin-process-lifecycle-v1" || result.armed!==true ||
            !Number.isSafeInteger(result.lease) || result.lease<=0) throw Error("Actual native Process arm refused");
        return result.lease;
    }
    function actualState(process,lease) {
        var state=NativeLifetime.Lifetime.processState(process,Quickshell);
        if(!state || state.error || state.schema!=="qml-pin-process-lifecycle-v1" || state.lease!==lease)
            return {error:"Actual selected Process state refused"};
        return state;
    }
    Connections {
        target:NativeLifetime.Lifetime
        function onProcessLifecycleChanged(process,lease) {
            // This signal contains no proof; stale leases are inert before query.
            if(process===captureProcess && lease===root.captureLease) root.captureFinished();
            else if(process===actionProcess && lease===root.actionLease) root.actionFinished();
        }
    }
    function openWindow(w) {
        // Busy capture is refused locally. Its eventual old reply cannot enable
        // the new generation; no automatic queued query or action is inserted.
        try {
            Policy.open(menuState,w);keyboardMode=true;sync();
            if(captureProcess.running || actionProcess.running) { menuState.status="capture-refused";sync();return; }
            if(!retirePrevious(captureProcess,captureOut,captureErr,captureLease)) { menuState.status="capture-refused";sync();return; }
            captureLease=0;captureNonce=menuState.nonce;captureTarget=menuState.target;capturePublished=false;
            captureExitSeen=false;captureOutDone=false;captureErrDone=false;captureCode=-1;
            var originalJSON=JSON.stringify(captureTarget);
            captureProcess.command=[homeDir+"/.local/bin/hypr-pin-capture","capture",originalJSON];
            captureLease=armActual(captureProcess,captureOut,captureErr,"capture",originalJSON);
            captureProcess.running=true;
        } catch(e) { close(); }
    }
    function captureFinished() {
        if(capturePublished || captureLease<=0) return;
        var registered=actualState(captureProcess,captureLease);
        if(registered.error || registered.fault===true) {
            capturePublished=true;Policy.captured(menuState,captureNonce,captureTarget,-1,null);sync();return;
        }
        if(!captureExitSeen || !captureOutDone || !captureErrDone || registered.normalLifecycle!==true) return;
        if(registered.stdoutEOF!==true || registered.stderrEOF!==true || registered.workerJoined!==true ||
            registered.kernelGone!==true || registered.receiptVerified!==true || registered.exitCode!==captureCode ||
            registered.stdout!==captureOut.text || registered.stderr!==captureErr.text) return;
        var receipt=null;try { receipt=JSON.parse(registered.stdout); } catch(e) {}
        capturePublished=true;
        Policy.captured(menuState,captureNonce,captureTarget,registered.complete===true?captureCode:-1,receipt);sync();
    }
    function toggle() {
        if(actionProcess.running) return;
        try {
            if(!retirePrevious(actionProcess,actionOut,actionErr,actionLease)) return;
            actionLease=0;
            invocation=Policy.invoke(menuState);if(!invocation) return;sync();
            actionPublished=false;actionExitSeen=false;actionOutDone=false;actionErrDone=false;actionCode=-1;
            var originalJSON=JSON.stringify(invocation.token);
            actionProcess.command=[homeDir+"/.local/bin/hypr-pin-toggle","toggle",originalJSON];
            actionLease=armActual(actionProcess,actionOut,actionErr,"toggle",originalJSON);
            actionProcess.running=true;
        } catch(e) { lastReceipt=null;Policy.completed(menuState,invocation,-1,null);sync();operationFinished(false); }
    }
    function actionFinished() {
        if(actionPublished || actionLease<=0) return;
        var registered=actualState(actionProcess,actionLease);
        if(registered.error || registered.fault===true) {
            actionPublished=true;lastReceipt=null;Policy.completed(menuState,invocation,-1,null);sync();operationFinished(false);return;
        }
        if(!actionExitSeen || !actionOutDone || !actionErrDone || registered.normalLifecycle!==true) return;
        if(registered.stdoutEOF!==true || registered.stderrEOF!==true || registered.workerJoined!==true ||
            registered.kernelGone!==true || registered.receiptVerified!==true || registered.exitCode!==actionCode ||
            registered.stdout!==actionOut.text || registered.stderr!==actionErr.text) return;
        var receipt=null;try { receipt=JSON.parse(registered.stdout || registered.stderr); } catch(e) {}
        actionPublished=true;lastReceipt=receipt;
        var complete=Policy.completed(menuState,invocation,registered.complete===true?actionCode:-1,receipt);sync();operationFinished(complete);
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
        id:pinPopup
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

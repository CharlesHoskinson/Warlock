"""Generate only diagnostic observations around the genuine, unchanged route.

No positive retirement, capture or toggle is invoked by this QA diagnostic API.
The fixed malformed typed retirement observations are an explicit root review
item, separate from the read-only getters and from every real input action.
"""
from pathlib import Path
import difflib
from io_guard import publish,publish_json,sha
from selection import B,COMPOSITION
def build():
 out=B/'frontend-observation';out.mkdir(mode=0o700);diff=B/'diffs';diff.mkdir(mode=0o700)
 original=(COMPOSITION/'frontend/PinWindowMenu.qml').read_text();text=original.replace('    property bool actionPublished: false\n','    property bool actionPublished: false\n    property var retirementObservations: []\n    property bool retirementObservationLost: false\n',1)
 needle='        projection.engineBefore=engineBefore;\n'
 added='''        projection.processDiagnostics={captureLease:captureLease,actionLease:actionLease,
            captureRunning:captureProcess.running,actionRunning:actionProcess.running,
            capture:captureLease>0 && !captureProcess.running?actualState(captureProcess,captureLease):null,
            action:actionLease>0 && !actionProcess.running?actualState(actionProcess,actionLease):null,
            retirements:retirementObservations,retirementObservationLost:retirementObservationLost};
'''
 assert original.count(needle)==1;text=text.replace(needle,added+needle,1)
 needle='        var result=NativeLifetime.Lifetime.retireProcess(root,toggleButton,pinPopup,process,out,err,lease,Quickshell);\n'
 added='''        // Observation follows the actual public call and cannot replace it.
        try {
            if(retirementObservations.length>=32) retirementObservationLost=true;
            else retirementObservations=retirementObservations.concat([{sequence:retirementObservations.length+1,
                role:process===captureProcess?"capture":"toggle",lease:lease,result:result,
                command:process.command,nonce:menuState.nonce}]);
        } catch(diagnosticError) { retirementObservationLost=true; }
'''
 assert original.count(needle)==1;text=text.replace(needle,needle+added,1)
 # Fixed public malformed arguments only, with genuine lexical tuple and no
 # private Registry access. The caller must already have a successful record.
 extra='''    function observeTypedRetirementRefusal(kind) {
        if(actionLease<=0 || actionProcess.running || status!=="complete")
            return {error:"Actual successful terminal action prerequisite missing"};
        var before=actualState(actionProcess,actionLease);
        if(before.error || before.complete!==true || before.normalLifecycle!==true)
            return {error:"Actual terminal positive registration prerequisite missing"};
        var argument;
        if(kind==="boolean") argument=true;
        else if(kind==="string") argument=String(actionLease);
        else if(kind==="null") argument=null;
        else if(kind==="wrong-collector") argument=actionLease;
        else return {error:"Fixed malformed public observation required"};
        var result=NativeLifetime.Lifetime.retireProcess(root,toggleButton,pinPopup,actionProcess,
            kind==="wrong-collector"?actionErr:actionOut,actionErr,argument,Quickshell);
        return {schema:"pin-public-typed-refusal-observation-v1",kind:kind,lease:actionLease,
            before:before,result:result,after:actualState(actionProcess,actionLease)};
    }
'''
 text=text.replace('    function armActual(process,out,err,role,originalJSON) {\n',extra+'    function armActual(process,out,err,role,originalJSON) {\n',1)
 publish(out/'PinWindowMenu.qml',text.encode());publish(diff/'PinWindowMenu.qml.diff',''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile=str(COMPOSITION/'frontend/PinWindowMenu.qml'),tofile=str(out/'PinWindowMenu.qml'))).encode())
 original_w=(COMPOSITION/'frontend/Windows.qml').read_text();needle='    function pinMenuState():string { return JSON.stringify(pinMenu.diagnosticState()) }\n';added='    function pinTypedRetirementRefusal(kind:string):string { return JSON.stringify(pinMenu.observeTypedRetirementRefusal(kind)) }\n';assert original_w.count(needle)==1;windows=original_w.replace(needle,needle+added,1)
 publish(out/'Windows.qml',windows.encode());publish(diff/'Windows.qml.diff',''.join(difflib.unified_diff(original_w.splitlines(True),windows.splitlines(True),fromfile=str(COMPOSITION/'frontend/Windows.qml'),tofile=str(out/'Windows.qml'))).encode())
 publish_json(B/'frontend-observation-report.json',dict(schema='pin-process-diagnostics-source-v1',originalPinSHA256=sha(COMPOSITION/'frontend/PinWindowMenu.qml'),originalWindowsSHA256=sha(COMPOSITION/'frontend/Windows.qml'),additions=dict(processStates='Actual public terminal state with raw kernel evidence',retirements='Actual public response before unchanged predicate/command mutation',typedRefusals='Only four fixed malformed public arguments after complete terminal positive'),sourceOnly=True,QtExecution=False,negativeIPCNeedsRootReview=True,GUI=False));return 0
if __name__=='__main__':raise SystemExit(build())

"""Explicit private teardown/marker patches with exact original reconstruction."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent
REL='home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml'
MARKERS=r'''  // Owned QA terminal evidence; never grants feature/native completion.
  property bool qaTerminalQuiesced: false
  property string qaTerminalNonce: Quickshell.env("WINDOW_QA_TERMINAL_NONCE") || ""
  property string qaTerminalError: ""
  property int qaTerminalQueuedBudget: 0
  property var qaProcessGenerations: ({snapshot:0,action:0,capture:0,allCapture:0})
  property var qaProcessCurrent: ({})
  property var qaProcessRecords: []
  function qaRecord(record) {
    if (qaProcessRecords.length >= 8192) { qaTerminalError="Process evidence limit"; return }
    qaProcessRecords=qaProcessRecords.concat([Object.assign({utcMs:Date.now()},record)])
  }
  function qaRequested(kind,command) {
    if (qaTerminalQuiesced) {
      if(kind!=="action" || qaTerminalQueuedBudget<=0) qaTerminalError="New process after terminal scheduling barrier"
      else qaTerminalQueuedBudget--
    }
    if(qaProcessCurrent[kind]) qaTerminalError="Overlapping Process request generation"
    var generations=Object.assign({},qaProcessGenerations)
    generations[kind]++;qaProcessGenerations=generations
    var current=Object.assign({},qaProcessCurrent)
    current[kind]={generation:generations[kind],command:Array.from(command),pid:0,started:false}
    qaProcessCurrent=current
    qaRecord({event:"requested",kind:kind,generation:generations[kind],command:Array.from(command)})
  }
  function qaStarted(kind,process) {
    var current=Object.assign({},qaProcessCurrent),entry=current[kind]
    var pid=Number(process.processId)
    if(!entry || entry.started || !Number.isInteger(pid) || pid<=0 || pid>=2147483648 || JSON.stringify(entry.command)!==JSON.stringify(Array.from(process.command))) {
      qaTerminalError="Process started without exact request";return
    }
    entry=Object.assign({},entry,{pid:pid,started:true});current[kind]=entry;qaProcessCurrent=current
    qaRecord({event:"started",kind:kind,generation:entry.generation,pid:pid,command:entry.command})
  }
  function qaExited(kind,code,status) {
    var current=Object.assign({},qaProcessCurrent),entry=current[kind]
    if(!entry || !entry.started) { qaTerminalError="Process exited without exact start";return }
    qaRecord({event:"exited",kind:kind,generation:entry.generation,pid:entry.pid,code:code,status:status})
    if(code!==0 || status!==0) qaTerminalError="Process abnormal terminal receipt"
    delete current[kind];qaProcessCurrent=current
  }
  function qaTerminalValid(nonce) {
    return /^[0-9a-f]{32}$/.test(nonce) && nonce===qaTerminalNonce
  }
  function qaTerminalBegin(nonce) {
    if(!qaTerminalValid(nonce) || qaTerminalQuiesced) return false
    qaTerminalQueuedBudget=actionQueue.length
    qaTerminalQuiesced=true
    qaSnapshotPoll.stop();qaCapturePoll.stop();qaAllCapturePoll.stop();captureDelay.stop()
    qaRecord({event:"quiesced",nonce:nonce,queuedActions:qaTerminalQueuedBudget})
    return true
  }
  function qaTerminalState(nonce) {
    if(!qaTerminalValid(nonce)) return {error:"Exact terminal nonce required"}
    var processes={snapshot:snapshotProcess,action:actionProcess,capture:captureProcess,allCapture:allCaptureProcess},states={}
    Object.keys(processes).forEach(function(kind) { var p=processes[kind];states[kind]={running:p.running,pid:p.processId===null ? null : Number(p.processId),command:Array.from(p.command)} })
    return {screenName:root.barScreen ? root.barScreen.name : "",currentMonitor:root.currentMonitor,nonce:nonce,
      quiesced:qaTerminalQuiesced,error:qaTerminalError,queuedActions:actionQueue.length,queuedBudget:qaTerminalQueuedBudget,
      timers:{snapshot:qaSnapshotPoll.running,capture:qaCapturePoll.running,allCapture:qaAllCapturePoll.running,captureDelay:captureDelay.running,queueDelay:queueDelay.running},
      generations:qaProcessGenerations,current:qaProcessCurrent,processes:states,records:qaProcessRecords}
  }
'''
IPC=r'''    function qaTerminalQuiesce(nonce:string):string {
      var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
      if(!items.length || items.some(function(item) { return !item || typeof item.qaTerminalBegin!=="function" || !item.qaTerminalValid(nonce) || item.qaTerminalQuiesced }))
        return JSON.stringify({version:1,nonce:nonce,ack:false,error:"Exact fresh terminal widget set required"})
      var ack=items.every(function(item) { return item.qaTerminalBegin(nonce) })
      return JSON.stringify({version:1,nonce:nonce,ack:ack,states:items.map(function(item) { return item.qaTerminalState(nonce) })})
    }
    function qaTerminalRead(nonce:string):string {
      var items=root.bar && typeof root.bar.moduleWidgets==="function" ? root.bar.moduleWidgets(root.moduleName) : [root]
      return JSON.stringify({version:1,nonce:nonce,ack:items.length>0 && items.every(function(item) { return item && item.qaTerminalValid(nonce) && item.qaTerminalQuiesced }),states:items.map(function(item) { return item.qaTerminalState(nonce) })})
    }
'''
def patches():
 old_refresh='  function refresh() { if (!snapshotProcess.running) snapshotProcess.running = true }'
 return [
 ('  property int diagnosticPopupEpoch: 0\n','  property int diagnosticPopupEpoch: 0\n'+MARKERS),
 ('    function motionRefresh(encoded:string):bool',IPC+'    function motionRefresh(encoded:string):bool'),
 (old_refresh,'  function refresh() { if (!root.qaTerminalQuiesced && !snapshotProcess.running) { root.qaRequested("snapshot",snapshotProcess.command); snapshotProcess.running = true } }'),
 ('    actionQueue = actionQueue.concat([args])','    if(root.qaTerminalQuiesced) root.qaTerminalError="New action queue after terminal barrier"\n    actionQueue = actionQueue.concat([args])'),
 ('    actionProcess.running = true','    root.qaRequested("action",actionProcess.command)\n    actionProcess.running = true'),
 ('    id: snapshotProcess\n','    id: snapshotProcess\n    onStarted: root.qaStarted("snapshot",snapshotProcess)\n    onExited: function(code,status) { root.qaExited("snapshot",code,status) }\n'),
 ('    id: actionProcess\n    onExited: function(code) {','    id: actionProcess\n    onStarted: root.qaStarted("action",actionProcess)\n    onExited: function(code,status) {\n      root.qaExited("action",code,status)'),
 ('    id: captureProcess\n','    id: captureProcess\n    onStarted: root.qaStarted("capture",captureProcess)\n'),
 ('    id: allCaptureProcess\n','    id: allCaptureProcess\n    onStarted: root.qaStarted("allCapture",allCaptureProcess)\n'),
 ('    onExited: { root.previewRevision++; root.refresh() }','    onExited: function(code,status) { root.qaExited("capture",code,status); root.previewRevision++; root.refresh() }',1),
 ('    onExited: { root.previewRevision++; root.refresh() }','    onExited: function(code,status) { root.qaExited("allCapture",code,status); root.previewRevision++; root.refresh() }',1),
 ('  Timer { interval: 10000; repeat: true; running: root.ipcOwner; triggeredOnStart: true; onTriggered: if (!allCaptureProcess.running) allCaptureProcess.running = true }','  Timer { id: qaAllCapturePoll; interval: 10000; repeat: true; running: root.ipcOwner && !root.qaTerminalQuiesced; triggeredOnStart: true; onTriggered: if (!root.qaTerminalQuiesced && !allCaptureProcess.running) { root.qaRequested("allCapture",allCaptureProcess.command); allCaptureProcess.running = true } }'),
 ('  Timer { id: captureDelay; interval: 450; onTriggered: if (!captureProcess.running && root.captureAddress) captureProcess.running = true }','  Timer { id: captureDelay; interval: 450; onTriggered: if (!root.qaTerminalQuiesced && !captureProcess.running && root.captureAddress) { root.qaRequested("capture",captureProcess.command); captureProcess.running = true } }'),
 ('  Timer { interval: 3000; repeat: true; running: true; onTriggered: if (root.focusedAddress && !captureProcess.running) { root.captureAddress=root.focusedAddress; captureProcess.running=true } }','  Timer { id: qaCapturePoll; interval: 3000; repeat: true; running: !root.qaTerminalQuiesced; onTriggered: if (!root.qaTerminalQuiesced && root.focusedAddress && !captureProcess.running) { root.captureAddress=root.focusedAddress; root.qaRequested("capture",captureProcess.command); captureProcess.running=true } }'),
 ('  Timer { interval: 900; repeat: true; running: true; triggeredOnStart: true; onTriggered: root.refresh() }','  Timer { id: qaSnapshotPoll; interval: 900; repeat: true; running: !root.qaTerminalQuiesced; triggeredOnStart: true; onTriggered: root.refresh() }')]
def apply(text):
 for row in patches():
  old,new,*count=row
  if not count and text.count(old)!=1:raise RuntimeError('Original QML patch context changed')
  if count and text.count(old)<count[0]:raise RuntimeError('Original ordered receipt context changed')
  text=text.replace(old,new,count[0]if count else 1)
 return text
def reconstruct(text):
 for old,new,*_ in reversed(patches()):
  if text.count(new)!=1:raise RuntimeError('Terminal QML inverse context changed')
  text=text.replace(new,old,1)
 return text
if __name__=='__main__':
 proof=json.loads((B/'terminal-receipts-formal-before-runtime.json').read_text());assert proof['result']=='pass'
 p=B/'payload'/REL;old=(B.with_name('toolkit-held-matrix-v14')/'payload'/REL).read_text();assert p.read_text()==old
 changed=apply(old);assert reconstruct(changed)==old;p.write_text(changed)
 manifest=B/'payload-manifest.json';descriptor=json.loads(manifest.read_text());descriptor['diagnosticCopies'][REL]['copySHA256']=hashlib.sha256(p.read_bytes()).hexdigest()
 descriptor['widgetDiagnosticsOnly']=False;descriptor['widgetTerminalQuiesceOnly']=True
 descriptor['terminalControl']={'sourceOriginalFrozenV14SHA256':hashlib.sha256(old.encode()).hexdigest(),'sourceCopySHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'inverseSourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'nonceEnvironment':'WINDOW_QA_TERMINAL_NONCE','phase':'normal private teardown only','processReceiptAuthority':'actual onStarted PID/command generation and onExited code/status; no inferred PIDstart'}
 manifest.write_text(json.dumps(descriptor,indent=2)+'\n')
 print(json.dumps({'originalReconstructedExactly':True,'privateOnly':True,'nativeLaunch':False}))

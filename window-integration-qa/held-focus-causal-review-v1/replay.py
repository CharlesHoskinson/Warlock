"""Read-only actual V5 causal subset replay; additive O_EXCL artifacts only."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
Q=Path('/home/hoskinson/window-integration-qa');B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('independent_held_audit',Q/'toolkit-held-terminal-audit-v2/audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
sys.path.insert(0,str(Q/'toolkit-held-matrix-v5'));import transport_check

def save(path,packet):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(packet,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())

def main():
 stage=Q/'toolkit-held-matrix-v5';attempt=stage/'attempt-1';folder=attempt/'qt-wayland';case=a.js(folder/'case-1/report.json');variant=a.js(folder/'report.json');frozen=a.js(stage/'frozen-inputs.json')
 exact=all(a.digest(p)==(h,frozen['inputModes'][p]) for p,h in frozen['inputs'].items()) and all(os.readlink(p)==v for p,v in frozen['symlinks'].items())
 selected={label:a.one(case['trace'],'label',label) for label in ('actual press','separate WM focus intervention','actual negative group drop region','before actual nonrelease interruption')}
 source=selected['actual press']['target'];peer=selected['separate WM focus intervention']['native']['nativeFocus'];motion=selected['actual negative group drop region']['native'];before=selected['before actual nonrelease interruption'];keys=variant['cleanup']['keyboard']['trace'];escape=a.one(keys,'command','key 1 1')
 expected=a.eq(selected['separate WM focus intervention']['native']['coreDragTarget'],source) and a.eq(motion['coreDragTarget'],source) and a.eq(motion['nativeFocus'],source) and a.eq(before['native']['nativeFocus'],source) and not a.eq(before['native']['nativeFocus'],peer) and before['timeNs']<escape['sentNs'] and before['native']['signalDownButtonIds']==[272] and before['public']['activeWindow']=='peer'
 native=Q/'toolkit-interruption-v5/native-candidate';primary=Q/'toolkit-interruption-v5/primary';paths=[stage/'held_controller.py',stage/'observations.py',native/'dragBridge.cpp',native/'familyBridge.cpp',native/'barDeco.cpp',primary/'InputManager.cpp',primary/'KeybindManager.cpp',primary/'DragController.cpp']
 evidence={str(p):a.digest(p)[0] for p in paths};assert all(frozen['inputs'][p]==h for p,h in evidence.items())
 packet=dict(result='pre-Escape-native-focus-theft-confirmed' if exact and expected else 'fail',originalHeldResult='fail',completeFrozenClosureExact=exact,actualBeforeEscapeSourceFocusConfirmed=expected,sourceIdentity=source,peerIdentity=peer,observations=selected,escapeInput=escape,afterRetirementRawSnapshotRetained=False,escapeSpecificFocusTheftAccepted=False,qtDelayedModalCauseAccepted=False,sourceHashes=evidence,sourcePath='InputManager moves captured geometry then native hit-test/FFM may raw-focus that same dragged source; V21 fullFocus cancellation guard applies only within dragEnd',policy='Preserve original deliberate WM retained-target intervention; genuine keyboard cancels before keybindings. No oracle redefinition.',nativeCommands=False,mainWrites=False,fullHeld52Accepted=False,replaySourceSHA256=a.digest(B/'replay.py')[0])
 save(attempt/'root-held-focus-causal-replay-v1.json',packet)
 hf=folder/'terminal-helpers';arc=a.js(hf/'archive.json');cfg_raw=a.read(hf/'helper-config.json');log=a.read(hf/'helper-events.jsonl');cfg=json.loads(cfg_raw);events=[json.loads(line) for line in log.splitlines() if line.strip()];starts=[e for e in events if e['event']=='started'];ends=[e for e in events if e['event']=='terminal']
 raw=hashlib.sha256(cfg_raw).hexdigest()==arc['configSHA256'] and hashlib.sha256(log).hexdigest()==arc['logSHA256'] and events==arc['events'] and arc['completeEOF'] is True and not arc['parseErrors']
 comps=[e for e in starts if e.get('class','compositor')=='compositor'];normal=len(events)==len(starts)+len(ends) and len(starts)==len(ends) and len({s['operation'] for s in starts})==len(starts) and set(cfg['allowed'])=={s['operation'] for s in comps}
 for s in starts:
  t=a.one(ends,'operation',s['operation']);normal=normal and t['exitCode']==0 and all(t.get(k)==s.get(k) for k in ('wrapper','delegate','class','queryRoot','helper','serviceOperation')) and a.gone(s['wrapper']) and a.gone(s['delegate']) and s['ipc']['completeServerEOF'] is True
 unexpected=variant['hostEvidence'].get('unexpectedInnerDescendants',[])
 packet=dict(result='pass' if raw and normal else 'fail',scope='Actual registered helper subset only; original full held failure unchanged',rawArchiveIntegrity=raw,actualRegisteredHelpersNormal=normal,compositorOperationCount=len(comps),queryRoles=[s['queryRoot'] for s in starts if s.get('class')=='query'],serviceRegistered='serviceMembers' in cfg,fullWorkloadAccepted=False,hostUnexpectedDescendants=unexpected,allRecordedUnexpectedOriginalsGone=all(a.gone(r) for r in unexpected),unexpectedAttributionAccepted=False,nativeCommands=False,mainWrites=False)
 save(attempt/'root-held-helper-subset-replay-v1.json',packet)
 authority=transport_check.verify_authority(frozen['inputs']);logs=[folder/'host/hyprland.log',folder/'host/weston-renderer.log'];data=[a.read(p) for p in logs];gate=transport_check.transport_log_gate([s.decode() for s in data])
 save(attempt/'root-held-transport-replay-v1.json',dict(result='pass' if authority and gate['passed'] else 'fail',sourceASTExact=authority,transport=gate,artifacts=[dict(path=str(p),sha256=hashlib.sha256(s).hexdigest(),completeEOF=True) for p,s in zip(logs,data)],scope='Mandatory parent transport only; original full held failure unchanged',nativeCommands=False,mainWrites=False))
 print(json.dumps(dict(preEscapeFocusTheft=expected,helperSubsetNormal=normal and raw,transport=gate['passed'],frozenExact=exact,nativeCommands=False)))
if __name__=='__main__':main()

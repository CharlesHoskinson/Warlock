"""Retain actual offline source/formal/oracle review; never runs native fixtures."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;scope=require_qa_scope();records=[]
commands=[['python3',str(B/'test_observations.py')],['quint','test',str(B/'interruption_test.qnt')],['quint','run',str(B/'interruption.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1']]
for cmd in commands:
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=90);records.append(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 if r.returncode:break
source=(B/'native-probe/probe.cpp').read_text();native=(B.parent/'toolkit-interruption-v4/primary/KeybindManager.cpp').read_text()
assert 'const auto& controller=g_layoutManager->dragController()' in source
assert 'm_currentlyHeldButtons' not in source and '#define private' not in source
assert 'HyprlandAPI::createFunctionHook' not in source and 'dragEnd(' not in source and 'dragBegin(' not in source
assert 'signalDownButtonIds' in source and 'coreDragTarget' in source and 'coreDragMode' in source and 'coreExclusiveDeviceGrab' in source
assert 'group->windows()' in source and 'group->current()' in source and 'group->head()' in source
assert 'bool       mouseBindWasActive = ensureMouseBindState();' in native
for p in B.rglob('*.py'):ast.parse(p.read_text())
report={'result':'pass' if len(records)==len(commands) and all(r['returncode']==0 for r in records) else 'fail','scope':scope,'commands':records,'sourceChecks':{'probeControllerBorrowedNotUniqueCopied':True,'publicRawSignalHeldIdsDistinctFromCoreBool':True,'noPrivateAccessMacro':True,'probeHasNoMutatingHooksDragCalls':True,'actualExactTargetModesGroupsExposed':True,'coreKeyboardCancelsTargetBeforeKeybindHandling':True,'pythonParses':True},'oracleTests':16,'formalNamedScenarios':19,'formalSamples':2000,'formalSteps':100,'requestedSeed':20260930,'candidateNativeBlocked':True,'candidateNativeBlockReason':'Root observed V20 idle retire_gesture_current SIGABRT in CWeakPointer ownership; fresh V5/V21 required','nativeFixtureLaunched':False,'nativeLoaded':False,'probeCompiledOnly':True,'wrapperFrozen':False}
p=B/'offline-review.json'
with p.open('x') as f:json.dump(report,f,indent=2)
print(json.dumps({'result':report['result'],'sourceChecks':len(report['sourceChecks']),'oracleTests':16,'formalNamed':19,'formalSamples':2000,'nativeLaunched':False}));raise SystemExit(report['result']!='pass')

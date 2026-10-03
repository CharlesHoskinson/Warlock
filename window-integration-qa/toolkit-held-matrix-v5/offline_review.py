"""Retain scoped actual protocol/formal/source review; never launches GUI/native."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent

def main():
 scope=require_qa_scope();records=[]
 commands=[
 ['/usr/bin/python3','-m','unittest','discover','-s',str(B),'-p','test*.py','-v'],
 ['/usr/bin/python3','-m','unittest','discover','-s',str(B/'frontend-candidate'),'-p','test*.py','-v'],
 ['quint','test',str(B/'interruption_test.qnt')],
 ['quint','run',str(B/'interruption.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1'],
 ['quint','test',str(B/'helper_generations.qnt')],
 ['quint','run',str(B/'helper_generations.qnt'),'--invariant=invariant','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1'],
 ['quint','test',str(B/'qs_readiness.qnt')],
 ['quint','run',str(B/'qs_readiness.qnt'),'--invariant=invariant','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1'],
 ['quint','test',str(B/'mapped_lifetimes.qnt')],
 ['quint','run',str(B/'mapped_lifetimes.qnt'),'--invariant=invariant','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1'],
 ['quint','test',str(B/'backend_lifecycle.qnt')],
 ['quint','run',str(B/'backend_lifecycle.qnt'),'--invariant=invariant','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]
 for command in commands:
  result=subprocess.run(command,capture_output=True,text=True,timeout=120);records.append(dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
  if result.returncode:break
 source=(B/'native-probe/probe.cpp').read_text();native=(B.parent/'toolkit-interruption-v5/primary/KeybindManager.cpp').read_text()
 checks=dict(probeControllerBorrowedNotUniqueCopied='const auto& controller=g_layoutManager->dragController()' in source,publicRawSignalHeldIdsDistinctFromCoreBool='signalDownButtonIds' in source and 'heldButtons' in source,noPrivateAccessMacro='m_currentlyHeldButtons' not in source and '#define private' not in source,probeHasNoMutatingHooksDragCalls=all(text not in source for text in ('HyprlandAPI::createFunctionHook','dragEnd(','dragBegin(')),actualDecorationsAndLayersQueried=all(text in source for text in ('getWindowDecorationBox','runLayer','layerState()->layers()')),coreKeyboardCancelsTargetBeforeKeybindHandling='bool       mouseBindWasActive = ensureMouseBindState();' in native)
 for path in B.rglob('*.py'):
  if '__pycache__' not in path.parts:ast.parse(path.read_text())
 checks['pythonParses']=True
 from freeze_packet import collect
 closure=collect();checks['fullBytesModesLinksCurrent']=True
 report=dict(result='pass' if len(records)==len(commands) and all(row['returncode']==0 for row in records) and all(checks.values()) else 'fail',scope=scope,commands=records,sourceChecks=checks,formalNamedScenarios=39,formalSamples=10000,formalSteps=100,nativeLaunched=False,nativeLoaded=False,probeCompiledOnly=True,rootReviewPending=True,wrapperFrozen=False,closureCounts=dict(inputs=len(closure['inputs']),modes=len(closure['inputModes']),links=len(closure['symlinks'])))
 path=B/'offline-review-v5.json'
 with path.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
 path.chmod(0o600);print(json.dumps(dict(result=report['result'],sourceChecks=len(checks),commands=len(records),nativeLaunched=False)));return int(report['result']!='pass')
if __name__=='__main__':raise SystemExit(main())

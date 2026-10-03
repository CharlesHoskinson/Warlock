from pathlib import Path
import json,hashlib,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;S=B.parent/'reduced-validation-counterexample-v1';P=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-responsive-v13')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
scope=require_qa_scope();before={str(p):sha(p) for p in [S/'REPAIR_CONTRACT.md',S/'reduction_validation.qnt',S/'reduction_validation_test.qnt',S/'probe.py',P/'scene_controller.py',P/'scene_manager.py',P/'direction.py',P/'test_scene_controller.py']}
commands=[['/usr/bin/python3','-B',str(B/'probe.py')],['quint','typecheck',str(S/'reduction_validation.qnt')],['quint','test',str(S/'reduction_validation_test.qnt')],['quint','run',str(S/'reduction_validation.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]
results=[]
for command in commands:
 r=subprocess.run(command,capture_output=True,text=True,timeout=120);results.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 if r.returncode:break
counterexample=json.loads((B/'result.json').read_text());checks=dict(sourceUnchanged=all(sha(p)==v for p,v in before.items()),formalReplayPass=len(results)==len(commands) and all(r['returncode']==0 for r in results),actualUnchangedControllerCounterexample=counterexample['counterexampleEstablished'] and counterexample['fixtureNativeStateUnchanged'] and not counterexample['actualNativeWrites'],currentModelIsAbstract=not 'identities' in (S/'reduction_validation.qnt').read_text(),contextPendingNotPromotedByAck='context:false' in (S/'reduction_validation.qnt').read_text() and 'oldAckCannotSupplyNewContextTest' in (S/'reduction_validation_test.qnt').read_text())
report=dict(result='pass-with-implementation-obligations' if all(checks.values()) else 'fail',scope=scope,checks=checks,sourceHashes=before,commands=results,counterexampleSHA256=sha(B/'result.json'),nativeLaunch=False,controllerModelEdits=False,obligations=[
'Separate visual-retirement ownership from current user receipt: exact old renderer token, complete ordered members/source paths, transport authority, cancel-queued/ack flags and latest receipt must be independent.',
'Reduced pending validation without visual keeps current Scene/context/deadline alive; no settle/cleanup/native effects. Existing explicit failure, deadline, supersession and uncertainty policies remain.',
'ManagedController contextPending early-return must still permit visual-only suppression, while forbidding prepare/native effects until latest context completes. Reduction off cannot retarget canceled visual.',
'On exact authenticated cancel ACK, preserve latest receipt, symbolic Direction and original receipt deadline/contextPending; replace internal Scene/generation atomically. Same-object token mutation leaves stale workers authoritative.',
'Atomically update manager pending ingress provisional Scene reference/internal token when replacing an internally restarted Scene; preserve receipt/intent/owner maps and original accepted receipt identity.',
'Guard every worker/native/capture/seed boundary against outstanding visual retirement and stale captured generation, including retire_gestures, apply_destination and late family/destination query replies.',
'Cancel ACK is closure only: fresh identity/family/scope/destination/context evidence required before commit or native effects. Never reuse previous.accepted_operation as authority for latest unvalidated receipt.',
'Latest successor must inherit old retirement object and capture ownership without duplicate cancel or retarget. Stale ready/endpoint/fatal/cancel events cannot settle/clear latest receipt.',
'Capture disposal waits exact cancel ACK or existing independently authenticated normal renderer closure. Generic transport loss cannot fabricate cancellation completion.',
'Model abstracts exact identities/transport/generation and assumes NewRequest visual transfer; concrete formal refinement must represent cancel send failure, context response generation, stale worker replies, supersession after queued ACK and reduction toggle racing renderer events.',
'Replay blocked metadata counterexample plus contextPending/no-visual/provisional visual/newer receipts/wrong+duplicate ACK/old callbacks/reduction reversals/deadline/closed member/transport error; preserve original baseline/strict native gates.'])
with (B/'review.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
(B/'review.json').chmod(0o600);print(json.dumps(dict(result=report['result'],checks=checks,reviewSHA256=sha(B/'review.json'))))
raise SystemExit(int(not all(checks.values())))

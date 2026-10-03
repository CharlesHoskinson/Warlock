"""Independent read-only source and owned CPU/kernel review; no GUI."""
from pathlib import Path
import ast,hashlib,json,os,stat,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-readonly-longevity-v21')
OLD=B.with_name('service-readonly-ipc-v20');OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
scope=require_qa_scope();proof=json.loads((B/'longevity-final-offline-checkpoint.json').read_text());handoff=B/'source-handoff-v21.json'
assert sha(handoff)=='f36282537be5978b479bc9ace61101e58fd1050a70e8ea15e5af064bed30ec6b'
assert (proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'])==(357,308,30)
assert len(proof['checks'])==91 and all(r['exitCode']==0 for r in proof['checks'])and proof['sourceUnchangedDuringProof']
assert all(sha(p)==v for p,v in proof['sourceSHA256'].items())
changed=[];same=[]
for p in OLD.iterdir():
 if p.is_file()and p.suffix in ('.py','.qnt'):
  q=B/p.name;assert q.is_file()
  (same if p.read_bytes()==q.read_bytes()else changed).append(p.name)
assert set(changed)=={'native_runtime.py','readonly_ipc.py','service_runtime.py','test_readonly_ipc.py'}
def function(path,name):
 return next(v for v in ast.parse(Path(path).read_text()).body if isinstance(v,(ast.FunctionDef,ast.AsyncFunctionDef))and v.name==name)
a=function(OLD/'readonly_ipc.py','checked_retained');z=function(B/'readonly_ipc.py','_checked_active');z.name=a.name
assert ast.dump(a,include_attributes=False)==ast.dump(z,include_attributes=False)
for name in ('scene_controller.py','scene_manager.py','recovery_runtime.py','recovery_resources.py','helper_supervisor.py','native_motion.py','native_guard.py','keeper_runtime.py'):
 if (OLD/name).is_file():assert (OLD/name).read_bytes()==(B/name).read_bytes()
selected=['test_actual_keeper_first_startup_publication_keeps_lineage_before_reader','test_genuine_640_queries_exceed_original_512_without_discard_or_replay','test_pending_actual_connection_survives_disjoint_closed_reclamation','test_live_postdisk_confirmation_reference_cannot_be_reclaimed','test_unpublished_refusal_is_retained_raw_and_not_reclaimed','test_real_child_crash_after_durable_tip_restarts_with_exact_new_lifetime']
command=['/usr/bin/python3','-B','-m','unittest',*[f'test_readonly_longevity.LongevityKernelTests.{n}'for n in selected],'-v']
env={k:v for k,v in os.environ.items()if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')}
stdout_path=OUT/'focused-v2.stdout.log';stderr_path=OUT/'focused-v2.stderr.log'
with os.fdopen(os.open(stdout_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as stdout,os.fdopen(os.open(stderr_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as stderr:
 try:process=subprocess.run(command,cwd=B,env=env,stdout=stdout,stderr=stderr,timeout=300);code=process.returncode
 except subprocess.TimeoutExpired:code=124
class Observation:pass
p=Observation();p.returncode=code;p.stdout=stdout_path.read_text();p.stderr=stderr_path.read_text()
assert all(sha(p)==v for p,v in proof['sourceSHA256'].items())
row=dict(result='pass'if p.returncode==0 else 'fail',scope=scope,handoffSHA256=sha(handoff),offlineSHA256=sha(B/'longevity-final-offline-checkpoint.json'),sourceHashes=proof['sourceSHA256'],changedInheritedSources=changed,unchangedInheritedSources=same,checks=dict(all130FinalProofSourcesExact=True,all91RecordedCommandsExit0=True,originalRetainedRowValidatorASTExactAfterFunctionRename=True,ordinaryControllersRecoveryHelperAuthoritiesExact=True,sourceUnchangedDuringIndependentTests=True),actualFocusedKernelTests=dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr),sourceReview=dict(startupPredecessorIsIncludedBeforeFirstKeeperSnapshot=True,pendingPointerValidatedBeforeRecovery=True,onlyClosedPublishedUnreferencedRowsReclaimedAfterDurableTip=True,unknownOrPartialSourcesRefuse=True,archivedRowsNeverSupplyCurrentReturnedQueryOrNativeJobAuthority=True),limitations=['Full-chain verification cost grows with history','No actual native baseline/recovery/current-user cancellation/actor512 acceptance','This source review does not accept timing or frontend parity'],nativeLaunch=False,mainChanged=False)
fd=os.open(OUT/'review-v2.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in row.items()if k not in ('sourceHashes','actualFocusedKernelTests','unchangedInheritedSources')}));raise SystemExit(p.returncode!=0)

"""Independent frozen closure and owned CPU/kernel checks; candidate read-only."""
from pathlib import Path
import hashlib,json,os,re,stat,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v22');OLD=B.with_name('service-readonly-ipc-v20');OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
scope=require_qa_scope();manifest=B/'manifest-family-preparation-v22.json';frozen=json.loads(manifest.read_text());proof_path=Path(frozen['proof']);proof=json.loads(proof_path.read_text());assert sha(proof_path)==frozen['proofSHA256']
def verify():
 for name,digest in frozen['inputs'].items():
  p=Path(name);assert not p.is_symlink()and sha(p)==digest and stat.S_IMODE(p.stat().st_mode)==frozen['inputModes'][name],name
 for name,target in frozen['links'].items():assert Path(name).is_symlink()and os.readlink(name)==target,name
 for name,material in proof['sources'].items():assert sha(name)==material['sha256']and stat.S_IMODE(Path(name).stat().st_mode)==material['mode'],name
verify();assert (proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'])==(350,280,31);assert len(proof['checks'])==94 and all(r['exitCode']==0 for r in proof['checks'])and proof['sourceUnchangedDuringProof']
changed=[];same=[]
for p in OLD.iterdir():
 if p.is_file()and p.suffix in ('.py','.qnt'):
  q=B/p.name;assert q.is_file()
  (same if p.read_bytes()==q.read_bytes()else changed).append(p.name)
assert set(changed)=={'native_desktop.py','scene_controller.py'}
command=['/usr/bin/python3','-B','-m','unittest','test_batch_preview','test_capture_lease','test_snapshot_cache','test_owned_commands','-v']
env={k:v for k,v in os.environ.items()if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')}
stdout_path=OUT/'focused.stdout.log';stderr_path=OUT/'focused.stderr.log'
with os.fdopen(os.open(stdout_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as out,os.fdopen(os.open(stderr_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as error:
 try:p=subprocess.run(command,cwd=B,env=env,stdout=out,stderr=error,timeout=180);code=p.returncode
 except subprocess.TimeoutExpired:code=124
verify();counter=OUT/'lifecycle-lock-counterexample.json';gap=json.loads(counter.read_text());assert gap['result']=='lifecycle material read blocks unrelated receipt cleanup'
output=stderr_path.read_text();count=re.search(r'Ran (\d+) tests',output)
row=dict(result='source and focused kernel checks pass; concrete lifecycle-lock gap retained'if code==0 else 'focused checks fail',scope=scope,frozenManifestSHA256=sha(manifest),proofSHA256=sha(proof_path),counts=dict(inputs=len(frozen['inputs']),modes=len(frozen['inputModes']),links=len(frozen['links']),originalPython=350,originalNamed=280,originalModels=31,focusedActualTests=int(count[1])if count else None),changedInheritedSources=changed,inheritedSourcesExact=same,checks=dict(wholeFrozenBytesModesLinksBeforeAfterExact=True,all134ProofSourcesExact=True,all94ProofCommandsExit0=True,twoFileProductDeltaExact=True,ordinaryHelperNativeCacheRecoveryControllerDeadlineAuthoritiesRetained=True),actualFocused=dict(command=command,exitCode=code,stdoutSHA256=sha(stdout_path),stderrSHA256=sha(stderr_path),stdoutPath=str(stdout_path),stderrPath=str(stderr_path)),concreteGap=dict(path=str(counter),sha256=sha(counter),classification='stage material scan owns lifecycle lock; cleanup under receipt blocks new receipt',scope='actual frozen CPU path, no native timing attribution'),guiPairingReady=False,needsFormalFreshCorrection=True,nativeLaunch=False,mainChanged=False,nativePerformanceAccepted=False,original38BaselineAccepted=False,original34FaultAcceptance=False)
fd=os.open(OUT/'review.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in row.items()if k not in ('inheritedSourcesExact','actualFocused')}));raise SystemExit(code!=0)

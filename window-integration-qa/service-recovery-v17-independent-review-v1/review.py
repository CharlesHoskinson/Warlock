from pathlib import Path
import ast,hashlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-recovery-terminal-v17');BASE=B.parent/'service-recovery-v15-frozen-v2';OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 scope=require_qa_scope();handoff=json.loads((B/'source-handoff.json').read_text());manifest=json.loads((BASE/'manifest-recovery-v15.json').read_text())
 checks={}
 for name,digest in handoff['reviewedSources'].items():
  if sha(name)!=digest:raise ValueError('Reviewed source changed '+name)
 checks['reviewedSourcesExact']=True
 files=manifest.get('inputs',manifest.get('files'));modes=manifest['inputModes']
 for name,digest in files.items():
  if (Path(name).is_symlink() and name not in manifest['links']) or sha(name)!=digest or Path(name).stat().st_mode&0o7777!=modes[name]:raise ValueError('Frozen base changed '+name)
 for name,target in manifest.get('symlinks',manifest.get('links',{})).items():
  if not Path(name).is_symlink() or os.readlink(name)!=target:raise ValueError('Frozen link changed')
 checks['wholeFrozenBaseExact']=True
 for name in handoff['inheritedPythonExact']:
  if (B/name).read_bytes()!=(BASE/name).read_bytes():raise ValueError('Inherited source changed '+name)
 checks['ordinaryAuthoritiesExact']=True
 source=(B/'recovery_resources.py').read_text();tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='renderer_terminal_state');lines=source.splitlines(keepends=True);rest=''.join(lines[:node.lineno-1]+lines[node.end_lineno+2:]);checks['resourceDeltaOnlyNewHelper']=rest==(BASE/'recovery_resources.py').read_text()
 runtime=(B/'recovery_runtime.py').read_text().replace('from recovery_resources import renderer_terminal_state','from recovery_resources import process_start').replace("renderer_terminal_state(row['renderer'])['oldLifetimeGone'] is not True","process_start(row['renderer']['pid'])==row['renderer']['start']")
 checks['runtimeDeltaExactlyTwoGuards']=runtime==(BASE/'recovery_runtime.py').read_text()
 checks['oneStatRecordIdentityState']='fields=tail.split()' in source and "return {'start':start,'state':state}" in source
 checks['kernelPidfdAndRecheck']='current=observe();gone=absent_or_reused(current)' in source and 'poll.register(pidfd,select.POLLIN)' in source and 'not(events[0][1]&select.POLLIN)' in source
 helper=ast.get_source_segment(source,node);checks['helperReadOnlyNoSignals']=all(word not in helper for word in ('send_signal','os.kill','unlink','write(','SIGTERM','SIGKILL'))
 checks['unexpectedErrorsRefuse']='except ProcessLookupError:' in helper and 'except OSError' not in helper and 'unexpected renderer pidfd terminal event; quarantined' in helper
 stage=OUT/'cpu-sources';stage.mkdir(mode=0o700)
 for path in B.glob('*.py'):
  dst=stage/path.name;dst.write_bytes(path.read_bytes());dst.chmod(path.stat().st_mode&0o7777)
 tests=subprocess.run(['/usr/bin/python3','-B','-m','unittest','test_renderer_terminal','test_recovery_cancel','test_recovery_runtime','test_recovery_resources','-v'],cwd=stage,capture_output=True,text=True,timeout=120)
 checks['independentCpuKernelTestsPass']=tests.returncode==0 and 'skipped=' not in tests.stderr
 checks['handoffStillExact']=all(sha(name)==digest for name,digest in handoff['reviewedSources'].items())
 report=dict(result='pass' if all(checks.values()) else 'fail',scope=scope,checks=checks,sourceHandoffSHA256=sha(B/'source-handoff.json'),reviewedSourceCount=len(handoff['reviewedSources']),frozenBaseInputs=len(files),frozenBaseLinks=len(manifest.get('symlinks',manifest.get('links',{}))),tests=dict(returncode=tests.returncode,stdout=tests.stdout,stderr=tests.stderr),scopeLimit='Read-only source and CPU/kernel exact lifetime review; no native or current-user cancellation acceptance',nativeLaunch=False,mainChanges=False)
 with (OUT/'review.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 (OUT/'review.json').chmod(0o600);print(json.dumps(dict(result=report['result'],checks=checks,reviewSHA256=sha(OUT/'review.json'))));return int(report['result']!='pass')
if __name__=='__main__':raise SystemExit(main())

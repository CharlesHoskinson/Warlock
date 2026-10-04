import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1), 'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parent
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'installed':False,'commands':[],'scope':'AQ held-key cancellation on leave/capability removal and parent loss; focused current-device callback admission, strong callback retention, all frozen AQ138 pointer/transport fences; unchanged public headers/all parent exports; native key/modifier/shortcut acceptance separate'}
def run(name,args):
 p=subprocess.run(args,capture_output=True,timeout=240)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 report['commands'].append({'name':name,'command':args,'exitCode':p.returncode})
 print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr.decode(errors='replace')[-4000:]
 return p
try:
 upstream=json.loads((ROOT/'upstream.json').read_text());parent=Path(upstream['parent'])
 cpu_path=sorted((ROOT/'qa').glob('replay-*/report.json'))[-1];model_path=sorted((ROOT/'qa').glob('model-*/report.json'))[-1]
 cpu=json.loads(cpu_path.read_text());model=json.loads(model_path.read_text());cancel_path=sorted((ROOT/'qa').glob('cancel-*/report.json'))[-1];cancel=json.loads(cancel_path.read_text());assert cancel['passed'] and cancel['candidateValidated'] and cancel['mutantsRejected']==5;assert cpu['passed'] and cpu['candidateValidated'] and cpu['mutantsRejected']==7 and model['passed'] and model['mutantsRejected']==10 and len(model['namedScenarios'])==16
 assert model['sourceSHA256']==digest(ROOT/'spec/held.qnt')
 for packet,path in [(cpu,cpu_path),(model,model_path),(cancel,cancel_path)]:
  for rel,wanted in packet['artifacts'].items():assert digest(path.parent/rel)==wanted,rel
 for path,wanted in cancel['inputs'].items():assert digest(path)==wanted,path
 assert digest(Path(next(path for path in cancel['inputs'] if path.endswith('candidate/src/backend/Wayland.cpp'))))==digest(ROOT/'candidate/src/backend/Wayland.cpp')
 keys_path=sorted((ROOT/'qa').glob('keys-*/report.json'))[-1];keys=json.loads(keys_path.read_text());assert keys['passed'] and keys['candidateValidated'] and keys['mutantsRejected']==7 and keys['candidateChecks']>=2000
 for rel,wanted in keys['artifacts'].items():assert digest(keys_path.parent/rel)==wanted,rel
 for path,wanted in keys['inputs'].items():assert digest(path)==wanted,path
 hooks_path=sorted((ROOT/'qa').glob('hooks-*/report.json'))[-1];hooks=json.loads(hooks_path.read_text());assert hooks['passed'] and hooks['candidateValidated'] and hooks['mutantsRejected']==8
 for rel,wanted in hooks['artifacts'].items():assert digest(hooks_path.parent/rel)==wanted,rel
 for path,wanted in hooks['inputs'].items():assert digest(path)==wanted,path
 report['proofReports']=[{'path':str(p),'sha256':digest(p)} for p in [cpu_path,model_path,cancel_path,keys_path,hooks_path]]
 assert digest(parent/'component-manifest.json')==upstream['parentManifestSHA256']
 def verify_parent():
  for rel,sha in upstream['sources'].items():assert digest(parent/'candidate'/rel)==sha,rel
 verify_parent()
 report['sources']={str(p.relative_to(ROOT/'candidate')):digest(p) for p in sorted((ROOT/'candidate').rglob('*')) if p.is_file()}
 report['upstreamSHA256']=digest(ROOT/'upstream.json');report['runnerSHA256']=digest(__file__)
 report['testSourceSHA256']=digest(ROOT/'test-dimensions.cpp')
 report['presentationTestSHA256']=digest(ROOT/'test-presentation.cpp')
 report['protocolInputs']={str(p):digest(p) for p in (Path('/usr/share/wayland-protocols/stable/viewporter/viewporter.xml'),Path('/usr/bin/hyprwayland-scanner'))}
 shutil.copytree(ROOT/'candidate',OUT/'inputs/candidate')
 for name in ('build.py','upstream.json','test-dimensions.cpp','test-presentation.cpp'):shutil.copy2(ROOT/name,OUT/'inputs'/name)
 for path in report['protocolInputs']:
  target=OUT/'inputs/protocol-inputs'/Path(path).name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 report['capturedInputs']={str(p.relative_to(OUT/'inputs')):digest(p) for p in sorted((OUT/'inputs').rglob('*')) if p.is_file()}
 for p in sorted((parent/'candidate/include').rglob('*')):
  if p.is_file():assert digest(p)==digest(ROOT/'candidate/include'/p.relative_to(parent/'candidate/include'))
 report['publicHeadersUnchanged']=True;report['opaqueParentInputHeaderAdded']=False;report['currentMembershipAndWeakPublication']=True
 run('guard-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-I'+str(OUT/'inputs/candidate/src/backend'),str(OUT/'inputs/test-dimensions.cpp'),'-o',str(OUT/'test-dimensions')])
 run('guard-tests',[str(OUT/'test-dimensions')])
 run('presentation-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-I'+str(OUT/'inputs/candidate/src/backend'),str(OUT/'inputs/test-presentation.cpp'),'-o',str(OUT/'test-presentation')])
 run('presentation-tests',[str(OUT/'test-presentation')])
 report['rejectionBeforeCommitMutation']=False # Source review plus actual native qualification must establish wiring.
 run('configure',['/usr/bin/cmake','-S',str(OUT/'inputs/candidate'),'-B',str(OUT/'cmake'),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_INSTALL_PREFIX='+str(OUT/'prefix')])
 run('library-build',['/usr/bin/cmake','--build',str(OUT/'cmake'),'--target','aquamarine','-j','2'])
 library=OUT/'cmake/libaquamarine.so.0.15.0';assert library.is_file()
 report['library']=str(library);report['librarySHA256']=digest(library)
 dependency_paths={}
 for dep in (OUT/'cmake').rglob('*.o.d'):
  for path in shlex.split(dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]):
   path=Path(path)
   if not path.is_absolute():path=OUT/'cmake'/path
   if path.is_file():dependency_paths[str(path.resolve())]=digest(path)
 report['dependencies']=dependency_paths
 parentPacket=json.loads((parent/'component-manifest.json').read_text())
 parentReportPath=Path(parentPacket['buildReport']);parentReport=json.loads(parentReportPath.read_text());assert parentReport['passed']
 report['parentBuildReportSHA256']=digest(parentReportPath)
 oldlib=Path(parentReport['library']);assert digest(oldlib)==parentReport['librarySHA256']
 def symbols(lib):
  proc=run('symbols-'+('parent' if lib==oldlib else 'candidate'),['/usr/bin/nm','-D','--defined-only',str(lib)])
  return {line.split()[-1] for line in proc.stdout.decode().splitlines() if line.split()}
 missing=sorted(symbols(oldlib)-symbols(library));report['missingParentSymbols']=missing;assert not missing,missing
 verify_parent()
 for rel,sha in report['sources'].items():assert digest(ROOT/'candidate'/rel)==sha,rel
 assert digest(__file__)==report['runnerSHA256']
 assert digest(ROOT/'test-dimensions.cpp')==report['testSourceSHA256']
 assert digest(ROOT/'test-presentation.cpp')==report['presentationTestSHA256']
 for path,sha in report['protocolInputs'].items():assert digest(path)==sha,path
 for rel,sha in report['capturedInputs'].items():assert digest(OUT/'inputs'/rel)==sha,rel
 report['parentPreserved']=True;report['passed']=True
except Exception as e:report['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json',flush=True)
raise SystemExit(not report['passed'])

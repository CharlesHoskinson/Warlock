"""Prepare exact offline C1 source/ELF dependency review; never launches the renderer."""
from pathlib import Path
import hashlib,json,os,re,shlex,shutil,stat,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as stream:
  while data:=stream.read(1024*1024):h.update(data)
 return h.hexdigest()
def main():
 scope=require_qa_scope();target=B/'source-ready.json'
 if target.exists():raise RuntimeError('Fresh source-stage review destination required')
 report=json.loads((B/'offline-report.json').read_text())
 if not report['sourceUnchangedDuringProof'] or any(r['exit'] for r in report['commands']):raise RuntimeError('Offline source/commands not accepted')
 rows={};links={};commands=[]
 def add(path,expected=None,mode=None):
  path=Path(os.path.abspath(path));before=path.stat()
  if not stat.S_ISREG(before.st_mode):raise RuntimeError('Nonregular dependency:'+str(path))
  digest=sha(path);after=path.stat()
  if any(getattr(before,n)!=getattr(after,n) for n in ('st_dev','st_ino','st_mode','st_uid','st_size','st_mtime_ns','st_ctime_ns')):raise RuntimeError('Dependency changed during hash:'+str(path))
  if expected is not None and digest!=expected:raise RuntimeError('Predecessor dependency bytes changed:'+str(path))
  actual=stat.S_IMODE(before.st_mode)
  if mode is not None and actual!=mode:raise RuntimeError('Predecessor dependency mode changed:'+str(path))
  row={'sha256':digest,'mode':actual}
  if str(path) in rows and rows[str(path)]!=row:raise RuntimeError('Conflicting dependency:'+str(path))
  rows[str(path)]=row
  for name in (path,*path.parents):
   if name.is_symlink():links[str(name)]=os.readlink(name)
  resolved=path.resolve()
  if resolved!=path:add(resolved,expected,mode)
 old=B.parent/'producer-production-default-v10/manifest-v10.json';packet=json.loads(old.read_text());add(old)
 for path,digest in packet['inputs'].items():add(path,digest,packet['inputModes'][path])
 for path,value in packet['links'].items():
  if not Path(path).is_symlink() or os.readlink(path)!=value:raise RuntimeError('Predecessor symlink changed:'+path)
  links[path]=value
 predecessor=json.loads((B/'predecessor-inputs.json').read_text())
 for group,root in (('v10Inputs',predecessor['v10']),('v12Inputs',predecessor['v12'])):
  for name,digest in predecessor[group].items():add(Path(root)/name,digest)
 for path,digest in report['sourceSHA256'].items():add(path,digest)
 for row in report['commands']:add(row['log'],row['logSHA256'])
 for p in B.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.name!='source-ready.json':add(p)
 env={k:v for k,v in os.environ.items() if not k.startswith('LD_')}
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','Qt6Core','libpng','egl','glesv2','wayland-client','wayland-egl'],text=True,env=env))
 for source in sorted(B.glob('*.cpp')):
  cmd=['g++','-std=c++20','-fPIC','-M','-MT','dependency-target',*flags,source.name]
  output=subprocess.check_output(cmd,cwd=B,text=True,env=env)
  for path in shlex.split(output.replace(chr(92)+'\n',' ').split(':',1)[1]):add(B/path)
  commands.append({'command':cmd,'kind':'preprocess dependency list; no renderer execution'})
 binaries=[B/'hypr-motion-renderer-staged']
 for name in ('g++','cc','make','pkg-config','wayland-scanner','python3','quint','node','glslangValidator'):
  path=shutil.which(name)
  if not path:raise RuntimeError('Missing proof/build tool:'+name)
  add(path);binaries.append(Path(path).resolve())
 for name in ('cc1plus','cc1','as','ld'):
  value=subprocess.check_output(['g++','-print-prog-name='+name],text=True,env=env).strip();path=Path(value) if '/' in value else Path(shutil.which(value));add(path);binaries.append(path.resolve())
 loader=[]
 for binary in binaries:
  with binary.open('rb') as stream:magic=stream.read(4)
  if magic!=bytes.fromhex('7f454c46'):continue
  cmd=['ldd',str(binary)];r=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=10)
  if r.returncode or 'not found' in r.stdout+r.stderr:raise RuntimeError('Missing loader dependency:'+str(binary))
  for path in re.findall(r'(?:=> )?(/[^\s]+) \(',r.stdout):add(path)
  loader.append({'command':cmd,'stdout':r.stdout,'stderr':r.stderr,'returncode':r.returncode,'method':'glibc ldd LD_TRACE_LOADED_OBJECTS before program initialization'})
 x={'scope':'Offline C1 ordinary renderer source candidate; static diagnostic unchanged','nativeExecution':False,'GPUConnected':False,'mainWrites':False,'productionDeployment':False,'physicalCadenceProved':False,'nativeAcceptancePending':True,'scopeEvidence':scope,'binary':str(B/'hypr-motion-renderer-staged'),'binarySHA256':sha(B/'hypr-motion-renderer-staged'),'inputs':{p:r['sha256'] for p,r in sorted(rows.items())},'inputModes':{p:r['mode'] for p,r in sorted(rows.items())},'links':dict(sorted(links.items())),'offlineReport':{'path':str(B/'offline-report.json'),'sha256':sha(B/'offline-report.json'),'counts':{k:v for k,v in report.items() if k.endswith('Checks') or k.endswith('Tests') or k.endswith('Named') or k=='totalNamedScenarios'}},'predecessors':predecessor,'dependencyCommands':commands,'loaderTraces':loader,'property':'Exact same immutable sampled geometry+analytic velocity for draw/submission/presentation, exact per-output source-order/generation/epoch origin, common all-output duration planned before token mutation, idempotent start and strict normal retirement','runtimeMappedClosureProved':False,'requiredNextStep':'Independent root source review and fresh private diagnostic/ordinary/reversal/mixed-output/reduced-motion harness closure; no native launch authority is granted by this packet'}
 target.write_text(json.dumps(x,indent=2)+'\n');target.chmod(0o600)
 print(json.dumps({'sourceReady':True,'files':len(rows),'links':len(links),'binarySHA256':x['binarySHA256'],'packetSHA256':sha(target),'nativeExecution':False}))
if __name__=='__main__':main()

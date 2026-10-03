"""Fresh candidate binding only; no input, dispatch, launch, retry or native effects."""
from pathlib import Path
import hashlib,json,os,re,stat,subprocess
CANDIDATE=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
CORE=CANDIDATE/'build-core-make/Hyprland'
PLUGIN=CANDIDATE/'plugin/hyprbars-native-max-core-v2-candidate.so'
HELPER=CANDIDATE/'helper/pin_helper.py'
POLICY='59a1485d5f900db177414814bae9577898d687d17f2dc6a533ecec40a21590d3'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_pair(path):
 row=json.loads(Path(path).read_bytes())
 if type(row)is not dict or row.get('buildComplete') is not True or row.get('sourceProposalOnly') is not False:
  raise RuntimeError('Completed root-reviewed pair required')
 if row.get('core')!=str(CORE) or row.get('plugin')!=str(PLUGIN) or row.get('helper')!=str(HELPER) or row.get('corePolicyBuild')!=POLICY:
  raise RuntimeError('Exact core/plugin/helper identity required')
 ready=CANDIDATE/'SOURCE_READY.json'
 if not ready.is_file() or ready.is_symlink() or row.get('sourceReadySHA256')!=digest(ready):raise RuntimeError('Exact completed source-ready required')
 source=json.loads(ready.read_bytes())
 if source.get('corePolicyBuild')!=POLICY or source.get('nativeAuthorized') is not False or source.get('coreELFBuildID')!=row.get('coreELFBuildID'):raise RuntimeError('Completed build identity differs')
 probe=Path(__file__).resolve().parent.parent/'readonly-probe/libqt-modal-probe.so'
 if row.get('probe')!=str(probe):raise RuntimeError('Exact paired observational probe path required')
 required={str(CORE),str(PLUGIN),str(HELPER),str(ready),str(probe),str(CANDIDATE/'SOURCE_READY_INPUTS.json')}
 if not required<=set(row['inputs']) or not required<=set(row['inputModes']):raise RuntimeError('Complete pair input inventory required')
 for name,value in row['inputs'].items():
  p=Path(name)
  if type(value)is not str or not re.fullmatch('[0-9a-f]{64}',value) or type(row['inputModes'].get(name))is not int:raise RuntimeError('Typed pair inventory required')
  if p.is_symlink() or not p.is_file() or digest(p)!=value or stat.S_IMODE(p.stat().st_mode)!=row['inputModes'][name]:raise RuntimeError('Pair source bytes/modes changed: '+name)
 closure_path=CANDIDATE/'SOURCE_READY_INPUTS.json'
 if source.get('sourceClosureSHA256')!=digest(closure_path):raise RuntimeError('Exact completed source closure required')
 closure=json.loads(closure_path.read_bytes());required_dirs={str(CANDIDATE/rel):mode for rel,mode in closure['directories'].items()}
 for ancestor in closure.get('ancestors',[]):
  for rel,mode in ancestor['directories'].items():required_dirs[str(Path(ancestor['stage'])/rel)]=mode
 if type(row.get('directoryModes'))is not dict or not set(required_dirs)<=set(row['directoryModes']):raise RuntimeError('Complete selected and ancestral directory modes required')
 for name,mode in required_dirs.items():
  if type(mode)is not int or type(row['directoryModes'][name])is not int or row['directoryModes'][name]!=mode:raise RuntimeError('Conflicting source directory mode')
 for name,mode in row['directoryModes'].items():
  p=Path(name)
  if type(mode)is not int or p.is_symlink()or not p.is_dir()or stat.S_IMODE(p.stat().st_mode)!=mode:raise RuntimeError('Pair source directory mode changed: '+name)
 # readelf is an ELF inspection, never execution of the candidate.
 result=subprocess.run(['/usr/bin/readelf','-n',str(CORE)],capture_output=True,text=True,check=True)
 ids=re.findall(r'Build ID: ([0-9a-f]+)',result.stdout)
 if ids!=[row['coreELFBuildID']]:raise RuntimeError('Exact core ELF build ID required')
 return row

def process_snapshot(pid):
 if type(pid)is not int or pid<=0:raise RuntimeError('Typed selected process required')
 p=Path('/proc')/str(pid);raw=(p/'stat').read_text();fields=raw[raw.rfind(')')+2:].split()
 return dict(pid=pid,start=fields[19],pgid=int(fields[2]),uid=p.stat().st_uid,exe=os.readlink(p/'exe'),argv=(p/'cmdline').read_bytes().split(b'\0')[:-1])
def attest(session,row,phase,loaded=()):
 """Return raw binding evidence before caller persists and applies passed predicate."""
 pid=session.evidence['compositorPID'];before=process_snapshot(pid)
 raw=Path('/proc')/str(pid)/'maps';text=raw.read_text();paths=[]
 for line in text.splitlines():
  fields=line.split(maxsplit=5)
  if len(fields)==6 and fields[5].startswith('/'):paths.append(fields[5])
 expected=[str(CORE)]+list(loaded);mapped={p:digest(p) for p in expected if p in paths and Path(p).is_file()}
 after=process_snapshot(pid)
 argv=[str(CORE).encode(),b'--config',session.evidence['compositorConfig'].encode()]
 passed=(before==after and before['exe']==str(CORE) and before['argv']==argv and before['uid']==os.getuid() and before['start']==session.evidence['compositorStart'] and before['pgid']==session.evidence['compositorPGID'] and all(mapped.get(p)==row['inputs'][p] for p in expected))
 def printable(s):return {**s,'argv':[v.decode('utf8','strict')for v in s['argv']]}
 return dict(phase=phase,passed=passed,before=printable(before),after=printable(after),rawMaps=text,rawMapsSHA256=hashlib.sha256(text.encode()).hexdigest(),expectedMapped=expected,mappedSHA256=mapped,corePolicyBuild=POLICY,coreELFBuildID=row['coreELFBuildID'],sourceReadySHA256=row['sourceReadySHA256'],scope='binding only; no helper/frontend/MAX acceptance')

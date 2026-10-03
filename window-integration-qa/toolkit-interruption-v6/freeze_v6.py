"""Exact V22 review closure; source-ready precedes root review and freezing."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,stat,subprocess
B=Path(__file__).resolve().parent;QA=B.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def collect():
 files={};modes={};links={}
 def add(path,digest=None,mode=None):
  path=Path(os.path.abspath(path));assert path.is_file(),str(path)
  actual=sha(path);actualmode=stat.S_IMODE(path.stat().st_mode)
  assert digest is None or digest==actual,str(path)
  assert mode is None or mode==actualmode,str(path)
  for name in (path,path.resolve()):
   assert str(name) not in files or files[str(name)]==actual,str(name)
   files[str(name)]=actual;modes[str(name)]=stat.S_IMODE(name.stat().st_mode)
  for name in (path,*path.parents):
   if name.is_symlink():
    target=os.readlink(name);assert str(name) not in links or links[str(name)]==target
    links[str(name)]=target
 inherited=QA/'toolkit-interruption-v5/frozen-inputs.json'
 assert sha(inherited)=='b5a1363da1f0635ce21e05f961324c246bf31cb914993b798b2ff8eb00909e8a'
 previous=json.loads(inherited.read_text());assert len(previous['files'])==1354
 for name,digest in previous['files'].items():add(name,digest,previous['inputModes'][name])
 for name,target in previous['links'].items():assert os.readlink(name)==target;links[name]=target
 for path in (inherited,inherited.with_name('REPORT.json'),QA/'toolkit-v5-root-source-review.json'):add(path)
 offline=json.loads((B/'offline-report-v6.json').read_text());assert offline['result']=='pass' and offline['sourceUnchangedDuringProof']
 for name,digest in offline['sourceSHA256'].items():add(name,digest)
 for row in offline['commands']:assert row['exitCode']==0;add(row['log'],row['logSHA256'])
 build=json.loads((B/'build-report-v6.json').read_text());assert build['result']=='compiled'
 for key in ('sourceHashes','sourceDependencies'):
  for name,digest in build[key].items():add(name,digest)
 for filename in ('helper-report.json','lua-lifetime-report.json','ownership-report.json','focus-abi-report.json'):
  proof=json.loads((B/filename).read_text());assert proof['result']=='pass'
  for name,digest in proof['dependencies'].items():add(name,digest)
 assert json.loads((B/'authority-report-2.json').read_text())['passedAssertions']==33
 for root in (B,QA/'held-focus-causal-review-v1',QA/'toolkit-held-matrix-v5/attempt-1'):
  for path in sorted(root.rglob('*')):
   if '__pycache__' in path.parts or (root==B and path.name in ('frozen-inputs.json','source-ready.json','REPORT.json')):continue
   if path.is_file():add(path)
 # Retain the complete original frozen failed workload, including its exact modes/links.
 held=QA/'toolkit-held-matrix-v5/frozen-inputs.json';old=json.loads(held.read_text())
 for name,digest in old['inputs'].items():add(name,digest,old['inputModes'][name])
 for name,target in old['symlinks'].items():assert os.readlink(name)==target;links[name]=target
 add(held)
 binaries=[B/'native-candidate/hyprbars-v22-interruption-candidate.so',Path('/usr/bin/Hyprland')]
 for directory in ('focus-build','ownership-build','helper-build','authority-build-2','lua-lifetime-build'):
  binaries.extend(p for p in (B/directory).iterdir() if p.is_file() and p.read_bytes()[:4]==b'\x7fELF')
 for tool in ('g++','make','pkg-config','python3','quint','node','addr2line','objdump','ldd'):
  name=shutil.which(tool);assert name;add(name);binaries.append(Path(name).resolve())
 for tool in ('cc1plus','as','ld'):
  name=subprocess.check_output(['g++','-print-prog-name='+tool],text=True).strip();name=name if '/' in name else shutil.which(name);add(name);binaries.append(Path(name))
 for path in binaries:
  add(path)
  if path.read_bytes()[:4]!=b'\x7fELF':continue
  out=subprocess.run(['ldd',str(path)],capture_output=True,text=True);assert out.returncode==0,out.stderr
  for name in re.findall(r'(?:=> )?(/[^\s]+) \(',out.stdout):add(name)
 binary=B/'native-candidate/hyprbars-v22-interruption-candidate.so';assert sha(binary)==build['binarySHA256']
 row=dict(kind='V22 exact retained-capture automatic FFM guard; root native acceptance pending',files=dict(sorted(files.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())),binary=str(binary),binarySHA256=sha(binary),snapLuaSHA256=sha(B/'native-candidate/installed-snap.lua'),inheritedV5Manifest=str(inherited),inheritedV5ManifestSHA256=sha(inherited),inheritedV5InputsUnchanged=True,inheritedInputCount=1354,retainedActualFailure=str(QA/'toolkit-held-matrix-v5/attempt-1'),sourceGates=25,focusABIAssertions=27,uniqueWeakLuaAssertions=66,uniqueWeakLuaScenarios=17,exactGestureAssertions=33,nativeLuaGetterScenarios=8,named=34,models=3,samplesPerModel=2000,nativeExecuted=False,nativeGUIExecuted=False,mainChanged=False,productionDeployed=False,full52Accepted=False,rootReviewPending=True)
 for name,digest in files.items():assert sha(name)==digest and stat.S_IMODE(Path(name).stat().st_mode)==modes[name],name
 for name,target in links.items():assert os.readlink(name)==target,name
 return row

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source-ready',action='store_true');parser.add_argument('--freeze',action='store_true');parser.add_argument('--verify',action='store_true');args=parser.parse_args()
 if args.verify:
  row=json.loads((B/'frozen-inputs.json').read_text())
  for name,digest in row['files'].items():assert sha(name)==digest and stat.S_IMODE(Path(name).stat().st_mode)==row['inputModes'][name],name
  for name,target in row['links'].items():assert os.readlink(name)==target,name
 else:
  assert args.source_ready != args.freeze
  row=collect();target=B/('source-ready.json' if args.source_ready else 'frozen-inputs.json')
  with target.open('x') as stream:json.dump(row,stream,indent=2);stream.write('\n')
  target.chmod(0o600)
 print(json.dumps(dict(result='source-ready' if args.source_ready else 'pass',inputs=len(row['files']),modes=len(row['inputModes']),links=len(row['links']),binarySHA256=row['binarySHA256'],nativeExecuted=False)))
if __name__=='__main__':main()

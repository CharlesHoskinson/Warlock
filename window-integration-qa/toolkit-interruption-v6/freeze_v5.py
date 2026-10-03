"""Freeze fresh V21 source, actual ABI counterexample and transitive material."""
from pathlib import Path
import hashlib,json,os,re,shutil,stat,subprocess

B=Path(__file__).resolve().parent
HOME_ROOT=Path('/home/hoskinson')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 target=B/'frozen-inputs.json';checkpoint=B/'REPORT.json'
 assert not target.exists() and not checkpoint.exists()
 files,modes,links={},{},{}
 def add(path,digest=None):
  path=Path(path)
  if not path.is_absolute():path=HOME_ROOT/path
  path=Path(os.path.abspath(path));assert path.is_file(),str(path)
  actual=sha(path);assert digest is None or actual==digest,str(path)
  for name in (path,path.resolve()):files[str(name)]=actual;modes[str(name)]=stat.S_IMODE(name.stat().st_mode)
  for name in (path,*path.parents):
   if name.is_symlink():links[str(name)]=os.readlink(name)
 inherited=B.parent/'toolkit-interruption-v4/frozen-inputs.json'
 previous=json.loads(inherited.read_text());assert len(previous['files'])==936
 for name,digest in previous['files'].items():add(name,digest)
 add(inherited);add(inherited.with_name('REPORT.json'))
 offline=json.loads((B/'offline-report-v5.json').read_text());assert offline['result']=='pass' and offline['sourceUnchangedDuringProof']
 for name,digest in offline['sourceSHA256'].items():add(name,digest)
 for command in offline['commands']:assert command['exitCode']==0;add(command['log'],command['logSHA256'])
 build=json.loads((B/'build-report-v5.json').read_text());assert build['result']=='compiled'
 for field in ('sourceHashes','sourceDependencies'):
  for name,digest in build[field].items():add(name,digest)
 for name in ('helper-report.json','lua-lifetime-report.json','ownership-report.json'):
  report=json.loads((B/name).read_text());assert report['result']=='pass'
  for filename,digest in report['dependencies'].items():add(filename,digest)
 authority=json.loads((B/'authority-report-2.json').read_text());assert authority['result']=='pass' and authority['passedAssertions']==33
 for path in B.rglob('*'):
  if path.is_file():add(path)
 # Exact retained actual compositor evidence supplies the diagnosis provenance.
 failed=HOME_ROOT/'window-integration-qa/family-service-taskbar-v6/attempt-1'
 for name in ('host/hyprland.log','host/runtime-archive/taskbar-home/xdg-cache/hyprland/hyprlandCrashReport1323584.txt'):
  add(failed/name)
 binaries=[B/'native-candidate/hyprbars-v21-interruption-candidate.so',Path('/usr/bin/Hyprland')]
 for directory in ('ownership-build','helper-build','authority-build-2','lua-lifetime-build'):
  binaries.extend(path for path in (B/directory).iterdir() if path.is_file() and path.read_bytes()[:4]==b'\x7fELF')
 for tool in ('g++','make','pkg-config','python3','quint','node','addr2line','objdump'):
  filename=shutil.which(tool);assert filename,tool;add(filename);binaries.append(Path(filename).resolve())
 for name in ('cc1plus','as','ld'):
  filename=subprocess.check_output(['g++','-print-prog-name='+name],text=True).strip()
  filename=filename if '/' in filename else shutil.which(filename);add(filename);binaries.append(Path(filename))
 for binary in binaries:
  add(binary)
  if binary.read_bytes()[:4]!=b'\x7fELF':continue
  result=subprocess.run(['ldd',str(binary)],capture_output=True,text=True);assert result.returncode==0,result.stderr
  for filename in re.findall(r'(?:=> )?(/[^\s]+) \(',result.stdout):add(filename)
 binary=B/'native-candidate/hyprbars-v21-interruption-candidate.so'
 symbol=subprocess.check_output(['addr2line','-C','-f','-e',str(B.parent/'toolkit-interruption-v4/native-candidate/hyprbars-v20-interruption-candidate.so'),'0x294e8'],text=True)
 assert 'luaRetireGestureCurrent' in symbol
 integrity={}
 for label,path,key in (
  ('ServiceV12',HOME_ROOT/'window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-review-v12/manifest-v12.json','inputs'),
  ('GPUV7',HOME_ROOT/'window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/producer-quantized-over-v7/manifest-v7.json','inputs')):
  manifest=json.loads(path.read_text())
  assert all(sha(Path(name))==digest for name,digest in manifest[key].items())
  integrity[label]={'manifest':str(path),'manifestSHA256':sha(path),'inputs':len(manifest[key]),'unchanged':True}
 record={'kind':'Formal-first fresh unique-decoration ownership correction V5 / native V21; root review/native acceptance pending',
  'binary':str(binary),'binarySHA256':sha(binary),'snapLuaSHA256':sha(B/'native-candidate/installed-snap.lua'),
  'nativeExecuted':False,'nativeGUIExecuted':False,'mainChanged':False,'productionDeployed':False,
  'frozenV4InputsUnchanged':True,'inheritedInputCount':936,'retainedActualFailure':str(failed),'frozenV20Symbolization':symbol.strip(),
  'preservedIntegrity':integrity,'files':dict(sorted(files.items())),'inputModes':dict(sorted(modes.items())),'links':dict(sorted(links.items()))}
 for filename,digest in files.items():
  path=Path(filename);assert sha(path)==digest and stat.S_IMODE(path.stat().st_mode)==modes[filename],filename
 for filename,value in links.items():assert os.readlink(filename)==value,filename
 target.write_text(json.dumps(record,indent=2)+'\n')
 summary={'result':'offline candidate frozen ready for root review','manifest':str(target),'manifestSHA256':sha(target),
  'inputCount':len(files),'modeCount':len(modes),'linkCount':len(links),'binary':str(binary),'binarySHA256':sha(binary),
  'snapLuaSHA256':record['snapLuaSHA256'],'nativeExecuted':False,'mainChanged':False,'productionDeployed':False,
  'sourceGates':22,'exactGestureAssertions':33,'nativeLuaGetterScenarios':8,'uniqueWeakLuaAssertions':66,'uniqueWeakLuaScenarios':17,
  'frozenV20Counterexample':'actual extracted idle API SIGABRT/WeakPtr.hpp180 with real Hyprutils ABI, coreLimit1',
  'named':28,'models':2,'samplesPerModel':2000,'atlasChecks':72,'cacheChecks':38,'protocolChecks':17,
  'unchangedCloseBackendInherited':{'named':3,'samples':2000,'backendTests':9},'preservedIntegrity':integrity,
  'remaining':['root source/mode review','actual private idle/pending/held/cancel/release/group/focus/retirement/native controls','browser/held/family integration','reviewed guarded deployment']}
 checkpoint.write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({k:summary[k] for k in ('manifestSHA256','binarySHA256','inputCount','modeCount','linkCount')}))

if __name__=='__main__':main()

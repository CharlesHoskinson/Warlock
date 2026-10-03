from pathlib import Path
import hashlib,json,os,shlex,stat,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;V=Path('/home/hoskinson/window-behavior-spec/qml-process-provider-v7-fault-projection')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();packet=V/'current-source-ready-inputs.json';wanted='fe506e4697555e8162a7b21591f1c180dbf89a908cb72780922fe2de05cbf2aa';assert sha(packet)==wanted;ready=json.loads(packet.read_text());buildPath=V/'production-module-current-build.json';build=json.loads(buildPath.read_text());assert build['result']=='pass';assert ready['inputs'][str(buildPath)]==sha(buildPath);inputs={};links={};depRows=[];selected={};units={};toolRows=[]
 def add(p):
  p=Path(os.path.abspath(p))
  for a in (p,*p.parents):
   if a.is_symlink():links[str(a)]=os.readlink(a)
  for f in {p,p.resolve(strict=True)}:
   if f.is_file()and not f.is_symlink():inputs[str(f)]={'sha256':sha(f),'mode':stat.S_IMODE(f.stat().st_mode)}
 def existing(p):
  p=Path(p);assert sha(p)==ready['inputs'][str(p)] and stat.S_IMODE(p.stat().st_mode)==ready['inputModes'][str(p)];add(p)
 for obj,wantedObj in build['reusedExactObjects'].items():
  obj=Path(obj);assert sha(obj)==wantedObj;existing(obj);dep=obj.with_suffix('.d');raw=dep.read_text();text=raw.replace('\\\n',' ');assert '\\'not in text,'Unexpected make depfile escaping needs exact parser';target,remainder=text.split(':',1);assert target.strip()==str(obj);names=remainder.split();assert names and all(Path(n).is_absolute()for n in names);source=obj.parent.parent/obj.name[:-2];assert names[0]==str(source);assert sha(source)==build['reusedObjectSources'][str(source)];existing(source);add(dep)
  for n in names:
   expected=build['dependencies'][n];assert sha(n)==expected['sha256']and stat.S_IMODE(Path(n).stat().st_mode)==expected['mode'];existing(n);selected[n]=expected
  depRows.append({'object':str(obj),'objectSHA256':sha(obj),'depfile':str(dep),'depfileSHA256':sha(dep),'source':str(source),'sourceSHA256':sha(source),'sourceMode':stat.S_IMODE(source.stat().st_mode),'dependencies':names,'dependencyCount':len(names),'matchesRecordedSourceAndReady':True});units[str(source)]=inputs[str(source)]
 assert len(depRows)==13;assert selected==build['dependencies'];command=build['commands'][0]['command'];query=[command[0],'-###',*command[1:]];r=subprocess.run(query,capture_output=True,text=True,timeout=30);assert r.returncode==0;plan={'command':query,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'compileOrLinkExecuted':False};(B/'actual-link-driver-plan.json').write_text(json.dumps(plan,indent=2)+'\n');add(B/'actual-link-driver-plan.json');discovered=[];startup=[]
 for line in r.stderr.splitlines():
  if line.lstrip().startswith('"'):
   parts=shlex.split(line);assert parts and Path(parts[0]).is_absolute();discovered.append(parts[0])
   for token in parts:
    if token.startswith('/')and Path(token).is_file():add(token);startup.append(token)
 assert '/usr/bin/ld'in discovered,'Actual selected linker differs: inspect plan';tools=list(dict.fromkeys([command[0],'/usr/lib/qt6/moc','/usr/bin/pkg-config',*discovered]))
 for tool in tools:
  add(tool);r=subprocess.run(['/usr/bin/ldd',tool],capture_output=True,text=True,timeout=30);assert r.returncode==0;loaded=[]
  for token in r.stdout.split():
   if token.startswith('/'):
    add(token);loaded.append(token)
  toolRows.append({'path':tool,'resolved':str(Path(tool).resolve(strict=True)),'sha256':sha(tool),'mode':stat.S_IMODE(Path(tool).stat().st_mode),'loaderQuery':{'command':['/usr/bin/ldd',tool],'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},'loaderPaths':loaded,'alreadyOriginalReadyPinned':str(Path(tool).resolve())in ready['inputs']})
 for p in (packet,V/'current-source-ready.json',buildPath,B/'close_provenance.py'):add(p)
 stable=sha(packet)==wanted and all(sha(p)==v['sha256']and stat.S_IMODE(Path(p).stat().st_mode)==v['mode']for p,v in inputs.items())and all(Path(p).is_symlink()and os.readlink(p)==t for p,t in links.items());assert stable
 row={'schema':'process-current-v7-additive-build-provenance-v1','result':'pass','inputs':inputs,'symlinks':links,'originalReadyInputPacket':str(packet),'originalReadyInputPacketSHA256':wanted,'originalReadyDescriptor':str(V/'current-source-ready.json'),'originalReadyDescriptorSHA256':sha(V/'current-source-ready.json'),'originalReadyUntouched':True,'selectedDepfiles':depRows,'selectedDependencyUnionExactlyEqualsRecordedBuild':True,'selectedDependencyCount':len(selected),'compiledUnits':units,'selectedToolchain':toolRows,'actualSelectedLinker':discovered,'actualDriverDiscoveredFilePaths':sorted(set(startup)),'driverPlan':'actual-link-driver-plan.json','currentToolchainAndRecordedBuildProvenanceOnly':True,'historicalCompilerMemoryAuthorityClaimed':False,'rebuild':False,'runtimeChanged':False,'GUI':False,'nativeReady':False,'sourceStable':stable}
 out=B/'build-provenance-companion.json';out.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'result':row['result'],'packet':str(out),'sha256':sha(out),'inputs':len(inputs),'links':len(links),'depfiles':len(depRows),'selectedDependencies':len(selected)}));return 0
if __name__=='__main__':raise SystemExit(main())

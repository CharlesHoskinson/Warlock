import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
COMPONENT=REPO/'implementation/elm-core-seat-focus-restoration-v450/component-manifest.json'
COMPONENT_SHA='71f6c4e70265e103ad625568800de227fcb608e089ce8df850fad76fe3e09de3'
OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'installed':False,'scope':'Read-only held-button/seat observer compile against exact core89 owning headers; no state mutation, policy implementation or native acceptance','commands':[]}
def run(name,args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 r['commands'].append({'name':name,'command':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr[-3500:];return p.stdout
try:
 assert sha(COMPONENT)==COMPONENT_SHA
 c=json.loads(COMPONENT.read_text());corePath=Path(c['buildReport']);core=json.loads(corePath.read_text());assert core['passed'] and len(core['owningHeaders'])==694
 for rel,row in c['files'].items():assert sha(COMPONENT.parent/rel)==row['sha256'],rel
 assert sha(corePath)==c['buildReportSHA256'] and sha(core['binary'])==core['binarySHA256']
 inputs={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'native/observer.cpp',Path(__file__)]}
 for rel,digest in inputs.items():
  dest=OUT/'inputs'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
 for rel,digest in core['owningHeaders'].items():
  source=corePath.parent/'owning-headers'/rel;assert sha(source)==digest
  dest=OUT/'owning-headers'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 include=OUT/'include';include.mkdir();(include/'hyprland').symlink_to(OUT/'owning-headers',target_is_directory=True)
 flags=shlex.split(run('flags',['/usr/bin/pkg-config','--cflags','pixman-1','libdrm','libinput','wayland-server','libeis-1.0']))
 binary=OUT/'elm-held-state-qa.so'
 run('compile',['/usr/bin/c++','-std=c++23','-O2','-fPIC','-shared','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-isystem',str(include),'-isystem',str(OUT/'owning-headers'),'-isystem',str(OUT/'owning-headers/src'),'-isystem',str(OUT/'owning-headers/protocols'),*flags,'-MD','-MF',str(OUT/'observer.d'),str(OUT/'inputs/native/observer.cpp'),'-o',str(binary)])
 dependencies={str(Path(p).resolve()):sha(Path(p).resolve()) for p in shlex.split((OUT/'observer.d').read_text().replace('\\\n',' ').split(':',1)[1])}
 assert not any(p.startswith('/usr/include/hyprland') for p in dependencies)
 linked={}
 for name,target in [('core',core['binary']),('observer',str(binary))]:
  output=run(name+'-ldd',['/usr/bin/ldd',target]);assert 'not found' not in output
  for line in output.splitlines():
   for word in line.split():
    if word.startswith('/') and Path(word).is_file():linked[str(Path(word).resolve())]=sha(Path(word).resolve())
 exports=set()
 for index,p in enumerate([core['binary'],*linked]):
  for line in run('exports-'+str(index),['/usr/bin/nm','-D','--defined-only',p]).splitlines():
   fields=line.split()
   if len(fields)>=3:exports.add(fields[-1].replace('@@','@'));exports.add(fields[-1].split('@')[0])
 requested=[]
 for line in run('undefined',['/usr/bin/nm','-D','--undefined-only',str(binary)]).splitlines():
  fields=line.split()
  if len(fields)==2 and fields[0]=='U':requested.append(fields[1])
 missing=sorted(set(requested)-exports);assert not missing,missing
 for rel,digest in inputs.items():assert sha(ROOT/rel)==sha(OUT/'inputs'/rel)==digest
 for rel,digest in core['owningHeaders'].items():assert sha(OUT/'owning-headers'/rel)==digest
 for section in [dependencies,linked]:
  for p,digest in section.items():assert sha(p)==digest,p
 r.update(passed=True,binary=str(binary),binarySHA256=sha(binary),core={'path':core['binary'],'sha256':core['binarySHA256'],'buildReport':str(corePath),'buildReportSHA256':sha(corePath),'componentManifest':str(COMPONENT),'componentManifestSHA256':COMPONENT_SHA},inputs=inputs,owningHeaders=core['owningHeaders'],dependencies=dependencies,linkedLibraries=linked,strongUndefinedCount=len(requested),missingSymbols=missing)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

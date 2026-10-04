"""Replay the exact link with hashed dependencies and require identical ELF."""
import hashlib,json,resource,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('link-closure-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Exact byte-identical ELF relink with linker input hashes; no GUI or plugin acceptance'}
try:
 descriptor=ROOT/'native-build-report.json';d=json.loads(descriptor.read_text())
 report=Path(d['buildReport']);assert sha(report)==d['buildReportSHA256'];b=json.loads(report.read_text());assert b['passed']
 row=next(c for c in b['commands'] if c['name']=='link');cwd=Path(row['cwd']);dep=report.parent/'link.d'
 def dependencies(path):
  names=shlex.split(path.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1])
  # GNU ld appends empty dependency targets; parse only the first rule.
  names=names[:next((i for i,n in enumerate(names) if n.endswith(':')),len(names))]
  paths={(Path(n) if Path(n).is_absolute() else cwd/n).resolve() for n in names}
  assert paths and all(p.is_file() for p in paths)
  return {str(p):sha(p) for p in sorted(paths)}
 before=dependencies(dep);r['dependencies']=before
 command=list(row['command'])
 for i,arg in enumerate(command):
  if i and command[i-1]=='-o':command[i]=str(OUT/'Hyprland')
  elif arg.startswith('-Wl,--dependency-file='):command[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 r['command']=command;r['cwd']=str(cwd)
 r['tools']={str(Path(p).resolve()):sha(Path(p).resolve()) for p in ['/usr/bin/c++','/usr/bin/ld']}
 p=subprocess.run(command,cwd=cwd,capture_output=True,timeout=240)
 (OUT/'link.stdout').write_bytes(p.stdout);(OUT/'link.stderr').write_bytes(p.stderr);r['exitCode']=p.returncode;assert p.returncode==0
 assert dependencies(dep)==before and dependencies(OUT/'link.d')==before,'Link dependency changed'
 assert sha(OUT/'Hyprland')==sha(d['binary'])==d['sha256'],'ELF relink was not byte-identical'
 r.update(passed=True,binary=d['binary'],sha256=d['sha256'],buildReportSHA256=sha(report),descriptorSHA256=sha(descriptor),inputs={str(Path(__file__).resolve()):sha(__file__),str(dep):sha(dep)})
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.iterdir() if p.is_file()}
path=OUT/'report.json';path.write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
 target=ROOT/'link-build-report.json';assert not target.exists()
 target.write_text(json.dumps({'result':'pass','report':str(path),'reportSHA256':sha(path),'nativeAcceptance':False},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(path),'error':r.get('error')}),flush=True)
raise SystemExit(not r['passed'])

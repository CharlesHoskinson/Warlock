import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Actual changed shared GTK host and inherited C admission tests; native stamp kernel/parser/gate tests; no Elm changes or GUI grant/map qualification','commands':[]}
def run(name,args):
 p=subprocess.run(args,cwd=OUT/'inputs',capture_output=True,timeout=180)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append({'name':name,'args':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr.decode(errors='replace')[-2500:]
 return p.stdout
try:
 inputs=[*sorted((ROOT/'native').glob('*')),Path(__file__),ROOT/'origin.json']
 r['inputs']={str(p.relative_to(ROOT)):sha(p) for p in inputs if p.is_file()}
 for rel in r['inputs']:
  q=OUT/'inputs'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,q)
 flags=shlex.split(run('flags',['/usr/bin/pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0','wayland-client']).decode())
 base=['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations']
 for name,source in [('host','shared-host.c'),('identity','popup-native-identity-test.c'),('geometry-carrier','geometry-carrier-test.c'),('context-guard','shared-context-test.c'),('context-keys','context-keys-test.c'),('surface','surface-test.c')]:
  run(name+'-build',[*base,'-MD','-MF',str(OUT/(name+'.d')),'native/'+source,'-o',str(OUT/name),*flags])
  run(name+'-tests',[str(OUT/name),*(['--self-test'] if name=='host' else [])])
 dependencies={}
 for p in OUT.glob('*.d'):
  for dep in shlex.split(p.read_text().replace('\\\n',' ').split(':',1)[1]):
   q=Path(dep) if Path(dep).is_absolute() else OUT/'inputs'/dep
   dependencies[str(q.resolve())]=sha(q)
 r['dependencies']=dependencies
 libs=run('host-libraries',['/usr/bin/ldd',str(OUT/'host')]).decode();assert 'not found' not in libs
 r['linkedLibraries']={str(Path(w).resolve()):sha(Path(w).resolve()) for line in libs.splitlines() for w in line.split() if w.startswith('/') and Path(w).is_file()}
 r['tools']={str(Path(p).resolve()):sha(Path(p).resolve()) for p in ['/usr/bin/cc','/usr/bin/pkg-config','/usr/bin/ldd']}
 for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest
 r['binarySHA256']=sha(OUT/'host');r['passed']=True
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

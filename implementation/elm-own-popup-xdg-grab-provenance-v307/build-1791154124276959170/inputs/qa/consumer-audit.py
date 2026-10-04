"""Resolve every current ordered archive object to its actual compilation."""
import hashlib,json,resource,shlex,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];R=ROOT.parent;O=R/'maximized-stack-v1/native-core-v2'
sys.path.insert(0,str(R/'elm-core-keyboardless-focus-v205'));from archive import archive_payloads
OUT=ROOT/'qa'/('audit-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
r={'passed':False,'nativeAcceptance':False,'objects':[],'affected':[]}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def deps(p):
 names=shlex.split(Path(p).read_text().replace('\\\n',' ').split(':',1)[1]);return [str((Path(n) if Path(n).is_absolute() else O/'build'/n).resolve()) for n in names]
def consumer(ds):return any(p.endswith('/src/protocols/XDGShell.hpp') for p in ds)
def report(rel):
 p=R/rel/'report.json';d=json.loads(p.read_text());assert d['passed'];return p,d
try:
 core,d=report('elm-core-keyboardless-focus-v205/build-1791139089126747676');archive=core.parent/'libhyprland_lib.a';assert sha(archive)==d['archiveSHA256'];r['archive']={'path':str(archive),'sha256':sha(archive),'report':str(core),'reportSHA256':sha(core)}
 db=O/'build/compile_commands.json';r['compileDatabaseSHA256']=sha(db);raw={}
 for row in json.loads(db.read_text()):
  p=O/'build'/row['output']
  if not p.is_file() or p.suffix!='.o':continue
  dep=Path(str(p)+'.d');raw[(p.name,sha(p))]={'source':row['file'],'sourceSHA256':sha(row['file']),'object':str(p),'objectSHA256':sha(p),'command':shlex.split(row['command']),'dependencyFile':str(dep),'dependencySHA256':sha(dep),'consumesHeader':consumer(deps(dep)),'origin':'byte-exact raw object'}
 patched={}
 def put(member,source,obj,command,ds,rp,dependencyFile=None):
  value={'source':str(source),'sourceSHA256':sha(source),'object':str(obj),'objectSHA256':sha(obj),'command':command,'consumesHeader':consumer(ds),'report':str(rp),'reportSHA256':sha(rp),'origin':'actual captured compilation'}
  if dependencyFile:value.update(dependencyFile=str(dependencyFile),dependencySHA256=sha(dependencyFile))
  else:value['dependencyInventory']={p:sha(p) for p in ds}
  patched[(member,sha(obj))]=value
 p,d=report('elm-geometry-monitor-core-v73/core/build-1791106255338249967')
 for rel,origin in d['sourceOrigins'].items():
  member=Path(rel).name+'.o';source=p.parent/'owning-headers'/rel;obj=p.parent/member;dep=p.parent/(member+'.d');command=next(x['command'] for x in d['commands'] if x['name']==Path(rel).stem+'-compile');put(member,source,obj,command,deps(dep),p,dep)
 for rel in ['elm-xdg-origin-owning-compile-v469/compile-1791134015610366520','elm-core-seat-focus-compile-v448/compile-1791131428386339336','elm-keyboardless-focus-compile-v202/compile-1791138502101316887']:
  p,d=report(rel)
  for x in d.get('translationUnits',[d]):put(Path(x['source']).name+'.o',x['source'],x['object'],x['command'],x['dependencies'],p)
 for rel,member,filename in [('elm-core-parent-first-anchor-v89/build-1791107301396755104','PointerManager.cpp.o','src/pointer/PointerManager.cpp'),('elm-core-monitor-reload-v47/build-1791101203494513446','MonitorRuleManager.cpp.o',None)]:
  p,d=report(rel);cmd=next(x['command'] for x in d['commands'] if x['name'] in ['compile','pointer-compile']);source=cmd[cmd.index('-c')+1];put(member,source,p.parent/member,cmd,d['dependencies'],p)
 p,d=report('elm-window-geometry-default-limits-v40/core/qa/consumer-audit-1791101299050361614')
 for x in d['patchedObjects']:
  if x['member'] not in ['Monitor.cpp.o','WindowPolicy.cpp.o']:continue
  rp=Path(x['report']);rd=json.loads(rp.read_text());cmd=next(c['command'] for c in rd['commands'] if '-c' in c['command'] and c['command'][c['command'].index('-c')+1]==x['source']);put(x['member'],x['source'],x['object'],cmd,deps(x['dependency']),rp,Path(x['dependency']))
 for ordinal,x in enumerate(archive_payloads(archive)):
  key=(x['name'],x['sha256']);e=patched.get(key) or raw.get(key);assert e is not None,('Unresolved actual object',x)
  row={'ordinal':ordinal,'member':x,**e};r['objects'].append(row)
  if e['consumesHeader']:r['affected'].append(row)
 assert len(r['objects'])==433
 r['passed']=True
except Exception as e:r['error']=repr(e)
finally:
 (OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS affected='+str(len(r['affected'])) if r['passed'] else r.get('error'))
if not r['passed']:raise SystemExit(1)

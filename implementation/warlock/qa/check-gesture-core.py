"""Protected one-TU native gesture key policy on the exact current owning core."""
import hashlib,importlib.util,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
pointer=json.loads((ROOT/'qa/current-scene-core.json').read_text());previous=REPO/pointer['report'];prior=json.loads(previous.read_text());PRIOR=previous.parent
OUT=ROOT/'qa/runs'/('gesture-core-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('owning_archive',REPO/'implementation/warlock-core-family-crop-v16/qa/archive.py');archive=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive)
r={'passed':False,'nativeAcceptance':False,'installed':False,'protectedScope':scope,'commands':[],'scope':__doc__}
def run(name,args,cwd=OWNER/'build'):
 p=subprocess.run(list(map(str,args)),cwd=cwd,capture_output=True,timeout=240)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append({'name':name,'command':list(map(str,args)),'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-4000:])
 return p.stdout
# Reuse the original dependency parser, including escaped spaces.
def dependencies(path):
 text=path.read_text().replace('\\\n',' ')
 names=shlex.split(text.split('\n\n',1)[0].split(':',1)[1]);return {str((pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n).resolve()):sha(pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n) for n in names}
try:
 assert prior['passed'] and sha(previous)==pointer['reportSHA256'] and sha(prior['binary'])==prior['binarySHA256']
 for p,h in {**prior['dependencies'],**prior['linkDependencies']}.items():assert sha(p)==h,p
 for p,h in prior['sourceHashes'].items():assert sha(ROOT/p)==h,p
 model=json.loads(run('gesture-keys-model',['/usr/bin/python3','-B',ROOT/'qa/check-gesture-keys.py'],REPO));assert model['passed'];r['gestureKeysModel']=model
 tree=OUT/'owning-headers';shutil.copytree(PRIOR/'owning-headers',tree)
 for rel,h in prior['owningHeaders'].items():assert sha(tree/rel)==h
 rel='src/managers/KeybindManager.cpp';source=ROOT/'native/core/KeybindManager.cpp';header=ROOT/'native/core/GestureKeyPolicy.hpp'
 compiled=tree/rel;shutil.copyfile(source,compiled);shutil.copyfile(header,compiled.parent/header.name)
 source_hashes={**prior['sourceHashes'],'native/core/KeybindManager.cpp':sha(source),'native/core/GestureKeyPolicy.hpp':sha(header)}
 originals=archive.archive_payloads(PRIOR/'libhyprland_lib.a');rows=[x for x in originals if x['name']=='KeybindManager.cpp.o'];assert len(rows)==1
 original=OWNER/rel;entries=json.loads((OWNER/'build/compile_commands.json').read_text());entry=next(e for e in entries if e['file']==str(original))
 args=shlex.split(entry['command']);command=[];i=0
 while i<len(args):
  a=args[i]
  if a in ('-o','-include'):i+=2;continue
  if a=='-c' or a==str(original):i+=1;continue
  if a.startswith('-I'+str(OWNER)) and '/build/' not in a and '/subprojects/' not in a:a='-I'+str(tree)+a[len('-I'+str(OWNER)):]
  command.append(a);i+=1
 obj=OUT/'KeybindManager.cpp.o';dep=OUT/'KeybindManager.cpp.d'
 run('compile-KeybindManager.cpp',command+['-MD','-MF',dep,'-o',obj,'-c',compiled]);deps=dependencies(dep)
 assert not any(p.startswith('/usr/include/hyprland') or p.startswith(str(OWNER)+'/src/') for p in deps)
 target=OUT/'libhyprland_lib.a';archive.replace_payload(PRIOR/'libhyprland_lib.a',target,rows[0]['sha256'],obj);run('archive-index',['ar','s',target])
 new=archive.archive_payloads(target);assert len(new)==len(originals)
 for a,b in zip(originals,new):
  assert a['name']==b['name'];assert b['sha256']==sha(obj) if a['name']=='KeybindManager.cpp.o' else a==b
 link=next(c['command'] for c in prior['commands'] if c['name']=='link').copy()
 for i,a in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif a==str(PRIOR/'libhyprland_lib.a'):link[i]=str(target)
  elif a.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link);actual=dependencies(OUT/'link.d')
 expected={str(target) if p==str(PRIOR/'libhyprland_lib.a') else p:sha(target) if p==str(PRIOR/'libhyprland_lib.a') else h for p,h in prior['linkDependencies'].items()};assert actual==expected
 exports=[]
 for name,binary in [('ancestor',PRIOR/'Hyprland'),('candidate',OUT/'Hyprland')]:exports.append({tuple(l.split()[1:]) for l in run(name+'-exports',['nm','-D','--defined-only',binary]).decode().splitlines()})
 strong=lambda xs:{x for x in xs if x[0] not in ('W','V','u')};assert strong(exports[0])==strong(exports[1])
 for p,h in source_hashes.items():assert sha(ROOT/p)==h
 r.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=sha(OUT/'Hyprland'),archiveSHA256=sha(target),sourceHashes=source_hashes,dependencies=deps,linkDependencies=actual,owningHeaders=prior['owningHeaders'],existingStrongExportsPreserved=True,existingPublicHeadersUnchanged=True,existingObjectLayoutsUnchanged=True,unchangedArchiveMembers=len(originals)-1,ancestor={'report':str(previous),'reportSHA256':sha(previous)},baselineSources={rel:{'path':str(original),'sha256':sha(original),'objectSHA256':rows[0]['sha256']}},aqLibrary=prior['aqLibrary'],aqLibrarySHA256=prior['aqLibrarySHA256'])
except Exception as error:
 import traceback
 r.update(error=repr(error),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

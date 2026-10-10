"""Protected changed native gesture TUs on the exact current owning core."""
import hashlib,importlib.util,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
assert not sys.argv[1:] or sys.argv[1:] in [['--caption'],['--terminal'],['--restoration']]
mode=sys.argv[1] if sys.argv[1:] else '--keys'
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
pointer=json.loads((ROOT/'qa/current-scene-core.json').read_text());previous=REPO/pointer['report'];prior=json.loads(previous.read_text());PRIOR=previous.parent
prefix={'--caption':'caption','--terminal':'gesture-terminal','--keys':'gesture','--restoration':'caption-restoration'}[mode]
OUT=ROOT/'qa/runs'/(prefix+'-core-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('owning_archive',REPO/'implementation/warlock-core-family-crop-v16/qa/archive.py');archive=importlib.util.module_from_spec(spec);spec.loader.exec_module(archive)
r={'passed':False,'nativeAcceptance':False,'installed':False,'protectedScope':scope,'commands':[],'scope':__doc__}
def run(name,args,cwd=OWNER/'build'):
 p=subprocess.run(list(map(str,args)),cwd=cwd,capture_output=True,timeout=240)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append({'name':name,'command':list(map(str,args)),'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-4000:])
 return p.stdout
def dependencies(path):
 text=path.read_text().replace('\\\n',' ')
 names=shlex.split(text.split('\n\n',1)[0].split(':',1)[1]);return {str((pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n).resolve()):sha(pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n) for n in names}
try:
 assert prior['passed'] and sha(previous)==pointer['reportSHA256'] and sha(prior['binary'])==prior['binarySHA256'] and sha(PRIOR/'libhyprland_lib.a')==prior['archiveSHA256']
 for p,h in {**prior['dependencies'],**prior['linkDependencies']}.items():assert sha(p)==h,p
 units={'--keys':['src/managers/KeybindManager.cpp'],'--caption':['src/desktop/view/Window.cpp'],'--restoration':['src/managers/KeybindManager.cpp','src/desktop/view/Window.cpp','src/layout/supplementary/DragController.cpp'],'--terminal':['src/managers/KeybindManager.cpp','src/desktop/view/Window.cpp','src/layout/supplementary/DragController.cpp','src/managers/input/InputManager.cpp']}[mode]
 primary_header={'--keys':'GestureKeyPolicy.hpp','--caption':'CaptionGesturePolicy.hpp','--terminal':'GestureEndPolicy.hpp','--restoration':'GestureEndPolicy.hpp'}[mode]
 changed_paths={'native/core/'+pathlib.Path(p).name for p in units}|{'native/core/'+primary_header}
 for p,h in prior['sourceHashes'].items():
  if p not in changed_paths:assert sha(ROOT/p)==h,p
 model_name={'--keys':'gesture-keys','--caption':'caption-gesture','--terminal':'gesture-end','--restoration':'caption-restoration'}[mode]
 model=json.loads(run(model_name+'-model',['/usr/bin/python3','-B',ROOT/('qa/check-'+model_name+'.py')],REPO));assert model['passed'];r[model_name+'Model']=model
 tree=OUT/'owning-headers';shutil.copytree(PRIOR/'owning-headers',tree)
 for rel,h in prior['owningHeaders'].items():assert sha(tree/rel)==h
 maximum=json.loads((ROOT/'qa/current-max-core.json').read_text());max_path=REPO/maximum['report'];assert sha(max_path)==maximum['reportSHA256'];max_record=json.loads(max_path.read_text());assert max_record['passed']
 policies=[p for p in max_record['dependencies'] if p.endswith('/WindowPolicy.hpp')];assert len(policies)==1
 policy=pathlib.Path(policies[0]);assert sha(policy)==max_record['dependencies'][str(policy)]
 originals=archive.archive_payloads(PRIOR/'libhyprland_lib.a');assert len(originals)==433
 entries=json.loads((OWNER/'build/compile_commands.json').read_text());source_hashes={**prior['sourceHashes']};deps={};replacements={};baseline_sources={}
 target=OUT/'libhyprland_lib.a';shutil.copyfile(PRIOR/'libhyprland_lib.a',target)
 private=['CommittedScene.hpp','GestureKeyPolicy.hpp','CaptionGesturePolicy.hpp','ModalRecipient.hpp']+(['GestureEndPolicy.hpp'] if mode=='--terminal' or 'native/core/GestureEndPolicy.hpp' in prior['sourceHashes'] else [])
 for rel in units:
  unit=pathlib.Path(rel).name;source=ROOT/'native/core'/unit;source_hashes['native/core/'+unit]=sha(source)
  rows=[x for x in originals if x['name']==unit+'.o'];assert len(rows)==1
  compiled=tree/rel;compiled.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,compiled)
  for name in private:shutil.copyfile(ROOT/'native/core'/name,compiled.parent/name)
  original=OWNER/rel;baseline_sources[rel]={'path':str(original),'sha256':sha(original),'objectSHA256':rows[0]['sha256'],'ancestorReport':str(previous),'ancestorReportSHA256':sha(previous)}
  entry=next(e for e in entries if e['file']==str(original));args=shlex.split(entry['command']);command=[];i=0
  while i<len(args):
   a=args[i]
   if a in ('-o','-include'):i+=2;continue
   if a=='-c' or a==str(original):i+=1;continue
   if a.startswith('-I'+str(OWNER)) and '/build/' not in a and '/subprojects/' not in a:a='-I'+str(tree)+a[len('-I'+str(OWNER)):]
   command.append(a);i+=1
  command.append('-I'+str(policy.parent));obj=OUT/(unit+'.o');dep=OUT/(unit+'.d')
  run('compile-'+unit,command+['-MD','-MF',dep,'-o',obj,'-c',compiled]);current=dependencies(dep)
  assert not any(p.startswith('/usr/include/hyprland') or p.startswith(str(OWNER)+'/src/') for p in current);deps.update(current)
  intermediate=OUT/('archive-'+unit+'.a');archive.replace_payload(target,intermediate,rows[0]['sha256'],obj);shutil.move(intermediate,target);replacements[unit+'.o']=sha(obj)
 source_hashes['native/core/'+primary_header]=sha(ROOT/'native/core'/primary_header)
 run('archive-index',['ar','s',target]);new=archive.archive_payloads(target);assert len(new)==len(originals)
 for a,b in zip(originals,new):
  assert a['name']==b['name'];assert b['sha256']==replacements[a['name']] if a['name'] in replacements else a==b
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
 r.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=sha(OUT/'Hyprland'),archiveSHA256=sha(target),sourceHashes=source_hashes,changedSources=sorted(changed_paths),rebuiltArchiveMembers=replacements,dependencies=deps,linkDependencies=actual,owningHeaders=prior['owningHeaders'],existingStrongExportsPreserved=True,existingPublicHeadersUnchanged=True,existingObjectLayoutsUnchanged=True,unchangedArchiveMembers=len(originals)-len(replacements),ancestor={'report':str(previous),'reportSHA256':sha(previous)},baselineSources=baseline_sources,aqLibrary=prior['aqLibrary'],aqLibrarySHA256=prior['aqLibrarySHA256'])
except Exception as error:
 import traceback
 r.update(error=repr(error),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

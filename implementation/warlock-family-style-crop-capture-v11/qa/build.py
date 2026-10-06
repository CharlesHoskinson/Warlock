"""Protected compile of distinct isolated-client capture against owning core205."""
import hashlib,json,os,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
PARENT=REPO/'implementation/elm-geometry-authority-pair-v34'
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
MANIFEST=PARENT/'qa/build-pair-manifest.json'
MANIFEST_SHA='ffe5d603d59d1da75a19b415f3d4bbd730b940025dce85cf8951816b01e1878a'
OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
r={'passed':False,'nativeAcceptance':False,'installed':False,'scope':'Exact owning family-render core/plugin and new family capture/FD compiled; strong-symbol closure only, native qualification pending','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,command):
 p=subprocess.run(command,capture_output=True,text=True,timeout=240)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 r['commands'].append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr[-6000:]
 return p.stdout
try:
 shutil.copy2(Path(__file__),OUT/'initial-build.py')
 upstream=json.loads((ROOT/'upstream.json').read_text());source_root=Path(upstream['parent'])
 scope_parent=Path(upstream['scopeParent']['path']);assert sha(scope_parent/'native-build-report.json')==upstream['scopeParent']['descriptorSHA256']
 capture_parent=Path(upstream['captureParent']['path']);assert sha(capture_parent/'native-build-report.json')==upstream['captureParent']['descriptorSHA256'];assert sha(capture_parent/'native/authority.cpp')==upstream['captureParent']['authoritySHA256']
 assert sha(source_root/'native-build-report.json')==upstream['parentDescriptorSHA256']
 for rel,wanted in upstream['parentSourceFiles'].items():assert sha(source_root/rel)==wanted,rel
 for rel,wanted in upstream['sourceFiles'].items():assert sha(ROOT/rel)==wanted,rel
 component_root=Path(upstream['coreComponent']);component_path=component_root/'component-manifest.json'
 assert sha(component_path)==upstream['coreManifestSHA256']
 component=json.loads(component_path.read_text());assert component['sourceHeld'] and component['evidenceIntegrityPassed'] and not component['nativeAcceptance']
 def verify_component():
  for rel,row in component['files'].items():
   p=component_root/rel;assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['size'] and sha(p)==row['sha256'],rel
 verify_component()
 core_path=Path(component['buildReport']);core_report=json.loads(core_path.read_text())
 assert core_report['passed'] and set(core_report['rebuiltArchiveMembers'])=={'Renderer.cpp.o','OpenGL.cpp.o'} and core_report['unchangedArchiveMembers']==431
 core={'path':core_report['binary'],'sha256':core_report['binarySHA256'],'buildReport':str(core_path),'buildReportSHA256':sha(core_path),'versionHeaderSHA256':core_report['owningVersionHeaderSHA256'],'componentManifest':str(component_path),'componentManifestSHA256':upstream['coreManifestSHA256']}
 assert sha(core['path'])==core['sha256'] and sha(OWNER/'src/version.h')==core['versionHeaderSHA256']
 # Frozen policy headers are also actual merged-core compile inputs.
 previous=core_report.copy()
 previous['inputs']={}
 for path,wanted in core_report['retainedPolicyHeaders'].items():
  p=Path(path);assert sha(p)==wanted;previous['inputs']['candidate/'+p.name]=wanted
 # Capture only our native/candidate/build/test inputs; concurrent adapters remain outside this build.
 files=[*sorted((ROOT/'native').rglob('*')),*sorted((ROOT/'candidate').rglob('*')),*sorted((ROOT/'qa').glob('*.py')),ROOT/'upstream.json',ROOT/'SPEC.md']
 helper=ROOT/'qa/native-helper-test.py'
 if helper.exists():files.append(helper)
 files=[p for p in files if p.is_file()]
 inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
 for p in files:
  dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);dest.chmod(0o444)
 headers=core_report['owningHeaders']
 for rel,wanted in headers.items():
  p=Path(core['buildReport']).parent/'owning-headers'/rel;assert sha(p)==wanted,rel
  dest=OUT/'owning-headers'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);dest.chmod(0o444)
 for name in ['SceneModal.hpp','WindowPolicy.hpp','SceneTrace.hpp']:
  rel='candidate/'+name;wanted=previous['inputs'][rel];p=core_path.parent/'inputs'/rel;assert sha(p)==wanted
  dest=OUT/'inputs'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert sha(dest)==wanted,rel
  else:shutil.copy2(p,dest);dest.chmod(0o444)
 inherited_policy={name:previous['inputs']['candidate/'+name] for name in ['SceneModal.hpp','WindowPolicy.hpp','SceneTrace.hpp']}
 include=OUT/'include';include.mkdir();(include/'hyprland').symlink_to(OUT/'owning-headers',target_is_directory=True)
 flags=shlex.split(run('flags',['pkg-config','--cflags','gio-2.0','glesv2','json-glib-1.0','pixman-1','libdrm','libinput','wayland-server','libeis-1.0']))
 libs=shlex.split(run('libs',['pkg-config','--libs','gio-2.0','glesv2','json-glib-1.0']))
 binary=OUT/'elm-window-geometry-authority.so'
 run('compile',['g++','-std=c++23','-O2','-fPIC','-shared','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-isystem',str(include),'-isystem',str(OUT/'owning-headers'),'-isystem',str(OUT/'owning-headers/src'),'-isystem',str(OUT/'owning-headers/protocols'),'-I'+str(OUT/'inputs/candidate'),*flags,'-MD','-MF',str(OUT/'authority.d'),str(OUT/'inputs/native/authority.cpp'),'-o',str(binary),*libs])
 paths=shlex.split((OUT/'authority.d').read_text().replace('\\\n',' ').split(':',1)[1]);dependencies={str(Path(p).resolve()):sha(Path(p).resolve()) for p in paths}
 assert not any(p.startswith('/usr/include/hyprland') or p.startswith(str(OWNER)+'/') for p in dependencies)
 symbols=run('core-symbols',['nm','-D','-C',core['path']])
 for symbol in ['Desktop::WindowPolicy::applyMinimized','Desktop::WindowPolicy::isMinimized','Render::SceneTrace::snapshots','IHyprRenderer::makeFamilyCropFB','IHyprRenderer::familyCropBounds','IHyprRenderer::familyObservationCropBounds']:assert symbol in symbols,symbol
 defined=run('plugin-symbols',['nm','-D','--defined-only',str(binary)])
 for symbol in ['pluginInit','pluginExit','pluginAPIVersion']:assert symbol in defined,symbol
 linked={}
 for name,target in [('core',core['path']),('plugin',str(binary))]:
  text=run(name+'-ldd',['ldd',target]);assert 'not found' not in text
  for line in text.splitlines():
   for word in line.split():
    if word.startswith('/') and Path(word).is_file():p=Path(word).resolve();linked[str(p)]=sha(p)
 exports=set()
 for i,p in enumerate([core['path'],*sorted(linked)]):
  for line in run('provider-symbols-'+str(i),['nm','-D','--defined-only',p]).splitlines():
   words=line.split()
   if len(words)>=3:symbol=words[-1].replace('@@','@');exports.add(symbol);exports.add(symbol.split('@')[0])
 requested=[];missing=[]
 for line in run('plugin-undefined',['nm','-D','--undefined-only',str(binary)]).splitlines():
  words=line.split()
  if len(words)==2 and words[0]=='U':requested.append(words[1]);missing.extend([] if words[1] in exports else [words[1]])
 assert not missing,missing
 for rel,wanted in inputs.items():assert sha(ROOT/rel)==sha(OUT/'inputs'/rel)==wanted,rel
 for rel,wanted in headers.items():assert sha(Path(core['buildReport']).parent/'owning-headers'/rel)==sha(OUT/'owning-headers'/rel)==wanted,rel
 for section in [dependencies,linked,core_report['dependencies']]:
  for p,wanted in section.items():assert sha(p)==wanted,p
 verify_component();assert sha(core['path'])==core['sha256']
 for rel,wanted in upstream['sourceFiles'].items():assert sha(ROOT/rel)==wanted,rel
 for section in ['tools','linkDependencies','linkedLibraries']:
  for path,wanted in core_report[section].items():assert sha(path)==wanted,path
 closure={'passed':True,'nativeAcceptance':False,'scope':'Strong-symbol closure only; no loading acceptance','core':core,'plugin':{'path':str(binary),'sha256':sha(binary)},'strongUndefinedCount':len(requested),'missingSymbols':missing,'linkedLibraries':linked,'providerExportCount':len(exports)}
 (OUT/'link-closure.json').write_text(json.dumps(closure,indent=2)+'\n')
 r.update(passed=True,core=core,binary=str(binary),binarySHA256=sha(binary),inputs=inputs,owningHeaders=headers,dependencies=dependencies,linkedLibraries=linked,inheritedPolicies=inherited_policy,sourceLineage=upstream,strongUndefinedCount=len(requested),missingSymbols=missing,providerExportCount=len(exports),linkClosureReport=str(OUT/'link-closure.json'),linkClosureReportSHA256=sha(OUT/'link-closure.json'),tools={str(Path(shutil.which(name)).resolve()):sha(Path(shutil.which(name)).resolve()) for name in ['g++','pkg-config','nm','ldd']})
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
report_path=OUT/'report.json';report_path.write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
 descriptor={'result':'pass','binary':core['path'],'sha256':core['sha256'],'buildReport':core['buildReport'],'buildReportSHA256':core['buildReportSHA256'],'nativeAcceptance':False,'installed':False,'scope':r['scope'],'plugin':{'path':str(binary),'sha256':sha(binary)},'pluginBuildReport':str(report_path),'pluginBuildReportSHA256':sha(report_path),'linkClosureReport':r['linkClosureReport'],'linkClosureReportSHA256':r['linkClosureReportSHA256'],'coreComponentManifest':str(component_path),'coreComponentManifestSHA256':upstream['coreManifestSHA256']}
 (ROOT/'native-build-report.json').write_text(json.dumps(descriptor,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(report_path),'error':r.get('error')}),flush=True);raise SystemExit(not r['passed'])

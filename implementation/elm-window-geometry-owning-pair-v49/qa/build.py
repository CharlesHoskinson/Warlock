"""Protected CPU compile of negotiated geometry observation against frozen V34/V28."""
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
r={'passed':False,'nativeAcceptance':False,'installed':False,'scope':'Negotiated geometry-effect source actual compile against exact V40 owning headers/core, strong-symbol closure only; no loading, GUI, model or menu acceptance','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,command):
 p=subprocess.run(command,capture_output=True,text=True,timeout=240)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 r['commands'].append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr[-6000:]
 return p.stdout
try:
 assert sha(MANIFEST)==MANIFEST_SHA
 manifest=json.loads(MANIFEST.read_text());assert manifest['passed'] and not manifest['nativeAcceptance']
 for rel,wanted in manifest['files'].items():assert sha(PARENT/rel)==wanted,rel
 previous_path=PARENT/manifest['buildReport'];assert sha(previous_path)==manifest['buildReportSHA256']
 previous=json.loads(previous_path.read_text());assert previous['passed'] and len(previous['owningHeaders'])==660
 upstream=json.loads((ROOT/'upstream.json').read_text())
 source_root=Path(upstream['source'])
 for rel,wanted in upstream['sourceFiles'].items():assert sha(source_root/rel)==sha(ROOT/rel)==wanted,rel
 for rel,wanted in previous['inputs'].items():assert sha(PARENT/rel)==sha(previous_path.parent/'inputs'/rel)==wanted,rel
 for section in ['dependencies','linkedLibraries','tools']:
  for p,wanted in previous[section].items():assert sha(p)==wanted,p
 component_root=Path(upstream['coreComponent']);descriptor_path=component_root/'core/native-build-report.json';descriptor_sha=sha(descriptor_path);descriptor=json.loads(descriptor_path.read_text());assert descriptor['result']=='pass'
 core_report=json.loads(Path(descriptor['buildReport']).read_text());assert core_report['passed'] and len(core_report['owningHeaders'])==691 and len(core_report['rebuiltArchiveMembers'])==17
 core={'path':descriptor['binary'],'sha256':descriptor['sha256'],'buildReport':descriptor['buildReport'],'buildReportSHA256':descriptor['buildReportSHA256'],'versionHeaderSHA256':core_report['owningVersionHeaderSHA256'],'componentManifest':str(component_root/'component-manifest.json'),'componentManifestSHA256':upstream['coreManifestSHA256'],'inventoryBase':str(REPO)}
 assert sha(core['path'])==core['sha256'] and sha(core['buildReport'])==core['buildReportSHA256']
 assert sha(OWNER/'src/version.h')==core['versionHeaderSHA256']
 component_path=Path(core['componentManifest']);assert sha(component_path)==core['componentManifestSHA256']
 component=json.loads(component_path.read_text());assert component['passed'] and len(component['files'])==1553 and not component['pluginABIQualified']
 audit_path=Path(component['consumerAudit']);assert sha(audit_path)==component['consumerAuditSHA256'];audit=json.loads(audit_path.read_text());assert audit['passed'] and len(audit['actualConsumerMembers'])==17 and len(audit['patchedObjects'])==10
 closure_path=Path(descriptor['closureReport']);assert sha(closure_path)==descriptor['closureReportSHA256'];core_closure=json.loads(closure_path.read_text());assert core_closure['passed']
 limits_path=Path(core_closure['limitsReport']);assert sha(limits_path)==core_closure['limitsReportSHA256'] and json.loads(limits_path.read_text())['passed']
 def verify_component():
  for entry in component['files']:
   p=Path(core['inventoryBase'])/entry['path']
   if 'symlink' in entry:assert p.is_symlink() and str(p.readlink())==entry['symlink'],str(p)
   else:assert p.is_file() and not p.is_symlink() and p.stat().st_size==entry['size'] and sha(p)==entry['sha256'],str(p)
 verify_component()
 core_report=json.loads(Path(core['buildReport']).read_text());assert core_report['passed'] and core_report['binarySHA256']==core['sha256']
 for p,wanted in core_report['dependencies'].items():assert sha(p)==wanted,p
 closure=core_closure;assert not closure['missingSymbols'] and closure['binary']==core['path'] and closure['sha256']==core['sha256']
 # Capture only our native/candidate/build/test inputs; concurrent adapters remain outside this build.
 files=[*sorted((ROOT/'native').rglob('*')),*sorted((ROOT/'candidate').rglob('*')),*sorted((ROOT/'qa').glob('*.py')),ROOT/'upstream.json']
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
  rel='candidate/'+name;wanted=previous['inputs'][rel];p=previous_path.parent/'inputs'/rel;assert sha(p)==wanted
  dest=OUT/'inputs'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert sha(dest)==wanted,rel
  else:shutil.copy2(p,dest);dest.chmod(0o444)
 inherited_policy={name:previous['inputs']['candidate/'+name] for name in ['SceneModal.hpp','WindowPolicy.hpp','SceneTrace.hpp']}
 include=OUT/'include';include.mkdir();(include/'hyprland').symlink_to(OUT/'owning-headers',target_is_directory=True)
 flags=shlex.split(run('flags',['pkg-config','--cflags','json-glib-1.0','pixman-1','libdrm','libinput','wayland-server','libeis-1.0']))
 libs=shlex.split(run('libs',['pkg-config','--libs','json-glib-1.0']))
 binary=OUT/'elm-window-geometry-authority.so'
 run('compile',['g++','-std=c++23','-O2','-fPIC','-shared','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-isystem',str(include),'-isystem',str(OUT/'owning-headers'),'-isystem',str(OUT/'owning-headers/src'),'-isystem',str(OUT/'owning-headers/protocols'),'-I'+str(OUT/'inputs/candidate'),*flags,'-MD','-MF',str(OUT/'authority.d'),str(OUT/'inputs/native/authority.cpp'),'-o',str(binary),*libs])
 paths=shlex.split((OUT/'authority.d').read_text().replace('\\\n',' ').split(':',1)[1]);dependencies={str(Path(p).resolve()):sha(Path(p).resolve()) for p in paths}
 assert not any(p.startswith('/usr/include/hyprland') or p.startswith(str(OWNER)+'/') for p in dependencies)
 symbols=run('core-symbols',['nm','-D','-C',core['path']])
 for symbol in ['Desktop::WindowPolicy::applyMinimized','Desktop::WindowPolicy::isMinimized','Render::SceneTrace::snapshots']:assert symbol in symbols,symbol
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
 verify_component();assert sha(MANIFEST)==MANIFEST_SHA and sha(core['path'])==core['sha256']
 for rel,wanted in upstream['sourceFiles'].items():assert sha(source_root/rel)==sha(ROOT/rel)==wanted,rel
 assert sha(descriptor_path)==descriptor_sha
 for section in ['tools','linkDependencies','linkedLibraries']:
  for path,wanted in core_report[section].items():assert sha(path)==wanted,path
 link_report={'passed':True,'nativeAcceptance':False,'scope':'Strong dynamic symbol closure against exact V40 core and hashed dynamic dependencies; no loading acceptance','core':core['path'],'coreSHA256':core['sha256'],'plugin':str(binary),'pluginSHA256':sha(binary),'strongUndefinedCount':len(requested),'missingSymbols':missing,'linkedLibraries':linked,'providerExportCount':len(exports)}
 (OUT/'link-closure.json').write_text(json.dumps(link_report,indent=2)+'\n')
 r.update(passed=True,linkClosureReport=str(OUT/'link-closure.json'),linkClosureReportSHA256=sha(OUT/'link-closure.json'),inputs=inputs,owningHeaders=headers,dependencies=dependencies,linkedLibraries=linked,inheritedPolicies=inherited_policy,parentManifest=str(MANIFEST),parentManifestSHA256=MANIFEST_SHA,parentBuildReport=str(previous_path),parentBuildReportSHA256=sha(previous_path),core=core,coreDependencies=core_report['dependencies'],coreLinkDependencies=core_report['linkDependencies'],coreDescriptor=str(descriptor_path),coreDescriptorSHA256=sha(descriptor_path),coreClosureReport=str(closure_path),coreClosureReportSHA256=sha(closure_path),coreConsumerAudit=str(audit_path),coreConsumerAuditSHA256=sha(audit_path),coreLimitsReport=str(limits_path),coreLimitsReportSHA256=sha(limits_path),sourceLineage=upstream,binary=str(binary),binarySHA256=sha(binary),strongUndefinedCount=len(requested),missingSymbols=missing,providerExportCount=len(exports),tools={str(Path(shutil.which(name)).resolve()):sha(Path(shutil.which(name)).resolve()) for name in ['g++','pkg-config','nm','ldd']})
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}),flush=True)
raise SystemExit(not r['passed'])

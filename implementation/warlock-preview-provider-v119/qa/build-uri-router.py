"""Immutable-source Elm/native host build; protected launcher required."""
import hashlib,json,os,resource,shlex,shutil,subprocess,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
files={}
for base in ['src','native','adapter','assets','qa']:
 for p in (ROOT/base).glob('*'):
  if not p.is_file() or p.name=='current-build.json':continue
  target=OUT/'inputs'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);files[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(ROOT/'elm.json',OUT/'inputs/elm.json')
files['elm.json']=hashlib.sha256((ROOT/'elm.json').read_bytes()).hexdigest()
from toolchain import verify,command as pin_command,checks as toolchain_checks
heldToolchain=verify();shutil.copytree(ROOT/heldToolchain['elmHome'],OUT/'mutable-elm-home')
rows=[]
def run(name,cmd):
 verify();cmd=pin_command(cmd);build_env=dict(os.environ,ELM_HOME=str(OUT/'mutable-elm-home'));p=subprocess.run(cmd,cwd=OUT/'inputs',capture_output=True,text=True,timeout=180,env=build_env);verify();toolchain_checks.append({'name':name,'beforeAfterVerified':True});(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);rows.append({'name':name,'command':cmd,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p.stdout
report={'elmToolchain':heldToolchain,'elmToolchainBeforeAfterChecks':toolchain_checks,'passed':False,'inputs':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual metadata/icon ownership and locked fallback concealment in the same immutable full Elm provider; native fallback acceptance remains pending. Full GUI519-derived explicit generated backdrop scope/FD4 owned mapping and original transparent family branch. Current color revision reconciles with retained original image/job, same coverage/URI/receipt/physical retirement. Full GUI519-derived shared physical broker for URI readers and paced native demand, exact retirement-before-poll recovery and unchanged full optimized Elm package. Typed own native child enrollment, strict ineligible native492 scope and terminal Broker proof projection/ack through actual host; forked sockets and physical-retirement tests. No eligible capture or native acceptance'}
try:
 run('authority-config-identity',['/usr/bin/python3','-B','qa/authority-config.py'])
 run('context-syntax',['node','--check','assets/context.js'])
 run('adapter-syntax',['node','--check','assets/adapter.js'])
 run('popup-adapter-syntax',['node','--check','assets/popup-adapter.js'])
 run('popup-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Popup.elm','--optimize','--output=assets/popup.js'])
 run('native-source-replay-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/NativePreviewSourceReplay.elm','--optimize','--output=assets/native-source-replay.js'])
 run('family-source-replay-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/NativeFamilyPreviewSourceReplay.elm','--optimize','--output=assets/family-source-replay.js'])
 run('preview-replay-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/PreviewPresenterReplay.elm','--optimize','--output=assets/preview-replay.js'])
 run('feedback-replay-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/PreviewFeedbackReplay.elm','--optimize','--output=assets/feedback-replay.js'])
 run('typed-source-presenter-replay',['node','qa/source-presenter-replay.js','assets/preview-replay.js','qa/native-source-fixture.json'])
 run('typed-family-presenter-replay',['node','qa/family-presenter-replay.js','assets/preview-replay.js','qa/family-source-fixture.json'])
 run('typed-source-denial-replay',['node','qa/denial-replay.js','assets/preview-replay.js','qa/native-source-fixture.json'])
 run('catalog-replay-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/PreviewCatalogReplay.elm','--optimize','--output=assets/catalog-replay.js'])
 run('catalog-enrollment-replay',['node','qa/catalog-replay.js','assets/catalog-replay.js','qa/native-source-fixture.json'])
 run('metadata-replay-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/PreviewMetadataReplay.elm','--optimize','--output=assets/metadata-replay.js'])
 run('metadata-privacy-replay',['node','qa/metadata-replay.js','assets/metadata-replay.js','qa/native-source-fixture.json'])
 run('bar-adapter-syntax',['node','--check','assets/bar-adapter.js'])
 run('bar-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Bar.elm','--optimize','--output=assets/bar.js'])
 run('elm-build',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm','--optimize','--output=assets/elm.js'])
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 run('host-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/'host.d'),'-c','native/shared-host.c','-o',str(OUT/'host.o'),*flags])
 for name in ['preview_uri.cpp','preview-uri-router.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp']:
  run(name+'-compile',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/(name+'.d')),'-c','native/'+name,'-o',str(OUT/(name+'.o')),*flags])
 run('host-build',['g++',str(OUT/'host.o'),str(OUT/'preview_uri.cpp.o'),str(OUT/'preview_icons.cpp.o'),str(OUT/'preview-uri-webkit.cpp.o'),str(OUT/'preview-uri-router.cpp.o'),str(OUT/'preview-provider-bootstrap.cpp.o'),str(OUT/'client-producer.cpp.o'),str(OUT/'imported-clients.cpp.o'),'-o',str(OUT/'elm-host'),*flags])
 run('window-catalog-test-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/window-catalog-test.cpp','-o',str(OUT/'window-catalog-tests'),*flags])
 run('window-catalog-admission-tests',[str(OUT/'window-catalog-tests')])
 run('metadata-icon-test-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/metadata-icon-test.cpp','native/preview_icons.cpp','-o',str(OUT/'metadata-icon-tests'),*flags])
 run('metadata-icon-physical-tests',[str(OUT/'metadata-icon-tests')])
 run('family-frame-test-build',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','native/family-frame-test.cpp','-o',str(OUT/'family-frame-tests'),*flags])
 run('family-frame-tests',[str(OUT/'family-frame-tests')])
 run('family-fd-test-build',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','native/family-fd-test.cpp','-o',str(OUT/'family-fd-tests'),*flags])
 run('family-fd-physical-tests',[str(OUT/'family-fd-tests')])
 run('family-source-test-build',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','native/family-source-test.cpp','-o',str(OUT/'family-source-tests'),*flags])
 run('family-source-coupled-decoder',['node','qa/family-source-replay.js','assets/family-source-replay.js',str(OUT/'family-source-tests'),'qa/family-source-fixture.json'])
 run('backdrop-frame-test-build',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','native/backdrop-frame-test.cpp','-o',str(OUT/'backdrop-frame-tests'),*flags])
 run('backdrop-frame-tests',[str(OUT/'backdrop-frame-tests')])
 run('backdrop-fd-test-build',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','native/backdrop-fd-test.cpp','-o',str(OUT/'backdrop-fd-tests'),*flags])
 run('backdrop-fd-physical-tests',[str(OUT/'backdrop-fd-tests')])
 run('backdrop-source-coupled-decoder',['node','qa/backdrop-source-replay.js','assets/family-source-replay.js',str(OUT/'family-source-tests'),'qa/backdrop-source-fixture.json'])
 run('backdrop-source-general-decoder',['node','qa/backdrop-general-replay.js','assets/native-source-replay.js','qa/backdrop-source-fixture.json'])
 run('typed-backdrop-presenter-replay',['node','qa/backdrop-presenter-replay.js','assets/preview-replay.js','qa/backdrop-source-fixture.json'])
 run('geometry-carrier-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','native/geometry-carrier-test.c','-o',str(OUT/'geometry-carrier-tests'),str(OUT/'preview_uri.cpp.o'),str(OUT/'preview_icons.cpp.o'),str(OUT/'preview-uri-webkit.cpp.o'),str(OUT/'preview-uri-router.cpp.o'),str(OUT/'preview-provider-bootstrap.cpp.o'),str(OUT/'client-producer.cpp.o'),str(OUT/'imported-clients.cpp.o'),*flags,'-lstdc++'])
 run('geometry-carrier-tests',[str(OUT/'geometry-carrier-tests')])
 run('reconciliation-carrier-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','native/reconciliation-carrier-test.c','-o',str(OUT/'reconciliation-carrier-tests'),str(OUT/'preview_uri.cpp.o'),str(OUT/'preview_icons.cpp.o'),str(OUT/'preview-uri-webkit.cpp.o'),str(OUT/'preview-uri-router.cpp.o'),str(OUT/'preview-provider-bootstrap.cpp.o'),str(OUT/'client-producer.cpp.o'),str(OUT/'imported-clients.cpp.o'),*flags,'-lstdc++'])
 run('reconciliation-carrier-tests',[str(OUT/'reconciliation-carrier-tests')])
 run('context-guard-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','native/shared-context-test.c','-o',str(OUT/'context-guard-tests'),str(OUT/'preview_uri.cpp.o'),str(OUT/'preview_icons.cpp.o'),str(OUT/'preview-uri-webkit.cpp.o'),str(OUT/'preview-uri-router.cpp.o'),str(OUT/'preview-provider-bootstrap.cpp.o'),str(OUT/'client-producer.cpp.o'),str(OUT/'imported-clients.cpp.o'),*flags,'-lstdc++'])
 run('context-guard-tests',[str(OUT/'context-guard-tests')])
 run('context-keys-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/context-keys-test.c','-o',str(OUT/'context-key-tests')])
 run('context-keys-tests',[str(OUT/'context-key-tests')])
 run('imported-c-boundary-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/imported-clients-boundary-test.c','-o',str(OUT/'imported-clients-boundary-tests'),str(OUT/'imported-clients.cpp.o'),str(OUT/'preview-provider-bootstrap.cpp.o'),str(OUT/'preview_uri.cpp.o'),str(OUT/'preview_icons.cpp.o'),*flags,'-lstdc++'])
 run('imported-c-boundary-tests',[str(OUT/'imported-clients-boundary-tests')])
 run('qa-reader-control-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/qa-reader-control-test.c','-o',str(OUT/'qa-reader-control-tests'),*flags])
 run('qa-reader-control-tests',[str(OUT/'qa-reader-control-tests')])
 run('host-tests',[str(OUT/'elm-host'),'--self-test'])
 run('provider-grant-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/provider-grant-test.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(OUT/'provider-grant-tests'),*flags])
 run('provider-grant-tests',[str(OUT/'provider-grant-tests')])
 run('provider-delivery-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/provider-delivery-test.cpp','native/preview_uri.cpp','-o',str(OUT/'provider-delivery-tests'),*flags])
 run('provider-delivery-tests',[str(OUT/'provider-delivery-tests')])
 run('provider-elm-delivery-replay',['node','qa/delivery-replay.js',str(OUT/'provider-delivery-tests'),'assets/preview-replay.js'])
 run('client-frame-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/client-frame-test.cpp','-o',str(OUT/'client-frame-tests'),*flags])
 run('client-frame-tests',[str(OUT/'client-frame-tests')])
 run('client-command-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/client-command-test.cpp','native/preview_uri.cpp','-o',str(OUT/'client-command-tests'),*flags])
 run('client-command-tests',[str(OUT/'client-command-tests')])
 run('client-observation-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/client-observation-test.cpp','native/preview_uri.cpp','-o',str(OUT/'client-observation-tests'),*flags])
 run('client-observation-tests',[str(OUT/'client-observation-tests')])
 run('client-denial-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/client-denial-test.cpp','native/preview_uri.cpp','-o',str(OUT/'client-denial-tests'),*flags])
 run('client-denial-tests',[str(OUT/'client-denial-tests')])
 run('backdrop-denial-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/backdrop-denial-test.cpp','native/preview_uri.cpp','-o',str(OUT/'backdrop-denial-tests'),*flags])
 run('backdrop-denial-tests',[str(OUT/'backdrop-denial-tests')])
 run('typed-backdrop-denial-replay',['node','qa/backdrop-denial-replay.js','assets/preview-replay.js','qa/backdrop-denial-fixture.json'])
 run('client-resume-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/client-resume-test.cpp','native/preview_uri.cpp','-o',str(OUT/'client-resume-tests'),*flags])
 run('client-resume-tests',[str(OUT/'client-resume-tests')])
 run('client-retained-presentation-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/client-retained-presentation-test.cpp','native/preview_uri.cpp','-o',str(OUT/'client-retained-presentation-tests'),*flags])
 run('client-retained-presentation-tests',[str(OUT/'client-retained-presentation-tests')])
 run('client-import-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/client-import-test.cpp','native/preview_uri.cpp','-o',str(OUT/'client-import-tests'),*flags])
 run('client-import-tests',[str(OUT/'client-import-tests')])
 run('imported-lifecycle-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/imported-lifecycle-test.cpp','native/preview_uri.cpp','-o',str(OUT/'imported-lifecycle-tests'),*flags])
 run('imported-lifecycle-tests',[str(OUT/'imported-lifecycle-tests')])
 run('provider-ownership-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/provider-ownership-test.cpp','native/preview_uri.cpp','-o',str(OUT/'provider-ownership-tests'),*flags])
 run('provider-ownership-tests',[str(OUT/'provider-ownership-tests')])
 run('receiver-extension-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/receiver-extension-test.cpp','native/preview_uri.cpp','-o',str(OUT/'receiver-extension-tests'),*flags])
 run('receiver-extension-physical-tests',[str(OUT/'receiver-extension-tests')])
 run('delivery-extension-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/delivery-extension-test.cpp','native/preview_uri.cpp','-o',str(OUT/'delivery-extension-tests'),*flags])
 run('delivery-extension-physical-tests',[str(OUT/'delivery-extension-tests')])
 run('imported-admission-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/imported-admission-test.cpp','-o',str(OUT/'imported-admission-tests'),*flags])
 run('imported-admission-tests',[str(OUT/'imported-admission-tests')])
 run('dynamic-enrollment-build',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/dynamic-enrollment-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(OUT/'dynamic-enrollment-tests'),*flags])
 run('dynamic-enrollment-tests',[str(OUT/'dynamic-enrollment-tests')])
 run('surface-test-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/surface-test.c','-o',str(OUT/'surface-tests'),*flags])
 run('surface-tests',[str(OUT/'surface-tests')])
 def inventory(paths):
  rows={}
  for path in paths:
   p=Path(path).absolute();target=p.resolve(strict=True)
   rows[str(p)]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size,'resolved':str(target)}
  return rows
 deps=[]
 for dependency_file in ['host.d','preview_uri.cpp.d','preview_icons.cpp.d','preview-uri-webkit.cpp.d','preview-provider-bootstrap.cpp.d','client-producer.cpp.d','imported-clients.cpp.d']:
  dependency_text=(OUT/dependency_file).read_text().replace('\\\n',' ');deps.extend(shlex.split(dependency_text.split(':',1)[1]))
 deps=sorted(set(deps))
 report['compilerDependencies']=inventory([str((OUT/'inputs'/p).resolve()) if not Path(p).is_absolute() else p for p in deps])
 toolpaths=[shutil.which(name) for name in ['cc','g++','pkg-config','node','npm','as','ld','ldd']]
 toolpaths+=[subprocess.check_output(['cc','-print-prog-name=cc1'],text=True).strip()]
 toolpaths+=[subprocess.check_output(['g++','-print-prog-name=cc1plus'],text=True).strip(),subprocess.check_output(['g++','-print-prog-name=collect2'],text=True).strip()]
 report['tools']=inventory(toolpaths)
 libs=run('linked-libraries',['ldd',str(OUT/'elm-host')]);library_paths=[]
 for line in libs.splitlines():
  fields=line.split()
  if '=>' in fields:
   path=fields[fields.index('=>')+1]
   if path.startswith('/'):library_paths.append(path)
  elif fields and fields[0].startswith('/'):library_paths.append(fields[0])
 report['linkedLibraries']=inventory(library_paths)
 report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'inputs/assets').glob('*') if p.is_file()}
 report['compiledAssetPackage']={'path':str(OUT/'inputs/assets'),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'inputs/assets').glob('*') if p.is_file()},'scope':'Exact current optimized Main/Bar/Popup and source adapters/styles; use this package rather than inherited source precompiled JS'}
 assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value for name,value in files.items()), 'Source changed during build'
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['commands']=rows
if (OUT/'elm-host').exists():report['binarySHA256']=hashlib.sha256((OUT/'elm-host').read_bytes()).hexdigest()
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])

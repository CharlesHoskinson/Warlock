"""Actual adopted mapped terminal wire drains the compiled Elm owner and native journal."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];plugin=root.parent/'warlock-family-style-crop-capture-v19'
out=root/'qa'/('capture-resource-elm-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
buildPath=root/'qa/build-1791344076098383540/report.json';build=json.loads(buildPath.read_text());assert build['passed']
assets=pathlib.Path(build['compiledAssetPackage']['path']);assert sha(assets/'preview-replay.js')==build['compiledAssetPackage']['files']['preview-replay.js']
elmInputs={k:v for k,v in build['inputs'].items() if k.startswith(('src/','assets/','adapter/')) or k=='elm.json'}
assert all(sha(root/k)==v for k,v in elmInputs.items())
inputs={str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()}
inputs.update({k:sha(root/k) for k in ['qa/capture-resource-elm-replay.js',str(pathlib.Path(__file__).relative_to(root))]})
report={'passed':False,'inputs':inputs,'elmSourceInputs':elmInputs,'elmBuildReport':str(buildPath),'elmBuildReportSHA256':sha(buildPath),'compiledElmSHA256':sha(assets/'preview-replay.js'),'pluginHeaderSHA256':sha(plugin/'native/capture-resources.hpp'),'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual current controlled C/bootstrap/socket/SCM_RIGHTS/mapping/Broker/resource drain sends original source/request and physical Released/Cancelled terminal wires to actual optimized PreviewPresenter/PreviewLifecycle. Unknown capture after lost offer and actual post-transfer result allocation exception retain original Elm cancellation; unseen Released is not terminal cancellation, exact final Cancelled yields original ACK that drains real native journal. Distinct incarnation/final actor confirmation and normal child exits retained. Compiled Elm package derives earlier full95 with unchanged Elm source, not a claim of current native host build. No Core pixels/WebKit/native GUI/full-release acceptance.'}
def run(name,args,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in inputs:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 shutil.copy2(plugin/'native/capture-resources.hpp',out/'inputs/native/capture-resources.hpp')
 shutil.copy2(assets/'preview-replay.js',out/'inputs/preview-replay.js')
 header=out/'inputs/native/client_import.hpp';s=header.read_text();old='namespace preview::bridge {';assert s.count(old)==1
 s=s.replace(old,old+'\nextern thread_local int mappedResourceAllocationFault;extern bool mappedResourceFaultEnabled;')
 old='auto result=broker.allocate(entry,job,payload,expires);';assert s.count(old)==1
 header.write_text(s.replace(old,'if(mappedResourceFaultEnabled)mappedResourceAllocationFault=2;\n        '+old))
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 run('compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/capture-resource-elm-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags])
 evidence=json.loads(run('actual-compiled-elm-native-final-ACK',['node','qa/capture-resource-elm-replay.js',str(out/'checks'),'preview-replay.js']).stdout)
 assert evidence['passed'] and evidence['actualCompiledElm'] and evidence['actualMappedNativeACK'] and evidence['normalOwnedExits']==2
 assert all(sha(root/rel)==value for rel,value in inputs.items()) and all(sha(root/rel)==value for rel,value in elmInputs.items())
 assert sha(plugin/'native/capture-resources.hpp')==report['pluginHeaderSHA256'] and sha(buildPath)==report['elmBuildReportSHA256']
 report.update(passed=True,evidence=evidence,controlledFaultHeaderSHA256=sha(header))
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1400]}),flush=True);sys.exit(not report['passed'])

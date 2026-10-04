import hashlib,importlib.util,json,time
from pathlib import Path
root=Path('/home/hoskinson/omarchy-windows-parity');p=Path(__file__).resolve().parents[1];runtime=root/'implementation/elm-geometry-producer-runtime-v185';out=p/'qa'/('verify-'+str(time.time_ns()));out.mkdir();records={}
def verify(path,sha):
 f=Path(path);actual=hashlib.sha256(f.read_bytes()).hexdigest();assert actual==sha,str(f);records[str(f)]=actual
manifest=runtime/'component-manifest.json';packet=json.loads(manifest.read_text())
for path,row in packet['files'].items():verify(runtime/path,row['sha256'])
meta=json.loads((runtime/'native-build-report.json').read_text());verify(meta['pluginBuildReport'],meta['pluginBuildReportSHA256']);verify(meta['linkClosureReport'],meta['linkClosureReportSHA256'])
build=json.loads(Path(meta['pluginBuildReport']).read_text());assert build['passed'] and build['missingSymbols']==[]
assert build['core']['path']==meta['binary'] and build['core']['sha256']==meta['sha256']
verify(meta['binary'],meta['sha256']);verify(meta['plugin']['path'],meta['plugin']['sha256'])
for path,sha in build['linkedLibraries'].items():verify(path,sha)
for path,sha in build['dependencies'].items():verify(path,sha)
spec=importlib.util.spec_from_file_location('reviewed_185_preflight',runtime/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
host.verify_inputs();row,lib=host.aq_tuple();assert Path(row['library'])==lib
assert issubclass(host.PrivateHyprSession,host.original.PrivateHyprSession)
assert issubclass(host.ReviewedWestonHost,host.original.PrivateWestonHost)
report={'passed':True,'linkedLibrariesVerified':len(build['linkedLibraries']),'verifiedFiles':len(records),'files':records,'hostImportedWithoutSession':True,'preparedManifest':str(manifest),'preparedManifestSHA256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'nativeAcceptance':False,'consumerAcceptance':False,'scope':'Protected CPU hash/library and actual host import preflight; no session constructed/plugin loaded/GUI'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'linkedLibraries':len(build['linkedLibraries']),'passed':True}))

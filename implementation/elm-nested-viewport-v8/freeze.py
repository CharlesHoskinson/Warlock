import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1), 'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parent
OUT=sorted(ROOT.glob('build-*/report.json'))[-1].parent
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((OUT/'report.json').read_text());assert report['passed']
assert digest(ROOT/'build.py')==report['runnerSHA256']
assert digest(report['library'])==report['librarySHA256']
assert b'checks: 47' in (OUT/'presentation-tests.stdout').read_bytes()
assert report['publicHeadersUnchanged'] and report['parentPreserved'] and not report['missingParentSymbols']
for relative,value in report['sources'].items():assert digest(ROOT/'candidate'/relative)==value,relative
for path,value in report['dependencies'].items():assert digest(path)==value,path
assert digest(ROOT/'test-dimensions.cpp')==report['testSourceSHA256']
assert digest(ROOT/'test-presentation.cpp')==report['presentationTestSHA256']
for path,value in report['protocolInputs'].items():assert digest(path)==value,path
for relative,value in report['capturedInputs'].items():assert digest(OUT/'inputs'/relative)==value,relative
review=json.loads((ROOT/'independent-review.json').read_text())
for relative,value in review['sources'].items():assert digest(ROOT/relative)==value,relative
upstream=json.loads((ROOT/'upstream.json').read_text())
assert digest(upstream['failedNativeReport'])==upstream['failedNativeReportSHA256']
assert json.loads(Path(upstream['failedNativeReport']).read_text())['passed'] is False
entries=[]
for path in sorted(ROOT.rglob('*')):
 if path.name=='component-manifest.json':continue
 if path.is_symlink():entries.append({'path':str(path.relative_to(ROOT)),'symlink':os.readlink(path)})
 elif path.is_file():entries.append({'path':str(path.relative_to(ROOT)),'sha256':digest(path),'size':path.stat().st_size})
manifest={'schema':1,'passed':True,'component':'AQ viewport/ACK generation/committed mapping source and build component','nativeAcceptance':False,'releaseAcceptance':False,'parentMappingQualified':False,'testPreflightImplemented':True,'failedNativeCampaignRetained':True,'scope':'47 production helper checks and full AQ compile only; native parent presentation and input recipients remain unqualified','buildReport':str(OUT/'report.json'),'buildReportSHA256':digest(OUT/'report.json'),'files':entries}
output=ROOT/'component-manifest.json';assert not output.exists();output.write_text(json.dumps(manifest,indent=2)+'\n');print(output,flush=True)

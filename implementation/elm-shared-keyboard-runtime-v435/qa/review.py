import hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pair=json.loads((ROOT/'qa/build-pair-manifest.json').read_text());accept=Path(pair['keyboardAcceptance']);assert sha(accept)==pair['keyboardAcceptanceSHA256'];a=json.loads(accept.read_text());assert a['passed'] and a['nativeAcceptance'] and not a['releaseAcceptance']
for e in a['files']:
 p=REPO/e['path']
 if 'symlink' in e:assert p.is_symlink() and os.readlink(p)==e['symlink']
 else:assert not p.is_symlink() and sha(p)==e['sha256']
component=Path(a['componentManifest']);assert sha(component)==a['componentManifestSHA256'];c=json.loads(component.read_text());assert c['passed']
for e in c['files']:
 p=component.parent/e['path']
 if 'symlink' in e:assert os.readlink(p)==e['symlink']
 else:assert sha(p)==e['sha256']
for row in a['nativeReports']:
 p=Path(row['report']);assert sha(p)==row['reportSHA256'];j=json.loads(p.read_text());assert j['passed'] and j['cleanupPassed'] and all(check['passed'] for check in j['checks'])
old=REPO/'implementation/elm-parent-transport-retirement-v105';new=component.parent
headers=[]
for p in (old/'candidate/include').rglob('*'):
 if p.is_file():q=new/'candidate'/p.relative_to(old/'candidate');assert sha(p)==sha(q);headers.append(str(p.relative_to(old/'candidate')))
assert {str(p.relative_to(old/'candidate/include')) for p in (old/'candidate/include').rglob('*') if p.is_file()}=={str(p.relative_to(new/'candidate/include')) for p in (new/'candidate/include').rglob('*') if p.is_file()}
previous=json.loads((REPO/'implementation/elm-geometry-bounds-runtime-v420/aq-tuple.json').read_text());candidate=json.loads((ROOT/'aq-tuple.json').read_text());symbols=[]
for filename in [previous['library'],candidate['library']]:
 output=subprocess.run(['/usr/bin/nm','-D','--defined-only',filename],capture_output=True,text=True,timeout=10);assert output.returncode==0;symbols.append({line.split()[-1] for line in output.stdout.splitlines() if line.split()})
assert not symbols[0]-symbols[1],'Missing existing exported symbols'
assert sha(ROOT/'candidate_host.py')==sha(REPO/'implementation/elm-geometry-bounds-runtime-v420/candidate_host.py')
for entry in pair['nativePair'].values():assert sha(Path(entry['path']))==entry['sha256']
out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir();report={'passed':True,'scope':'Independent158 frozen evidence/header/export review for proposed coherent435 runtime; no current shared native acceptance','nativeAcceptance':False,'headersIdentical':len(headers),'oldExportsPreserved':len(symbols[0]),'independentNativeCheckExecutions':a['nativeCheckExecutions'],'acceptanceSHA256':sha(accept),'librarySHA256':candidate['librarySHA256']};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(report,report=str(out/'report.json'))))

import hashlib,json,os,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):s=p.stat();return {'sha256':sha(p),'size':s.st_size,'mode':oct(stat.S_IMODE(s.st_mode))}
reports=[sorted((ROOT/'qa').glob(prefix+'-*/report.json'))[-1].parent.name for prefix in ('preflight','source-test','helper-test','acquisition-test','closure','fault-preflight','geometry-reply')]
for n in reports:assert json.loads((ROOT/'qa'/n/'report.json').read_text())['passed'],n
origin=json.loads((ROOT/'geometry-reply-origin.json').read_text())
parent=Path(origin['parent']);assert sha(parent/'component-manifest.json')==origin['parentManifestSHA256'];assert sha(Path(origin['failedNative']))==origin['failedNativeSHA256']
expected=(parent/'qa/driver.py').read_bytes().replace(b"g['windows']",b"g['facts']['windows']").replace(b"geo['windows']",b"geo['facts']['windows']")
assert (ROOT/'qa/driver.py').read_bytes()==expected
replay=json.loads((ROOT/'qa'/reports[-1]/'report.json').read_text());assert replay['sourceSHA256']==sha(ROOT/'qa/driver.py') and len(replay['controls'])==3
adoption=json.loads((ROOT/'adoption.json').read_text());native=Path(adoption['diagnosticNative']['path']);assert sha(native)==adoption['diagnosticNative']['sha256'];j=json.loads(native.read_text());assert j['passed'] and j['cleanupPassed'] and len(j['checks'])==27
external={str(native):row(native)}
external[str(parent/'component-manifest.json')]=row(parent/'component-manifest.json');external[origin['failedNative']]=row(Path(origin['failedNative']))
for key in ['reviewSnapshot','sourceReview','cleanupSource']:
 p=Path(adoption[key]['path']);assert sha(p)==adoption[key]['sha256'];external[str(p)]=row(p)
preflight=json.loads((ROOT/'qa'/reports[0]/'report.json').read_text())
for name,expected in preflight['inputs'].items():
 p=Path(name)
 if name.endswith('#symlink'):continue
 if isinstance(expected,dict) and 'symlink' in expected:assert p.is_symlink() and os.readlink(p)==expected['symlink'];external[name]=expected;continue
 assert sha(p)==expected,name;external[name]=row(p)
for name,digest in adoption['adoptedModules'].items():assert sha(ROOT/'qa/helpers'/name)==digest
files={};links={}
for p in sorted(ROOT.rglob('*')):
 rel=str(p.relative_to(ROOT))
 if p.is_symlink():links[rel]=os.readlink(p)
 elif p.is_file():files[rel]=row(p)
packet={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullCampaignPassed':False,'scope':'Full GTK01–08 executable-source readiness and current tuple CPU closure; no native transfer','files':files,'symlinks':links,'externalFiles':external,'reports':[str(Path('qa')/n/'report.json') for n in reports]}
p=ROOT/'component-manifest.json';assert not p.exists();p.write_text(json.dumps(packet,indent=2)+'\n')
for name,expected in files.items():assert row(ROOT/name)==expected,name
for name,target in links.items():assert os.readlink(ROOT/name)==target
print(p);print(sha(p));print('files',len(files),'external',len(external),'symlinks',len(links))

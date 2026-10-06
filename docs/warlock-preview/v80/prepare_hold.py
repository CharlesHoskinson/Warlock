"""Prepare reviewed evidence freezer for the current full host derivative."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');f=pathlib.Path(__file__).parent/'hold80.py';assert not f.exists()
s=(r/'docs/warlock-preview/v79/hold79.py').read_text().replace('warlock-preview-provider-v79','warlock-preview-provider-v80').replace('docs/warlock-preview/v79/report.json','docs/warlock-preview/v80/report.json')
marker='files={}\n';assert s.count(marker)==1
evidence="""evidence={}
for name in ['catalog-enrollment-replay','delivery-extension-physical-tests','metadata-privacy-replay','metadata-icon-physical-tests','receiver-extension-physical-tests','imported-admission-tests','imported-lifecycle-tests']:
 d=json.loads((bp.parent/(name+'.stdout')).read_text());assert d['passed'];evidence[name]=d
evidence['dynamic-enrollment-tests']=json.loads((bp.parent/'dynamic-enrollment-tests.stdout').read_text().splitlines()[-1]);assert evidence['dynamic-enrollment-tests']['checks']==34
"""
s=s.replace(marker,evidence+marker).replace("'files':files,'nativeAcceptance'","'files':files,'evidence':evidence,'evidenceIntegrityPassed':True,'nativeAcceptance'")
s=s.replace('Nextfresh80 unissuedpriority plus ownABI nativeGUI expiry/reopen/image/cleanup.','Current80 unissuedpriority compiled; nextnative115 ownABI GUI expiry/reopen/image/cleanup.').replace('PROGRESS79 explicit successor component held','PROGRESS80 full unissued-priority successor component held')
ast.parse(s);f.write_text(s);print(f)

"""Freeze host same-bootstrap integration after actual protected compilation."""
import hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');ROOT=REPO/'implementation/warlock-preview-provider-v6'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'qa/build-1791231646780910186/report.json';build=json.loads(p.read_text());assert build['passed'] and len(build['commands'])==33
for name,digest in build['inputs'].items():assert sha(ROOT/name)==digest,name
parent=REPO/'implementation/warlock-preview-provider-v5'
for module in (ROOT/'src').glob('*.elm'):assert sha(module)==sha(parent/'src'/module.name)
for name in ['preview_broker.hpp','demand.hpp','preview_delivery.hpp','preview_client.hpp']:assert sha(ROOT/'native'/name)==sha(parent/'native'/name)
files={}
for p in sorted(ROOT.rglob('*')):
 relative=str(p.relative_to(ROOT))
 if relative=='component-manifest.json' or '/mutable-elm-home/' in '/'+relative+'/' or '/elm-stuff/' in '/'+relative+'/':continue
 if p.is_file():files[relative]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)}
packet={'schema':1,'status':'compiled-host-same-bootstrap-native-producer-api','fullGUIBuildPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'productionCaptureWired':False,'sameHostAPIRuntimeQualified':False,'grantFixtureChecks':79,'physicalDeliveryChecks':41,'actualCompiledPresenterLiveBrokerChecks':23,'GIOOwnershipChecks':23,'policyModulesUnchanged':49,'inheritedDemandModelEvidence':{'path':str(parent/'qa/check-1791230962238416457/report.json'),'sha256':sha(parent/'qa/check-1791230962238416457/report.json'),'scope':'Demand and Broker headers unchanged; no new model execution claimed'},'files':files}
(ROOT/'component-manifest.json').write_text(json.dumps(packet,indent=2)+'\n')
report={'passed':True,'scope':'Actual changed full host compilation and inherited real socket/physical/compiled Elm replay checks; GTK producer-facing wrapper runtime not qualified','files':len(files),'manifestSHA256':sha(ROOT/'component-manifest.json'),'nativeAcceptance':False,'fullReleaseAccepted':False}
(pathlib.Path(__file__).parent/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

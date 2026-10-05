"""Freeze exact owned component and compatibility evidence under QA scope."""
import hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
root=REPO/'implementation/warlock-preview-provider-v5'
build=root/'qa/build-1791230896360624225/report.json';model=root/'qa/check-1791230962238416457/report.json'
b=json.loads(build.read_text());q=json.loads(model.read_text());assert b['passed'] and q['passed']
for rel,digest in b['inputs'].items():assert sha(root/rel)==digest,rel
for rel,digest in q['inputs'].items():assert sha(root/rel)==digest,rel
parent=REPO/'implementation/warlock-preview-provider-v3'
for p in (root/'src').glob('*.elm'):assert sha(p)==sha(parent/'src'/p.name),p
assert len(list((root/'src').glob('*.elm')))==49
files={}
for p in sorted(root.rglob('*')):
 rel=str(p.relative_to(root))
 if rel=='component-manifest.json' or '/mutable-elm-home/' in '/'+rel+'/' or '/elm-stuff/' in '/'+rel+'/':continue
 if p.is_file():files[rel]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)}
manifest={'schema':1,'status':'compiled-typed-enrollment-and-retained-delivery-component-qualified','fullGUIBuildPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'productionCaptureWired':False,'grantFixtureChecks':79,'physicalDeliveryChecks':41,'actualCompiledPresenterLiveBrokerChecks':23,'GIOOwnershipChecks':23,'demandChecks':36,'namedQuintScenarios':10,'invariantSamples':300,'coupledTraces':len(q['coupledTraces']),'projectedStatesCompared':sum(v['statesCompared'] for v in q['coupledTraces']),'unsafeDemandMutantsDetected':3,'policyModulesUnchanged':49,'files':files}
assert manifest['projectedStatesCompared']==564
(root/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
compat=REPO/'docs/warlock-compatibility/omarchy-v1';c=json.loads((compat/'inventory.json').read_text())
for row in c['observations']:assert sha(compat/row['file'])==row['sha256']
for row in c['sources']:assert sha(compat/row['snapshot'])==row['sha256']
commands=json.loads((compat/'commands.json').read_text())['commands'];bindings=json.loads((compat/'effective-bindings.json').read_text())
assert len(commands)==c['commandCount']==443 and len(bindings)==c['effectiveBindingCount']==265
spec=REPO/'openspec/changes/warlock-omarchy-compatibility/specs/omarchy-compatibility/spec.md';text=spec.read_text();assert text.count('### Requirement:')==4 and text.count('#### Scenario:')==8
report={'passed':True,'scope':'Owned immutable source/build/evidence closure and additive Omarchy inventory; no new native or release acceptance','manifestSHA256':sha(root/'component-manifest.json'),'componentFiles':len(files),'policyModulesUnchanged':49,'OmarchyCommands':443,'OmarchyBindings':265,'OmarchySourceFiles':len(c['sources']),'compatibilityRequirements':4,'compatibilityScenarios':8,'nativeAcceptance':False,'fullReleaseAccepted':False}
(pathlib.Path(__file__).parent/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

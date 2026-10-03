"""Complete declared ancestry union; source capture/freezer only, never GUI."""
from pathlib import Path
import sys,os,json,hashlib,stat
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
V2=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v2')
O=Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-observer-v2-build')
D=Path('/home/hoskinson/window-behavior-spec/pin-maximized-native-policy-v1-design')
QA=V2.parent
sys.path.insert(0,str(V2/'proposed'))
from closure_union import union

def meta(p):return dict(sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest(),mode=stat.S_IMODE(Path(p).stat().st_mode))
def inventory():
 # Union literal declared whole frozen A ancestry, not merely embed its JSON.
 a=json.loads((V2/'frozen-inputs.json').read_bytes())
 observer=json.loads((O/'SOURCE_READY_INPUTS.json').read_bytes())
 observer=dict(inputs=observer['inputs'],inputModes=observer['inputModes'],symlinks=observer['links'],directoryModes=observer['directoryModes'])
 design=json.loads((D/'DESIGN_INPUTS.json').read_bytes())
 design=dict(inputs={str(D/p):m['sha256']for p,m in design['files'].items()},inputModes={str(D/p):m['mode']for p,m in design['files'].items()},symlinks={},directoryModes={})
 extras=[V2/'frozen-inputs.json',V2/'source-ready-v2.json',O/'SOURCE_READY.json',O/'SOURCE_READY_INPUTS.json',D/'DESIGN_READY.json',D/'DESIGN_INPUTS.json',QA/'pin-max-native-campaign-b-root-design-review-v1.json',QA/'pin-max-native-v2-root-completion-v1.json',QA/'pin-max-campaign-b-observer-root-source-review-v1.json',QA/'pin-max-campaign-b-observer-correction-root-review-v1.json',QA/'pin-max-campaign-b-observer-root-build-review-v1.json',QA/'pin-max-campaign-b-observer-root-header-origin-v1.json',QA/'review_pin_campaign_b_observer_build_v1.py',QA/'review_resume_sources_20261002_v1.py']
 row=union(B,[a,observer,design],extras)
 row['ancestralDescriptors']=[dict(path=str(p),**meta(p))for p in [V2/'frozen-inputs.json',O/'SOURCE_READY_INPUTS.json',D/'DESIGN_INPUTS.json']]
 row['scope']='source-only B01–B12 component proposal; no native/freeze authority'
 return row

def publish(path,row):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2,allow_nan=False);out.write('\n');out.flush();os.fsync(out.fileno())
 fd=os.open(Path(path).parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
if __name__=='__main__':
 row=inventory();publish(B/'SOURCE_INPUTS.json',row)
 ready=dict(schema=1,sourceOnly=True,nativeAuthorized=False,freezeAuthorized=False,sourceInputsSHA256=meta(B/'SOURCE_INPUTS.json')['sha256'],pairSHA256=meta(B/'PAIR_READY.json')['sha256'],inputs=len(row['inputs']),symlinks=len(row['symlinks']),directoryModes=len(row['directoryModes']),controllerCPU=16,producerNamedFormal=14,producerTraces=2000,producerMaxSteps=100,originalA3SourcesConserved=31,original14Credit=False,coreAndObserverUnchanged=True,scope='B01–B12 bounded components only',fullCampaignBAccepted=False,remaining=['B03 full CLI ingress','B07–09 presentation ROI','B11–12 third blocked peer','exhaustive native mode trajectory','B13–B24 actual masks/scroll/transfer/twooutputs','B24 genuine failure trigger','full Windows parity'])
 publish(B/'SOURCE_READY.json',ready)
 print(json.dumps(dict(sourceReadySHA256=meta(B/'SOURCE_READY.json')['sha256'],sourceInputsSHA256=ready['sourceInputsSHA256'],inputs=ready['inputs'],symlinks=ready['symlinks'],directories=ready['directoryModes'],noNative=True)))

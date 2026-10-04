"""Compiled actual unsafe production derivatives, killed by independent named cases."""
import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT.parents[1]/'implementation/elm-menu-post-close-selection-v69'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[SOURCE/'elm.json',*sorted((SOURCE/'src').glob('*.elm'))];inputs={str(p.relative_to(SOURCE)):sha(p) for p in files}
qafiles=[ROOT/'src/MenuSurfaceReplay.elm',ROOT/'qa/post-close.cjs',*sorted((ROOT/'qa/original').glob('*')),Path(__file__)];qainputs={str(p.relative_to(ROOT)):sha(p) for p in qafiles}
mutants=[
 ('wrong-timer-cancels',[('MenuBridge.elm','if slot.token==token then','if True then',2)],'stale preparation deadline cannot cancel current slot'),
 ('fresh-stage-drops-sent-registry',[('MenuBridge.elm','Model {state|menu=closed,prepared=Just slot,preparedSerial=token}','Model {state|menu=closed,router=ReceiptRouter.empty,prepared=Just slot,preparedSerial=token}',1)],'unrelated preparation preserves original sent Unknown registry'),
 ('changed-geometry-records-retarget',[('MenuBridge.elm','before.windows==after.windows','True',1),('ReceiptRouter.elm','before.windows==after.windows','True',1)],'changed workarea revision cannot retarget prepared operation'),
 ('notification-replaces-correlation',[('Shell.elm','if not model.deferNotifications && model.notificationQueued','if True && model.notificationQueued',1)],'notification burst then exact pair produces one effect'),
 ('apps-popup-bypasses-preparation',[('Desktop.elm','if capture model /= Just stamp || MenuBridge.preparedSnapshot model.windows.menus/=Nothing then','if capture model /= Just stamp then',1)],'application opener cannot create competing popup while selection prepared')]
report={'passed':False,'nativeAcceptance':False,'scope':'Actual compiled production mutants against independent post-close trace oracles','sourceRoot':str(SOURCE),'sourceInputs':inputs,'qaInputs':qainputs,'mutants':[]}
try:
 for name,edits,oracle in mutants:
  target=OUT/name;target.mkdir();workspace=target/'inputs';workspace.mkdir()
  for fs,origin in [(files,SOURCE),(qafiles,ROOT)]:
   for p in fs:
    dest=workspace/p.relative_to(origin);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  applied=[]
  for relative,needle,replacement,count in edits:
   p=workspace/'src'/relative;s=p.read_text();assert s.count(needle)==count,(name,relative,s.count(needle));p.write_text(s.replace(needle,replacement));applied.append({'path':'src/'+relative,'needle':needle,'replacement':replacement,'count':count,'mutatedSHA256':sha(p)})
  argv=['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/MenuSurfaceReplay.elm','--output='+str(target/'replay.js')]
  process=subprocess.run(argv,cwd=workspace,capture_output=True,text=True,timeout=180);(target/'compile.stdout').write_text(process.stdout);(target/'compile.stderr').write_text(process.stderr)
  assert process.returncode==0,'Compilation failure does not kill mutant '+name
  argv=['node',str(workspace/'qa/post-close.cjs'),str(target/'replay.js'),str(workspace/'qa/original/fixtures.json'),str(workspace/'qa/original/geometry-fixtures.json'),str(target/'checks.json')]
  process=subprocess.run(argv,cwd=workspace,capture_output=True,text=True,timeout=45);(target/'checks.stdout').write_text(process.stdout);(target/'checks.stderr').write_text(process.stderr)
  checks=json.loads((target/'checks.json').read_text());failed=[x['name'] for x in checks['cases'] if not x['passed']]
  assert process.returncode==1 and checks['passed'] is False and oracle in failed,(name,failed)
  report['mutants'].append({'name':name,'compiled':True,'namedOracle':oracle,'failedCases':failed,'edits':applied,'binarySHA256':sha(target/'replay.js')});print(name,'killed',flush=True)
 for relative,digest in inputs.items():assert sha(SOURCE/relative)==digest
 for relative,digest in qainputs.items():assert sha(ROOT/relative)==digest
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])

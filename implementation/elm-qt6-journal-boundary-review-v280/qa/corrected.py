import hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];source=ROOT/"inputs/corrected-journal.py"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location("corrected",source);j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
reportpath=REPO/"implementation/elm-qt6-journal-consumer-v279/qa/test-1791148464886285381/report.json";report=json.loads(reportpath.read_text());assert report['passed'] is True and report['sourceSHA256']==sha(source)
inputs={str(reportpath):sha(reportpath),str(source):sha(source),str(REPO/"implementation/elm-qt6-journal-consumer-v279/qa/journal.py"):sha(source)}
for path,digest in report['externalFiles'].items():assert sha(path)==digest;inputs[path]=digest
checks=[]
def refused(name,fn):
 try:fn()
 except j.Refused:checks.append({'name':name,'passed':True});return
 raise AssertionError(name)
refused('huge-expected-coordinate-typed-refusal',lambda:j.coordinates({'localX':0,'localY':0},'local',[10**400,0]))
row=dict(schema=1,sequence=1,pid=4000,processStarted=9000,monotonicUs=100,requestSequence=0,event='window-button-unknown',profile='window-modal')
refused('unknown-event-typed-refusal',lambda:j.parse(json.dumps(row).encode()+b'\n',pid=4000,started='9000'))
base=dict(role='C',instance=2,mapGeneration=1,surfaceId=71,sourceSurfaceId=71,trackedRecipient=True,qtTimestamp=1000,qtModifiers=0,localX=8,localY=8,globalQtX=428,globalQtY=98,qtButton=1,qtMouseSource=2)
pair=[]
for seq,event,eventtype,buttons in [(1,'window-button-press',2,1),(2,'window-button-release',3,0)]:pair.append(dict(row,sequence=seq,event=event,rawEventType=eventtype,qtButtons=buttons,**base))
rows=j.parse(b''.join(json.dumps(r).encode()+b'\n' for r in pair),pid=4000,started='9000')
refused('synthetic-source-refused-for-explicit-native-source',lambda:j.raw_pointer_interval(rows,0,role='C',instance=2,map_generation=1,surface_id=71,event_types=report['compiledQtEventTypes'],qt_button=1,qt_mouse_source=0,modifiers=0,expected_local=[8,8],expected_global=[428,98]))
out=ROOT/"qa"/("corrected-"+str(time.time_ns()));out.mkdir();(out/"report.json").write_text(json.dumps({'passed':True,'nativeAcceptance':False,'checks':checks,'inputs':inputs},indent=2)+"\n");print(out/"report.json")

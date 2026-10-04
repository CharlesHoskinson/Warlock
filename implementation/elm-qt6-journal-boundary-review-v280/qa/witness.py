import hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];source=ROOT/"inputs/journal.py"
spec=importlib.util.spec_from_file_location("captured",source);j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
out=ROOT/"qa"/("witness-"+str(time.time_ns()));out.mkdir();checks=[]
try:j.coordinates({'localX':0,'localY':0},'local',[10**400,0])
except OverflowError as error:checks.append({'name':'huge-expected-coordinate','actualFailure':'OverflowError','typedRefused':False,'error':str(error)})
else:raise AssertionError('Expected preserved huge-int fault')
row=dict(schema=1,sequence=1,pid=4000,processStarted=9000,monotonicUs=100,requestSequence=0,event='window-button-unknown',profile='window-modal')
rows=j.parse(json.dumps(row).encode()+b'\n',pid=4000,started='9000');assert j.blocked_raw_pointer_interval(rows,0)==[];checks.append({'name':'unknown-window-input-event-hidden-from-negative-interval','accepted':True})
base=dict(role='C',instance=2,mapGeneration=1,surfaceId=71,sourceSurfaceId=71,trackedRecipient=True,qtTimestamp=1000,qtModifiers=0,localX=8,localY=8,globalQtX=428,globalQtY=98,qtButton=1,qtMouseSource=2)
pair=[]
for seq,event,eventtype,buttons in [(1,'window-button-press',2,1),(2,'window-button-release',3,0)]:pair.append(dict(row,sequence=seq,event=event,rawEventType=eventtype,qtButtons=buttons,**base))
rows=j.parse(b''.join(json.dumps(r).encode()+b'\n' for r in pair),pid=4000,started='9000')
j.raw_pointer_interval(rows,0,role='C',instance=2,map_generation=1,surface_id=71,event_types={'window-button-press':2,'window-button-release':3},qt_button=1,modifiers=0,expected_local=[8,8],expected_global=[428,98]);checks.append({'name':'synthetic-mouse-source-not-checked','accepted':True,'syntheticDTO':True})
report={'passed':True,'nativeAcceptance':False,'checks':checks,'inputs':{str(source):hashlib.sha256(source.read_bytes()).hexdigest(),str(Path(__file__)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')

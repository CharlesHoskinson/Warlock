"""Strict Qt DTO adversarial tests using actual compiled Qt event constants."""
import copy,hashlib,json,resource,shlex,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
import journal as j
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'qa'/('test-'+str(time.time_ns()));out.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'checks':[]}
def checked(name,fn,refused=False):
 try:fn()
 except j.Refused:
  assert refused,name
 else:assert not refused,name
 report['checks'].append({'name':name,'passed':True})
def row(event,**fields):
 return dict(schema=1,sequence=1,pid=4000,processStarted=9000,monotonicUs=100,requestSequence=0,event=event,profile='window-modal',**fields)
def encode(rows):
 rows=copy.deepcopy(rows)
 for index,r in enumerate(rows,1):r['sequence']=index;r['monotonicUs']=100+index
 return b''.join(json.dumps(r).encode()+b'\n' for r in rows)
def parse(raw,**kw):return j.parse(raw,pid=4000,started='9000',**kw)
try:
 source=out/'enums.cpp';source.write_text('#include <QEvent>\n#include <Qt>\n#include <iostream>\nint main(){std::cout<<"{\\"window-button-press\\":"<<int(QEvent::MouseButtonPress)<<",\\"window-button-release\\":"<<int(QEvent::MouseButtonRelease)<<",\\"window-button-double-click\\":"<<int(QEvent::MouseButtonDblClick)<<",\\"window-key-press\\":"<<int(QEvent::KeyPress)<<",\\"window-key-release\\":"<<int(QEvent::KeyRelease)<<"}";}\n')
 flags=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core'],text=True))
 binary=out/'enums';command=['/usr/bin/c++','-std=c++17','-Wall','-Wextra','-Werror',str(source),'-o',str(binary),*flags]
 p=subprocess.run(command,capture_output=True,timeout=20);(out/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
 types=json.loads(subprocess.check_output([str(binary)],timeout=3));report['compiledQtEventTypes']=types
 base=dict(role='C',instance=2,mapGeneration=1,surfaceId=71,sourceSurfaceId=71,trackedRecipient=True,qtTimestamp=1000,qtModifiers=0)
 pointer=[row(event,**base,rawEventType=types[event],qtButton=1,qtButtons=buttons,localX=8,localY=8,globalQtX=428,globalQtY=98) for event,buttons in [('window-button-press',1),('window-button-release',0)]]
 args=dict(role='C',instance=2,map_generation=1,surface_id=71,event_types=types,qt_button=1,modifiers=0,expected_local=[8,8],expected_global=[428,98])
 def pointer_check(rows):j.raw_pointer_interval(parse(encode(rows)),0,**args)
 checked('actual-Qt-enum-bound-raw-pointer-pair',lambda:pointer_check(pointer))
 for field,value in [('role','A'),('instance',3),('mapGeneration',2),('surfaceId',72),('sourceSurfaceId',72),('trackedRecipient',False),('trackedRecipient',1),('rawEventType',True),('qtButton',2),('qtButtons',3),('qtModifiers',1),('localX',9),('globalQtY',99)]:
  changed=copy.deepcopy(pointer);changed[0][field]=value;checked('raw-pointer-refuses-'+field,lambda c=changed:pointer_check(c),True)
 checked('raw-pointer-refuses-extra-untracked-recipient',lambda:pointer_check(pointer+[row('window-button-press',trackedRecipient=False)]),True)
 changed=copy.deepcopy(pointer);changed[0]['event']='window-button-double-click';checked('explicit-double-click-not-single-pair',lambda:pointer_check(changed),True)
 propagated=[copy.deepcopy(pointer[0]),row('widget-button-press',**base,recipientWidget='landmark'),row('widget-button-press',**base,recipientWidget='root-C'),copy.deepcopy(pointer[1]),row('widget-button-release',**base,recipientWidget='root-C')]
 checked('QWidget-propagation-is-not-additional-native-dispatch',lambda:pointer_check(propagated))
 decoded=parse(encode(propagated));assert len(j.widget_input_observations(decoded,0))==3
 checked('blocked-raw-refuses-any-role',lambda:j.blocked_raw_pointer_interval(decoded,0),True)
 key=[row(event,**base,rawEventType=types[event],qtKey=65,nativeScanCode=38,nativeVirtualKey=97,nativeModifiers=0,autoRepeat=False,keyText='a') for event in ['window-key-press','window-key-release']]
 keyargs=dict(role='C',instance=2,map_generation=1,surface_id=71,event_types=types,qt_key=65,native_scan=38,native_virtual=97,qt_modifiers=[0,0],native_modifiers=[0,0])
 def key_check(rows):j.raw_key_interval(parse(encode(rows)),0,**keyargs)
 checked('raw-key-pair-explicit-domains',lambda:key_check(key))
 for field,value in [('qtKey',66),('nativeScanCode',39),('nativeVirtualKey',98),('nativeModifiers',1),('qtModifiers',1),('autoRepeat',True),('sourceSurfaceId',72)]:
  changed=copy.deepcopy(key);changed[1][field]=value;checked('raw-key-refuses-'+field,lambda c=changed:key_check(c),True)
 checked('raw-key-extra-role-not-filtered',lambda:key_check(key+[row('window-key-press',**base)]),True)
 ready=encode([row('ready')]);checked('valid-partial-tail-retained-only-complete',lambda:parse(ready+b'{"partial":'))
 for label,raw in [('duplicate',ready.replace(b'"schema": 1',b'"schema": 1,"schema": 1')),('nonfinite',ready.replace(b'"monotonicUs": 101',b'"monotonicUs": NaN')),('foreignPID',ready.replace(b'4000',b'4001')),('foreignStart',ready.replace(b'9000',b'9001')),('wrongProfile',ready.replace(b'window-modal',b'application-modal')),('invalidUTF8',b'\xff\n'),('nested',encode([row('ready',nested=[])])),('refusal',encode([row('refusal')])),('bool-sequence',ready.replace(b'"sequence": 1',b'"sequence": true'))]:checked('journal-'+label,lambda r=raw:parse(r),True)
 checked('immutable-observed-prefix',lambda:parse(ready.replace(b'"requestSequence": 0',b'"requestSequence": 1'),previous=parse(ready)),True)
 checked('bounded-journal-bytes',lambda:parse(b'x'*(2*1024*1024+1)),True)
 (out/'pointer.jsonl').write_bytes(encode(propagated));(out/'key.jsonl').write_bytes(encode(key))
 report.update(passed=True,sourceSHA256=sha(ROOT/'qa/journal.py'),compilerSHA256=sha('/usr/bin/c++'),enumSourceSHA256=sha(source),enumBinarySHA256=sha(binary),compileCommand=command)
finally:
 (out/'test.py').write_bytes(Path(__file__).read_bytes());(out/'journal.py').write_bytes((ROOT/'qa/journal.py').read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')

import hashlib,importlib.util,json,os,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;source=ROOT/'witness-1791157163324137596/inputs/guard.py';OUT=ROOT/('parser-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
spec=importlib.util.spec_from_file_location('guard',source);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
raw=Path('/proc/self/stat').read_text();tail=raw[raw.rfind(')')+2:].split();bad_start=tail.copy();bad_start[19]='1'*5000;bad_state=tail.copy();bad_state[0]='?';st=Path('/').stat();identity=(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino)
cases=[('5000-digit map inode',lambda:g.parse_maps('100-200 r-xp 0 00:01 '+'1'*5000+' /tmp/a')),('5000-digit process start',lambda:g.process_identity(str(os.getpid())+' (owned) '+' '.join(bad_start),pid=os.getpid())),('5000-digit mount device',lambda:g.map_identity('/bin',identity,'1 0 '+'1'*5000+':1 / / rw - btrfs /dev/fake rw')),('unknown process state',lambda:g.process_identity(str(os.getpid())+' (owned) '+' '.join(bad_state),pid=os.getpid())),('reversed map range',lambda:g.parse_maps('200-100 r-xp 0 00:01 1 /tmp/a'))]
r={'passed':True,'nativeAcceptance':False,'scope':'Actual captured predecessor parser characterization, hostile synthetic syntax/kernel-domain boundary only','source':str(source),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':[]}
for name,f in cases:
 try:result=f();outcome='accepted'
 except g.Refused as e:result=str(e);outcome='typed-refused'
 except Exception as e:result=repr(e);outcome='ordinary-error'
 r['cases'].append({'name':name,'outcome':outcome,'result':str(result)[:500]})
assert [x['outcome'] for x in r['cases']]==['ordinary-error','ordinary-error','ordinary-error','accepted','accepted']
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS five predecessor boundary classifications')

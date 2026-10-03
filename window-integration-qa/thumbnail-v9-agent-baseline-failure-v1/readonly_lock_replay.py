import hashlib,json,os,sys,threading,time
from pathlib import Path
D=Path(__file__).parent
S=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
sys.dont_write_bytecode=True;sys.path.insert(0,str(S))
from test_readonly_ipc import ReadonlyKernelTests
home=D/'readonly-private-home';home.mkdir(mode=0o700);os.environ['HOME']=str(home)
c=ReadonlyKernelTests();c.setUp();entered=threading.Event();finished=threading.Event();errors=[];observed={}
original=c.reader.register
def register(row):
 observed['registeredRow']=dict(row);entered.set();return original(row)
c.reader.register=register
def query():
 began=time.monotonic_ns()
 try:c.query(timeout=1)
 except BaseException as e:errors.append({'type':type(e).__name__,'message':str(e)})
 finally:observed['queryElapsedNs']=time.monotonic_ns()-began;finished.set()
try:
 with c.lock:
  worker=threading.Thread(target=query);worker.start();assert entered.wait(2)
  # The fixed original1s deadline is consumed by an actual competing receipt lock.
  time.sleep(1.05);assert not finished.is_set()
 worker.join(timeout=2);assert not worker.is_alive();assert errors and errors[0]['type']=='TimeoutError'
 row=c.row();assert row['outcome']=='refused'and row['closed']and row['published']
 assert row['evidence']['peer']is None and row['evidence']['replyBytes']==0
 assert b'j/clients'not in c.control.requests
 observed.update(result='pass',errors=errors,row=row,deadlineSeconds=1,limitation='Exact CPU reservation-lock path shown; native row33 timeout site and lock holder unproved',readonlySourceSHA256=hashlib.sha256((S/'readonly_ipc.py').read_bytes()).hexdigest())
 with os.fdopen(os.open(D/'readonly-lock-replay-v1.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(observed,f,indent=2);f.write('\n')
finally:c.tearDown()

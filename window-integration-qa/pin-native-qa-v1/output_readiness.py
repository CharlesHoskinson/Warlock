"""Fixed read-only owned IPC observation, bounded by original child launch budget."""
import base64,hashlib,json,math,os,socket,struct,time
from pathlib import Path
FIELDS={'width':1600,'height':1000,'scale':1,'x':0,'y':0,'transform':0}
def exact_outputs(rows):
 return isinstance(rows,list) and len(rows)==1 and isinstance(rows[0],dict) and all(type(rows[0].get(k)) in (int,float) and rows[0][k]==v for k,v in FIELDS.items())
def numeric(value):return type(value) in (int,float) and math.isfinite(value)
def remaining(deadline,clock):
 now=clock()
 if not numeric(now) or now<0 or now>=deadline:raise RuntimeError('Original private child startup deadline expired')
 return deadline-now

def query(session,deadline,row,persist,clock=time.monotonic):
 original=session.host.__class__.__module__ # diagnostic class only, never a selector
 row['hostClassModule']=original
 from private_output_host import original as host_api
 def observe(label):
  row[label]={'expectedChild':dict(session.child_identity),'expectedSockets':session.sockets,
   'selected':{k:session.env.get(k)for k in ('HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','XDG_RUNTIME_DIR','DBUS_SESSION_BUS_ADDRESS')}}
  persist()
  row[label]['actualChild']=host_api.process(session.evidence['compositorPID']);persist()
  session.guard()
 observe('before')
 path=Path(session.evidence['ipcReadiness'][0]['path'])
 if str(path)!=str(session.host.runtime/'hypr'/session.evidence['signature']/'.socket.sock'):raise RuntimeError('Exact owned readiness IPC path required')
 before=host_api.socket_identity(path,session.host.runtime);row['socketBefore']=before;persist()
 if before not in session.sockets:raise RuntimeError('Readiness socket differs from registered exact socket')
 raw=bytearray();row.update(request='j/monitors',completeServerEOF=False,rawReplyBase64='',replyBytes=0);persist()
 try:
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
   conn.settimeout(min(2,remaining(deadline,clock)));conn.connect(str(path))
   pid,uid,gid=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   row['peer']={'pid':pid,'uid':uid,'gid':gid};persist()
   if pid!=session.evidence['compositorPID'] or uid!=os.getuid():raise RuntimeError('Private output readiness peer identity mismatch')
   if host_api.socket_identity(path,session.host.runtime)!=before:raise RuntimeError('Readiness socket replaced before request')
   session.guard();remaining(deadline,clock);conn.sendall(b'j/monitors')
   while True:
    conn.settimeout(min(2,remaining(deadline,clock)));chunk=conn.recv(4096)
    if not chunk:row['completeServerEOF']=True;persist();break
    raw.extend(chunk);row.update(rawReplyBase64=base64.b64encode(raw).decode(),replyBytes=len(raw),replySHA256=hashlib.sha256(raw).hexdigest());persist()
    if len(raw)>65536:raise RuntimeError('Private output readiness reply too large')
   remaining(deadline,clock)
  row['socketAfter']=host_api.socket_identity(path,session.host.runtime);persist()
  if row['socketAfter']!=before:raise RuntimeError('Readiness socket replaced after reply')
  observe('after');remaining(deadline,clock)
  return bytes(raw)
 except BaseException as error:
  row['queryError']=repr(error);persist();raise

def collect(session,destination,clock=time.monotonic,sleep=time.sleep,reader=query):
 evidence={'accepted':False,'originalFeatureAcceptance':False,'observations':[],'budgetSeconds':15,'budgetReset':False}
 destination=Path(destination)
 def persist():
  destination.write_text(json.dumps(evidence,indent=2)+'\n');destination.chmod(0o600)
 persist()
 try:
  budget=session.evidence['browserStartupBudget'];evidence['startupBudget']=dict(budget);persist()
  start=budget['launchReturnedMonotonic'];deadline=budget['deadlineMonotonic'];now=clock()
  if type(budget.get('pid')) is not int or budget['pid']<=0 or budget['pid']!=session.evidence['compositorPID']:raise RuntimeError('Exact same launch PID budget required')
  if not numeric(start) or not numeric(deadline) or not numeric(now) or start<0 or deadline!=start+15 or now<start:raise RuntimeError('Exact original private launch budget required')
  while True:
   remaining(deadline,clock);row={'sequence':len(evidence['observations'])+1,'startedMonotonic':clock()};evidence['observations'].append(row);persist()
   raw=reader(session,deadline,row,persist,clock);row['rawReplyBase64']=base64.b64encode(raw).decode();row['replyBytes']=len(raw);row['replySHA256']=hashlib.sha256(raw).hexdigest();persist()
   if row.get('completeServerEOF') is not True or len(raw)>65536:raise RuntimeError('Complete bounded output response required')
   rows=json.loads(raw.decode('utf-8'));row['actualOutputs']=rows;row['completedMonotonic']=clock();persist();remaining(deadline,clock)
   if not isinstance(rows,list):raise RuntimeError('Actual private monitors reply must be a list')
   if rows:
    if not exact_outputs(rows):raise RuntimeError('Actual nonempty private output differs from original exact fixture')
    session.guard();remaining(deadline,clock);evidence['accepted']=True;persist();return evidence
   sleep(min(.03,remaining(deadline,clock)))
 except BaseException as error:
  evidence['accepted']=False;evidence['error']=repr(error);persist();raise

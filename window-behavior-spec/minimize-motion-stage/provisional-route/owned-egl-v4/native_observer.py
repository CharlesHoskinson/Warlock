"""Native evidence consumer; importing/tests never connect to a display."""
import json,subprocess,threading,time

class Producer:
 def __init__(self,binary,env,stderr):
  self.rows=[];self.condition=threading.Condition();self.error=None
  self.log=stderr.open('w')
  self.process=subprocess.Popen([str(binary)],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=True,bufsize=1)
  self.thread=threading.Thread(target=self._read,daemon=True);self.thread.start()
 def _read(self):
  try:
   for line in self.process.stdout:
    row=json.loads(line);row['observerReceivedNs']=time.monotonic_ns()
    with self.condition:self.rows.append(row);self.condition.notify_all()
  except Exception as error:self.error=repr(error)
  finally:
   with self.condition:self.condition.notify_all()
 def send(self,**command):
  self.process.stdin.write(json.dumps(command,separators=(',',':'))+'\n');self.process.stdin.flush()
 def wait(self,predicate,message,timeout=5):
  end=time.monotonic()+timeout
  with self.condition:
   while True:
    for row in reversed(self.rows):
     if predicate(row):return row
    fatal=next((r for r in self.rows if r.get('event')=='fatal'),None)
    if fatal and not predicate(fatal):raise AssertionError(message+': '+repr(fatal))
    if self.error or self.process.poll() is not None:raise AssertionError(message+': producer exited '+str(self.error))
    remaining=end-time.monotonic()
    if remaining<=0:raise AssertionError(message+': timeout')
    self.condition.wait(min(remaining,.1))
 def close(self):
  if self.process.poll() is None:
   try:self.send(command='stop');self.process.wait(timeout=3)
   except (OSError,subprocess.TimeoutExpired):self.process.kill();self.process.wait()
  self.thread.join(timeout=2);self.log.close()

def accepted(event,token=None):
 return event.get('event')=='presented' and event.get('accepted') is True and (token is None or event.get('token')==token)

def handover(rows,event):
 diagnostics=[]
 for origin in event['origins']:
  prior=next((r for r in reversed(rows) if accepted(r) and r['output']==origin['output'] and r['generation']==origin['generation'] and r['sequence']==origin['sequence']),None)
  matches=bool(prior and prior['timestampNs']==origin['timestampNs'] and prior['rectangle']==origin['rectangle'])
  interior=bool(prior and .0001<prior['progress']<.9999)
  diagnostics.append({'output':origin['output'],'origin':origin,'actualPrior':prior,'exactPresentedOrigin':matches,'strictlyInterior':interior})
 return {'token':event['token'],'outputs':diagnostics,'passes':bool(diagnostics) and all(d['exactPresentedOrigin'] and d['strictlyInterior'] for d in diagnostics)}

def cadence(records,outputs):
 result={}
 for output in outputs:
  rows=[r for r in records if r['output']==output['name']]
  times=[int(r['timestampNs']) for r in rows]
  gaps=[(b-a)/1e6 for a,b in zip(times,times[1:])]
  refresh=output['refreshMilliHz']/1000;period=1000/refresh if refresh>0 else 0
  ordered=all(b>a for a,b in zip(times,times[1:]))
  bound=2*period+.5 if period else 0
  result[output['name']]={'sampleCount':len(rows),'gapsMs':gaps,'maximumGapMs':max(gaps,default=0),'p95GapMs':sorted(gaps)[min(len(gaps)-1,int(len(gaps)*.95))] if gaps else 0,'refreshHz':refresh,'maximumAllowedMs':bound,'timestampsOrdered':ordered,'passes':len(rows)>=12 and ordered and bool(gaps) and period>0 and max(gaps)<=bound}
 return result

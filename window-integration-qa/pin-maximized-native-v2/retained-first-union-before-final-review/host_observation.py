"""Observe unchanged owned signals/stop limits and actual reaped return codes."""
import json,os,signal,time

def normal_row(row):
 if type(row)is not dict or row.get('registeredExact')is not True or row.get('reaped')is not True or row.get('stopError')is not None:return False
 if type(row.get('pid'))is not int or row['pid']<=0 or type(row.get('pgid'))is not int or row['pgid']!=row['pid'] or type(row.get('start'))is not str or not row['start'].isdigit()or int(row['start'])<=0:return False
 rc=row.get('returncode');events=row.get('signals')
 if type(rc)is not int or type(events)is not list:return False
 if any(type(e)is not dict or type(e.get('signal'))is not int or type(e.get('pid'))is not int or e.get('pid')!=row['pid'] or e.get('sent')is not True or e.get('error')is not None or e['signal']!=signal.SIGTERM for e in events):return False
 name=row.get('name')
 if type(name)is not str or name not in ['hyprland','weston','privateBus']:return False
 return rc==0 or (name=='privateBus'and rc==-signal.SIGTERM and len(events)==1)

def normal_closure(row):
 if type(row)is not dict or row.get('closeError')is not None:return False
 rows=row.get('rows');order=row.get('registeredStopOrder')
 if type(rows)is not list or len(rows)!=3 or any(type(r)is not dict for r in rows) or type(order)is not list or any(type(v)is not str for v in order) or order!=['hyprland','weston','privateBus']:return False
 if [r.get('name')for r in rows]!=['privateBus','weston','hyprland']:return False
 return all(normal_row(r)for r in rows)

class ObservedShutdownMixin:
 def _same_process(self,row):return self._original_module.same_process(row)
 def _observed_signal(self,pid,sig):
  event=dict(pid=pid,signal=int(sig),sent=False,error=None)
  self._active_stop['signals'].append(event)
  try:os.kill(pid,sig)
  except BaseException as error:
   event['error']=repr(error);raise
  else:event['sent']=True
 def stop(self,row,proc=None):
  records=self.evidence.setdefault('ownedStops',[])
  entry=dict(row=dict(row),registeredExact=any(p is proc and r is row for p,r in self.processes),signals=[],error=None,returncodeBefore=proc.returncode if proc is not None else None)
  records.append(entry);self._active_stop=entry
  try:return self._inherited_stop(row,proc)
  except BaseException as error:entry['error']=repr(error);raise
  finally:
   entry['returncodeAfterStop']=proc.returncode if proc is not None else None
   self._active_stop=None
 def close(self):
  if not self.runtime:return super().close()
  selected=list(self.processes);error=None
  try:return super().close()
  except BaseException as caught:error=repr(caught);raise
  finally:
   rows=[];stops=self.evidence.get('ownedStops',[])
   for proc,row in selected:
    matching=[s for s in stops if s['registeredExact']is True and all(s['row'].get(k)==row.get(k)for k in ['pid','start','pgid','name'])]
    events=[event for s in matching for event in s['signals']]
    errors=[s['error']for s in matching if s['error']is not None]
    rows.append(dict(**row,registeredExact=len(matching)==1 and proc.pid==row['pid'],reaped=type(proc.returncode)is int,returncode=proc.returncode,signals=events,stopError=errors[0]if errors else None))
   order=[s['row']['name']for s in stops if s['registeredExact']is True]
   observation=dict(rows=rows,registeredStopOrder=order,closeError=error,originalStopSeconds=4,originalWaitSeconds=4,scope='observed host closure only; named bus termination distinguished')
   observation['normal']=normal_closure(observation);self.evidence['ownedNormalClosure']=observation
   destination=self.output/'host-normal-closure.json';destination.write_text(json.dumps(observation,indent=2,allow_nan=False)+'\n');destination.chmod(0o600)
 def _inherited_stop(self,row,proc=None):
  if proc is not None and proc.poll() is not None:return
  if not self._same_process(row):return
  self._observed_signal(row['pid'],signal.SIGTERM);end=time.monotonic()+4
  while self._same_process(row) and time.monotonic()<end:
   if proc is not None and proc.poll() is not None:return
   time.sleep(.03)
  if self._same_process(row):self._observed_signal(row['pid'],signal.SIGKILL)


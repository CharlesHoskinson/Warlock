"""Exact reviewed V2 host plus separate declared frontend normal classification."""
from pathlib import Path
import importlib.util,os,stat,sys
from io_guard import publish_json,sha,strict,verify,exact
from selection import B,QA,QS,FIXTURE,POINTER,KEYBOARD,COMPOSITION
V2=QA/'pin-maximized-native-v2'
sys.path.insert(0,str(V2/'proposed'))
try:
 spec=importlib.util.spec_from_file_location('_pin_qs_exact_owning_host',V2/'proposed/candidate_host.py');accepted=importlib.util.module_from_spec(spec);spec.loader.exec_module(accepted)
finally:sys.path.pop(0)
original=accepted.original;CORE=accepted.CORE;AQ=accepted.AQ
BASE=['privateBus','weston','hyprland']
def classify(raw,prior,packet):
 if type(raw)is not dict or raw.get('closeError')is not None or raw.get('originalStopSeconds')!=4 or type(raw.get('originalStopSeconds'))is not int or raw.get('originalWaitSeconds')!=4 or type(raw.get('originalWaitSeconds'))is not int:raise ValueError('Inherited original4s normal close required')
 rows=raw.get('rows')
 if type(rows)is not list or len(rows)<6 or [r.get('name')for r in rows[:3]]!=BASE or len(rows)!=len(prior):raise ValueError('Exact base and declared frontend actor inventory required')
 from host_observation import normal_row
 if not all(normal_row(r)for r in rows[:3])or raw.get('registeredStopOrder')!=list(reversed([r['name']for r in rows])):raise ValueError('Unchanged original bus/Weston/core normal lifecycle required')
 seen=set()
 for before,after in zip(prior[3:],rows[3:]):
  root=before['registered'];key=(root['pid'],root['start'],root['pgid'])
  if key in seen or root['pgid']!=root['pid']:raise ValueError('Duplicate/reused frontend actor')
  seen.add(key)
  if any(not exact(root.get(k),after.get(k))for k in ('name','pid','start','pgid','command'))or before['returncode']!=0 or type(before['returncode'])is not int or before['gone']is not True:raise ValueError('Exact pre-close normally gone frontend actor required')
  if after.get('registeredExact')is not True or after.get('reaped')is not True or type(after.get('returncode'))is not int or after['returncode']!=0 or after.get('signals')!=[] or after.get('stopError')is not None:raise ValueError('No frontend forced/signal cleanup accepted')
  cmd=root['command'];source=before['source'];name=root['name']
  if source.get('path')!=cmd[0]or source.get('sha256')!=packet['inputs'].get(cmd[0])or source.get('mode')!=packet['inputModes'].get(cmd[0]):raise ValueError('Exact selected registered command source required')
  if name=='pin-legacy-qt':
   if cmd[0]!=str(FIXTURE)or len(cmd)!=2:raise ValueError('Exact Qt fixture role required')
  elif name=='pin-pointer':
   if cmd!=[str(POINTER),'1600','1000']:raise ValueError('Exact pointer role required')
  elif name in ('pin-qs-A','pin-qs-B'):
   if cmd!=[str(QS),'-p',str(B/'payload/omarchy/shell')]:raise ValueError('Exact QS role required')
  elif name.startswith('pin-qs-observation-'):
   if len(cmd)<8 or cmd[:2]!=[str(QS),'ipc']or cmd[2]!='--pid'or cmd[4:6]!=['call','--']or (cmd[6],cmd[7])not in {('shell','ping'),('hoskinson.windows','state'),('hoskinson.windows','pinMenuState'),('hoskinson.windows','pinTypedRetirementRefusal')}:raise ValueError('Exact declared QS query/refusal role required')
  elif name.startswith('pin-qs-stop-'):
   if len(cmd)!=4 or cmd[:3]!=[str(QS),'kill','--pid']:raise ValueError('Exact QS normal kill IPC role required')
  elif name.startswith('pin-frontend-chord-'):
   if len(cmd)!=3 or cmd[0]!=str(COMPOSITION/'keyboard/physical-keyboard')or cmd[1]!='--chord'or cmd[2]not in ('super-t','menu','return','escape'):raise ValueError('Exact physical route producer required')
  else:raise ValueError('Unknown frontend registered role')
 return True
class ReviewedWestonHost(accepted.ReviewedWestonHost):
 def close(self):
  if not self.runtime:return super().close()
  selected=list(self.processes);before=[];fault=None
  for process,row in selected:
   item=dict(registered=dict(row),returncode=process.poll(),gone=not Path('/proc/'+str(process.pid)).exists())
   if len(before)>=3:
    path=Path(row['command'][0]);item['source']=dict(path=str(path),sha256=sha(path),mode=stat.S_IMODE(path.stat().st_mode))
   before.append(item)
  publish_json(self.output/'qs-actors-before-close.json',dict(rows=before))
  try:return super().close()
  except BaseException as e:fault=repr(e);raise
  finally:
   result=dict(normal=False,before=before,delegatedCloseError=fault,oldFixedAClassificationSelected=False)
   try:result['normal']=fault is None and classify(self.evidence['ownedNormalClosure'],before,self.qs_frozen)
   except BaseException as e:result['error']=repr(e)
   self.evidence['privateQSNormalClosure']=result;publish_json(self.output/'qs-normal-classification.json',result)
class PrivateHyprSession(accepted.PrivateHyprSession):
 def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
  super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor);self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor);self.evidence=self.host.evidence

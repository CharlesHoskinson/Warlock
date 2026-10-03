"""Read-only binding of the exact already-closed campaign A producers."""
from pathlib import Path
import hashlib,json,os,stat

B=Path(__file__).resolve().parent.parent
QA=Path('/home/hoskinson/window-integration-qa')
FIXTURE=QA/'qt-modal-private-v9/build-v7/qt-window-modal-fixture'
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
KEYBOARD=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3/keyboard-chords/physical-keyboard')
BASE=['privateBus','weston','hyprland']
CLIENTS=['pin-legacy-qt','pin-pointer','pin-chord-3','pin-chord-4','pin-chord-5','pin-chord-6']
ROUTES=['titlebar','titlebar','super-p','super-ctrl-t','super-p','super-ctrl-t']

def exact(a,b):
 if type(a)is not type(b):return False
 if type(a)is dict:return a.keys()==b.keys()and all(exact(a[k],b[k])for k in a)
 if type(a)is list:return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 return a==b

def require(value,message):
 if value is not True:raise ValueError(message)

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def identity(row):
 require(type(row)is dict,'typed registered row')
 require(type(row.get('pid'))is int and row['pid']>0 and type(row.get('pgid'))is int and row['pgid']==row['pid'],'registered PID/PGID')
 require(type(row.get('start'))is str and row['start'].isdigit()and int(row['start'])>0,'registered start')
 return [row['pid'],row['start'],row['pgid']]

def derive(rows,report,sources,output):
 require(type(rows)is list and [r.get('name')for r in rows]==BASE+CLIENTS,'exact full registered roles')
 lives=[identity(r)for r in rows]
 require(len({tuple(v)for v in lives})==9 and len({v[0]for v in lives})==9,'unique registered lifetimes')
 require(type(report)is dict and report.get('normalCleanup')is True and not report.get('cleanupErrors')and report.get('result')=='pass'and report.get('nativeFeatureAccepted')is True,'original normal case completion')
 require(type(report.get('checks'))is list and len(report['checks'])==14 and all(type(r)is dict and r.get('passed')is True for r in report['checks']),'original14 complete case record')
 inputs=report.get('inputs')
 require(type(inputs)is list and len(inputs)==6 and [r.get('route')for r in inputs]==ROUTES,'exact genuine original six input routes')
 cleanup=report.get('cleanup');require(type(cleanup)is dict and set(cleanup)=={'pointer','fixture'},'exact case cleanup roles')
 fixture=report.get('fixture');pointer=report.get('pointer')
 require(type(fixture)is dict and type(pointer)is dict,'original captured producer records')
 required={str(FIXTURE),str(POINTER),str(KEYBOARD),str(B/'native_cases.py')}
 require(type(sources)is dict and set(sources)==required,'exact four selected sources')
 for p,s in sources.items():
  require(type(s)is dict and type(s.get('sha256'))is str and len(s['sha256'])==64 and type(s.get('mode'))is int,'typed frozen source projection')
 bindings=[]
 for i,row in enumerate(rows[3:]):
  name=row['name'];life=identity(row)
  if i==0:
   receipt=cleanup['fixture'];record=fixture;argv=[str(FIXTURE),str(output)];sha=sources[str(FIXTURE)]['sha256']
   require(exact(record.get('executable'),str(FIXTURE))and exact(record.get('sha256'),sha),'fixture source receipt')
  elif i==1:
   receipt=cleanup['pointer'];record=pointer;argv=[str(POINTER),'1600','1000'];sha=sources[str(POINTER)]['sha256']
   require(exact(pointer,row),'original pointer full registered identity')
  else:
   receipt=inputs[i]['keyboardProcess'];record=receipt;argv=[str(KEYBOARD),'--chord',ROUTES[i]];sha=sources[str(KEYBOARD)]['sha256']
   require(type(receipt)is dict and exact(receipt.get('argv'),argv)and exact(receipt.get('executableSHA256'),sha),'keyboard source completion receipt')
  require(type(receipt)is dict and exact(receipt.get('pid'),life[0])and receipt.get('gone')is True and type(receipt.get('exitCode'))is int and receipt['exitCode']==0 and receipt.get('error')is None,'actual matching normal cleanup receipt')
  if i<2:require(receipt.get('forced')is False,'no forced case cleanup')
  require(exact(record.get('pid'),life[0])and exact(record.get('start'),life[1])and exact(row.get('command'),argv),'source-bound exact captured lifetime/argv')
  bindings.append(dict(name=name,pid=life[0],start=life[1],pgid=life[2],command=argv,executableSHA256=sha,sourceMode=sources[argv[0]]['mode'],receipt=receipt))
 return bindings

def capture(host,selected):
 evidence=dict(ok=False,error=None,beforeDelegatedClose=True,rows=[],sources={})
 try:
  report_path=host.output.parent/'native/cases.json'
  require(report_path.resolve()==report_path and report_path.parent==host.output.parent/'native','exact owned case report path')
  st=report_path.stat();require(stat.S_ISREG(st.st_mode)and stat.S_IMODE(st.st_mode)==0o600 and st.st_uid==os.getuid()and st.st_nlink==1 and 0<st.st_size<=16*1024*1024,'owned bounded raw case report')
  raw=report_path.read_bytes();report=json.loads(raw)
  artifact=host.output/'client-closure-cases.json'
  fd=os.open(artifact,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb')as out:out.write(raw);out.flush();os.fsync(out.fileno())
  evidence.update(caseReport=str(report_path),caseReportSHA256=hashlib.sha256(raw).hexdigest(),rawArtifact=str(artifact),rawArtifactSHA256=digest(artifact),rawPersisted=True)
  frozen=json.loads((B/'frozen-inputs.json').read_bytes())
  for p in [B/'native_cases.py',FIXTURE,POINTER,KEYBOARD]:
   key=str(p);actual=dict(sha256=digest(p),mode=stat.S_IMODE(p.stat().st_mode));evidence['sources'][key]=actual
   require(not p.is_symlink()and actual['sha256']==frozen['inputs'][key]and type(frozen['inputModes'][key])is int and actual['mode']==frozen['inputModes'][key],'current frozen launcher/executable bytes/mode')
  rows=[dict(row)for proc,row in selected]
  evidence['bindings']=derive(rows,report,evidence['sources'],host.output.parent/'native')
  for proc,row in selected[3:]:
   actual=dict(name=row.get('name'),pid=proc.pid,start=row.get('start'),pgid=row.get('pgid'),command=row.get('command'),registeredExact=any(p is proc and r is row for p,r in host.processes),returncode=proc.poll(),gone=not Path('/proc/'+str(proc.pid)).exists())
   evidence['rows'].append(actual)
   require(actual['registeredExact']is True and exact(actual['pid'],row.get('pid'))and type(actual['returncode'])is int and actual['returncode']==0 and actual['gone']is True,'already normally reaped exact registered client before host close')
  require(report_path.read_bytes()==raw,'case report changed during before-close capture')
  evidence['ok']=True
 except BaseException as error:evidence['error']=repr(error)
 return evidence

def normal_clients(observation):
 proof=observation.get('clientClosureBinding');rows=observation.get('rows')
 if type(proof)is not dict or proof.get('ok')is not True or proof.get('error')is not None or proof.get('beforeDelegatedClose')is not True or proof.get('rawPersisted')is not True:return False
 if type(rows)is not list or len(rows)!=9 or [r.get('name')for r in rows]!=BASE+CLIENTS:return False
 if not exact(observation.get('registeredStopOrder'),list(reversed(BASE+CLIENTS))):return False
 bindings=proof.get('bindings');before=proof.get('rows')
 if type(bindings)is not list or type(before)is not list or len(bindings)!=6 or len(before)!=6:return False
 try:
  lives=[identity(row)for row in rows]
  require(len({tuple(v)for v in lives})==9 and len({v[0]for v in lives})==9,'unique closure lifetimes')
  for row,binding,pre in zip(rows[3:],bindings,before):
   for field in ['name','pid','start','pgid','command']:
    require(exact(row.get(field),binding.get(field))and exact(pre.get(field),binding.get(field)),'same registered before/after client')
   require(row.get('registeredExact')is True and row.get('reaped')is True and row.get('stopError')is None and type(row.get('returncode'))is int and row['returncode']==0 and exact(row.get('signals'),[]),'no client signals/forced close/error')
   require(pre.get('registeredExact')is True and type(pre.get('returncode'))is int and pre['returncode']==0 and pre.get('gone')is True,'already closed current client before delegated stop')
 except (ValueError,KeyError,TypeError):return False
 return True

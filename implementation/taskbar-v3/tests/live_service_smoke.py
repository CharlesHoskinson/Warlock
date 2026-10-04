"""Read-only check of the deployed shared shell observation service."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path(__file__).resolve().parents[1]
command=['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows','observerState']
def state():return json.loads(subprocess.check_output(command,text=True,timeout=3))
def observers():
 rows=[]
 for p in Path('/proc').glob('[0-9]*'):
  try:
   if p.stat().st_uid!=os.getuid():continue
   args=(p/'cmdline').read_bytes().split(b'\0')
   if b'/home/hoskinson/.local/share/hypr-taskbar-v3/hypr-taskbar' in args and b'observe' in args:
    fields=(p/'stat').read_text().rsplit(')',1)[1].split()
    rows.append({'pid':int(p.name),'ppid':int(fields[1]),'start':fields[19]})
  except OSError:pass
 return rows
before=state();first=observers();time.sleep(18);after=state();last=observers()
deployment=json.loads((B/'deployment.json').read_text());hashes=deployment['files']|deployment['widgetFiles'];hashes['/home/hoskinson/.config/omarchy/plugins/hoskinson.windows/manifest.json']=deployment['manifestSHA256']
checks={'oneObserver':len(first)==1 and first==last,'online':before['online'] and after['online'],
 'sameEpoch':before['epoch']==after['epoch'],'monotonic':after['sequence']>=before['sequence'],
 'noRejectedRecords':after['rejected']==0,'noErrors':after['error']=='',
 'deployedSourcesStable':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())}
report={'result':'pass' if all(checks.values()) else 'fail','scope':scope,'checks':checks,'before':before,'after':after,'observer':last,'intervalSeconds':18,'nativeWindowAcceptance':False,'readOnly':True}
(B/'tests/live-service-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
raise SystemExit(report['result']!='pass')

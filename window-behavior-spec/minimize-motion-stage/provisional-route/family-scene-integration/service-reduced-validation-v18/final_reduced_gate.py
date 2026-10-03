"""Scoped complete CPU/formal proof with no ambient desktop selectors."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;scope=require_qa_scope();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[p for p in B.iterdir()if p.is_file()and p.suffix in ('.py','.qnt','.md')];before={str(p):dict(sha256=sha(p),mode=p.stat().st_mode&0o7777)for p in names}
env={k:v for k,v in os.environ.items()if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')};env['PYTHONDONTWRITEBYTECODE']='1'
records=[]
for cmd in (['/usr/bin/python3',str(B/'check_offline.py')],['/usr/bin/python3',str(B/'collect_reduced_validation.py'),'--source-ready']):
 p=subprocess.run(cmd,cwd=B,env=env,capture_output=True,text=True,timeout=2400);records.append(dict(command=cmd,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr))
 if p.returncode:break
changed=[n for n,w in before.items()if sha(n)!=w['sha256']or Path(n).stat().st_mode&0o7777!=w['mode']]
row=dict(result='pass'if len(records)==2 and all(r['exitCode']==0 for r in records)and not changed else 'fail',scope=scope,records=records,sourceWitnesses=before,changedSources=changed,nativeLaunch=False,mainChanged=False)
fd=os.open(B/'final-reduced-gate-checkpoint.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in row.items()if k!='sourceWitnesses'}));raise SystemExit(row['result']!='pass')

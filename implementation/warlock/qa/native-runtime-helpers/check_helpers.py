#!/usr/bin/env python3
"""Protected negative checks for a reviewed helper build."""
import argparse,json,os,subprocess,sys,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--report-sha256',required=True);p.add_argument('--lock-sha256',required=True);a=p.parse_args()
repo=a.repo.resolve(strict=True);package=Path(__file__).resolve().parent;report=a.report.resolve(strict=True);out=report.parent
sys.path.insert(0,str(repo/'window-integration-qa'))
from qa_launch import require_qa_scope
require_qa_scope()
from build_helpers import InputError,resolve_input,validate,verify_build,sha
lock=package/'inputs-lock.json';pin=a.lock_sha256
def refused(fn):
 try:fn()
 except (InputError,OSError,ValueError):return
 raise AssertionError('invalid input accepted')
verify_build(report,a.report_sha256,lock,pin,repo,package)
for key in ['generated:../kiosk-shell.c','generated:/tmp/kiosk-shell.c','repo:../etc/passwd','package:../virtual_pointer.c']:
 refused(lambda key=key:resolve_input(key,repo,package,out))
refused(lambda:validate(lock,'0'*64,repo,package,out))
with tempfile.TemporaryDirectory(dir=out.parent) as tmp:
 temp=Path(tmp);bad=json.loads(lock.read_text());del bad['inputs']['package:virtual_pointer.c']['sha256'];path=temp/'missing.json';path.write_text(json.dumps(bad));refused(lambda:validate(path,sha(path),repo,package,out))
 bad=json.loads(lock.read_text());bad['inputs']['generated:kiosk-shell.c']['sha256']='0'*64;path=temp/'generated.json';path.write_text(json.dumps(bad));refused(lambda:validate(path,sha(path),repo,package,out,include_generated=True))
 env=dict(os.environ,XDG_RUNTIME_DIR=tmp,WAYLAND_DISPLAY=str(temp/'absent-socket'));r=subprocess.run([str(out/'virtual-pointer'),'1600','600'],input='sync 1\n',capture_output=True,text=True,env=env)
 assert r.returncode==3 and r.stdout=='',(r.returncode,r.stdout)
print('pinned build, generated-path traversal, missing hash, stale generated hash, and no-socket no-ack negatives pass')

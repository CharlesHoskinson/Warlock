"""External closed-profile oracles against actual source and fresh receipt parser."""
import ast,hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('profile-'+str(time.time_ns()));(OUT/'inputs/qa').mkdir(parents=True)
for p in [Path(__file__),ROOT/'qa/relay.py']:shutil.copy2(p,OUT/'inputs/qa'/p.name)
def load(p):
 s=importlib.util.spec_from_file_location('profile_relay',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=load(OUT/'inputs/qa/relay.py');checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
def refuses(fn):
 try:fn();return False
 except (r.RelayFailure,OSError,ValueError):return True
ctl=OUT/'relay-control';ctl.mkdir(mode=0o700);receiptctl=OUT/'receipt-control';receiptctl.mkdir(mode=0o700)
authority=OUT/'authority.json';authority.write_text('{}');authority.chmod(0o600)
receipt=OUT/'receipt.json';value={'authorityConfig':str(authority),'controlDirectory':str(receiptctl),'incarnation':'2','effectOperation':'restore-geometry','selectorOrdinal':2};receipt.write_text(json.dumps(value));receipt.chmod(0o600)
broker={'profile':'broker','authorityConfig':str(authority),'controlDirectory':str(ctl)};wrapped={'profile':'receipt','receiptConfig':str(receipt),'controlDirectory':str(ctl)}
report={'passed':False,'scope':'Closed fixed profiles, source pinning and fresh actual V82 configuration parser only; no native or GUI acceptance','checks':checks}
try:
 b=r.command_for(broker,REPO);w=r.command_for(wrapped,REPO)
 check('broker fixed captured V74 executable and original authority',b==['/usr/bin/python3','-B',str(REPO/'implementation/elm-geometry-staged-menu-build-v74/qa/build-1791106471110680936/inputs/adapter/daemon.py'),str(authority)])
 check('receipt fixed held V82 entrypoint and original private config',w==['/usr/bin/python3','-B',str(REPO/'implementation/elm-geometry-receipt-selector-v82/qa/broker-entrypoint.py'),str(receipt)])
 for cfg,label in [(dict(broker,profile='custom'),'unknown'),(dict(broker,command=['/bin/sh']),'arbitrary command'),(dict(broker,backend='/bin/sh'),'arbitrary backend'),(dict(broker,receiptConfig=str(receipt)),'mixed profiles'),({k:v for k,v in broker.items() if k!='profile'},'legacy unprofiled'),(dict(wrapped,authorityConfig=str(authority)),'receipt extra authority'),(dict(wrapped,receiptConfig=True),'boolean path')]:check(label+' refuses before launch',refuses(lambda:r.command_for(cfg,REPO)))
 public=OUT/'public.json';public.write_text('{}');public.chmod(0o644);check('public receipt config refused',refuses(lambda:r.command_for(dict(wrapped,receiptConfig=str(public)),REPO)))
 link=OUT/'receipt-link.json';link.symlink_to(receipt);check('receipt config symlink refused',refuses(lambda:r.command_for(dict(wrapped,receiptConfig=str(link)),REPO)))
 hard=OUT/'hard.json';os.link(receipt,hard);check('receipt config hardlink refused',refuses(lambda:r.command_for(wrapped,REPO)));hard.unlink()
 check('receipt inventory all entries verified',r.verify_receipt(REPO/'implementation/elm-geometry-receipt-selector-v82')==Path(w[2]))
 # Actual unchanged V82 parser in a new interpreter; no fake parser or native call.
 code="import importlib.util,sys;sys.path.insert(0,sys.argv[1]);s=importlib.util.spec_from_file_location('entry',sys.argv[1]+'/broker-entrypoint.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);v=m.configuration(sys.argv[2]);print(v.get('selectorOrdinal',1))"
 def parse(v):
  receipt.write_text(json.dumps(v));return subprocess.run(['/usr/bin/python3','-B','-c',code,str(Path(w[2]).parent),str(receipt)],capture_output=True)
 p=parse(value);check('actual fresh receipt parser accepts ordinal2',p.returncode==0 and p.stdout==b'2\n')
 old={k:v for k,v in value.items() if k!='selectorOrdinal'};p=parse(old);check('actual fresh receipt parser defaults ordinal1',p.returncode==0 and p.stdout==b'1\n')
 for v,label in [(dict(value,selectorOrdinal=3),'ordinal3'),(dict(value,selectorOrdinal=True),'boolean ordinal'),(dict(value,effectOperation='minimize'),'legacy operation'),(dict(value,backend='/bin/sh'),'backend injection')]:p=parse(v);check('actual receipt parser refuses '+label,p.returncode!=0 and not p.stdout)
 receipt.write_text(json.dumps(value))
 # Mutate isolated parent copy; the verifier must catch regular source and link evidence.
 copy=OUT/'receipt-copy';shutil.copytree(REPO/'implementation/elm-geometry-receipt-selector-v82',copy,symlinks=True)
 f=copy/'qa/wrapper.py';before=f.read_bytes();f.write_bytes(before+b'\n# unsafe change\n');check('changed held wrapper refused',refuses(lambda:r.verify_receipt(copy)));f.write_bytes(before)
 f.chmod(0o600);check('changed held source mode refused',refuses(lambda:r.verify_receipt(copy)));f.chmod((REPO/'implementation/elm-geometry-receipt-selector-v82/qa/wrapper.py').stat().st_mode&0o777)
 symlink=next(p for p in copy.rglob('*') if p.is_symlink());original=os.readlink(symlink);symlink.unlink();symlink.symlink_to('/tmp/foreign');check('changed preserved symlink refused',refuses(lambda:r.verify_receipt(copy)));symlink.unlink();symlink.symlink_to(original)
 m=copy/'qa/held-source-manifest.json';m.chmod(0o600);m.write_bytes(m.read_bytes()+b' ');check('changed parent inventory refused',refuses(lambda:r.verify_receipt(copy)))
 actual=ast.parse((ROOT/'qa/relay.py').read_text());parent=ast.parse((REPO/'implementation/elm-geometry-broker-eof-deadline-v92/qa/relay.py').read_text())
 names=['pump','actor_status','exit_status','close_stdin','directory','read_private','decode']
 def fn(tree,name):return ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
 check('V92 actual pump controls and strict deadlines unchanged',all(fn(actual,n)==fn(parent,n) for n in names))
 report['passed']=True
except Exception as error:report['error']=repr(error)
finally:
 report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])

"""Closed current schema5 profile/parser/source and unchanged pump proof."""
import ast,hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('profile-current-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in [*sorted((ROOT/'qa').glob('*.py')),ROOT/'backend-pin.json',ROOT/'fixture-source-pin.json']:
 target=OUT/'inputs'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
sys.path.insert(0,str(ROOT/'qa'))
import relay as r
import backend
spec=importlib.util.spec_from_file_location('current_entry',ROOT/'qa/broker-entrypoint.py');entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
checks=[];report={'passed':False,'scope':'Closed current144 schema5 profile, actual parser and source AST; no socket or native launch','checks':checks}
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
def refuses(fn):
 try:fn();return False
 except (r.RelayFailure,backend.BackendFailure,OSError,ValueError):return True
try:
 ctl=OUT/'relay-control';ctl.mkdir(mode=0o700);hold=OUT/'hold-control';hold.mkdir(mode=0o700)
 authority=OUT/'authority.json';authority.write_text('{}');authority.chmod(0o600)
 config=OUT/'receipt.json';value={'authorityConfig':str(authority),'controlDirectory':str(hold),'incarnation':'2','effectOperation':'restore-geometry','selectorOrdinal':2};config.write_text(json.dumps(value));config.chmod(0o600)
 normal={'profile':'broker','authorityConfig':str(authority),'controlDirectory':str(ctl)}
 wrapped={'profile':'receipt','receiptConfig':str(config),'controlDirectory':str(ctl)}
 check('broker exactly current captured daemon fixed Python argv',r.command_for(normal,REPO)==['/usr/bin/python3','-B',str(backend.verify_backend()),str(authority)])
 check('receipt exactly new148 entrypoint fixed Python argv',r.command_for(wrapped,REPO)==['/usr/bin/python3','-B',str(ROOT/'qa/broker-entrypoint.py'),str(config)])
 for cfg,label in [(dict(normal,profile='custom'),'unknown profile'),(dict(normal,command=['/bin/sh']),'arbitrary command'),(dict(normal,backend='/bin/sh'),'arbitrary backend'),(dict(normal,receiptConfig=str(config)),'mixed profile'),(dict(wrapped,authorityConfig=str(authority)),'extra authority'),(dict(wrapped,receiptConfig=True),'boolean path')]:check(label+' refused',refuses(lambda:r.command_for(cfg,REPO)))
 public=OUT/'public.json';public.write_text('{}');public.chmod(0o644)
 check('public receipt config refused',refuses(lambda:r.command_for(dict(wrapped,receiptConfig=str(public)),REPO)))
 link=OUT/'link.json';link.symlink_to(config)
 check('symlink config refused',refuses(lambda:r.command_for(dict(wrapped,receiptConfig=str(link)),REPO)))
 os.link(config,OUT/'hard.json');check('hardlinked config refused',refuses(lambda:r.command_for(wrapped,REPO)));(OUT/'hard.json').unlink()
 check('actual unchanged receipt parser accepts ordinal2',entry.configuration(str(config))==value)
 old={k:v for k,v in value.items() if k!='selectorOrdinal'};config.write_text(json.dumps(old))
 check('actual unchanged parser retains default ordinal1',entry.configuration(str(config)).get('selectorOrdinal',1)==1)
 for bad,label in [(dict(value,selectorOrdinal=True),'boolean ordinal'),(dict(value,selectorOrdinal=3),'ordinal3'),(dict(value,effectOperation='minimize'),'unsupported held operation'),(dict(value,backend='/bin/sh'),'code injection')]:
  config.write_text(json.dumps(bad))
  rejected=False
  try:entry.configuration(str(config))
  except Exception:rejected=True
  check('actual parser rejects '+label,rejected)
 copy=OUT/'isolated-fixture';copy.mkdir();(copy/'qa').mkdir()
 for rel in ['fixture-source-pin.json','backend-pin.json','qa/wrapper.py','qa/backend.py','qa/broker-entrypoint.py']:
  shutil.copy2(ROOT/rel,copy/rel)
 check('isolated exact receipt sources verify',r.verify_receipt(copy)==copy/'qa/broker-entrypoint.py')
 file=copy/'qa/wrapper.py';saved=file.read_bytes();file.write_bytes(saved+b'\n# mutation\n')
 check('changed receipt code refuses before child launch',refuses(lambda:r.verify_receipt(copy)));file.write_bytes(saved)
 file.chmod(0o600);check('changed receipt mode refuses',refuses(lambda:r.verify_receipt(copy)))
 def fn(path,name):
  tree=ast.parse(path.read_text());node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
  return ast.dump(node,include_attributes=False)
 parent=REPO/'implementation/elm-geometry-broker-eof-deadline-v92/qa/relay.py'
 names=['pump','actor_status','exit_status','close_stdin','directory','read_private','decode']
 check('all original V92 pump identity controls and3s deadlines unchanged',all(fn(ROOT/'qa/relay.py',name)==fn(parent,name) for name in names))
 old=REPO/'implementation/elm-geometry-receipt-selector-v82/qa/wrapper.py'
 check('original ReceiptHold5s exact key selector/watchdog implementation unchanged',fn(ROOT/'qa/wrapper.py','ReceiptHold')==fn(old,'ReceiptHold'))
 check('original receipt supervision/normalEOF release semantics unchanged',all(fn(ROOT/'qa/wrapper.py',n)==fn(old,n) for n in ['supervise','write_release','main']))
 check('host-compatible entrypoint source byteidentical',sha(ROOT/'qa/broker-entrypoint.py')==sha(old.with_name('broker-entrypoint.py')))
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])

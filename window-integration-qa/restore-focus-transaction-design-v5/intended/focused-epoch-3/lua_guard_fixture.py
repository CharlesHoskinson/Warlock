"""Lua5.5 syntax/typed-result fixture. No compositor or native Lua APIs."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from test_proposal import native,NONCE
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope()
window={'address':'0x1','stableId':'1','pid':os.getpid(),'mapped':True}
monitor={'id':0,'name':'CPU-fixture-output','x':0,'y':0,'width':1600,'height':1000,'scale':1.0,'transform':0}
plan={'identity':list(native.key(window)),'destination':'1','monitor':monitor}
owner=native.NativeDesktop.__new__(native.NativeDesktop);owner.base=SimpleNamespace()
expression=owner._focus_pair_expression(window,plan,NONCE,6,0)
rows=[]
for fault in ('normal','first-refused','second-refused','wrong-return-type','reuse-before','reuse-between-effects','output-before'):
    body='''
local w={address="0x1",stable_id=1,pid=PID,mapped=true}
local m={id=0,name="CPU-fixture-output",x=0,y=0,width=1600,height=1000,scale=1.0,transform=0}
local fault=FAULT
local effects={}
if fault=="reuse-before" then w.pid=w.pid+1 end
if fault=="output-before" then m.scale=2.0 end
hl={get_window=function(selector) assert(selector=="address:0x1"); return w end,
    get_monitor=function(selector) assert(selector==m.name); return m end,dsp={}}
hl.dsp.focus=function(args)
 return function()
  local label=args.monitor and "monitor" or "workspace"
  effects[#effects+1]=label
  if fault=="reuse-between-effects" then w.pid=w.pid+1 end
  if fault=="wrong-return-type" then return true end
  return {ok=not((fault=="first-refused" and label=="monitor") or (fault=="second-refused" and label=="workspace"))}
 end
end
hl.dispatch=function(action) return action() end
EXPRESSION
io.stderr:write(table.concat(effects,","))
'''.replace('PID',str(window['pid'])).replace('FAULT',json.dumps(fault)).replace('EXPRESSION',expression)
    result=subprocess.run(['/usr/bin/lua','-'],input=body.encode(),capture_output=True,timeout=2)
    assert result.returncode==0,result.stderr
    receipt=json.loads(result.stdout)
    expected={'normal':(True,2,'monitor,workspace'),'first-refused':(False,0,'monitor'),
        'second-refused':(False,1,'monitor,workspace'),'wrong-return-type':(False,0,'monitor'),
        'reuse-before':(False,0,''),'reuse-between-effects':(False,1,'monitor'),'output-before':(False,0,'')}[fault]
    assert (receipt['ok'],receipt['completed'],result.stderr.decode())==expected
    rows.append({'fault':fault,'argv':['/usr/bin/lua','-'],'scriptSHA256':hashlib.sha256(body.encode()).hexdigest(),
        'exitCode':result.returncode,'stdout':result.stdout.decode(),'effects':result.stderr.decode(),'expected':expected})
report={'result':'pass','scope':scope,'syntaxAndFixtureOnly':True,'nativeLuaExecuted':False,'runtimeApplied':False,
    'interpreter':'/usr/bin/lua','interpreterSHA256':hashlib.sha256(Path('/usr/bin/lua').read_bytes()).hexdigest(),
    'expression':expression,'expressionSHA256':hashlib.sha256(expression.encode()).hexdigest(),'cases':rows}
with os.fdopen(os.open(HERE/'lua-guard-fixture.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as stream:json.dump(report,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
print(json.dumps({'result':'pass','cases':len(rows),'nativeLuaExecuted':False}))

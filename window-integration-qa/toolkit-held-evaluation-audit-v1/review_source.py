"""Nongraphical source-only cleanup refinement counterexample; no producer import."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
B=Path(__file__).resolve().parent;STAGE=B.parent/'toolkit-held-matrix-v7'
sys.path.insert(0,str(B.parent));from qa_launch import require_qa_scope

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 scope=require_qa_scope();source=STAGE/'evaluation_setup.py';tree=ast.parse(source.read_text());prologue=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROLOGUE' for t in n.targets)))
 lua='local env={WINDOW_QA_EVALUATION_NONCE="'+('b'*32)+'",WINDOW_QA_EVALUATION_KIND="native-load",WINDOW_QA_EVALUATION_LIMIT="2",WINDOW_QA_EVALUATION_ORDINAL="0"}\nos.getenv=function(k)return env[k]end\nhl={env=function(k,v)env[k]=v end}\nlocal f=assert(load('+json.dumps(prologue)+'));f();f();local ok=pcall(f);assert(not ok);print(env.WINDOW_QA_EVALUATION_ORDINAL)\n'
 actual=subprocess.run(['/usr/bin/lua','-'],input=lua,text=True,capture_output=True,check=True,timeout=5);assert actual.stdout.strip()=='3'
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='ordinal');scope_code={'re':re,'json':json,'repl':lambda x:x};exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),scope_code)
 class Session:
  def guard(self):pass
  def ctl(self,*_):return '\n'.join(['b'*32,'native-load','2','3'])
 try:scope_code['ordinal'](Session(),dict(nonce='b'*32,kind='native-load',count=2))
 except RuntimeError as error:failure=str(error)
 else:raise AssertionError('Actual extra ordinal should refuse terminal arm')
 assert failure=='Unexpected extra actual Lua evaluation'
 formal=subprocess.run(['quint','test',str(B/'cleanup_counterexample.qnt')],text=True,capture_output=True,timeout=90);assert formal.returncode==0,formal.stdout+formal.stderr
 paths=[source,STAGE/'evaluation_tickets.qnt',B/'cleanup_counterexample.qnt',B/'review_source.py']
 result=dict(result='counterexample-confirmed',scope=scope,nativeCommands=False,mainWrites=False,sourceOnly=True,sources={str(p):sha(p) for p in paths},actualLuaOrdinalAfterExtraEvaluation=3,actualOrdinalGuard=failure,actualTerminalArmBlockedBeforeUnload=True,formalCleanupReachableAfterExtraEvaluation=True,formal=dict(command=['quint','test',str(B/'cleanup_counterexample.qnt')],returncode=formal.returncode,stdout=formal.stdout,stderr=formal.stderr),boundary='No actual V7 extra evaluation observed. Expected clean-commit unload1/load2 remains source-backed. This source/model difference can prevent normal native unload after an unexpected evaluation even with normal owned input/client/helper closure.',postGateEvidenceBoundary='Actual captured selectors are journaled at reservation. A separate post-gate snapshot is not retained; frozen guarded code path plus exact normal delegate terminal supplies that provenance.',stageMutated=False)
 fd=os.open(B/'source-review-counterexample.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(result,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 print(json.dumps(dict(result=result['result'],artifact=str(B/'source-review-counterexample.json'))))
if __name__=='__main__':main()

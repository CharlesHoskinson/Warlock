"""Owned nongraphical IPC plus unchanged real helper delegate, never native GUI."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import threading
import unittest
import helper_observer as h
import helper_setup as setup
import private_shell
import qa_launch
import test_evaluations
B=Path(__file__).resolve().parent

class ExactDelegate(unittest.TestCase):
 def test_actual_wrappers_delegate_once_per_captured_occurrence_and_durable_refusals(self):
  qa_launch.require_qa_scope()
  with qa_launch.owned_runtime() as folder:
   runtime=Path(folder);home=runtime/'taskbar-home';shutil.copytree(B/'payload/home',home);private_shell.normalize_home_directories(home);binary=home/'.local/bin'
   helpers={}
   for kind,name,source in [('snap','hypr-snap-groups',setup.FRESH_HELPER),('shell','omarchy-shell',B/'payload/omarchy/bin/omarchy-shell')]:
    wrapper=binary/name;actual=wrapper.with_name(name+'.actual');shutil.copyfile(source,actual);actual.chmod(0o700);shutil.copyfile(B/'helper_observer.py',wrapper);wrapper.chmod(0o700)
    helpers[kind]=dict(wrapper=str(wrapper),actual=str(actual),wrapperSHA256=h.digest(wrapper),actualSHA256=h.digest(actual),invocation=str(wrapper) if kind=='snap' else 'omarchy-shell')
   # Real Snap hydrate delegates its ordinary clients and window_families reads
   # to this owned argv recorder. No actual compositor or QS is launched.
   for name in ('hyprctl','qs'):
    recorder=binary/name;recorder.write_text('#!/usr/bin/python3\nimport os,sys,json\nfrom pathlib import Path\nwith (Path(os.environ["HOME"])/"'+name+'-argv.jsonl").open("a") as f:f.write(json.dumps(sys.argv[1:])+"\\n")\nprint("[]")\n');recorder.chmod(0o700)
   env=dict(os.environ,HOME=str(home),XDG_RUNTIME_DIR=folder,HYPRLAND_INSTANCE_SIGNATURE='actual-test-lifetime',PATH=str(binary)+':/usr/bin',OMARCHY_PATH=str(B/'payload/omarchy'),WINDOW_QA_HELPER_CONFIG=str(home/'helper-config.json'))
   config,selectors,ticket=test_evaluations.EvaluationProtocol().fixture(runtime)
   log=home/'helper-events.jsonl';log.touch(mode=0o600)
   server=socket.socket(socket.AF_UNIX);endpoint=runtime/'fixture-ipc';server.bind(str(endpoint));server.listen();server.settimeout(.1);reply=b'{"fixture":"owned nongraphical exact version EOF"}';info=endpoint.stat();stop=threading.Event();requests=[]
   config.update(socket=str(endpoint),socketIdentity=[info.st_dev,info.st_ino,info.st_uid],versionSHA256=h.digest_bytes(reply),helpers=helpers,log=str(log),allowed=h.evaluation_keys(ticket))
   ticket['armIPC']=dict(completeServerEOF=True,replySHA256=config['versionSHA256'],socketIdentity=config['socketIdentity'],peer=dict(pid=os.getpid(),uid=os.getuid()))
   # The true authorizing root is the running unittest interpreter, whose
   # source/argv/executable/lifetime are pinned independently of the child.
   ticket['root']['source']=str(Path(__file__).resolve());ticket['root']['sourceSHA256']=h.digest(__file__);config['queryRoots']['harness']=dict(ticket['root'])
   setup.write_json(Path(env['WINDOW_QA_HELPER_CONFIG']),config)
   def serve():
    while not stop.is_set():
     try:connection,_=server.accept()
     except socket.timeout:continue
     with connection:requests.append(connection.recv(1024));connection.sendall(reply)
   thread=threading.Thread(target=serve);thread.start()
   def invoke(kind,args,changes=None):
    actual={**env,**selectors,**(changes or {})}
    return subprocess.run([helpers[kind]['wrapper'],*args],env=actual,capture_output=True,text=True,timeout=5)
   try:
    self.assertEqual(invoke('snap',['hydrate']).returncode,0)
    selectors['WINDOW_QA_EVALUATION_ORDINAL']='2'
    self.assertEqual(invoke('snap',['hydrate']).returncode,0)
    relay=['hoskinson.windows','fileDrag','false','123','234','0','1']
    self.assertEqual(invoke('shell',relay).returncode,0)
    rows=[json.loads(line) for line in log.read_text().splitlines()]
    summary=h.summarize(rows,config['allowed']);self.assertTrue(summary['allNormal']);self.assertTrue(summary['allExactProcessesGone'])
    self.assertEqual(len((home/'hyprctl-argv.jsonl').read_text().splitlines()),4);self.assertEqual(len((home/'qs-argv.jsonl').read_text().splitlines()),1)
    self.assertEqual(len(requests),3)
    refusals=[]
    for kind,args,changes in [('snap',['hydrate'],None),('shell',relay,{'WINDOW_QA_EVALUATION_ORDINAL':'1'}),('snap',['hydrate'],{'WINDOW_QA_EVALUATION_NONCE':'d'*32}),('snap',['hydrate'],{'WINDOW_QA_EVALUATION_ORDINAL':'3'})]:
     result=invoke(kind,args,changes);self.assertEqual(result.returncode,125,result.stderr);refusals.append(result.stderr)
    Path(ticket['configuration']['path']).write_text('changed source witness')
    result=invoke('snap',['hydrate']);self.assertEqual(result.returncode,125,result.stderr);refusals.append(result.stderr)
    rows=[json.loads(line) for line in log.read_text().splitlines()];denied=[row for row in rows if row['event']=='refused']
    self.assertEqual(len(denied),5);self.assertTrue(all(row['delegateExecuted'] is False and row['exitCode']==125 for row in denied));self.assertEqual(''.join(refusals),''.join(row['stderr'] for row in denied))
    self.assertEqual(len((home/'hyprctl-argv.jsonl').read_text().splitlines()),4);self.assertEqual(len((home/'qs-argv.jsonl').read_text().splitlines()),1)
    self.assertTrue(all(row['evaluationEnvironment']['WINDOW_QA_EVALUATION_NONCE']==ticket['nonce'] for row in rows if row['event']=='started'))
    self.assertEqual(Path(helpers['snap']['actual']).read_bytes(),setup.FRESH_HELPER.read_bytes());self.assertEqual(Path(helpers['shell']['actual']).read_bytes(),(B/'payload/omarchy/bin/omarchy-shell').read_bytes())
    with self.assertRaises(RuntimeError):h.summarize(rows,config['allowed'])
   finally:stop.set();thread.join(timeout=2);server.close()
if __name__=='__main__':unittest.main()

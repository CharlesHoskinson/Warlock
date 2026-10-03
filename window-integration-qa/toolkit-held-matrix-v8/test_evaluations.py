"""Nongraphical exact-ticket faults and child environment transport."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import evaluation_setup as setup
import helper_observer as observer
B=Path(__file__).resolve().parent

class EvaluationProtocol(unittest.TestCase):
 def fixture(self,root,kind='native-load'):
  configuration=root/'hyprland.lua';configuration.write_text('owned immutable config\n');configuration.chmod(0o600)
  artifact=root/'candidate.so';artifact.write_bytes(b'not loaded native artifact');artifact.chmod(0o600)
  identity=observer.process(os.getpid());executable=(Path('/proc')/str(os.getpid())/'exe').resolve()
  source=Path(__file__).resolve();authorizer=dict(identity=identity,argv=observer.cmdline(os.getpid()),source=str(source),sourceSHA256=observer.digest(source),executable=str(executable),executableSHA256=observer.digest(executable))
  config=dict(compositor={key:identity[key] for key in ('pid','start')},instance='actual-test-lifetime',versionSHA256='a'*64,socketIdentity=[1,2,os.getuid()],queryRoots={'harness':authorizer},evaluationConfiguration=observer.material_witness(configuration),evaluationArtifacts={'native':observer.material_witness(artifact),'probe':observer.material_witness(artifact)},evaluationInitialCommand=['repl','actual complete paired source'],evaluationTickets=[],activeEvaluation='b'*32)
  count,relay=observer.EVALUATION_RULES[kind]
  command=['reload'] if kind=='reload' else config['evaluationInitialCommand'] if kind=='initial' else ['plugin','load' if kind=='native-load' else 'unload',str(artifact)]
  ticket=dict(serial=1,nonce=config['activeEvaluation'],kind=kind,count=count,relayOrdinal=relay,command=command,root=copy.deepcopy(authorizer),compositor=copy.deepcopy(config['compositor']),instance=config['instance'],configuration=config['evaluationConfiguration'],artifact=None if kind in ('initial','reload') else config['evaluationArtifacts']['native'],armIPC=dict(completeServerEOF=True,replySHA256=config['versionSHA256'],socketIdentity=config['socketIdentity'],peer=dict(pid=os.getpid(),uid=os.getuid())))
  config['evaluationTickets']=[ticket]
  env=dict(WINDOW_QA_EVALUATION_NONCE=ticket['nonce'],WINDOW_QA_EVALUATION_KIND=kind,WINDOW_QA_EVALUATION_LIMIT=str(count),WINDOW_QA_EVALUATION_ORDINAL='1')
  return config,env,ticket
 def test_all_source_backed_commands_exact_occurrence_and_callback_keys(self):
  for kind in observer.EVALUATION_RULES:
   with self.subTest(kind=kind),tempfile.TemporaryDirectory() as directory:
    config,env,ticket=self.fixture(Path(directory),kind)
    for index in range(1,ticket['count']+1):
     env['WINDOW_QA_EVALUATION_ORDINAL']=str(index)
     self.assertIn(observer.evaluation_operation(config,env,'hydrate'),observer.evaluation_keys(ticket))
    if ticket['relayOrdinal']:
     env['WINDOW_QA_EVALUATION_ORDINAL']=str(ticket['relayOrdinal'])
     self.assertIn(observer.evaluation_operation(config,env,'inactive-fileDrag'),observer.evaluation_keys(ticket))
 def test_superseded_first_load_relay_and_every_unload_relay_refuse(self):
  for kind in ('native-load','native-unload','probe-unload'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory() as directory:
    config,env,ticket=self.fixture(Path(directory),kind)
    with self.assertRaisesRegex(RuntimeError,'context lifetime'):observer.evaluation_operation(config,env,'inactive-fileDrag')
 def test_missing_stale_noncanonical_extra_child_selectors_refuse(self):
  with tempfile.TemporaryDirectory() as directory:
   config,env,ticket=self.fixture(Path(directory))
   changes=[('WINDOW_QA_EVALUATION_NONCE','c'*32),('WINDOW_QA_EVALUATION_NONCE',''),('WINDOW_QA_EVALUATION_ORDINAL','01'),('WINDOW_QA_EVALUATION_ORDINAL','3'),('WINDOW_QA_EVALUATION_ORDINAL','-1'),('WINDOW_QA_EVALUATION_KIND','reload'),('WINDOW_QA_EVALUATION_LIMIT','3')]
   for key,value in changes:
    actual={**env,key:value}
    with self.subTest(key=key,value=value),self.assertRaises(RuntimeError):observer.evaluation_operation(config,actual,'hydrate')
 def test_duplicate_ticket_or_active_nonce_or_serial_changed_refuses(self):
  with tempfile.TemporaryDirectory() as directory:
   config,env,ticket=self.fixture(Path(directory))
   for mutate in (lambda c:c['evaluationTickets'].append(copy.deepcopy(c['evaluationTickets'][0])),lambda c:c.update(activeEvaluation='c'*32),lambda c:c['evaluationTickets'][0].update(serial=2)):
    actual=copy.deepcopy(config);mutate(actual)
    with self.assertRaises(RuntimeError):observer.evaluation_operation(actual,env,'hydrate')
 def test_changed_exact_command_and_artifact_role_refuse(self):
  with tempfile.TemporaryDirectory() as directory:
   config,env,ticket=self.fixture(Path(directory))
   for mutate in (lambda t:t.update(command=['reload']),lambda t:t.update(command=['plugin','unload',t['artifact']['path']]),lambda t:t['artifact'].update(sha256='e'*64)):
    actual=copy.deepcopy(config);mutate(actual['evaluationTickets'][0])
    with self.assertRaises(RuntimeError):observer.evaluation_operation(actual,env,'hydrate')
 def test_root_pid_start_argv_source_and_executable_guards(self):
  with tempfile.TemporaryDirectory() as directory:
   config,env,ticket=self.fixture(Path(directory))
   for mutate in (lambda r:r['identity'].update(start='0'),lambda r:r.update(argv=['unexpected']),lambda r:r.update(sourceSHA256='d'*64),lambda r:r.update(executableSHA256='d'*64)):
    actual=copy.deepcopy(config);mutate(actual['queryRoots']['harness']);actual['evaluationTickets'][0]['root']=copy.deepcopy(actual['queryRoots']['harness'])
    with self.assertRaises(RuntimeError):observer.evaluation_operation(actual,env,'hydrate')
 def test_selected_session_peer_full_eof_and_socket_identity_guards(self):
  with tempfile.TemporaryDirectory() as directory:
   config,env,ticket=self.fixture(Path(directory))
   for mutate in (lambda t:t.update(instance='other'),lambda t:t['compositor'].update(start='0'),lambda t:t['armIPC'].update(completeServerEOF=False),lambda t:t['armIPC']['peer'].update(pid=1),lambda t:t['armIPC'].update(socketIdentity=[1,3,os.getuid()])):
    actual=copy.deepcopy(config);mutate(actual['evaluationTickets'][0])
    with self.assertRaises(RuntimeError):observer.evaluation_operation(actual,env,'hydrate')
 def test_configuration_and_artifact_byte_inode_mode_mutation_guards(self):
  for target,change in (('configuration','bytes'),('artifact','bytes'),('configuration','inode'),('artifact','mode')):
   with self.subTest(target=target,change=change),tempfile.TemporaryDirectory() as directory:
    config,env,ticket=self.fixture(Path(directory));path=Path(ticket[target]['path'])
    if change=='bytes':path.write_bytes(b'changed')
    elif change=='inode':path.unlink();path.write_text('owned immutable config\n');path.chmod(0o600)
    else:path.chmod(0o666)
    with self.assertRaises(RuntimeError):observer.evaluation_operation(config,env,'hydrate')
 def test_configuration_symlink_refuses_without_reading_target(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);source=root/'owned';source.write_text('owned');source.chmod(0o600);link=root/'link';link.symlink_to(source)
   with self.assertRaises(RuntimeError):observer.material_witness(link)
 def test_actual_child_captures_dynamic_environment_not_proc_initial_snapshot(self):
  # Only Python transport processes; no compositor/QS/client/native library.
  script='import os,subprocess,sys,json\nos.environ["WINDOW_QA_EVALUATION_NONCE"]="'+('e'*32)+'"\nos.environ["WINDOW_QA_EVALUATION_ORDINAL"]="2"\nprint(subprocess.check_output([sys.executable,"-IS","-c","import os,json; print(json.dumps({k:os.getenv(k) for k in (\\\"WINDOW_QA_EVALUATION_NONCE\\\",\\\"WINDOW_QA_EVALUATION_ORDINAL\\\")}))"],text=True).strip())\n'
  result=subprocess.run(['/usr/bin/python3','-IS','-c',script],capture_output=True,text=True,check=True,timeout=5)
  self.assertEqual(json.loads(result.stdout),dict(WINDOW_QA_EVALUATION_NONCE='e'*32,WINDOW_QA_EVALUATION_ORDINAL='2'))
 def test_prior_untouched_feature_refusal_stays_failure_terminal_scope_only(self):
  rows=[dict(event='refused',wrapper=dict(pid=1,start='old',pgid=1))]
  with patch.object(observer,'still_live',return_value=False):
   with self.assertRaisesRegex(RuntimeError,'forbids feature'):setup.terminal_closure(rows)
   self.assertTrue(setup.terminal_closure(rows,allow_refused=True))
   self.assertFalse(setup.terminal_closure(rows,required=['current:hydrate'],allow_refused=True))
  self.assertEqual(rows[0]['event'],'refused')
 def test_live_or_abnormal_prior_helper_forbids_new_feature_ticket(self):
  start=dict(event='started',operation='old',wrapper=dict(pid=1,start='1'),delegate=dict(pid=2,start='1'))
  end=dict(start,event='terminal',exitCode=0)
  with patch.object(observer,'still_live',return_value=True):self.assertFalse(setup.terminal_closure([start,end]))
  with patch.object(observer,'still_live',return_value=False):
   bad=dict(end,exitCode=125)
   with self.assertRaisesRegex(RuntimeError,'terminal mismatch'):setup.terminal_closure([start,bad])
   self.assertTrue(setup.terminal_closure([start,bad],allow_refused=True))
   with self.assertRaisesRegex(RuntimeError,'terminal mismatch'):setup.terminal_closure([start,bad],required=['old'],allow_refused=True)
 def test_missing_duplicate_wrong_lifetime_terminal_and_unknown_event_refuse(self):
  start=dict(event='started',operation='current:hydrate',wrapper=dict(pid=1,start='1'),delegate=dict(pid=2,start='1'))
  end=dict(start,event='terminal',exitCode=0)
  with patch.object(observer,'still_live',return_value=False):
   self.assertFalse(setup.terminal_closure([start],required=['current:hydrate']))
   self.assertFalse(setup.terminal_closure([start,end],required=['current:hydrate','missing']))
   for rows in ([start,end,dict(end)],[start,dict(end,wrapper=dict(pid=1,start='2'))],[dict(event='unknown')]):
    with self.assertRaises(RuntimeError):setup.terminal_closure(rows)
 def test_unlogged_actual_entry_is_pinned_until_normal_eof(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);entry=root/'exact-entry';entry.write_text('#!/usr/bin/python3\nimport sys\nprint("ready",flush=True)\nsys.stdin.read()\n');entry.chmod(0o700)
   process=subprocess.Popen([str(entry)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
   config=dict(helpers={'snap':{'wrapper':str(entry),'actual':str(root/'exact-entry.actual')},'shell':{'wrapper':str(root/'exact-shell'),'actual':str(root/'exact-shell.actual'),'invocation':'omarchy-shell'}},compositor=dict(pid=os.getpid()))
   try:
    self.assertEqual(process.stdout.readline().strip(),'ready');identity=observer.process(process.pid)
    found=setup.pending_helper_processes(config);self.assertEqual([row['identity'] for row in found],[identity]);self.assertTrue(found[0]['exactEntry'])
   finally:process.stdin.close();process.wait(timeout=5);process.stdout.close()
   self.assertEqual(process.returncode,0);self.assertEqual(setup.pending_helper_processes(config),[])
 def test_terminal_arm_requires_retained_actual_input_client_root_closure(self):
  from types import SimpleNamespace
  session=SimpleNamespace(guard=lambda:None,data=lambda *_:[])
  evaluation=setup.Evaluations({'WINDOW_QA_HELPER_CONFIG':'owned'},{},session,'owned',{})
  with self.assertRaisesRegex(RuntimeError,'normal owned lifetime'):evaluation.arm('native-unload',['plugin','unload','owned'],terminal=True)
 def test_actual_lua_prologue_two_occurrences_and_extra_evaluation_fault(self):
  script='local env={WINDOW_QA_EVALUATION_NONCE="'+('b'*32)+'",WINDOW_QA_EVALUATION_KIND="native-load",WINDOW_QA_EVALUATION_LIMIT="2",WINDOW_QA_EVALUATION_ORDINAL="0"}\nos.getenv=function(k)return env[k]end\nhl={env=function(k,v)env[k]=v end}\nlocal source='+json.dumps(setup.PROLOGUE)+'\nassert(load(source))();assert(env.WINDOW_QA_EVALUATION_ORDINAL=="1")\nassert(load(source))();assert(env.WINDOW_QA_EVALUATION_ORDINAL=="2")\nlocal ok=pcall(assert(load(source)));assert(not ok);assert(env.WINDOW_QA_EVALUATION_ORDINAL=="3")\nprint("two occurrences exact; extra evaluation refused")\n'
  result=subprocess.run(['/usr/bin/lua','-'],input=script,text=True,capture_output=True,timeout=5,check=True)
  self.assertEqual(result.stdout.strip(),'two occurrences exact; extra evaluation refused')
 def test_actual_lua_prologue_unknown_nonce_kind_limit_or_ordinal_refuses(self):
  for field,value in [('WINDOW_QA_EVALUATION_NONCE','bad'),('WINDOW_QA_EVALUATION_KIND','unknown'),('WINDOW_QA_EVALUATION_LIMIT','3'),('WINDOW_QA_EVALUATION_ORDINAL','-1')]:
   env=dict(WINDOW_QA_EVALUATION_NONCE='b'*32,WINDOW_QA_EVALUATION_KIND='native-load',WINDOW_QA_EVALUATION_LIMIT='2',WINDOW_QA_EVALUATION_ORDINAL='0');env[field]=value
   script='local env={'+','.join(k+'='+json.dumps(v) for k,v in env.items())+'}\nos.getenv=function(k)return env[k]end\nhl={env=function(k,v)env[k]=v end}\nlocal ok=pcall(assert(load('+json.dumps(setup.PROLOGUE)+')));assert(not ok)\n'
   with self.subTest(field=field):subprocess.run(['/usr/bin/lua','-'],input=script,text=True,capture_output=True,timeout=5,check=True)
 def test_actual_source_bounded_batch_and_timer_retirement_evidence(self):
  primary=B.parent/'held-load-causal-review-v1/primary'
  core=(primary/'src_plugins_PluginSystem.cpp').read_text();loop=(primary/'src_managers_eventLoop_EventLoopManager.cpp').read_text();lua=(primary/'src_config_lua_ConfigManager.cpp').read_text()
  self.assertEqual(core.count('g_pEventLoopManager->doLater([] { Config::mgr()->reload(); });'),2)
  self.assertIn('auto fns  = std::move(IDLE->fns);',loop);self.assertIn('for (auto& f : fns)',loop)
  self.assertIn('t.timer->cancel();',lua);self.assertIn('g_pEventLoopManager->removeTimer(t.timer);',lua);self.assertIn('m_luaTimers.clear();',lua)
 def test_original_action_still_unload_load_then_explicit_reload(self):
  source=(B/'held_route.py').read_text();start=source.index("if end=='unload-reload':");end=source.index("if end=='close-reopen':",start);branch=source[start:end]
  self.assertLess(branch.index("ctl('plugin','unload'"),branch.index("ctl('plugin','load'"));self.assertLess(branch.index("ctl('plugin','load'"),branch.index("ctl('reload')"))
  self.assertIn("arm('native-unload'",branch);self.assertIn("arm('native-load'",branch);self.assertIn("arm('reload'",branch)
 def test_final_queue_drain_and_resample_precede_host_runtime_deletion(self):
  source=(B/'run_native.py').read_text();final=source[source.index('            if loaded:'):]
  self.assertLess(final.index("arm('native-unload'"),final.index("ctl('plugin','unload',str(plugin))"))
  self.assertLess(final.index("arm('probe-unload'"),final.index("ctl('plugin','unload',str(probe))"))
  self.assertLess(final.index("complete(probe_ticket)"),final.index("'finalCompletedHelpers'"))
  self.assertIn('helper_setup.retain_before_runtime_delete',source)
if __name__=='__main__':unittest.main()

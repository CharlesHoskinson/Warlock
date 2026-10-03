import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from public_toolkit import actual_backend,paired_button,PublicFixture
from held_controller import allocated_point
from input_control import PinnedInput
import helper_setup

IDENTITY=dict(address='0xabc',stableId='1',pid=123)
NATIVE=dict(IDENTITY,surfaceBox=[100,250,460,300],mapped=True,hidden=False,acceptsInput=True)
QT=dict(pid=123,platform='wayland',windows=dict(source=dict(geometryGlobal=[9999,9999,460,300],buttonClient=[11,139,438,22],layoutGeometry=[0,0,460,300],visible=True,native=True,enabled=True,clicks=0)))

class Protocol(unittest.TestCase):
 def test_qt_native_origin_and_gtk_actual_transform(self):
  self.assertEqual(paired_button(QT,'source',NATIVE,'QtWidgets'),[330,400])
  gtk=dict(windows=dict(source=dict(client=[460,300],buttonClient=[11,139,438,22],mapped=True,surfaceTransform=[True,0,0])))
  self.assertEqual(paired_button(gtk,'source',NATIVE,'GTK4'),[330,400])
 def test_stale_or_outside_allocation_refuses(self):
  for change in (lambda q:q['windows']['source'].update(geometryGlobal=[0,0,999,300]),lambda q:q['windows']['source'].update(buttonClient=[11,139,999,22]),lambda q:q['windows']['source'].update(enabled=False)):
   row=copy.deepcopy(QT);change(row)
   with self.assertRaises(ValueError):paired_button(row,'source',NATIVE,'QtWidgets')
 def test_actual_caption_and_group_allocations_not_fixed_offset(self):
  state=dict(decorationAllocations=[dict(window=IDENTITY,name='Hyprbar',type=4,flags=1,box=[105,222,450,24]),dict(window=IDENTITY,name='Group',type=0,flags=1,box=[105,210,450,12])])
  self.assertEqual(allocated_point(state,IDENTITY,'caption'),[330,234]);self.assertEqual(allocated_point(state,IDENTITY,'group'),[330,216])
  with self.assertRaises(ValueError):allocated_point(state,dict(IDENTITY,stableId='2'),'caption')
 def test_native_backend_and_frozen_actual_mapped_module_required(self):
  variant=dict(toolkit='QtWidgets',backend='wayland');modules={'/usr/lib/qt6/plugins/platforms/libqwayland-egl.so':'digest'};clients=[dict(pid=123,xwayland=False)]
  self.assertEqual(actual_backend(QT,clients,variant,123,modules,modules)['backend'],'wayland')
  with self.assertRaises(ValueError):actual_backend(QT,[dict(pid=123,xwayland=True)],variant,123,modules,modules)
  with self.assertRaises(ValueError):actual_backend(QT,clients,variant,123,modules,{})
 def test_unknown_fixture_commands_refuse_before_guard_or_io(self):
  client=PublicFixture(None,'QtWidgets','/unusable',lambda:self.fail('must not call guard'),None)
  for name in ('focus','setText','move','click','invokeCallback'):
   with self.assertRaises(ValueError):client.command(name)
 def test_public_alias_preserves_actual_nested_source_bytes(self):
  with tempfile.TemporaryDirectory() as folder:
   state=dict(pid=123,windows=dict(nested=dict(clicks=2)));Path(folder,'state.json').write_text(json.dumps(state))
   from types import SimpleNamespace
   fixture=PublicFixture(SimpleNamespace(pid=123),'QtWidgets',folder,lambda:None,None,aliases={'source':'nested'})
   self.assertEqual(fixture.state()['windows']['source'],state['windows']['nested']);self.assertEqual(json.loads(Path(folder,'state.json').read_text()),state)
 def test_exact_owned_non_graphical_input_pipe_transitions_normal_eof(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);script=root/'producer.py';script.write_text('import sys\nfor line in sys.stdin:\n if line=="sync\\n":print("ready",flush=True)\n')
   env=dict(os.environ,HOME=folder,XDG_RUNTIME_DIR=folder,WAYLAND_DISPLAY='owned-fixture',HYPRLAND_INSTANCE_SIGNATURE='owned-fixture',POINTER_QA_COMPOSITOR_PID=str(os.getpid()),POINTER_QA_COMPOSITOR_START='fixture',HYPR_A11Y_BRIDGE_PRIVATE='1')
   command=['/usr/bin/python3',str(script)];process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,env=env,start_new_session=True)
   try:
    control=PinnedInput(process,command,env,lambda:None,'pointer');control.button(272,True)
    with self.assertRaises(ValueError):control.button(272,True)
    with self.assertRaises(ValueError):control.absolute([-1,0],[1600,1000])
    result=control.close();self.assertTrue(result['normalEOF']);self.assertEqual(control.down,set());self.assertTrue(any(row['command']=='button 272 0' for row in result['trace']))
   finally:
    if process.poll() is None:process.stdin.close();process.wait(timeout=3)
    process.stdout.close()
 def test_reload_generation_requires_prior_helpers_normal_and_retained(self):
  config=dict(log='owned',loadGeneration=1,allowed=['generation:1:hydrate','generation:1:inactive-fileDrag'])
  from contextlib import nullcontext
  events=[dict(event='started',operation='generation:1:hydrate',wrapper=dict(pid=1,start='1'),delegate=dict(pid=2,start='1'))]
  with patch.object(helper_setup.observer,'locked_log',return_value=nullcontext(None)),patch.object(helper_setup.observer,'read_config',return_value=config),patch.object(helper_setup.observer,'rows',return_value=events),patch.object(helper_setup.observer,'still_live',return_value=False),patch.object(helper_setup,'write_json') as write:
   with self.assertRaisesRegex(RuntimeError,'incomplete'):helper_setup.register_load_generation({'WINDOW_QA_HELPER_CONFIG':'owned'},config)
   self.assertFalse(write.called)
   events.append(dict(events[0],operation='generation:1:inactive-fileDrag'))
   with self.assertRaisesRegex(RuntimeError,'normally retire'):helper_setup.register_load_generation({'WINDOW_QA_HELPER_CONFIG':'owned'},config)
   events.append(dict(events[0],event='terminal',exitCode=0))
   events.append(dict(events[1],event='terminal',exitCode=0))
   self.assertEqual(helper_setup.register_load_generation({'WINDOW_QA_HELPER_CONFIG':'owned'},config),2)
   self.assertIn('generation:1:hydrate',config['allowed']);self.assertIn('generation:2:hydrate',config['allowed'])

 def test_reload_refusal_duplicate_and_nonzero_terminal_never_register(self):
  from contextlib import nullcontext
  for problem in ('refused','duplicate','nonzero'):
   config=dict(log='owned',loadGeneration=1,allowed=['generation:1:hydrate','generation:1:inactive-fileDrag'])
   starts=[dict(event='started',operation=key,wrapper=dict(pid=1,start='1'),delegate=dict(pid=2,start='1')) for key in config['allowed']]
   events=starts+[dict(row,event='terminal',exitCode=0) for row in starts]
   if problem=='refused':events.append(dict(event='refused'))
   if problem=='duplicate':events.append(starts[0])
   if problem=='nonzero':events[-1]['exitCode']=125
   with patch.object(helper_setup.observer,'locked_log',return_value=nullcontext(None)),patch.object(helper_setup.observer,'read_config',return_value=config),patch.object(helper_setup.observer,'rows',return_value=events),patch.object(helper_setup.observer,'still_live',return_value=False),patch.object(helper_setup,'write_json') as write:
    with self.assertRaises(RuntimeError):helper_setup.register_load_generation({'WINDOW_QA_HELPER_CONFIG':'owned'},config)
    self.assertFalse(write.called);self.assertEqual(config['loadGeneration'],1)
 def test_real_layer_item_point_requires_exact_mapped_allocation(self):
  from frontend_route import layer,item_point
  state=dict(layers=[dict(pid=123,namespace='real',mapped=True,visible=True,box=[50,100,600,40])])
  row=layer(state,123,'real');self.assertEqual(item_point(dict(x=200,y=0,width=100,height=40),row),[300,120])
  with self.assertRaises(ValueError):layer(state,124,'real')
  with self.assertRaises(ValueError):item_point(dict(x=601,y=0,width=100,height=40),row)
 def test_exact_identity_bool_and_float_pid_refused(self):
  from observations import exact
  self.assertTrue(exact(IDENTITY,dict(IDENTITY)))
  for value in (True,123.0,0,-1):self.assertFalse(exact(IDENTITY,dict(IDENTITY,pid=value)))

if __name__=='__main__':unittest.main(verbosity=2)

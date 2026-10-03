import ast,copy,importlib.util,json,os,signal,subprocess,sys,tempfile,time,types,unittest
from pathlib import Path
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('host_observation',B/'proposed/host_observation.py');ob=importlib.util.module_from_spec(spec);spec.loader.exec_module(ob)
original=ast.parse((B/'inverses/original-host.py').read_text());functions=[n for n in original.body if isinstance(n,ast.FunctionDef)and n.name in ['process','same_process']]
ns={'Path':Path,'os':os};exec(compile(ast.Module(body=functions,type_ignores=[]),'exact-original-process-functions','exec'),ns)
class Observer(ob.ObservedShutdownMixin):
 _original_module=types.SimpleNamespace(same_process=ns['same_process'])
 def __init__(self,child,row):self.processes=[(child,row)];self.evidence={}
class HostObservation(unittest.TestCase):
 def test_whole_stop_inverse_and_original_limits(self):
  tree=ast.parse((B/'proposed/host_observation.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef));n=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='_inherited_stop')
  original_cls=next(n for n in original.body if isinstance(n,ast.ClassDef)and n.name=='PrivateWestonHost');before=next(n for n in original_cls.body if isinstance(n,ast.FunctionDef)and n.name=='stop')
  class Inverse(ast.NodeTransformer):
   def visit_FunctionDef(self,n):n.name='stop';return self.generic_visit(n)
   def visit_Call(self,n):
    n=self.generic_visit(n)
    if isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='self':
     if n.func.attr=='_observed_signal':n.func=ast.Attribute(value=ast.Name(id='os',ctx=ast.Load()),attr='kill',ctx=ast.Load())
     elif n.func.attr=='_same_process':n.func=ast.Name(id='same_process',ctx=ast.Load())
    return n
  self.assertEqual(ast.dump(before,include_attributes=False),ast.dump(Inverse().visit(copy.deepcopy(n)),include_attributes=False))
 def kernel(self,ignore):
  code='import signal,time,sys;signal.signal(signal.SIGTERM,'+('lambda *_:None'if ignore else'lambda *_:sys.exit(0)')+');print("ready",flush=True);time.sleep(30)'
  child=subprocess.Popen([sys.executable,'-c',code],stdout=subprocess.PIPE,text=True,start_new_session=True)
  try:
   self.assertEqual(child.stdout.readline(),'ready\n');row=ns['process'](child.pid);row['name']='hyprland';observer=Observer(child,row);start=time.monotonic();observer.stop(row,child);child.wait(timeout=4)
   stop=observer.evidence['ownedStops'][0]
   record=dict(**row,registeredExact=stop['registeredExact'],reaped=True,returncode=child.returncode,signals=stop['signals'],stopError=stop['error'])
   return record,time.monotonic()-start
  finally:
   if child.poll()is None:child.kill();child.wait(timeout=4)
   child.stdout.close()
 def test_actual_handled_term_zero(self):
  row,elapsed=self.kernel(False);self.assertEqual(row['returncode'],0);self.assertEqual([e['signal']for e in row['signals']],[signal.SIGTERM]);self.assertTrue(ob.normal_row(row));self.assertLess(elapsed,4)
 def test_actual_escalation_cannot_count_normal(self):
  row,elapsed=self.kernel(True);self.assertEqual(row['returncode'],-signal.SIGKILL);self.assertEqual([e['signal']for e in row['signals']],[signal.SIGTERM,signal.SIGKILL]);self.assertFalse(ob.normal_row(row));self.assertGreaterEqual(elapsed,4)
 def test_strict_terminal_rows(self):
  row=dict(name='hyprland',pid=99,start='123',pgid=99,registeredExact=True,reaped=True,returncode=0,signals=[dict(pid=99,signal=15,sent=True,error=None)],stopError=None)
  self.assertTrue(ob.normal_row(row))
  for field,value in [('pid',99.0),('pgid',True),('returncode',False),('reaped',1),('registeredExact',1),('start',123),('returncode',-15),('returncode',-9),('returncode',None)]:
   bad=copy.deepcopy(row);bad[field]=value;self.assertFalse(ob.normal_row(bad),(field,value))
  bad=copy.deepcopy(row);bad['signals'][0]['pid']=99.0;self.assertFalse(ob.normal_row(bad))
  bus=copy.deepcopy(row);bus.update(name='privateBus',returncode=-15);self.assertTrue(ob.normal_row(bus));bus['signals']=[];self.assertFalse(ob.normal_row(bus))
 def test_separate_closure_requires_exact_order_roles(self):
  base=dict(pid=99,start='123',pgid=99,registeredExact=True,reaped=True,returncode=0,signals=[],stopError=None)
  rows=[dict(**base,name=n)for n in ['privateBus','weston','hyprland']]
  record=dict(rows=rows,registeredStopOrder=['hyprland','weston','privateBus'],closeError=None)
  self.assertTrue(ob.normal_closure(record));record['registeredStopOrder'].reverse();self.assertFalse(ob.normal_closure(record));record['registeredStopOrder'].reverse();record['rows'][2]['returncode']=-9;self.assertFalse(ob.normal_closure(record))
if __name__=='__main__':unittest.main(verbosity=2)

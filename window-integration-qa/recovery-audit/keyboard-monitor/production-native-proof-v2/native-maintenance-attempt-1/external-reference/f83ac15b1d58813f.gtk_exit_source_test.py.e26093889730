"""Extracted actual GTK command source, no GTK display or synthetic AX event."""
import ast,contextlib,io,json,sys,unittest
from pathlib import Path
from types import SimpleNamespace as NS
ROOT=Path(__file__).parent
class Output(io.StringIO):
 def __init__(self,events):super().__init__();self.events=events
 def flush(self):self.events.append(('flush',self.getvalue()))
def invoke(filename,line):
 events=[];out=Output(events)
 app=NS(quit=lambda:events.append(('quit',None)))
 ns={'sys':NS(stdin=io.StringIO(line)),'app':app,'json':json,'snapshot':lambda:events.append(('snapshot',None)),'popover':None,'popup_button':None,'window':lambda name:events.append(('window',name)),'tag':'A'}
 tree=ast.parse((ROOT/filename).read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='command')
 exec(compile(ast.Module(body=[fn],type_ignores=[]),str(ROOT/filename),'exec'),ns)
 with contextlib.redirect_stdout(out):result=ns['command'](None,None)
 return result,out.getvalue(),events
class ExitSource(unittest.TestCase):
 def test_actual_old_exit_counterexample(self):
  result,text,events=invoke('gtk_peer_old.py','{"operation":"exit"}\n')
  self.assertFalse(result);self.assertEqual(text,'');self.assertEqual(events,[('quit',None)])
 def test_real_source_acknowledges_before_quit(self):
  result,text,events=invoke('gtk_peer.py','{"operation":"exit"}\n')
  self.assertFalse(result);self.assertEqual(json.loads(text),{'pass_':True,'operation':'exit'})
  self.assertEqual(len(text.splitlines()),1);self.assertEqual(events[0][0],'flush');self.assertEqual(events[1],('quit',None))
 def test_eof_without_request_quits_without_reply(self):
  result,text,events=invoke('gtk_peer.py','');self.assertFalse(result);self.assertEqual(text,'');self.assertEqual(events,[('quit',None)])
 def test_nonexit_snapshot_reply_preserved(self):
  result,text,events=invoke('gtk_peer.py','{"operation":"second"}\n');self.assertTrue(result);self.assertEqual(json.loads(text),{'pass_':True,'operation':'second'});self.assertEqual([e[0] for e in events],['window','snapshot','flush'])
if __name__=='__main__':unittest.main()

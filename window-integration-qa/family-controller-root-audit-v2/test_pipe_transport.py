import os
from pathlib import Path
import tempfile
import time
import unittest
from pipe_transport import PipeTransport

SCRIPT='''#!/usr/bin/env python3
import json,sys
print(json.dumps({'event':'outputs','outputs':[{'name':'test','generation':1}]}),flush=True)
for line in sys.stdin:
 m=json.loads(line)
 if m['command']=='stop':break
 if m['command']=='exitBad':sys.exit(7)
 if m['command']=='malformed':print('{bad',flush=True);break
 print(json.dumps({'event':'state','observationId':m.get('observationId'),'payload':m.get('payload')}),flush=True)
'''
class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'fake-renderer';self.path.write_text(SCRIPT);self.path.chmod(0o700);self.failures=[]
        self.t=PipeTransport(self.path,env=dict(os.environ),failure=self.failures.append)
    def tearDown(self):
        try:self.t.close()
        except RuntimeError:pass
        self.temp.cleanup()
    def wait(self,p):
        end=time.monotonic()+2
        while time.monotonic()<end:
            if p():return
            time.sleep(.002)
        self.fail('pipe boundary timeout')
    def test_persistent_ordered_json_pipe_and_normal_exit(self):
        self.wait(lambda:self.t.outputs());self.assertEqual(self.t.outputs(),[{'name':'test','generation':1}])
        for i in range(30):self.t.send({'command':'state','observationId':i,'payload':'line\n雪'})
        self.wait(lambda:len([e for e in self.t.events if e['event']=='state'])==30)
        states=[e for e in self.t.events if e['event']=='state'];self.assertEqual([e['observationId'] for e in states],list(range(30)));self.assertEqual(states[-1]['payload'],'line\n雪')
        self.assertEqual(self.t.close(),0);self.assertFalse(self.failures)
    def test_nonfinite_and_unbounded_commands_reject_before_wire(self):
        with self.assertRaises(ValueError):self.t.send({'command':'state','payload':float('nan')})
        with self.assertRaises(ValueError):self.t.send({'command':'state','payload':'x'*1048576})
        self.assertEqual(self.t.close(),0)
    def test_malformed_event_retires_transport_once(self):
        self.t.send({'command':'malformed'});self.wait(lambda:self.t.failed);self.assertEqual(len(self.failures),1)
        with self.assertRaises(BrokenPipeError):self.t.send({'command':'state'})
    def test_nonzero_shutdown_cannot_be_accepted_as_cleanup(self):
        self.t.send({'command':'exitBad'});self.wait(lambda:self.t.failed)
        with self.assertRaises(RuntimeError):self.t.close()
        self.assertEqual(self.t.process.returncode,7)

if __name__=='__main__':unittest.main()

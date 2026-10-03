#!/usr/bin/env python3
"""Staged snap helper disk migration; mocked snapshots, no compositor restart."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HELPER = Path(os.getenv('SNAP_SESSION_HELPER',str(Path.home()/'.local/bin/hypr-snap-groups')))


class SnapSession(unittest.TestCase):
    def test_disk_migration_reload_close_and_new_instance(self):
        with tempfile.TemporaryDirectory(prefix='snap-session-') as directory:
            root = Path(directory)
            binary=root/'bin';binary.mkdir()
            ctl=binary/'hyprctl'
            ctl.write_text('#!/usr/bin/env python3\nimport os,pathlib,sys\nr=pathlib.Path(os.environ["HYPR_SNAP_STATE_DIR"])\nwith (r/"ctl.log").open("a") as f:f.write(sys.argv[1]+":"+os.environ.get("HYPRLAND_INSTANCE_SIGNATURE","")+"\\n")\nif sys.argv[1]=="clients":print((r/"clients.json").read_text())\nelif sys.argv[1]=="instances":print((r/"instances.json").read_text())\nelif sys.argv[1]=="repl":print("[]")\nelse:print("ok")\n')
            ctl.chmod(0o755)
            windows=[{'address':'0x1','pid':42,'initialClass':'qa','stableId':'a','workspace':{'name':'1'},'monitor':0},
                     {'address':'0x2','pid':43,'initialClass':'qa','stableId':'b','workspace':{'name':'1'},'monitor':0}]
            (root/'clients.json').write_text(json.dumps(windows))
            state={'version':1,'next_id':1,'snapped':{},'groups':[{'id':'snap-1','addresses':['0x1','0x2']}]}
            for w,zone in zip(windows,['left','right']):
                state['snapped'][w['address']]={'identity':[w['address'],w['pid'],'qa',w['stableId']], 'zone':zone,'workspace':'1','monitor':0,'normalSize':[640,480],'normalRect':[100,100,640,480]}
            (root/'state.json').write_text(json.dumps(state))
            env=dict(os.environ,PATH=str(binary)+':'+os.environ['PATH'],HYPR_SNAP_STATE_DIR=str(root),HYPRLAND_INSTANCE_SIGNATURE='session-first')
            def listing():
                return json.loads(subprocess.check_output([str(HELPER),'list'],env=env,text=True))
            self.assertEqual(len(listing()),1, 'legacy live state retained')
            saved=json.loads((root/'state.json').read_text())
            self.assertEqual(saved['instance'],'session-first')
            self.assertEqual(saved['snapped']['0x1']['normalRect'],[100,100,640,480])
            self.assertEqual(len(listing()),1,'same session process restart retains group')
            self.assertNotIn('instances:',(root/'ctl.log').read_text(),'explicit signature is strict')
            env.pop('HYPRLAND_INSTANCE_SIGNATURE')
            (root/'instances.json').write_text(json.dumps([{'instance':'session-first'}]))
            self.assertEqual(len(listing()),1,'missing env resolves unique compositor')
            calls=(root/'ctl.log').read_text().splitlines()
            unique_lookup=calls.index('instances:')
            self.assertEqual(calls[unique_lookup+1],'clients:session-first','subsequent queries share resolved target')
            original_disk=(root/'state.json').read_bytes()
            (root/'instances.json').write_text(json.dumps([{'instance':'session-first'},{'instance':'other'}]))
            rejected=subprocess.run([str(HELPER),'list'],env=env,text=True,capture_output=True)
            self.assertNotEqual(rejected.returncode,0)
            self.assertIn('no unique compositor',rejected.stderr)
            self.assertEqual((root/'state.json').read_bytes(),original_disk,'ambiguous target cannot clear or retag state')
            (root/'instances.json').write_text('[]')
            rejected=subprocess.run([str(HELPER),'list'],env=env,text=True,capture_output=True)
            self.assertNotEqual(rejected.returncode,0)
            self.assertEqual((root/'state.json').read_bytes(),original_disk,'unavailable compositor cannot write state')
            # Exact PID/address/stable-ID reuse cannot recreate a foreign session.
            env['HYPRLAND_INSTANCE_SIGNATURE']='session-second'
            self.assertEqual(listing(),[])
            self.assertEqual(json.loads((root/'state.json').read_text())['snapped'],{})
            # A close missed while the helper was down is removed by live sync.
            saved['instance']='session-second'
            (root/'state.json').write_text(json.dumps(saved))
            (root/'clients.json').write_text(json.dumps(windows[:1]))
            self.assertEqual(listing(),[])
            self.assertNotIn('0x2',json.loads((root/'state.json').read_text())['snapped'])


if __name__=='__main__':unittest.main()

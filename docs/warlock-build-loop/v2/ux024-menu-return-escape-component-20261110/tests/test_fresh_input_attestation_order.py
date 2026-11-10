#!/usr/bin/env python3
"""Actual loop/consume/attest ordering under fixed mocks; no process or GUI effects."""
import argparse,ast,copy,importlib.util,os,stat,sys,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
p=argparse.ArgumentParser();p.add_argument('--module',required=True);args,rest=p.parse_known_args()
spec=importlib.util.spec_from_file_location('guard_order_runner',args.module)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Controls(unittest.TestCase):
    def test_each_input_has_one_full_fresh_attestation_and_guard_failure_stops_input(self):
        tree=ast.parse(Path(args.module).read_text())
        execute=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
        loops=[n for n in ast.walk(execute) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call)
               and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='enumerate'
               and len(n.iter.args)==1 and isinstance(n.iter.args[0],ast.Name) and n.iter.args[0].id=='MENU_STEPS']
        self.assertEqual(len(loops),1)
        # Execute the unchanged production transaction loop, not a rewritten test loop.
        wrapper=ast.parse('def transaction_loop(phase_channel,receipt,packet,output,command,geometry,clock,same_window,keyboard):\n    pass\n')
        wrapper.body[0].body=[copy.deepcopy(loops[0])];ast.fix_missing_locations(wrapper)
        namespace=dict(vars(m));exec(compile(wrapper,'<actual-transaction-loop>','exec'),namespace)
        for failed in (None,'current','keyboard','window','backing','deadline'):
            with self.subTest(failed=failed):
                events=[];index=[0];inputs=[]
                def guard(name):
                    events.append((index[0],name))
                    if failed==name and index[0]==4:raise ValueError('guard failed: '+name)
                owner=object.__new__(m._ObserverCloseSnapshots)
                owner.current=lambda:guard('current');owner.held=SimpleNamespace(attest=lambda:guard('keyboard'))
                owner.same_window=lambda:guard('window');owner.backend=SimpleNamespace(pid=101,poll=lambda:None)
                owner.backend_birth='7';owner.window={'pid':102};owner.window_birth='7'
                owner.parent_pid=103;owner.parent_birth='7';owner.parent_fd='10';owner.path='/fixed/private-root'
                owner.root_fd=10;owner.root_pin=(1,2,os.getuid());owner.role_fds={'bar':11,'popup':12}
                owner.role_pins={'bar':owner.root_pin,'popup':owner.root_pin};owner.owner_pid='1'
                owner.assets={'owner':{'sha256':m.digest(b'image')}};owner.clock={'deadline':99}
                owner.journey=True;owner.journey_step=0;owner.ready=None
                def await_phase(step):
                    index[0]=[x['name']for x in m.MENU_STEPS].index(step);owner.ready=step
                owner.await_phase=await_phase
                owner._private_dir=lambda value:guard('backing')
                receipt={'frames':[],'keyboardTransactions':[]}
                def command(role,argv):
                    events.append((index[0],role))
                    if role=='wtype':inputs.append(index[0])
                    return b''
                status=SimpleNamespace(st_dev=1,st_ino=2,st_uid=os.getuid(),st_mode=stat.S_IFDIR|0o700)
                def regular(path,*unused):return b'NSpid: 102 1\n' if str(path).endswith('/status') else b'image'
                with patch.object(m,'birth',return_value=('7',100)),patch.object(m,'descendant',return_value=True),\
                     patch.object(m.os,'readlink',return_value=owner.path),patch.object(m.os,'stat',return_value=status),\
                     patch.object(m.os,'lstat',return_value=status),patch.object(m.os,'fstat',return_value=status),\
                     patch.object(m.Path,'resolve',lambda path:path),patch.object(m,'regular',side_effect=regular),\
                     patch.object(m,'left',side_effect=lambda clock:guard('deadline')):
                    namespace['regular']=regular
                    call=lambda:namespace['transaction_loop'](owner,receipt,{'input':{'frameLimit':16}},Path('/fixed'),command,
                        SimpleNamespace(require_frame=lambda *a:None),owner.clock,owner.same_window,owner.held)
                    if failed is None:call()
                    else:
                        with self.assertRaisesRegex(ValueError,'guard failed'):call()
                expected=list(range(9 if failed is None else 4));self.assertEqual(inputs,expected)
                for i in expected:
                    sequence=[kind for at,kind in events if at==i]
                    self.assertEqual(sequence.count('current'),1)
                    self.assertEqual(sequence.count('keyboard'),1)
                    self.assertEqual(sequence.count('window'),1)
                    self.assertEqual(sequence[:4],['grim','current','keyboard','window'])
                    self.assertIn('backing',sequence)
                    self.assertEqual(sequence[-3:],['deadline','deadline','wtype'])
                self.assertEqual(owner.journey_step,len(expected))
if __name__=='__main__':unittest.main(argv=[sys.argv[0],*rest])

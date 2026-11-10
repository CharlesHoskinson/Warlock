#!/usr/bin/env python3
"""Fixed pure/mocked connected-runner contracts; no target import or native effect."""
import argparse,ast,copy,importlib.util,io,json,sys,unittest
from pathlib import Path
from unittest.mock import Mock,patch
p=argparse.ArgumentParser();p.add_argument('--module',required=True);args,rest=p.parse_known_args()
spec=importlib.util.spec_from_file_location('fixed_connected_observer',args.module);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class Controls(unittest.TestCase):
    def packet(self):
        assets={role:{'path':'/fixed/'+role,'sha256':'a'*64} for role in m.ASSETS}
        return dict(schema=1,kind='ux024-connected-foreign-toplevel-observer',armed=True,recordPath=m.RECORD,recordIdentitySha256=m.IDENTITY,selectionGeneration=29,
          authorization={},sourceHashes={**m.HELPERS,str(m.SELF.relative_to(m.ROOT)):'a'*64},guardHashes={},assets=assets,
          assetSources={role:{} for role in m.ASSETS-{'nestedConfig'}},buildReport={},foundationPacket={},foundationReport={},reuse={},
          reviews={role:{} for role in m.REVIEWS},input={'monitorSize':[1280,720],'windowSize':[980,680],'closeArgv':m.CLOSE_ARGV,'pointer':False,'frameLimit':16},
          binding={'lifetime':'1','session':'2','frontend':'3'},contract={},processInventory={'/fixed/runtime':'a'*64},abi={},keyboardBuildReport={},documentBuildReport={},documentFixtureOnly=True)
    def phase(self,phase='READ_WINDOW',sequence=2,rows=None):
        return dict(schema=1,nonce='a'*64,sequence=sequence,phase=phase,binding={'lifetime':'1','session':'2','frontend':'3'},configChecks=15,nativeAcceptance=False,readsPerformed=1,rows=[] if rows is None else rows)
    def row(self):
        return dict(handleOrdinal='1',identityScope='same-owner-QA-label-not-protocol-wire-id',title='Actual owned window',appId='owned.app',states=['activated'],outputOrdinals=['1'],parentOrdinal=None)
    def terminal(self):
        return dict(schema=1,nonce='a'*64,sequence=4,phase='RETIRE',binding={'lifetime':'1','session':'2','frontend':'3'},configChecks=15,nativeAcceptance=False,completedPhases=4,actionPassed=True,status='Retired',passed=True,error=None)
    def test_fixed_packet_scope_and_no_arbitrary_command(self):
        self.assertIs(m.parse_packet(self.packet())['armed'],True)
        for field,value in [('schema',True),('armed',False),('recordPath','.warlock-contributor/other.json'),('recordIdentitySha256','b'*64),('selectionGeneration',True),('documentFixtureOnly',False)]:
            packet=self.packet();packet[field]=value
            with self.assertRaises(ValueError):m.parse_packet(packet)
        packet=self.packet();packet['command']=['sh']
        with self.assertRaises(ValueError):m.parse_packet(packet)
    def test_no_pointer_asset_or_alternate_close(self):
        packet=self.packet();packet['assets']['pointer']={'path':'/fixed/pointer','sha256':'b'*64}
        with self.assertRaises(ValueError):m.parse_packet(packet)
        packet=self.packet();packet['input']['closeArgv']=['--','sh']
        with self.assertRaises(ValueError):m.parse_packet(packet)
    def test_positive_u64_binding_not_boolean_or_wrapped(self):
        for value in ['0','-1','01',True,str(2**64),'1;sh']:
            packet=self.packet();packet['binding']['frontend']=value
            with self.assertRaises(ValueError):m.parse_packet(packet)
    def test_phase_current_nonce_binding_config_and_role(self):
        base=self.phase(rows=[self.row()]);bound=base['binding'];m.phase_response(base,'READ_WINDOW',2,'a'*64,bound)
        for key,value in [('nonce','b'*64),('binding',dict(bound,frontend='9')),('sequence',True),('phase','ACK'),('configChecks',13),('nativeAcceptance',True),('schema',True)]:
            row=copy.deepcopy(base);row[key]=value
            with self.assertRaises(ValueError):m.phase_response(row,'READ_WINDOW',2,'a'*64,bound)
    def test_phase_exact_read_and_output_bounds(self):
        for phase,sequence,read in [('READ_INITIAL',1,2),('READ_WINDOW',2,17),('READ_CLOSED',3,0)]:
            row=self.phase(phase,sequence);row['readsPerformed']=read
            with self.assertRaises(ValueError):m.phase_response(row,phase,sequence,'a'*64,row['binding'])
        row=self.phase(rows=[self.row()]);row['rows'][0]['outputOrdinals']=['1','1']
        with self.assertRaises(ValueError):m.phase_response(row,'READ_WINDOW',2,'a'*64,row['binding'])
    def test_done_row_requires_real_metadata_join_not_ack(self):
        phase=self.phase(rows=[self.row()]);self.assertEqual(m.match_mapped(phase,{'title':'Actual owned window','class':'owned.app'})['handleOrdinal'],'1')
        for window in [{'title':'other','class':'owned.app'},{'title':'Actual owned window','class':'other'},{}]:
            with self.assertRaises(ValueError):m.match_mapped(phase,window)
        with self.assertRaises(ValueError):m.match_mapped(self.phase(),{'title':'Actual owned window','class':'owned.app'})
    def test_retained_unknown_and_caught_action_failure_never_pass(self):
        base=self.terminal();m.terminal_response(base,'a'*64,base['binding'])
        for key,value in [('status','RetainedUnknown'),('actionPassed',False),('passed',False),('completedPhases',3),('error','actualfailure')]:
            changed=copy.deepcopy(base);changed[key]=value
            with self.assertRaises(ValueError):m.terminal_response(changed,'a'*64,base['binding'])
    def test_pipe_refuses_replay_before_any_write(self):
        proc=Mock();proc.stdout.fileno.return_value=8;proc.stdin.fileno.return_value=9
        reader=m.ObserverPipe(proc,{},'a'*64,self.phase()['binding'],io.BytesIO())
        with patch.object(m.os,'write') as write:
            with self.assertRaises(ValueError):reader.command('READ_WINDOW')
        write.assert_not_called()
    def test_pipe_keeps_actual_retained_terminal_before_rejection(self):
        value=self.terminal();value['status']='RetainedUnknown';value['passed']=False
        proc=Mock();proc.poll.return_value=None;proc.stdout.fileno.return_value=8;proc.stdin.fileno.return_value=9
        wire=io.BytesIO();reader=m.ObserverPipe(proc,{},'a'*64,value['binding'],wire);reader.sequence=3
        with patch.object(m,'left',return_value=1_000_000_000),patch.object(m.select,'select',side_effect=[([],[],[]),([8],[],[])]),patch.object(m.os,'write',return_value=7),patch.object(m.os,'read',return_value=(json.dumps(value)+'\n').encode()):
            with self.assertRaises(ValueError):reader.command('RETIRE')
        self.assertEqual(reader.last_response,value);self.assertEqual(json.loads(wire.getvalue()),value)
        self.assertIsNone(proc.stdin)
    def test_observer_and_producer_flags_are_not_cpu_modes(self):
        source=Path(m.__file__).read_text();tree=ast.parse(source)
        execute=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
        literals={n.value for n in ast.walk(execute) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
        self.assertIn('--foreign-endpoint-observe-only',literals);self.assertIn('--foreign-endpoint-window-producer',literals)
        self.assertNotIn('--allocation-only',literals);self.assertNotIn('--foreign-endpoint-refusal-only',literals)
        self.assertIn('RETIRE',literals);self.assertEqual(m.CLOSE_ARGV,['-M','alt','-k','F4','-m','alt'])
    def test_bounded_seeded_actual_metadata_refusals(self):
        for seed in range(32):
            value=(seed*1664525+1013904223)&0xffffffff
            phase=self.phase(rows=[self.row()]);window={'title':'Actual owned window','class':'owned.app'}
            if seed%8==0:self.assertEqual(m.match_mapped(phase,window)['handleOrdinal'],'1')
            else:
                window['title' if value&1 else 'class']='different-'+str(value)
                with self.assertRaises(ValueError):m.match_mapped(phase,window)
    def test_close_predicate_uses_current_dom_and_never_notification_gate(self):
        source=Path(m.__file__).read_text();tree=ast.parse(source)
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='_ObserverCloseSnapshots')
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='await_phase')
        names={n.func.id for n in ast.walk(method) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
        self.assertIn('close_ready_matches',names)
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr=='phase_witness_matches' for n in ast.walk(method)))


    def close_pair(self):
        bound={'lifetime':'1','session':'2','frontend':'3'}
        identity='applications:'+json.dumps(bound,separators=(',',':'))+':7:control:opener'
        def snap(mode):return dict(root={'mode':mode,'pub':'7','lease':'0','loading':'false'},documentFocused=False,query=None,retained=None,controls=[])
        pair={'bar':{'snapshot':snap(None)},'popup':{'snapshot':snap('closed')}}
        pair['bar']['snapshot']['controls']=[dict(id=identity,control='bar:applications',tag='BUTTON',disabled=False,ariaDisabled='false',focusOnly='false')]
        return pair,bound
    def test_close_ready_current_binding_publication_and_no_popup(self):
        pair,bound=self.close_pair();validator=Mock();fixture=Mock(validate_phase_pair=validator)
        with patch.object(m,'keyboard_fixture',fixture):self.assertTrue(m.close_ready_matches(pair,{},bound))
        validator.assert_called_once_with(pair,{})
        for mutation in ('popup','loading','view','binding','disabled','duplicate','query','lease','popupfocus'):
            changed=copy.deepcopy(pair);b=changed['bar']['snapshot'];p=changed['popup']['snapshot']
            if mutation=='popup':p['root']['mode']='applications'
            if mutation=='loading':b['root']['loading']='true'
            if mutation=='view':b['root']['pub']='8'
            if mutation=='binding':b['controls'][0]['id']='applications:detached:7:control:opener'
            if mutation=='disabled':b['controls'][0]['disabled']=True
            if mutation=='duplicate':b['controls']*=2
            if mutation=='query':p['query']={'value':'x','disabled':False}
            if mutation=='lease':b['root']['lease']='1'
            if mutation=='popupfocus':p['documentFocused']=True
            with patch.object(m,'keyboard_fixture',fixture):self.assertFalse(m.close_ready_matches(changed,{},bound))
    def test_close_ready_does_not_swallow_custody_validation_failure(self):
        pair,bound=self.close_pair();fixture=Mock();fixture.validate_phase_pair.side_effect=ValueError('wrong live owner/request')
        with patch.object(m,'keyboard_fixture',fixture):self.assertFalse(m.close_ready_matches(pair,{},bound))

if __name__=='__main__':unittest.main(argv=[sys.argv[0],*rest])

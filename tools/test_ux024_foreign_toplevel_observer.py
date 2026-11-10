#!/usr/bin/env python3
"""Fixed pure/mocked connected-runner contracts; no target import or native effect."""
import argparse,ast,copy,importlib.util,io,json,signal,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import Mock,patch
p=argparse.ArgumentParser();p.add_argument('--module',required=True);p.add_argument('--phase-fixture',type=Path);p.add_argument('--capture-failure',type=Path);args,rest=p.parse_known_args()
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
        host='applications:'+json.dumps(bound,separators=(',',':'))+':7:'
        for control,suffix in [('bar:overview','control:overview-opener'),('bar:switcher','control:switcher-opener'),('bar:notifications','notifications:opener'),('bar:files','files:opener'),('bar:system','system:opener'),('bar:settings','settings:opener')]:
            pair['bar']['snapshot']['controls'].append(dict(id=host+suffix,control=control,tag='BUTTON',disabled=True,ariaDisabled='true',focusOnly='false'))
        return pair,bound
    def test_close_ready_current_binding_publication_and_no_popup(self):
        pair,bound=self.close_pair();validator=Mock();fixture=Mock(validate_phase_pair=validator)
        with patch.object(m,'keyboard_fixture',fixture):self.assertTrue(m.close_ready_matches(pair,{'expectedLease':0},bound))
        validator.assert_called_once_with(pair,{'expectedLease':0})
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
            with patch.object(m,'keyboard_fixture',fixture):self.assertFalse(m.close_ready_matches(changed,{'expectedLease':0},bound))
    def test_close_ready_does_not_swallow_custody_validation_failure(self):
        pair,bound=self.close_pair();fixture=Mock();fixture.validate_phase_pair.side_effect=ValueError('wrong live owner/request')
        with patch.object(m,'keyboard_fixture',fixture):self.assertFalse(m.close_ready_matches(pair,{'expectedLease':0},bound))


    def test_actual_core_relative_prerequisite_representation(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();path=root/'proof.json';path.write_text('{}')
            absolute={'path':str(path),'sha256':'a'*64}
            with patch.object(m,'ROOT',root):
                normalized=m.canonical_prerequisite(absolute)
                self.assertEqual(normalized,{'path':'proof.json','sha256':'a'*64})
                self.assertIn(normalized,[{'path':'proof.json','sha256':'a'*64}])
                self.assertNotIn(dict(normalized,sha256='b'*64),[normalized])
                for ref in [dict(absolute,path='/etc/passwd'),dict(absolute,path=str(root/'child/../proof.json')),dict(absolute,path='proof.json')]:
                    with self.assertRaises(ValueError):m.canonical_prerequisite(ref)
                alias=root/'alias.json';alias.symlink_to(path)
                with self.assertRaises(ValueError):m.canonical_prerequisite(dict(absolute,path=str(alias)))


    def retained_phase_fixture(self):
        self.assertIsNotNone(args.phase_fixture,'Explicit frozen actual phase fixture required')
        raw=args.phase_fixture.read_bytes()
        self.assertEqual(m.digest(raw),'c96757e47a8851ecb50b1bd526fcd8fbcef9cdd6a25a54accec68a6a87ea2d8a')
        fixture=json.loads(raw)
        self.assertEqual(len(fixture['phaseObservations']),16)
        spec=importlib.util.spec_from_file_location('exact_retained_phase_validator',m.ROOT/'tools/ux023_notifications_keyboard_fixture.py')
        phase=importlib.util.module_from_spec(spec);spec.loader.exec_module(phase)
        return fixture,phase
    def test_retained_actual_16_pairs_publication5_presentation4(self):
        fixture,phase=self.retained_phase_fixture()
        with patch.object(m,'keyboard_fixture',phase):
            for row in fixture['phaseObservations']:
                with self.subTest(sequence=row['binding']['seq']):
                    self.assertEqual(row['responses']['bar']['snapshot']['root']['pub'],'5')
                    self.assertTrue(m.close_ready_matches(row['responses'],row['binding'],fixture['runtimeBinding']))
    def test_retained_stale_opener_or_utility_counter_refused(self):
        fixture,phase=self.retained_phase_fixture();row=fixture['phaseObservations'][0]
        with patch.object(m,'keyboard_fixture',phase):
            for index in range(7):
                pair=copy.deepcopy(row['responses']);control=pair['bar']['snapshot']['controls'][index]
                control['id']=control['id'].replace('}:4:','}:3:')
                with self.subTest(control=index):self.assertFalse(m.close_ready_matches(pair,row['binding'],fixture['runtimeBinding']))
    def test_retained_wrong_binding_or_noncanonical_counter_refused(self):
        fixture,phase=self.retained_phase_fixture();row=fixture['phaseObservations'][0]
        with patch.object(m,'keyboard_fixture',phase):
            for value in ['0','04','-1','+4','٤',str(2**64)]:
                pair=copy.deepcopy(row['responses']);pair['bar']['snapshot']['controls'][0]['id']=pair['bar']['snapshot']['controls'][0]['id'].replace('}:4:', '}:'+value+':')
                with self.subTest(counter=value):self.assertFalse(m.close_ready_matches(pair,row['binding'],fixture['runtimeBinding']))
            wrong=dict(fixture['runtimeBinding'],frontend='1')
            self.assertFalse(m.close_ready_matches(row['responses'],row['binding'],wrong))
            wrong=dict(fixture['runtimeBinding'],frontend=True)
            self.assertFalse(m.close_ready_matches(row['responses'],row['binding'],wrong))
    def test_retained_freshness_identity_lease_and_replay_refusals(self):
        fixture,phase=self.retained_phase_fixture();row=fixture['phaseObservations'][0]
        with patch.object(m,'keyboard_fixture',phase):
            for mutation in ['nonce','owner','request','publication','lease','expectedLease','replay','closed','popupFocus']:
                pair=copy.deepcopy(row['responses']);binding=copy.deepcopy(row['binding'])
                if mutation=='nonce':pair['bar']['nonce']='0'*64
                if mutation=='owner':pair['bar']['ownerPid']='2'
                if mutation=='request':pair['bar']['request']['inode']='999'
                if mutation=='publication':binding['minimumPublication']={'bar':6,'popup':6}
                if mutation=='lease':pair['bar']['snapshot']['root']['lease']='1'
                if mutation=='expectedLease':binding['expectedLease']=1
                if mutation=='replay':binding=fixture['phaseObservations'][1]['binding']
                if mutation=='closed':pair['popup']['snapshot']['root']['mode']='applications'
                if mutation=='popupFocus':pair['popup']['snapshot']['documentFocused']=True
                with self.subTest(mutation=mutation):self.assertFalse(m.close_ready_matches(pair,binding,fixture['runtimeBinding']))
    def test_retained_missing_duplicate_or_malformed_current_witness(self):
        fixture,phase=self.retained_phase_fixture();row=fixture['phaseObservations'][0]
        with patch.object(m,'keyboard_fixture',phase):
            for mutation in ['missing','duplicate','tag','suffix','focusOnly']:
                pair=copy.deepcopy(row['responses']);controls=pair['bar']['snapshot']['controls']
                if mutation=='missing':controls.pop()
                if mutation=='duplicate':controls.append(copy.deepcopy(controls[-1]))
                if mutation=='tag':controls[-1]['tag']='INPUT'
                if mutation=='suffix':controls[-1]['id']+=':stale'
                if mutation=='focusOnly':controls[-1]['focusOnly']='true'
                with self.subTest(mutation=mutation):self.assertFalse(m.close_ready_matches(pair,row['binding'],fixture['runtimeBinding']))
    def test_retained_32_seeded_internal_counter_correspondences(self):
        fixture,phase=self.retained_phase_fixture();row=fixture['phaseObservations'][0]
        with patch.object(m,'keyboard_fixture',phase):
            for seed in range(32):
                value=(seed*1664525+1013904223)&0xffffffff;pair=copy.deepcopy(row['responses'])
                if seed%2:pair['bar']['snapshot']['controls'][1+value%6]['id']=pair['bar']['snapshot']['controls'][1+value%6]['id'].replace('}:4:', '}:3:')
                with self.subTest(seed=seed):self.assertEqual(m.close_ready_matches(pair,row['binding'],fixture['runtimeBinding']),seed%2==0)
    def test_publication_does_not_prove_independent_document_counter(self):
        fixture,phase=self.retained_phase_fixture();row=fixture['phaseObservations'][0]
        pair=copy.deepcopy(row['responses'])
        for control in pair['bar']['snapshot']['controls']:control['id']=control['id'].replace('}:4:', '}:6:')
        with patch.object(m,'keyboard_fixture',phase):self.assertTrue(m.close_ready_matches(pair,row['binding'],fixture['runtimeBinding']))
        # This epistemic limit is explicit: publication5 alone cannot disprove a
        # coherently different whole current-document presentation. Fresh live
        # owner/request/nonce/DOM custody, not arithmetic guessing, binds it.


    def capture_assets(self):
        return {name:{'path':'/fixed/'+name,'sha256':'a'*64} for name in ('grim','hyprctl','wtype','controls','keyboardSeat')}
    def capture_memfd_child(self,module_path,function_name,byte_count):
        code="""import importlib.util,os,signal,sys
spec=importlib.util.spec_from_file_location('fixed_output_profile',sys.argv[1])
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
getattr(module,sys.argv[2])()
signal.signal(signal.SIGXFSZ,signal.SIG_DFL)
fd=os.memfd_create('fixed-capture-bound-control',os.MFD_CLOEXEC)
try:
 os.ftruncate(fd,int(sys.argv[3]))
 print('bounded-memfd-control:PASS')
finally:os.close(fd)
"""
        return subprocess.run([sys.executable,'-B','-c',code,str(module_path),function_name,str(byte_count)],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5,check=False)
    def test_retained_actual_grim_sigxfsz_not_relabelled(self):
        self.assertIsNotNone(args.capture_failure,'Explicit retained capture failure required')
        raw=args.capture_failure.read_bytes()
        self.assertEqual(m.digest(raw),'026d354a31f9c88a79d59df6083c9ee6200ffbbd0a6f7320549224ae46798fbc')
        report=json.loads(raw);failed=[row for row in report['stackRetirement']['processes'] if row['role']=='command-24']
        self.assertEqual(len(failed),1);self.assertEqual(failed[0]['exit'],-signal.SIGXFSZ)
        self.assertFalse(report['passed']);self.assertEqual(report['frames'],[])
        self.assertTrue(report['phaseObservations'][0]['phaseComplete'])
        self.assertFalse(any(row['role']=='wtype' for row in report['commands']))
    def test_exact_fixed_grim_uses_finite_existing_frame_limit(self):
        assets=self.capture_assets();base=Mock();output=Path('/fixed/output')
        self.assertIs(m.command_output_bound(base,['/fixed/grim',str(output/'actual-owned-window.png')],assets,output),m.bound_capture_output)
        self.assertEqual(m.CAPTURE_FILE_LIMIT,32*1024*1024)
    def test_all_non_capture_children_keep_exact_base_guard(self):
        assets=self.capture_assets();base=Mock();base.bound_output=object()
        for role in ('hyprctl','wtype','controls','keyboardSeat'):
            with self.subTest(role=role):self.assertIs(m.command_output_bound(base,[assets[role]['path'],'fixed'],assets,Path('/fixed/output')),base.bound_output)
    def test_alternate_grim_argv_cannot_get_capture_profile(self):
        assets=self.capture_assets();base=Mock();output=Path('/fixed/output')
        for argv in [['/fixed/grim'],['/fixed/grim','/elsewhere/actual-owned-window.png'],['/fixed/grim',str(output/'different.png')],['/fixed/grim','-t','png',str(output/'actual-owned-window.png')]]:
            with self.subTest(argv=argv),self.assertRaises(ValueError):m.command_output_bound(base,argv,assets,output)
    def test_capture_setrlimit_is_exact_finite_pair(self):
        import resource
        with patch.object(resource,'setrlimit') as setter:m.bound_capture_output()
        setter.assert_called_once_with(resource.RLIMIT_FSIZE,(32*1024*1024,32*1024*1024))
    def test_os_memfd_old_bound_refuses_capture_bound_allows_and_caps(self):
        legacy=m.ROOT/'tools/run_arm_gl_foundation_renewed_20261108_0623.py'
        self.assertEqual(m.digest(legacy.read_bytes()),m.HELPERS[str(legacy.relative_to(m.ROOT))])
        old=self.capture_memfd_child(legacy,'bound_output',1280*720*4)
        self.assertEqual(old.returncode,-signal.SIGXFSZ)
        enough=self.capture_memfd_child(Path(m.__file__),'bound_capture_output',1280*720*4)
        self.assertEqual(enough.returncode,0,msg=enough.stderr.decode(errors='replace'))
        self.assertEqual(enough.stdout,b'bounded-memfd-control:PASS\n')
        too_large=self.capture_memfd_child(Path(m.__file__),'bound_capture_output',32*1024*1024+1)
        self.assertEqual(too_large.returncode,-signal.SIGXFSZ)
    def test_32_seeded_capture_paths_do_not_broaden_other_children(self):
        assets=self.capture_assets();base=Mock();base.bound_output=object();output=Path('/fixed/output')
        for seed in range(32):
            value=(seed*1664525+1013904223)&0xffffffff
            if seed%4==0:
                self.assertIs(m.command_output_bound(base,['/fixed/grim',str(output/'actual-owned-window.png')],assets,output),m.bound_capture_output)
            elif seed%4==1:
                with self.assertRaises(ValueError):m.command_output_bound(base,['/fixed/grim',str(output/(str(value)+'.png'))],assets,output)
            else:self.assertIs(m.command_output_bound(base,['/fixed/wtype','-k',str(value)],assets,output),base.bound_output)
    def test_actual_spawn_selects_profile_and_keeps_frame_cap(self):
        tree=ast.parse(Path(args.module).read_text())
        execute=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
        spawn=next(n for n in ast.walk(execute) if isinstance(n,ast.FunctionDef) and n.name=='spawn')
        popen=next(n for n in ast.walk(spawn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Popen')
        hook=next(k.value for k in popen.keywords if k.arg=='preexec_fn')
        self.assertEqual(ast.dump(hook),ast.dump(ast.parse("command_output_bound(context['base'],argv,assets,output)",mode='eval').body))
        self.assertIn("regular(frame,32*1024*1024)",Path(args.module).read_text())

if __name__=='__main__':unittest.main(argv=[sys.argv[0],*rest])

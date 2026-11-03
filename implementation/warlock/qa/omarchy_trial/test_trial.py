"""Pure and mocked controls; Root runs only under reviewed protected QA."""
import unittest
from unittest.mock import Mock, patch
import runner


class TrialControls(unittest.TestCase):
    def test_outside_scope_refuses_before_ssh(self):
        with patch.object(runner,'require_qa_scope',side_effect=RuntimeError('outside scope')), patch.object(runner,'ssh') as ssh:
            with self.assertRaisesRegex(RuntimeError,'outside scope'):runner.main([])
            ssh.assert_not_called()

    def test_service_identity_rejects_replacement_and_missing_values(self):
        expected={'InvocationID':'a'*32,'ControlGroup':'/user.slice/user-1000.slice/user@1000.service/app.slice/warlock-trial-'+'b'*32+'.service'}
        runner.require_same_service(expected,dict(expected),'warlock-trial-'+'b'*32)
        for changed in ({**expected,'InvocationID':'c'*32},{**expected,'ControlGroup':''},{}):
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                runner.require_same_service(expected,changed,'warlock-trial-'+'b'*32)

    def test_stop_refuses_replaced_service_without_invoking_stop(self):
        unit='warlock-trial-'+'b'*32
        expected={'InvocationID':'a'*32,'ControlGroup':'/user.slice/user-1000.slice/user@1000.service/app.slice/'+unit+'.service'}
        stop=Mock();show=Mock(return_value={**expected,'InvocationID':'c'*32})
        with self.assertRaises(ValueError): runner.stop_owned(unit,expected,show,stop)
        stop.assert_not_called()

    def test_stop_targets_only_bound_unique_unit(self):
        unit='warlock-trial-'+'b'*32
        expected={'InvocationID':'a'*32,'ControlGroup':'/user.slice/user-1000.slice/user@1000.service/app.slice/'+unit+'.service'}
        stop=Mock();runner.stop_owned(unit,expected,lambda _:expected,stop)
        stop.assert_called_once_with(unit)

    def test_census_birth_loss_or_missing_group_is_unknown(self):
        self.assertEqual(runner.census_status(None), 'unknown')
        self.assertEqual(runner.census_status([{'pid':1,'startTicks':None,'cgroup':'/x'}]), 'unknown')
        self.assertEqual(runner.census_status([{'pid':1,'startTicks':'5','cgroup':'/x'}]), 'observed')
        self.assertEqual(runner.retirement_state(None,None), 'unknown')

    def test_bad_input_receipt_rejected_before_guest_launch(self):
        for reason in ('unknown-abi','source-mismatch','html-mismatch','wrong-deadline','wrong-attachment'):
            with self.subTest(reason=reason), self.assertRaises(ValueError):
                runner.validate_reviewed_inputs(*runner.fixture_inputs(reason))
        runner.validate_reviewed_inputs(*runner.fixture_inputs('valid'))

    def test_missing_original_scenario_fails_before_guest_launch(self):
        packet,build,frontend,abi,scenario=runner.fixture_inputs('valid')
        scenario['slice']['scenarios']=[]
        with self.assertRaisesRegex(ValueError,'original-scenario record not bound'):
            runner.validate_reviewed_inputs(packet,build,frontend,abi,scenario)

    def test_birth_parser_handles_spaces_and_right_parentheses(self):
        raw='42 (worker ) task) S '+' '.join(str(i) for i in range(1,20))
        self.assertEqual(runner.proc_birth(raw),'19')
        with self.assertRaises(ValueError): runner.proc_birth('42 bad')

class CaptureBoundaryTests(unittest.TestCase):
    def test_main_rejects_bad_receipt_before_ssh(self):
        import json
        packet,build,frontend,abi,scenario=runner.fixture_inputs('wrong-attachment')
        raw=json.dumps(packet).encode()
        with patch.object(runner,'require_qa_scope'), patch.object(runner,'read_regular',return_value=raw), \
             patch.object(runner,'reviewed_file',side_effect=[json.dumps(x).encode() for x in (build,frontend,abi,scenario)]), \
             patch.object(runner,'ssh') as ssh:
            with self.assertRaisesRegex(ValueError,'fixed trial packet'):
                runner.main(['--packet','/unused','--sha256',runner.sha(raw),'--output','/unused'])
            ssh.assert_not_called()

    def test_pre_capture_requires_live_births_mapped_owner_and_deadline(self):
        ident={'InvocationID':'a'*32,'ControlGroup':'/user.slice/unit'}; guest='/tmp/owned'
        rows=[{'pid':1,'startTicks':'11','exe':guest+'/backend'}, {'pid':2,'startTicks':'12','exe':guest+'/owner'}, {'pid':3,'startTicks':'13','exe':guest+'/owner'}]
        ready={'invocation':ident['InvocationID'],'cgroup':ident['ControlGroup'],'mappedOwnerPids':[2], 'observedMonotonicNs':10,'deadlineMonotonicNs':20,'actors':rows}
        self.assertEqual(runner.validate_pre_capture(ready,ident,{'rows':rows},guest)[2],'12')
        for bad in ({**ready,'mappedOwnerPids':[]},{**ready,'deadlineMonotonicNs':10},{**ready,'invocation':'wrong'}):
            with self.subTest(bad=bad),self.assertRaises(RuntimeError):runner.validate_pre_capture(bad,ident,{'rows':rows},guest)
        with self.assertRaises(RuntimeError):runner.validate_pre_capture(ready,ident,{'rows':rows[:2]},guest)
        with self.assertRaises(RuntimeError):runner.validate_pre_capture(ready,ident,{'rows':None},guest)


class GuestAndQmpControls(unittest.TestCase):
    def test_guest_wrong_uid_fails_before_backend(self):
        import json,sys
        import guest_trial
        packet={'dir':'/tmp/warlock-trial-'+'b'*32,'unit':'warlock-trial-'+'b'*32}
        with patch.object(guest_trial,'read_regular',return_value=json.dumps(packet).encode()), \
             patch.object(guest_trial.os,'getuid',return_value=999), \
             patch.object(guest_trial.subprocess,'Popen') as launch, \
             patch.object(sys,'argv',['guest','/fixture']):
            with self.assertRaisesRegex(RuntimeError,'service identity'):guest_trial.main()
            launch.assert_not_called()

    def test_qmp_wrong_vm_never_sends_screendump(self):
        import json,tempfile
        from pathlib import Path
        class Stream:
            def __init__(self):self.lines=iter([b'{"QMP":{}}\n',b'{"return":{}}\n',b'{"return":{"UUID":"00000000-0000-0000-0000-000000000000"}}\n']);self.sent=[]
            def readline(self):return next(self.lines)
            def write(self,raw):self.sent.append(json.loads(raw))
        class Sock:
            def __init__(self,stream):self.stream=stream
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def settimeout(self,*args):pass
            def connect(self,*args):pass
            def makefile(self,*args,**kwargs):return self.stream
        stream=Stream()
        with tempfile.TemporaryDirectory() as tmp,patch.object(runner.socket,'socket',return_value=Sock(stream)):
            with self.assertRaisesRegex(RuntimeError,'VM identity'):runner.qmp_screenshot(Path(tmp)/'frame.png','12345678-1234-1234-1234-123456789abc')
        self.assertNotIn('screendump',[x['execute'] for x in stream.sent])


class CleanupAndCompletionTests(unittest.TestCase):
    def test_uncertain_launch_identity_absent_is_not_invented(self):
        unit='warlock-trial-'+'b'*32
        with self.assertRaises(ValueError):runner.recover_service_identity(unit,None,True,lambda _:{'InvocationID':'','ControlGroup':''})
        show=Mock()
        self.assertIsNone(runner.recover_service_identity(unit,None,False,show))
        show.assert_not_called()

    def test_completion_requires_original_birth_and_deadline(self):
        ready={'deadlineMonotonicNs':100,'mappedOwnerPids':[2]};births={2:'12'}
        runner.validate_post_capture(ready,births,{'rows':[{'pid':2,'startTicks':'12'}]},99)
        for after,clock in (({'rows':None},99),({'rows':[{'pid':2,'startTicks':'13'}]},99),({'rows':[{'pid':2,'startTicks':'12'}]},100)):
            with self.subTest(after=after,clock=clock),self.assertRaises(RuntimeError):runner.validate_post_capture(ready,births,after,clock)


class GuestLoaderControls(unittest.TestCase):
    def test_scrub_all_loader_variables_preserves_guest_scope(self):
        import guest_trial
        source={'LD_PRELOAD':'bad','LD_LIBRARY_PATH':'bad','LD_AUDIT':'bad','LD_FUTURE':'bad','GLIBC_TUNABLES':'bad','INVOCATION_ID':'bound','OTHER':'kept'}
        env=guest_trial.production_environment(source)
        self.assertFalse(any(k.startswith('LD_') or k=='GLIBC_TUNABLES' for k in env))
        self.assertEqual(env['INVOCATION_ID'],'bound')
        self.assertEqual(env['OMARCHY_PATH'],'/usr/share/omarchy')
        self.assertEqual(env['WAYLAND_DISPLAY'],'wayland-1')
        self.assertEqual(env['OTHER'],'kept')

    def test_active_or_unreadable_preload_refuses_before_backend(self):
        import guest_trial
        for body in (b'/tmp/inject.so\n',b'# safe comment\n /tmp/inject.so\n'):
            with self.subTest(body=body),patch.object(guest_trial,'read_regular',return_value=body),patch.object(guest_trial.subprocess,'Popen') as launch:
                with self.assertRaisesRegex(RuntimeError,'preload'):guest_trial.launch_backend(['/fixture'],{},None,None)
                launch.assert_not_called()
        with patch.object(guest_trial,'read_regular',side_effect=PermissionError('denied')),patch.object(guest_trial.subprocess,'Popen') as launch:
            with self.assertRaisesRegex(RuntimeError,'preload'):guest_trial.launch_backend(['/fixture'],{},None,None)
            launch.assert_not_called()

    def test_absent_or_comments_preload_allowed_but_dirty_env_rejected(self):
        import guest_trial
        with patch.object(guest_trial,'read_regular',return_value=b'  # comment\n\n'),patch.object(guest_trial.subprocess,'Popen') as launch:
            guest_trial.launch_backend(['/fixture'],{},None,None)
            launch.assert_called_once()
            launch.reset_mock()
            with self.assertRaisesRegex(RuntimeError,'not scrubbed'):guest_trial.launch_backend(['/fixture'],{'LD_PRELOAD':'x'},None,None)
            launch.assert_not_called()
        with patch.object(guest_trial,'read_regular',side_effect=FileNotFoundError()):
            self.assertEqual(guest_trial.require_safe_preload(),'absent')


class RetainedServiceControls(unittest.TestCase):
    def setUp(self):
        self.unit='warlock-trial-'+'b'*32
        self.identity={'InvocationID':'a'*32,'ControlGroup':'/user.slice/u/'+self.unit+'.service'}
        self.status={**self.identity,'ActiveState':'active','SubState':'exited','MainPID':'0',
                     'Result':'success','ExecMainCode':'1','ExecMainStatus':'0'}

    def test_matching_active_exited_and_failed_snapshots(self):
        for status in (self.status,{**self.status,'ActiveState':'failed','SubState':'failed','Result':'exit-code','ExecMainStatus':'1','ControlGroup':''}):
            with self.subTest(status=status):
                self.assertEqual(runner.matching_terminal(self.unit,self.identity,status),status)

    def test_reject_foreign_invocation_changed_group_and_live_main(self):
        for status in ({**self.status,'InvocationID':'c'*32},{**self.status,'ControlGroup':'/user.slice/other'},
                       {**self.status,'SubState':'running','MainPID':'50'},
                       {**self.status,'MainPID':'50'},{**self.status,'ExecMainStatus':''}):
            with self.subTest(status=status):
                self.assertIsNone(runner.matching_terminal(self.unit,self.identity,status))

    def test_missing_group_terminal_does_not_authorize_stop(self):
        result={'scopeRetirement':'unknown','retiredBirths':'unknown'}
        missing={**self.status,'ControlGroup':''}; stop=Mock(); observe=Mock()
        with self.assertRaises(ValueError):
            runner.cleanup_owned_service(result,self.unit,self.identity,lambda _:missing,lambda _:missing,stop,observe)
        stop.assert_not_called();observe.assert_not_called()
        self.assertEqual(result['terminalService'],missing)
        self.assertEqual(result['scopeRetirement'],'unknown')

    def test_live_or_retained_same_group_stops_only_exact_unit(self):
        for status in (self.status,{**self.status,'SubState':'running','MainPID':'50'}):
            result={'scopeRetirement':'unknown','retiredBirths':'unknown'};stop=Mock()
            observe=Mock(side_effect=[{'rows':[{'pid':50}],'populated':'1'}, {'rows':None,'populated':None}])
            runner.cleanup_owned_service(result,self.unit,self.identity,lambda _:status,lambda _:self.identity,stop,observe)
            stop.assert_called_once_with(self.unit)
            self.assertTrue(result['stopRequested'])
            self.assertEqual(result['scopeRetirement'],'unknown')

    def test_replaced_between_status_and_stop_never_signalled(self):
        result={'scopeRetirement':'unknown','retiredBirths':'unknown'};stop=Mock()
        changed={**self.identity,'InvocationID':'c'*32}
        with self.assertRaises(ValueError):
            runner.cleanup_owned_service(result,self.unit,self.identity,lambda _:self.status,lambda _:changed,stop,lambda _:{'rows':[],'populated':'0'})
        stop.assert_not_called()

    def test_invocation_journal_filters_all_supported_invocation_fields(self):
        expected=Mock(stdout=b'{}\n')
        with patch.object(runner,'ssh',return_value=expected) as ssh:
            runner.invocation_journal(self.unit,self.identity)
        cmd=ssh.call_args.args[0]
        self.assertIn('--invocation='+self.identity['InvocationID'],cmd)
        self.assertIn('--user-unit=',cmd)




class DesktopPreservationTests(unittest.TestCase):
    def snapshot(self):
        return {'valid':True,'boot':'boot-1','session':{'instance':'i','pid':10,'birth':'99'},'startMonotonicNs':1,'endMonotonicNs':2,'foot':[{'address':'0xab','pid':5,'birth':'42'}],'idle':{'enabled':True,'stayAwake':False,'locked':False}}

    def test_same_facts_and_absent_baseline(self):
        a=self.snapshot();b=self.snapshot();b.update(startMonotonicNs=3,endMonotonicNs=4)
        self.assertEqual(runner.compare_preservation(a,b),{'foot':'preserved','idle':'preserved'})
        a['foot']=[]
        self.assertEqual(runner.compare_preservation(a,b)['foot'],'not-present-at-baseline')

    def test_changes_and_missing_never_preserved(self):
        from copy import deepcopy
        a=self.snapshot();b=deepcopy(a);b.update(startMonotonicNs=3,endMonotonicNs=4)
        b['foot'][0]['birth']='43';b['idle']['stayAwake']=True
        self.assertEqual(runner.compare_preservation(a,b),{'foot':'changed','idle':'changed'})
        for bad in ({},dict(b,boot='other'),dict(b,session=None),dict(b,valid=False),dict(b,startMonotonicNs=1),dict(b,idle={'enabled':True})):
            with self.subTest(bad=bad):self.assertEqual(runner.compare_preservation(a,bad),{'foot':'unknown','idle':'unknown'})

    def test_failed_capture_is_unknown(self):
        with patch.object(runner,'ssh',side_effect=OSError('offline')):
            snap=runner.preservation_snapshot(None,'before')
        self.assertFalse(snap['valid'])
        self.assertEqual(runner.compare_preservation(snap,self.snapshot()),{'foot':'unknown','idle':'unknown'})

    def test_duplicate_addresses_and_inverted_snapshot_bounds_are_unknown(self):
        from copy import deepcopy
        a=self.snapshot();b=deepcopy(a);b.update(startMonotonicNs=3,endMonotonicNs=4)
        for side in ('before','after'):
            x,y=deepcopy(a),deepcopy(b)
            (x if side=='before' else y)['foot'].append(dict(a['foot'][0]))
            self.assertEqual(runner.compare_preservation(x,y),{'foot':'unknown','idle':'unknown'})
        for x,y in ((dict(a,startMonotonicNs=3),b),(a,dict(b,endMonotonicNs=2)),(dict(a,startMonotonicNs=None),b)):
            self.assertEqual(runner.compare_preservation(x,y),{'foot':'unknown','idle':'unknown'})

    def test_early_launch_failure_attempts_final_snapshot_and_never_stops(self):
        import json,tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temp:
            repo=Path(temp); (repo/'implementation/warlock/haskell').mkdir(parents=True)
            (repo/'implementation/warlock/src').mkdir(parents=True)
            (repo/'implementation/warlock/elm.json').write_bytes(b'elm')
            build_report=repo/'build/report.json'; build_report.parent.mkdir()
            production=build_report.parent/'haskell-build/dist-production';production.mkdir(parents=True)
            for name in ('warlock-ui-owner','warlock-ui-backend'):(production/name).write_bytes(b'fixture')
            front_report=repo/'front/report.json';front_report.parent.mkdir();(front_report.parent/'observer.json').write_bytes(b'observer')
            packet,build,front,abi,scenario=runner.fixture_inputs('valid')
            scenario_path=repo/'scenario.json'; scenario_ref={'path':str(scenario_path),'sha256':'a'*64}
            packet.update(scenarioRecord=scenario_ref,participantIndex={'path':str(repo/'.warlock-contributor/participant-index.json'),'sha256':'b'*64},requirements={'path':str(repo/'docs/elm-roadmap/requirements.json'),'sha256':'c'*64})
            packet['assets']['owner']['path']=str(production/'warlock-ui-owner')
            packet['assets']['backend']['path']=str(production/'warlock-ui-backend')
            packet['assets']['helper']['path']=str(repo/'tools/omarchy_ui_mvp.py')
            front.update(sources={},report={'path':str(front_report),'sha256':'d'*64})
            build['build']['sourceHashes']={}
            ident={'owner':None,'baseline':None,'startedUTC':None,'requirements':scenario['slice']['requirements'],'scenarios':scenario['slice']['scenarios']}
            canonical=lambda x: json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
            idx={'schema':1,'records':{'scenario.json':{'recordSha256':scenario_ref['sha256'],'identitySha256':runner.sha(canonical(ident))}}}
            idx['indexSha256']=runner.sha(canonical(idx))
            requirements={'requirements':[{'id':packet['requirement'],'scenarios':[{'name':packet['scenario']}]}]}
            front_result={'passed':True,'subscriptions':{'passed':True,'requirement':'ELM-TEA-004','scenario':'tea-subscriptions','marker':'TEA_SUBSCRIPTIONS_OBSERVE_V1'},'httpRootObserver':{'result':{'ok':True},'resultPath':'observer.json','resultSHA256':runner.sha(b'observer')},'compiledSubscriptionRoots':[None]*8,'httpDocuments':{n:{'sha256':front['documents'][n]} for n in ('controller','bar','popup')},'sources':{'implementation/warlock/elm.json':runner.sha(b'elm')}}
            provenance={'schema':1,'independent':True,'disposition':'accepted','buildReportSHA256':packet['buildReport']['sha256'],'ownerSHA256':packet['assets']['owner']['sha256'],'backendSHA256':packet['assets']['backend']['sha256'],'ownerPath':packet['assets']['owner']['path'],'backendPath':packet['assets']['backend']['path'],'sourceHashesVerified':True,'reviewer':'test'}
            values=[build,front,abi,scenario,idx,requirements]+[{} for _ in packet['assets']]+[front_result,provenance]
            expected_reads=[json.dumps(v).encode() for v in values]
            packet_path=repo/'packet.json';raw=json.dumps(packet).encode();packet_path.write_bytes(raw)
            out=repo/'out'; before=self.snapshot()
            snapshots=Mock(side_effect=[before,{'valid':False,'error':'post unavailable'}])
            with patch.object(runner,'REPO',repo),patch.object(runner,'BUILD_REPORT',build_report),patch.object(runner,'FRONTEND_REPORT',front_report),patch.object(runner,'FRONTEND_REPORT_SHA','d'*64),patch.object(runner,'require_qa_scope'),patch.object(runner,'validate_reviewed_inputs'),patch.object(runner,'reviewed_file',side_effect=expected_reads),patch.object(runner,'preservation_snapshot',snapshots),patch.object(runner,'ssh',side_effect=RuntimeError('early preflight failure')),patch.object(runner,'stop_service') as stop:
                self.assertEqual(runner.main(['--packet',str(packet_path),'--sha256',runner.sha(raw),'--output',str(out)]),1)
            result=json.loads((out/'observation.json').read_text())
            self.assertEqual([c.args[1] for c in snapshots.call_args_list],['before','after'])
            self.assertEqual(result['error'],'early preflight failure')
            self.assertEqual(result['desktopPreservation'],{'foot':'unknown','idle':'unknown'})
            self.assertEqual(result['scopeRetirement'],'unknown')
            stop.assert_not_called()

if __name__ == '__main__': unittest.main()

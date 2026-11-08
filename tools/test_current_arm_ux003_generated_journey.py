"""Pure and mocked source-first contracts. No native/input/compiler execution."""
import argparse
import ast
import copy
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock,patch
import test_ux003_attempt_authorization as auth_contracts
AuthorizationControls = auth_contracts.AttemptAuthorizationControls


class Contracts(unittest.TestCase):
    def test_retired_foundation_report_is_not_live_context(self):
        for value in (None,{},dict(passed=True,hostObserved=True,nestedObserved=True,cleanup=True)):
            with self.assertRaises(ValueError):j.require_live_stack(value,100)

    def test_staging_deadline_exact_original_28(self):
        self.assertEqual(j.staging_clock({'generatedMonotonicNs':'10','deadlineMonotonicNs':'28000000010'},'boot')['deadline'],28000000010)
        with self.assertRaises(ValueError):j.staging_clock({'generatedMonotonicNs':'10','deadlineMonotonicNs':'30000000010'},'boot')

    def test_effect_expiry_and_monotonic_regression_refuse(self):
        for now in (9,100):
            with self.assertRaises((ValueError,TimeoutError)):j.remaining({'last':10,'deadline':100,'boot':'boot'},now,'boot')
        with self.assertRaises(ValueError):j.remaining({'last':10,'deadline':100,'boot':'boot'},11,'wrong')

    def test_missing_or_stale_ack_never_retry(self):
        for response in ((0,b''),(0,b'ready 2\n'),(1,b'ready 1\n')):
            used=set();emit=Mock(return_value=response)
            with self.assertRaises(ValueError):j.perform_pointer_step('open',(10,20),(1280,800),used,emit)
            with self.assertRaises(ValueError):j.perform_pointer_step('open',(10,20),(1280,800),used,emit)
            self.assertEqual(emit.call_count,1)

    def test_exact_two_pointer_roundtrips_and_payloads(self):
        for step,n in [('open',1),('visible',2)]:
            emit=Mock(return_value=(0,('ready %s\n'%n).encode()))
            j.perform_pointer_step(step,(10,20),(1280,800),set(),emit)
            emit.assert_called_once_with(('move 10 20\nbutton 272 1\nbutton 272 0\nsync %s\n'%n).encode())

    def test_literal_unicode_empty_and_space_argv(self):
        self.assertTrue(j.argv_matches(b'["two words","","caf\\233"]\n',b''))
        self.assertFalse(j.argv_matches(b'["two","words","caf\\233"]\n',b''))
        self.assertFalse(j.argv_matches(b'["two words","caf\\233"]\n',b''))

    def test_empty_namespace_census_never_terminal_cleanup(self):
        row={'owner':{'engineObservation':{'backing':{'retired':True}}},'retainedChildNamespaceDiagnostic':{'count':0}}
        self.assertFalse(j.parent_observation(row));self.assertFalse(j.observation_checks(row)['journeyFactsObserved'])

    def test_original_typed_parent_fields_cannot_be_bool_claims(self):
        self.assertFalse(j.parent_observation({'owner':{'cleanup':True,'engineCleanup':True,'passed':True}}))

    def test_packet_unknown_or_missing_live_foundation_refuses(self):
        for packet in ({},dict(schema=1,kind='fixed-ux003-native-journey',armed=True)):
            with self.assertRaises(ValueError):j.packet_shape(packet)

    def test_only_two_exact_noncompiled_build_tool_changes_allowed(self):
        old={'implementation/example.hs':'a'*64}
        current=dict(old)
        self.assertEqual(j.build_deltas(old,current),{})
        with self.assertRaises(ValueError):j.build_deltas(old,dict(current,**{'implementation/example.hs':'b'*64}))
        with self.assertRaises(ValueError):j.build_deltas({'tools/other.py':'a'*64},{'tools/other.py':'b'*64})

    def test_new_runner_never_attaches_historical_aq015_descriptor(self):
        source=Path(j.__file__).read_text()
        self.assertNotIn('from qa_nested_target import attach',source)
        self.assertNotIn('libaquamarine.so.0.15.0',source)
        self.assertNotIn("os.environ['QA_NESTED_DESCRIPTOR']",source)

    def test_host_and_nested_same_original_deadline(self):
        self.assertEqual((j.JOURNEY_NS,j.CLEANUP_NS),(28_000_000_000,2_000_000_000))
        self.assertNotIn('EXPIRY_NS',vars(j))
        fixture=AuthorizationControls(methodName='test_current_canonical_authorization_resolves');fixture.setUp();self.addCleanup(fixture.doCleanups)
        authority=fixture.resolve();issued=fixture.clock(authority)
        self.assertEqual(issued['deadline']-issued['origin'],j.JOURNEY_NS)

    def test_final_packet_failure_clears_any_prior_success(self):
        receipt={'passed':True,'checks':dict(actualBackingAbsent=True,actualEnginePidAbsent=True,journeyFactsObserved=True,actualRunBound=True)}
        with patch.object(j,'verify_packet',side_effect=ValueError('late source drift')),patch.object(j,'left'):
            with self.assertRaises(ValueError):j.finalize_journey_checks({}, {}, receipt)
        self.assertFalse(receipt['passed'])

    def test_late_original_deadline_failure_cannot_publish_success(self):
        receipt={'passed':True,'checks':dict(actualBackingAbsent=True,actualEnginePidAbsent=True,journeyFactsObserved=True,actualRunBound=True)}
        with patch.object(j,'verify_packet'),patch.object(j,'left',side_effect=TimeoutError('original D exhausted')):
            with self.assertRaises(TimeoutError):j.finalize_journey_checks({}, {}, receipt)
        self.assertFalse(receipt['passed'])

    def test_final_cleanup_ceiling_never_renews_original_budget(self):
        fixture=AuthorizationControls(methodName='test_current_canonical_authorization_resolves');fixture.setUp();self.addCleanup(fixture.doCleanups)
        authority=fixture.resolve();clock=fixture.clock(authority);deadline=clock['deadline'];horizon=authority.expires_ns
        with patch.object(j.time,'time_ns',return_value=horizon-1):
            with patch.object(j.time,'monotonic_ns',return_value=deadline+j.CLEANUP_NS):self.assertTrue(j.cleanup_in_budget(clock))
            with patch.object(j.time,'monotonic_ns',return_value=deadline+1+j.CLEANUP_NS):self.assertFalse(j.cleanup_in_budget(clock))
        with patch.object(j.time,'time_ns',return_value=horizon):self.assertFalse(j.cleanup_in_budget(clock))

    def test_actual_same_window_rejects_exec_with_same_pid_and_birth(self):
        tree=ast.parse(Path(j.__file__).read_text())
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        node=next(n for n in ast.walk(main) if isinstance(n,ast.FunctionDef) and n.name=='same_window')
        window={'pid':71,'address':'0xabc','at':[150,60],'size':[980,680]}
        command=Mock(return_value=j.json.dumps(window));fakepath=Mock();fakepath.resolve.return_value='/pinned-image'
        env=dict(current=Mock(),birth=lambda _: (12,1),window=window,window_birth=12,
                 descendant=lambda *_:True,backend=Mock(pid=70),backend_birth=11,
                 digest=lambda _:'different-executed-image',regular=Mock(return_value=b'changed'),
                 Path=Mock(return_value=fakepath),assets={'owner':{'sha256':'pinned-owner'}},
                 left=Mock(),clock={'deadline':100},clients=Mock(return_value=[window]),command=command,
                 instance={'signature':'same-owned'},json=j.json)
        exec(compile(ast.Module(body=[node],type_ignores=[]),j.__file__,'exec'),env)
        with self.assertRaises(ValueError):env['same_window']()
        command.assert_not_called()

    def test_current_alive_lease_guard_in_actual_input_caller(self):
        tree=ast.parse(Path(j.__file__).read_text())
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        current=next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name=='current')
        self.assertTrue(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require_live_stack' for n in ast.walk(current)))

    def test_generated_mapping_dispatch_is_two_owned_roles_only(self):
        stack=object.__new__(j._OwnedStack);stack.p={'host':{'labwc':'/labwc','wlroots':'/wlroots'},'hostInputs':{'/labwc':'hostpin'},'nested':{'compositor':'/hypr','backend':'/aq','inputs':{'/hypr':'nestedpin'}}}
        stack.c=Mock();stack.c.FONT_SHA='fontpin';stack.c.generated_context_mapped.side_effect=[{'role':'host'},{'role':'nested'}]
        stack.base=Mock();stack.clock={'deadline':28};stack.output=Path('/private');stack.host=Mock();stack.host_birth=11;stack.nested=Mock();stack.nested_birth=12
        stack.font_layout={'copies':{'/private/nested-fonts/qualified.ttf':'copyfontpin'}}
        stack.nested_inventory=dict(stack.p['nested']['inputs'],**stack.font_layout['copies'])
        self.assertEqual(stack.map_generated_role('host'),{'role':'host'});self.assertEqual(stack.map_generated_role('nested'),{'role':'nested'})
        a,b=stack.c.generated_context_mapped.call_args_list
        self.assertIs(a.args[1],stack.host);self.assertEqual(a.args[2:5],(11,'host','hostpin'))
        self.assertIs(b.args[1],stack.nested);self.assertEqual(b.args[2:5],(12,'nested','nestedpin'))
        self.assertIs(b.args[5],stack.nested_inventory)
        self.assertEqual(b.args[5],{'/hypr':'nestedpin','/private/nested-fonts/qualified.ttf':'copyfontpin'})
        self.assertIs(a.args[-2],stack.clock);self.assertIs(b.args[-1],stack.p)
        stack.c.generated_context_mapped.reset_mock()
        for role in ['owner','observer','engine','recorder','foreign']:
            with self.assertRaises(ValueError):stack.map_generated_role(role)
        stack.c.generated_context_mapped.assert_not_called()

    def test_generated_foundation_basis_binds_current_helper_and_two_images(self):
        f={'sourceInputs':{str(j.ROOT/j.GENERATED_HELPER):j.HELPERS[j.GENERATED_HELPER],str(j.ROOT/'tools/run_arm_gl_foundation_renewed_20261107.py'):j.HELPERS['tools/run_arm_gl_foundation_renewed_20261107.py']},'host':{'labwc':'/labwc'},'hostInputs':{'/labwc':j.GENERATED_IMAGES['host']},'nested':{'compositor':'/hypr','inputs':{'/hypr':j.GENERATED_IMAGES['nested']}}}
        report={key+'GeneratedRuntime':{'role':key,'identity':{'image':pin},'creatorAttested':False,'generatedObject':None} for key,pin in j.GENERATED_IMAGES.items()}
        j.validate_generated_foundation_basis(f,report)
        for changed in [dict(report,hostGeneratedRuntime={}),dict(report,nestedGeneratedRuntime=report['hostGeneratedRuntime'])]:
            with self.assertRaises(ValueError):j.validate_generated_foundation_basis(f,changed)
        f['sourceInputs'][str(j.ROOT/j.GENERATED_HELPER)]='0'*64
        with self.assertRaises(ValueError):j.validate_generated_foundation_basis(f,report)

    def test_mutable_kernel_pair_does_not_require_creator_attestation(self):
        f={'sourceInputs':{str(j.ROOT/j.GENERATED_HELPER):j.HELPERS[j.GENERATED_HELPER],str(j.ROOT/'tools/run_arm_gl_foundation_renewed_20261107.py'):j.HELPERS['tools/run_arm_gl_foundation_renewed_20261107.py']},'host':{'labwc':'/labwc'},'hostInputs':{'/labwc':j.GENERATED_IMAGES['host']},'nested':{'compositor':'/hypr','inputs':{'/hypr':j.GENERATED_IMAGES['nested']}}}
        report={key+'GeneratedRuntime':{'role':key,'identity':{'image':pin},'creatorAttested':False,'generatedObject':{'mutableExecutableBacking':True,'creatorAttested':False}} for key,pin in j.GENERATED_IMAGES.items()}
        j.validate_generated_foundation_basis(f,report)
        report['hostGeneratedRuntime']['generatedObject']['creatorAttested']=True
        with self.assertRaises(ValueError):j.validate_generated_foundation_basis(f,report)

    def test_actual_stack_uses_generated_roles_and_exact_lua_helper(self):
        tree=ast.parse(Path(j.__file__).read_text());stack=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='_OwnedStack');start=next(n for n in stack.body if isinstance(n,ast.FunctionDef) and n.name=='start')
        calls=[n for n in ast.walk(start) if isinstance(n,ast.Call)]
        roles=[n.args[0].value for n in calls if isinstance(n.func,ast.Attribute) and n.func.attr=='map_generated_role']
        self.assertEqual(roles,['host','nested'])
        self.assertFalse(any(isinstance(n.func,ast.Attribute) and n.func.attr=='mapped' for n in calls))
        self.assertTrue(any(isinstance(n.func,ast.Attribute) and n.func.attr=='write_nested_config' for n in calls))
        self.assertTrue(any(isinstance(n.func,ast.Attribute) and n.func.attr=='nested_argv' for n in calls))


    def _document_compatibility_fixture(self):
        import copy
        stage='tools/arm64_native_stage.py';elm='implementation/warlock/src/HttpMain.elm';rec='implementation/warlock/haskell/runtime/fixture-application-argv/Main.hs'
        old={stage:'3f6a94cc541a3105b70e9b3c7ffc24b7e46282ad48572af7f095449fa1119f35',elm:'a'*64,rec:'b'*64}
        now=dict(old);now[stage]='d0686ec4859ed1eb97760397ea42ed37d21e11e58b08fb7e3fb968c6f2795aec'
        images={k:{'path':'/selected/'+k,'sha256':'c'*64,'device':'1','inode':'2','size':'3'} for k in ['controller','bar','popup','recorder']}
        assets={k:{'path':v['path'],'sha256':v['sha256']} for k,v in images.items()}
        report={'sourceHashes':old,'uiDocuments':{k:v for k,v in images.items() if k!='recorder'},'executables':{'application-argv-fixture':images['recorder']}}
        packet={'sourceHashes':now,'documentBuildReport':{'path':'/document-report','sha256':'d'*64},'assets':assets}
        proof={'schema':1,'disposition':'accepted','scope':'ux003-selected-document-build-source-correspondence','documentBuildReport':packet['documentBuildReport'],'compiledSelectedSourceHashes':old,'currentSelectedSourceHashes':now,'qaToolDeltas':[{'path':stage,'compiledSha256':old[stage],'currentSha256':now[stage]}],'selectedBuiltImages':images,'selectedAssets':assets,'independentDiffProof':{'path':'/independent-diff-proof','sha256':'e'*64}}
        return packet,report,{'documentBuildCompatibility':copy.deepcopy(proof)}

    def test_document_stage_delta_requires_exact_independent_correspondence(self):
        packet,report,reuse=self._document_compatibility_fixture()
        with self.assertRaises(ValueError):j.validate_document_source_correspondence(packet,report,{})
        with patch.object(j,'pinned',return_value=b'proof') as pinned:
            j.validate_document_source_correspondence(packet,report,reuse)
            pinned.assert_called_once_with(reuse['documentBuildCompatibility']['independentDiffProof'],32*1024*1024)

    def test_document_compatibility_rejects_foreign_or_unreviewed_metadata(self):
        import copy
        packet,report,reuse=self._document_compatibility_fixture()
        for field,value in [('disposition','pending'),('scope','other'),('documentBuildReport',{'path':'/foreign','sha256':'f'*64}),('qaToolDeltas',[])]:
            bad=copy.deepcopy(reuse);bad['documentBuildCompatibility'][field]=value
            with self.assertRaises(ValueError):j.validate_document_source_correspondence(packet,report,bad)

    def test_document_compatibility_never_waives_product_or_arbitrary_tool_drift(self):
        import copy
        packet,report,reuse=self._document_compatibility_fixture()
        for name in ['implementation/warlock/src/HttpMain.elm','implementation/warlock/haskell/runtime/fixture-application-argv/Main.hs','tools/arm64_native_stage.py']:
            bad=copy.deepcopy(packet);bad['sourceHashes'][name]='f'*64
            with self.assertRaises(ValueError):j.validate_document_source_correspondence(bad,report,reuse)

    def test_document_compatibility_binds_selected_images_and_diff_proof_bytes(self):
        import copy
        packet,report,reuse=self._document_compatibility_fixture()
        for field in ['selectedBuiltImages','selectedAssets','compiledSelectedSourceHashes','currentSelectedSourceHashes']:
            bad=copy.deepcopy(reuse);bad['documentBuildCompatibility'][field]={}
            with self.assertRaises(ValueError):j.validate_document_source_correspondence(packet,report,bad)
        with patch.object(j,'pinned',side_effect=ValueError('proof changed')):
            with self.assertRaises(ValueError):j.validate_document_source_correspondence(packet,report,reuse)


    def test_preflight_collects_independent_errors_and_unchecked_dependencies(self):
        checks=j.PreflightChecks()
        for name in ('cache','stage'):
            checks.check(name,lambda:(_ for _ in ()).throw(ValueError('literal failure')))
        checks.check('images',lambda:self.fail('dependency executed'),('stage',))
        self.assertEqual([x['check'] for x in checks.blockers],['cache','stage','images'])
        self.assertEqual(checks.blockers[-1]['kind'],'dependency')
        self.assertFalse(checks.result()['passed'])

    def test_preflight_missing_two_helpers_reports_both(self):
        packet={'sourceHashes':dict(j.HELPERS)}
        missing=['tools/omarchy_ui_mvp.py','tools/run_webkit_provider_probe.py']
        for name in missing:del packet['sourceHashes'][name]
        checks=j.PreflightChecks();j.check_helper_membership(packet,checks)
        self.assertEqual({x['check'] for x in checks.blockers},{'helper-membership:'+x for x in missing})

    def test_preflight_stage_failure_does_not_hide_other_error(self):
        packet,report,reuse=self._document_compatibility_fixture()
        packet['sourceHashes']['tools/arm64_native_stage.py']='f'*64
        checks=j.PreflightChecks()
        checks.check('document-stage',lambda:j.validate_document_source_correspondence(packet,report,reuse))
        checks.check('cache',lambda:j.require_preflight(False,'cache changed'))
        self.assertEqual(len(checks.blockers),2)

    def test_preflight_cache_failure_still_scans_each_inventory_entry_once(self):
        import json
        files={'/usr/bin/a':{'mode':493,'sha256':'a'*64},'/usr/lib/b':{'link':'a'}}
        raw=json.dumps({'files':files}).encode()
        metadata=Mock(SYSTEM=Path('/fixed/inventory'),SYSTEM_SHA=j.digest(raw),unique=j.unique)
        metadata.regular.side_effect=lambda path,limit:raw if path==metadata.SYSTEM else b'changed-cache'
        checks=j.PreflightChecks()
        with patch.object(j,'system_input_actual',side_effect=lambda m,n,e:e) as actual:
            j.verify_system_preflight(metadata,metadata.SYSTEM_SHA,checks)
        self.assertEqual(actual.call_count,2)
        self.assertEqual(checks.system_inventory['matchedEntries'],2)
        self.assertEqual([x['check'] for x in checks.blockers],['system-loader-cache'])

    def test_preflight_accepted_cache_never_hides_inventory_drift(self):
        import json
        raw=json.dumps({'files':{'/usr/bin/a':{'mode':493,'sha256':'a'*64}}}).encode()
        metadata=Mock(SYSTEM=Path('/fixed/inventory'),SYSTEM_SHA=j.digest(raw),unique=j.unique)
        metadata.regular.side_effect=lambda p,l:raw if p==metadata.SYSTEM else b'cache'
        checks=j.PreflightChecks()
        proof=dict(schema=1,disposition='accepted',scope='ux003-current-loader-cache-correspondence',
            expectedCacheSha256=j.LEGACY_SYSTEM_CACHE_SHA,currentCacheSha256='1'*64,
            systemInventorySha256=metadata.SYSTEM_SHA,reviewer='build_audit',edgeCount=800,selectedResolutionMismatches=0,requiredAbsentCandidateCount=10,requiredAbsentNowPresent=[])
        with patch.object(j,'digest',side_effect=lambda b:'1'*64 if b==b'cache' else __import__('hashlib').sha256(b).hexdigest()),patch.object(j,'system_input_actual',return_value=None),patch.object(j,'pinned',return_value=json.dumps(proof).encode()):
            j.verify_system_preflight(metadata,metadata.SYSTEM_SHA,checks,{'path':'proof','sha256':'a'*64})
        self.assertEqual(len(checks.blockers),2)

    def test_preflight_utf8_canonical_matches_literal_nonascii_core_contract(self):
        import hashlib,json
        value={'expectedObservation':'café'}
        expected=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(j.canonical_json_sha256(value),expected)
        self.assertNotEqual(expected,hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest())

    def test_preflight_candidate_rejects_utf8_identity_or_fixed_argv_drift(self):
        candidate={'scope':'native','argv':['unexpected'],'expectedObservation':'café'}
        with self.assertRaises(ValueError):j.validate_candidate_identity(candidate,j.canonical_json_sha256(candidate),'a'*64)
        with self.assertRaises(ValueError):j.validate_candidate_identity(candidate,'f'*64,'a'*64)

    def test_blocked_native_main_never_stages_starts_clock_or_spawns(self):
        with patch.object(sys,'argv',['journey','--sha256','a'*64]),patch.object(j,'run_preflight',return_value=({'passed':False,'blockers':[{'check':'cache'}]},{})),patch.object(j.subprocess,'Popen') as spawn,patch.object(j,'staging_clock') as clock,patch.object(Path,'mkdir') as mkdir:
            self.assertEqual(j.main(),2)
            spawn.assert_not_called();clock.assert_not_called();mkdir.assert_not_called()

    def test_preflight_only_success_never_stages_starts_clock_or_spawns(self):
        with patch.object(sys,'argv',['journey','--sha256','a'*64,'--preflight-only']),patch.object(j,'run_preflight',return_value=({'passed':True,'blockers':[]},{})) as phase,patch.object(j.subprocess,'Popen') as spawn,patch.object(j,'staging_clock') as clock,patch.object(Path,'mkdir') as mkdir:
            self.assertEqual(j.main(),0)
            phase.assert_called_once_with('a'*64,None,None)
            spawn.assert_not_called();clock.assert_not_called();mkdir.assert_not_called()

    def test_native_and_readonly_modes_share_phase_before_effects(self):
        tree=ast.parse(Path(j.__file__).read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        calls=[n.func.id for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
        self.assertEqual(calls.count('run_preflight'),1)
        self.assertIn('staging_clock',calls)

    def test_preflight_dependency_categories_never_claim_complete(self):
        checks=j.PreflightChecks();checks.check('packet-images',lambda:None,('packet-shape',))
        result=checks.result()
        self.assertEqual(result['disposition'],'blocked')
        self.assertFalse(result['nativeAuthorized']);self.assertFalse(result['effectsStarted'])



    def test_preflight_cache_changed_during_inventory_scan_refuses(self):
        import json
        raw=json.dumps({'files':{'/usr/bin/a':{'mode':493,'sha256':'a'*64}}}).encode()
        metadata=Mock(SYSTEM=Path('/fixed/inventory'),SYSTEM_SHA=j.digest(raw),unique=j.unique)
        cache_reads=iter([b'before',b'after'])
        metadata.regular.side_effect=lambda p,l:raw if p==metadata.SYSTEM else next(cache_reads)
        checks=j.PreflightChecks()
        with patch.object(j,'system_input_actual',side_effect=lambda m,n,e:e):
            j.verify_system_preflight(metadata,metadata.SYSTEM_SHA,checks)
        self.assertIn('system-loader-cache-stability',[x['check'] for x in checks.blockers])
        self.assertFalse(checks.result()['passed'])

    def test_preflight_native_success_report_is_emitted_before_qa_scope(self):
        tree=ast.parse(Path(j.__file__).read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        printed=[n.lineno for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='print']
        qa=[n.lineno for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require_qa_scope']
        self.assertTrue(printed and qa and min(printed)<min(qa))


    @staticmethod
    def _selected720_monitor(height=720):
        import json
        return json.dumps([{'name':'WAYLAND-1','width':1280,'height':height,'x':0,'y':0,'scale':1,'transform':0,'disabled':False}]).encode()

    def test_selected720_fixture_is_strict_not_a_resolution_wildcard(self):
        self.assertEqual(j.geometry.validate_monitor(self._selected720_monitor(),(1280,720))['height'],720)
        for height in (719,721,800):
            with self.assertRaises(ValueError):j.geometry.validate_monitor(self._selected720_monitor(height),(1280,720))
        with self.assertRaises(ValueError):j.geometry.validate_monitor(self._selected720_monitor(),(1280,800))

    def test_selected720_parser_preserves_utf8_finite_and_active_geometry_guards(self):
        import json
        row=json.loads(self._selected720_monitor())[0]
        variants=[dict(row,scale=2),dict(row,transform=1),dict(row,disabled=True),dict(row,width=1279),dict(row,x=1)]
        for value in variants:
            with self.assertRaises(ValueError):j.geometry.validate_monitor(json.dumps([value]).encode(),(1280,720))
        for raw in [self._selected720_monitor().decode().encode('utf-16'),json.dumps([dict(row,unused=float('nan'))]).encode(),b'[]',b'[{"height":720,"height":800}]']:
            with self.assertRaises(ValueError):j.geometry.validate_monitor(raw,(1280,720))

    def test_selected720_png_frame_correspondence_rejects_old800_frame(self):
        import struct,zlib
        def chunk(kind,body):return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
        def png(height):
            body=(b'\x00'+bytes(1280))*height
            return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1280,height,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(body))+chunk(b'IEND',b'')
        self.assertEqual(j.geometry.png_dimensions(png(720)),(1280,720))
        j.geometry.require_frame(png(720),(1280,720))
        with self.assertRaises(ValueError):j.geometry.require_frame(png(800),(1280,720))
        with self.assertRaises(ValueError):j.geometry.require_frame(png(720),(1280,800))

    def test_selected720_fits_unchanged_owner_and_exact_pointer_offsets_without_poll(self):
        extent=(1280,720);origin=(150,20);owner=(980,680)
        for step,offset,n in [('open',(48,28),1),('visible',(150,460),2)]:
            point=tuple(a+b for a,b in zip(origin,offset))
            self.assertTrue(all(0<=p<s for p,s in zip(offset,owner)))
            self.assertTrue(all(0<=p<e for p,e in zip(point,extent)))
            emit=Mock(return_value=(0,('ready %s\n'%n).encode()))
            j.perform_pointer_step(step,point,extent,set(),emit)
            emit.assert_called_once_with(('move %s %s\nbutton 272 1\nbutton 272 0\nsync %s\n'%(point[0],point[1],n)).encode())
        self.assertTrue(origin[1]+owner[1]<=extent[1]);self.assertEqual(j.ARGV_BYTES,b'["two words","","caf\\233"]\n')
        tree=ast.parse(Path(j.__file__).read_text())
        self.assertFalse(any(isinstance(n,ast.FunctionDef) and n.name=='await_nested_geometry' for n in tree.body))
        owner_node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='_OwnedStack')
        start=next(n for n in owner_node.body if isinstance(n,ast.FunctionDef) and n.name=='start')
        self.assertTrue(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='write_text' and n.args and isinstance(n.args[0],ast.Attribute) and isinstance(n.args[0].value,ast.Name) and n.args[0].value.id=='c' and n.args[0].attr=='RC' for n in ast.walk(start)))
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
        launch=next(n.value for n in ast.walk(main)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='pointer_proc'for x in n.targets))
        self.assertEqual(ast.dump(launch.args[0],include_attributes=False),ast.dump(ast.parse("[assets['pointer']['path'],'1280','720']",mode='eval').body,include_attributes=False))
        click=next(n for n in ast.walk(main)if isinstance(n,ast.FunctionDef)and n.name=='click')
        calls=[n for n in ast.walk(click)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='held_pointer'and n.func.attr=='transact']
        self.assertEqual(len(calls),1)
        self.assertEqual([ast.dump(x,include_attributes=False)for x in calls[0].args],[ast.dump(x,include_attributes=False)for x in ast.parse("held_pointer.transact(step, point, packet['input']['monitorSize'])",mode='eval').body.args])


    def test_owned_fonts_live_inputs_remove_only_exact_ten_historical_caches(self):
        f=j.owned_fonts
        historical=dict(f.GLOBAL_CACHE_PINS,**f.FONT_PINS,**{'/usr/lib/qualified.so':'a'*64})
        live=f.live_inputs(historical)
        self.assertEqual(set(historical)-set(live),set(f.GLOBAL_CACHE_PINS))
        self.assertEqual({k:live[k] for k in f.FONT_PINS},f.FONT_PINS)
        for changed in [dict(historical,**{'/var/cache/fontconfig/unexpected.cache':'b'*64}),dict(historical,**{next(iter(f.FONT_PINS)):'b'*64})]:
            with self.assertRaises(ValueError):f.live_inputs(changed)

    def test_owned_fonts_environment_is_private_parent_issued_and_nonmutating(self):
        f=j.owned_fonts
        with self.assertRaises(ValueError):f.environment({}, {'config':'/etc/fonts/fonts.conf'})
        layout={'_owner':f._LAYOUT_KEY,'config':'/owned/nested-font-config/fonts.conf','configSha256':'a'*64,'configDirectory':'/owned/nested-font-config','copies':{}}
        source={'WAYLAND_DISPLAY':'/owned/display'}
        with patch.object(f,'read_pinned',return_value=b'config'):
            env=f.environment(source,layout)
        self.assertEqual(source,{'WAYLAND_DISPLAY':'/owned/display'})
        self.assertEqual(env['FONTCONFIG_FILE'],layout['config']);self.assertEqual(env['FONTCONFIG_USE_MMAP'],'0')
        self.assertEqual(env['FONTCONFIG_PATH'],layout['configDirectory'])

    def test_owned_fonts_drift_refuses_before_creating_layout(self):
        import tempfile
        f=j.owned_fonts
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory);output.chmod(0o700)
            with patch.object(f,'FONT_PINS',{'/qualified/font.ttf':'a'*64}),patch.object(f,'read_pinned',side_effect=ValueError('font changed')):
                with self.assertRaises(ValueError):f.prepare(output,Mock())
            self.assertEqual(list(output.iterdir()),[])

    def test_owned_fonts_copy_hashes_config_scope_and_originalD_guard(self):
        import tempfile,hashlib,xml.etree.ElementTree as ET
        f=j.owned_fonts
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory);output.chmod(0o700);source=output/'source.ttf';source.write_bytes(b'fixedfont');pin=hashlib.sha256(b'fixedfont').hexdigest()
            with patch.object(f,'FONT_PINS',{str(source):pin}):layout=f.prepare(output,Mock())
            tree=ET.fromstring(Path(layout['config']).read_bytes())
            self.assertEqual(tree.findtext('dir'),str(output/'nested-fonts'))
            self.assertEqual(tree.findtext('cachedir'),str(output/'nested-font-cache'))
            self.assertEqual(tree.findall('include'),[])
            self.assertEqual(f.mapping_inputs(layout),{str(output/'nested-fonts/source.ttf'):pin})
            Path(layout['config']).write_bytes(b'changed')
            with self.assertRaises(ValueError):f.environment({},layout)
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory);output.chmod(0o700)
            with self.assertRaises(TimeoutError):f.prepare(output,Mock(side_effect=TimeoutError('originalD')))
            self.assertEqual(list(output.iterdir()),[])

    def test_product_transport_preserves_issued_endpoint_as_relative_basename(self):
        runtime='/run/user/1000/wqa/private-session'
        source={'XDG_RUNTIME_DIR':runtime,'WAYLAND_DISPLAY':runtime+'/wayland-1'}
        env=j.product_environment(source)
        self.assertEqual(env['XDG_RUNTIME_DIR'],runtime)
        self.assertEqual(env['WAYLAND_DISPLAY'],'wayland-1')
        self.assertEqual(str(Path(env['XDG_RUNTIME_DIR'])/env['WAYLAND_DISPLAY']),source['WAYLAND_DISPLAY'])
        self.assertEqual(source['WAYLAND_DISPLAY'],runtime+'/wayland-1')

    def test_product_transport_rejects_noncanonical_or_foreign_endpoint(self):
        runtime='/run/user/1000/wqa/private-session'
        bad=[(runtime+'/',runtime+'/wayland-1'),(runtime,runtime+'//wayland-1'),
             (runtime,runtime+'/../wayland-1'),(runtime,runtime+'/nested/wayland-1'),
             (runtime,'/foreign/wayland-1'),(runtime,runtime+'/not-wayland'),
             (runtime,runtime+'/wayland-'+('x'*57))]
        for root,display in bad:
            with self.subTest(root=root,display=display):
                with self.assertRaises(ValueError):
                    j.product_environment({'XDG_RUNTIME_DIR':root,'WAYLAND_DISPLAY':display})

    def test_live_config_rule_is_exact_nonempty_observed_class(self):
        c=j.load_helper(j.LIVE_CONFIG_HELPER,'test_owned_window_live_config')
        self.assertIn('match={class="^GTK Application$"}',c.NESTED_LUA)
        self.assertNotIn('match={}',c.NESTED_LUA)
        self.assertIn('float=true,center=true,size={980,680}',c.NESTED_LUA)
        self.assertEqual(j.digest(c.NESTED_LUA.encode()),c.NESTED_LUA_SHA)

    def test_live_config_helper_preserves_historical_policy_entire_ast(self):
        before=ast.parse((j.ROOT/j.GENERATED_HELPER).read_text())
        after=ast.parse((j.ROOT/j.LIVE_CONFIG_HELPER).read_text())
        def policy(tree):
            return [ast.dump(n,include_attributes=False) for n in tree.body if not (isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id in ('NESTED_LUA','NESTED_LUA_SHA') for v in n.targets))]
        self.assertEqual(policy(before),policy(after))
        self.assertNotEqual(j.GENERATED_HELPER,j.LIVE_CONFIG_HELPER)
        self.assertEqual(j.HELPERS[j.GENERATED_HELPER],'f313c21d4e47adf8b3d37a3abd9ac9b5901b397901260cf71970e4abf47a1f69')

    def test_live_config_writer_and_receipt_source_pin_are_current(self):
        import tempfile
        c=j.load_helper(j.LIVE_CONFIG_HELPER,'test_owned_window_config_write')
        with tempfile.TemporaryDirectory() as root:
            path=c.write_nested_config(Path(root))
            self.assertEqual(path.read_bytes(),c.NESTED_LUA.encode())
            self.assertEqual(j.digest(path.read_bytes()),c.NESTED_LUA_SHA)
            self.assertEqual(c.nested_argv('/owned/nested',Path(root)),['/owned/nested','--config',str(path)])
            with self.assertRaises(FileExistsError):c.write_nested_config(Path(root))


    def test_opener_readiness_actual_blank_and_five_painted_frames(self):
        import hashlib
        ready=j.load_helper('tools/ux003_opener_readiness.py','test_opener_actual_frames')
        root=j.ROOT/'.warlock-contributor/current-arm-ux003-journey-1794136423914047474'
        corpus=[('mapped',False,'29a302ba8e2130778037768012d7096f966fe66496a853db420b27a7ccc5439e'),
          ('catalog-before-search',True,'be468a6120afdcdc664b1b8f4be77126cace238ce2071ef1539536c6dde90aae'),
          ('hidden-search',True,'11f2152eeb6b32d0e92d91053bd1abf2df17c4d99269b668804e30de40909b8f'),
          ('search-cleared',True,'8a446f2cf6c472a0c2dfecbfbc772b7ca2ee1e2aec0695a96080167b820195f9'),
          ('visible-search',True,'1f9e7ceee05ba584f692b79ae9776ad21bef5f3fcfd38c968c8f5c42f3717a98'),
          ('after-launch',True,'293f9524a5fb677dfb8ddb8a21776a3d84e9c7af0b10c1e6113e2ab12d7dc575')]
        for name,expected,pin in corpus:
            raw=(root/(name+'.png')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),pin)
            self.assertIs(ready.opener_readiness(raw,(150,20),(980,680))['ready'],expected,name)

    def test_opener_readiness_rejects_crop_bad_framing_and_outside_window(self):
        ready=j.load_helper('tools/ux003_opener_readiness.py','test_opener_bad_frames')
        raw=(j.ROOT/'.warlock-contributor/current-arm-ux003-journey-1794136423914047474/visible-search.png').read_bytes()
        for data in (b'',raw[:-1],raw[:64],raw[:-4]+b'bad!'):
            with self.assertRaises(ValueError):ready.opener_readiness(data,(150,20),(980,680))
        for at,size in (((True,20),(980,680)),((-1,20),(980,680)),((301,20),(980,680)),((150,20),(979,680)),((150,41),(980,680))):
            with self.assertRaises(ValueError):ready.opener_readiness(raw,at,size)

    def test_opener_pixel_witness_requires_enabled_colors_and_text(self):
        ready=j.load_helper('tools/ux003_opener_readiness.py','test_opener_color_policy')
        self.assertTrue(ready.enabled_opener_pixels([(53,28,31)]*400,[(246,239,232)]*100+[(53,28,31)]*1088))
        self.assertFalse(ready.enabled_opener_pixels([(19,16,17)]*400,[(246,239,232)]*1188))
        self.assertFalse(ready.enabled_opener_pixels([(53,28,31)]*400,[(154,142,139)]*1188))
        self.assertFalse(ready.enabled_opener_pixels([(53,28,31)]*400,[(246,239,232)]*99+[(53,28,31)]*1089))
        self.assertFalse(ready.enabled_opener_pixels([(53,28,31)]*399,[(246,239,232)]*1188))

    def test_opener_label_sampling_excludes_known_cursor_footprint(self):
        ready=j.load_helper('tools/ux003_opener_readiness.py','test_opener_cursor_mask')
        for point in ((48,28),(44,20),(73,37)):
            self.assertFalse(ready.label_pixel_sampled(*point))
        for point in ((25,25),(100,25)):
            self.assertTrue(ready.label_pixel_sampled(*point))
        self.assertEqual(sum(ready.label_pixel_sampled(x,y)for y in range(20,38)for x in range(22,118)),1188)

    def test_opener_wait_records_each_frame_and_only_then_allows_single_input(self):
        record=[];order=[];emit=Mock(return_value=(0,b'ready 1\n'))
        frames=iter([(b'blank',{'screenshot':'blank.png'}),(b'painted',{'screenshot':'ready.png'})])
        def check():order.append('owned')
        def capture(index):order.append('capture'+str(index));return next(frames)
        def predicate(raw):return {'ready':raw==b'painted'}
        found=j.await_rendered_opener(check,capture,predicate,record)
        self.assertEqual(found['screenshot'],'ready.png');self.assertEqual([r['witness']['ready']for r in record],[False,True])
        self.assertEqual(order,['owned','capture0','owned','owned','capture1','owned'])
        j.perform_pointer_step('open',(198,48),(1280,720),set(),emit);self.assertEqual(emit.call_count,1)

    def test_opener_wait_timeout_or_bad_frame_never_spends_input(self):
        for failure in (TimeoutError('same originalD'),ValueError('bad PNG')):
            emit=Mock();record=[]
            def trial():
                j.await_rendered_opener(lambda:None,lambda _: (b'bad',{}),Mock(side_effect=failure),record)
                j.perform_pointer_step('open',(198,48),(1280,720),set(),emit)
            with self.assertRaises(type(failure)):trial()
            emit.assert_not_called()
        record=[];capture=Mock(return_value=(b'blank',{}))
        with self.assertRaises(ValueError):j.await_rendered_opener(lambda:None,capture,lambda _: {'ready':False},record)
        self.assertEqual(capture.call_count,16);self.assertEqual(len(record),16)

    def test_native_opener_wait_is_before_sole_open_transaction(self):
        tree=ast.parse(Path(j.__file__).read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
        calls=[n for n in ast.walk(main)if isinstance(n,ast.Call)]
        waits=[n.lineno for n in calls if isinstance(n.func,ast.Name)and n.func.id=='await_rendered_opener']
        opens=[n.lineno for n in calls if isinstance(n.func,ast.Name)and n.func.id=='click'and n.args and isinstance(n.args[0],ast.Constant)and n.args[0].value=='open']
        self.assertEqual(len(waits),1);self.assertEqual(len(opens),1);self.assertLess(waits[0],opens[0])


    def held_pointer_fixture(self):
        self.enterContext(patch.object(j.select,'select',return_value=([],[],[])))
        self.enterContext(patch.object(j.os,'killpg',side_effect=ProcessLookupError))
        proc=Mock(spec=j.subprocess.Popen);proc.pid=123;proc.poll.return_value=None
        proc.stdin=Mock();proc.stdout=Mock();proc.stdout.fileno.return_value=11
        proc.stdin.write.side_effect=lambda raw:len(raw)
        held=j._HeldPointer.__new__(j._HeldPointer)
        held.proc=proc;held.clock={'deadline':100};held.start_ticks=99
        held.image_sha='a'*64;held.stderr_path=Path('/unused/mock.stderr')
        held.used=set();held.bootstrap=None;held.final=None;held.closing=False
        held.attest=Mock();held.read_ack=Mock(side_effect=lambda expected:expected)
        return held,proc

    def test_held_pointer_bootstrap_is_noninput_and_live(self):
        held,proc=self.held_pointer_fixture();row=held.start()
        proc.stdin.write.assert_called_once_with(b'sync 0\n')
        held.read_ack.assert_called_once_with(b'ready 0\n')
        self.assertIsNone(row['exit']);self.assertTrue(row['alive'])
        self.assertEqual(row['startTicks'],99)
        with self.assertRaises(ValueError):held.start()
        self.assertEqual(proc.stdin.write.call_count,1)

    def test_held_pointer_same_process_exact_two_original_payloads(self):
        held,proc=self.held_pointer_fixture();held.start()
        for step,n in [('open',1),('visible',2)]:
            row=held.transact(step,(198,48),(1280,720))
            self.assertEqual(row['pid'],123);self.assertIsNone(row['exit'])
            self.assertEqual(row['inputHex'],('move 198 48\nbutton 272 1\nbutton 272 0\nsync %s\n'%n).encode().hex())
        self.assertEqual(proc.stdin.write.call_count,3)

    def test_held_pointer_requires_bootstrap_order_and_never_replays_uncertain_input(self):
        held,proc=self.held_pointer_fixture()
        with self.assertRaises(ValueError):held.transact('open',(1,2),(1280,720))
        proc.stdin.write.assert_not_called();held.start()
        with self.assertRaises(ValueError):held.transact('visible',(1,2),(1280,720))
        held.read_ack.side_effect=TimeoutError('same D')
        with self.assertRaises(TimeoutError):held.transact('open',(1,2),(1280,720))
        with self.assertRaises(ValueError):held.transact('open',(1,2),(1280,720))
        self.assertEqual(proc.stdin.write.call_count,2)

    def test_held_pointer_custody_failure_prevents_any_write(self):
        held,proc=self.held_pointer_fixture();held.attest.side_effect=ValueError('birth changed')
        with self.assertRaises(ValueError):held.start()
        proc.stdin.write.assert_not_called()

    def test_held_pointer_partial_ack_reads_stay_under_original_clock(self):
        held,proc=self.held_pointer_fixture();del held.read_ack
        with patch.object(j.select,'select',return_value=([11],[],[])),patch.object(j.os,'read',side_effect=[b'rea',b'dy 0\n']),patch.object(j,'left',return_value=17):
            self.assertEqual(held.read_ack(b'ready 0\n'),b'ready 0\n')
        self.assertEqual(held.clock,{'deadline':100})

    def test_held_pointer_stale_extra_eof_and_timeout_ack_refuse(self):
        for raw in (b'ready 2\n',b'ready 0\nextra',b''):
            held,proc=self.held_pointer_fixture();del held.read_ack
            with patch.object(j.select,'select',return_value=([11],[],[])),patch.object(j.os,'read',return_value=raw),patch.object(j,'left',return_value=17):
                with self.assertRaises(ValueError):held.read_ack(b'ready 0\n')
        held,proc=self.held_pointer_fixture();del held.read_ack
        with patch.object(j.select,'select',return_value=([],[],[])),patch.object(j,'left',return_value=17):
            with self.assertRaises(TimeoutError):held.read_ack(b'ready 0\n')

    def test_held_pointer_final_requires_real_zero_and_no_unread_output_or_diagnostics(self):
        for code,tail,err in ((1,b'',b''),(0,b'extra',b''),(0,b'',b'diagnostic')):
            held,proc=self.held_pointer_fixture();proc.communicate.return_value=(tail,None);proc.returncode=code
            with patch.object(j,'left',return_value=17),patch.object(j,'regular',return_value=err):
                with self.assertRaises(ValueError):held.finish()
            self.assertTrue(held.closing)
        held,proc=self.held_pointer_fixture();proc.communicate.return_value=(b'',None);proc.returncode=0
        with patch.object(j,'left',return_value=17),patch.object(j,'regular',return_value=b''):
            row=held.finish()
        proc.communicate.assert_called_once_with(b'',timeout=17/1_000_000_000)
        self.assertEqual(row['exit'],0);self.assertTrue(row['normal']);self.assertIs(held.finish(),row)

    def test_held_pointer_partial_write_is_never_reissued(self):
        held,proc=self.held_pointer_fixture();proc.stdin.write.return_value=1;proc.stdin.write.side_effect=None
        with self.assertRaises(ValueError):held.start()
        with self.assertRaises(ValueError):held.start()
        self.assertEqual(proc.stdin.write.call_count,1)

    def test_held_pointer_native_start_precedes_backend_and_close_follows_gui_close(self):
        tree=ast.parse(Path(j.__file__).read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
        calls=[n for n in ast.walk(main)if isinstance(n,ast.Call)]
        bootstrap=next(n.lineno for n in calls if isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='held_pointer'and n.func.attr=='start')
        backend=next(n.lineno for n in ast.walk(main)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='backend'for x in n.targets)and isinstance(n.value,ast.Call))
        finish=next(n.lineno for n in calls if isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='held_pointer'and n.func.attr=='finish')
        close=next(n.lineno for n in calls if isinstance(n.func,ast.Name)and n.func.id=='keyboard_args'and n.args and isinstance(n.args[0],ast.Constant)and n.args[0].value=='close')
        self.assertLess(bootstrap,backend);self.assertLess(close,finish)
        click=next(n for n in ast.walk(main)if isinstance(n,ast.FunctionDef)and n.name=='click')
        self.assertIn('held_pointer.transact',ast.unparse(click));self.assertNotIn("command('pointer'",ast.unparse(click))


    def test_held_pointer_late_custody_read_refuses_before_write(self):
        held,proc=self.held_pointer_fixture();del held.attest
        with patch.object(j,'left',side_effect=[17,TimeoutError('original D elapsed during image read')]),patch.object(j,'birth',return_value=(99,)),patch.object(j.os,'getpgid',return_value=123),patch.object(j,'regular',side_effect=[b'image',b'']),patch.object(j,'digest',return_value='a'*64):
            with self.assertRaises(TimeoutError):held.start()
        proc.stdin.write.assert_not_called()

    def test_held_pointer_retained_group_after_reap_cannot_be_normal(self):
        held,proc=self.held_pointer_fixture();proc.communicate.return_value=(b'',None);proc.returncode=0
        with patch.object(j,'left',return_value=17),patch.object(j,'regular',return_value=b''),patch.object(j.os,'killpg',return_value=None):
            with self.assertRaises(ValueError):held.finish()
        self.assertIsNone(held.final)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--module',type=Path,required=True);a=p.parse_args()
    sys.path.insert(0,str(a.module.parent));spec=importlib.util.spec_from_file_location('current_journey',a.module)
    if spec is None or spec.loader is None:raise RuntimeError('fixed journey source missing')
    j=importlib.util.module_from_spec(spec);spec.loader.exec_module(j)
    unittest.main(argv=['current-journey-pure-contracts'])

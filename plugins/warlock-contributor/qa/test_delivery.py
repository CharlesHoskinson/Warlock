"""Backlog, native progress and staging checks in isolated contribution repositories."""
import json
import subprocess
import sys
import unittest

import test_warlock as fixtures


class DeliveryHelperTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli

    def test_remaining_preserves_original_oracles_and_writes_nothing(self):
        ledger = self.repo / 'docs/warlock-build-loop/v2/requirement-ledger.json'
        before = ledger.read_bytes()
        report = json.loads(self.cli('remaining', '--requirement', 'ELM-UI-007').stdout)
        original = next(r for r in self.fixture.original['requirements'] if r['id'] == 'ELM-UI-007')
        self.assertEqual(report['requirementsConsidered'], 1)
        self.assertEqual(report['matchingScenarios'], len(original['scenarios']))
        self.assertEqual([r['original'] for r in report['scenarios']], original['scenarios'])
        self.assertTrue(all(r['verificationScope'] == original['verification'] for r in report['scenarios']))
        self.assertTrue(report['recordedOnly'])
        self.assertFalse(report['releaseAccepted'])
        self.assertEqual(before, ledger.read_bytes())
        self.assertFalse((self.repo / '.warlock-contributor/slice.json').exists())

    def test_remaining_default_excludes_accepted_but_counts_it_without_inference(self):
        name = 'docs/warlock-build-loop/v2/requirement-ledger.json'
        ledger = json.loads((self.repo / name).read_text())
        row = next(r for r in ledger['requirements'] if r['id'] == 'ELM-UI-007')
        row['scenarios'][0]['status'] = 'accepted'
        row['scenarios'][1]['status'] = 'failed'
        self.fixture.write(name, ledger)
        report = json.loads(self.cli('remaining', '--requirement', 'ELM-UI-007').stdout)
        self.assertEqual(report['scenarioCountsByRecordedStatus']['accepted'], 1)
        self.assertEqual(report['matchingScenarios'], len(row['scenarios']) - 1)
        self.assertFalse(any(r['ledger']['status'] == 'accepted' for r in report['scenarios']))
        failed = json.loads(self.cli('remaining', '--requirement', 'ELM-UI-007', '--status', 'failed').stdout)
        self.assertEqual(failed['matchingScenarios'], 1)
        accepted = json.loads(self.cli('remaining', '--requirement', 'ELM-UI-007', '--status', 'accepted').stdout)
        self.assertEqual(accepted['matchingScenarios'], 1)
        self.assertTrue(accepted['recordedOnly'])

    def test_remaining_summary_counts_whole_baseline_and_rejects_invalid_ids(self):
        report = json.loads(self.cli('remaining', '--summary').stdout)
        self.assertEqual(report['requirementsConsidered'], 242)
        self.assertEqual(sum(report['scenarioCountsByRecordedStatus'].values()), 417)
        self.assertEqual(report['scenarios'], [])
        self.cli('remaining', '--requirement', 'CONTROL-NEW', ok=False)
        self.cli('remaining', '--requirement', 'ELM-UI-007', '--requirement', 'ELM-UI-007', ok=False)

    def test_remaining_pages_partition_filtered_rows_without_losing_originals(self):
        full = json.loads(self.cli('remaining', '--requirement', 'ELM-UI-007').stdout)
        collected, offset = [], 0
        while True:
            page = json.loads(self.cli('remaining', '--requirement', 'ELM-UI-007',
                                      '--limit', '2', '--offset', str(offset)).stdout)
            self.assertEqual(page['ledgerSha256'], full['ledgerSha256'])
            self.assertEqual(page['matchingScenarios'], full['matchingScenarios'])
            self.assertEqual(page['scenarioCountsByRecordedStatus'], full['scenarioCountsByRecordedStatus'])
            self.assertLessEqual(page['shownScenarios'], 2)
            self.assertEqual(page['shownScenarios'], len(page['scenarios']))
            self.assertEqual(page['omittedBefore'] + page['shownScenarios'] + page['omittedAfter'],
                             full['matchingScenarios'])
            collected.extend(page['scenarios'])
            if page['nextOffset'] is None:
                break
            self.assertGreater(page['nextOffset'], offset)
            offset = page['nextOffset']
        self.assertEqual(collected, full['scenarios'])

    def test_remaining_applies_status_filter_before_paging(self):
        name = 'docs/warlock-build-loop/v2/requirement-ledger.json'
        ledger = json.loads((self.repo / name).read_text())
        row = next(r for r in ledger['requirements'] if r['id'] == 'ELM-UI-007')
        for scenario in row['scenarios']:
            scenario['status'] = 'accepted'
        row['scenarios'][-1]['status'] = 'failed'
        self.fixture.write(name, ledger)
        packet = json.loads(self.cli('remaining', '--requirement', row['id'],
                                    '--status', 'failed', '--limit', '1').stdout)
        self.assertEqual(packet['matchingScenarios'], 1)
        self.assertEqual(packet['scenarios'][0]['original']['name'], row['scenarios'][-1]['name'])
        self.assertIsNone(packet['nextOffset'])

    def test_remaining_invalid_bounds_and_conflicting_options_fail(self):
        for options in (('--limit', '0'), ('--limit', '-1'), ('--offset', '-1'),
                        ('--limit', 'abc'), ('--summary', '--limit', '2'),
                        ('--summary', '--offset', '1'), ('--markdown',)):
            with self.subTest(options=options):
                self.cli('remaining', *options, ok=False)

    def test_remaining_empty_page_is_explicit_and_does_not_infer_completion(self):
        packet = json.loads(self.cli('remaining', '--limit', '3', '--offset', '1000').stdout)
        self.assertGreater(packet['matchingScenarios'], 0)
        self.assertEqual(packet['scenarios'], [])
        self.assertEqual(packet['omittedBefore'], packet['matchingScenarios'])
        self.assertEqual(packet['omittedAfter'], 0)
        self.assertIsNone(packet['nextOffset'])
        self.assertFalse(packet['releaseAccepted'])
        text = self.remaining_markdown('--limit', '3', '--offset', '1000')
        self.assertIn('No rows on this page', text)
        self.assertIn('does not establish release completion', text)

    def remaining_markdown(self, *options):
        result = subprocess.run([sys.executable, '-B', str(fixtures.CHECKER), '--repo',
                                 str(self.repo), 'remaining', '--markdown', *options],
                                capture_output=True, text=True, env=self.fixture.env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_remaining_markdown_retains_obligations_and_is_read_only(self):
        ledger = self.repo / 'docs/warlock-build-loop/v2/requirement-ledger.json'
        row = next(r for r in json.loads(ledger.read_text())['requirements'] if r['id'] == 'ELM-UI-007')
        row['scenarios'][0]['missingObservation'] = 'Actual native presentation remains open'
        data = json.loads(ledger.read_text())
        next(r for r in data['requirements'] if r['id'] == row['id'])['scenarios'] = row['scenarios']
        self.fixture.write(str(ledger.relative_to(self.repo)), data)
        before = (ledger.read_bytes(), (self.repo / '.git/index').read_bytes())
        text = self.remaining_markdown('--requirement', row['id'], '--limit', '1')
        self.assertIn(row['scenarios'][0]['name'], text)
        self.assertIn('Original oracle:', text)
        self.assertIn('Verification obligations:', text)
        self.assertIn('Actual native presentation remains open', text)
        self.assertIn('omitted', text)
        self.assertIn('Ledger SHA-256:', text)
        self.assertNotIn('- [x]', text)
        self.assertEqual(before, (ledger.read_bytes(), (self.repo / '.git/index').read_bytes()))
        self.assertFalse((self.repo / '.warlock-contributor/slice.json').exists())

    def test_remaining_markdown_does_not_check_recorded_acceptance_or_render_injected_text(self):
        name = 'docs/warlock-build-loop/v2/requirement-ledger.json'
        data = json.loads((self.repo / name).read_text())
        row = next(r for r in data['requirements'] if r['id'] == 'ELM-UI-007')
        row['scenarios'][0].update(status='accepted', missingObservation=
                                  '<script>bad</script>\n# Approved\n[claim](https://example.invalid)')
        self.fixture.write(name, data)
        text = self.remaining_markdown('--requirement', row['id'], '--status', 'accepted', '--limit', '1')
        self.assertIn('recorded accepted', text)
        self.assertIn('not revalidated', text)
        self.assertNotIn('- [x]', text)
        self.assertNotIn('<script>', text)
        self.assertNotIn('\n# Approved', text)
        self.assertNotIn('[claim](', text)

    def test_remaining_markdown_summary_has_no_scenario_detail(self):
        text = self.remaining_markdown('--summary')
        self.assertIn('242 requirements considered', text)
        self.assertIn('Recorded counts:', text)
        self.assertNotIn('Original oracle:', text)
        self.assertNotIn('Next page:', text)

    def start_native(self, extension):
        name = 'implementation/warlock/native/authority' + extension
        self.fixture.write(name, 'original native unit\n')
        self.fixture.run_git('add', name)
        self.fixture.run_git('commit', '-qm', 'native fixture')
        selection = dict(self.fixture.slice, paths=[name])
        self.fixture.write('.warlock-contributor/native-plan.json', selection)
        self.cli('start', '--owner', 'native-contributor', '--slice-file', '.warlock-contributor/native-plan.json')
        self.fixture.write(name, 'changed native behavior\n')
        return name

    def test_cpp_and_hpp_are_historical_only_under_policy_five(self):
        for extension in ('.cpp', '.hpp'):
            with self.subTest(extension=extension):
                if (self.repo / '.warlock-contributor/slice.json').exists():
                    self.fixture.run_git('add', 'implementation/warlock')
                    self.fixture.run_git('commit', '-qm', 'retain previous native fixture')
                    (self.repo / '.warlock-contributor/slice.json').rename(self.repo / '.warlock-contributor/previous.json')
                self.start_native(extension)
                self.cli('record', '--outcome', 'production-fix', '--summary', 'native behavior changed')
                record = json.loads((self.repo / '.warlock-contributor/slice.json').read_text())
                self.assertFalse(record['iterations'][-1]['meaningfulProgress'])
                self.assertEqual(record['iterations'][-1]['progressPolicy'], 6)
                # Reconstruct a historical policy-4 row and prove it remains valid.
                record['iterations'][-1].update(progressPolicy=4, meaningfulProgress=True)
                self.fixture.write('.warlock-contributor/slice.json', record)
                self.fixture.refresh_fixture_participant_index()
                self.cli('check')

    def test_legacy_cpp_progress_assertion_remains_valid(self):
        self.start_native('.cpp')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'native behavior changed')
        path = self.repo / '.warlock-contributor/slice.json'
        record = json.loads(path.read_text())
        record['iterations'][-1].pop('progressPolicy')
        record['iterations'][-1]['meaningfulProgress'] = False
        self.fixture.write(str(path.relative_to(self.repo)), record)
        self.fixture.refresh_fixture_participant_index()
        self.cli('check')
        self.cli('record', '--outcome', 'qualification', '--summary', 'no additional code change')
        record = json.loads(path.read_text())
        self.assertFalse(record['iterations'][-1]['meaningfulProgress'])

    def test_review_is_read_only_and_compares_staged_source(self):
        self.fixture.start()
        name = 'implementation/warlock/src/Desktop.elm'
        self.fixture.write(name, 'authored implementation\n')
        self.fixture.run_git('add', name)
        index = (self.repo / '.git/index').read_bytes()
        record = (self.repo / '.warlock-contributor/slice.json').read_bytes()
        report = json.loads(self.cli('review').stdout)
        self.assertEqual([r['path'] for r in report['staged']], [name])
        self.assertTrue(report['staged'][0]['matchesWorkingTree'])
        self.assertEqual(index, (self.repo / '.git/index').read_bytes())
        self.assertEqual(record, (self.repo / '.warlock-contributor/slice.json').read_bytes())
        self.fixture.write(name, 'additional untested edit\n')
        report = json.loads(self.cli('review', ok=False).stdout)
        self.assertFalse(report['staged'][0]['matchesWorkingTree'])

    def test_review_cannot_include_foreign_staged_file(self):
        self.fixture.write('foreign.txt', 'other contributor draft\n')
        self.fixture.start()
        self.fixture.run_git('add', 'foreign.txt')
        report = json.loads(self.cli('review', '--include', 'foreign.txt', ok=False).stdout)
        self.assertTrue(any('Staged protected foreign' in e for e in report['errors']))

    def test_review_requires_explicit_support_scope_and_handles_spaces(self):
        self.fixture.start()
        name = 'docs/owned support file.md'
        self.fixture.write(name, 'supporting observation\n')
        self.fixture.run_git('add', name)
        self.cli('review', ok=False)
        report = json.loads(self.cli('review', '--include', name).stdout)
        self.assertTrue(report['staged'][0]['matchesWorkingTree'])

    def test_review_claim_evidence_is_in_scope_but_changed_bytes_fail(self):
        self.fixture.start()
        self.fixture.record_claim(self.fixture.claim())
        name = 'implementation/warlock/qa/evidence/result.json'
        self.fixture.run_git('add', name)
        self.cli('review')
        self.fixture.write(name, {'changed': 'after observation'})
        self.cli('review', ok=False)

    def test_review_staged_delete_must_match_current_working_tree(self):
        self.fixture.start()
        name = 'implementation/warlock/src/Desktop.elm'
        self.fixture.run_git('rm', '--cached', name)
        self.cli('review', ok=False)
        (self.repo / name).unlink()
        report = json.loads(self.cli('review').stdout)
        self.assertIsNone(report['staged'][0]['stagedSha256'])
        self.assertIsNone(report['staged'][0]['workingSha256'])

    def test_review_rejects_symlink_archival_include_and_missing_record(self):
        self.cli('review', ok=False)
        self.fixture.start()
        self.cli('review', '--include', '../outside', ok=False)
        self.cli('review', '--include', 'implementation/warlock-preview-provider-v143/frozen.txt', ok=False)
        name = 'docs/symlink.md'
        (self.repo / name).symlink_to(self.repo / 'foreign.txt')
        self.fixture.run_git('add', name)
        self.cli('review', '--include', name, ok=False)

    def test_review_empty_index_is_an_advisory(self):
        self.fixture.start()
        report = json.loads(self.cli('review').stdout)
        self.assertEqual(report['staged'], [])
        self.assertTrue(any('Nothing is staged' in w for w in report['warnings']))





class DeliveryEditPrecheckTests(unittest.TestCase):
    """Eight finite edit-boundary counterexamples; no process/native execution."""
    def setUp(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from test_delivery_flow import engine
        self.m=engine();self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'.warlock-contributor').mkdir()
        self.runner='.warlock-contributor/runner.py';(self.root/self.runner).write_text('tested bytes')
        self.record={'schema':1,'owner':'root','slice':{'id':'fixture','paths':[self.runner]},
            '_recordPath':'.warlock-contributor/fixture.json','delivery':{'events':[]}}
        self.candidate={'scope':'cpu','argv':['fixed'],'manifest':{role:{self.runner:'a'*64}for role in ('sources','fixtures','runners','profiles')}}
        self.view={'candidate':self.candidate,'candidateSha256':'b'*64,'job':None,'terminal':None,
                   'review':{'disposition':'accepted'},'refusal':None}
        self.record['delivery']['events']=[{'kind':'candidate','candidateSha256':'b'*64,'candidate':self.candidate}]
        self.state={'activeContributorRecord':self.record['_recordPath'],'activeSlice':self.record['slice'],
            'activeSelection':{'generation':1,'recordIdentitySha256':self.m.record_identity(self.record,self.record['_recordPath']),
                               'selectedUTC':'2026-11-08T00:00:00Z'}}
        self.addCleanup(patch.stopall)
        patch.object(self.m,'delivery_state',side_effect=lambda *args:self.view).start()

    def launch(self):
        receipt={'record':self.record['_recordPath'],'candidateSha256':'b'*64,'selection':1,
                 'scope':'cpu','pid':123,'startTicks':'77','argv':['fixed'],'acceptanceInferred':False}
        return self.m.record_delivery_launch(self.root,self.record,{},receipt)

    def check(self,paths=None,selection=1):
        return self.m.validate_delivery_edit_precheck(self.root,self.record,{},self.state,selection,
                                                     [self.runner]if paths is None else paths)

    def close(self,consumed,job='pid123-start77',sha='b'*64):
        self.record['delivery']['events'] += [
            {'kind':'execution-started','candidateSha256':sha,'jobId':job,'outerHandle':'outer'},
            {'kind':'execution-finished','candidateSha256':sha,'jobId':job,'outerHandleConsumed':consumed}]

    def test_actual_launch_journal_blocks_without_any_canonical_started(self):
        self.launch();self.assertFalse(any(x['kind']=='execution-started'for x in self.record['delivery']['events']))
        with self.assertRaisesRegex(ValueError,'unclosed launched job'):self.check()
        self.assertEqual((self.root/self.runner).read_text(),'tested bytes')

    def test_canonical_started_without_journal_still_blocks(self):
        self.view['job']={'jobId':'legacy','consumed':False}
        with self.assertRaisesRegex(ValueError,'unclosed canonical job'):self.check()

    def test_outer_completion_or_process_exit_is_not_canonical_consumption(self):
        self.launch();self.record['observedOuter']={'exit':0,'consumed':True,'pidAbsent':True}
        with self.assertRaisesRegex(ValueError,'unclosed launched job'):self.check()

    def test_terminal_without_consumption_blocks_then_exact_consumption_releases(self):
        self.launch();self.close(False)
        with self.assertRaises(ValueError):self.check()
        self.record['delivery']['events'].append({'kind':'execution-consumed','jobId':'pid123-start77','outerHandle':'outer'})
        self.assertTrue(self.check()['structuralPrecheckPassed'])

    def test_stale_selection_refuses_before_any_journal_or_disjoint_write(self):
        self.state['activeSelection']['generation']=2
        with self.assertRaisesRegex(ValueError,'selection differs'):self.check(['.warlock-contributor/new-terminal.json'])
        self.assertFalse((self.root/'.warlock-contributor/new-terminal.json').exists())

    def test_ready_review_with_no_launched_job_needs_no_new_refusal_event(self):
        self.assertTrue(self.check()['structuralPrecheckPassed'])
        self.assertEqual(self.record['delivery']['events'][0]['kind'],'candidate')
        self.assertEqual(len(self.record['delivery']['events']),1)

    def test_idempotent_no_byte_change_and_disjoint_terminal_evidence_stay_available(self):
        self.launch();before=(self.root/self.runner).read_bytes()
        self.assertTrue(self.check([])['structuralPrecheckPassed'])
        self.assertTrue(self.check(['.warlock-contributor/new-terminal.json'])['structuralPrecheckPassed'])
        self.assertEqual((self.root/self.runner).read_bytes(),before)

    def test_unrelated_candidate_or_job_terminal_does_not_release_actual_launch(self):
        self.launch();self.close(True,job='pid999-start88')
        with self.assertRaises(ValueError):self.check()
        self.close(True,sha='c'*64)
        with self.assertRaises(ValueError):self.check()




class CanonicalSelectionStateTests(unittest.TestCase):
    """Exact inverse of canonical selection; no custody or clock mutation."""
    def setUp(self):
        import tempfile
        from pathlib import Path
        from test_delivery_flow import engine
        self.m=engine();self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.path=self.root/self.m.STATE;self.path.parent.mkdir(parents=True)
        self.before={'schema':1,'sentinel':'unchanged foreign bytes','activeContributorRecord':'.warlock-contributor/older.json',
            'activeSlice':{'id':'older'},'activeSelection':{'generation':19,'recordIdentitySha256':'a'*64,'selectedUTC':'2026-11-08T00:00:00Z'},'sliceSelectionHistory':[]}
        self.record={'schema':1,'owner':'same-logical-owner','workflowPolicy':2,'_recordPath':'.warlock-contributor/new.json',
            'startedUTC':'2026-11-08T01:00:00Z','sourceRevision':'b'*40,'sourceHashes':{},'baseline':self.m.EXPECTED,
            'slice':{'id':'different-original','requirements':['ELM-UX-023'],'scenarios':['keyboard-launcher'],'paths':[],
                     'before':'before','after':'after','verification':['literal original']},
            'foreignDirty':{self.m.STATE:self.sha(self.before)},'adoptedDirty':{'paths':[],'ownershipNote':None},
            'delivery':{'clockOrigin':{'utc':'2026-11-08T01:00:00Z'}}}
        self.state=dict(self.before,activeContributorRecord=self.record['_recordPath'],activeSlice=self.record['slice'],
            activeSelection={'generation':20,'recordIdentitySha256':self.m.record_identity(self.record,self.record['_recordPath']),
                             'selectedUTC':'2026-11-08T01:00:02Z'},
            sliceSelectionHistory=[dict(atUTC='2026-11-08T01:00:01Z',**{k:self.before[k]for k in ('activeContributorRecord','activeSlice','activeSelection')})])
    def sha(self,value):
        import hashlib
        return hashlib.sha256((json.dumps(value,indent=2)+'\n').encode()).hexdigest()
    def proof(self):
        self.path.write_text(json.dumps(self.state,indent=2)+'\n')
        return self.m.canonical_selection_state_provenance(self.root,self.record)
    def test_exact_selection_delta_recognized_without_rewriting_custody(self):
        before=json.dumps(self.record,sort_keys=True)
        self.assertEqual(self.proof(),{self.m.STATE:self.sha(self.state)})
        overlay, errors, _ = self.m.protected_reconciliations(self.root,self.record)
        self.assertEqual(errors,[])
        self.assertEqual(overlay,{self.m.STATE:self.sha(self.state)})
        self.assertEqual(json.dumps(self.record,sort_keys=True),before)
    def test_other_state_field_drift_is_not_selection_provenance(self):
        self.state['sentinel']='unreviewed extra change';self.assertEqual(self.proof(),{})
    def test_wrong_active_record_or_slice_is_not_selection_provenance(self):
        self.state['activeContributorRecord']='.warlock-contributor/foreign.json';self.assertEqual(self.proof(),{})
        self.state['activeContributorRecord']=self.record['_recordPath'];self.state['activeSlice']={'id':'foreign'}
        self.assertEqual(self.proof(),{})
    def test_wrong_current_record_identity_is_not_selection_provenance(self):
        self.state['activeSelection']['recordIdentitySha256']='c'*64;self.assertEqual(self.proof(),{})
    def test_skipped_or_boolean_generation_is_not_selection_provenance(self):
        self.state['activeSelection']['generation']=21;self.assertEqual(self.proof(),{})
        self.state['activeSelection']['generation']=True;self.assertEqual(self.proof(),{})
    def test_history_and_chronology_drift_are_not_selection_provenance(self):
        self.state['sliceSelectionHistory'][0]['activeSlice']={'id':'laundered'};self.assertEqual(self.proof(),{})
        self.state['sliceSelectionHistory'][0]['activeSlice']=self.before['activeSlice']
        self.state['sliceSelectionHistory'][0]['atUTC']='2026-11-08T00:00:00Z';self.assertEqual(self.proof(),{})
    def test_unmatched_captured_foreign_baseline_is_not_selection_provenance(self):
        self.record['foreignDirty'][self.m.STATE]='d'*64
        self.state['activeSelection']['recordIdentitySha256']=self.m.record_identity(self.record,self.record['_recordPath'])
        self.assertEqual(self.proof(),{})
    def test_canonical_selection_from_absent_legacy_selection_fields(self):
        self.before.pop('activeContributorRecord');self.before.pop('activeSelection');self.before.pop('sliceSelectionHistory')
        self.record['foreignDirty'][self.m.STATE]=self.sha(self.before)
        self.state=dict(self.before,activeContributorRecord=self.record['_recordPath'],activeSlice=self.record['slice'],
            activeSelection={'generation':1,'recordIdentitySha256':self.m.record_identity(self.record,self.record['_recordPath']),
                             'selectedUTC':'2026-11-08T01:00:02Z'},
            sliceSelectionHistory=[{'atUTC':'2026-11-08T01:00:01Z','activeContributorRecord':None,
                                   'activeSlice':self.before['activeSlice'],'activeSelection':None}])
        self.assertEqual(self.proof(),{self.m.STATE:self.sha(self.state)})




class RootPluginSupportActorTests(unittest.TestCase):
    """Closed logical-Root binding retains real live AgentBus names and DIDs."""
    def setUp(self):
        import tempfile, datetime as dt
        from pathlib import Path
        from test_delivery_flow import engine
        from unittest.mock import patch
        self.patch=patch;self.dt=dt;self.m=engine();self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.names=set(self.m.ROOT_PLUGIN_REPAIR_PATHS)
        self.record={'schema':1,'owner':'root-agentbus','workflowPolicy':2,'_recordPath':self.m.ROOT_PLUGIN_REPAIR_RECORD,
            'foreignDirty':dict(self.m.ROOT_PLUGIN_REPAIR_BASELINE),'slice':{'id':'closedfixture'},'startedUTC':'2026-11-08T15:21:48.868426+00:00'}
        self.addCleanup(patch.stopall)
        # Calibrate the fixed case identifier to this finite fixture; realrecord
        # f532 and its exact frozen baselines are independently bound in review.
        patch.object(self.m,'ROOT_PLUGIN_REPAIR_IDENTITY',self.m.record_identity(self.record,self.record['_recordPath'])).start()
        now=dt.datetime.now(dt.timezone.utc);self.now=now
        self.did='did:key:z6MktqHDyXraPakaajyGEA15fCs783S1X1yzx6Bysxxk5yie'
        self.proof={'schema':1,'owner':self.record['owner'],'claimOwner':self.m.ROOT_PLUGIN_REPAIR_ACTOR,'run':'assigned-run',
            'observedUTC':(now-dt.timedelta(seconds=1)).isoformat(),'claims':[{'resource':'file:'+str(self.root/name),
              'holder':self.m.ROOT_PLUGIN_REPAIR_ACTOR,'holder_did':self.did,'lease_end':(now+dt.timedelta(minutes=10)).isoformat()}
              for name in sorted(self.names)]}
    def test_closed_live_actor_binding_preserves_logical_owner_and_calls_real_agent(self):
        with self.patch.object(self.m,'support_live_claims',return_value=self.proof['claims'])as live:
            self.m.confirm_support_claims(self.root,self.record,self.proof,self.names)
        live.assert_called_once_with(self.m.ROOT_PLUGIN_REPAIR_ACTOR,'assigned-run')
        self.assertTrue(self.names.isdisjoint(self.m.SUPPORT_CUSTODY_PATHS))
        self.assertEqual(self.record['owner'],'root-agentbus')
        self.assertEqual(self.record['foreignDirty'],self.m.ROOT_PLUGIN_REPAIR_BASELINE)
        rows=self.m.support_proof_rows(self.root,self.proof,self.record['owner'],self.now,claim_owner=self.m.ROOT_PLUGIN_REPAIR_ACTOR,record=self.record)
        self.assertEqual({row['holder_did']for row in rows.values()},{self.did})
    def test_closed_binding_refuses_unrelated_scope_and_unconfirmed_live_custody(self):
        import copy
        for label,change in [('record',lambda r,p:r.update(_recordPath='.warlock-contributor/other.json')),
             ('identity',lambda r,p:r.update(startedUTC='2000-01-01T00:00:00Z')),
             ('baseline',lambda r,p:r['foreignDirty'].update({next(iter(self.names)):'0'*64})),
             ('actor',lambda r,p:p.update(claimOwner='invented-alias')),
             ('resource',lambda r,p:p['claims'][0].update(resource='file:'+str(self.root/'docs/HANDOFF.md')))]:
            with self.subTest(label=label):
                record,proof=copy.deepcopy(self.record),copy.deepcopy(self.proof);change(record,proof)
                with self.assertRaises(ValueError):self.m.support_claim_owner(self.root,record,proof)
        wrong=copy.deepcopy(self.proof['claims']);wrong[0]['holder_did']='did:key:z6Mkm2Ryw8nxkXhQaBvHF8EKiLFrb14pNCgjWK8xjnaVeP27'
        with self.patch.object(self.m,'support_live_claims',return_value=wrong):
            with self.assertRaisesRegex(ValueError,'currently confirmed'):self.m.confirm_support_claims(self.root,self.record,self.proof,self.names)
        expired=copy.deepcopy(self.proof);expired['claims'][0]['lease_end']=(self.now-self.dt.timedelta(seconds=1)).isoformat()
        with self.patch.object(self.m,'support_live_claims')as live:
            with self.assertRaises(ValueError):self.m.confirm_support_claims(self.root,self.record,expired,self.names)
            live.assert_not_called()




class ProspectiveGapRecoveryTests(unittest.TestCase):
    """One calibrated closed fixture; all other renewals keep the prior-window bound."""
    def setUp(self):
        from test_delegated_authorization import DelegatedAuthorizationTests
        from unittest.mock import patch
        self.f = DelegatedAuthorizationTests('test_actual_delegated_decision_accepts_without_human_impersonation')
        self.f.setUp(); self.addCleanup(self.f.doCleanups)
        f = self.f
        f.evidence['authorizedUTC'] = '2026-01-01T06:00:00Z'
        f.goal['observedUTC'] = '2026-01-01T06:00:01Z'
        f.event['atUTC'] = '2026-01-01T06:00:02Z'
        f.evidence['authorizationExpiresUTC'] = '2026-01-01T07:00:00Z'
        f.event['authorizationExpiresUTC'] = f.evidence['authorizationExpiresUTC']
        f.request['choices'][0]['payload']['proposedUntilUTC'] = f.event['authorizationExpiresUTC']
        f.answer['requestSha256'] = f.module.json_sha256(f.request)
        f.terminal['actualResult']['result'] = json.dumps(f.answer)
        f.decision.update(f.answer, selectedChoice=f.request['choices'][0], actualTerminal=f.ref('terminal', f.terminal))
        self.case = {'recordPath': f.record['_recordPath'],
            'recordIdentitySha256': f.module.record_identity(f.record, f.record['_recordPath']),
            'previousExpiresUTC': f.evidence['previousExpiresUTC'],
            'authorizationExpiresUTC': f.event['authorizationExpiresUTC'],
            'notAfterUTC': f.policy['notAfterUTC'], 'humanDelegationSha256': f.grantref['sha256'],
            'requestSha256': f.module.json_sha256(f.request), 'answerSha256': f.module.json_sha256(f.answer),
            'terminalSha256': f.decision['actualTerminal']['sha256']}
        held = patch.object(f.module, 'UX023_PROSPECTIVE_GAP_RECOVERY', dict(self.case), create=True)
        held.start(); self.addCleanup(held.stop)

    def test_exact_prospective_gap_retains_history_and_accepts(self):
        import copy
        before = copy.deepcopy(self.f.record)
        self.assertEqual(self.f.validate(), self.f.evidence['authorizedUTC'])
        self.assertEqual(self.f.record, before)

    def test_other_record_identity_and_prior_deadline_refuse(self):
        from unittest.mock import patch
        for key in ('recordPath', 'recordIdentitySha256', 'previousExpiresUTC'):
            with self.subTest(key=key), patch.dict(self.f.module.UX023_PROSPECTIVE_GAP_RECOVERY, {key: 'different'}):
                with self.assertRaises(ValueError): self.f.validate()

    def test_different_request_answer_terminal_or_grant_refuses(self):
        from unittest.mock import patch
        for key in ('requestSha256', 'answerSha256', 'terminalSha256', 'humanDelegationSha256'):
            with self.subTest(key=key), patch.dict(self.f.module.UX023_PROSPECTIVE_GAP_RECOVERY, {key: '0'*64}):
                with self.assertRaises(ValueError): self.f.validate()

    def test_different_selected_expiry_or_cap_refuses(self):
        from unittest.mock import patch
        for key in ('authorizationExpiresUTC', 'notAfterUTC'):
            with self.subTest(key=key), patch.dict(self.f.module.UX023_PROSPECTIVE_GAP_RECOVERY, {key: 'different'}):
                with self.assertRaises(ValueError): self.f.validate()

    def test_unmatched_late_renewal_keeps_default_previous_two_hour_guard(self):
        self.f.module.UX023_PROSPECTIVE_GAP_RECOVERY.clear()
        with self.assertRaises(ValueError): self.f.validate()

    def test_exact_case_cannot_waive_fresh_duration_or_hard_cap(self):
        self.f.evidence['authorizedUTC'] = '2026-01-01T04:59:59Z'
        with self.assertRaises(ValueError): self.f.validate()
        self.f.evidence['authorizedUTC'] = '2026-01-01T06:00:00Z'
        self.f.policy['notAfterUTC'] = '2026-01-01T06:59:59Z'
        self.f.module.UX023_PROSPECTIVE_GAP_RECOVERY['notAfterUTC'] = self.f.policy['notAfterUTC']
        with self.assertRaises(ValueError): self.f.validate()

    def test_exact_case_cannot_waive_actual_terminal_goal_or_scope(self):
        self.f.terminal['timedOut'] = True
        self.f.decision['actualTerminal'] = self.f.ref('terminal', self.f.terminal)
        with self.assertRaises(ValueError): self.f.validate()
        self.f.terminal['timedOut'] = False
        self.f.decision['actualTerminal'] = self.f.ref('terminal', self.f.terminal)
        self.f.goal['stopRequested'] = True
        with self.assertRaises(ValueError): self.f.validate()
        self.f.goal['stopRequested'] = False
        self.f.scopes['root']['claims'].append('new')
        with self.assertRaises(ValueError): self.f.validate()

    def test_exact_case_cannot_replay_or_waive_attempt_requirement(self):
        self.f.evidence['previousExpiresUTC'] = self.f.event['authorizationExpiresUTC']
        with self.assertRaises(ValueError): self.f.validate()
        self.f.evidence['previousExpiresUTC'] = self.case['previousExpiresUTC']
        self.f.record['delivery']['events'] = []
        self.f.event['sequence'] = 1
        with self.assertRaises(ValueError): self.f.validate()




class QualifiedGapAuditEntryTests(unittest.TestCase):
    """Provenance errors refuse before any canonical mutation or product command."""
    def setUp(self):
        import tempfile, datetime as dt
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import patch
        from test_delivery_flow import engine
        self.m = engine(); self.patch = patch; self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.record = {'schema': 1, 'owner': 'root-agentbus', 'startedUTC': '2026-11-08T15:21:48.868426+00:00', 'delivery': {'events': []}}
        self.record['_recordPath'] = self.m.UX023_PROSPECTIVE_GAP_RECOVERY['recordPath']
        self.args = SimpleNamespace(record=self.record['_recordPath'], expect_selection=20, command='delivery-event', event_file='event.json', path=list(self.m.ROOT_PLUGIN_REPAIR_PATHS))
        self.checker = 'a'*64; self.base = self.m.UX023_QUALIFIED_BASE_CORE
        self.event = {'eventId': 'actual-closure', 'kind': 'execution-started', 'candidateSha256': self.m.UX023_CLOSED_NATIVE[0], 'jobId': self.m.UX023_CLOSED_NATIVE[1], 'outerHandle': '55475'}
        self.write('event.json', self.event)
        self.case = dict(self.m.UX023_PROSPECTIVE_GAP_RECOVERY, recordIdentitySha256=self.m.record_identity(self.record, self.args.record), authorizationExpiresUTC=(dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=5)).isoformat())
        held = patch.object(self.m, 'UX023_PROSPECTIVE_GAP_RECOVERY', self.case); held.start(); self.addCleanup(held.stop)
        self.claims = patch.object(self.m, 'confirm_support_claims'); self.live = self.claims.start(); self.addCleanup(self.claims.stop)
        self.inputs = {'candidatePlugin': {'sha256': 'candidate-snapshot', 'files': {'plugins/warlock-contributor/scripts/warlock.py': self.checker, 'plugins/warlock-contributor/qa/test_delivery.py': 'b'*64}}}
        self.report = {'passed': True, 'exit': 0, 'primarySourceUnchanged': True, 'fullRegressionTests': 557, 'comparisonTestExecutions': 16, 'candidatePluginSha256': 'candidate-snapshot', 'commands': [{'exit': 0}]*4}
        self.goal = {'schema': 1, 'status': 'active', 'observedUTC': dt.datetime.now(dt.timezone.utc).isoformat(), 'goalDefinition': {'threadId': '01a1ad00-8273-7e90-84cd-e8528d5a99c3', 'createdAt': 1794094624, 'objectiveSha256': '53689bf07ab5d5c8a603e828651dc7c63f52496ccf2eacacd0848ca320a8947a'}, 'humanPaused': False, 'humanHandoff': False, 'stopRequested': False}
        self.descriptor = {'schema': 1, 'checkerSha256': self.checker, 'baselineCoreSha256': self.base, 'recordIdentitySha256': self.case['recordIdentitySha256'], 'rulingAnswerSha256': self.case['answerSha256'], 'testDeliverySha256': 'b'*64, 'auditEvents': {'authorization-renewed': '0'*64, 'execution-started': self.m.json_sha256(self.event), 'execution-finished': '0'*64}}
        self.refresh()

    def write(self, name, value):
        import hashlib
        path = self.root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value))
        return {'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    def refresh(self):
        d = self.descriptor
        d['qualificationInputs'] = self.write('inputs.json', self.inputs)
        d['qualificationReport'] = self.write('report.json', self.report)
        self.receipt = {'schema': 1, 'completed': True, 'exit': 0, 'outerHandleConsumed': True, 'outerHandle': 'qualified-outer', 'protectedScope': 'qa-harness-fixed', 'report': d['qualificationReport'], 'inputs': d['qualificationInputs'], 'checkerSha256': self.checker}
        d['qualificationReceipt'] = self.write('receipt.json', self.receipt)
        self.review = {'scope': 'ux023-qualified-audit-entry', 'disposition': 'accepted', 'reviewer': 'workflow_astra', 'checkerSha256': self.checker, 'qualificationReportSha256': d['qualificationReport']['sha256'], 'qualificationReceiptSha256': d['qualificationReceipt']['sha256'], 'qualificationInputsSha256': d['qualificationInputs']['sha256'], 'auditEventsSha256': self.m.json_sha256(d['auditEvents'])}
        d['independentReview'] = self.write('review.json', self.review)
        d['goalObservation'] = self.write('goal.json', self.goal)
        self.proof = {'claims': [{'resource': 'file:' + str(self.root/name)} for name in sorted(self.m.ROOT_PLUGIN_REPAIR_PATHS)]}
        d['claimProof'] = self.write('claims.json', self.proof)
        self.write(self.m.UX023_QUALIFIED_ADOPTION, d)

    def validate(self):
        return self.m.validate_ux023_qualified_audit_entry(self.root, self.record, self.args, self.checker, self.base)

    def test_exact_qualified_audit_calls_live_claim_check_without_writes(self):
        before = (self.root/'event.json').read_bytes(); self.validate()
        self.live.assert_called_once_with(self.root, self.record, self.proof, self.m.ROOT_PLUGIN_REPAIR_PATHS)
        self.assertEqual(before, (self.root/'event.json').read_bytes())

    def test_missing_descriptor_and_mismatched_self_base_record_refuse(self):
        path = self.root/self.m.UX023_QUALIFIED_ADOPTION; path.unlink()
        with self.assertRaises((ValueError, OSError)): self.validate()
        self.refresh()
        for key in ('checkerSha256', 'baselineCoreSha256', 'recordIdentitySha256', 'rulingAnswerSha256'):
            with self.subTest(key=key):
                old = self.descriptor[key]; self.descriptor[key] = 'wrong'; self.write(self.m.UX023_QUALIFIED_ADOPTION, self.descriptor)
                with self.assertRaises(ValueError): self.validate()
                self.descriptor[key] = old

    def test_missing_or_wrong_review_and_qualification_refuse(self):
        for key, value in [('fullRegressionTests', 553), ('passed', False), ('comparisonTestExecutions', 0)]:
            old = self.report[key]; self.report[key] = value; self.refresh()
            with self.subTest(key=key), self.assertRaises(ValueError): self.validate()
            self.report[key] = old
        self.refresh(); self.review['reviewer'] = 'root-agentbus'; self.descriptor['independentReview'] = self.write('review.json', self.review); self.write(self.m.UX023_QUALIFIED_ADOPTION, self.descriptor)
        with self.assertRaises(ValueError): self.validate()

    def test_unconsumed_or_nonprotected_qualification_refuses(self):
        for key, value in [('outerHandleConsumed', False), ('protectedScope', 'ordinary-shell')]:
            self.refresh(); self.receipt[key] = value; self.descriptor['qualificationReceipt'] = self.write('receipt.json', self.receipt)
            self.review['qualificationReceiptSha256'] = self.descriptor['qualificationReceipt']['sha256']; self.descriptor['independentReview'] = self.write('review.json', self.review); self.write(self.m.UX023_QUALIFIED_ADOPTION, self.descriptor)
            with self.subTest(key=key), self.assertRaises(ValueError): self.validate()

    def test_wrong_job_or_unapproved_event_and_ordinary_command_refuse(self):
        self.event['jobId'] = 'other-job'; self.descriptor['auditEvents']['execution-started'] = self.m.json_sha256(self.event); self.write('event.json', self.event); self.refresh()
        with self.assertRaises(ValueError): self.validate()
        self.args.command = 'record'
        with self.assertRaises(ValueError): self.validate()
        self.args.command = 'delivery-precheck'
        with self.assertRaises(ValueError): self.validate()

    def test_stale_goal_stop_and_live_claim_failure_refuse(self):
        import datetime as dt
        self.goal['observedUTC'] = (dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=61)).isoformat(); self.refresh()
        with self.assertRaises(ValueError): self.validate()
        self.goal['observedUTC'] = dt.datetime.now(dt.timezone.utc).isoformat(); self.goal['stopRequested'] = True; self.refresh()
        with self.assertRaises(ValueError): self.validate()
        self.goal['stopRequested'] = False; self.refresh(); self.live.side_effect = ValueError('expired broker authentication')
        with self.assertRaises(ValueError): self.validate()

    def test_edit_check_requires_consumed_closure_and_exact_pair(self):
        self.args.command = 'delivery-edit-precheck'
        with self.assertRaises(ValueError): self.validate()
        sha, job = self.m.UX023_CLOSED_NATIVE
        self.record['delivery']['events'] = [{'kind': 'execution-started', 'jobId': job, 'candidateSha256': sha, 'outerHandle': '55475'}, {'kind': 'execution-finished', 'jobId': job, 'candidateSha256': sha, 'outerHandleConsumed': True}]
        self.validate()
        self.args.path = [self.args.path[0]]
        with self.assertRaises(ValueError): self.validate()

    def test_missing_repair_claim_or_unrelated_support_claim_refuses(self):
        for proof in ({'claims': []}, {'claims': [{'resource': 'file:' + str(self.root/'docs/HANDOFF.md')}]},
                      {'claims': [{'resource': 'file:' + str(self.root/next(iter(self.m.ROOT_PLUGIN_REPAIR_PATHS)))}]}):
            self.descriptor['claimProof'] = self.write('claims.json', proof)
            self.write(self.m.UX023_QUALIFIED_ADOPTION, self.descriptor)
            self.live.reset_mock()
            with self.assertRaises(ValueError): self.validate()
            self.live.assert_not_called()

    def test_missing_test_digest_and_matching_absent_input_refuse(self):
        self.descriptor.pop('testDeliverySha256')
        self.inputs['candidatePlugin']['files'].pop('plugins/warlock-contributor/qa/test_delivery.py')
        self.refresh()
        with self.assertRaises(ValueError): self.validate()

    def test_validated_event_object_survives_later_file_replacement(self):
        returned = self.validate()
        self.write('event.json', dict(self.event, jobId='replacement-job'))
        self.assertEqual(returned, self.event)
        import inspect
        self.assertIn('event = qualified_event if qualified_audit else read(safe(root, args.event_file))', inspect.getsource(self.m.main))

    def test_main_default_guard_and_locked_route_are_explicit(self):
        import ast, inspect
        tree = ast.parse(inspect.getsource(self.m.main)); calls = [x for x in ast.walk(tree) if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == 'validate_ux023_qualified_audit_entry']
        self.assertEqual(len(calls), 2)
        text = inspect.getsource(self.m.main)
        self.assertIn("args.command not in ('delivery-event', 'delivery-edit-precheck')", text)
        self.assertIn("with delivery_edit_lock(root,args.record):", text)




class ClosedHistoricalIntegrationTests(unittest.TestCase):
    def setUp(self):
        import tempfile, hashlib
        from pathlib import Path
        from unittest.mock import patch
        from test_delivery_flow import engine
        self.m=engine();self.patch=patch;self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.core='plugins/warlock-contributor/scripts/warlock.py';self.test='plugins/warlock-contributor/qa/test_delivery.py'
        self.write(self.core,Path(self.m.__file__).read_bytes());self.write(self.test,b'new test bytes')
        self.sources={}
        for i in range(3):
            name='implementation/warlock/src/Focus'+str(i)+'.elm';self.write(name,b'current product');self.sources[name]=self.digest(self.root/name)
        for name in ('fixture','runner','profile','prerequisite.json'):self.write(name,b'{}')
        self.candidate={'id':'closed-fixture','scope':'native','argv':['fixed'],'expectedObservation':'original','nativePrerequisites':[self.ref('prerequisite.json')],'manifest':{'sources':dict(self.sources),'fixtures':{'fixture':self.digest(self.root/'fixture')},'runners':{self.core:'a'*64,'runner':self.digest(self.root/'runner')},'profiles':{'profile':self.digest(self.root/'profile')}}}
        self.record={'schema':1,'workflowPolicy':2,'owner':'root-agentbus','startedUTC':'2026-11-08T15:21:48.868426+00:00','slice':{'paths':list(self.sources)},'_recordPath':self.m.UX023_CLOSED_INTEGRATION['recordPath'],'delivery':{'schema':1,'journey':{},'clockOrigin':{},'authorizationExpiresUTC':'2026-11-09T04:45:00Z','guardHashes':{},'events':[]}}
        self.case=dict(self.m.UX023_CLOSED_INTEGRATION,recordIdentitySha256=self.m.record_identity(self.record,self.record['_recordPath']),candidateSha256=self.m.json_sha256(self.candidate),oldCore='a'*64,recoveredCore='b'*64,recoveredTest='c'*64,revision='d'*40)
        self.actual={'candidate':self.candidate,'candidateSha256':self.case['candidateSha256'],'job':{'jobId':self.case['jobId'],'outerHandle':'55475','consumed':True},'terminal':{'classification':'pass','exit':0},'integrated':None}
        self.event={'kind':'integrated','candidateSha256':self.case['candidateSha256'],'revision':self.case['revision']}
        self.record['delivery']['events']=[{'kind':'execution-finished','candidateSha256':self.case['candidateSha256'],'jobId':self.case['jobId'],'outerHandleConsumed':True,'report':{'sha256':self.case['terminalSha256']}}]
        self.report={'passed':True,'exit':0,'primarySourceUnchanged':True,'fullRegressionTests':557,'comparisonTestExecutions':16,'commands':[{'exit':0}]*4}
        self.write('qualification.json',json.dumps(self.report).encode());self.case['qualificationReportSha256']=self.digest(self.root/'qualification.json')
        self.descriptor={'schema':1,'checkerSha256':self.case['recoveredCore'],'testDeliverySha256':self.case['recoveredTest'],'recordIdentitySha256':self.case['recordIdentitySha256'],'qualificationReport':self.ref('qualification.json'),'qualificationReceipt':self.put('receipt.json',{'completed':True,'exit':0,'outerHandleConsumed':True,'checkerSha256':self.case['recoveredCore']})}
        self.descriptor['independentReview']=self.put('review.json',{'scope':'ux023-qualified-audit-entry','disposition':'accepted','reviewer':'workflow_astra','checkerSha256':self.case['recoveredCore'],'qualificationReportSha256':self.case['qualificationReportSha256'],'qualificationReceiptSha256':self.descriptor['qualificationReceipt']['sha256']})
        self.put(self.m.UX023_QUALIFIED_ADOPTION,self.descriptor)
        self.overlay={self.core:self.digest(self.root/self.core),self.test:self.digest(self.root/self.test)}
        self.chain={'events':[{'path':self.core,'fromSha256':self.case['oldCore'],'toSha256':self.case['recoveredCore']},{'path':self.core,'fromSha256':self.case['recoveredCore'],'toSha256':self.overlay[self.core]},{'path':self.test,'fromSha256':self.case['recoveredTest'],'toSha256':self.overlay[self.test]}]}
        for held in (patch.object(self.m,'UX023_CLOSED_INTEGRATION',self.case),patch.object(self.m,'support_reconciliations',return_value=(self.overlay,[],self.chain)),patch.object(self.m,'git',side_effect=self.git)):
            held.start();self.addCleanup(held.stop)
    def write(self,name,value):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value)
    def digest(self,path):
        import hashlib
        return hashlib.sha256(path.read_bytes()).hexdigest()
    def ref(self,name):return {'path':name,'sha256':self.digest(self.root/name)}
    def put(self,name,value):self.write(name,json.dumps(value).encode());return self.ref(name)
    def git(self,root,*args):
        if args[0]=='ls-tree':return ('100644 blob blob-id\t'+args[-1]+'\n').encode()
        if args[0]=='cat-file':return b'current product'
        raise AssertionError(args)
    def check(self):return self.m.validate_ux023_closed_historical_integration(self.root,self.record,self.actual,self.event)
    def test_exact_closed_provenance_accepts_without_candidate_mutation(self):
        import copy
        before=copy.deepcopy(self.candidate);self.assertTrue(self.check());self.assertEqual(self.candidate,before)
    def test_default_current_candidate_guard_still_refuses_old_runner(self):
        with self.assertRaisesRegex(ValueError,'input changed'):self.m.validate_delivery_candidate(self.root,self.record,self.candidate,current=True)
        self.assertTrue(self.check())
    def test_other_record_candidate_revision_or_event_never_uses_exception(self):
        for key,value in [('recordPath','other'),('candidateSha256','0'*64),('revision','0'*40)]:
            old=self.case[key];self.case[key]=value
            with self.subTest(key=key):self.assertFalse(self.check())
            self.case[key]=old
        for kind in ('review','journey-observed','execution-started'):
            self.event['kind']=kind;self.assertFalse(self.check())
    def test_unconsumed_failed_wrong_job_or_terminal_refuses(self):
        self.actual['job']['consumed']=False
        with self.assertRaises(ValueError):self.check()
        self.actual['job']['consumed']=True;self.actual['terminal']['classification']='failed'
        with self.assertRaises(ValueError):self.check()
        self.actual['terminal']['classification']='pass';self.actual['job']['jobId']='different'
        with self.assertRaises(ValueError):self.check()
        self.actual['job']['jobId']=self.case['jobId'];self.record['delivery']['events'][0]['report']['sha256']='0'*64
        with self.assertRaises(ValueError):self.check()
    def test_any_other_runner_fixture_profile_or_product_drift_refuses(self):
        for name in ('runner','fixture','profile',next(iter(self.sources))):
            old=(self.root/name).read_bytes();self.write(name,b'drift')
            with self.subTest(name=name),self.assertRaises(ValueError):self.check()
            self.write(name,old)
    def test_missing_or_unreconciled_exact_support_chain_refuses(self):
        old=list(self.chain['events']);self.chain['events']=old[1:]
        with self.assertRaises(ValueError):self.check()
        self.chain['events']=old;self.overlay[self.test]='0'*64
        with self.assertRaises(ValueError):self.check()
    def test_wrong_qualified_version_report_or_independent_review_refuses(self):
        self.descriptor['checkerSha256']='0'*64;self.put(self.m.UX023_QUALIFIED_ADOPTION,self.descriptor)
        with self.assertRaises(ValueError):self.check()
        self.descriptor['checkerSha256']=self.case['recoveredCore'];self.descriptor['qualificationReport']['sha256']='0'*64;self.put(self.m.UX023_QUALIFIED_ADOPTION,self.descriptor)
        with self.assertRaises(ValueError):self.check()
    def test_nonregular_or_different_committed_product_blob_refuses(self):
        with self.patch.object(self.m,'git',return_value=b'120000 blob bad\tname\n'):
            with self.assertRaises(ValueError):self.check()
        with self.patch.object(self.m,'git',side_effect=lambda root,*args:self.git(root,*args)if args[0]=='ls-tree'else b'otherblob'):
            with self.assertRaises(ValueError):self.check()
    def test_wrong_current_authorization_or_owned_source_set_refuses(self):
        self.record['delivery']['authorizationExpiresUTC']='2026-11-09T05:05:00Z'
        with self.assertRaises(ValueError):self.check()
        self.record['delivery']['authorizationExpiresUTC']=self.case['authorizationExpiresUTC'];self.record['slice']['paths'].append('other')
        with self.assertRaises(ValueError):self.check()
    def test_main_exception_is_only_in_integrated_branch(self):
        import ast,inspect
        source=inspect.getsource(self.m.main);tree=ast.parse(source);calls=[x for x in ast.walk(tree)if isinstance(x,ast.Call)and isinstance(x.func,ast.Name)and x.func.id=='validate_ux023_closed_historical_integration'];self.assertEqual(len(calls),1)
        self.assertIn("event['kind'] == 'integrated' and validate_ux023_closed_historical_integration",source)


if __name__ == '__main__':
    unittest.main()

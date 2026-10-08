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

    def test_cpp_and_hpp_changes_count_as_authored_progress(self):
        for extension in ('.cpp', '.hpp'):
            with self.subTest(extension=extension):
                if (self.repo / '.warlock-contributor/slice.json').exists():
                    self.fixture.run_git('add', 'implementation/warlock')
                    self.fixture.run_git('commit', '-qm', 'retain previous native fixture')
                    (self.repo / '.warlock-contributor/slice.json').rename(self.repo / '.warlock-contributor/previous.json')
                self.start_native(extension)
                self.cli('record', '--outcome', 'production-fix', '--summary', 'native behavior changed')
                record = json.loads((self.repo / '.warlock-contributor/slice.json').read_text())
                self.assertTrue(record['iterations'][-1]['meaningfulProgress'])
                self.assertEqual(record['iterations'][-1]['progressPolicy'], 2)
                self.cli('check')

    def test_legacy_cpp_progress_assertion_remains_valid(self):
        self.start_native('.cpp')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'native behavior changed')
        path = self.repo / '.warlock-contributor/slice.json'
        record = json.loads(path.read_text())
        record['iterations'][-1].pop('progressPolicy')
        record['iterations'][-1]['meaningfulProgress'] = False
        self.fixture.write(str(path.relative_to(self.repo)), record)
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


if __name__ == '__main__':
    unittest.main()

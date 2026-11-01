"""A fresh participant record must not erase a same-scenario stop."""
import json
import fcntl
import datetime as dt
import importlib.util
import os
import subprocess
import sys
import time
import unittest

import test_warlock as fixtures

_spec = importlib.util.spec_from_file_location('stop_continuity_policy', fixtures.CHECKER)
_policy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_policy)


class StopContinuityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli

    def stop_current_record(self):
        self.fixture.start()
        for _ in range(2):
            self.cli('record', '--outcome', 'qualification', '--summary', 'No original-scenario observation')
        return (self.repo/'.warlock-contributor/slice.json').read_bytes()

    def prospective_slice(self, scenario, slice_id):
        selected = dict(self.fixture.slice)
        selected.update(id=slice_id, scenarios=[scenario])
        path = self.fixture.write('.warlock-contributor/'+slice_id+'.json', selected)
        return path.relative_to(self.repo).as_posix()

    def test_preflight_reports_prior_stopped_same_scenario_without_writing(self):
        original = self.stop_current_record()
        plan = self.prospective_slice('restore-pending', 'same-scenario-next')
        result = self.cli('--record', '.warlock-contributor/next.json', 'preflight',
                          '--slice-file', plan, ok=False)
        packet = json.loads(result.stdout)
        self.assertFalse(packet['canStartCleanDraft'])
        self.assertEqual(len(packet['priorStoppedRecords']), 1)
        self.assertEqual(packet['priorStoppedRecords'][0]['overlappingOriginals'], [
            {'requirement': 'ELM-UI-007', 'scenario': 'restore-pending'}])
        self.assertEqual((self.repo/'.warlock-contributor/slice.json').read_bytes(), original)
        self.assertFalse((self.repo/'.warlock-contributor/next.json').exists())

    def test_start_refuses_timer_reset_and_preserves_prior_record_bytes(self):
        original = self.stop_current_record()
        plan = self.prospective_slice('restore-pending', 'same-scenario-next')
        result = self.cli('--record', '.warlock-contributor/next.json', 'start',
                          '--owner', 'new-contributor', '--slice-file', plan, ok=False)
        packet = json.loads(result.stdout)
        self.assertTrue(any('prior stopped record' in error for error in packet['errors']))
        self.assertEqual((self.repo/'.warlock-contributor/slice.json').read_bytes(), original)
        self.assertFalse((self.repo/'.warlock-contributor/next.json').exists())

    def test_independent_original_scenario_can_start(self):
        self.stop_current_record()
        original = next(row for row in self.fixture.original['requirements']
                        if row['id'] == 'ELM-UI-007')
        other = next(row['name'] for row in original['scenarios']
                     if row['name'] != 'restore-pending')
        plan = self.prospective_slice(other, 'independent-scenario')
        preflight = json.loads(self.cli('--record', '.warlock-contributor/other.json',
                                        'preflight', '--slice-file', plan).stdout)
        self.assertEqual(preflight['priorStoppedRecords'], [])
        self.assertTrue(preflight['canStartCleanDraft'])
        started = json.loads(self.cli('--record', '.warlock-contributor/other.json',
                                      'start', '--owner', 'independent-contributor',
                                      '--slice-file', plan).stdout)
        self.assertEqual(started['slice']['scenarios'], [other])
        self.assertTrue((self.repo/'.warlock-contributor/slice.json').exists())

    def test_new_records_are_restricted_to_the_inventoried_directory(self):
        plan = self.prospective_slice('restore-pending', 'outside-inventory')
        record = '.warlock-contributor/nested/next.json'
        preflight = self.cli('--record', record, 'preflight', '--slice-file', plan, ok=False)
        packet = json.loads(preflight.stdout)
        self.assertTrue(any('direct .json children' in error for error in packet['errors']))
        started = self.cli('--record', record, 'start', '--owner', 'new-contributor',
                           '--slice-file', plan, ok=False)
        self.assertTrue(any('direct .json children' in error for error in json.loads(started.stdout)['errors']))
        self.assertFalse((self.repo/record).exists())

    def test_unreadable_unrelated_json_warns_but_does_not_block_other_scenarios(self):
        self.stop_current_record()
        original = next(row for row in self.fixture.original['requirements']
                        if row['id'] == 'ELM-UI-007')
        other = next(row['name'] for row in original['scenarios']
                     if row['name'] != 'restore-pending')
        self.fixture.write('.warlock-contributor/unrelated.json', '{ malformed')
        plan = self.prospective_slice(other, 'independent-with-unreadable-file')
        packet = json.loads(self.cli('--record', '.warlock-contributor/other.json',
                                     'preflight', '--slice-file', plan).stdout)
        self.assertTrue(packet['canStartCleanDraft'])
        self.assertEqual(packet['historyWarnings'], ['.warlock-contributor/unrelated.json'])
        self.assertTrue(any('inspect these paths' in warning for warning in packet['warnings']))
        started = self.cli('--record', '.warlock-contributor/other.json', 'start',
                           '--owner', 'independent-contributor', '--slice-file', plan)
        self.assertIn('.warlock-contributor/unrelated.json', started.stdout)
        self.assertTrue((self.repo/'.warlock-contributor/other.json').is_file())

    def test_unreadable_json_prevents_claiming_a_complete_initial_inventory(self):
        self.fixture.write('.warlock-contributor/unclassified.json', '{ incomplete')
        plan = self.prospective_slice('restore-pending', 'bootstrap-must-be-complete')
        result = self.cli('--record', '.warlock-contributor/new.json', 'start',
                          '--owner', 'new-contributor', '--slice-file', plan, ok=False)
        self.assertIn('Participant history inventory is incomplete', json.loads(result.stdout)['errors'][0])
        self.assertFalse((self.repo/'.warlock-contributor/participant-index.json').exists())
        self.assertFalse((self.repo/'.warlock-contributor/new.json').exists())

    def test_corrupted_indexed_participant_history_blocks_fresh_start(self):
        self.stop_current_record()
        index_path = self.repo/'.warlock-contributor/participant-index.json'
        index = json.loads(index_path.read_text())
        self.assertIn('.warlock-contributor/slice.json', index['records'])
        original_path = self.repo/'.warlock-contributor/slice.json'
        original_path.write_text('{ truncated participant history')
        plan = self.prospective_slice('restore-pending', 'must-not-reset-corrupt-history')
        preflight = self.cli('--record', '.warlock-contributor/next.json', 'preflight',
                             '--slice-file', plan, ok=False)
        packet = json.loads(preflight.stdout)
        self.assertFalse(packet['canStartCleanDraft'])
        self.assertTrue(any('Indexed participant history is unreadable' in error
                            for error in packet['historyErrors']))
        started = self.cli('--record', '.warlock-contributor/next.json', 'start',
                           '--owner', 'new-contributor', '--slice-file', plan, ok=False)
        self.assertIn('Participant history inventory is incomplete',
                      json.loads(started.stdout)['errors'][0])
        self.assertFalse((self.repo/'.warlock-contributor/next.json').exists())

    def test_mutated_indexed_iterations_block_erasing_a_stop(self):
        self.stop_current_record()
        record_path = self.repo/'.warlock-contributor/slice.json'
        record = json.loads(record_path.read_text())
        record['iterations'] = []
        record_path.write_text(json.dumps(record, indent=2)+'\n')
        plan = self.prospective_slice('restore-pending', 'must-not-erase-indexed-stop')
        result = self.cli('--record', '.warlock-contributor/next.json', 'start',
                          '--owner', 'new-contributor', '--slice-file', plan, ok=False)
        self.assertIn('participant bytes differ from indexed history',
                      json.loads(result.stdout)['errors'][0])
        self.assertFalse((self.repo/'.warlock-contributor/next.json').exists())

    def test_identity_only_legacy_index_cannot_silently_bind_mutated_history(self):
        self.stop_current_record()
        index_path = self.repo/'.warlock-contributor/participant-index.json'
        index = json.loads(index_path.read_text())
        del index['records']['.warlock-contributor/slice.json']['recordSha256']
        payload = {'schema': index['schema'], 'records': index['records']}
        index['indexSha256'] = _policy.json_sha256(payload)
        index_path.write_text(json.dumps(index, indent=2)+'\n')
        record_path = self.repo/'.warlock-contributor/slice.json'
        record = json.loads(record_path.read_text())
        record['iterations'] = []
        record_path.write_text(json.dumps(record, indent=2)+'\n')
        plan = self.prospective_slice('restore-pending', 'legacy-hashless-history')
        result = self.cli('--record', '.warlock-contributor/next.json', 'start',
                          '--owner', 'new-contributor', '--slice-file', plan, ok=False)
        self.assertIn('lacks an exact-byte binding', json.loads(result.stdout)['errors'][0])
        self.assertFalse((self.repo/'.warlock-contributor/next.json').exists())

    def test_duplicate_relocation_sources_cannot_collapse_to_one_destination(self):
        self.fixture.start()
        record = (self.repo/'.warlock-contributor/slice.json').read_bytes()
        duplicate = self.repo/'.warlock-contributor/duplicate.json'
        duplicate.write_bytes(record)
        self.cli('index-participants')
        (self.repo/'.warlock-contributor/slice.json').unlink()
        duplicate.unlink()
        destination = self.repo/'.warlock-contributor/moved.json'
        destination.write_bytes(record)
        plan = self.prospective_slice('restore-pending', 'ambiguous-relocation')
        result = self.cli('--record', '.warlock-contributor/next.json', 'start',
                          '--owner', 'new-contributor', '--slice-file', plan, ok=False)
        message = json.loads(result.stdout)['errors'][0]
        self.assertIn('no unique exact relocation', message)
        self.assertFalse((self.repo/'.warlock-contributor/next.json').exists())

    def test_invalid_requirement_identity_fails_closed_without_exception(self):
        self.stop_current_record()
        record_path = self.repo/'.warlock-contributor/slice.json'
        record = json.loads(record_path.read_text())
        record['slice']['requirements'] = [{}]
        record_path.write_text(json.dumps(record, indent=2)+'\n')
        plan = self.prospective_slice('restore-pending', 'malformed-prior-identity')
        result = self.cli('--record', '.warlock-contributor/next.json', 'start',
                          '--owner', 'new-contributor', '--slice-file', plan, ok=False)
        message = json.loads(result.stdout)['errors'][0]
        self.assertIn('Participant history inventory is incomplete', message)
        self.assertNotIn('NameError', message)
        self.assertFalse((self.repo/'.warlock-contributor/next.json').exists())

    def test_stop_thresholds_include_exact_iteration_and_time_boundaries(self):
        started = dt.datetime.fromisoformat('2026-01-01T00:00:00+00:00')
        record = {'startedUTC': started.isoformat(), 'iterations': []}
        record['iterations'] = [{'meaningfulProgress': False, 'atUTC': started.isoformat()}]
        one_iteration = _policy.progress_status(record, started + dt.timedelta(seconds=1))
        self.assertFalse(one_iteration['investigationNeedsChange'])
        record['iterations'].append({'meaningfulProgress': False, 'atUTC': started.isoformat()})
        two_iterations = _policy.progress_status(record, started + dt.timedelta(seconds=1))
        self.assertIn('two-iterations-without-progress', two_iterations['reasons'])
        record['iterations'] = []
        before_time_limit = _policy.progress_status(record, started + dt.timedelta(seconds=2699))
        exact_time_limit = _policy.progress_status(record, started + dt.timedelta(seconds=2700))
        self.assertFalse(before_time_limit['investigationNeedsChange'])
        self.assertIn('45-minutes-without-recorded-progress', exact_time_limit['reasons'])

    def test_legacy_nested_stopped_record_remains_in_the_inventory(self):
        original = self.stop_current_record()
        nested = self.repo/'.warlock-contributor/legacy/archive.json'
        nested.parent.mkdir(parents=True)
        nested.write_bytes(original)
        plan = self.prospective_slice('restore-pending', 'legacy-nested-match')
        packet = json.loads(self.cli('--record', '.warlock-contributor/next.json',
                                     'preflight', '--slice-file', plan, ok=False).stdout)
        self.assertEqual(len(packet['priorStoppedRecords']), 2)
        self.assertEqual(packet['participantInventoryCount'], 2)
        self.assertTrue(any(row['record'] == '.warlock-contributor/legacy/archive.json'
                            for row in packet['priorStoppedRecords']))

    def test_index_participants_freezes_paths_without_editing_records(self):
        self.stop_current_record()
        record = self.repo/'.warlock-contributor/slice.json'
        original = record.read_bytes()
        index = json.loads(self.cli('index-participants').stdout)
        self.assertEqual(index['participantCount'], 1)
        self.assertIn('.warlock-contributor/slice.json', index['recordPaths'])
        stored = json.loads((self.repo/'.warlock-contributor/participant-index.json').read_text())
        self.assertRegex(stored['records']['.warlock-contributor/slice.json']['recordSha256'], r'^[0-9a-f]{64}$')
        self.assertEqual(record.read_bytes(), original)
        self.assertTrue((self.repo/'.warlock-contributor/participant-index.json').is_file())

    def test_meaningful_progress_in_original_record_clears_current_stop(self):
        self.stop_current_record()
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'identity = "new committed route"\n')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'Recorded real source progress')
        plan = self.prospective_slice('restore-pending', 'after-genuine-progress')
        packet = json.loads(self.cli('--record', '.warlock-contributor/next.json',
                                     'preflight', '--slice-file', plan).stdout)
        self.assertEqual(packet['priorStoppedRecords'], [])
        # A meaningful edit makes the new record require an explicit ownership
        # decision. That warning must not be confused with the old stop.
        self.assertFalse(packet['canStartCleanDraft'])
        self.assertTrue(packet['requiresOwnershipDecision'])
        self.assertTrue(any('Selected dirty paths' in warning for warning in packet['warnings']))

    def test_record_and_start_share_one_serialization_lock(self):
        self.fixture.start()
        self.cli('record', '--outcome', 'qualification', '--summary', 'First no-progress observation')
        plan = self.prospective_slice('restore-pending', 'concurrent-next')
        lock_path = self.repo/'.warlock-contributor/.records.lock'
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        record = subprocess.Popen([sys.executable, '-B', str(fixtures.CHECKER), '--repo', str(self.repo),
                                   '--json', 'record', '--outcome', 'qualification',
                                   '--summary', 'Second no-progress observation'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.fixture.env)
        start = subprocess.Popen([sys.executable, '-B', str(fixtures.CHECKER), '--repo', str(self.repo),
                                  '--record', '.warlock-contributor/next.json', '--json', 'start',
                                  '--owner', 'new-contributor', '--slice-file', plan],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.fixture.env)
        try:
            time.sleep(0.1)
            self.assertIsNone(record.poll())
            self.assertIsNone(start.poll())
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
        record_out, record_err = record.communicate(timeout=10)
        start_out, start_err = start.communicate(timeout=10)
        self.assertEqual(record.returncode, 0, record_out+record_err)
        self.assertIn(start.returncode, (0, 2), start_out+start_err)
        previous = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        self.assertEqual(len(previous['iterations']), 2)
        self.assertEqual([item['outcome'] for item in previous['iterations']],
                         ['qualification', 'qualification'])
        if start.returncode == 0:
            created = json.loads((self.repo/'.warlock-contributor/next.json').read_text())
            self.assertLessEqual(created['startedUTC'], previous['iterations'][-1]['atUTC'])
        else:
            self.assertFalse((self.repo/'.warlock-contributor/next.json').exists())


if __name__ == '__main__':
    unittest.main()

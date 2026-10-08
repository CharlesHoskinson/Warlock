"""Scaffold and resume helpers against isolated repositories; no GUI or client launch."""
import datetime as dt
import json
import os
from pathlib import Path
import unittest

import test_warlock as fixtures


class ContributorHelperTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        self.cli = self.fixture.cli

    def plan(self, *extra, ok=True):
        return self.cli('plan', '--id', 'visible-feedback', '--requirement', 'ELM-UI-007',
                        '--scenario', 'restore-pending', '--path', 'src/Desktop.elm',
                        '--before', 'feedback hidden', '--after', 'feedback visible',
                        '--verify', 'changed source compile and typed negative replay',
                        *extra, ok=ok)

    def test_plan_preserves_original_oracle_and_starts_without_selecting_global_work(self):
        state = self.repo / 'docs/warlock-build-loop/v2/STATE.json'
        before = state.read_bytes()
        plan = json.loads(self.plan().stdout)
        original = next(r for r in self.fixture.original['requirements'] if r['id'] == 'ELM-UI-007')
        scenario = next(s for s in original['scenarios'] if s['name'] == 'restore-pending')
        self.assertEqual(plan['originals'][0]['scenarios'], [scenario])
        self.assertEqual(plan['slice']['paths'], ['implementation/warlock/src/Desktop.elm'])
        self.fixture.write('.warlock-contributor/plan.json', plan)
        self.cli('start', '--owner', 'contributor', '--slice-file', '.warlock-contributor/plan.json')
        self.cli('check')
        self.assertEqual(before, state.read_bytes())

    def test_plan_rejects_scenarios_outside_requirement_and_path_escape(self):
        self.plan('--scenario', 'search-no-match', ok=False)
        self.plan('--path', '../outside', ok=False)
        self.plan('--requirement', 'made-up-ID', ok=False)

    def test_plan_does_not_adopt_existing_dirty_source(self):
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'foreign draft')
        self.fixture.write('.warlock-contributor/plan.json', json.loads(self.plan().stdout))
        self.cli('start', '--owner', 'contributor', '--slice-file', '.warlock-contributor/plan.json')
        record = json.loads((self.repo / '.warlock-contributor/slice.json').read_text())
        self.assertIn('implementation/warlock/src/Desktop.elm', record['foreignDirty'])
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'attempted overwrite')
        self.cli('check', ok=False)

    def test_handoff_is_read_only_and_exposes_actual_missing_observations(self):
        self.fixture.start()
        self.fixture.record_claim(self.fixture.claim())
        path = self.repo / '.warlock-contributor/slice.json'
        before = path.read_bytes()
        report = json.loads(self.cli('handoff').stdout)
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(report['changedSinceLastRecord'], [])
        self.assertTrue(report['observations'][0]['evidenceMatchesCurrentSources'])
        self.assertEqual(report['observations'][0]['recordedDisposition'], 'partial')
        self.assertIn('native physical presentation and AT remain open', report['observations'][0]['missingObservations'])

    def test_handoff_rejects_stale_claim_but_still_reports_changed_source(self):
        self.fixture.start()
        self.fixture.record_claim(self.fixture.claim())
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'current new source')
        report = json.loads(self.cli('handoff', ok=False).stdout)
        self.assertEqual(report['changedSinceLastRecord'], ['implementation/warlock/src/Desktop.elm'])
        self.assertFalse(report['observations'][0]['evidenceMatchesCurrentSources'])
        self.assertTrue(any('Stale' in e for e in report['errors']))

    def test_handoff_no_progress_and_no_record_are_explicit(self):
        self.cli('handoff', ok=False)
        self.fixture.start()
        record = json.loads((self.repo / '.warlock-contributor/slice.json').read_text())
        record['startedUTC'] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).isoformat()
        self.fixture.write('.warlock-contributor/slice.json', record)
        report = json.loads(self.cli('handoff').stdout)
        self.assertTrue(any('Stop expanding' in w for w in report['warnings']))
        self.assertIsNone(report['observations'][0]['recordedDisposition'])
        self.assertFalse(report['observations'][0]['evidenceMatchesCurrentSources'])

    def test_handoff_changed_evidence_is_not_reported_as_current(self):
        self.fixture.start()
        self.fixture.record_claim(self.fixture.claim())
        self.fixture.write('implementation/warlock/qa/evidence/result.json', {'changed': True})
        report = json.loads(self.cli('handoff', ok=False).stdout)
        self.assertFalse(report['observations'][0]['evidenceMatchesCurrentSources'])
        self.assertTrue(any('changed evidence' in e for e in report['errors']))

    def complete_package(self):
        for name in ('scripts/session_hook.py', 'skills/warlock-contribute/SKILL.md',
                     '.claude-plugin/plugin.json', '.codex-plugin/plugin.json',
                     'hooks/hooks.json', 'hooks/codex.json'):
            self.fixture.write('plugins/warlock-contributor/' + name, (fixtures.PLUGIN / name).read_text())

    def test_doctor_reports_missing_package_and_never_executes_clients(self):
        report = json.loads(self.cli('doctor', ok=False).stdout)
        self.assertIn('plugins/warlock-contributor/hooks/codex.json', report['missingPackageFiles'])
        self.complete_package()
        bin_dir = self.repo / 'bin'
        bin_dir.mkdir()
        sentinel = self.repo / 'client-executed'
        for name in ('claude', 'codex', 'grok'):
            exe = bin_dir / name
            exe.write_text('#!/bin/sh\ntouch "' + str(sentinel) + '"\n')
            exe.chmod(0o755)
        self.fixture.env['PATH'] = str(bin_dir) + os.pathsep + os.environ['PATH']
        report = json.loads(self.cli('doctor').stdout)
        self.assertFalse(sentinel.exists())
        self.assertTrue(report['recordIgnored'])
        self.assertFalse(report['recordExists'])
        self.assertEqual(report['clientExecutables']['grok'], str(bin_dir / 'grok'))
        self.assertEqual(report['missingPackageFiles'], [])

    def test_doctor_rejects_symlink_package_path(self):
        self.complete_package()
        path = self.repo / 'plugins/warlock-contributor/hooks/codex.json'
        path.unlink()
        path.symlink_to(fixtures.PLUGIN / 'hooks/codex.json')
        self.cli('doctor', ok=False)

    def test_doctor_missing_ignore_has_an_actionable_warning_without_writing(self):
        self.complete_package()
        before = (self.repo / '.gitignore').read_bytes()
        report = json.loads(self.cli('--record', 'unignored-record.json', 'doctor').stdout)
        self.assertFalse(report['recordIgnored'])
        self.assertTrue(any('start will refuse' in w for w in report['warnings']))
        self.assertEqual(before, (self.repo / '.gitignore').read_bytes())
        self.assertFalse((self.repo / 'unignored-record.json').exists())

    def claim_packet(self, *extra, ok=True):
        return self.cli('claim', '--requirement', 'ELM-UI-007', '--scenario', 'restore-pending',
                        '--evidence', 'implementation/warlock/qa/evidence/result.json',
                        '--scope', 'typed component replay only', '--disposition', 'partial',
                        '--missing', 'Native physical presentation and AT remain open', *extra, ok=ok)

    def test_claim_packet_preserves_original_and_is_record_compatible_without_writes(self):
        self.fixture.start()
        expected = self.fixture.claim()
        record = self.repo / '.warlock-contributor/slice.json'
        ledger = self.repo / 'docs/warlock-build-loop/v2/requirement-ledger.json'
        before = (record.read_bytes(), ledger.read_bytes())
        packet = json.loads(self.claim_packet().stdout)
        self.assertEqual(before, (record.read_bytes(), ledger.read_bytes()))
        claim = packet['claims'][0]
        for key in ('oracle', 'verificationScope', 'evidence', 'sourceHashes'):
            self.assertEqual(claim[key], expected[key])
        self.assertEqual(claim['reviewer'], 'fresh-contributor')
        self.assertEqual(claim['disposition'], 'partial')
        self.fixture.write('.warlock-contributor/packet.json', packet)
        self.cli('record', '--outcome', 'scenario-verdict', '--summary', 'Observed bounded replay',
                 '--claim-file', '.warlock-contributor/packet.json')
        self.cli('check')
        self.assertEqual(ledger.read_bytes(), before[1])

    def test_claim_packet_tampering_and_changed_evidence_are_rechecked_by_record(self):
        self.fixture.start()
        expected = self.fixture.claim()
        packet = json.loads(self.claim_packet().stdout)
        packet['claims'][0]['oracle'] = 'Relaxed oracle'
        self.fixture.write('.warlock-contributor/packet.json', packet)
        self.cli('record', '--outcome', 'scenario-verdict', '--summary', 'Attempted claim',
                 '--claim-file', '.warlock-contributor/packet.json', ok=False)
        packet = json.loads(self.claim_packet().stdout)
        self.fixture.write('.warlock-contributor/packet.json', packet)
        self.fixture.write(expected['evidence'][0]['path'], 'changed after scaffold')
        self.cli('record', '--outcome', 'scenario-verdict', '--summary', 'Attempted stale claim',
                 '--claim-file', '.warlock-contributor/packet.json', ok=False)

    def test_claim_cannot_accept_or_expand_slice(self):
        self.claim_packet(ok=False)  # No participant record.
        self.fixture.start()
        self.fixture.claim()
        self.claim_packet('--disposition', 'accepted', ok=False)
        self.claim_packet('--scenario', 'search-no-match', ok=False)
        self.claim_packet('--requirement', 'ELM-UI-005', ok=False)
        self.claim_packet('--scope', ' ', ok=False)

    def test_claim_requires_real_safe_evidence_and_existing_sources(self):
        self.fixture.start()
        self.claim_packet(ok=False)  # Missing evidence file.
        self.fixture.claim()
        self.claim_packet('--evidence', '../escape', ok=False)
        evidence = self.repo / 'linked.json'
        evidence.symlink_to(self.repo / 'implementation/warlock/qa/evidence/result.json')
        self.claim_packet('--evidence', 'linked.json', ok=False)
        (self.repo / 'implementation/warlock/src/Desktop.elm').unlink()
        self.claim_packet(ok=False)

    def test_claim_requires_missing_observation_and_guards_foreign_work(self):
        self.fixture.write('foreign.txt', 'other contributor draft')
        self.fixture.start()
        self.fixture.claim()
        self.cli('claim', '--requirement', 'ELM-UI-007', '--scenario', 'restore-pending',
                 '--evidence', 'implementation/warlock/qa/evidence/result.json',
                 '--scope', 'component', '--disposition', 'partial', ok=False)
        self.fixture.write('foreign.txt', 'overwritten draft')
        self.claim_packet(ok=False)

    def test_claim_after_source_change_retains_prior_record_and_hashes_current_source(self):
        self.fixture.start()
        self.fixture.record_claim(self.fixture.claim())
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'new own implementation')
        record = self.repo / '.warlock-contributor/slice.json'
        before = record.read_bytes()
        packet = json.loads(self.claim_packet().stdout)
        self.assertEqual(record.read_bytes(), before)
        self.assertEqual(packet['claims'][0]['sourceHashes']['implementation/warlock/src/Desktop.elm'],
                         fixtures.digest(self.repo / 'implementation/warlock/src/Desktop.elm'))
        self.fixture.write('.warlock-contributor/packet.json', packet)
        self.cli('record', '--outcome', 'scenario-verdict', '--summary', 'Updated bounded replay',
                 '--claim-file', '.warlock-contributor/packet.json')
        self.assertTrue(json.loads(record.read_text())['iterations'][0]['claims'][0]['historicalAfterSourceChange'])
        self.cli('check')


if __name__ == '__main__':
    unittest.main()

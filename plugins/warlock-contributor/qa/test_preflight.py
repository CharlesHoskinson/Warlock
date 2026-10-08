"""Saved-plan previews in temporary repositories, including ownership conflicts."""
import copy
import json
import unittest

import test_warlock as fixtures


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli
        self.plan_file = '.warlock-contributor/preview-plan.json'
        self.plan = json.loads(self.cli(
            'plan', '--id', 'visible-feedback', '--requirement', 'ELM-UI-007',
            '--scenario', 'restore-pending', '--path', 'src/Desktop.elm',
            '--before', 'feedback hidden', '--after', 'feedback visible',
            '--verify', 'changed compile and negative replay').stdout)
        self.fixture.write(self.plan_file, self.plan)

    def preview(self, *global_args, ok=True):
        return json.loads(self.cli(*global_args, 'preflight', '--slice-file', self.plan_file, ok=ok).stdout)

    def protected_bytes(self):
        return {n: (self.repo / n).read_bytes() for n in (
            self.plan_file, '.git/index', 'docs/warlock-build-loop/v2/STATE.json',
            'docs/warlock-build-loop/v2/requirement-ledger.json',
            'implementation/warlock/src/Desktop.elm', 'foreign.txt')}

    def test_clean_preview_matches_start_without_writing_or_reserving_ownership(self):
        before = self.protected_bytes()
        result = self.preview()
        self.assertTrue(result['canStartCleanDraft'])
        self.assertFalse(result['writesPerformed'])
        self.assertFalse(result['acceptanceInferred'])
        self.assertEqual(result['originals'], self.plan['originals'])
        self.assertEqual(result['sourceHashes']['implementation/warlock/src/Desktop.elm'],
                         fixtures.digest(self.repo / 'implementation/warlock/src/Desktop.elm'))
        self.assertEqual(before, self.protected_bytes())
        self.assertFalse((self.repo / '.warlock-contributor/slice.json').exists())
        self.assertFalse((self.repo / '.warlock-contributor/slice.json.lock').exists())
        self.cli('start', '--owner', 'contributor', '--slice-file', self.plan_file)
        record = json.loads((self.repo / '.warlock-contributor/slice.json').read_text())
        self.assertEqual(result['slice'], record['slice'])

    def test_dirty_selection_stays_unowned_and_other_drafts_are_identified(self):
        selected = 'implementation/warlock/src/Desktop.elm'
        self.fixture.write(selected, 'other contributor source draft')
        self.fixture.write('foreign.txt', 'other contributor unrelated draft')
        before = self.protected_bytes()
        result = self.preview()
        self.assertFalse(result['canStartCleanDraft'])
        self.assertTrue(result['requiresOwnershipDecision'])
        self.assertEqual(result['selectedDirtyPaths'][selected], fixtures.digest(self.repo / selected))
        self.assertIn('foreign.txt', result['otherDirtyPaths'])
        self.assertEqual(before, self.protected_bytes())
        self.cli('start', '--owner', 'contributor', '--slice-file', self.plan_file)
        record = json.loads((self.repo / '.warlock-contributor/slice.json').read_text())
        self.assertIn(selected, record['foreignDirty'])
        self.assertEqual(record['adoptedDirty']['paths'], [])

    def test_existing_record_is_retained_and_an_alternate_record_can_be_previewed(self):
        self.fixture.start()
        path = self.repo / '.warlock-contributor/slice.json'
        before = path.read_bytes()
        result = self.preview(ok=False)
        self.assertTrue(result['recordExists'])
        self.assertFalse(result['canStartCleanDraft'])
        self.assertTrue(any('handoff' in e for e in result['errors']))
        self.assertEqual(path.read_bytes(), before)
        alternate = self.preview('--record', '.warlock-contributor/new-slice.json')
        self.assertTrue(alternate['canStartCleanDraft'])
        self.assertFalse((self.repo / alternate['record']).exists())

    def test_unignored_record_and_file_parent_are_actionable_without_creating_paths(self):
        result = self.preview('--record', 'unignored/new.json', ok=False)
        self.assertFalse(result['recordIgnored'])
        self.assertFalse((self.repo / 'unignored').exists())
        self.fixture.write('.warlock-contributor/file', 'regular file')
        result = self.preview('--record', '.warlock-contributor/file/new.json', ok=False)
        self.assertTrue(any('parent is not a directory' in e for e in result['errors']))

    def test_new_sources_and_bare_slice_are_allowed_without_fabricated_hashes(self):
        bare = copy.deepcopy(self.plan['slice'])
        bare['paths'].append('src/New.elm')
        self.fixture.write(self.plan_file, bare)
        result = self.preview()
        self.assertEqual(result['newSourcePaths'], ['implementation/warlock/src/New.elm'])
        self.assertIsNone(result['sourceHashes']['implementation/warlock/src/New.elm'])
        self.assertTrue(result['canStartCleanDraft'])
        self.assertFalse((self.repo / 'implementation/warlock/src/New.elm').exists())
        self.cli('start', '--owner', 'contributor', '--slice-file', self.plan_file)

    def test_modified_originals_fail_in_preview_and_start(self):
        for field in ('verification', 'given', 'when', 'then'):
            with self.subTest(field=field):
                packet = copy.deepcopy(self.plan)
                if field == 'verification':
                    packet['originals'][0][field] = 'weakened verification'
                else:
                    packet['originals'][0]['scenarios'][0][field] = 'changed original'
                self.fixture.write(self.plan_file, packet)
                result = self.preview(ok=False)
                self.assertTrue(any('originals differ' in e for e in result['errors']))
                self.cli('start', '--owner', 'contributor', '--slice-file', self.plan_file, ok=False)
                self.assertFalse((self.repo / '.warlock-contributor/slice.json').exists())

    def test_packet_with_changed_selection_or_unsupported_schema_is_rejected(self):
        packet = copy.deepcopy(self.plan)
        original = next(r for r in self.fixture.original['requirements'] if r['id'] == 'ELM-UI-007')
        packet['slice']['scenarios'] = [next(s['name'] for s in original['scenarios'] if s['name'] != 'restore-pending')]
        self.fixture.write(self.plan_file, packet)
        result = self.preview(ok=False)
        self.assertTrue(any('originals differ' in e for e in result['errors']))
        for value in (True, 2, '1'):
            packet = copy.deepcopy(self.plan)
            packet['planSchema'] = value
            self.fixture.write(self.plan_file, packet)
            self.preview(ok=False)
            self.cli('start', '--owner', 'contributor', '--slice-file', self.plan_file, ok=False)
        self.fixture.write(self.plan_file, [])
        self.preview(ok=False)

    def test_symlink_plan_record_or_source_is_refused(self):
        plan = self.repo / self.plan_file
        target = self.fixture.write('.warlock-contributor/target.json', self.plan)
        plan.unlink()
        plan.symlink_to(target)
        self.preview(ok=False)
        plan.unlink()
        self.fixture.write(self.plan_file, self.plan)
        (self.repo / '.warlock-contributor/slice.json').symlink_to(target)
        self.preview(ok=False)
        (self.repo / '.warlock-contributor/slice.json').unlink()
        source = self.repo / 'implementation/warlock/src/Desktop.elm'
        source.unlink()
        source.symlink_to(self.repo / 'foreign.txt')
        self.preview(ok=False)

    def test_start_rechecks_edits_after_the_preview(self):
        self.assertTrue(self.preview()['canStartCleanDraft'])
        selected = 'implementation/warlock/src/Desktop.elm'
        self.fixture.write(selected, 'concurrent foreign draft after preview')
        self.cli('start', '--owner', 'contributor', '--slice-file', self.plan_file)
        record = json.loads((self.repo / '.warlock-contributor/slice.json').read_text())
        self.assertEqual(record['foreignDirty'][selected], fixtures.digest(self.repo / selected))


if __name__ == '__main__':
    unittest.main()

"""Canonical selection is checked without rewriting historical projections."""
import json
import subprocess
import sys
import unittest

import test_warlock as fixtures
from test_delivery_flow import DeliveryFixture


class DeliverySelectionTests(DeliveryFixture):
    def test_old_v016_inventory_and_owner_census_read_new_policy_record(self):
        self.start_delivery()
        (self.repo / '.warlock-contributor/delivery-plan.json').unlink()
        baseline = subprocess.check_output(['git', 'show',
            '94a2eb00a59cca4ffca61ca929aacc3abe468d8b:plugins/warlock-contributor/scripts/warlock.py'],
            cwd=fixtures.PLUGIN, env=self.fixture.env)
        old_checker = self.repo / 'plugins/warlock-contributor/scripts/warlock.py'
        old_checker.write_bytes(baseline)
        before = (self.repo / self.record_path).read_bytes()
        result = subprocess.run([sys.executable, '-B', str(old_checker), '--repo', str(self.repo),
                                 '--record', self.record_path, '--json', 'owner-census'],
                                capture_output=True, text=True, env=self.fixture.env, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, (self.repo / self.record_path).read_bytes())
        self.assertEqual(json.loads(result.stdout)['participantCount'], 1)

    def test_selection_cas_and_history(self):
        self.start_delivery()
        path = self.repo / 'docs/warlock-build-loop/v2/STATE.json'
        before = path.read_bytes()
        self.fixture.cli('--record', self.record_path, 'delivery-select', '--expect-state-sha', '0' * 64, ok=False)
        self.assertEqual(before, path.read_bytes())
        state = json.loads(before)
        self.assertEqual(state['activeSelection']['generation'], 1)
        self.assertEqual(state['activeContributorRecord'], self.record_path)
        self.assertEqual(len(state['sliceSelectionHistory']), 1)

    def test_wrong_current_record_and_generation_fail(self):
        self.start_delivery()
        self.ready()
        before = (self.repo / self.record_path).read_bytes()
        self.fixture.cli('--record', self.record_path, 'progress-audit', '--expect-slice',
                         'visible-feedback', '--expect-selection', '2', ok=False)
        state = json.loads((self.repo / 'docs/warlock-build-loop/v2/STATE.json').read_text())
        state['activeContributorRecord'] = '.warlock-contributor/stale.json'
        self.fixture.write('docs/warlock-build-loop/v2/STATE.json', state)
        self.precheck(ok=False)
        self.assertEqual(before, (self.repo / self.record_path).read_bytes())

    def test_audit_requires_selection_and_preserves_counts(self):
        self.start_delivery()
        self.ready()
        self.fixture.cli('--record', self.record_path, 'progress-audit', '--expect-slice', 'visible-feedback', ok=False)
        result = json.loads(self.fixture.cli('--record', self.record_path, 'progress-audit',
                            '--expect-slice', 'visible-feedback', '--expect-selection', '1').stdout)
        self.assertEqual(result['nextRootAction']['kind'], 'execute')
        self.assertFalse(result['originalAcceptance'])
        self.assertEqual(result['originalAcceptanceCounts']['requirements'], 242)
        self.assertEqual(result['originalAcceptanceCounts']['scenarios'], 417)

    def test_source_path_escape_refused(self):
        self.start_delivery()
        self.append({'eventId': 'bad', 'kind': 'candidate', 'candidate': {
            'id': 'bad', 'scope': 'cpu', 'argv': ['true'], 'expectedObservation': 'bad',
            'nativePrerequisites': [], 'manifest': {'sources': {'../escape': '0' * 64},
                'fixtures': {}, 'runners': {}, 'profiles': {}}}}, ok=False)


if __name__ == '__main__':
    unittest.main()

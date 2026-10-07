"""Network-free contribution-policy tests using tiny isolated Git repositories."""
import hashlib
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
CHECKER = PLUGIN / 'scripts/warlock.py'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ContributionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='warlock-contributor-test-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(('GIT_', 'GROK_'))}
        self.env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')
        self.run_git('init', '-q')
        self.run_git('config', 'user.name', 'Isolated contributor')
        self.run_git('config', 'user.email', 'fixture@example.invalid')
        source = PLUGIN.parents[1] / 'docs/elm-roadmap/requirements.json'
        self.original = json.loads(source.read_text())
        baseline = self.repo/'docs/elm-roadmap/requirements.json'
        baseline.parent.mkdir(parents=True)
        baseline.write_bytes(source.read_bytes())
        ledger = PLUGIN.parents[1]/'docs/warlock-build-loop/v2/requirement-ledger.json'
        self.write('docs/warlock-build-loop/v2/requirement-ledger.json', json.loads(ledger.read_text()))
        self.slice = {'id': 'visible-feedback', 'requirements': ['ELM-UI-007'],
                      'scenarios': ['restore-pending'], 'before': 'feedback hidden',
                      'after': 'feedback visible', 'paths': ['src/Desktop.elm'],
                      'verification': ['changed source compile', 'negative state replay']}
        self.write('docs/warlock-build-loop/v2/STATE.json', {
            'schema': 1, 'sourceCandidate': 'implementation/warlock',
            'heldParent': 'implementation/warlock-preview-provider-v143', 'activeSlice': self.slice,
            'releaseAccepted': False})
        self.write('.gitignore', '.warlock-contributor/\n')
        self.write('implementation/warlock/src/Desktop.elm', 'module Desktop exposing (identity)\nidentity = "old"\n')
        self.write('implementation/warlock/ANCESTRY.json', {'parent': 'implementation/warlock-preview-provider-v143'})
        self.write('implementation/warlock-preview-provider-v143/frozen.txt', 'held immutable baseline\n')
        self.write('foreign.txt', 'original unrelated worker file\n')
        installed = self.repo/'plugins/warlock-contributor/scripts/warlock.py'
        installed.parent.mkdir(parents=True)
        shutil.copyfile(CHECKER, installed)
        self.run_git('add', '.')
        self.run_git('commit', '-qm', 'minimal fixture baseline')

    def write(self, name, value):
        path = self.repo/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2)+'\n' if isinstance(value, (dict, list)) else value)
        return path

    def run_git(self, *args):
        return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgSign=false', '-c', 'tag.gpgSign=false', '-C', str(self.repo), *args], check=True,
                              capture_output=True, text=True, env=self.env).stdout.strip()

    def cli(self, *args, ok=True):
        proc = subprocess.run([sys.executable, '-B', str(CHECKER), '--repo', str(self.repo),
                               '--json', *args], capture_output=True, text=True, env=self.env)
        if ok:
            self.assertEqual(proc.returncode, 0, proc.stdout+'\n'+proc.stderr)
        else:
            self.assertNotEqual(proc.returncode, 0, proc.stdout+'\n'+proc.stderr)
        return proc

    def start(self):
        self.cli('start', '--owner', 'fresh-contributor')

    def claim(self, scope='component', scenario='restore-pending'):
        row = next(r for r in self.original['requirements'] if r['id'] == 'ELM-UI-007')
        original = next(s for s in row['scenarios'] if s['name'] == scenario)
        evidence = self.write('implementation/warlock/qa/evidence/result.json', {'component': 'pass'})
        return {'requirement': row['id'], 'scenario': scenario, 'oracle': original['then'],
                'verificationScope': row['verification'], 'scope': scope,
                'evidence': [{'path': str(evidence.relative_to(self.repo)), 'sha256': digest(evidence)}],
                'sourceHashes': {'implementation/warlock/src/Desktop.elm': digest(self.repo/'implementation/warlock/src/Desktop.elm')},
                'reviewer': 'independent-fixture-reviewer', 'disposition': 'partial',
                'missingObservations': ['native physical presentation and AT remain open']}

    def record_claim(self, claim, ok=True):
        self.write('.warlock-contributor/claim.json', [claim])
        return self.cli('record', '--outcome', 'scenario-verdict', '--summary', 'bounded component observation',
                        '--claim-file', '.warlock-contributor/claim.json', ok=ok)

    def test_fresh_start_status_check_record(self):
        before = (self.repo/'docs/warlock-build-loop/v2/requirement-ledger.json').read_bytes()
        self.cli('status')
        self.start()
        self.cli('status')
        self.cli('check')
        self.record_claim(self.claim())
        result = json.loads(self.cli('check').stdout)
        self.assertIn('external evidence', result['acceptanceBoundary'])
        self.assertEqual(before, (self.repo/'docs/warlock-build-loop/v2/requirement-ledger.json').read_bytes())

    def test_missing_source_cannot_support_claim(self):
        self.slice['paths'] = ['src/Missing.elm']
        self.write('docs/warlock-build-loop/v2/STATE.json', {'activeSlice': self.slice})
        self.cli('start', '--owner', 'contributor')
        c = self.claim()
        c['sourceHashes'] = {'implementation/warlock/src/Missing.elm': None}
        self.record_claim(c, ok=False)

    def test_typo_and_wrong_requirement_rejected(self):
        for requirements, scenarios in [(['ELM-UI-007'], ['restore-pendng']), (['ELM-UX-008'], ['restore-pending'])]:
            self.slice.update(requirements=requirements, scenarios=scenarios)
            self.write('.warlock-contributor/override.json', self.slice)
            self.cli('start', '--owner', 'contributor', '--slice-file', '.warlock-contributor/override.json', ok=False)

    def test_changed_original_baseline_rejected(self):
        self.start()
        self.original['requirements'][0]['verification'] += ' changed'
        self.write('docs/elm-roadmap/requirements.json', self.original)
        self.cli('check', ok=False)

    def test_frozen_archive_edit_rejected(self):
        self.start()
        self.write('implementation/warlock-preview-provider-v143/frozen.txt', 'changed archive')
        self.cli('check', ok=False)

    def test_foreign_dirty_preserved_and_mutation_rejected(self):
        path = self.write('foreign.txt', 'ongoing unrelated contributor work')
        self.start()
        self.cli('check')
        self.assertEqual(path.read_text(), 'ongoing unrelated contributor work')
        path.write_text('mutated foreign work')
        self.cli('check', ok=False)

    def test_path_escape_and_symlink_rejected(self):
        for escape in ['../outside', '/tmp/outside']:
            self.cli('--record', escape, 'start', '--owner', 'contributor', ok=False)
        (self.repo/'implementation/warlock/src/escaped').symlink_to('/tmp')
        self.slice['paths'] = ['src/escaped/outside']
        self.write('.warlock-contributor/override.json', self.slice)
        self.cli('start', '--owner', 'contributor', '--slice-file', '.warlock-contributor/override.json', ok=False)

    def test_stale_source_evidence_and_exact_oracle(self):
        self.start()
        c = self.claim()
        self.record_claim(c)
        self.write(c['evidence'][0]['path'], 'changed evidence')
        self.cli('check', ok=False)

    def test_claim_source_hash_or_oracle_mismatch_rejected(self):
        self.start()
        for key in ['sourceHashes', 'oracle', 'verificationScope']:
            c = self.claim()
            c[key] = {next(iter(c[key])): '0'*64} if key == 'sourceHashes' else 'different original obligation'
            self.record_claim(c, ok=False)

    def test_no_progress_advisory_keeps_independent_work_allowed(self):
        self.start()
        for i in range(2):
            self.cli('record', '--outcome', 'qualification', '--summary', 'no source or verdict progress')
        result = json.loads(self.cli('check').stdout)
        self.assertTrue(result['ok'])
        self.assertTrue(any('Independent work remains allowed' in w for w in result['warnings']))
        self.assertNotIn('goal', result)

    def test_missing_evidence_null_hash_rejected(self):
        self.start()
        c = self.claim()
        c['evidence'] = [{'path': 'docs/missing-report.json', 'sha256': None}]
        self.record_claim(c, ok=False)

    def test_source_changed_after_claim_rejected(self):
        self.start()
        self.record_claim(self.claim())
        self.write('implementation/warlock/src/Desktop.elm', 'actual new source')
        self.cli('check', ok=False)

    def test_production_fix_progress_requires_source_delta(self):
        self.start()
        self.cli('record', '--outcome', 'production-fix', '--summary', 'claim without source delta')
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        self.assertFalse(record['iterations'][-1]['meaningfulProgress'])
        self.write('implementation/warlock/src/Desktop.elm', 'actual source delta')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'actual visible source fix')
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        self.assertTrue(record['iterations'][-1]['meaningfulProgress'])

    def test_mandatory_check_requires_record(self):
        self.cli('check', '--require-record', ok=False)
        self.start()
        self.cli('check', '--require-record')

    def test_ledger_scenario_identity_is_frozen(self):
        path = self.repo/'docs/warlock-build-loop/v2/requirement-ledger.json'
        ledger = json.loads(path.read_text())
        ledger['requirements'][0]['scenarios'][0]['name'] += '-typo'
        path.write_text(json.dumps(ledger))
        self.cli('status', ok=False)

    def test_selected_dirty_source_is_protected_by_default(self):
        source = self.write('implementation/warlock/src/Desktop.elm', 'foreign draft at start')
        self.start()
        self.cli('check')
        source.write_text('changed draft without explicit ownership')
        self.cli('check', ok=False)

    def test_explicit_adoption_allows_selected_draft_edits(self):
        source = self.write('implementation/warlock/src/Desktop.elm', 'owned draft at start')
        self.cli('start', '--owner', 'returning-contributor', '--adopt-dirty', 'implementation/warlock/src/Desktop.elm', '--ownership-note', 'Resuming my own fixture draft')
        source.write_text('continued owned implementation')
        self.cli('check')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'continued explicitly owned source')
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        self.assertTrue(record['iterations'][-1]['meaningfulProgress'])

    def test_adoption_cannot_take_unrelated_dirty_path(self):
        self.write('foreign.txt', 'other contributor draft')
        self.cli('start', '--owner', 'contributor', '--adopt-dirty', 'foreign.txt',
                 '--ownership-note', 'attempt unrelated ownership', ok=False)

    def test_adoption_preserves_unrelated_foreign_dirty_file(self):
        self.write('implementation/warlock/src/Desktop.elm', 'owned draft at start')
        foreign = self.write('foreign.txt', 'other contributor draft')
        self.cli('start', '--owner', 'returning-contributor', '--adopt-dirty', 'implementation/warlock/src/Desktop.elm', '--ownership-note', 'Resuming my own fixture draft')
        self.write('implementation/warlock/src/Desktop.elm', 'continued owned source')
        self.cli('check')
        self.assertEqual(foreign.read_text(), 'other contributor draft')
        foreign.write_text('illicit unrelated draft edit')
        self.cli('check', ok=False)

    def test_internal_symlink_record_rejected(self):
        (self.repo/'.warlock-contributor').mkdir()
        (self.repo/'.warlock-link').symlink_to(self.repo/'.warlock-contributor')
        self.cli('--record', '.warlock-link/record.json', 'start', '--owner', 'contributor', ok=False)

    def test_prior_partial_claim_becomes_historical_after_source_fix(self):
        self.start()
        claim = self.claim()
        evidence = self.repo/claim['evidence'][0]['path']
        immutable = evidence.read_bytes()
        self.record_claim(claim)
        self.write('implementation/warlock/src/Desktop.elm', 'next actual production fix')
        self.cli('check', ok=False)
        result = json.loads(self.cli('record', '--outcome', 'production-fix',
                                     '--summary', 'next visible source behavior').stdout)
        self.assertTrue(any('current acceptance invalidated' in w for w in result['warnings']))
        self.cli('check')
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        historical = record['iterations'][0]['claims'][0]
        self.assertTrue(historical['historicalAfterSourceChange'])
        self.assertEqual(historical['sourceHashes'], claim['sourceHashes'])
        self.assertEqual(historical['evidence'], claim['evidence'])
        self.assertEqual(evidence.read_bytes(), immutable)
        self.assertTrue(record['iterations'][-1]['meaningfulProgress'])

    def test_new_stale_claim_does_not_claim_current_acceptance(self):
        self.start()
        stale = self.claim()
        self.record_claim(stale)
        self.write('implementation/warlock/src/Desktop.elm', 'new current source')
        self.record_claim(stale, ok=False)

    def test_qa_generated_changes_are_not_production_progress(self):
        self.slice['paths'] += ['qa/check.py', 'assets/shell.js']
        self.write('implementation/warlock/qa/check.py', 'original test')
        self.write('implementation/warlock/assets/shell.js', 'original generated bundle')
        self.run_git('add', '.')
        self.run_git('commit', '-qm', 'supporting paths fixture')
        self.write('.warlock-contributor/override.json', self.slice)
        self.cli('start', '--owner', 'contributor', '--slice-file', '.warlock-contributor/override.json')
        self.write('implementation/warlock/qa/check.py', 'updated test')
        self.write('implementation/warlock/assets/shell.js', 'updated generated bundle')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'only generated output and QA changed')
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        self.assertFalse(record['iterations'][-1]['meaningfulProgress'])

    def test_inspect_selected_original_and_ledger(self):
        result = json.loads(self.cli('inspect', '--requirement', 'ELM-UI-007').stdout)
        row = result['requirements'][0]
        original = next(r for r in self.original['requirements'] if r['id'] == 'ELM-UI-007')
        self.assertEqual(row['original'], original)
        self.assertEqual(row['ledger']['id'], original['id'])
        self.assertEqual(row['pointers']['original'], 'docs/elm-roadmap/requirements.json')
        self.cli('inspect', '--requirement', 'ELM-UI-007', '--requirement', 'ELM-UI-007', ok=False)
        self.cli('inspect', '--requirement', 'ELM-NOT-REAL', ok=False)

    def accepted_claim(self):
        claim = self.claim('native-and-AT')
        claim['disposition'] = 'accepted'
        claim['missingObservations'] = []
        claim['reviewer'] = {'name': 'external reviewer', 'independent': True, 'disposition': 'accepted'}
        claim['sourceTuple'] = {'sourceRevision': self.run_git('rev-parse', 'HEAD'), 'core': 'fixture-core',
                                'plugin': 'fixture-plugin', 'toolchain': 'fixture-toolchain'}
        return claim

    def test_duplicate_partial_verdict_cannot_reset_no_progress(self):
        self.start()
        claim = self.claim()
        self.record_claim(claim)
        for i in range(2):
            self.record_claim(claim)
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        self.assertTrue(record['iterations'][0]['meaningfulProgress'])
        self.assertTrue(all(not i['meaningfulProgress'] for i in record['iterations'][1:]))
        result = json.loads(self.cli('check').stdout)
        self.assertTrue(result['warnings'])
        self.assertTrue(result['ok'])

    def test_time_hash_only_requalification_does_not_count(self):
        self.start()
        claim = self.claim()
        self.record_claim(claim)
        newer = self.write('implementation/warlock/qa/evidence/requalification.json', {'sameObservation': 'another run'})
        claim['evidence'] = [{'path': str(newer.relative_to(self.repo)), 'sha256': digest(newer)}]
        self.record_claim(claim)
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        self.assertFalse(record['iterations'][-1]['meaningfulProgress'])
        record['iterations'][-1]['meaningfulProgress'] = True
        (self.repo/'.warlock-contributor/slice.json').write_text(json.dumps(record))
        self.cli('check', ok=False)

    def test_claim_disposition_must_be_defined(self):
        self.start()
        claim = self.claim()
        claim['disposition'] = 'counts-as-feature'
        self.record_claim(claim, ok=False)

    def test_accepted_claim_cannot_have_missing_observations(self):
        self.start()
        claim = self.accepted_claim()
        claim['missingObservations'] = ['native physical oracle still unobserved']
        self.record_claim(claim, ok=False)

    def test_accepted_owner_cannot_self_review(self):
        self.start()
        claim = self.accepted_claim()
        claim['reviewer']['name'] = 'fresh-contributor'
        self.record_claim(claim, ok=False)

    def test_accepted_evidence_cannot_be_ignored_or_product_source(self):
        self.start()
        for name in ['.warlock-contributor/ignored-report.json', 'implementation/warlock/src/Desktop.elm']:
            claim = self.accepted_claim()
            path = self.repo/name
            if name.startswith('.warlock-contributor'):
                self.write(name, {'observation': 'ignored ephemeral fixture'})
            claim['evidence'] = [{'path': name, 'sha256': digest(path)}]
            self.record_claim(claim, ok=False)

    def test_accepted_git_ignored_evidence_rejected(self):
        self.write('.gitignore', '.warlock-contributor/\nignored-evidence/\n')
        self.run_git('add', '.gitignore')
        self.run_git('commit', '-qm', 'ignored evidence fixture')
        self.start()
        claim = self.accepted_claim()
        path = self.write('ignored-evidence/report.json', {'observation': 'ephemeral'})
        claim['evidence'] = [{'path': 'ignored-evidence/report.json', 'sha256': digest(path)}]
        self.record_claim(claim, ok=False)

    def test_cached_checker_defaults_to_current_repo(self):
        cached = self.repo/'.plugin-cache/scripts/warlock.py'
        cached.parent.mkdir(parents=True)
        shutil.copyfile(CHECKER, cached)
        proc = subprocess.run([sys.executable, '-B', str(cached), '--json', 'status'],
                              cwd=self.repo, env=self.env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout+proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['activeSlice']['id'], self.slice['id'])

    def test_cache_mismatched_repository_checker_rejected(self):
        cached = self.repo/'.plugin-cache/scripts/warlock.py'
        cached.parent.mkdir(parents=True)
        shutil.copyfile(CHECKER, cached)
        self.write('plugins/warlock-contributor/scripts/warlock.py', '# incompatible repository checker')
        proc = subprocess.run([sys.executable, '-B', str(cached), '--json', 'status'],
                              cwd=self.repo, env=self.env, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)

    def test_archive_rename_endpoint_base_ref_rejected_with_record(self):
        self.start()
        base = self.run_git('rev-parse', 'HEAD')
        self.run_git('mv', 'implementation/warlock-preview-provider-v143/frozen.txt',
                     'implementation/warlock/src/moved.txt')
        self.run_git('commit', '-qm', 'archive moved to candidate fixture')
        self.cli('check', '--base-ref', base, ok=False)

    def test_archive_rename_endpoint_base_ref_rejected_without_record(self):
        base = self.run_git('rev-parse', 'HEAD')
        self.run_git('mv', 'implementation/warlock-preview-provider-v143/frozen.txt',
                     'implementation/warlock/src/moved.txt')
        self.run_git('commit', '-qm', 'archive moved before participant record')
        self.cli('check', '--project-only', '--base-ref', base, ok=False)

    def test_concurrent_record_writes_retain_every_iteration(self):
        self.start()
        def invoke(number):
            return subprocess.run([sys.executable, '-B', str(CHECKER), '--repo', str(self.repo),
                                   '--json', 'record', '--outcome', 'qualification', '--summary', str(number)],
                                  env=self.env, capture_output=True, text=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(invoke, range(4)))
        self.assertTrue(all(r.returncode == 0 for r in results), [r.stdout for r in results])
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        self.assertEqual({i['summary'] for i in record['iterations']}, {'0', '1', '2', '3'})
        self.cli('check')

    def test_staged_archive_move_rejected(self):
        self.start()
        self.run_git('mv', 'implementation/warlock-preview-provider-v143/frozen.txt',
                     'implementation/warlock/src/moved.txt')
        self.cli('check', ok=False)

    def test_concurrent_start_has_one_winner_and_valid_record(self):
        def invoke(owner):
            return subprocess.run([sys.executable, '-B', str(CHECKER), '--repo', str(self.repo),
                                   '--json', 'start', '--owner', owner], env=self.env,
                                  capture_output=True, text=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(invoke, ['owner-a', 'owner-b', 'owner-c', 'owner-d']))
        self.assertEqual(sum(r.returncode == 0 for r in results), 1)
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        self.assertIn(record['owner'], ['owner-a', 'owner-b', 'owner-c', 'owner-d'])
        self.cli('check')

    def test_normalized_duplicate_source_paths_rejected(self):
        self.slice['paths'] = ['src/Desktop.elm', 'implementation/warlock/src/Desktop.elm']
        self.write('.warlock-contributor/override.json', self.slice)
        self.cli('start', '--owner', 'contributor', '--slice-file', '.warlock-contributor/override.json', ok=False)

    def test_unignored_record_has_friendly_failure(self):
        self.write('.gitignore', '')
        result = json.loads(self.cli('start', '--owner', 'contributor', ok=False).stdout)
        self.assertTrue(any('Git-ignored' in e for e in result['errors']))
        self.assertFalse((self.repo/'.warlock-contributor/slice.json').exists())

    def test_project_only_avoids_stale_record_and_rejects_required_record(self):
        self.start()
        self.write('.warlock-contributor/slice.json', {'invalid': 'stale record'})
        self.cli('check', ok=False)
        self.cli('check', '--project-only')
        self.cli('check', '--project-only', '--require-record', ok=False)

    def test_foreign_symlink_is_fingerprinted_without_following(self):
        foreign = self.repo/'foreign.txt'
        foreign.unlink()
        foreign.symlink_to('/outside-secret-must-not-be-read')
        self.start()
        self.cli('check')
        foreign.unlink()
        foreign.symlink_to('/different-outside-target')
        self.cli('check', ok=False)

    def test_git_environment_cannot_redirect_checker_repository(self):
        fake_index = self.repo/'hostile-index'
        fake_index.write_bytes(b'foreign index sentinel')
        before = (self.repo/'.git/index').read_bytes()
        env = dict(self.env, GIT_INDEX_FILE=str(fake_index), GIT_DIR='/missing/hostile-git-dir',
                   GIT_WORK_TREE='/missing/hostile-worktree', GIT_CONFIG_COUNT='1',
                   GIT_CONFIG_KEY_0='core.hooksPath', GIT_CONFIG_VALUE_0='/missing/hostile-hook')
        proc = subprocess.run([sys.executable, '-B', str(CHECKER), '--repo', str(self.repo),
                               '--json', 'start', '--owner', 'contributor'], env=env,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout+proc.stderr)
        self.assertEqual(fake_index.read_bytes(), b'foreign index sentinel')
        self.assertEqual((self.repo/'.git/index').read_bytes(), before)

    def test_accepted_source_revision_must_exist_as_commit(self):
        self.start()
        claim = self.accepted_claim()
        claim['sourceTuple']['sourceRevision'] = '0'*40
        self.record_claim(claim, ok=False)

    def test_elapsed_no_progress_advisory(self):
        self.start()
        path = self.repo/'.warlock-contributor/slice.json'
        record = json.loads(path.read_text())
        record['startedUTC'] = '2000-01-01T00:00:00+00:00'
        path.write_text(json.dumps(record))
        result = json.loads(self.cli('check').stdout)
        self.assertTrue(result['ok'])
        self.assertTrue(result['warnings'])

    def test_partial_native_at_scope_stays_explicit(self):
        self.start()
        for scope in ['component', 'native-input-only', 'AT-observation-only']:
            self.record_claim(self.claim(scope))
        record = json.loads((self.repo/'.warlock-contributor/slice.json').read_text())
        claims = [i['claims'][0] for i in record['iterations']]
        self.assertEqual([c['scope'] for c in claims], ['component', 'native-input-only', 'AT-observation-only'])
        self.assertTrue(all(c['disposition'] == 'partial' and c['missingObservations'] for c in claims))

    def test_cold_contributor_skill_command_path(self):
        # Simulated fresh request: "Make Pending feedback visible in Warlock."
        # Only the shared skill and selected STATE identify the commands and IDs.
        skill = (PLUGIN/'skills/warlock-contribute/SKILL.md').read_text()
        self.assertIn('status', skill)
        self.assertIn('start --owner', skill)
        self.assertIn('record --outcome', skill)
        self.cli('status')
        self.cli('check')
        self.start()
        self.cli('check')
        self.write('implementation/warlock/src/Desktop.elm', 'visible Pending fixture delta')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'Pending text rendered by fixture; native/AT unobserved')
        self.cli('check')

    def test_hook_is_advisory_and_unrelated_work_is_allowed(self):
        self.start()
        self.write('implementation/warlock-preview-provider-v143/frozen.txt', 'invalid archive change')
        hook = PLUGIN/'scripts/session_hook.py'
        payload = {'hook_event_name': 'SessionStart', 'cwd': str(self.repo), 'prompt': 'edit unrelated documentation'}
        proc = subprocess.run([sys.executable, '-B', str(hook)], input=json.dumps(payload),
                              capture_output=True, text=True, env=self.env)
        self.assertEqual(proc.returncode, 0)
        result = json.loads(proc.stdout)
        self.assertNotIn('decision', result)
        self.assertIn('Unrelated work may continue', result['hookSpecificOutput']['additionalContext'])
        outside = subprocess.run([sys.executable, '-B', str(hook)],
                                 input=json.dumps({'hook_event_name': 'UserPromptSubmit', 'cwd': '/tmp'}),
                                 capture_output=True, text=True, env=self.env)
        self.assertEqual(outside.returncode, 0)
        self.assertEqual(outside.stdout, '')

    def test_accepted_label_is_not_checker_acceptance(self):
        self.start()
        c = self.claim('native-and-AT')
        c['disposition'] = 'accepted'
        c['missingObservations'] = []
        c['reviewer'] = {'name': 'external reviewer', 'independent': True, 'disposition': 'accepted'}
        c['sourceTuple'] = {'sourceRevision': self.run_git('rev-parse', 'HEAD'), 'core': 'fixture-core', 'plugin': 'fixture-plugin', 'toolchain': 'fixture-toolchain'}
        result = json.loads(self.record_claim(c).stdout)
        self.assertIn('independent review', result['acceptanceBoundary'])
        self.assertNotIn('releaseAccepted', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)

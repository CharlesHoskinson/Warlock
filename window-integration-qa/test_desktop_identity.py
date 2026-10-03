#!/usr/bin/env python3
"""Installed desktop helper rejects stale queued targets before any mutation."""
import unittest
from test_windowctl import Environment, window

class DesktopIdentity(unittest.TestCase):
    def setUp(self):
        owner = {**window('0xaaa', stable_id='owner-1'), 'pid':42}
        self.env = Environment([owner])
        self.env.virtual_desktops('list')
        self.env.virtual_desktops('new')

    def tearDown(self):
        self.env.close()

    def test_listing_and_valid_captured_move(self):
        result, _ = self.env.virtual_desktops('list')
        listed = next(w for d in result['desktops'] for w in d['windows'])
        self.assertEqual((listed['stableId'], listed['pid']), ('owner-1', 42))
        _, state = self.env.virtual_desktops('move', '0xaaa', '2', 'owner-1', '42')
        self.assertEqual(state['clients'][0]['workspace']['name'], '2')

    def test_old_identity_and_wrong_process_do_not_dispatch(self):
        for identity, pid in [('owner-old', '42'), ('owner-1', '43')]:
            with self.subTest(identity=identity, pid=pid):
                before = self.env.state
                self.env.virtual_desktops('move', '0xaaa', '2', identity, pid, expected=2)
                self.assertEqual(self.env.state, before)

    def test_minimized_stale_target_does_not_rewrite_home(self):
        self.env.run('minimize', '0xaaa')
        home = self.env.root / 'runtime/hypr-windowctl/0xaaa'
        before, metadata = self.env.state, home.read_bytes()
        self.env.virtual_desktops('move', '0xaaa', '2', 'owner-old', '42', expected=2)
        self.assertEqual(self.env.state, before)
        self.assertEqual(home.read_bytes(), metadata)

    def test_rejected_new_move_does_not_create_ghost_desktop(self):
        catalog = self.env.root / 'home/.config/omarchy/virtual-desktops.json'
        before, metadata = self.env.state, catalog.read_bytes()
        self.env.virtual_desktops('new-move', '0xaaa', 'owner-old', '42', expected=2)
        self.assertEqual(self.env.state, before)
        self.assertEqual(catalog.read_bytes(), metadata)

if __name__ == '__main__':
    unittest.main()

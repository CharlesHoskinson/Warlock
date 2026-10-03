import unittest
from cursor_fixture import require_invisible_private_cursor, require_deterministic_owned_raster


class PrivateRasterStateTests(unittest.TestCase):
    def test_missing_or_unset_cursor_option_refuses(self):
        class Session:
            def __init__(self, value): self.value = value
            def data(self, *args):
                assert args == ('getoption', 'cursor:invisible')
                return self.value
        for row in ({}, {'bool': True}, {'bool': False, 'set': True}, {'bool': True, 'set': False}):
            with self.subTest(row=row), self.assertRaises(AssertionError):
                require_invisible_private_cursor(Session(row))
        self.assertEqual(require_invisible_private_cursor(Session({'bool': True, 'set': True})),
                         {'bool': True, 'set': True})

    def test_missing_enabled_or_error_state_refuses(self):
        for rows in ([], [{'event': 'outputs'}], [{'event': 'rasterState'}],
                     [{'event': 'rasterState', 'ditherAfter': True, 'error': 0}],
                     [{'event': 'rasterState', 'ditherAfter': False, 'error': 1282}]):
            with self.subTest(rows=rows), self.assertRaises(AssertionError):
                require_deterministic_owned_raster(rows)

    def test_actual_reported_disabled_state_is_required(self):
        state = {'event': 'rasterState', 'ditherBefore': True, 'ditherAfter': False, 'error': 0}
        self.assertIs(require_deterministic_owned_raster([{'event': 'backendObserved'}, state]), state)


if __name__ == '__main__': unittest.main()

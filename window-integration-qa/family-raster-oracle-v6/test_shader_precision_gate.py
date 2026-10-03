import copy
import unittest
from precision_fixture import require_explicit_high_precision


class ShaderPrecisionGateTests(unittest.TestCase):
    def vector(self):
        return {'event': 'shaderPrecision', 'supported': True, 'error': 0,
                'observed': [{'stage': s, 'kind': k, 'precisionBits': 23 if k == 'high' else 10,
                              'rangeMin': 127 if k == 'high' else 15, 'rangeMax': 127 if k == 'high' else 15}
                             for s in ('vertex', 'fragment') for k in ('low', 'medium', 'high')]}

    def test_missing_or_failed_actual_diagnostic_refuses(self):
        good = self.vector()
        for rows in ([], [{'event': 'gpu'}], [dict(good, supported=False)], [dict(good, error=1280)]):
            with self.subTest(rows=rows), self.assertRaises(AssertionError):
                require_explicit_high_precision(rows)

    def test_incomplete_or_duplicate_stage_vector_refuses(self):
        good = self.vector()
        duplicate = copy.deepcopy(good['observed']); duplicate[5] = copy.deepcopy(duplicate[2])
        for values in (good['observed'][:-1], duplicate):
            with self.subTest(values=values), self.assertRaises(AssertionError):
                require_explicit_high_precision([dict(good, observed=values)])

    def test_claimed_support_cannot_replace_measured_range_and_bits(self):
        for stage in ('vertex', 'fragment'):
            for field, value in (('precisionBits', 22), ('rangeMin', 126), ('rangeMax', 126)):
                row = self.vector()
                next(x for x in row['observed'] if x['stage'] == stage and x['kind'] == 'high')[field] = value
                with self.subTest(stage=stage, field=field), self.assertRaises(AssertionError):
                    require_explicit_high_precision([row])

    def test_complete_measured_vector_is_retained(self):
        row = self.vector()
        self.assertIs(require_explicit_high_precision([row]), row)


if __name__ == '__main__': unittest.main()

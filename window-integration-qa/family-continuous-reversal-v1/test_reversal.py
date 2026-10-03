"""Adversarial event evidence fixtures; these are not native execution evidence."""
import copy
import unittest
from verify_reversal import verify

IDS = [{'stableId': str(i), 'pid': 42} for i in (1, 2, 3)]
SOURCES = [dict(r, digest=str(i) * 64) for i, r in enumerate(IDS, 1)]
TOKENS = ['abcdef123456-' + str(i) for i in (1, 2, 3)]


def fixture():
    events = [dict(event='uploaded', digest=s['digest'], pixels=[100, 100], uploadCount=i)
              for i, s in enumerate(SOURCES, 1)]
    events.append(dict(event='seeded', token=TOKENS[0], identities=IDS,
                       sourceDigests=SOURCES, nativeAuthority=False))
    rect = dict(x=10, y=20, width=100, height=100)
    members = [dict(s, rectangle=rect) for s in SOURCES]
    for i, value in enumerate(TOKENS, 1):
        if i > 1:
            previous = next(r for r in reversed(events) if r['event'] == 'presented')
            events.append(dict(event='retargetAccepted', token=value, identities=IDS,
                               sourceDigests=SOURCES, nativeAuthority=False))
            origin = {k: previous[k] for k in ('output', 'generation', 'sequence', 'timestampNs', 'rectangle', 'members')}
            events.append(dict(event='retargeted', token=value, origins=[origin],
                               identities=IDS, sourceDigests=SOURCES,
                               sourceReused=True, nativeAuthority=False, uploadCount=3))
        frame = dict(token=value, sequence=str(i), output='WAYLAND-1', generation=6,
                     members=members, rectangle=rect, progress=.4,
                     timestampNs=str(100 + i), endpoint=False)
        events.append(dict(frame, event='swap', success=True))
        events.append(dict(frame, event='presented', accepted=True))
    frame = dict(frame, sequence='4', timestampNs='104', progress=1, endpoint=True)
    events.extend([dict(frame, event='swap', success=True),
                   dict(frame, event='presented', accepted=True),
                   dict(event='endpoint', token=TOKENS[-1], identities=IDS,
                        sourceDigests=SOURCES, servicePromoted=True)])
    return copy.deepcopy(events)


class ReversalEvidence(unittest.TestCase):
    def refuse(self, mutate):
        events = fixture()
        mutate(events)
        with self.assertRaises(ValueError):
            verify(events, IDS)

    def test_complete_fixture_scopes_acceptance(self):
        answer = verify(fixture(), IDS)
        self.assertEqual(len(answer['reversals']), 2)
        self.assertFalse(answer['nativeCommitAccepted'])
        self.assertFalse(answer['physicalCadenceAccepted'])

    def test_missing_second_reversal(self):
        self.refuse(lambda es: es.__setitem__(slice(None), [e for e in es if not (e['event'].startswith('retarget') and e['token'] == TOKENS[2])]))

    def test_wrong_origin_sequence(self):
        self.refuse(lambda es: next(e for e in es if e['event'] == 'retargeted')['origins'][0].update(sequence='99'))

    def test_wrong_origin_member_rectangle(self):
        def mutate(es):
            e = next(e for e in es if e['event'] == 'retargeted')
            e['origins'] = copy.deepcopy(e['origins'])
            e['origins'][0]['members'][0]['rectangle']['x'] = 999
        self.refuse(mutate)

    def test_wrong_origin_timestamp(self):
        self.refuse(lambda es: next(e for e in es if e['event'] == 'retargeted')['origins'][0].update(timestampNs='0'))

    def test_output_generation_change(self):
        self.refuse(lambda es: next(e for e in es if e['event'] == 'retargeted')['origins'][0].update(generation=7))

    def test_missing_output_origin(self):
        self.refuse(lambda es: next(e for e in es if e['event'] == 'retargeted').update(origins=[]))

    def test_duplicate_origin(self):
        def mutate(es):
            origins = next(e for e in es if e['event'] == 'retargeted')['origins']
            origins.append(copy.deepcopy(origins[0]))
        self.refuse(mutate)

    def test_failed_swap(self):
        self.refuse(lambda es: next(e for e in es if e['event'] == 'swap').update(success=False))

    def test_duplicate_swap(self):
        self.refuse(lambda es: es.append(copy.deepcopy(next(e for e in es if e['event'] == 'swap'))))

    def test_unknown_presented_token(self):
        def mutate(es):
            for e in es:
                if e.get('sequence') == '2':
                    e['token'] = 'abcdef123456-99'
        self.refuse(mutate)

    def test_receipt_serial_regression(self):
        self.refuse(lambda es: next(e for e in es if e['event'] == 'retargetAccepted').update(token=TOKENS[0]))

    def test_changed_receipt_prefix(self):
        self.refuse(lambda es: next(e for e in es if e['event'] == 'retargetAccepted').update(token='fedcba123456-2'))

    def test_retarg_applied_twice(self):
        def mutate(es):
            index = next(i for i, e in enumerate(es) if e['event'] == 'retargeted')
            es.insert(index + 1, copy.deepcopy(es[index]))
        self.refuse(mutate)

    def test_second_seed_is_recapture(self):
        self.refuse(lambda es: es.append(copy.deepcopy(next(e for e in es if e['event'] == 'seeded'))))

    def test_extra_texture_upload(self):
        self.refuse(lambda es: es.append(copy.deepcopy(es[0])))

    def test_wrong_uploaded_source(self):
        self.refuse(lambda es: es[0].update(digest='f' * 64))

    def test_retarg_claims_native_authority(self):
        self.refuse(lambda es: next(e for e in es if e['event'] == 'retargetAccepted').update(nativeAuthority=True))

    def test_retarg_does_not_reuse_source(self):
        self.refuse(lambda es: next(e for e in es if e['event'] == 'retargeted').update(sourceReused=False))

    def test_stale_endpoint(self):
        self.refuse(lambda es: es[-1].update(token=TOKENS[0]))

    def test_unpresented_final_endpoint(self):
        self.refuse(lambda es: es.__setitem__(slice(None), [e for e in es if not (e['event'] == 'presented' and e.get('endpoint'))]))

    def test_endpoint_is_not_an_interior_reversal(self):
        def mutate(es):
            for e in es:
                if e.get('sequence') == '1':
                    e['progress'] = 1
        self.refuse(mutate)

    def test_original_actual_baseline_is_insufficient(self):
        from pathlib import Path
        import json
        body = json.loads(Path('/home/hoskinson/window-integration-qa/family-service-taskbar-v8/attempt-1/service-evidence.json').read_text())
        events = body['transports'][0]['events']
        identities = next(e['identities'] for e in events if e['event'] == 'seeded')
        with self.assertRaisesRegex(ValueError, 'reversals missing'):
            verify(events, identities)


if __name__ == '__main__':
    unittest.main()

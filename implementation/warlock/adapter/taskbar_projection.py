"""Join validated native facts around a snapshot without inventing scene authority."""
def coherent_scene(before, snapshot, after):
    # Snapshot revision belongs to its own namespace. The bracketing facts
    # revision includes grouping, ownership, native focus and visibility.
    if before['revision'] != after['revision'] or before['outputGeneration'] != after['outputGeneration']:
        return None
    facts = {w['incarnation']: w for w in after['facts']['windows']}
    if set(facts) != {w['incarnation'] for w in snapshot['windows']}:
        return None
    if any(w['minimized'] != facts[w['incarnation']]['minimized'] or w['application'] != facts[w['incarnation']]['application'] for w in snapshot['windows']):
        return None
    return {'revision': after['revision'], 'focused': after['facts']['focused'], 'windows': [
        {**w, 'owner': facts[w['incarnation']]['owner'],
         'available': not facts[w['incarnation']]['hidden']
                      and facts[w['incarnation']]['workspace'] is not None and int(facts[w['incarnation']]['workspace']) > 0}
        for w in snapshot['windows']]}

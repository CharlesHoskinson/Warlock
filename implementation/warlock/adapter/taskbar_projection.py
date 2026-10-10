"""Join validated native facts around a snapshot without inventing scene authority."""
def coherent_scene(before, snapshot, after):
    # Snapshot revision belongs to its own namespace. The bracketing facts
    # revision includes grouping, ownership, native focus and visibility.
    if before['revision'] != after['revision'] or before['outputGeneration'] != after['outputGeneration']:
        return None
    if before.get('attentionProtocol')!=after.get('attentionProtocol') or before['facts']!=after['facts']:
        return None
    facts = {w['incarnation']: w for w in after['facts']['windows']}
    if set(facts) != {w['incarnation'] for w in snapshot['windows']}:
        return None
    if any(w['minimized'] != facts[w['incarnation']]['minimized'] or w['application'] != facts[w['incarnation']]['application'] for w in snapshot['windows']):
        return None
    focus = after['facts']['focused']
    focused_member = facts.get(focus)
    # Desktop focus can outlive presentation of its workspace after output
    # retirement. It cannot make that member the active primary Minimize target.
    # Do not consult keyboard focus: bar/popup custody keeps a visible desktop
    # family active. Raw native facts and native effect admission stay intact.
    if focused_member is None or focused_member['hidden'] or focused_member['minimized'] or not focused_member['workspaceVisible'] or focused_member['workspace'] is None or int(focused_member['workspace']) <= 0:
        focus = None
    return {'revision': after['revision'], 'focused': focus, 'windows': [
        {**w, **({'attention': facts[w['incarnation']]['attention']} if after.get('attentionProtocol')==1 else {}), 'owner': facts[w['incarnation']]['owner'],
         'available': not facts[w['incarnation']]['hidden']
                      and facts[w['incarnation']]['workspace'] is not None and int(facts[w['incarnation']]['workspace']) > 0}
        for w in snapshot['windows']]}

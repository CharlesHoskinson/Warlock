"""Bind each diagnostic causal copy to the current observed prefix and target.

Configuration evidence only; the existing full-pixel oracle is authoritative.
"""


def verify_target(record, frame, copy_program, copy_state):
    keys = ('token', 'sequence', 'output', 'generation', 'bufferWidth', 'bufferHeight', 'members')
    if any(record.get(k) != frame.get(k) or type(record.get(k)) is not type(frame.get(k)) for k in keys):
        raise ValueError('causal copy immutable frame binding differs')
    if type(record.get('readFramebuffer')) is not int or record['readFramebuffer'] != 0:
        raise ValueError('causal read must use actual owned default target')
    if record.get('nativeAuthority') is not False or record.get('presentationProof') is not False:
        raise ValueError('diagnostic causal read has unexpected authority')
    passes = frame.get('passes')
    if not isinstance(passes, list) or not passes:
        raise ValueError('current complete prefix passes absent')
    groups, group = [], []
    for entry in passes:
        if not isinstance(entry, dict) or type(entry.get('prefixCount')) is not int:
            raise ValueError('prefix pass index is not an integer')
        if entry['prefixCount'] == 1 and group:
            groups.append(group)
            group = []
        if entry['prefixCount'] != len(group) + 1:
            raise ValueError('prefix pass order has a gap or repetition')
        group.append(entry)
    groups.append(group)
    family = groups[-1]
    if len(family) != len(frame['members']) or any(p.get('controlIndex') != -1 for p in family):
        raise ValueError('complete ordered family pass vector absent')
    if record.get('kind') == 'member-prefix':
        count = record.get('prefixCount')
        if type(count) is not int or not 1 <= count <= len(family) or record.get('controls') != []:
            raise ValueError('causal family prefix index differs')
        chosen = family[count - 1]
    elif record.get('kind') == 'constant-control':
        controls = record.get('controls')
        if record.get('prefixCount') != 0 or not isinstance(controls, list) or not controls:
            raise ValueError('causal control vector absent')
        indices = [c.get('index') for c in controls if isinstance(c, dict)]
        if len(indices) != len(controls) or any(type(i) is not int for i in indices):
            raise ValueError('causal control indices differ')
        matching = [g for g in groups[:-1] if [p.get('controlIndex') for p in g] == indices]
        if len(matching) != 1:
            raise ValueError('control copy has no unique ordered pass vector')
        count, chosen = len(controls), matching[0][-1]
    else:
        raise ValueError('unknown causal read kind')
    if type(record.get('observedPrefixCount')) is not int or record['observedPrefixCount'] != count:
        raise ValueError('causal copy observed prefix count differs')
    texture = record.get('prefixTexture')
    if type(texture) is not int or texture <= 0 or texture != chosen.get('writeTexture'):
        raise ValueError('causal copy source is not the matching current prefix')
    copy_state(record.get('readTargetCopy'), 0, texture,
               [frame['bufferWidth'], frame['bufferHeight']], copy_program)
    return {'sequence': frame['sequence'], 'output': frame['output'], 'generation': frame['generation'],
            'kind': record['kind'], 'observedPrefixCount': count, 'prefixTexture': texture,
            'readFramebuffer': 0, 'actualCausalTargetBound': True,
            'pixelProof': False, 'nativeAuthority': False}

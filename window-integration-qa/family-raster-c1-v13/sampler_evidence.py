"""Read-only actual sampler configuration binding; configuration is not pixels."""
POLICY = 'four-nearest-centers-highp-bilinear-v1'


def fragment_digest(header):
    import hashlib
    material = header.read_bytes()
    opening = b'inline constexpr const char* manualFragment = R"GLSL('
    closing = b')GLSL";'
    if material.count(opening) != 1:
        raise ValueError('Exact explicit raw shader literal required')
    tail = material.split(opening, 1)[1]
    if tail.count(closing) != 1:
        raise ValueError('Exact explicit raw shader terminator required')
    return hashlib.sha256(tail.split(closing, 1)[0]).hexdigest()


def verify_sampler(events, sources, shader_digest):
    modes = [e for e in events if e.get('event') == 'samplingExperiment']
    if len(modes) != 1 or modes[0].get('policy') != POLICY or modes[0].get('fragmentSHA256') != shader_digest:
        raise ValueError('Exact frozen sampler experiment shader required')
    if (modes[0].get('rasterDiagnostic') is not True or modes[0].get('nativeAuthority') is not False
            or modes[0].get('pixelProof') is not False):
        raise ValueError('Sampler experiment must retain diagnostic-only authority')
    rows = [e for e in events if e.get('event') == 'samplingConfigured']
    source_rows = [e for e in rows if e.get('controlIndex') == -1]
    controls = [e for e in rows if e.get('controlIndex') in (0, 1, 2)]
    if len(rows) != 6 or len(source_rows) != 3 or len(controls) != 3:
        raise ValueError('Complete unique family and control sampler vector required')
    if [(e.get('sourceDigest'), e.get('pixels')) for e in source_rows] != [(s['digest'], s['pixels']) for s in sources]:
        raise ValueError('Actual source sampler order/digest/extent differs')
    if sorted(e['controlIndex'] for e in controls) != [0, 1, 2]:
        raise ValueError('All predetermined controls required')
    textures = []
    for row in rows:
        texture = row.get('textureId')
        if type(texture) is not int or texture <= 0 or texture in textures:
            raise ValueError('Positive distinct actual texture IDs required')
        textures.append(texture)
        if (row.get('policy') != POLICY or row.get('minFilter') != 9728 or row.get('magFilter') != 9728
                or row.get('wrapS') != 33071 or row.get('wrapT') != 33071
                or row.get('inspectionError') != 0 or row.get('nativeAuthority') is not False
                or row.get('pixelProof') is not False or row.get('extentUniform') != row.get('pixels')):
            raise ValueError('Actual manual nearest/center/extent configuration differs')
        if row in controls and (row.get('sourceDigest') != '' or row.get('pixels') != [1, 1]):
            raise ValueError('Control sampler cannot claim snapshot source authority')
    return {'policy': POLICY, 'shaderDigest': shader_digest, 'sourceConfiguration': source_rows,
            'controlConfiguration': controls, 'configurationAccepted': True, 'pixelProof': False}

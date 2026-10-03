"""Independent diagnostic configuration gate; never presentation/pixel proof."""
from collections import Counter
import hashlib
import re

POLICY = 'four-nearest-centers-highp-bilinear-v1'


def fragment_digest(header):
    match = re.search(r'manualFragment = R"GLSL\((.*?)\)GLSL";', header, re.S)
    if not match:
        raise ValueError('exact frozen experiment fragment absent')
    return hashlib.sha256(match.group(1).encode()).hexdigest()


def verify(events, source_material, expected_fragment_digest):
    configs = [e for e in events if e.get('event') == 'samplingConfigured']
    shaders = [e for e in events if e.get('event') == 'samplingExperiment']
    if len(shaders) != 1 or shaders[0] != {
        'event': 'samplingExperiment', 'policy': POLICY,
        'fragmentSHA256': expected_fragment_digest, 'rasterDiagnostic': True,
        'nativeAuthority': False, 'pixelProof': False,
    }:
        raise ValueError('frozen explicit shader configuration not observed')
    family = []
    controls = []
    seen = set()
    for e in configs:
        if (e.get('policy') != POLICY or e.get('nativeAuthority') is not False
                or e.get('pixelProof') is not False):
            raise ValueError('diagnostic sampling policy/authority mismatch')
        tid = e.get('textureId')
        if type(tid) is not int or not 1 <= tid <= 0xffffffff or tid in seen:
            raise ValueError('exact unique upload texture IDs required')
        seen.add(tid)
        p = e.get('pixels')
        if (not isinstance(p, list) or len(p) != 2 or
                any(type(n) is not int or not 1 <= n <= 8192 for n in p)):
            raise ValueError('actual immutable upload extent required')
        u = e.get('extentUniform')
        if (not isinstance(u, list) or len(u) != 2 or
                any(isinstance(n, bool) or not isinstance(n, (int, float)) for n in u)
                or u != p):
            raise ValueError('queried shader extent differs from actual source')
        required = {'minFilter': 9728, 'magFilter': 9728, 'wrapS': 33071,
                    'wrapT': 33071, 'inspectionError': 0}
        if any(type(e.get(k)) not in (int, float) or isinstance(e[k], bool) or e[k] != v
               for k, v in required.items()):
            raise ValueError('actual queried nearest/clamp state or GL error differs')
        c = e.get('controlIndex')
        if type(c) is not int:
            raise ValueError('exact source/control discrimination required')
        if c == -1:
            digest = e.get('sourceDigest')
            if re.fullmatch(r'[0-9a-f]{64}', digest or '') is None:
                raise ValueError('complete immutable family source digest required')
            family.append((digest, tuple(p)))
        elif c in (0, 1, 2):
            if e.get('sourceDigest') != '' or p != [1, 1]:
                raise ValueError('controls cannot masquerade as family pixels')
            controls.append(c)
        else:
            raise ValueError('unrecognized control index')
    expected = [(s['digest'], tuple(s['pixels'])) for s in source_material]
    if Counter(family) != Counter(expected) or sorted(controls) != [0, 1, 2]:
        raise ValueError('every exact family source and all fixed controls required')
    return {'policy': POLICY, 'familyTextureCount': len(family), 'controlTextureCount': 3,
            'actualGetterGate': True, 'pixelProof': False, 'nativeAuthority': False}

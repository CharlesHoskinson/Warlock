"""Exact reviewed C1 source packet authority; no native launch."""
from pathlib import Path
import hashlib
import json
import os
import stat

QA=Path('/home/hoskinson/window-integration-qa')
PRODUCER=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/producer-continuous-dev-v13')
PACKET=PRODUCER/'source-ready.json'
REVIEW=QA/'producer-c1-v13-root-source-review.json'
PACKET_SHA='2e8205fff740072eaf2903e4ce17bd8ad594765932dc0c6b8d7b9b7ec1f44414'
REVIEW_SHA='5c139a7a67b018300dc8f33c976f7369525f9d8216d7a1b4d5a535c6bd018b99'
BINARY_SHA='824173e2e1461a0f32bb101ee8daa6e6de09b6eb48f4484f07bc64510db0a02c'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verified_packet():
    if sha(PACKET)!=PACKET_SHA or sha(REVIEW)!=REVIEW_SHA:
        raise ValueError('Exact independent C1 source review changed')
    packet=json.loads(PACKET.read_text())
    for name,value in packet['inputs'].items():
        if sha(name)!=value or stat.S_IMODE(Path(name).stat().st_mode)!=packet['inputModes'][name]:
            raise ValueError('C1 source/loader byte or mode changed: '+name)
    for name,value in packet['links'].items():
        if not Path(name).is_symlink() or os.readlink(name)!=value:
            raise ValueError('C1 loader link changed: '+name)
    if packet['binary']!=str(PRODUCER/'hypr-motion-renderer-staged') or packet['binarySHA256']!=BINARY_SHA:
        raise ValueError('C1 candidate binary selection changed')
    packet['inputs'].update({str(PACKET):PACKET_SHA,str(REVIEW):REVIEW_SHA})
    packet['inputModes'].update({str(p):stat.S_IMODE(p.stat().st_mode) for p in (PACKET,REVIEW)})
    return packet

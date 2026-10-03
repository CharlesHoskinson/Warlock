"""Freeze a fresh diagnostic collector after producer/root source review."""
from pathlib import Path
import hashlib
import json
import os
import stat
import c1_pairing

B=Path(__file__).resolve().parent
QA=B.parent
P=c1_pairing.PRODUCER


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    old=QA/'family-raster-production-default-v12'
    previous=json.loads((old/'frozen-inputs.json').read_text())
    packet=c1_pairing.verified_packet()
    inputs={};links={};modes={}
    for source in (previous,packet):
        for name,digest in source['inputs'].items():
            if sha(name)!=digest:raise RuntimeError('Frozen input drift: '+name)
            if name in inputs and inputs[name]!=digest:raise RuntimeError('Conflicting source packets: '+name)
            inputs[name]=digest
        for name,mode in source.get('inputModes',{}).items():
            if stat.S_IMODE(Path(name).stat().st_mode)!=mode:raise RuntimeError('Frozen mode drift: '+name)
            modes[name]=mode
        links.update(source.get('symlinks',source.get('links',{})))
    for name,target in links.items():
        if not Path(name).is_symlink() or os.readlink(name)!=target:raise RuntimeError('Frozen link drift: '+name)
    for name in ('raster_oracle.py','compare_scene.py','producer_observer.py','readback_evidence.py','private-nested.lua'):
        if (B/name).read_bytes()!=(old/name).read_bytes():raise RuntimeError('Original oracle/source/geometry/readback changed: '+name)
    for path in (old/'frozen-inputs.json',old/'attempt-1/report.json',old/'attempt-1/root-completion.json',c1_pairing.PACKET,c1_pairing.REVIEW,QA/'crash-handoff-v5/review.json'):
        inputs[str(path)]=sha(path)
    for path in B.rglob('*'):
        if path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and not any(x.startswith('attempt-') for x in path.parts) and path.name!='frozen-inputs.json':
            inputs[str(path)]=sha(path)
    modes.update({name:stat.S_IMODE(Path(name).stat().st_mode) for name in inputs})
    row={'inputs':inputs,'inputModes':modes,'symlinks':links,'producerManifestSHA256':sha(c1_pairing.PACKET),
         'previousQuantizedManifestSHA256':sha(old/'frozen-inputs.json'),
         'same44OriginalImageComparisonsRequired':True,'mainChanges':False,'nativeAccepted':False,'physicalCadenceAccepted':False}
    with (B/'frozen-inputs.json').open('x') as stream:json.dump(row,stream,indent=2);stream.write('\n')
    (B/'frozen-inputs.json').chmod(0o600)
    print(json.dumps({'frozen':True,'inputs':len(inputs),'links':len(links),'manifestSHA256':sha(B/'frozen-inputs.json'),'nativeLaunch':False}))


if __name__=='__main__':main()

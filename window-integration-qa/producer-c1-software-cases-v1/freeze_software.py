"""Freeze source-only software campaign after C1 pair review; no launch."""
from pathlib import Path
import hashlib
import json
import os
import stat
import c1_pairing
B=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    inputs={};modes={};links={}
    for source in [c1_pairing.verified_packet(),
            json.loads((B.parent/'family-continuous-c1-v4/frozen-inputs.json').read_text()),
            json.loads((B.parent/'family-raster-c1-v13/frozen-inputs.json').read_text())]:
        for name,value in source['inputs'].items():
            if sha(name)!=value or (name in inputs and inputs[name]!=value):raise ValueError('Exact paired source changed: '+name)
            inputs[name]=value
        modes.update(source['inputModes']);links.update(source.get('links',source.get('symlinks',{})))
    for name,value in modes.items():
        if stat.S_IMODE(Path(name).stat().st_mode)!=value:raise ValueError('Paired mode changed')
    for name,value in links.items():
        if not Path(name).is_symlink() or os.readlink(name)!=value:raise ValueError('Paired link changed')
    for source in [B.parent/'family-continuous-c1-v4/frozen-inputs.json',B.parent/'family-raster-c1-v13/frozen-inputs.json',*B.rglob('*')]:
        if source.is_file() and not source.is_symlink() and '__pycache__' not in source.parts and not any(p.startswith('attempt-') for p in source.parts) and source.name!='frozen-inputs.json':inputs[str(source)]=sha(source)
    modes.update({name:stat.S_IMODE(Path(name).stat().st_mode) for name in inputs})
    row=dict(inputs=inputs,inputModes=modes,symlinks=links,sourceOnly=True,nativeExecuted=False,mainWrites=False,physicalCadenceAccepted=False,producerSourcePacketSHA256=c1_pairing.PACKET_SHA,producerRootReviewSHA256=c1_pairing.REVIEW_SHA)
    with (B/'frozen-inputs.json').open('x') as output:json.dump(row,output,indent=2);output.write('\n')
    (B/'frozen-inputs.json').chmod(0o600)
    print(json.dumps(dict(frozen=True,inputs=len(inputs),links=len(links),nativeLaunch=False,sha256=sha(B/'frozen-inputs.json'))))
if __name__=='__main__':main()

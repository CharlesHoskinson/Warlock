"""Run through protected QA; freeze final derivative without altering initial audit."""
import datetime,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];repo=root.parents[1]
manifest=root/'audits/final-plan-manifest.json'
paths=sorted(p for base in [root,repo/'docs/research/elm-pivot',repo/'openspec'] for p in base.rglob('*') if p.is_file() and p!=manifest)
report=dict(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),branch='feature/elm',scope='Final planning derivative, scoped source corpus and CPU prototypes; no deployed implementation acceptance',registrySHA256=hashlib.sha256((root/'requirements.json').read_bytes()).hexdigest(),files=[dict(path=str(p.relative_to(repo)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths])
manifest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(files=len(paths),bytes=sum(x['bytes'] for x in report['files']),registrySHA256=report['registrySHA256'])))

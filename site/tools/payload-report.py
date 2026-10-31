#!/usr/bin/env python3
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',default='.');a=p.parse_args();root=Path(a.root).resolve()
files=[x for x in root.rglob('*') if x.is_file() and 'design' not in x.parts and '.git' not in x.parts]
print('Published candidate bytes:',sum(x.stat().st_size for x in files))
for x in sorted(files,key=lambda x:x.stat().st_size,reverse=True)[:20]:print(x.stat().st_size,x.relative_to(root))
for x in files:
 rel=x.relative_to(root).as_posix()
 if '/qa/' in '/'+rel or 'elm-stuff/' in rel or '/build-' in rel:print('REVIEW: possible QA/build-tree copy:',rel)
home=root/'index.html'
if home.exists():
 for line in home.read_text().splitlines():
  if any(s in line for s in ('test-drive/runtime/','test-drive/bootstrap.js','desktop-stage.js','elm.js')):print('REVIEW: possible initial desktop bundle load:',line.strip()[:240])

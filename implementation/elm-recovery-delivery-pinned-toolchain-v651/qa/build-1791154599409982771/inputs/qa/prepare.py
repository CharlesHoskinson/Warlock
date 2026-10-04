import hashlib,json,pathlib,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];DEST=ROOT/'qa/toolchain';DEST.mkdir()
SOURCE=pathlib.Path('/home/hoskinson/.npm/_npx/84e76f4d63d5907c');HOME=pathlib.Path('/home/hoskinson/.elm/0.19.2/packages');pins={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['package.json','package-lock.json','node_modules/.package-lock.json']:
 source=SOURCE/name;target=DEST/'npm-package'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);pins[str(source)]={'sha256':sha(source),'size':source.stat().st_size}
for name in ['node_modules/elm','node_modules/@elm_binaries/linux_x64']:
 source=SOURCE/name;target=DEST/'npm-package'/name;shutil.copytree(source,target)
 for p in source.rglob('*'):
  if p.is_file():pins[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
meta=json.loads((SOURCE/'node_modules/elm/package.json').read_text());assert meta['version']=='0.19.2-0'
packageRoot=DEST/'elm-home/0.19.2/packages';packageRoot.mkdir(parents=True)
registry=HOME/'registry.dat';shutil.copy2(registry,packageRoot/'registry.dat');pins[str(registry)]={'sha256':sha(registry),'size':registry.stat().st_size}
config=json.loads((ROOT/'elm.json').read_text());deps={**config['dependencies']['direct'],**config['dependencies']['indirect']}
for name,version in deps.items():
 source=HOME/name/version;target=packageRoot/name/version;shutil.copytree(source,target)
 for p in source.rglob('*'):
  if p.is_file():pins[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
held={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in DEST.rglob('*') if p.is_file()}
compiler=DEST/'npm-package/node_modules/@elm_binaries/linux_x64/elm';assert sha(compiler)==sha(DEST/'npm-package/node_modules/elm/bin/elm')
for p,row in pins.items():assert sha(pathlib.Path(p))==row['sha256']
out={'passed':True,'compiler':str(compiler.relative_to(ROOT)),'compilerSHA256':sha(compiler),'elmHome':str((DEST/'elm-home').relative_to(ROOT)),'npmPackageVersion':meta['version'],'elmDependencies':deps,'heldFiles':held,'originalCacheFiles':pins,'claim':'Actual resolved cached ELF compiler/package files and exact seven Elm dependency/cache/registry bytes copied and pinned; no global configuration edit or retroactive640 provenance'};(ROOT/'qa/toolchain.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':True,'compilerSHA256':sha(compiler),'heldFiles':len(held),'dependencyPackages':len(deps)}))

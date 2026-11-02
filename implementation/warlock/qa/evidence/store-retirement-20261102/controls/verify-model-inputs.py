import hashlib,json
from pathlib import Path
base=Path(__file__).resolve().parent
def sha(p):
 with Path(p).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
m=json.loads((base/'store-model-manifest.json').read_text());pin=json.loads((base/'model-toolchain.json').read_text());rows={};root=base/'model-toolchain/quint'
for p in sorted(root.rglob('*')):
 n=str(p.relative_to(root))
 if p.is_symlink():rows[n]={'symlink':p.readlink().as_posix(),'sha256':sha(p) if p.is_file() else None}
 elif p.is_file():rows[n]={'sha256':sha(p)}
assert len(rows)==pin['files'] and hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()==pin['treeSHA256']
assert sha(base/'model-toolchain/node')==pin['nodeSHA256']
observed={}
for row in m['canonicalModels'].values():
 observed[row['localName']]=sha(base/row['localName']);assert observed[row['localName']]==row['sha256']
observed['store-retirement-guided.qnt']=sha(base/'store-retirement-guided.qnt');assert observed['store-retirement-guided.qnt']=='0330d9588b101055ec57eda98939a42b806c429749556eea21a800f988670eb3'
print(json.dumps(dict(modelInputs=observed,quintFiles=len(rows),quintTreeSHA256=pin['treeSHA256'],nodeSHA256=pin['nodeSHA256'],postInputsMatch=True,nativeAccepted=False)))

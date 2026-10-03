from pathlib import Path
import hashlib,json,re,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
from source_relevance import selected_aliases
B=Path(__file__).resolve().parent
P=Path('/home/hoskinson/window-behavior-spec/qml-process-provider-v2-async/product-capture-runtime-1790969789274993790.json')
M=Path('/home/hoskinson/window-behavior-spec/qml-object-lifetime-v5-popup/source-ready-inputs.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 require_qa_scope();r=json.loads(P.read_text());native=json.loads(r['stdout']);e=native['state']['evidence'];sample=e['workerCollection']['epochs'][0];raw=sample['rawMaps'];images={m.group(1)for line in raw.splitlines()if(m:=re.match(r'^[^ ]+ +[^ ]+ +[^ ]+ +[^ ]+ +[^ ]+ +(/.*)$',line))};manifest=json.loads(M.read_text());aliases,unresolved=selected_aliases(images,{'/usr/bin/env','/usr/bin/python3','/usr/bin/python3.14'},manifest['symlinks']);out=dict(schema='actual-retained-map-frozen-reference-attribution-v1',inputs={str(p):sha(p)for p in [P,M,B/'source_relevance.py',Path(__file__)]},inventoryLinkCount=len(manifest['symlinks']),actualCapturedDiskPaths=sorted(images),actualCapturedRawMapsSHA256=hashlib.sha256(raw.encode()).hexdigest(),selectedLiteralAliases={a:manifest['symlinks'][a]for a in aliases},selectedAliasCount=len(aliases),unresolvedFrozenInventoryReferences=unresolved,actualFullInventoryBefore=sample['fullInventoryLinksBefore'],observerBeforeMicroseconds=sample['observerBeforeMicroseconds'],actualNativeExit=e['actualNativeExitSignal'],kernelAccepted=False,runtimePredicateChanged=False,GUI=False,claim='retained failed live sample attribution only; no source FD/lifetime acceptance')
 p=B/'actual-reference-attribution.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(artifact=str(p),images=len(images),selectedAliases=len(aliases),inventory=len(manifest['symlinks']),unresolved=len(unresolved))))
if __name__=='__main__':main()

from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();core=json.loads((B/'process-cpu-build.json').read_text());old=json.loads((B/'fast-capture-first-attempt/product-capture-build.json').read_text());assert core['result']==old['result']=='pass';changed={str(B/'MappingBatch.cpp'),str(B/'product_capture_once.py')}
 assert all(sha(p)==h for p,h in old['sources'].items()if p not in changed);assert all(sha(p)==h for p,h in core['dependencies'].items()if p not in changed)
 commands=[next(v['command']for v in core['commands']if '-c'in v['command']and str(B/'MappingBatch.cpp')in v['command']),old['commands'][-1]['command']];before={str(p):sha(p)for p in B.iterdir()if p.suffix in('.cpp','.hpp','.py')};rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 stable=all(sha(p)==h for p,h in before.items());good=len(rows)==2 and all(r['exitCode']==0 for r in rows)and stable;row=dict(result='pass'if good else'fail',sources=before,sourceUnchanged=stable,commands=rows,explicitSourceChanges={p:dict(before=old['sources'][p],after=sha(p))for p in changed},GUI=False,verifiedPriorProductBuildSHA256=sha(B/'fast-capture-first-attempt/product-capture-build.json'),registryBuildSHA256=sha(B/'process-cpu-build.json'))
 if good:row['binarySHA256']=sha(B/'cpu-product-capture');row['objectSHA256']={str(p):sha(p)for p in(B/'process-build').glob('*.o')}
 p=B/('product-capture-build.json'if good else f'product-capture-diagnostic-build-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())

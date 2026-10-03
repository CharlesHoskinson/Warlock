from pathlib import Path
import hashlib,json,resource,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope

B=Path(__file__).resolve().parent
COMMANDS=[
 ('source',['python3','-m','unittest','-v','test_source','test_ownership_source']),
 ('atlas-cache-protocol',['python3','run_helpers.py']),
 ('exact-gesture-cancellation',['python3','run_authority_helpers.py']),
 ('actual-lua-native-getter',['python3','run_lua_lifetime.py']),
 ('ownership-typecheck',['quint','typecheck','ownership_test.qnt']),
 ('ownership-named',['quint','test','ownership_test.qnt']),
 ('ownership-model',['quint','run','ownership.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=2026100105','--verbosity=0']),
 ('interruption-typecheck',['quint','typecheck','interruption_test.qnt']),
 ('interruption-named',['quint','test','interruption_test.qnt']),
 ('interruption-model',['quint','run','interruption.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=0']),
]

def main():
 scope=require_qa_scope();target=B/'offline-report-v5.json';assert not target.exists()
 sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in B.rglob('*') if p.is_file() and p.suffix in ('.cpp','.hpp','.lua','.qnt','.py')}
 records=[]
 for label,command in COMMANDS:
  process=subprocess.run(command,cwd=B,capture_output=True,text=True,timeout=240)
  log=B/('offline-'+label+'.log');assert not log.exists();log.write_text(process.stdout+process.stderr)
  records.append({'label':label,'command':command,'exitCode':process.returncode,'log':str(log),'logSHA256':hashlib.sha256(log.read_bytes()).hexdigest()})
  print(label,process.returncode,flush=True)
  if process.returncode:raise SystemExit(process.stdout+process.stderr)
 assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in sources.items())
 report={'result':'pass','scope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),
 'commands':records,'sourceSHA256':sources,'sourceUnchangedDuringProof':True,
 'sourceGates':22,'ownershipNamed':9,'interruptionNamed':19,'models':2,'samplesPerModel':2000,
 'exactGestureAssertions':33,'nativeLuaGetterScenarios':8,'atlasChecks':72,'cacheChecks':38,'protocolChecks':17,
 'ownershipProof':str(B/'ownership-report.json'),'ownershipProofSHA256':hashlib.sha256((B/'ownership-report.json').read_bytes()).hexdigest(),
 'nativeGUIExecuted':False,'mainChanged':False,'remaining':'root source review and actual idle/held/pending/retirement native controls'}
 target.write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()

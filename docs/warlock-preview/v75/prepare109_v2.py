"""Read native manifest schema correctly; require actual accepted native report."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
p=pathlib.Path('/home/hoskinson/omarchy-windows-parity/docs/warlock-preview/v75/prepare109.py');s=p.read_text();old="assert d['passed'] and not t.exists()";assert s.count(old)==1
s=s.replace(old,"assert d['sourceHeld'] and d['evidenceIntegrityPassed'] and not t.exists();accepted=json.loads(next(p.glob('qa/native-*/report.json')).read_text());assert accepted['passed'] and accepted['cleanupPassed'] and len(accepted['checks'])==2416 and len(accepted['ownedExitCodes'])==269 and all(row['exitCode']==0 for row in accepted['ownedExitCodes'])")
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})

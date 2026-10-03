#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
scope=require_qa_scope();results=[]
for name in ('test_lifecycle-independent','test_version-independent'):
 path=B/name;run=subprocess.run([str(path)],capture_output=True,text=True,timeout=10)
 results.append({'binary':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'exitCode':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
report={'result':'pass' if all(row['exitCode']==0 for row in results) else 'fail','scopeEvidence':scope,'inheritedCoreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'tests':results,'nativeGuiLaunched':False}
path=B/'independent-model-evidence/scoped-cpp-report.json';assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n');path.chmod(0o600)
print(json.dumps(report,indent=2));raise SystemExit(report['result']!='pass')

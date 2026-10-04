"""Replay actual263 reporting inconsistency through new aggregate gate."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from cleanup import cleanup_passed
ROOT=Path(__file__).resolve().parent;source=ROOT.parents[1]/'elm-gtk-post-bus-retirement-v263/qa/native-1791145436509122699/report.json';data=json.loads(source.read_text());evidence=data['cleanup'];assert data['cleanupPassed'] is True and evidence['privateActivationCleanupPassed'] is False
assert cleanup_passed(evidence) is False
out=ROOT/('cleanup-regression-'+str(time.time_ns()));out.mkdir();report={'passed':True,'nativeAcceptance':False,'actualHistoricalCleanupWasIncorrectlyTrue':True,'correctedCleanupPassed':False,'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'cleanup.py',source]}};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')

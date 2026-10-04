"""Retain the actual failed usability requirements against compiled V132 output."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'qa/review-1791119213760603058/checks.json';actual=json.loads(source.read_text());assert actual['passed']
checks=[]
for operation in ['minimize','restore-geometry']:
 row=actual['traces'][operation];checks.append({'name':operation+' proven local non-submission must not retain indefinitely Pending native-issued mapping','passed':row['issued']==[] and row['unresolvedFull']==[],'actual':{'issued':row['issued'],'unresolved':row['unresolvedFull'],'submitted':row['submitted']}})
row=actual['traces']['readCapacity'];checks.append({'name':'proven local non-submission must not retain unmatched expected observation IDs','passed':row['correlation']['legacy'] is None and row['correlation']['geometry'] is None,'actual':row['correlation']})
OUT=ROOT/'qa'/('usability-'+str(time.time_ns()));OUT.mkdir();report={'passed':all(c['passed'] for c in checks),'scope':'Required usability assertions deliberately fail on unchanged V132; no fix, GUI, certificate or native effect execution','nativeAcceptance':False,'checks':checks,'input':str(source.relative_to(ROOT)),'inputSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])

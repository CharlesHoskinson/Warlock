import ast,json,subprocess,sys,time,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native

out=native.ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Protected source/compiled closure and inert host import only'}
try:
    host,meta,pointer,inputs=native.preflight()
    ast.parse((native.ROOT/'qa/native.py').read_text());ast.parse((native.FIXTURE/'qa/backend.py').read_text())
    for name in ('driver.js','inspect.js'):
        result=subprocess.run(['node','--check',str(native.FIXTURE/'qa'/name)],capture_output=True,text=True,timeout=10)
        assert result.returncode==0,result.stderr
    report.update(passed=True,inputs=inputs,verifiedInputs=len(inputs),nativePair=meta,physicalInputClient=pointer)
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if report['passed']:(native.ROOT/'qa/review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}))
sys.exit(0 if report['passed'] else 1)

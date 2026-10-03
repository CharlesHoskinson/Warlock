"""Read back the already executed exact ABI proof without overwriting it."""
from pathlib import Path
import hashlib,json
from run_focus_abi import SHIM,CASES
from run_retirement_ownership import block
B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((B/'focus-abi-report.json').read_text())
source=B/'native-candidate/dragBridge.cpp';text=source.read_text()
exact=block(text,'struct GestureCapture')+';\nstd::optional<GestureCapture> gesture;\n'+block(text,'bool sameGesture')+'\n'+block(text,'bool preserveCapturedGestureFocus')
assert report['result']=='pass' and report['compileReturnCode']==0
assert report['execute']=={'exitCode':0,'stdout':'27 exact focus guard ABI assertions PASS\n','stderr':''}
assert sha(source)==report['candidateSourceSHA256']
assert hashlib.sha256(exact.encode()).hexdigest()==report['extractedSourceSHA256']
assert (B/'focus-build/test.cpp').read_text()==SHIM+exact+CASES
assert all(sha(Path(p))==h for p,h in report['dependencies'].items())
assert report['nativeGUIExecuted'] is False and report['mainChanged'] is False
print('27 retained exact focus ABI assertions/source/dependencies verified')

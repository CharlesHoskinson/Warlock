from pathlib import Path
import hashlib,json
base=Path(__file__).resolve().parents[1]
source=base/'native/pointer_native-v8.hpp'
s=source.read_text()
ranges=[('void rotatePointerOwner(', 'std::string pointerRegistration('),('std::string pointerRegistration(', 'DBusConnection* axBus='),('void reconcilePointerOwners()', 'struct AxRef'),('void pollPointerNotifications()', 'void queryPointer('),('void pointerRetire()', 'void pointerCleanup()')]
out='// Exact staged production-function bodies; deterministic transport adapter below.\n'
for begin,end in ranges:
    out+=s[s.index(begin):s.index(end,s.index(begin))]+'\n'
(base/'owner-lifecycle-v2/actual_functions.inc').write_text(out)
(base/'owner-lifecycle-v2/source-extraction.json').write_text(json.dumps({'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'extractSha256':hashlib.sha256(out.encode()).hexdigest(),'functions':[r[0] for r in ranges]},indent=2)+'\n')

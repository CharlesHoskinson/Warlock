import hashlib,json,os,resource,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=REPO/'implementation/elm-shared-navigation-diagnostics-v366';old=REPO/'implementation/elm-shared-keyboard-recovery-merge-v359'
changed=[]
for folder in ['src','native','adapter','assets']:
 for p in sorted((old/folder).rglob('*')):
  if p.is_file():
   rel=p.relative_to(old)
   if sha(p)!=sha(s/rel):changed.append(str(rel))
assert changed==['native/shared-host.c'],changed
build=s/'qa/build-1791120445608298072/report.json';b=json.loads(build.read_text());assert b['passed']
for rel,digest in b['inputs'].items():assert sha(s/rel)==digest,rel
native=REPO/'implementation/elm-shared-navigation-diagnostics-native-v367/qa/native-1791120483118572951/report.json';n=json.loads(native.read_text());assert n['passed'] and n['cleanupPassed'] and len(n['checks'])==48
files=[];special=[]
for name in ['elm-shared-navigation-diagnostics-v366','elm-shared-navigation-diagnostics-native-v367',ROOT.name]:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(p));files.append(row)
  elif stat.S_ISREG(st.st_mode):row.update(size=st.st_size,sha256=sha(p));files.append(row)
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
prior=REPO/'implementation/elm-shared-keyboard-recovery-evidence-v365/qa/slice-manifest.json'
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps({'passed':True,'scope':'Read-only diagnostic source and one strict native48 pass; intermittent predecessor failure remains open','files':files,'specialFiles':special,'finalSource':str(s.relative_to(REPO)),'behaviorChanges':False,'diagnosticChanges':changed,'priorPacket':str(prior.relative_to(REPO)),'priorPacketSHA256':sha(prior),'nativeReport':str(native.relative_to(REPO)),'nativeReportSHA256':sha(native),'nativeChecks':48,'cleanupPassed':True,'renderTransitionQualified':False,'completedRequirementIds':[],'fullReleaseAccepted':False},indent=2)+'\n');print(str(p))

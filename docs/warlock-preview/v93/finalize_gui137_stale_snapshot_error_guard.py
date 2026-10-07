"""Finalize intact held manifests with a unique report name; preserve Native137."""
import hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();docs=r/'docs/warlock-preview/v93';gui=r/'implementation/warlock-preview-provider-v137'
historical=docs/'component-report137.json';old=json.loads(historical.read_text());assert old['passed'] and old['nativeChecks']==26 and 'warlock-preview-provider-v126' in old['reports']['build']['path'];oldsha=sha(historical)
for name,count in [('warlock-preview-provider-v137',36),('warlock-client-provider-native-v160',29),('warlock-client-provider-native-v161',36),('warlock-client-provider-native-v162',35),('warlock-client-provider-native-v163',18),('warlock-client-provider-native-v164',51)]:
 root=r/'implementation'/name;d=json.loads((root/'component-manifest.json').read_text());assert d['passed'] and d['sourceHeld'] and d['nativeChecks']==count and not d['currentMatchingErrorNativeQualified'] and not d['fullReleaseAccepted']
 for n,row in d['files'].items():assert sha(root/n)==row['sha256'] and (root/n).stat().st_size==row['size'],n
 for n,row in d['reports'].items():assert sha(pathlib.Path(row['path']))==row['sha256'],n
common=json.loads((gui/'component-manifest.json').read_text());common={k:v for k,v in common.items() if k not in {'files','nativeChecks','normalOwnedExits'}}
common['freezeFinalization']={'reason':'Initial freezer validated all source/build/model/native evidence and wrote all six immutable manifests, then stopped rather than overwrite pre-existing historical Native137 report. Unique GUI report finalizes those unchanged manifests; no source/probe/oracle/deadline/test rerun or historical evidence modification.','historicalReport':str(historical),'historicalReportSHA256':oldsha}
out=docs/'component-report-gui137-stale-error.json';assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n');assert sha(historical)==oldsha
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS heldGUI137 final audit of all six unchanged source/build/native manifests after report-name collision, historical Native137 preserved. Real canceled old result fixed: unchanged Native16136/13, normal16029/13/success16235/13/delayed16318/8/rapid16451/17/full119/Quint10/200/4 actual projected cases. Matching current error source unchanged but real current-error native gate still open. Next PUBLIC100 then that control and remaining async/physical/recovery/release gates. Installed drafts foreign preserved.'],'progress',[str(out.relative_to(r)),str((gui/'component-manifest.json').relative_to(r))]))

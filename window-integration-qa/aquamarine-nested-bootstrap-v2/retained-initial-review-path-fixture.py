"""Read-only ELF/source and formal proofs; never loads the candidate library."""
from pathlib import Path
import hashlib,json,subprocess,os,re
B=Path(__file__).resolve().parent;Q=B.parent;OLD=Q/'aquamarine-nested-lifecycle-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
 row=dict(command=cmd,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr)
 records.append(row)
 if p.returncode:raise RuntimeError(row)
 return p.stdout
def exported(p):return {line.split()[-1] for line in run(['/usr/bin/nm','-D','--defined-only',str(p)]).splitlines() if line.split()}
records=[];report={}
try:
 for name,invariant,count in [('configure_lifecycle','safe',15),('nested_selection','safe',12),('version_guard','validBinding and truthfulRefusal',5)]:
  run(['quint','test',str(B/(name+'.qnt'))]);run(['quint','run',str(B/(name+'.qnt')),'--invariant',invariant,'--max-steps','100','--max-samples','2000','--seed','20261001','--verbosity','1'])
 old=json.loads((B/'source-before-bootstrap-patch.json').read_text())
 # The retained snapshot uses candidate-relative paths.
 files=old.get('inputs',old.get('sources',old))
 if 'candidate' in files:files=files['candidate']
 changed=[]
 for name,digest in files.items():
  path=Path(name) if Path(name).is_absolute() else B/'candidate'/name
  if sha(path)!=digest:changed.append(str(path.relative_to(B/'candidate')))
 assert changed==['src/backend/Wayland.cpp'],changed
 oldraw=(OLD/'candidate/src/backend/Wayland.cpp').read_text();newraw=(B/'candidate/src/backend/Wayland.cpp').read_text()
 delta='''    // Initial empty xdg commit is queued after dispatchEvents() above. Flush it
    // before returning: no parent readability may arrive until this is sent.
    // Any negative result (including EAGAIN) refuses mandatory private startup.
    if (wl_display_flush(waylandState.display) < 0) {
        backend->log(AQ_LOG_ERROR, std::format("Wayland initial output flush failed: errno {}", errno));
        return false;
    }

'''
 assert newraw.count(delta)==1 and newraw.replace(delta,'')==oldraw
 hosts={}
 for prior,fresh,find,repl in [('private-weston-aq-host-v4','private-weston-aq-bootstrap-host-v5','aquamarine-nested-lifecycle-v1','aquamarine-nested-bootstrap-v2'),('private-weston-x11-host-v2','private-weston-x11-bootstrap-host-v3','private-weston-aq-host-v4','private-weston-aq-bootstrap-host-v5')]:
  before=(Q/prior/'weston_host.py').read_bytes();after=(Q/fresh/'weston_host.py').read_bytes()
  assert after.count(repl.encode())==1 and after.replace(repl.encode(),find.encode())==before
  hosts[fresh]=dict(sha256=sha(Q/fresh/'weston_host.py'),reconstructsExactOriginal=True)
 assert (Q/'private-weston-x11-host-v2/x11_authority.py').read_bytes()==(Q/'private-weston-x11-bootstrap-host-v3/x11_authority.py').read_bytes()
 lib=B/'prefix/lib/libaquamarine.so.0.15.0';oldlib=OLD/'prefix/lib/libaquamarine.so.0.15.0'
 exports=exported(lib);oldexports=exported(oldlib)
 aq=lambda s:{x for x in s if 'Aquamarine' in x}
 missing=sorted(aq(oldexports)-exports);assert not missing,missing
 headers={str(p.relative_to(OLD/'prefix/include')):p.read_bytes()==(B/'prefix/include'/p.relative_to(OLD/'prefix/include')).read_bytes() for p in (OLD/'prefix/include').rglob('*') if p.is_file()};assert all(headers.values()) and len(headers)==18
 needed=[x.split()[-1] for x in run(['/usr/bin/nm','-D','--undefined-only','/usr/bin/Hyprland']).splitlines() if x.split() and 'Aquamarine' in x];assert not(set(needed)-exports)
 report.update(result='pass',candidateSHA256=sha(lib),candidateExports=len(exports),oldExports=len(oldexports),missingAquamarineAPI=missing,missingDirectHyprlandImports=sorted(set(needed)-exports),headersByteIdentical=headers,soleSourceDelta=changed,inverseBootstrapSourceExact=True,hostSelectors=hosts,inheritedNamedCount=32,inheritedModels=3,inheritedSamples=6000,nativeLoaded=False,nativeLaunched=False,actualFailedWireCauseProved=False)
except BaseException as e:report.update(result='fail',error=repr(e))
report['records']=records
with (B/'source-abi-formal-checkpoint.json').open('x') as out:json.dump(report,out,indent=2);out.write('\n')
(B/'source-abi-formal-checkpoint.json').chmod(0o600)
print(json.dumps({k:v for k,v in report.items() if k!='records'}));raise SystemExit(report['result']!='pass')

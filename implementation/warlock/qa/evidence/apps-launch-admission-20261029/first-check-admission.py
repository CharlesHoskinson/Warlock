#!/usr/bin/env python3
"""Private compiled controller/native transport regression; no native acceptance."""
import hashlib,json,os,pathlib,shlex,shutil,subprocess,sys,tempfile
R=pathlib.Path('/home/charles/Warlock'); P=R/'implementation/warlock'; H=R/'implementation/warlock-preview-provider-v143'; HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(R/'window-integration-qa'))
from qa_launch import require_qa_scope
PINS={'LaunchAdmissionReplay.elm':'a7f0b55fd279c17ba734262836359ffd7d850c87a1d8336ac8150ab61e02f08c','preflight.c':'e12de4f580b4fb448213067698c0112a7c5eba235faf6155cc322ec7d6a82a13','run-replay.cjs':'2b38c8e5e2e9c756a56496a8ca74dd35e9fe9f53bf59b517804399a2d2ee0f03'}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
 report={'passed':False,'nativeAcceptance':False,'scope':'Compiled Elm OutputController packet into actual host transport preflight only; no shared-batch/backend authority or GUI proof','commands':[]}
 def run(args,cwd,env=None):
  q=subprocess.run([str(a) for a in args],cwd=cwd,env=env,capture_output=True,text=True,timeout=240);report['commands'].append({'argv':[str(a) for a in args],'cwd':str(cwd),'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr});
  if q.returncode:raise RuntimeError('command failed: '+str(args[0]))
  return q.stdout
 try:
  report['protectedScope']=require_qa_scope()
  for n,v in PINS.items():assert sha(HERE/n)==v,n
  assert sha(P/'src/Desktop.elm')=='a503d926599b5aa194956a1208fdc0004fb829442cd523c5372d41fd1fab0404'
  assert sha(P/'native/host.c')=='f78d1ba337dff920e50e79e7324d5467cfbfe240a3b4d03c7d4239f52b17850a'
  assert sha(P/'qa/OutputRetirementReplay.elm')=='fc288be90c83b37ad007bfe4fe8a7224bbd2359773aa599a2bc97bbeddb152b9'
  assert sha(H/'qa/toolchain.json')=='fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'
  manifest=json.loads((H/'qa/toolchain.json').read_text());assert len(manifest['heldFiles'])==111
  def verify():
   for n,v in manifest['heldFiles'].items():assert (H/n).stat().st_size==v['size'] and sha(H/n)==v['sha256'],n
  verify();compiler=H/manifest['compiler'];assert sha(compiler)==manifest['compilerSHA256']
  sources={str(p):sha(p) for p in sorted((P/'src').rglob('*.elm'))};sources.update({str(p):sha(p) for p in [P/'native/host.c',P/'native/surface.h',P/'qa/OutputRetirementReplay.elm',P/'elm.json',*(HERE/n for n in PINS)]});report['sourceHashes']=sources
  with tempfile.TemporaryDirectory(prefix='warlock-admission-') as t:
   t=pathlib.Path(t);ws=t/'workspace';ws.mkdir();(ws/'src').symlink_to(P/'src',target_is_directory=True);(ws/'qa').symlink_to(P/'qa',target_is_directory=True);(ws/'private').mkdir();shutil.copyfile(HERE/'LaunchAdmissionReplay.elm',ws/'private/LaunchAdmissionReplay.elm')
   elm=json.loads((P/'elm.json').read_text());elm['source-directories']=['src','qa','private'];(ws/'elm.json').write_text(json.dumps(elm));home=t/'elm-home';shutil.copytree(H/manifest['elmHome'],home);env={**os.environ,'ELM_HOME':str(home),'PYTHONDONTWRITEBYTECODE':'1'}
   run([compiler,'make','private/LaunchAdmissionReplay.elm','--optimize','--output='+str(t/'worker.js')],ws,env);report['compiledSHA256']=sha(t/'worker.js')
   packet=run(['node',HERE/'run-replay.cjs',t/'worker.js'],ws,env);(t/'packet.json').write_text(packet);report['elmPacket']=json.loads(packet);report['elmPacketSHA256']=sha(t/'packet.json')
   original=run(['git','show','338f8cd1b8272b6ab7a3228469adea08d7844f82:implementation/warlock/native/host.c'],R);(t/'host-old.c').write_text(original);assert sha(t/'host-old.c')=='cde6230199756dfaa193d5e8af5a41470f8b65de3cdd1942e0e0224ab458ccbf'
   flags=shlex.split(run(['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],R))
   for label,source in [('old',t/'host-old.c'),('new',P/'native/host.c')]:
    run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-ffunction-sections','-fdata-sections','-I'+str(P/'native'),'-DHOST_SOURCE="'+str(source)+'"',HERE/'preflight.c','-Wl,--gc-sections','-o',t/label,*flags],R)
    report[label+'BinarySHA256']=sha(t/label);run([t/label,t/'packet.json',label],R)
   assert all(sha(p)==v for p,v in sources.items());verify()
  report['passed']=True
 except Exception as e:report['error']=repr(e)
 print(json.dumps(report,indent=2));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())

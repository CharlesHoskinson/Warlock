"""Protected compile of actual prototype; original oracle counts unclaimed."""
import hashlib,json,pathlib,shutil,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def main():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 scope=require_qa_scope();out=ROOT/'qa'/('compile-'+str(time.time_ns()));out.mkdir();paths=[*(ROOT/'src').glob('*.elm'),ROOT/'elm.json',ROOT/'upstream.json',ROOT/'SPEC.md',pathlib.Path(__file__).resolve()];sources={str(p):digest(p) for p in paths};report={'passed':False,'nativeAcceptance':False,'modelAcceptance':False,'scope':'Actual Main/Popup Elm prototype compilation only; old oracle counts not claimed','qaScope':scope,'sources':sources,'commands':[]}
 for p in paths:
  dest=out/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 try:
  for name in ['Main','Popup','MenuSurfaceReplay']:
   command=['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/'+name+'.elm','--output='+str(out/(name+'.js'))];result=subprocess.run(command,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr);report['commands'].append({'command':command,'exitCode':result.returncode});assert result.returncode==0,result.stderr
  for p,value in sources.items():assert digest(p)==value,p
  report['passed']=True
 except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
 report['artifacts']={str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file()};path=out/'report.json';path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(path),'error':report.get('error')}),flush=True);return not report['passed']
if __name__=='__main__':raise SystemExit(main())

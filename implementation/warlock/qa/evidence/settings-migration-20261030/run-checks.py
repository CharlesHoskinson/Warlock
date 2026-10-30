import hashlib,json,pathlib,subprocess,sys,time
root=pathlib.Path('/home/charles/Warlock')
out=pathlib.Path(__file__).parent/('checks-'+str(time.time_ns()));out.mkdir()
results=[]
for name in ['check-settings.py','check-settings-migration.py']:
 p=root/'implementation/warlock/qa'/name
 result=subprocess.run([sys.executable,'-B',str(p)],cwd=root,capture_output=True,text=True)
 (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr)
 results.append({'name':name,'sourceSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'exitCode':result.returncode})
report={'passed':all(x['exitCode']==0 for x in results),'checks':results,'storeSHA256':hashlib.sha256((root/'implementation/warlock/adapter/shell_preferences.py').read_bytes()).hexdigest()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out);print(json.dumps(report));assert report['passed']

import hashlib,json,pathlib,subprocess,sys,time
root=pathlib.Path('/home/charles/Warlock');out=pathlib.Path(__file__).parent/('process-cuts-'+str(time.time_ns()));out.mkdir()
p=root/'implementation/warlock/qa/check-settings-migration-crash.py'
r=subprocess.run([sys.executable,'-B',str(p)],cwd=root,capture_output=True,text=True)
(out/'stdout').write_text(r.stdout);(out/'stderr').write_text(r.stderr)
report={'passed':r.returncode==0,'exitCode':r.returncode,'runnerSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'storeSHA256':hashlib.sha256((root/'implementation/warlock/adapter/shell_preferences.py').read_bytes()).hexdigest(),'scope':'Abrupt process-exit witnesses; no hardware power-loss or original acceptance.'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out);print(json.dumps(report));assert report['passed']

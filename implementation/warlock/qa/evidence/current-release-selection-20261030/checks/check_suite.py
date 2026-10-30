import json,pathlib,subprocess,sys
p=pathlib.Path(__file__).resolve().parent
commands=[['/usr/bin/python3','-B',str(p/'check_composition.py'),'--mode','test','--frontend-report',str(p.parent/'pin-scrollport-build-root-v1/report.json'),'--frontend-sha256','65b909422a1866a9df8f118b134ea42778fd69564aed070bdb92c0975f3818d8','--lock',str(p.parent/'current-native-capture-1793327475166710937/native-lock.json'),'--sha256','159926b838187ef3d3b610ed119673293f138da9a53e4f382e787f3f69ad9afb'],['/usr/bin/python3','-B',str(p/'check_selection.py')]]
rows=[]
for i,cmd in enumerate(commands):
 r=subprocess.run(cmd,capture_output=True,timeout=240)
 (p/('suite-'+str(i)+'.stdout')).write_bytes(r.stdout);(p/('suite-'+str(i)+'.stderr')).write_bytes(r.stderr)
 rows.append(dict(command=cmd,exit=r.returncode));print(r.stdout.decode(),flush=True)
 if r.returncode:break
report=dict(passed=len(rows)==2 and all(x['exit']==0 for x in rows),commands=rows,nativeAcceptance=False,releaseAccepted=False)
(p/'suite-report.json').write_text(json.dumps(report,indent=2)+'\n');sys.exit(0 if report['passed'] else 1)

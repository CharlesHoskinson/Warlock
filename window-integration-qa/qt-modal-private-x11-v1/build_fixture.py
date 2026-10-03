#!/usr/bin/env python3
"""Compile observation-only Qt fixture; never start the resulting GUI client."""
from pathlib import Path
import hashlib,json,resource,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
scope=require_qa_scope();output=B/'qt-build-report.json';assert not output.exists()
commands=[['cmake','-S',str(B),'-B',str(B/'build-v7'),'-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',str(B/'build-v7'),'--parallel','2']]
results=[]
for command in commands:
 result=subprocess.run(command,text=True,capture_output=True);results.append({'command':command,'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
 if result.returncode:break
binary=B/'build-v7/qt-window-modal-fixture'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'result':'compiled' if all(r['exitCode']==0 for r in results) and len(results)==2 else 'fail','qtWidgetsVersion':'6.11.2 EXACT','qaBuildScope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'commands':results,'sourceSHA256':sha(B/'fixture.cpp'),'binarySHA256':sha(binary) if binary.exists() else None,'originalQt203BinarySHA256':sha(B/'build/qt-window-modal-fixture'),'nativeExecuted':False,'sourceDelta':'Observation-only Resize/Move/LayoutRequest snapshot refresh and QVBoxLayout geometry; window creation, command actions, callback code unchanged.'}
output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':report['result'],'binarySHA256':report['binarySHA256'],'reportSHA256':sha(output),'scope':scope}));raise SystemExit(report['result']!='compiled')

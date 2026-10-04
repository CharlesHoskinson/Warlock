import ast,hashlib,json,pathlib,subprocess,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];BASE=ROOT.parent/'elm-qt6-full-driver-surface-transform-v313';out=ROOT/'qa'/('mutation-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False}
try:
 source=(BASE/'qa/helpers/scene.py').read_text();node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='same');body=ast.get_source_segment(source,node);(out/'original-same.py').write_text(body+'\n');(out/'unsafe-same.py').write_text(body.replace("'marker',",'').replace("'action'","'identity'")+'\n')
 p=subprocess.run(['/usr/bin/python3','-B',str(ROOT/'qa/test.py'),'--unsafe-omit-mapping'],capture_output=True,text=True);(out/'stdout').write_text(p.stdout);(out/'stderr').write_text(p.stderr);assert p.returncode==1,p.stdout+p.stderr
 result=json.loads(p.stdout.strip().split('\n')[-1]);assert result['passed'] is False and result['error']=="AssertionError('left-map-change-actual-method-refuses')",result
 report.update(passed=True,unsafeControlRejected=True,actualUnsafeReport=result['report'],originalSourceSHA256=hashlib.sha256(source.encode()).hexdigest())
except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc())
(out/'mutation.py').write_bytes(pathlib.Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'error':report.get('error')}));raise SystemExit(0 if report['passed'] else 1)

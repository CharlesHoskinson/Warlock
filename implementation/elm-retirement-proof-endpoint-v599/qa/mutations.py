import pathlib,json,time,subprocess,shutil,ast,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir()
source=(ROOT/'adapter/grant_endpoint.py').read_text()
r={'passed':False,'controls':[],'scope':'Python decoder guard controls, synthetic transport only'}
mutations=[
 ('inflight-binding','if not self.bound or NativeBinding.parse(self.bound) != captured:','if False:'),
 ('caller-correlation','NativeBinding.parse(response[\'binding\']) != captured or','False or'),
 ('target-correlation','or NativeBinding.parse(response[\'queriedBinding\']) != target:','or False:'),
 ('request-correlation','if response[\'requestId\'] != request_id:','if False:'),
 ('operation-correlation','or response[\'operation\'] != operation:','or False:'),
 ('boolean-protocol','type(response[\'retirementProtocol\']) is not int or ','False or '),
 ('duplicate-proof','if sequence <= watermarks.get(captured.lifetime, 0):','if sequence < watermarks.get(captured.lifetime, 0):'),
 ('retired-only','if operation == \'retire\' and state != \'Retired\':','if False:'),
 ('future-release','return self.grant_state == \'Retired\'','return True')]
try:
 for name,before,after in mutations:
  assert source.count(before)==1,(name,source.count(before));body=source.replace(before,after);ast.parse(body)
  d=OUT/name;(d/'adapter').mkdir(parents=True);(d/'qa/fixtures').mkdir(parents=True)
  for filename in ['endpoint.py','effect_endpoint.py']:shutil.copyfile(ROOT/'adapter'/filename,d/'adapter'/filename)
  (d/'adapter/grant_endpoint.py').write_text(body)
  shutil.copyfile(ROOT/'qa/test.py',d/'qa/test.py');shutil.copyfile(ROOT/'qa/fixtures/native596-report.json',d/'qa/fixtures/native596-report.json')
  p=subprocess.run(['/usr/bin/python3','-B',str(d/'qa/test.py')],capture_output=True,text=True,timeout=30)
  (d/'stdout').write_text(p.stdout);(d/'stderr').write_text(p.stderr)
  rows=sorted((d/'qa').glob('test-*/report.json'));assert rows
  failed=json.loads(rows[-1].read_text());assert p.returncode==1 and not failed['passed'],(name,p.returncode,p.stdout,p.stderr)
  r['controls'].append({'name':name,'syntaxValid':True,'exitCode':p.returncode,'error':failed.get('error'),'report':str(rows[-1].relative_to(ROOT))})
 r.update(passed=True,mutantsRejected=len(mutations),endpointSHA256=hashlib.sha256(source.encode()).hexdigest())
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'mutants':len(r['controls']),'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

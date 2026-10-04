import ast,hashlib,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
SOURCE=REPO/'implementation/elm-durable-reservation-release-v608'
OUT=ROOT/'qa'/('controls-'+str(time.time_ns()));OUT.mkdir()
text=(SOURCE/'adapter/retirement_ledger.py').read_text()
mutants=[
 ('skip-restart-journal-barrier','try: os.fsync(self.fd)\n        except BaseException: self.poisoned=True; raise','try: pass\n        except BaseException: self.poisoned=True; raise'),
 ('skip-admission-absence-barrier','        os.fsync(directory)\n','        pass\n'),
 ('accept-future-proof',"proof['grantState'] != 'Retired'","proof['grantState'] not in ['Retired','Future']"),
 ('accept-bool-marker',"actual != expected or type(actual.get('schema')) is not int","actual != expected"),
 ('skip-inherited-fsync-poison','except OSError: self.poisoned=True; raise','except OSError: raise'),
 ('skip-cleanup-poison','except BaseException: self.poisoned=True; raise\n\n    def _remove_admission','except BaseException: raise\n\n    def _remove_admission'),
]
rows=[]
for name,old,new in mutants:
 assert text.count(old)==1,(name,text.count(old))
 candidate=OUT/name;candidate.mkdir()
 for directory in ['adapter','native']:
  shutil.copytree(SOURCE/directory,candidate/directory)
 (candidate/'qa').mkdir();shutil.copy2(SOURCE/'qa/test.py',candidate/'qa/test.py')
 changed=text.replace(old,new);ast.parse(changed)
 (candidate/'adapter/retirement_ledger.py').write_text(changed)
 p=subprocess.run([sys.executable,'-B',str(candidate/'qa/test.py')],capture_output=True,text=True,timeout=60)
 (candidate/'stdout.txt').write_text(p.stdout);(candidate/'stderr.txt').write_text(p.stderr)
 reports=list((candidate/'qa').glob('tests-*/report.json'));assert len(reports)==1
 report=json.loads(reports[0].read_text());failed=[r for r in report['checks'] if not r['passed']]
 assert p.returncode!=0 and not report['passed'] and failed,(name,'mutation escaped or harness failed without behavioral witness',report)
 rows.append({'name':name,'syntaxValid':True,'detected':True,'returncode':p.returncode,'behavioralCounterexample':failed[-1]['name'],'report':str(reports[0].relative_to(ROOT))})
result={'passed':True,'sourceSHA256':hashlib.sha256(text.encode()).hexdigest(),'mutations':rows,'claim':'Actual Python source mutations executed with actual compiled unchanged C admission producer; CPU only','nativeAcceptance':False}
(OUT/'report.json').write_text(json.dumps(result,indent=2));print(OUT/'report.json')

"""Apply actual unsafe oracle source changes; use the same external boundary suite."""
import ast,hashlib,json,resource,time,types
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];test=s/'qa/test.py';source=s/'oracle.py';out=s/'qa'/('mutations-'+str(time.time_ns()));out.mkdir()
# Extract the actual hand-authored fixture/suite without executing its report writer.
tree=ast.parse(test.read_text());keep=[]
for node in tree.body:
 if isinstance(node,(ast.Import,ast.ImportFrom,ast.FunctionDef)):keep.append(node)
 elif isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HISTORY_DEFAULT' for t in node.targets):keep.append(node)
namespace={};exec(compile(ast.Module(body=keep,type_ignores=[]),str(test),'exec'),namespace)
original=source.read_text();controls={
 'missing-history-type-guard':("    for previous in observed_serials:\n        integer(previous,0,2**32-1)\n",''),
 'missing-bool-option-guard':("    if type(diagnostic_nonzero) is not bool:raise Refused('diagnostic option domain')\n",''),
 'excluded-zero-history-bound':('        integer(previous,0,2**32-1)','        integer(previous,1,2**32-1)'),
 'truncated-history-upper-bound':('        integer(previous,0,2**32-1)','        integer(previous,0,2**31-1)')}
records=[]
for name,(old,new) in controls.items():
 assert original.count(old)==1,name
 candidate=original.replace(old,new);path=out/(name+'.py');path.write_text(candidate);module=types.ModuleType(name);exec(compile(candidate,str(path),'exec'),module.__dict__)
 try:namespace['suite'](module)
 except AssertionError as error:records.append({'name':name,'rejected':True,'firstFailedOracle':str(error),'sourceSHA256':hashlib.sha256(path.read_bytes()).hexdigest()})
 except module.Refused as error:records.append({'name':name,'rejected':True,'firstFailedOracle':'valid boundary refused: '+str(error),'sourceSHA256':hashlib.sha256(path.read_bytes()).hexdigest()})
 else:raise AssertionError('Unsafe source control passed:'+name)
report={'passed':True,'controls':records,'scope':'Four executed unsafe production-oracle source controls rejected by actual boundary fixtures; no native capture/GUI acceptance','sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'testSourceSHA256':hashlib.sha256(test.read_bytes()).hexdigest(),'scriptSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(out/'report.json'),'controls':len(records)}))

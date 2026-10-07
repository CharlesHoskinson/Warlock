"""Extend exact original lifetime oracles with readonly custody semantics."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v118')
def fresh(rel,text):
 p=root/rel;assert not p.exists();p.write_text(text)
s=(root/'native/persistent-policy-lifetime-fixture.cpp').read_text().replace('#include <fstream>','#include <fstream>\n#include <cstring>')
old='        } else if (op == "missing-visual-output") {';assert s.count(old)==1
s=s.replace(old,'        } else if (op == "visual-copy") {\n            char* first = nullptr;\n            ok = warlock_preview_policy_visual_projection(policy, &first, &error);\n            if (ok) {\n                const std::string original(first);\n                std::memset(first, \'!\', original.size());\n                ok = warlock_preview_policy_visual_projection(policy, &output, &error);\n                if (!ok || !output || original != output || first == output) std::abort();\n            }\n            g_free(first);\n'+old)
fresh('native/persistent-policy-lifetime-fixture-v2.cpp',s)
s=(root/'spec/native_policy_lifetime.qnt').read_text().replace('module native_policy_lifetime {','module readonly_policy_lifetime {').replace('TrustedClose|Destroy','TrustedClose|Destroy|ReadVisual|ForeignRead').replace('|Destroy=>"Destroy"','|Destroy=>"Destroy"|ReadVisual=>"ReadVisual"|ForeignRead=>"ForeignRead"').replace('else if(e==WrongThreadInvoke or e==WrongThreadClose)','else if(e==ReadVisual){...base,code:if(st.controlled and not(st.closed))0 else 6}\n  else if(e==WrongThreadInvoke or e==WrongThreadClose or e==ForeignRead)').replace('ForeignClose,TrustedClose,Destroy).oneOf()','ForeignClose,TrustedClose,Destroy,ReadVisual,ForeignRead).oneOf()').replace('s.code<=5','s.code<=6')
fresh('spec/readonly_policy_lifetime.qnt',s)
s=(root/'spec/native_policy_lifetime_tests.qnt').read_text().replace('native_policy_lifetime_tests','readonly_policy_lifetime_tests').replace('import native_policy_lifetime.* from "./native_policy_lifetime"','import readonly_policy_lifetime.* from "./readonly_policy_lifetime"')
tail=''' run absentAuthorityRefusesReadonly=init.then(fire(ReadVisual)).then(check(s.held and not(s.controlled) and s.code==6))
 run openAuthorityReadonlyKeepsModel=init.then(fire(Grant)).then(fire(ReadVisual)).then(check(s.held and s.controlled and not(s.closed) and s.code==0))
 run closedAuthorityRefusesReadonly=init.then(fire(Grant)).then(fire(TrustedClose)).then(fire(ReadVisual)).then(check(s.held and s.closed and s.code==6))
 run foreignThreadRefusesReadonly=init.then(fire(Grant)).then(fire(ForeignRead)).then(check(s.held and s.controlled and not(s.closed) and s.code==2))
 run refusedInputRetainsReadableProjection=init.then(fire(Grant)).then(fire(Malformed)).then(fire(ReadVisual)).then(check(s.held and s.controlled and not(s.closed) and s.code==0))
 run destroyedOwnerCannotRead=init.then(fire(Destroy)).then(fire(ReadVisual)).then(check(not(s.held) and s.code==1))
'''
assert s.endswith('}\n');fresh('spec/readonly_policy_lifetime_tests.qnt',s[:-2]+tail+'}\n')
s=(root/'qa/persistent-policy-lifetime-check.py').read_text().replace('persistent-policy-lifetime-check-','readonly-policy-lifetime-check-').replace('qa/persistent-policy-lifetime-check.py','qa/readonly-policy-lifetime-check.py').replace('native/persistent-policy-lifetime-fixture.cpp','native/persistent-policy-lifetime-fixture-v2.cpp').replace('native_policy_lifetime','readonly_policy_lifetime').replace('len(selected)==8','len(selected)==14').replace("glob('named-*.itf.json')))==8","glob('named-*.itf.json')))==14").replace('namedScenarios=8','namedScenarios=14').replace('assert body.count(old)==2','assert body.count(old)==3')
old=" report['boundaryChecks']=checks;report['originalInvalidInputs']=len(invalid)";assert s.count(old)==1
new=old+'''
 read={'op':'visual'}
 steps=[read,grant,status,read,{'op':'visual-copy'},status,{'op':'foreign-visual'},read,{'op':'missing-visual-output'},read,{'op':'invoke','input':'invalid'},read,status,closed,read,{'op':'close'},read,{'op':'missing-visual-output'}]
 _,rows=execute('readonly-boundaries',steps);readonly=0
 def readcheck(ok,label):
  global readonly
  assert ok,label
  readonly+=1
 for index,code,held_owner in [(0,6,True),(6,2,True),(8,1,True),(10,1,True),(14,6,True),(16,1,False),(17,1,False)]:readcheck(rows[index]=={'ok':False,'code':code,'held':held_owner},'Original readonly refusal with no output')
 visual=rows[2]['projection']['visuals']
 for index in [3,4,7,9,11]:readcheck(rows[index]['ok'] and rows[index]['projection']==visual,'Detached exact visual data remains after query/copy/refusal')
 readcheck(rows[2]['projection']==rows[5]['projection']==rows[12]['projection'],'Queries/caller mutation never change the original model or output')
 readcheck(set(visual)=={'visualProtocol','kind','binding','receiverEpoch','surface','previews'},'Only visual fields leave the private native diagnostic cache')
 readcheck(rows[15]=={'ok':True,'code':0,'held':False},'Original trusted-close policy destroys normally')
 report['readonlyBoundaryChecks']=readonly
'''
s=s.replace(old,new)
s=s.replace("'Destroy':{'op':'close'}", "'Destroy':{'op':'close'},'ReadVisual':{'op':'visual'},'ForeignRead':{'op':'foreign-visual'}")
old="   if 'projection' in row:assert row['projection']['realm']['controlled']==state['controlled'] and row['projection']['realm']['closed']==state['closed'] and row['projection']['models']==[],(path.name,index,state,row)";assert s.count(old)==1
new="""   if 'projection' in row:
    if state['history'] and state['history'][-1]=='ReadVisual':assert row['projection']=={'visualProtocol':1,'kind':'native-preview-visual',**domain,'surface':None,'previews':[]},(path.name,index,state,row)
    else:assert row['projection']['realm']['controlled']==state['controlled'] and row['projection']['realm']['closed']==state['closed'] and row['projection']['models']==[],(path.name,index,state,row)""";s=s.replace(old,new)
s=s.replace("('foreign-kind','&& name != \"status\")','&& name != \"status\" && name != \"foreign\")',None)","('foreign-kind','&& name != \"status\")','&& name != \"status\" && name != \"foreign\")',None),('foreign-read',close_guard,'/* missing readonly creator guard */','foreignThreadRefusesReadonly'),('closed-read','!self->controlled || self->closed','!self->controlled','closedAuthorityRefusesReadonly')")
old="  if name=='foreign-destroy':assert body.count(old)==3;where=body.index('gboolean warlock_preview_policy_close(');body=body[:where]+body[where:].replace(old,new,1)";assert s.count(old)==1
new="  if name in {'foreign-destroy','foreign-read'}:\n   assert body.count(old)==3;where=body.index('gboolean warlock_preview_policy_close(' if name=='foreign-destroy' else 'gboolean warlock_preview_policy_visual_projection(');body=body[:where]+body[where:].replace(old,new,1)";s=s.replace(old,new)
s=s.replace("'scope':'Actual creator-owned", "'scope':'Readonly visual queries run no JS and keep the original model unchanged, including detached caller-mutated copies, absent/closed/foreign/missing-output refusal. Six additive readonly Quint scenarios retain all eight original lifetime scenarios. Actual creator-owned")
ast.parse(s);fresh('qa/readonly-policy-lifetime-check.py',s);print(root/'qa/readonly-policy-lifetime-check.py')

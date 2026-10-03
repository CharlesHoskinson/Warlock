"""Draft typed decoder. Current-only native read proof, never effect authority."""
from decimal import Decimal
import json,re

POLICY='59a1485d5f900db177414814bae9577898d687d17f2dc6a533ecec40a21590d3'
MASKS=(19,27,147,83,3)

def require(ok,message):
 if ok is not True:raise ValueError(message)
def exact(a,b):
 if type(a)is not type(b):return False
 if type(a)is dict:return a.keys()==b.keys()and all(exact(a[k],b[k])for k in a)
 if type(a)is list:return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 return a==b
def fields(row,names):require(type(row)is dict and set(row)==set(names.split()),'exact observation fields')
def integer(v,lo,hi):require(type(v)is int and lo<=v<=hi,'typed bounded integer');return v
def boolean(v):require(type(v)is bool,'typed boolean');return v
def decimal(v):
 require(type(v)is str and re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?',v)is not None and len(v)<=64,'represented native scalar')
 n=Decimal(v);require(n.is_finite(),'finite native scalar');return n
def unsigned(v,positive=False):
 require(type(v)is str and re.fullmatch(r'0|[1-9][0-9]*',v)is not None and int(v)<=2**64-1 and (not positive or int(v)>0),'uint64 token');return v
def pointer(v,positive=False):
 require(type(v)is str and re.fullmatch(r'0x(?:0|[1-9a-f][0-9a-f]{0,15})',v)is not None and (not positive or int(v,16)>0),'canonical owning pointer');return v
def identity(row,nullable=False):
 if row is None and nullable:return None
 fields(row,'address stableId pid');pointer(row['address'],True)
 require(type(row['stableId'])is str and re.fullmatch(r'0|[1-9a-f][0-9a-f]{0,15}',row['stableId'])is not None,'stable public ID')
 integer(row['pid'],1,2**31-1);return row
def box(value):
 require(type(value)is list and len(value)==4,'native box shape')
 for v in value:decimal(v)
 return value
def unique(pairs):
 result={}
 for k,v in pairs:require(k not in result,'duplicate JSON field');result[k]=v
 return result

def scroll(row,target):
 if row is None:return
 fields(row,'owner controller selectedData selectedColumn offset direction columns')
 for k in ['owner','controller','selectedData','selectedColumn']:pointer(row[k],True)
 decimal(row['offset']);integer(row['direction'],0,3)
 cols=row['columns'];require(type(cols)is list and 0<len(cols)<=64,'complete actual scrolling columns')
 seen_cols=set();seen_data=set();seen_targets=set();selected=[];total=0
 for col in cols:
  fields(col,'column width rows');pointer(col['column'],True)
  require(col['column']not in seen_cols,'unique scrolling column');seen_cols.add(col['column'])
  require(decimal(col['width'])>0,'positive column width')
  require(type(col['rows'])is list and 0<len(col['rows'])<=256,'actual column rows')
  for member in col['rows']:
   total+=1;require(total<=256,'complete bounded row inventory')
   fields(member,'data target owner size layoutBox');pointer(member['data'],True);pointer(member['target'],True);identity(member['owner'])
   require(member['data']not in seen_data and member['target']not in seen_targets,'unique actual row/target')
   seen_data.add(member['data']);seen_targets.add(member['target']);require(decimal(member['size'])>0,'positive row size');box(member['layoutBox'])
   if member['data']==row['selectedData']:selected.append((col['column'],member['target']))
 require(len(selected)==1 and selected[0]==(row['selectedColumn'],target),'selected row in exact current column/owning target')

def transfer(row):
 if row is None:return
 fields(row,'operation generation accepted actualModesKnown beforeInternal beforeClient actualInternal actualClient target space workspace output reason')
 unsigned(row['operation'],True);unsigned(row['generation'],True);boolean(row['accepted']);boolean(row['actualModesKnown'])
 for k in ['beforeInternal','beforeClient','actualInternal','actualClient']:integer(row[k],0,3)
 for k in ['target','space','workspace','output']:pointer(row[k],row['actualModesKnown'])
 require(type(row['reason'])is str and 0<len(row['reason'].encode())<=4096,'bounded actual outcome reason')
 require(not row['accepted']or row['actualModesKnown'],'no accepted unknown native modes')
 # A refused/unknown outcome is retained, never translated to success.

def decode(raw,root,captured,mask=None,ignore=False):
 require(type(raw)is bytes and 0<len(raw)<=131072,'bounded complete native observation bytes')
 if mask is not None:integer(mask,0,4)
 boolean(ignore);require(mask is not None or ignore is False,'metadata cannot ignore a selected owner')
 row=json.loads(raw.decode('utf-8'),object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('non-JSON scalar')))
 fields(row,'schema queryKind queryProperties ignoreOwner hitOwner corePolicyBuild compositorPid compositorPgid compositorStart session sequence observedNs ok error body postBody')
 integer(row['schema'],1,1);boolean(row['ok']);require(type(row['queryKind'])is str and row['queryKind']==('metadata'if mask is None else 'windowAtStimulus'),'explicit observation/stimulus kind');require(type(row['corePolicyBuild'])is str and row['corePolicyBuild']==POLICY,'exact reviewed source policy')
 integer(row['compositorPid'],1,2**31-1);integer(row['compositorPgid'],1,2**31-1);unsigned(row['observedNs'],True)
 if not row['ok']:
  require(type(row['error'])is str and row['error'],'raw explicit native read refusal')
  raise ValueError('Native observation refused: '+row['error'])
 require(row['error']is None,'no partial successful native read')
 unsigned(row['compositorStart'],True);unsigned(row['sequence'],True)
 require(type(row['session'])is str and re.fullmatch(r'[A-Za-z0-9_]+',row['session'])is not None,'actual instance token')
 for key in ['compositorPid','compositorPgid','compositorStart','session']:require(exact(row[key],root[key]),'same selected actual root '+key)
 b=row['body'];fields(b,'owner mapped hidden acceptsInput noFocus priorityFocus pinned floating internalMode clientMode fullscreenHandler target space workspace output logicalBox visualBox restoreValid restoreGeneration restoreLogicalBox restoreVisualBox restoreFloating restoreLayoutHandled restoreTarget restoreLayoutTarget restoreSpace restoreOrigin restoreManaged ownedUnpinReady group groupMembers cursor coreFocus scroll transfer')
 identity(b['owner']);require(exact(b['owner'],{k:captured[k]for k in ['address','stableId','pid']}),'exact selected public lifetime')
 for k in ['mapped','hidden','acceptsInput','noFocus','priorityFocus','pinned','floating','restoreValid','restoreFloating','restoreLayoutHandled','restoreOrigin','restoreManaged','ownedUnpinReady']:boolean(b[k])
 require(b['mapped'],'actual mapped selected owner')
 for k in ['internalMode','clientMode']:integer(b[k],0,3)
 for k in ['fullscreenHandler','target','space','workspace','output']:pointer(b[k],True)
 pointer(b['group']);unsigned(b['restoreGeneration'],b['restoreValid'])
 for k in ['restoreTarget','restoreLayoutTarget','restoreSpace']:pointer(b[k],b['restoreValid'])
 if b['restoreValid']:require(b['restoreLayoutTarget']==b['target']and b['restoreSpace']==b['space'],'valid projection current owning scope')
 for k in ['logicalBox','visualBox','restoreLogicalBox','restoreVisualBox']:box(b[k])
 require(type(b['groupMembers'])is list and len(b['groupMembers'])<=64,'bounded actual group')
 for member in b['groupMembers']:identity(member)
 require(len({(v['address'],v['stableId'],v['pid'])for v in b['groupMembers']})==len(b['groupMembers']),'unique group lifetimes')
 require((b['group']=='0x0')==(not b['groupMembers']),'actual group presence')
 require(type(b['cursor'])is list and len(b['cursor'])==2,'actual native cursor')
 for v in b['cursor']:decimal(v)
 require(exact(row['body'],row['postBody']),'complete raw owning before/post equality')
 identity(b['coreFocus'],True)
 identity(row['ignoreOwner'],True);identity(row['hitOwner'],True)
 if mask is None:
  require(row['queryProperties']is None and row['ignoreOwner']is None and row['hitOwner']is None,'pure metadata contains no native hit stimulus')
 else:
  integer(row['queryProperties'],0,511);require(row['queryProperties']==MASKS[mask],'fixed native query mask')
  require(exact(row['ignoreOwner'],b['owner']if ignore else None),'exact native ignore lifetime')
 scroll(b['scroll'],b['target']);transfer(b['transfer'])
 return row

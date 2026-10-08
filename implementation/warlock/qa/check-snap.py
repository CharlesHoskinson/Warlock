"""Focused real snap wire/custody validators; no native acceptance claim."""
import copy,json,pathlib,shlex,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapter'))
import geometry_placement,recovery_journal,admission_ledger
from geometry_endpoint import GeometryEndpoint as Endpoint
from endpoint import Refused
bound={'lifetime':'1','session':'1','frontend':'1'}
placement={'region':'left-half','geometry':[-80,30,400.5,601],'monitor':'0','outputOwnershipGeneration':'2','workAreaRevision':'3','workspaceGeneration':'4'}
intent={'request':'1','generation':'1','incarnation':'1','operation':'snap','context':{'lifetime':'1','epoch':'1','output':'1','revision':'1'},'placement':placement}
record={'schema':2,'effectProtocol':2,'binding':bound,'intent':intent,'status':'Pending'}
checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
def reject(fn):
 try:fn()
 except Refused:return True
 return False
check('Actual journal accepts complete snap custody',recovery_journal.validate(copy.deepcopy(record))==record)
check('Unknown journal retains exact placement',recovery_journal.validate(dict(copy.deepcopy(record),status='Unknown'))['intent']==intent)
for name,mutate in [
 ('unsupported region',lambda p:p.update(region='fullscreen')),
 ('zero output generation',lambda p:p.update(outputOwnershipGeneration='0')),
 ('boolean width',lambda p:p['geometry'].__setitem__(2,True)),
 ('zero height',lambda p:p['geometry'].__setitem__(3,0)),
 ('extra placement field',lambda p:p.update(command='anything')),
 ('noncanonical monitor',lambda p:p.update(monitor='00')),
 ('invalid rectangle shape',lambda p:p.update(geometry=[0,0,1]))]:
 candidate=copy.deepcopy(record);mutate(candidate['intent']['placement']);check('Journal rejects '+name,reject(lambda:recovery_journal.validate(candidate)))
legacy=copy.deepcopy(record);legacy['effectProtocol']=1
check('Legacy protocol cannot carry snap',reject(lambda:recovery_journal.validate(legacy)))
client=object.__new__(Endpoint);client.bound=bound;client.geometry_binding=bound;client.geometry_capabilities={'effects':True,'operations':['maximize','restore-geometry','snap']};calls=[]
def request(frame):
 calls.append(frame)
 return {'protocolVersion':3,'kind':'effect-outcome','effectProtocol':2,'binding':bound,'intent':frame['intent'],'status':'Refused','reason':'dependency-mismatch','revision':'2','outputGeneration':'2'}
client.request=request
outcome=client.geometry_effect(copy.deepcopy(intent))
check('Real endpoint preserves typed placement in protocol 2',len(calls)==1 and calls[0]['intent']==intent and calls[0]['effectProtocol']==2 and outcome['status']=='Refused')
client.geometry_capabilities['operations']=['maximize','restore-geometry']
check('Unnegotiated snap never reaches transport',reject(lambda:client.geometry_effect(copy.deepcopy(intent))) and len(calls)==1)
# Compile the exact production codec functions, without storage/process globals.
# The source is extracted verbatim and includes the real surface validator.
source=(ROOT/'native/host-journal.h').read_text();start=source.index('static gboolean admission_positive(');end=source.index('static JsonNode *admission_normalize(',start)
main=r'''
int main(int argc,char **argv){
 if(argc!=2)return 2;
 JsonParser *parser=json_parser_new();if(!json_parser_load_from_data(parser,argv[1],-1,NULL))return 3;
 JsonNode *record=admission_record(json_parser_get_root(parser));
 if(!record){puts("REJECT");g_object_unref(parser);return 0;}
 char *key=admission_key(record);puts(key);g_free(key);json_node_free(record);g_object_unref(parser);return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='warlock-snap-codec-') as tmp:
 p=pathlib.Path(tmp);unit=p/'snap-codec.c';unit.write_text('#include <math.h>\n#include <glib.h>\n#include <json-glib/json-glib.h>\n#include <stdio.h>\n#include "surface.h"\n'+source[start:end]+main)
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0'],text=True))
 subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-I'+str(ROOT/'native'),str(unit),'-o',str(p/'codec'),*flags],check=True)
 def codec(value):return subprocess.check_output([str(p/'codec'),json.dumps(value,separators=(',',':'))],text=True).strip()
 frame={'protocolVersion':3,'kind':'window-effect','effectProtocol':2,'binding':bound,'intent':intent};key=codec(frame)
 check('Real host admits complete snap payload',key!='REJECT')
 check('Real host and broker custody keys agree',key==admission_ledger.storage_key(record))
 altered=copy.deepcopy(frame);altered['intent']['placement']['geometry'][0]+=1
 check('Host custody identity includes rectangle',codec(altered)!=key and codec(altered)!='REJECT')
 reordered=copy.deepcopy(frame);reordered['intent']['placement']=dict(reversed(list(reordered['intent']['placement'].items())))
 check('Host custody identity ignores field order',codec(reordered)==key)
 missing=copy.deepcopy(frame);del missing['intent']['placement'];check('Host rejects missing placement',codec(missing)=='REJECT')
 extra=copy.deepcopy(frame);extra['intent']['placement']['unexpected']=1;check('Host rejects extra placement fields',codec(extra)=='REJECT')
 bool_rect=copy.deepcopy(frame);bool_rect['intent']['placement']['geometry'][2]=True;check('Host rejects boolean rectangle',codec(bool_rect)=='REJECT')
 bad_protocol=copy.deepcopy(frame);bad_protocol['effectProtocol']=1;check('Host rejects snap under legacy protocol',codec(bad_protocol)=='REJECT')
print(json.dumps({'passed':True,'checks':checks,'nativeAcceptance':False}))

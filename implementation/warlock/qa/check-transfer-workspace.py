"""Actual C/Python admission correlation and durable no-replay behavior."""
import copy,json,pathlib,shlex,subprocess,sys,tempfile,os
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapter'))
from geometry_endpoint import GeometryEndpoint,validate_transfer
from recovery_journal import validate
from admission_ledger import storage_key
from durable_ledger import Ledger
from endpoint import Refused
bound={'lifetime':'1','session':'2','frontend':'3'}
intent={'request':'1','generation':'1','incarnation':'7','operation':'transfer-workspace','context':{'lifetime':'1','epoch':'3','output':'1','revision':'1'},'transfer':{'source':'1','sourceGeneration':'4','destination':'2'}}
record={'schema':2,'effectProtocol':2,'binding':bound,'intent':intent,'status':'Pending'}
checks=[]
with tempfile.TemporaryDirectory(prefix='transfer-custody-') as temporary:
 os.chmod(temporary,0o700);binary=pathlib.Path(temporary)/'host-journal'
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0'],text=True))
 subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function',str(ROOT/'native/host-journal-test.c'),'-o',str(binary),*flags],check=True,capture_output=True,text=True)
 def native(row):
  request={'protocolVersion':3,'kind':'window-effect','effectProtocol':2,'binding':bound,'intent':row['intent']}
  return subprocess.run([str(binary),json.dumps(request)],capture_output=True,text=True)
 validate(record);validate_transfer(intent['transfer']);actual=native(record);assert actual.returncode==0 and actual.stdout.strip()==storage_key(record);checks.append('CAndPythonAdmissionKeysAgree')
 for destination in ['3','10','9223372036854775807']:
  changed=copy.deepcopy(record);changed['intent']['transfer']['destination']=destination
  assert storage_key(changed)!=storage_key(record) and native(changed).stdout.strip()==storage_key(changed);checks.append('DestinationIdentity'+destination)
 for patch in [{'destination':'-99'},{'destination':'0'},{'destination':'02'},{'destination':'1'},{'destination':'9223372036854775808'},{'sourceGeneration':'0'},{'extra':'value'}]:
  changed=copy.deepcopy(record);changed['intent']['transfer'].update(patch)
  for validator in [lambda:validate(changed),lambda:validate_transfer(changed['intent']['transfer'])]:
   try:validator();raise AssertionError(patch)
   except Refused:pass
  assert native(changed).returncode==1;checks.append('InvalidPayload'+str(patch))
 ledger=Ledger(temporary,'owned_transfer','1')
 try:
  assert ledger.begin(bound,intent,2) and not ledger.begin(bound,intent,2);checks.append('DuplicateAdmissionCannotResubmit')
  outcome={'protocolVersion':3,'kind':'effect-outcome','effectProtocol':2,'binding':bound,'intent':intent,'status':'Unknown','reason':'effect-unproven','revision':'2','outputGeneration':'1'}
  ledger.settle(outcome);recovered=ledger.recover(bound)
  assert recovered['entries'][0]['intent']==intent and recovered['entries'][0]['status']=='Unknown' and 'commands' not in recovered;checks.append('UnknownRecoveryIsObservationOnly')
  wrong=copy.deepcopy(outcome);wrong['intent']['transfer']['destination']='3';wrong['status']='Committed'
  try:ledger.settle(wrong);raise AssertionError('foreign destination settled')
  except Refused:checks.append('WrongDestinationCannotSettleCustody')
  assert ledger.blocked('1','7');retry=copy.deepcopy(intent);retry.update(request='2',generation='2')
  try:ledger.begin(bound,retry,2);raise AssertionError('unknown replay')
  except Refused:checks.append('UnknownTargetCannotReplay')
  ledger.settle({**outcome,'status':'Committed'});assert not ledger.blocked('1','7');checks.append('ExactCommittedReceiptSettlesCustody')
 finally:ledger.close()
print(json.dumps({'passed':True,'checks':checks,'nativeAcceptance':False}))

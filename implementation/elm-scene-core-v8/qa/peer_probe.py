"""Actual second-process credentials: borrowed frontend binding must be refused."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'adapter'))
from endpoint import Endpoint,Refused
config=json.loads(Path(sys.argv[1]).read_text());borrowed=config.pop('borrowed')
client=Endpoint(**config);client.bound=borrowed
try:client.snapshot('1')
except Refused as error:
 assert str(error)=='binding-mismatch',error
else:raise RuntimeError('Borrowed PID binding admitted')
hello=client.hello();snapshot=client.snapshot('1')
assert hello['binding']['session']!=borrowed['session']
print(json.dumps({'borrowedBindingRefused':True,'ownBindingAccepted':True,'binding':hello['binding'],'windowCount':len(snapshot['windows'])}))

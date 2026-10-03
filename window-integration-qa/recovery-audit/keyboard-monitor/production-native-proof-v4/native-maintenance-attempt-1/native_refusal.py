"""Owned Lua observes a genuine native refusal; product transport stays exact."""
import json,re
MISMATCH='maintenance target/incarnation mismatch'

def observation_lua(identity):
    tokens=[identity[key] for key in ('instance','packageID','incarnation')]
    if any(not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,256}',token) for token in tokens):
        raise ValueError('Exact native identity tokens required')
    invocation='hl.plugin.omarchy_a11y.prepare_unload('+','.join(json.dumps(token) for token in tokens)+')'
    return ('local ok,value=pcall(function() return '+invocation+' end); '
        'local message=tostring(value); if #message>4096 then return \'{"ok":\'..tostring(ok)..\',"errorTooLong":true}\' end; '
        'local bytes={}; for i=1,#message do bytes[i]=tostring(string.byte(message,i)) end; '
        'return \'{"ok":\'..tostring(ok)..\',"errorBytes":[\'..table.concat(bytes,",")..\']}\'')

def decode_refusal(raw):
    if not isinstance(raw,str) or len(raw.encode('utf8'))>65536:raise ValueError('Bounded actual native refusal JSON required')
    value=json.loads(raw)
    if not isinstance(value,dict) or set(value)!=set(('ok','errorBytes')) or value['ok'] is not False:
        raise ValueError('Actual native pcall must return false with exact error bytes')
    numbers=value['errorBytes']
    if not isinstance(numbers,list) or not 1<=len(numbers)<=4096 or any(type(n) is not int or not 0<=n<=255 for n in numbers):
        raise ValueError('Invalid bounded native error bytes')
    message=bytes(numbers).decode('utf8')
    if MISMATCH not in message:raise ValueError('Specific native target/incarnation mismatch absent')
    return dict(ok=False,error=message,errorBytes=numbers,actualReply=raw,
                genuinePrepareDelegatedOnce=True,exceptionFallback=False)

def observe_native_refusal(control,identity):
    # Transport exceptions propagate. They can never become a native refusal.
    return decode_refusal(control.ipc('repl',observation_lua(identity)))

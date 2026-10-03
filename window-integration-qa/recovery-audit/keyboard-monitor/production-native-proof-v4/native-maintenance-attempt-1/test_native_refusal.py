"""Actual Lua pcall/byte encoding and strict Python decode, without a compositor."""
import json,subprocess,types,unittest
import native_refusal as n
IDENTITY=dict(instance='a'*40+'_1_2',packageID='omarchy-a11y-prod-v2',incarnation='b'*64)

class NativeRefusalTests(unittest.TestCase):
    def lua_reply(self,message,success=False):
        arguments=','.join(json.dumps(IDENTITY[k]) for k in ('instance','packageID','incarnation'))
        compare='local expected={'+arguments+'}; assert(a==expected[1] and b==expected[2] and c==expected[3]); '
        behavior='return {ready=true}' if success else 'local values={'+','.join(str(i) for i in message.encode('utf8'))+'}; local chars={}; for _,byte in ipairs(values) do chars[#chars+1]=string.char(byte) end; error(table.concat(chars),0)'
        source='local calls=0; hl={plugin={omarchy_a11y={prepare_unload=function(a,b,c) calls=calls+1; '+compare+behavior+' end}}}; '
        source+='local raw=(function() '+n.observation_lua(IDENTITY)+' end)(); assert(calls==1); io.write(raw)'
        result=subprocess.run(['/usr/bin/lua','-'],input=source,capture_output=True,text=True,timeout=3,check=True)
        self.assertEqual(result.stderr,'');return result.stdout

    def test_actual_lua_false_pcall_exact_error_utf8_quotes_newlines_and_delegate_once(self):
        message='native "quoted"\nλ: '+n.MISMATCH
        raw=self.lua_reply(message);row=n.decode_refusal(raw)
        self.assertEqual(row['error'],message);self.assertEqual(row['errorBytes'],list(message.encode('utf8')));self.assertFalse(row['exceptionFallback']);self.assertTrue(row['genuinePrepareDelegatedOnce'])

    def test_actual_lua_success_arbitrary_error_empty_or_too_long_never_pass(self):
        for raw in [self.lua_reply(n.MISMATCH,success=True),self.lua_reply('unexpected native failure'),self.lua_reply(''),self.lua_reply('x'*4097)]:
            with self.assertRaises(ValueError):n.decode_refusal(raw)

    def test_malformed_wire_boolean_byte_types_ranges_and_bounds_refuse(self):
        valid=list(n.MISMATCH.encode())
        invalid=['IPC failed: ','{}','null','[]',json.dumps(dict(ok=True,errorBytes=valid)),json.dumps(dict(ok=0,errorBytes=valid)),json.dumps(dict(ok=False,errorBytes=valid,extra='wrong'))]
        for numbers in [[],[256],[-1],[True],[1.5],['1'],[255],valid+[0]*4097]:invalid.append(json.dumps(dict(ok=False,errorBytes=numbers)))
        invalid.append('x'*65537)
        for raw in invalid:
            with self.assertRaises((ValueError,UnicodeError),msg=raw[:80]):n.decode_refusal(raw)

    def test_observe_uses_actual_repl_once_with_exact_tokens_and_archives_raw(self):
        raw=self.lua_reply(n.MISMATCH);calls=[]
        class Control:
            def ipc(self,*args):calls.append(args);return raw
        row=n.observe_native_refusal(Control(),IDENTITY)
        self.assertEqual(calls,[('repl',n.observation_lua(IDENTITY))]);self.assertEqual(row['actualReply'],raw)

    def test_real_transport_exception_cannot_count_as_native_refusal(self):
        class Control:
            def ipc(self,*args):raise RuntimeError('IPC failed: ')
        with self.assertRaisesRegex(RuntimeError,'IPC failed'):n.observe_native_refusal(Control(),IDENTITY)

    def test_identity_token_injection_refuses_before_transport(self):
        calls=[]
        control=types.SimpleNamespace(ipc=lambda *args:calls.append(args))
        for token in ['bad"token','bad\ntoken','λ','',1,'x'*257]:
            with self.assertRaises(ValueError):n.observe_native_refusal(control,{**IDENTITY,'incarnation':token})
        self.assertEqual(calls,[])

if __name__=='__main__':unittest.main()

import json,os,threading,unittest
from cdp_readonly import ReadOnlyPipe,DOM_QUERY
from network_guard import routes
class Protocol(unittest.TestCase):
 def setUp(self):
  self.to_read,self.to_write=os.pipe();self.from_read,self.from_write=os.pipe();self.client=ReadOnlyPipe(self.to_write,self.from_read)
 def tearDown(self):
  for fd in (self.to_read,self.to_write,self.from_read,self.from_write):
   try:os.close(fd)
   except OSError:pass
 def server(self,reply):
  def run():
   payload=b''
   while b'\0' not in payload:payload+=os.read(self.to_read,64)
   row=json.loads(payload.split(b'\0')[0]);data=reply(row)
   for part in [data[:7],data[7:]]:os.write(self.from_write,part)
  worker=threading.Thread(target=run);worker.start();return worker
 def test_fragmented_actual_reply(self):
  worker=self.server(lambda r:json.dumps({'id':r['id'],'result':{'product':'fake protocol transport only'}}).encode()+b'\0')
  self.assertEqual(self.client.request('Browser.getVersion')['product'],'fake protocol transport only');worker.join()
 def test_event_before_reply(self):
  worker=self.server(lambda r:b'{"method":"Target.created","params":{}}\0'+json.dumps({'id':r['id'],'result':{}}).encode()+b'\0')
  self.client.request('Browser.getVersion');worker.join();self.assertEqual(len(self.client.events),1)
 def test_mutation_refused_before_any_write(self):
  for name,params in [('Input.dispatchKeyEvent',{}),('Runtime.evaluate',{'expression':"document.getElementById('draft').value='fake'",'returnByValue':True}),('Target.createTarget',{'url':'https://example.com'})]:
   with self.assertRaises(RuntimeError):self.client.request(name,params,'session')
  import select
  self.assertEqual(select.select([self.to_read],[],[],0)[0],[])
 def test_dom_needs_exact_session(self):
  with self.assertRaises(RuntimeError):self.client.request('Runtime.evaluate',{'expression':DOM_QUERY,'returnByValue':True})
 def test_wrong_session_refused(self):
  worker=self.server(lambda r:json.dumps({'id':r['id'],'sessionId':'other','result':{}}).encode()+b'\0')
  with self.assertRaises(RuntimeError):self.client.request('Runtime.evaluate',{'expression':DOM_QUERY,'returnByValue':True},'actual')
  worker.join()
 def test_wrong_command_reply_refused(self):
  worker=self.server(lambda r:json.dumps({'id':r['id']+1,'result':{}}).encode()+b'\0')
  with self.assertRaises(RuntimeError):self.client.request('Browser.getVersion')
  worker.join()
 def test_public_query_result_not_ack(self):
  value={'value':'actual\nbytes','selection':[4,4],'active':'draft'}
  worker=self.server(lambda r:json.dumps({'id':r['id'],'sessionId':'actual','result':{'result':{'value':json.dumps(value)}}}).encode()+b'\0')
  self.assertEqual(self.client.dom('actual'),value);worker.join()
 def test_no_external_route(self):self.assertEqual(routes('Iface Destination\n','0000 lo\n')['ipv6'],'0000 lo\n')
 def test_external_ipv4_refused(self):
  with self.assertRaises(RuntimeError):routes('Iface Destination\neth0 00000000\n','')
 def test_external_ipv6_refused(self):
  with self.assertRaises(RuntimeError):routes('Iface Destination\n','0000 eth0\n')
if __name__=='__main__':unittest.main(verbosity=2)

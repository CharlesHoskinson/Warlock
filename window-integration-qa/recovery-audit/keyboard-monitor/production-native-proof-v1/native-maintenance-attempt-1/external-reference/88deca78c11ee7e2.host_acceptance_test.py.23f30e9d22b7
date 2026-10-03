import copy,json,os,unittest
from pathlib import Path
import host_acceptance as h
class Acceptance(unittest.TestCase):
 def evidence(self):return json.loads((Path(__file__).parent/'host-bootstrap-evidence.json').read_text())['evidence']
 def test_actual_retained_native_complete_reply(self):self.assertTrue(h.ipc_complete(self.evidence()))
 def test_wrong_or_missing_child_peer_refused(self):
  for field,value in [('pid',-1),('uid',os.getuid()+1)]:
   row=self.evidence();row['ipcReadiness'][0]['peer'][field]=value;self.assertFalse(h.ipc_complete(row))
 def test_complete_reply_not_inferred_from_connection(self):
  for field,value in [('completeServerEOF',False),('replyBytes',0),('replyBytes',65537),('replySHA256','not-a-hash'),('request','version')]:
   row=self.evidence();row['ipcReadiness'][0][field]=value;self.assertFalse(h.ipc_complete(row))
 def test_replaced_socket_and_commit_refused(self):
  row=self.evidence();row['ipcReadiness'][0]['socket']['inode']+=1;self.assertFalse(h.ipc_complete(row))
  row=self.evidence();row['ipcReadiness'][0]['version']['commit']='other-core';self.assertFalse(h.ipc_complete(row))
 def test_one_exact_owned_reply(self):
  row=self.evidence();row['ipcReadiness']*=2;self.assertFalse(h.ipc_complete(row))
  row=self.evidence();row['ipcReadiness'][0]['path']='/run/user/1000/main';self.assertFalse(h.ipc_complete(row))
 def test_transport_requires_marker_and_configure(self):
  good=[h.MARKER,'Output WAYLAND-1: configure surface with 1']
  self.assertTrue(h.transport(good)['pass_']);self.assertFalse(h.transport(good[:1])['pass_']);self.assertFalse(h.transport(good[1:])['pass_'])
 def test_forbidden_transport_errors_never_waived(self):
  good=[h.MARKER,'Output WAYLAND-1: configure surface with 3']
  for bad in ('[libseat]','DRM Backend failed','Starting the DRM backend','enabling fallbacks','error 3:','Broken pipe','parent transport failed','xdg_surface never configured'):
   self.assertFalse(h.transport(good+[bad])['pass_'],bad)
if __name__=='__main__':unittest.main()

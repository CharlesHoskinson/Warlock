import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import capture_evidence
from service_observer import ObservedFactory
from snapshot_cache import SnapshotCache

class CaptureEvidenceTests(unittest.TestCase):
 def fixture(self,root):
  root=Path(root);members=[];rows=[];pairs=[];sources=[];events=[]
  for index in range(3):
   member=dict(address=hex(index+1),stableId=format(index+1,'x'),pid=42+index);members.append(member)
   files=[]
   for suffix in ('.json','.png'):
    path=root/(str(index)+suffix);data=(str(index)+suffix).encode();path.write_bytes(data);path.chmod(0o600)
    files.append(dict(source=str(path),retainedPath=str(path),sha256=hashlib.sha256(data).hexdigest()))
   source=dict(stableId=member['stableId'],pid=member['pid'],digest=files[1]['sha256'],pixels=[1,1],sceneToken='scene')
   sources.append(source);rows.append(dict(source=source,retainedPath=files[1]['source'],sha256=source['digest'],captureCallbackDelegatedOnce=True,sourceResultUnchanged=True))
   pairs.append(dict(identity=[member['address'],member['stableId'],member['pid']],files=files))
   events.append(dict(event='uploaded',digest=source['digest'],pixels=source['pixels']))
  events.append(dict(event='seeded',token='scene',sourceDigests=[{k:s[k] for k in ('stableId','pid','digest')} for s in sources]))
  packet=dict(retirement=dict(actor=1),retainedEpochSources=rows,cachePairsAtCapture=pairs,history=[dict(operation='minimize',sources=sources,token='scene')],rendererEvents=events)
  return members,packet
 def test_capture_seed_and_exact_pairs_then_restore_reuse(self):
  with tempfile.TemporaryDirectory() as root:
   members,packet=self.fixture(root);self.assertEqual(capture_evidence.captured_and_seeded(packet,'minimize',members)['actor'],1)
   pairs=capture_evidence.unchanged_pairs(packet,members);self.assertEqual(capture_evidence.unchanged_pairs(packet,members,pairs),pairs)
 def test_native_fallback_no_sources_or_seed_cannot_satisfy(self):
  with tempfile.TemporaryDirectory() as root:
   members,packet=self.fixture(root)
   for mutate in (lambda p:p.update(retainedEpochSources=[]),lambda p:p.update(rendererEvents=[dict(event='gpu')]),lambda p:p['rendererEvents'][-1].update(token='foreign'),lambda p:p['rendererEvents'][-1].update(sourceDigests=[])):
    changed=copy.deepcopy(packet);mutate(changed)
    with self.assertRaises(ValueError):capture_evidence.captured_and_seeded(changed,'minimize',members)
 def test_cache_missing_changed_symlink_and_restore_difference_refuse(self):
  with tempfile.TemporaryDirectory() as root:
   members,packet=self.fixture(root);prior=capture_evidence.unchanged_pairs(packet,members)
   with self.assertRaisesRegex(ValueError,'reuse'):capture_evidence.unchanged_pairs(packet,members,{})
   changed=copy.deepcopy(packet);changed['cachePairsAtCapture'].pop()
   with self.assertRaisesRegex(ValueError,'Three'):capture_evidence.unchanged_pairs(changed,members)
   path=Path(packet['cachePairsAtCapture'][0]['files'][0]['source']);path.write_bytes(b'mutated')
   with self.assertRaisesRegex(ValueError,'changed'):capture_evidence.unchanged_pairs(packet,members,prior)
   path.unlink();path.symlink_to(Path(root)/'1.json')
   with self.assertRaises(OSError):capture_evidence.unchanged_pairs(packet,members)
 def test_actual_product_cache_read_minimize_and_composed_restore(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);evidence=root/'evidence';evidence.mkdir(mode=0o700)
   window=dict(address='0x1',stableId='1',pid=42,at=[0,0],size=[1,1],workspace=dict(name='1'))
   pixels=b'\x89PNG\r\n\x1a\n'+b'\x00\x00\x00\rIHDR'+struct.pack('!II',1,1)+bytes([8,6])+b'\x00'*7
   cache=SnapshotCache(root/'cache',lambda *_:None);metadata=dict(identity=['0x1','1',42],clientSize=[1,1],whole=True,canonical=True,pixels=[1,1]);cache.publish(window,metadata,pixels)
   source=dict(digest=hashlib.sha256(pixels).hexdigest(),captureEpoch='epoch',sceneToken='token')
   factory=object.__new__(ObservedFactory);factory.evidence_root=evidence;factory.source_lock=threading.Lock();desktop=SimpleNamespace(shared_cache=cache)
   before={p.name:p.read_bytes() for p in cache.root.iterdir()};factory.retain_cache_pair(1,desktop,window,source)
   restored=copy.deepcopy(window);restored['workspace']['name']='special:win-minimized';fresh=dict(source,digest='a'*64)
   factory.retain_cache_pair(2,desktop,restored,fresh)
   self.assertEqual(before,{p.name:p.read_bytes() for p in cache.root.iterdir()})
   self.assertEqual(factory.observed_cache_pairs[0]['cacheDigest'],factory.observed_cache_pairs[1]['cacheDigest'])
   self.assertNotEqual(factory.observed_cache_pairs[1]['cacheDigest'],factory.observed_cache_pairs[1]['returnedSourceDigest'])
   for pair in factory.observed_cache_pairs:
    for row in pair['files']:self.assertEqual(capture_evidence.digest(row['retainedPath']),row['sha256'])
 def test_retirement_retains_drained_real_seed_events_after_delegate(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);members,packet=self.fixture(root)
   factory=object.__new__(ObservedFactory);factory.evidence_root=root;factory.source_lock=threading.Lock();factory.observed_sources=[dict(r,actor=1) for r in packet['retainedEpochSources']];factory.observed_cache_pairs=[dict(p,actor=1) for p in packet['cachePairsAtCapture']];factory.observed_retirements=[]
   transport=SimpleNamespace(lock=threading.Lock(),events=packet['rendererEvents'],closed=True,process=SimpleNamespace(poll=lambda:0))
   factory.observed_controllers=[(1,SimpleNamespace(transport=transport,history=[]))];desktop=SimpleNamespace(root=root/'gone');factory.desktops=[desktop];calls=[]
   def retire(number,value):calls.append(number);factory.desktops.remove(value);return 'same-result'
   with patch('service_observer.native_runtime.NativeFactory.retired',side_effect=retire):self.assertEqual(factory.retired(1,desktop),'same-result')
   retained=json.loads((root/'service-retirement-1.json').read_text());self.assertEqual(calls,[1]);self.assertEqual(retained['rendererEvents'],packet['rendererEvents']);self.assertEqual(len(retained['retainedEpochSources']),3);self.assertEqual(len(retained['cachePairsAtCapture']),3)

if __name__=='__main__':unittest.main()

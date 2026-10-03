import copy
import threading
import time
import unittest
from scene_controller import SceneController, Scene, ids, key, rectangle
import production_motion_6d9 as core

class Transport:
    def __init__(self):self.sent=[];self.callback=None
    def set_callback(self,callback):self.callback=callback
    def send(self,message):self.sent.append(copy.deepcopy(message))
    def outputs(self):return [{'name':'left','generation':1},{'name':'right','generation':2}]

class Desktop:
    def __init__(self):
        self.windows=[{'address':'0x'+sid,'stableId':sid,'pid':pid,'at':[i*50+100,i*50+100],'size':[300-i*50,200-i*40], 'mapped':True,'pinned':i==0,'workspace':{'name':'1'}} for i,(sid,pid) in enumerate([('aa01',41),('bb02',42),('cc03',43)])]
        self.native=[dict(w,parent='' if i==0 else self.windows[i-1]['address'],parentStableId='' if i==0 else self.windows[i-1]['stableId'],modal=i>0) for i,w in enumerate(self.windows)]
        self.commits=[];self.block=None;self.started=threading.Event();self.reduced_flag=False;self.captures=0;self.destinations=[];self.released=[];self.commit_block=None
    def clients(self):return copy.deepcopy(self.windows)
    def family(self,w,windows,single=False):
        if self.block:
            self.started.set();self.block.wait(3)
        if single:return [w],w
        return core.native_family_plan(w,self.clients(),copy.deepcopy(self.native))
    def active(self):return self.windows[0]['address']
    def reduced(self):return self.reduced_flag
    def select_destination(self,w):self.destinations.append(key(w))
    def capture_source(self,w,token,index):
        self.captures+=1
        return dict(stableId=w['stableId'],pid=w['pid'],nativeRect=rectangle(w),atlasRect=rectangle(w),iconRect={'x':10,'y':700,'width':28,'height':28},digest=str(index)*64,path='/unused/'+token+'.png',insets={'left':0,'top':0,'right':0,'bottom':0},pixels=w['size'],captureScale=1)
    def release_sources(self,sources):self.released.append(copy.deepcopy(sources))
    def commit(self,op,w,preview=True):
        if self.commit_block:self.started.set();self.commit_block.wait(3)
        current=next((m for m in self.windows if key(m)==key(w)),None)
        if current is None:raise ValueError('stale core identity')
        self.commits.append((op,key(w),current['pinned']))
        current['workspace']['name']='special:win-minimized' if op=='minimize' else '1'

class SceneTests(unittest.TestCase):
    def setUp(self):self.d=Desktop();self.t=Transport();self.c=SceneController(self.d,self.t)
    def tearDown(self):
        if self.d.block:self.d.block.set()
        if self.d.commit_block:self.d.commit_block.set()
        self.c.workers.shutdown(wait=True,cancel_futures=True)
    def wait(self,predicate):
        end=time.monotonic()+3
        while time.monotonic()<end:
            if predicate():return
            time.sleep(.002)
        self.fail('worker did not reach expected boundary')
    def request(self,op='minimize',context=1):
        w=self.d.windows[0];return self.c.request(op,w['address'],w['stableId'],w['pid'],context=context)
    def seed(self):
        result=self.request();self.wait(lambda:any(m['command']=='validate' and m['token']==result['token'] for m in self.t.sent));return self.c.current
    def event(self,record,kind):return self.c.event({'event':kind,'token':record.token,'identities':ids(record.members),'servicePromoted':True,'sourceDigests':[{k:s[k] for k in ('stableId','pid','digest')} for s in record.sources]})
    def test_seed_complete_family_ready_and_endpoint(self):
        r=self.seed();self.assertEqual(len(r.members),3);self.assertEqual(len(self.t.sent[0]['members']),3);self.assertEqual(self.d.captures,3)
        self.assertTrue(self.event(r,'ready'));self.assertEqual([op for op,*_ in self.d.commits],['minimize']*3)
        self.assertEqual([p for *_,p in self.d.commits],[True,False,False]);self.assertTrue(self.event(r,'endpoint'))
        self.assertIs(self.c.current,r);self.assertTrue(self.event(r,'cancelled'));self.assertIsNone(self.c.current)
        self.assertEqual(len(self.d.commits),3)
    def test_third_intent_retargets_before_blocked_metadata_and_reuses_all_pixels(self):
        old=self.seed();self.event(old,'ready');self.d.block=threading.Event();self.d.started.clear()
        second=self.request('restore');self.assertEqual(self.t.sent[-1]['command'],'retarget');self.assertTrue(self.d.started.wait(1))
        third=self.request('minimize');current=self.c.current
        self.assertEqual(self.t.sent[-1]['token'],third['token']);self.assertEqual(current.sources,old.sources);self.assertFalse(current.validated);self.assertEqual(self.d.captures,3)
        self.assertFalse(self.event(old,'endpoint'));self.assertFalse(self.c.event({'event':'ready','token':second['token'],'identities':ids(old.members),'servicePromoted':True}))
        self.assertFalse(self.event(current,'endpoint'));self.assertEqual(len(self.d.commits),3)
        self.d.block.set();self.wait(lambda:current.validated)
        self.assertFalse(any(m['command']=='validate' and m['token']==second['token'] for m in self.t.sent));self.assertEqual(self.d.captures,3)
        self.assertTrue(self.event(current,'ready'));self.assertTrue(self.event(current,'endpoint'));self.assertEqual(len(self.d.commits),6)
        # The producer already runs provisional retarget; readiness must NOT
        # reset its shared clock via a redundant start command.
        self.assertFalse(any(m['command']=='start' and m['token']==third['token'] for m in self.t.sent))
    def test_context_change_switches_destination_before_retarg_expansion(self):
        old=self.seed();self.event(old,'ready');self.d.block=threading.Event();self.d.started.clear();r=self.request('restore',context=2)
        self.assertTrue(self.d.started.wait(1));self.assertFalse(any(m['command']=='retarget' and m['token']==r['token'] for m in self.t.sent))
        self.d.block.set();self.wait(lambda:self.c.current.validated and any(m['command']=='validate' and m['token']==r['token'] for m in self.t.sent))
        self.assertEqual(set(self.d.destinations),{key(w) for w in self.d.windows});self.assertEqual(self.d.captures,3)
    def test_fresh_relation_failure_never_truncates_to_singleton(self):
        old=self.seed();self.event(old,'ready');self.d.native.pop();r=self.request('restore')
        self.wait(lambda:'failure' in self.c.current.profile)
        self.assertFalse(self.c.current.validated);self.assertEqual(len(self.c.current.members),3)
        self.assertFalse(any(m['command']=='validate' and m['token']==r['token'] for m in self.t.sent));self.assertEqual(len(self.d.commits),3)
    def test_same_pid_foreign_peer_is_not_in_family(self):
        foreign=copy.deepcopy(self.d.windows[0]);foreign.update(address='0xdddd',stableId='dddd');self.d.windows.append(foreign);self.d.native.append(dict(foreign,parent='',parentStableId='',modal=False))
        r=self.seed();self.assertEqual(len(r.members),3);self.assertNotIn(key(foreign),{key(m) for m in r.members})
        with self.assertRaises(ValueError):self.c.request('minimize',foreign['address'],foreign['stableId'],foreign['pid'],context=1)
    def test_peer_reuse_removes_native_authority(self):
        old=self.seed();self.event(old,'ready');self.d.windows[1]['pid']+=100;self.d.native[1]['pid']+=100
        r=self.request('restore');self.wait(lambda:'failure' in self.c.current.profile)
        self.assertEqual(len(self.d.commits),3);self.assertFalse(self.c.current.validated);self.assertFalse(any(m['command']=='validate' and m['token']==r['token'] for m in self.t.sent))
    def test_reduce_during_unvalidated_reversal_settles_previous_accepted_intent(self):
        old=self.seed();self.event(old,'ready');self.d.block=threading.Event();self.d.started.clear();self.request('restore');self.assertTrue(self.d.started.wait(1))
        record=self.c.current;self.d.reduced_flag=True
        # Reduction cannot confer authority on reserved restore. Simulate loss
        # of renderer connection while fresh relation lookup remains blocked.
        with self.c.lock:
            self.d.block.set();self.d.block=None;self.c.transport_failure('reduced while validating')
        self.assertTrue(all(op=='minimize' for op,*_ in self.d.commits));self.assertIsNone(self.c.current)
    def test_fresh_reduced_initial_request_commits_without_renderer(self):
        self.d.reduced_flag=True;r=self.request();self.wait(lambda:self.c.current is None)
        self.assertEqual(len(self.d.commits),3);self.assertFalse(self.t.sent);self.assertEqual(self.d.captures,0)
    def test_atomic_native_commit_prevents_peer_callback_reservation_race(self):
        old=self.seed();self.d.commit_block=threading.Event();self.d.started.clear()
        callback=threading.Thread(target=lambda:self.event(old,'ready'));callback.start();self.assertTrue(self.d.started.wait(1))
        accepted=[];request=threading.Thread(target=lambda:accepted.append(self.request('restore')));request.start();time.sleep(.02)
        self.assertFalse(accepted);self.d.commit_block.set();callback.join(2);request.join(2);self.assertEqual(len(self.d.commits),3);self.assertEqual(len(accepted),1)
    def test_reduce_mid_running_settles_complete_latest_family(self):
        r=self.seed();self.event(r,'ready');self.d.reduced_flag=True;self.c.watchdog()
        self.assertTrue(all(op=='minimize' for op,*_ in self.d.commits));self.assertEqual(len(self.d.commits),6)
        self.assertEqual(self.t.sent[-1]['command'],'cancel');self.event(r,'cancelled');self.assertIsNone(self.c.current)
    def test_unvalidated_deadline_cannot_commit_requested_restore(self):
        old=self.seed();self.event(old,'ready');self.d.block=threading.Event();self.d.started.clear();self.request('restore');self.assertTrue(self.d.started.wait(1))
        r=self.c.current
        with self.c.lock:
            r.profile['receivedNs']=time.monotonic_ns()-3000000000
            self.d.block.set();self.d.block=None;self.c.watchdog()
        self.assertTrue(all(op=='minimize' for op,*_ in self.d.commits));self.assertEqual(self.t.sent[-1]['command'],'cancel')
    def test_wrong_snapshot_digest_event_has_no_native_authority(self):
        r=self.seed();wrong={'event':'ready','token':r.token,'identities':ids(r.members),'servicePromoted':True,'sourceDigests':[{'stableId':m['stableId'],'pid':m['pid'],'digest':'f'*64} for m in r.members]}
        self.assertFalse(self.c.event(wrong));self.assertFalse(self.d.commits)
    def test_changed_native_geometry_does_not_replace_retained_pixels(self):
        old=self.seed();self.event(old,'ready');self.d.windows[1]['size'][0]+=10
        r=self.request('restore');self.wait(lambda:'failure' in self.c.current.profile)
        self.assertFalse(any(m['command']=='validate' and m['token']==r['token'] for m in self.t.sent));self.assertEqual(self.d.captures,3)

if __name__=='__main__':unittest.main()

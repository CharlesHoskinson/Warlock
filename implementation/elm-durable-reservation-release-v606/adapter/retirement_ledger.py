"""Durable reservation retirement. Historical Unknown is never an outcome guess.

The caller owns authenticated native transport and accepted frontend read replies.
This module checks correlation and storage ordering; it never submits an effect.
"""
import copy, hashlib, json, os, secrets
from admission_ledger import AdmissionLedger, storage_key
from durable_ledger import encoded, key, normalize
from recovery_journal import Journal, validate
from endpoint import Refused, binding, canonical, exact, unique
from grant_endpoint import RetirementProof

NAME = 'ledger-v6.json'
MARKER = 'ledger-v6.initialized'
MAX_BYTES = 1048576

def context(value, bound):
    exact(value, ['lifetime','epoch','output','revision'])
    for v in value.values(): canonical(v)
    if value['lifetime'] != bound['lifetime'] or value['epoch'] != bound['frontend']:
        raise Refused('Observation binding')
    return copy.deepcopy(value)

def release_payload(record, proof, observation):
    validate(record)
    if record['schema'] != 2 or record['status'] != 'Unknown':
        raise Refused('Historical release requires Unknown')
    exact(proof, ['protocolVersion','kind','retirementProtocol','operation','binding',
                  'queriedBinding','requestId','sequence','grantState'])
    if type(proof['protocolVersion']) is not int or proof['protocolVersion'] != 3 or type(proof['retirementProtocol']) is not int or proof['retirementProtocol'] != 1:
        raise Refused('Retirement version')
    if proof['kind'] != 'binding-retirement' or proof['operation'] not in ['observe','retire'] or proof['grantState'] != 'Retired':
        raise Refused('Positive native retirement required')
    binding(proof['binding']); binding(proof['queriedBinding'])
    canonical(proof['requestId']); canonical(proof['sequence'])
    if proof['queriedBinding'] != record['binding'] or proof['binding'] == record['binding'] or proof['binding']['lifetime'] != record['binding']['lifetime']:
        raise Refused('Retirement historical scope')
    exact(observation, ['actionRequestId','geometryRequestId','actionContext','geometryContext'])
    canonical(observation['actionRequestId']); canonical(observation['geometryRequestId'])
    a=context(observation['actionContext'], proof['binding'])
    g=context(observation['geometryContext'], proof['binding'])
    if a['output'] != g['output']: raise Refused('Observation output generation')
    # Read IDs, revisions and native proof sequences belong to independent domains.
    return copy.deepcopy({'record':record,'proof':proof,'observation':observation})

class ObservationJoin:
    """Only reads explicitly requested after this proof can complete this join.

    Production coordinator must call accept only for its authenticated read reply
    after frontend delivery/acceptance. No unsolicited/cached IDs are allocated.
    """
    def __init__(self, record, proof):
        if type(proof) is not RetirementProof or not proof.allows_release:
            raise Refused('Typed native retirement proof required')
        self.record=copy.deepcopy(record); self.proof=proof.as_dict()
        self.requested={}; self.accepted={}
        # Validate the proof/record now using a structurally valid placeholder.
        b=self.proof['binding']; c={'lifetime':b['lifetime'],'epoch':b['frontend'],'output':'1','revision':'1'}
        release_payload(self.record,self.proof,{'actionRequestId':'1','geometryRequestId':'1','actionContext':c,'geometryContext':c})
    def expect(self, domain, request_id):
        if domain not in ['action','geometry'] or domain in self.requested: raise Refused('Read already requested/domain')
        canonical(request_id); self.requested[domain]=request_id
    def accept(self, domain, request_id, current_binding, read_context):
        binding(current_binding)
        if current_binding != self.proof['binding'] or self.requested.get(domain) != request_id or domain in self.accepted:
            raise Refused('Post-retirement read correlation')
        self.accepted[domain]=context(read_context,current_binding)
    def observation(self):
        if set(self.accepted) != {'action','geometry'}: raise Refused('Both fresh observations required')
        value={'actionRequestId':self.requested['action'],'geometryRequestId':self.requested['geometry'],
               'actionContext':self.accepted['action'],'geometryContext':self.accepted['geometry']}
        release_payload(self.record,self.proof,value)
        return copy.deepcopy(value)

class RetirementLedger(AdmissionLedger):
    def __init__(self, runtime, instance, lifetime):
        self.poisoned=False
        Journal.__init__(self,runtime,instance,lifetime)
        try:
            with self.host_guard() as directory:
                raw=self.raw(self.fd,NAME,MAX_BYTES)
                if raw is None:
                    if self.raw(self.fd,MARKER,4096) is not None: raise Refused('Retirement ledger missing')
                    # Bootstrap the unchanged predecessor while holding both writer
                    # locks. Its exact bytes remain immutable after migration.
                    previous=AdmissionLedger.__new__(AdmissionLedger)
                    previous.__dict__=self.__dict__.copy()
                    if self.raw(self.fd,'ledger-v5.json',MAX_BYTES) is None:
                        if self.raw(self.fd,'ledger-v5.initialized',4096) is not None: raise Refused('Predecessor missing')
                        previous._bootstrap()
                    previous._ensure_marker()
                    state=previous._load(); raw5=self.raw(self.fd,'ledger-v5.json',MAX_BYTES)
                    history=copy.deepcopy(state['settled'])
                    latest=state['latest']
                    if latest is not None and latest['status'] in ['Committed','Refused'] and not any(key(r)==key(latest) for r in history): history.append(copy.deepcopy(latest))
                    state.update(schema=6,v5SHA256=hashlib.sha256(raw5).hexdigest(),releases=[],settlementHistory=history)
                    self._save(state)
                else: self._validate(json.loads(raw,object_pairs_hook=unique))
                expected={'schema':1,'lifetime':lifetime,'kind':'retirement-ledger-initialized'}
                marker=self.raw(self.fd,MARKER,4096)
                if marker is None: self.atomic(MARKER,encoded(expected))
                else:
                    actual=json.loads(marker,object_pairs_hook=unique)
                    if actual != expected or type(actual.get('schema')) is not int: raise Refused('Retirement initialization marker')
                state=self._sync(directory)
                changed=False
                for r in state['entries']:
                    if r['status']=='Pending': r['status']='Unknown'; changed=True
                if state['latest'] is not None and state['latest']['status']=='Pending': state['latest']['status']='Unknown'; changed=True
                if changed:self._save(state)
        except BaseException: self.close(); raise

    def _validate(self, state):
        fields=['schema','lifetime','entries','watermarks','bootstrapHashes','latest','predecessorName','predecessorSHA256','settled','v5SHA256','releases','settlementHistory']
        exact(state,fields)
        if type(state['schema']) is not int or state['schema'] != 6: raise Refused('Retirement ledger schema')
        raw5=self.raw(self.fd,'ledger-v5.json',MAX_BYTES)
        if raw5 is None or state['v5SHA256'] != hashlib.sha256(raw5).hexdigest(): raise Refused('Predecessor producer changed')
        predecessor=AdmissionLedger._validate(self,json.loads(raw5,object_pairs_hook=unique))
        releases=state['releases']
        if not isinstance(releases,list) or len(releases)>64: raise Refused('Historical release capacity')
        seen=set(); live={key(r):r for r in state['entries']}
        for release in releases:
            exact(release,['id','record','proof','observation','phase'])
            value=release_payload(release['record'],release['proof'],release['observation'])
            if release['id'] != hashlib.sha256(encoded(value)).hexdigest() or key(value['record']) in seen: raise Refused('Historical release identity')
            seen.add(key(value['record']))
            if release['phase'] not in ['Prepared','Released']: raise Refused('Release phase')
            old=live.get(key(value['record']))
            if release['phase']=='Prepared' and old != value['record']: raise Refused('Prepared must remain reserved')
            if release['phase']=='Released' and old is not None: raise Refused('Released cannot remain live')
            mark=next((m for m in state['watermarks'] if m['binding']==value['record']['binding']),None)
            if mark is None or int(mark['request'])<int(value['record']['intent']['request']) or int(mark['generation'])<int(value['record']['intent']['generation']): raise Refused('Historical allocation watermark')
        history=state['settlementHistory']
        if not isinstance(history,list) or len(history)>64: raise Refused('Definitive history capacity')
        definitive={}
        for r in history:
            validate(r)
            if r['schema']!=2 or r['status'] not in ['Committed','Refused'] or r['binding']['lifetime']!=state['lifetime'] or key(r) in seen or key(r) in live or key(r) in definitive:
                raise Refused('Historical outcome consistency')
            definitive[key(r)]=r
            mark=next((m for m in state['watermarks'] if m['binding']==r['binding']),None)
            if mark is None or int(mark['request'])<int(r['intent']['request']) or int(mark['generation'])<int(r['intent']['generation']): raise Refused('Definitive allocation watermark')
        for r in state['settled']:
            if key(r) in seen or definitive.get(key(r))!=r: raise Refused('Settlement must match definitive history')
        if any(key(r) not in set(live)|seen|set(definitive) for r in predecessor['entries']): raise Refused('Migrated reservation lost')
        for r in predecessor['settled']+([predecessor['latest']] if predecessor['latest'] is not None and predecessor['latest']['status'] in ['Committed','Refused'] else []):
            if definitive.get(key(r))!=r: raise Refused('Migrated definitive history lost')
        for prior in predecessor['watermarks']:
            mark=next((m for m in state['watermarks'] if m['binding']==prior['binding']),None)
            if mark is None or int(mark['request'])<int(prior['request']) or int(mark['generation'])<int(prior['generation']): raise Refused('Migrated watermark decreased')
        view={k:copy.deepcopy(state[k]) for k in fields if k not in ['v5SHA256','releases','settlementHistory']}; view['schema']=5
        latest=state['latest']
        if latest is not None and latest['status'] in ['Committed','Refused'] and definitive.get(key(latest))!=latest: raise Refused('Latest definitive history correlation')
        if latest is not None and any(r['phase']=='Released' and r['record']==latest for r in releases): view['latest']=None
        AdmissionLedger._validate(self,view)
        if len(encoded(state))>MAX_BYTES: raise Refused('Retirement byte capacity')
        return state

    def _load(self):
        if self.poisoned: raise Refused('Retirement storage requires explicit correction')
        raw=self.raw(self.fd,NAME,MAX_BYTES)
        if raw is None: raise Refused('Retirement ledger missing')
        return self._validate(json.loads(raw,object_pairs_hook=unique))

    def _save(self,state):
        if self.poisoned: raise Refused('Retirement storage requires explicit correction')
        self._validate(state); raw=encoded(state)
        temporary='retirement-pending-'+secrets.token_hex(12); fd=None
        try:
            previous=self.raw(self.fd,NAME,MAX_BYTES)
            if previous is not None:
                old=self._validate(json.loads(previous,object_pairs_hook=unique))
                releases={r['id']:r for r in state['releases']}
                for r in old['releases']:
                    new=releases.get(r['id'])
                    if new is None or {k:v for k,v in new.items() if k!='phase'}!={k:v for k,v in r.items() if k!='phase'} or (r['phase']=='Released' and new['phase']!='Released'):
                        raise Refused('Release history cannot disappear or regress')
                history={key(r):r for r in state['settlementHistory']}
                if any(history.get(key(r))!=r for r in old['settlementHistory']): raise Refused('Definitive history cannot disappear')
                destinations={key(r) for r in state['entries']+state['settlementHistory']}|{key(r['record']) for r in state['releases'] if r['phase']=='Released'}
                if any(key(r) not in destinations for r in old['entries']): raise Refused('Live reservation cannot disappear without disposition')
                for prior in old['watermarks']:
                    m=next((m for m in state['watermarks'] if m['binding']==prior['binding']),None)
                    if m is None or int(m['request'])<int(prior['request']) or int(m['generation'])<int(prior['generation']): raise Refused('Allocation watermark cannot decrease')
            fd=os.open(temporary,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
            offset=0
            while offset<len(raw):
                try: n=os.write(fd,raw[offset:])
                except InterruptedError: continue
                if n<=0: raise OSError('Retirement write made no progress')
                offset+=n
            os.fsync(fd); closing=fd; fd=None; os.close(closing)
            os.replace(temporary,NAME,src_dir_fd=self.fd,dst_dir_fd=self.fd); os.fsync(self.fd)
        except BaseException: self.poisoned=True; raise
        finally:
            try:
                if fd is not None: os.close(fd)
            except BaseException: self.poisoned=True; raise
            finally:
                try: os.unlink(temporary,dir_fd=self.fd)
                except FileNotFoundError: pass
                except BaseException: self.poisoned=True; raise

    def _remove_admission(self,directory,record):
        name=storage_key(record)+'.json'; raw=self.raw(directory,name,4096)
        if raw is not None:
            admitted=normalize(json.loads(raw,object_pairs_hook=unique))
            if admitted['status']!='Pending' or key(admitted)!=key(record): raise Refused('Exact admission retirement correlation')
            os.unlink(name,dir_fd=directory)
        # Persist absence even when interrupted unlink was already visible.
        os.fsync(directory)

    def _finish(self,directory,state,release):
        try:
            self._remove_admission(directory,release['record'])
            state['entries']=[r for r in state['entries'] if key(r)!=key(release['record'])]
            release['phase']='Released'; self._save(state)
        except BaseException: self.poisoned=True; raise

    def _sync(self,directory,exclude=None):
        state=self._load()
        # A rename visible after interruption does not prove its directory fsync
        # completed. Reestablish the journal barrier before retiring any admission
        # or exposing a recovered Released phase, including an existing marker.
        try: os.fsync(self.fd)
        except BaseException: self.poisoned=True; raise
        for release in state['releases']:
            if release['phase']=='Prepared': self._finish(directory,state,release)
            else:
                # Exact released keys cannot be resurrected by a late C write.
                try: self._remove_admission(directory,release['record'])
                except BaseException: self.poisoned=True; raise
        # A different late admission from a proven retired scope remains blocked
        # until a fresh bounded reconciliation archives its own Unknown record.
        return AdmissionLedger._sync(self,directory,exclude)

    def release(self,join):
        if type(join) is not ObservationJoin: raise Refused('Post-retirement join required')
        payload=release_payload(join.record,join.proof,join.observation())
        identifier=hashlib.sha256(encoded(payload)).hexdigest()
        with self.host_guard() as directory:
            state=self._sync(directory)
            # A fresh legitimate proof/read join after restart cannot rewrite the
            # first durable evidence. Return its immutable historical disposition.
            # Callers must not relabel this with the fresh read IDs/current binding.
            existing=next((r for r in state['releases'] if r['record']==payload['record']),None)
            if existing is not None: return copy.deepcopy(existing)
            if len(state['releases'])>=64: raise Refused('Historical release capacity')
            matching=[r for r in state['entries'] if key(r)==key(payload['record'])]
            if len(matching)!=1 or matching[0]!=payload['record']: raise Refused('Release must match stored Unknown')
            release=dict(payload,id=identifier,phase='Prepared'); state['releases'].append(release)
            self._save(state)  # Persist historical evidence before touching admission.
            self._finish(directory,state,release)
            return copy.deepcopy(release)  # Only after BOTH directory barriers.

    def begin(self,bound,intent,effectProtocol=1):
        binding(bound)
        state=self._load()
        if len(state['settlementHistory'])>=64 or len(state['releases'])>=64:
            raise Refused('History capacity prevents new effect admission')
        if any(r['proof']['queriedBinding']==bound for r in state['releases']):
            raise Refused('Retired scope cannot submit a new effect')
        return AdmissionLedger.begin(self,bound,intent,effectProtocol)

    def _settle_record(self,r):
        r=normalize(r)
        if r['status'] not in ['Committed','Refused','Unknown']: raise Refused('Admission receipt status')
        with self.host_guard() as directory:
            state=self._sync(directory)
            matching=[old for old in state['entries'] if key(old)==key(r)]
            if len(matching)!=1: raise Refused('Admission uncorrelated receipt')
            if r['status']=='Unknown': matching[0]['status']='Unknown'
            else:
                if len(state['settled'])>=64 or len(state['settlementHistory'])>=64: raise Refused('Definitive history capacity')
                state['entries']=[old for old in state['entries'] if key(old)!=key(r)]
                state['settled'].append(copy.deepcopy(r)); state['settlementHistory'].append(copy.deepcopy(r))
            if state['latest'] is not None and key(state['latest'])==key(r): state['latest']=copy.deepcopy(r)
            self._save(state)

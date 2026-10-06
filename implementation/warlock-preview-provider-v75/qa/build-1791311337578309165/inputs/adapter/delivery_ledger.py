"""Bounded mutable delivery certificates anchored to immutable V6 releases.

Typed proof and accepted read transport are trusted coordinator inputs. This
sidecar never changes effect outcomes, reservations or their original archive.
"""
import copy,hashlib,json,os,secrets
from durable_ledger import encoded,key
from endpoint import Refused,exact,unique
from retirement_ledger import RetirementLedger,ObservationJoin,release_payload

NAME='release-deliveries-v1.json'
MARKER='release-deliveries-v1.initialized'
MAX_BYTES=1048576
CAPACITY=64

def certificate(anchor,join):
    if type(join) is not ObservationJoin:raise Refused('Accepted post-proof join required')
    payload=release_payload(join.record,join.proof,join.observation())
    if anchor['phase']!='Released' or anchor['record']!=payload['record']:raise Refused('Exact historical Released anchor required')
    if int(payload['proof']['sequence'])<int(anchor['proof']['sequence']):raise Refused('Proof predates original retirement')
    payload['anchorId']=anchor['id']
    return dict(payload,id=hashlib.sha256(encoded(payload)).hexdigest())

class DeliveryLedger(RetirementLedger):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        try:
            with self.host_guard() as directory:
                parent=self._sync(directory)
                marker=self.raw(self.fd,MARKER,4096)
                raw=self.raw(self.fd,NAME,MAX_BYTES)
                if raw is None:
                    if marker is not None:raise Refused('Delivery sidecar missing after initialization')
                    self._delivery_write(NAME,encoded({'schema':1,'lifetime':self.target['lifetime'],'certificates':[]}))
                else:
                    state=self._delivery_validate(json.loads(raw,object_pairs_hook=unique),parent)
                    # Only an empty initial sidecar can legitimately precede its
                    # marker; certificates are never written before that barrier.
                    if marker is None and state['certificates']:raise Refused('Populated delivery marker missing')
                expected={'schema':1,'lifetime':self.target['lifetime'],'kind':'release-deliveries-initialized'}
                if marker is None:self._delivery_write(MARKER,encoded(expected))
                else:
                    actual=json.loads(marker,object_pairs_hook=unique)
                    if actual!=expected or type(actual.get('schema')) is not int:raise Refused('Delivery initialization marker')
                # Observing a rename after interruption is not a durability proof.
                os.fsync(self.fd)
        except BaseException:self.poisoned=True;self.close();raise

    def _delivery_validate(self,state,parent):
        exact(state,['schema','lifetime','certificates'])
        if type(state['schema']) is not int or state['schema']!=1 or state['lifetime']!=self.target['lifetime']:raise Refused('Delivery schema/lifetime')
        certificates=state['certificates']
        if not isinstance(certificates,list) or len(certificates)>CAPACITY:raise Refused('Delivery capacity')
        seen=set()
        for cert in certificates:
            exact(cert,['id','anchorId','record','proof','observation'])
            payload=release_payload(cert['record'],cert['proof'],cert['observation'])
            anchor=next((r for r in parent['releases'] if r['phase']=='Released' and r['record']==cert['record']),None)
            if anchor is None or cert['anchorId']!=anchor['id'] or int(cert['proof']['sequence'])<int(anchor['proof']['sequence']):raise Refused('Delivery immutable anchor')
            payload['anchorId']=cert['anchorId']
            identity=key(cert['record'])
            if identity in seen or cert['id']!=hashlib.sha256(encoded(payload)).hexdigest():raise Refused('Delivery certificate identity')
            seen.add(identity)
        if len(encoded(state))>MAX_BYTES:raise Refused('Delivery byte capacity')
        return state

    def _delivery_load(self,parent):
        if self.poisoned:raise Refused('Delivery storage requires explicit correction')
        try:
            expected={'schema':1,'lifetime':self.target['lifetime'],'kind':'release-deliveries-initialized'}
            marker=self.raw(self.fd,MARKER,4096)
            if marker is None:raise Refused('Delivery initialization marker missing')
            actual=json.loads(marker,object_pairs_hook=unique)
            if actual!=expected or type(actual.get('schema')) is not int:raise Refused('Delivery initialization marker')
            raw=self.raw(self.fd,NAME,MAX_BYTES)
            if raw is None:raise Refused('Delivery sidecar missing after initialization')
            state=self._delivery_validate(json.loads(raw,object_pairs_hook=unique),parent)
            os.fsync(self.fd)
            return state
        except BaseException:self.poisoned=True;raise

    def _delivery_write(self,name,raw):
        if self.poisoned:raise Refused('Delivery storage requires explicit correction')
        temporary='delivery-pending-'+secrets.token_hex(12);fd=None
        try:
            self.raw(self.fd,name,MAX_BYTES)
            fd=os.open(temporary,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
            offset=0
            while offset<len(raw):
                try:n=os.write(fd,raw[offset:])
                except InterruptedError:continue
                if n<=0:raise OSError('Delivery write made no progress')
                offset+=n
            os.fsync(fd);closing=fd;fd=None;os.close(closing)
            os.replace(temporary,name,src_dir_fd=self.fd,dst_dir_fd=self.fd);os.fsync(self.fd)
        except BaseException:self.poisoned=True;raise
        finally:
            try:
                if fd is not None:os.close(fd)
            except BaseException:self.poisoned=True;raise
            finally:
                try:os.unlink(temporary,dir_fd=self.fd)
                except FileNotFoundError:pass
                except BaseException:self.poisoned=True;raise

    def delivery_snapshot(self):
        try:
            with self.host_guard() as directory:
                parent=self._sync(directory)
                return copy.deepcopy(self._delivery_load(parent))
        except OSError:self.poisoned=True;raise

    def attest(self,join):
        if type(join) is not ObservationJoin:raise Refused('Accepted post-proof join required')
        # Reject malformed or incomplete coordinator input before touching storage.
        release_payload(join.record,join.proof,join.observation())
        try:
            with self.host_guard() as directory:
                parent=self._sync(directory)
                state=self._delivery_load(parent)
                anchor=next((r for r in parent['releases'] if r['phase']=='Released' and r['record']==join.record),None)
                if anchor is None:raise Refused('Exact existing historical Released Unknown required')
                cert=certificate(anchor,join)
                old=next((r for r in state['certificates'] if r['record']==join.record),None)
                if old is not None:
                    if old==cert:return copy.deepcopy(old)
                    if int(cert['proof']['sequence'])<=int(old['proof']['sequence']):raise Refused('Fresh delivery proof sequence required')
                    state['certificates'][state['certificates'].index(old)]=cert
                else:
                    if len(state['certificates'])>=CAPACITY:raise Refused('Delivery capacity')
                    state['certificates'].append(cert)
                self._delivery_validate(state,parent)
                self._delivery_write(NAME,encoded(state))
                return copy.deepcopy(cert)
        except OSError:self.poisoned=True;raise

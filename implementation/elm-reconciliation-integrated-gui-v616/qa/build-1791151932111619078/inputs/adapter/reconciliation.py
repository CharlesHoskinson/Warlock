"""Native retirement precedes frontend-requested reads, durable release and wire.

The owning daemon supplies authenticated599 proofs and validated native read
replies. This coordinator never makes an effect, an unsolicited read or an
allocation in the effect/read ID domains.
"""
import copy
from durable_ledger import key
from endpoint import Refused,binding,canonical,exact
from retirement_ledger import ObservationJoin,context

class Reconciliation:
    def __init__(self,client,ledger,send):
        self.client=client;self.ledger=ledger;self.send=send
        self.bound=copy.deepcopy(binding(client.bound))
        self.pending={};self.requested={};self.accepted={};self.proof_request=0
        self.active=None;self.ready=False;self.announced=False
        self.completed={}

    def current(self):
        if binding(self.client.bound)!=self.bound:raise Refused('Reconciliation binding changed')

    def announce(self):
        self.current()
        if self.announced:raise Refused('Reconciliation already announced')
        self.announced=True
        records=self.ledger.synchronization_snapshot()['entries']
        if len(records)>64:raise Refused('Reconciliation capacity')
        proofs={}
        for record in records:
            if record['status']!='Unknown':raise Refused('Recovered record must be durably Unknown')
            self.send({'protocolVersion':3,'kind':'host-reservation-unknown','binding':copy.deepcopy(self.bound),'record':copy.deepcopy(record)})
        # Every full record is delivered before its proof; all proofs precede
        # processing any frontend read request, including requests already queued.
        for record in records:
            self.current()
            if record['binding']==self.bound:continue  # Never retire our own grant.
            scope=tuple(record['binding'][k] for k in ['lifetime','session','frontend'])
            if scope not in proofs:
                self.proof_request+=1;request=str(self.proof_request);canonical(request)
                proof=self.client.retire(request,record['binding']);self.current()
                # Full structural/typed correlation before publishing this proof.
                ObservationJoin(record,proof)
                proofs[scope]=proof
            self.pending[key(record)]=(copy.deepcopy(record),proofs[scope])
        self._announce_next()

    def _announce_next(self):
        if self.active is not None and not any(p==self.active for _,p in self.pending.values()):
            self.completed[self.active.request_id]=self.active
        self.current();self.requested={};self.accepted={};self.ready=False
        self.active=next((p for _,p in self.pending.values()),None)
        # Serial proof scopes retain the C carrier's unchanged16-request bound.
        if self.active is not None:self.send(self.active.as_dict())

    def proof_ready(self,request):
        self.current()
        exact(request,['protocolVersion','kind','binding','proofRequestId','queriedBinding'])
        if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or request['kind']!='reconciliation-ready':raise Refused('Reconciliation ready version/kind')
        binding(request['binding']);binding(request['queriedBinding']);canonical(request['proofRequestId'])
        old=self.completed.get(request['proofRequestId'])
        if old is not None and request['binding']==self.bound and request['queriedBinding']==old.queried_binding.as_dict():
            return  # Late completed-scope acknowledgement never readies a new scope.
        if self.active is None or request['binding']!=self.bound or request['queriedBinding']!=self.active.queried_binding.as_dict() or request['proofRequestId']!=self.active.request_id:
            raise Refused('Reconciliation ready proof correlation')
        # Duplicates are informational; they cannot invalidate already fresh reads.
        self.ready=True

    def requested_read(self,domain,request_id):
        self.current()
        if domain not in ['action','geometry']:raise Refused('Reconciliation read domain')
        canonical(request_id)
        if not self.pending or not self.ready:return
        self.requested[domain]=request_id;self.accepted.pop(domain,None)

    def delivered_read(self,domain,request_id,read_context):
        """Call only AFTER send(validated read reply) returns successfully."""
        self.current()
        if not self.pending or not self.ready:return
        if self.requested.get(domain)!=request_id:return  # Pre-proof/stale read cannot qualify.
        self.accepted[domain]=context(read_context,self.bound)
        if set(self.accepted)!={'action','geometry'}:return
        if self.accepted['action']['output']!=self.accepted['geometry']['output']:return
        for identity,(record,proof) in list(self.pending.items()):
            if proof!=self.active:continue
            self.current();join=ObservationJoin(record,proof)
            for d in ['action','geometry']:
                join.expect(d,self.requested[d]);join.accept(d,self.requested[d],self.bound,self.accepted[d])
            released=self.ledger.release(join)
            self.current()
            if released['phase']!='Released':raise Refused('Unpersisted release disposition')
            # An already-released historical result keeps its original context.
            # Never relabel it with this fresh proof/read IDs for a frontend frame.
            if released['proof']==proof.as_dict() and released['observation']==join.observation():
                release={k:copy.deepcopy(released[k]) for k in ['id','proof','observation']}
                self.send({'protocolVersion':3,'kind':'host-reservation-released','binding':copy.deepcopy(self.bound),'record':copy.deepcopy(record),'release':release})
            del self.pending[identity]
        self._announce_next()

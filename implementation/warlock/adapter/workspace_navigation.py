"""Typed durable workspace navigation. Reads never submit an effect.

Shares the existing secure namespace/writer lock, but never represents a
workspace as a window incarnation or enters family custody reconciliation.
"""
import copy,json,os,re
from endpoint import Refused,binding,canonical,exact,unique

NAME='workspace-navigation-v1.json'
MARKER='workspace-navigation-v1.initialized'
STATUSES={'Pending','Unknown','Committed','Refused'}

def row(value):
    exact(value,['identity','generation','monitor','outputOwnershipGeneration'])
    canonical(value['identity']);canonical(value['generation']);canonical(value['monitor'],True);canonical(value['outputOwnershipGeneration'])
    if int(value['identity'])>(1<<63)-1:raise Refused('Workspace signed identity bound')
    return value

def intent(value,bound):
    exact(value,['request','generation','source','destination','context'])
    canonical(value['request']);canonical(value['generation']);row(value['source']);row(value['destination'])
    context=value['context'];exact(context,['lifetime','epoch','output','revision'])
    for counter in context.values():canonical(counter)
    if context['lifetime']!=bound['lifetime'] or context['epoch']!=bound['frontend']:raise Refused('Workspace context authority')
    return value

def record(value,lifetime):
    exact(value,['schema','binding','intent','status','reason'])
    if type(value['schema']) is not int or value['schema']!=1 or binding(value['binding'])['lifetime']!=lifetime:raise Refused('Workspace recovery namespace')
    intent(value['intent'],value['binding'])
    if value['status'] not in STATUSES or not isinstance(value['reason'],str) or not re.fullmatch('[a-z][a-z0-9-]{0,63}',value['reason']):raise Refused('Workspace recovery status/reason')
    return value

def encoded(value):return json.dumps(value,separators=(',',':'),ensure_ascii=True).encode()

def native_outcome(client,value,bound,selected):
    exact(value,['protocolVersion','kind','workspaceProtocol','binding','intent','status','reason'])
    if type(value['protocolVersion']) is not int or value['protocolVersion']!=3 or type(value['workspaceProtocol']) is not int or value['workspaceProtocol']!=1 or value['kind']!='workspace-navigation-outcome':raise Refused('Workspace outcome protocol')
    result=record({k:value[k] for k in ['binding','intent','status','reason']}|{'schema':1},bound['lifetime'])
    if result['binding']!=bound or result['intent']!=selected or result['status']=='Pending':raise Refused('Workspace outcome correlation')
    return result

class Navigation:
    def __init__(self,recovery):
        self.ledger=recovery.ledger;self.poisoned=False;self.read_request=0
        with self.ledger.host_guard():
            raw=self.ledger.raw(self.ledger.fd,NAME,4096);marker=self.ledger.raw(self.ledger.fd,MARKER,4096)
            expected={'schema':1,'lifetime':self.ledger.target['lifetime'],'kind':'workspace-navigation-initialized'}
            if raw is None:
                if marker is not None:raise Refused('Workspace journal missing after initialization')
                self._write(None)
            elif marker is None and json.loads(raw,object_pairs_hook=unique) is not None:raise Refused('Workspace journal marker missing')
            if marker is None:self.ledger.atomic(MARKER,encoded(expected))
            elif json.loads(marker,object_pairs_hook=unique)!=expected:raise Refused('Workspace journal marker mismatch')
            self._load();os.fsync(self.ledger.fd)
    def attach(self,client):
        response=client.request({'protocolVersion':3,'kind':'workspace-navigation-attach','workspaceProtocol':1,'binding':client.bound})
        exact(response,['protocolVersion','kind','workspaceProtocol','binding','existingEmptyOnly','historyCapacity'])
        if type(response['protocolVersion']) is not int or response['protocolVersion']!=3 or type(response['workspaceProtocol']) is not int or response['workspaceProtocol']!=1 or response['kind']!='workspace-navigation-attached' or binding(response['binding'])!=client.bound or response['existingEmptyOnly'] is not True or type(response['historyCapacity']) is not int or response['historyCapacity']!=64:raise Refused('Workspace capability correlation')
        return response
    def _load(self):
        if self.poisoned:raise Refused('Workspace storage requires correction')
        raw=self.ledger.raw(self.ledger.fd,NAME,4096)
        if raw is None:raise Refused('Workspace journal missing')
        value=json.loads(raw,object_pairs_hook=unique)
        return record(value,self.ledger.target['lifetime']) if value is not None else None
    def _write(self,value):
        if self.poisoned:raise Refused('Workspace storage requires correction')
        try:
            if value is not None:record(value,self.ledger.target['lifetime'])
            self.ledger.atomic(NAME,encoded(value))
        except BaseException:self.poisoned=True;raise
    def blocked(self):
        with self.ledger.host_guard():
            value=self._load();return value is not None and value['status'] in {'Pending','Unknown'}
    def begin(self,bound,selected):
        binding(bound);intent(selected,bound)
        with self.ledger.host_guard() as directory:
            prior=self._load()
            if prior is None or prior['binding']!=bound or prior['intent']!=selected or prior['status']!='Pending':raise Refused('Exact host workspace admission required; no replay')
            # Native dispatch is permitted only after this durable Unknown write.
            # Losing either ACK or process never causes automatic submission.
            prior=copy.deepcopy(prior);prior['status']='Unknown';prior['reason']='effect-unproven';self._write(prior)
            window_state=self.ledger._sync(directory)
            if window_state['entries']:
                prior['status']='Refused';prior['reason']='window-operation-unresolved';self._write(prior);return prior
            return None
    def settle(self,terminal):
        record(terminal,self.ledger.target['lifetime'])
        with self.ledger.host_guard():
            prior=self._load()
            if prior is None or prior['binding']!=terminal['binding'] or prior['intent']!=terminal['intent'] or prior['status']!='Unknown' or terminal['status']=='Pending':raise Refused('Workspace settlement correlation')
            self._write(terminal)
    def recover(self,client):
        with self.ledger.host_guard():
            value=copy.deepcopy(self._load())
            if value is not None and value['status']=='Pending':
                value['status']='Unknown';value['reason']='delivery-unproven';self._write(value)
        if value is not None and value['status']=='Unknown':
            self.read_request+=1;request_id=str(self.read_request)
            response=client.request({'protocolVersion':3,'kind':'workspace-navigation-state-request','workspaceProtocol':1,'binding':client.bound,'requestId':request_id,'record':{'binding':value['binding'],'intent':value['intent']}})
            exact(response,['protocolVersion','kind','workspaceProtocol','binding','requestId','record'])
            if type(response['protocolVersion']) is not int or response['protocolVersion']!=3 or type(response['workspaceProtocol']) is not int or response['workspaceProtocol']!=1 or response['kind']!='workspace-navigation-state' or binding(response['binding'])!=client.bound or response['requestId']!=request_id:raise Refused('Workspace state correlation')
            observed=record(response['record'],client.bound['lifetime'])
            if observed['binding']!=value['binding'] or observed['intent']!=value['intent'] or observed['status']=='Pending':raise Refused('Workspace historical identity mismatch')
            self.settle(observed);value=observed
        return {'protocolVersion':3,'kind':'workspace-navigation-recovery','workspaceProtocol':1,'binding':copy.deepcopy(client.bound),'record':value}
    def handle(self,client,request):
        kind=request.get('kind')
        exact(request,['protocolVersion','kind','workspaceProtocol','binding']+(['intent'] if kind=='workspace-navigation' else []))
        if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or type(request['workspaceProtocol']) is not int or request['workspaceProtocol']!=1 or binding(request['binding'])!=client.bound:raise Refused('Workspace request scope')
        if kind=='workspace-navigation-recover':return self.recover(client)
        if kind!='workspace-navigation':raise Refused('Workspace request kind')
        selected=intent(request['intent'],client.bound)
        local=self.begin(client.bound,selected)
        if local is not None:return {'protocolVersion':3,'kind':'workspace-navigation-outcome','workspaceProtocol':1,**{k:local[k] for k in ['binding','intent','status','reason']}}
        response=client.request(request);terminal=native_outcome(client,response,client.bound,selected);self.settle(terminal)
        return response

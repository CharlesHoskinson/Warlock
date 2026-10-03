"""Fresh adapter draw order, independent of modal focus and native authority."""
from collections import defaultdict
import re
from scene_controller import key


def checked_identity(w):
    if (not isinstance(w, dict) or re.fullmatch(r'0x[0-9a-f]{1,16}', str(w.get('address',''))) is None
            or re.fullmatch(r'[0-9a-f]{1,16}', str(w.get('stableId',''))) is None
            or type(w.get('pid')) is not int or w['pid'] < 1):
        raise ValueError('exact native paint identity required')
    return key(w)


def siblings(members):
    groups=defaultdict(list)
    for w in members:
        groups[w.get('parent')].append(w)
    return [group for parent,group in groups.items() if parent and len(group)>1]


def needs_active_witness(members):
    return any(sum(w.get('floating') is False for w in group)>1 for group in siblings(members))


def order_family(members, native, *, active=None, active_observed=False):
    """Ancestor first; independent siblings use exact native render pass/vector.

    The caller first obtains the established complete native family graph.
    This function never queries, infers shared-PID edges or changes focus.
    """
    if not isinstance(members,list) or not 1<=len(members)<=64 or not isinstance(native,list):
        raise ValueError('complete bounded family and native paint witness required')
    vector={}
    for index,w in enumerate(native):
        identity=checked_identity(w)
        if identity[0] in vector:
            raise ValueError('duplicate native vector address')
        vector[identity[0]]=(identity,index,w)
    selected={}
    parents={}
    for w in members:
        identity=checked_identity(w)
        if identity in selected or any(k[0]==identity[0] for k in selected):
            raise ValueError('duplicate selected family identity')
        observed=vector.get(identity[0])
        if observed is None or observed[0]!=identity:
            raise ValueError('missing/reused selected native vector identity')
        n=observed[2]
        if w.get('parent')!=n.get('parent') or w.get('parentStableId')!=n.get('parentStableId'):
            raise ValueError('selected parent witness changed')
        if type(w.get('floating')) is not bool or type(w.get('pinned')) is not bool:
            raise ValueError('native render plane missing')
        if type(w.get('fullscreen')) is not int or not 0<=w['fullscreen']<=3:
            raise ValueError('native fullscreen pass missing')
        if not isinstance(n.get('parent'),str) or not isinstance(n.get('parentStableId'),str):
            raise ValueError('complete explicit parent witness required')
        selected[identity]=w
    by_address={identity[0]:identity for identity in selected}
    for identity,w in selected.items():
        parent=w['parent']
        if not parent:
            if w['parentStableId']:
                raise ValueError('root has stale parent stable identity')
            parents[identity]=None
        else:
            parent_identity=by_address.get(parent)
            if not parent_identity or parent_identity[1]!=w['parentStableId']:
                raise ValueError('selected exact ancestor missing/reused')
            parents[identity]=parent_identity
    if sum(p is None for p in parents.values())!=1:
        raise ValueError('family must have one exact owner')
    for identity in selected:
        visited=set()
        ancestor=identity
        while ancestor is not None:
            if ancestor in visited:
                raise ValueError('selected transient cycle')
            visited.add(ancestor)
            ancestor=parents[ancestor]
    for group in siblings(members):
        if any(w['fullscreen'] for w in group):
            raise ValueError('independent fullscreen sibling pass is ambiguous')
    if needs_active_witness(members) and active_observed is not True:
        raise ValueError('active tiled paint witness unavailable')
    if active is not None and (not isinstance(active,tuple) or len(active)!=3):
        raise ValueError('exact active identity witness required')
    def paint(identity):
        w=selected[identity]
        plane=2 if w['floating'] and w['pinned'] else 1 if w['floating'] else 0
        active_tiled=plane==0 and active==identity
        return plane,active_tiled,vector[identity[0]][1]
    emitted=[]
    done=set()
    while len(emitted)<len(selected):
        eligible=[identity for identity,parent in parents.items()
                  if identity not in done and (parent is None or parent in done)]
        if not eligible:
            raise ValueError('no complete acyclic family order')
        identity=min(eligible,key=paint)
        emitted.append(selected[identity]);done.add(identity)
    return emitted

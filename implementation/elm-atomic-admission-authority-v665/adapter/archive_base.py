"""Isolated immutable paged history primitive. No native/ledger authority."""
import base64
from collections import OrderedDict
import fcntl
import hashlib
import json
import math
import os
import re
import stat
import uuid

class ArchiveError(Exception): pass
class Refused(ArchiveError): pass
class Corrupt(ArchiveError): pass
class Poisoned(ArchiveError): pass

KINDS={'Admission','Unknown','Terminal','Prepared','Released','DeliveryAttestation','Predecessor'}
MAX64=(1<<64)-1
PAGE=16384
EVENT=65536
NAME=re.compile(r'^(event|index|root)-[0-9a-f]{64}\.json$')

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()

def pairs(items):
    result={}
    for k,v in items:
        if k in result: raise Corrupt('duplicate JSON key')
        result[k]=v
    return result

def decode(data):
    def finite_float(value):
        number=float(value)
        if not math.isfinite(number):raise Corrupt('overflowed JSON number')
        return number
    try:
        return json.loads(data,object_pairs_hook=pairs,parse_float=finite_float,parse_constant=lambda x: (_ for _ in ()).throw(Corrupt('non-finite JSON')))
    except (ValueError,UnicodeError,RecursionError) as e: raise Corrupt('invalid JSON') from e

def fields(x,names):
    if type(x) is not dict or set(x)!=set(names): raise Corrupt('schema fields')

def integer(x,maximum=MAX64):
    if type(x) is not int or not 0<=x<=maximum: raise Corrupt('noncanonical counter')
    return x

def ref(data,kind):
    digest=hashlib.sha256(data).hexdigest()
    return {'name':kind+'-'+digest+'.json','sha256':digest,'size':len(data)}

class Archive:
    def __init__(self,path,*,byte_quota=1<<30,inode_quota=100000,hook=None):
        integer(byte_quota);integer(inode_quota)
        self.path=os.path.abspath(path);self.uid=os.getuid();self.hook=hook or (lambda _:None)
        self.poisoned=False;self.closed=False;self.cache=OrderedDict();self.max_cache=0;self.page_reads=0
        self.dfd=None;self.lfd=None;self.byte_quota=byte_quota;self.inode_quota=inode_quota
        if os.path.realpath(self.path)!=self.path: raise Corrupt('symlink path component')
        try:
            os.mkdir(self.path,0o700)
            parentfd=os.open(os.path.dirname(self.path),os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
            try:self._call('archive-parent:fsync',lambda:os.fsync(parentfd))
            finally:os.close(parentfd)
        except FileExistsError: pass
        try:
            self.dfd=os.open(self.path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
            st=os.fstat(self.dfd)
            if st.st_uid!=self.uid or stat.S_IMODE(st.st_mode)!=0o700: raise Corrupt('private archive directory required')
            self.dir_identity=(st.st_dev,st.st_ino)
            self.lfd=os.open('WRITER',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.dfd)
            self._file_stat(os.fstat(self.lfd));fcntl.flock(self.lfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.lock_identity=(os.fstat(self.lfd).st_dev,os.fstat(self.lfd).st_ino)
            self._guard()
            if not self._exists('MARKER'):
                if self._exists('CURRENT') or self._exists('QUOTA'): raise Corrupt('incomplete bootstrap; explicit operator recovery required')
                self.lifetime=uuid.uuid4().hex
                if byte_quota<4096 or inode_quota<5:raise Refused('bootstrap capacity')
                self.quota={'schema':1,'lifetime':self.lifetime,'bytes':4096,'files':5}
                self._atomic('QUOTA',canonical(self.quota),'quota');self._sync('quota-dir')
                empty={'schema':1,'lifetime':self.lifetime,'generation':0,'count':0,'predecessor':None,'index':None,'newPages':[]}
                self.root_ref=ref(canonical(empty),'root');self._immutable(self.root_ref,canonical(empty),'manifest');self._sync('manifest-dir')
                self._atomic('CURRENT',canonical({'schema':1,'lifetime':self.lifetime,'root':self.root_ref}),'current');self._sync('root')
                self._atomic('MARKER',canonical({'schema':1,'lifetime':self.lifetime}),'marker');self._sync('marker-dir')
            marker=self._json('MARKER',1024);fields(marker,('schema','lifetime'))
            if type(marker['schema']) is not int or marker['schema']!=1 or type(marker['lifetime']) is not str or not re.fullmatch('[0-9a-f]{32}',marker['lifetime']): raise Corrupt('marker')
            self.lifetime=marker['lifetime']
            self.quota=self._quota()
            current=self._current();self.root_ref=current['root'];self.root=self._root(self.root_ref)
            if self.root['predecessor'] is not None:
                predecessor=self._root(self.root['predecessor'])
                if predecessor['generation']+1!=self.root['generation'] or predecessor['count']+1!=self.root['count']: raise Corrupt('predecessor transition')
            elif self.root['generation']!=0 or self.root['count']!=0: raise Corrupt('initial root')
            for p in self.root['newPages']:
                obj=self._load(p)
                if p['name'].startswith('event-'):self._event(obj)
                else:self._index(obj)
            if self.root['index'] is not None:self._index(self._load(self.root['index']),0)
            self._sync('restart-root')  # NO positive lookup/absence before this succeeds.
        except BaseException:
            self.poisoned=True;self.close();raise

    def _call(self,name,fn):
        self.hook('before:'+name)
        result=fn()
        self.hook('after:'+name)
        return result

    def _exists(self,name):
        try:os.stat(name,dir_fd=self.dfd,follow_symlinks=False);return True
        except FileNotFoundError:return False

    def _file_stat(self,st):
        if not stat.S_ISREG(st.st_mode) or st.st_uid!=self.uid or stat.S_IMODE(st.st_mode)!=0o600 or st.st_nlink!=1:raise Corrupt('unsafe file')

    def _guard(self):
        if self.poisoned or self.closed:raise Poisoned('handle unavailable')
        st=os.stat(self.path,follow_symlinks=False)
        if not stat.S_ISDIR(st.st_mode) or stat.S_IMODE(st.st_mode)!=0o700 or st.st_uid!=self.uid or (st.st_dev,st.st_ino)!=self.dir_identity:raise Corrupt('directory replaced')
        st=os.stat('WRITER',dir_fd=self.dfd,follow_symlinks=False);self._file_stat(st)
        if (st.st_dev,st.st_ino)!=self.lock_identity:raise Corrupt('writer lock replaced')

    def _read(self,name,limit):
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=self.dfd)
        try:
            st=os.fstat(fd);self._file_stat(st)
            if st.st_size>limit:raise Corrupt('oversized file')
            chunks=[];remaining=limit+1
            while remaining:
                part=os.read(fd,remaining)
                if not part:break
                chunks.append(part);remaining-=len(part)
            data=b''.join(chunks)
            if len(data)>limit or len(data)!=st.st_size:raise Corrupt('changed/oversized file')
            return data
        finally:os.close(fd)

    def _json(self,name,limit):return decode(self._read(name,limit))

    def _check_ref(self,r,kind=None):
        fields(r,('name','sha256','size'))
        if type(r['name']) is not str or not NAME.fullmatch(r['name']):raise Corrupt('reference name')
        if type(r['sha256']) is not str or r['name'].split('-')[1][:-5]!=r['sha256']:raise Corrupt('reference digest')
        if kind and not r['name'].startswith(kind+'-'):raise Corrupt('reference kind')
        integer(r['size'],EVENT if r['name'].startswith('event-') else PAGE)
        if not r['size']:raise Corrupt('empty reference')

    def _load(self,r):
        self._check_ref(r);data=self._read(r['name'],r['size']);self.page_reads+=1
        if len(data)!=r['size'] or hashlib.sha256(data).hexdigest()!=r['sha256']:raise Corrupt('page hash/size')
        # Every cache hit still validates disk bytes; same-UID edits are not hidden.
        if r['name'] in self.cache: obj=self.cache.pop(r['name'])
        else:obj=decode(data)
        self.cache[r['name']]=obj
        if len(self.cache)>64:self.cache.popitem(last=False)
        self.max_cache=max(self.max_cache,len(self.cache));return obj

    def _index(self,x,depth=None):
        if type(x) is not dict or x.get('schema')!=1 or type(x.get('schema')) is not int:raise Corrupt('index schema')
        d=integer(x.get('depth'),16)
        if depth is not None and depth!=d:raise Corrupt('index depth')
        if d<16:
            fields(x,('schema','depth','children'))
            if type(x['children']) is not dict or not 1<=len(x['children'])<=16:raise Corrupt('branch bound')
            for nibble,r in x['children'].items():
                if nibble not in '0123456789abcdef' or len(nibble)!=1:raise Corrupt('branch edge')
                self._check_ref(r,'index')
        else:
            fields(x,('schema','depth','entries'))
            if type(x['entries']) is not list or not 1<=len(x['entries'])<=32:raise Corrupt('leaf bound')
            hashes=[]
            for e in x['entries']:
                fields(e,('keyHash','event'))
                if type(e['keyHash']) is not str or not re.fullmatch('[0-9a-f]{64}',e['keyHash']):raise Corrupt('key digest')
                hashes.append(e['keyHash']);self._check_ref(e['event'],'event')
            if hashes!=sorted(set(hashes)):raise Corrupt('leaf uniqueness/order')
        return x

    def _event(self,x):
        fields(x,('schema','key','kind','payload'))
        if type(x['schema']) is not int or x['schema']!=1 or x['kind'] not in KINDS:raise Corrupt('event schema')
        if type(x['key']) is not dict or not x['key'] or len(canonical(x['key']))>2048:raise Corrupt('full key')
        if type(x['payload']) is not str:raise Corrupt('payload encoding')
        try:raw=base64.b64decode(x['payload'],validate=True)
        except ValueError as e:raise Corrupt('payload encoding') from e
        if len(raw)>16384 or type(decode(raw)) is not dict or base64.b64encode(raw).decode()!=x['payload']:raise Corrupt('payload schema/size')
        return raw

    def _root(self,r):
        self._check_ref(r,'root');x=self._load(r);fields(x,('schema','lifetime','generation','count','predecessor','index','newPages'))
        if type(x['schema']) is not int or x['schema']!=1 or x['lifetime']!=self.lifetime:raise Corrupt('root lifetime/schema')
        if integer(x['generation'])!=integer(x['count']):raise Corrupt('root count')
        if x['predecessor'] is not None:self._check_ref(x['predecessor'],'root')
        if x['index'] is not None:self._check_ref(x['index'],'index')
        if type(x['newPages']) is not list or len(x['newPages'])>18:raise Corrupt('publication closure bound')
        names=[]
        for p in x['newPages']:
            self._check_ref(p)
            if p['name'].startswith('root-'):raise Corrupt('closure root recursion')
            names.append(p['name'])
        if len(names)!=len(set(names)):raise Corrupt('duplicate closure page')
        if x['count'] and (len(names)!=18 or sum(n.startswith('event-') for n in names)!=1 or x['index']['name'] not in names):raise Corrupt('publication closure shape')
        if self.quota['files']<5+x['count']*22:raise Corrupt('root exceeds reservation')
        if (x['count']==0)!=(x['index'] is None):raise Corrupt('empty root index')
        return x

    def _current(self):
        x=self._json('CURRENT',1024);fields(x,('schema','lifetime','root'))
        if type(x['schema']) is not int or x['schema']!=1 or x['lifetime']!=self.lifetime:raise Corrupt('CURRENT schema/lifetime')
        self._check_ref(x['root'],'root');return x

    def _quota(self):
        x=self._json('QUOTA',1024);fields(x,('schema','lifetime','bytes','files'))
        if type(x['schema']) is not int or x['schema']!=1 or x['lifetime']!=self.lifetime:raise Corrupt('quota schema')
        integer(x['bytes']);integer(x['files'])
        if x['bytes']>self.byte_quota or x['files']>self.inode_quota:raise Refused('configured capacity below durable charge')
        return x

    def _sync(self,label):self._call(label+':fsync',lambda:os.fsync(self.dfd))

    def _atomic(self,name,data,label):
        # Fixed slots for mutable publication files prevent uncharged QUOTA
        # orphan accumulation. A leftover slot refuses further mutation until
        # separate reviewed recovery; it never gets overwritten silently.
        tmp='.tmp-'+name;fd=None;created=False
        try:
            self.hook('before:'+label+':open')
            fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.dfd)
            created=True
            self.hook('after:'+label+':open')
            offset=0
            while offset<len(data):
                n=self._call(label+':write',lambda:os.write(fd,data[offset:]))
                if n<=0:raise OSError('zero write')
                offset+=n
            self._call(label+':fsync',lambda:os.fsync(fd))
            self.hook('before:'+label+':close');os.close(fd);fd=None;self.hook('after:'+label+':close')
            self._call(label+':rename',lambda:os.replace(tmp,name,src_dir_fd=self.dfd,dst_dir_fd=self.dfd))
        finally:
            if fd is not None:
                try:os.close(fd)
                except OSError: self.poisoned=True;raise
            if created and self._exists(tmp):
                try:self._call(label+':cleanup',lambda:os.unlink(tmp,dir_fd=self.dfd))
                except BaseException:self.poisoned=True;raise

    def _immutable(self,r,data,label):
        if self._exists(r['name']):
            if self._read(r['name'],r['size'])!=data:raise Corrupt('immutable content collision')
        else:self._atomic(r['name'],data,label)

    def _live(self):
        self._guard()
        if self._current()['root']!=self.root_ref:raise Corrupt('CURRENT changed while writer active')

    def _find(self,key,root):
        digest=hashlib.sha256(canonical(key)).hexdigest();r=root['index']
        for depth in range(17):
            if r is None:return None
            node=self._index(self._load(r),depth)
            if depth<16:r=node['children'].get(digest[depth]);continue
            for entry in node['entries']:
                if entry['keyHash']==digest:
                    obj=self._load(entry['event']);self._event(obj)
                    if canonical(obj['key'])!=canonical(key):raise Corrupt('full key digest collision')
                    return obj
        return None

    def lookup(self,key):
        try:self._live();self._key(key);obj=self._find(key,self.root);return None if obj is None else self._event(obj)
        except Refused:raise
        except BaseException:self.poisoned=True;raise

    def _key(self,key):
        if type(key) is not dict or not key:raise Refused('full key required')
        try: data=canonical(key);decode(data)
        except (TypeError,ValueError,Corrupt,RecursionError) as e:raise Refused('invalid key') from e
        if len(data)>2048:raise Refused('key too large')

    def append(self,key,kind,payload):
        self._key(key)
        if kind not in KINDS or type(payload) is not bytes or len(payload)>16384:raise Refused('kind/payload bound')
        try:
            if type(decode(payload)) is not dict:raise Refused('object payload required')
        except Corrupt as e:raise Refused('invalid caller JSON') from e
        obj={'schema':1,'key':key,'kind':kind,'payload':base64.b64encode(payload).decode()};data=canonical(obj)
        try:
            self._live();old=self._find(key,self.root)
            if old is not None:
                if canonical(old)!=data:raise Refused('immutable key conflict')
                return self.root_ref['sha256']
            if self.root['generation']==MAX64:raise Refused('generation exhausted')
            event_ref=ref(data,'event');planned=[(event_ref,data)]
            digest=hashlib.sha256(canonical(key)).hexdigest()
            def cow(r,depth):
                node=self._index(self._load(r),depth) if r is not None else {'schema':1,'depth':depth,**({'children':{}} if depth<16 else {'entries':[]})}
                if depth<16:
                    children=dict(node['children']);children[digest[depth]]=cow(children.get(digest[depth]),depth+1);new={'schema':1,'depth':depth,'children':children}
                else:
                    if len(node['entries'])>=32:raise Refused('collision bucket exhausted')
                    entries=node['entries']+[{'keyHash':digest,'event':event_ref}];new={'schema':1,'depth':depth,'entries':sorted(entries,key=lambda e:e['keyHash'])}
                encoded=canonical(new)
                if len(encoded)>PAGE:raise Refused('page exhausted')
                rr=ref(encoded,'index');planned.append((rr,encoded));return rr
            index=cow(self.root['index'],0)
            newroot={'schema':1,'lifetime':self.lifetime,'generation':self.root['generation']+1,'count':self.root['count']+1,'predecessor':self.root_ref,'index':index,'newPages':[p for p,_ in planned]}
            root_data=canonical(newroot)
            if len(root_data)>PAGE:raise Refused('root size')
            newref=ref(root_data,'root')
            quota=self._quota()
            if quota['bytes']<self.quota['bytes'] or quota['files']<self.quota['files']:raise Corrupt('quota rollback')
            # Conservative charge includes temporary publication overhead; orphan charges are never refunded.
            charged={'schema':1,'lifetime':self.lifetime,'bytes':quota['bytes']+sum(len(b) for _,b in planned)+len(root_data)+4096,'files':quota['files']+len(planned)+4}
            if charged['bytes']>self.byte_quota or charged['files']>self.inode_quota:raise Refused('archive quota exhausted')
            self._atomic('QUOTA',canonical(charged),'quota');self._sync('quota-dir');self.quota=charged
            for p,b in planned:self._immutable(p,b,'page')
            self._sync('pages-dir')
            self._immutable(newref,root_data,'manifest');self._sync('manifest-dir')
            self._atomic('CURRENT',canonical({'schema':1,'lifetime':self.lifetime,'root':newref}),'current');self._sync('root')
            self.root_ref=newref;self.root=newroot
            return newref['sha256']
        except Refused:raise
        except BaseException:self.poisoned=True;raise

    def batches(self,limit=32):
        """Pinned immutable root. DFS stack <=16*16 refs; no history-size list."""
        if type(limit) is not int or not 1<=limit<=32:raise Refused('batch bound')
        self._live();pinned=self.root_ref.copy()
        def walk():
            try:
                root=self._root(pinned);stack=[] if root['index'] is None else [(root['index'],0,'')];batch=[]
                while stack:
                    self._guard();r,d,prefix=stack.pop();node=self._index(self._load(r),d)
                    if d<16:
                        for n in reversed(sorted(node['children'])):stack.append((node['children'][n],d+1,prefix+n))
                    else:
                        for e in node['entries']:
                            obj=self._load(e['event']);raw=self._event(obj);digest=hashlib.sha256(canonical(obj['key'])).hexdigest()
                            if digest!=e['keyHash'] or not digest.startswith(prefix):raise Corrupt('index key path')
                            batch.append((decode(canonical(obj['key'])),obj['kind'],raw))
                            if len(batch)==limit:yield batch;batch=[]
                if batch:yield batch
            except GeneratorExit:raise  # An abandoned read cursor is not an I/O failure.
            except BaseException:self.poisoned=True;raise
        return walk()

    def close(self):
        if self.lfd is not None:os.close(self.lfd);self.lfd=None
        if self.dfd is not None:os.close(self.dfd);self.dfd=None
        self.closed=True

    def __enter__(self):return self
    def __exit__(self,*args):self.close()

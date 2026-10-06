import hashlib
from pathlib import Path
def archive_payloads(path):
 # GNU ar allows duplicate basenames. Hash every ordered payload, not ar p's
 # first matching name. Ignore only the rebuilt symbol/long-name metadata.
 entries=[];longnames=b''
 with Path(path).open('rb') as stream:
  assert stream.read(8)==b'!<arch>\n','Expected regular GNU archive'
  while True:
   header=stream.read(60)
   if not header:break
   assert len(header)==60 and header[58:60]==b'`\n','Archive header'
   name=header[:16].decode('ascii').strip();size=int(header[48:58]);remaining=size
   if name=='//':longnames=stream.read(size);assert len(longnames)==size
   else:
    hasher=hashlib.sha256()
    while remaining:
     chunk=stream.read(min(remaining,1048576));assert chunk,'Truncated archive'
     hasher.update(chunk);remaining-=len(chunk)
    if name not in ('/','/SYM64/'):
     assert not name.startswith('#1/'),'Unsupported BSD member names'
     if name.startswith('/'):
      offset=int(name[1:]);end=longnames.index(b'/\n',offset);name=longnames[offset:end].decode('utf-8')
     else:name=name.removesuffix('/')
     entries.append({'name':name,'size':size,'sha256':hasher.hexdigest()})
   if size%2:assert len(stream.read(1))==1
 return entries


def replace_payload(source,destination,originalSHA,replacement):
 data=Path(source).read_bytes();assert data[:8]==b'!<arch>\n';output=bytearray(data[:8]);pos=8;matches=0
 while pos<len(data):
  header=data[pos:pos+60];assert len(header)==60 and header[58:60]==b'`\n';size=int(header[48:58]);payload=data[pos+60:pos+60+size];assert len(payload)==size
  if hashlib.sha256(payload).hexdigest()==originalSHA:
   matches+=1;payload=Path(replacement).read_bytes();header=header[:48]+str(len(payload)).encode().ljust(10,b' ')+header[58:]
  output+=header+payload
  if len(payload)%2:output+=b'\n'
  pos+=60+size+size%2
 assert matches==1 and pos==len(data);Path(destination).write_bytes(output)

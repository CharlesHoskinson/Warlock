import hashlib,os,stat
from xml.sax.saxutils import escape
XML_PREFIX='<busconfig><type>session</type><auth>EXTERNAL</auth>'
XML_SUFFIX='<policy context="default"><allow send_destination="*" eavesdrop="true"/><allow eavesdrop="true"/><allow own="*"/></policy><limit name="service_start_timeout">3000</limit></busconfig>\n'
def configuration(address):
 if not address.startswith('unix:path=') or not address[10:] or '\n' in address:raise ValueError('Private bus address only')
 return XML_PREFIX+'<listen>'+escape(address)+'</listen>'+XML_SUFFIX

def install(host):
 parent=host.ReviewedWestonHost
 class ControlledBoundsHost(parent):
  def launch(self,name,command,env=None):
   if name=='privateBus':
    expected=['/usr/bin/dbus-daemon','--session','--nofork','--address='+self.env['DBUS_SESSION_BUS_ADDRESS']]
    if list(command)!=expected:raise RuntimeError('Unreviewed private bus launch')
    st=self.runtime.lstat()
    if self.runtime.is_symlink() or st.st_uid!=os.getuid() or stat.S_IMODE(st.st_mode)!=0o700:raise RuntimeError('Private bus runtime ownership')
    path=self.runtime/'bounds-bus.conf';data=configuration(self.env['DBUS_SESSION_BUS_ADDRESS']).encode();fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(data)
    self.evidence['boundsBusPolicy']={'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'serviceActivation':False,'scope':'Controlled GUI bounds only; normal portal/AT integration qualification separate'}
    command=['/usr/bin/dbus-daemon','--nofork','--config-file='+str(path)]
   return super().launch(name,command,env)
 host.ReviewedWestonHost=ControlledBoundsHost

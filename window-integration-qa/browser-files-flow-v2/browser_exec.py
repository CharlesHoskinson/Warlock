"""Unshare child pre-exec validator. Invoked only by authorized native runner."""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,verify_runtime,check_private_directory,verify_parent
from network_guard import network_authority
B=Path(__file__).resolve().parent
BINARY=Path('/opt/brave-bin/brave')
def command(profile,page):
 return [str(BINARY),'--ozone-platform=wayland','--user-data-dir='+str(profile),'--remote-debugging-pipe','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--disable-default-apps','--disable-breakpad','--disable-dev-shm-usage','--disable-features=MediaRouter,OptimizationHints,AutofillServerCommunication,BraveNews,BraveRewards','--metrics-recording-only','--password-store=basic',page]
def remap_pipe(read_fd,write_fd):
 # Safe remapping even when original pipe happens to occupy fd3 or fd4.
 rd=fcntl.fcntl(read_fd,fcntl.F_DUPFD_CLOEXEC,10);wr=fcntl.fcntl(write_fd,fcntl.F_DUPFD_CLOEXEC,10)
 for fd in set((read_fd,write_fd)):
  os.close(fd)
 os.dup2(rd,3,inheritable=True);os.dup2(wr,4,inheritable=True);os.close(rd);os.close(wr)
def main():
 p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--profile',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--parent-netns',required=True);p.add_argument('--uid',type=int,required=True);p.add_argument('--read-fd',type=int,required=True);p.add_argument('--write-fd',type=int,required=True);p.add_argument('--binary-sha',required=True);p.add_argument('--compositor-pid',type=int,required=True);p.add_argument('--compositor-start',required=True);p.add_argument('--signature',required=True);args=p.parse_args()
 scope=require_qa_scope();runtime=verify_runtime(args.runtime);check_private_directory(args.profile)
 if os.environ['XDG_RUNTIME_DIR']!=str(runtime) or os.environ['HYPRLAND_INSTANCE_SIGNATURE']!=args.signature:raise RuntimeError('Exact captured compositor selectors required')
 peer=verify_parent(dict(os.environ))
 if not Path(peer['path']).resolve().is_relative_to(runtime.resolve()) or peer['pid']!=args.compositor_pid or Path(f'/proc/{peer["pid"]}/stat').read_text().rsplit(')',1)[1].split()[19]!=args.compositor_start:raise RuntimeError('Actual owned compositor peer/lifetime required')
 for key in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','TMPDIR'):
  if not Path(os.environ[key]).resolve().is_relative_to(runtime.resolve()):raise RuntimeError('Private browser environment required:'+key)
 if any(os.environ.get(k) for k in ('DISPLAY','WAYLAND_SOCKET','AT_SPI_BUS_ADDRESS','SESSION_MANAGER','XAUTHORITY')):raise RuntimeError('Inherited main selector refused')
 if not args.profile.resolve().is_relative_to(runtime.resolve()):raise RuntimeError('Profile escaped private runtime')
 if list(args.profile.iterdir()):raise RuntimeError('Browser requires fresh empty owned profile')
 page=(B/'compose.html').resolve();net=network_authority(args.parent_netns,args.uid)
 if hashlib.sha256(BINARY.read_bytes()).hexdigest()!=args.binary_sha:raise RuntimeError('Browser binary changed before exec')
 remap_pipe(args.read_fd,args.write_fd)
 argv=command(args.profile,page.as_uri())
 record={'pid':os.getpid(),'start':Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19],'scope':scope,'network':net,'waylandPeer':peer,'compositorStart':args.compositor_start,'signature':args.signature,'argv':argv,'binarySHA256':args.binary_sha,'profile':str(args.profile),'page':page.as_uri(),'sandboxEnabled':True,'cdpPipeDescriptors':[3,4]}
 with args.evidence.open('x') as handle:json.dump(record,handle,indent=2)
 args.evidence.chmod(0o600)
 os.execve(str(BINARY),argv,dict(os.environ))
if __name__=='__main__':main()

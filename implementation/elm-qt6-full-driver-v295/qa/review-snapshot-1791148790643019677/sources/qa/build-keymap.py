"""CPU actual read-only keymap helper build and owning GTK constants; no display."""
import hashlib,json,pathlib,resource,shlex,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('keymap-build-'+str(time.time_ns()));OUT.mkdir();(OUT/'inputs').mkdir()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'inputs':{},'artifacts':{},'libraries':{},'dependencies':{}}
try:
 for p in [pathlib.Path(__file__),*sorted((ROOT/'native').glob('*'))]:
  (OUT/'inputs'/p.name).write_bytes(p.read_bytes());report['inputs'][str(p)]=sha(p)
 flags=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','wayland-client','xkbcommon'],text=True))
 argv=['/usr/bin/cc','-std=c11','-Wall','-Wextra','-Werror','-MD','-MF',str(OUT/'keymap.d'),'-I',str(OUT/'inputs'),str(OUT/'inputs/keymap.c'),'-o',str(OUT/'keymap'),*flags]
 result=subprocess.run(argv,capture_output=True,timeout=60);(OUT/'compile.stdout').write_bytes(result.stdout);(OUT/'compile.stderr').write_bytes(result.stderr);report['argv']=argv;assert result.returncode==0,result.stderr.decode()
 source=OUT/'constants.c';source.write_text('#include <stdio.h>\n#include <gdk/gdk.h>\nint main(void){printf("{\\"button-press\\":%d,\\"button-release\\":%d,\\"key-press\\":%d,\\"key-release\\":%d,\\"shiftMask\\":%u}\\n",GDK_BUTTON_PRESS,GDK_BUTTON_RELEASE,GDK_KEY_PRESS,GDK_KEY_RELEASE,GDK_SHIFT_MASK);return 0;}\n')
 flags=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','gtk4'],text=True));argv=['/usr/bin/cc','-std=c11','-Wall','-Wextra','-Werror','-MD','-MF',str(OUT/'constants.d'),str(source),'-o',str(OUT/'constants'),*flags]
 result=subprocess.run(argv,capture_output=True,timeout=60);(OUT/'constants.stderr').write_bytes(result.stderr);assert result.returncode==0,result.stderr.decode();report['constants']=json.loads(subprocess.check_output([str(OUT/'constants')],timeout=3))
 for depfile in [OUT/'keymap.d',OUT/'constants.d']:
  text=depfile.read_text().replace('\\\n',' ').split(':',1)[1]
  for value in shlex.split(text):report['dependencies'][value]=sha(value)
 for binary in [OUT/'keymap',OUT/'constants']:
  report['artifacts'][str(binary)]=sha(binary);linked=subprocess.check_output(['/usr/bin/ldd',str(binary)],text=True);(OUT/(binary.name+'.ldd')).write_text(linked)
  for word in linked.split():
   if word.startswith('/') and pathlib.Path(word).is_file():report['libraries'][word]=sha(word)
 report['tools']={p:sha(p) for p in ['/usr/bin/cc','/usr/bin/pkg-config','/usr/bin/ldd','/usr/bin/python3']};report['passed']=True
except BaseException as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(OUT/'report.json'),'passed':report['passed'],'error':report.get('error')}))
if report['passed']:(ROOT/'keymap-build-report.json').write_text(json.dumps({'buildReport':str(OUT/'report.json'),'buildReportSHA256':sha(OUT/'report.json'),'binary':str(OUT/'keymap'),'binarySHA256':sha(OUT/'keymap'),'constants':report['constants'],'nativeAcceptance':False},indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)

"""Compile guard mutations of the actual host; no GUI or native input claims."""
import hashlib,json,resource,shlex,shutil,subprocess,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir()
source=(ROOT/'native/shared-context.h').read_text()
begin=source.index('static gboolean shared_native_escape_press(GtkWidget *widget) {')
end=source.index('static JsonNode *terminal_take',begin)
helper=source[begin:end]
controls=[
 ('requires-current-dom','    const ContextProof *proof=&context_proof;','    const ContextProof *proof=&context_proof;\n    if(!surface_popup_ready())return FALSE;'),
 ('reuses-consumed-press','!proof->available || proof->pointer','proof->pointer'),
 ('admits-early-release-as-new-press','proof->released ||\n       proof->key!=GDK_KEY_Escape || proof->source!=widget ||\n       !(held_context_keys&context_key_bit(GDK_KEY_Escape))','proof->key!=GDK_KEY_Escape || proof->source!=widget'),
 ('admits-wrong-key','proof->key!=GDK_KEY_Escape || proof->source!=widget','proof->source!=widget'),
 ('admits-application-popup','g_strcmp0(json_object_get_string_member(snapshot,"mode"),"menu")!=0','FALSE'),
 ('stamps-old-dom','g_strdup_printf("%" G_GUINT64_FORMAT,proof->publication)','g_strdup_printf("%" G_GUINT64_FORMAT,applied_publication)'),
 ('does-not-consume','    context_proof.available=FALSE;','    context_proof.available=TRUE;'),
 ('renews-deadline','    gboolean stored=terminal_store(message,proof);','    context_proof.captured=g_get_monotonic_time();\n    gboolean stored=terminal_store(message,proof);'),
 ('admits-old-snapshot','publication!=proof->publication','FALSE'),
 ('admits-old-lease','lease!=proof->lease','FALSE'),
]
report={'passed':False,'nativeAcceptance':False,'releaseAcceptance':False,'sourceSHA256':hashlib.sha256(source.encode()).hexdigest(),'controls':[]}
def run(name,cmd,cwd):
 p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 return p
try:
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],text=True))
 for name,old,new in [('baseline',None,None),*controls]:
  case=OUT/name;shutil.copytree(ROOT/'native',case)
  changed=helper
  if old is not None:assert helper.count(old)==1,(name,helper.count(old));changed=helper.replace(old,new)
  (case/'shared-context.h').write_text(source[:begin]+changed+source[end:])
  binary=case/'checks'
  build=run(name+'-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations',str(case/'shared-context-test.c'),'-o',str(binary),*flags],case)
  assert build.returncode==0,(name,build.stderr)
  test=run(name+'-test',[str(binary)],case)
  accepted=(test.returncode==0) if name=='baseline' else (test.returncode==1 and 'failed ' in test.stderr)
  report['controls'].append({'name':name,'buildExitCode':build.returncode,'testExitCode':test.returncode,'accepted':accepted,'binarySHA256':hashlib.sha256(binary.read_bytes()).hexdigest()})
  print(name,accepted,flush=True);assert accepted,(name,test.stdout,test.stderr)
 assert (ROOT/'native/shared-context.h').read_text()==source
 report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(OUT/'report.json');raise SystemExit(not report['passed'])

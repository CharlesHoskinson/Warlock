from pathlib import Path
import hashlib,json,difflib,shutil,subprocess,re
v1=Path(__file__).resolve().parent;v2=v1.parent/'maximized-stack-v2'
if v2.exists():raise ValueError('fresh v2 directory required')
v2.mkdir(mode=0o700);shutil.copytree(v1/'original',v2/'original')
source=v1/'candidate/src/render/Renderer.cpp';style=v1/'native-core-v2/.clang-format'
formatted=subprocess.check_output(['/usr/bin/clang-format','--style=file:'+str(style),'--lines=412:428',str(source)],text=True)
original=source.read_text()
if re.sub(r'\s+','',original)!=re.sub(r'\s+','',formatted):raise ValueError('format changed nonwhitespace')
path='src/render/Renderer.cpp';dest=v2/'candidate'/path;dest.parent.mkdir(parents=True);dest.write_text(formatted)
base=(v2/'original'/path).read_text();patch=''.join(difflib.unified_diff(base.splitlines(True),formatted.splitlines(True),fromfile='a/'+path,tofile='b/'+path));(v2/'floating-max-stack.patch').write_text(patch)
manifest=json.loads((v1/'source-manifest.json').read_text());manifest['candidate']['sha256']=hashlib.sha256(formatted.encode()).hexdigest();manifest['candidate']['changed_lines']=len([line for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++')]);manifest['previous_candidate']={'path':str(source),'sha256':hashlib.sha256(original.encode()).hexdigest()};manifest['formatting']={'clang_format':subprocess.check_output(['/usr/bin/clang-format','--version'],text=True).strip(),'style_file':str(style),'style_sha256':hashlib.sha256(style.read_bytes()).hexdigest(),'range':'412:428','logic_changed':False}
(v2/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');shutil.copy2(v1/'test_stack_policy.py',v2/'test_stack_policy.py')
(v2/'format-only-v1-to-v2.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),formatted.splitlines(True),fromfile='v1/'+path,tofile='v2/'+path)))
print(json.dumps({'renderer':str(dest),'sha256':manifest['candidate']['sha256']},indent=2))

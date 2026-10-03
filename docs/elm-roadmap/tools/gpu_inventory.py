"""Read-only driver/API inventory; not a browser WebGPU acceptance test."""
import datetime,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
results=[]
for cmd in [['lspci','-nnk'],['vulkaninfo','--summary'],['nvidia-smi','--query-gpu=name,driver_version','--format=csv,noheader'],['pacman','-Q','webkit2gtk-4.1','gtk-layer-shell','gtk4-layer-shell','mesa','vulkan-intel','nvidia-utils']]:
 try:
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
  output=p.stdout
  if cmd[0]=='lspci':
   lines=output.splitlines();selected=[]
   for i,line in enumerate(lines):
    if any(term in line for term in ['VGA compatible','3D controller','Display controller']):selected+=lines[i:i+5]
   output='\n'.join(selected)+'\n'
  results.append({'command':cmd,'exitCode':p.returncode,'stdout':output,'stderr':p.stderr})
 except (OSError,subprocess.TimeoutExpired) as e:results.append({'command':cmd,'error':str(e)})
report={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only physical GPU/driver and Vulkan API inventory; no webview, WebGPU adapter, capture interoperability or displayed-frame acceptance established','results':results}
(root/'gpu-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

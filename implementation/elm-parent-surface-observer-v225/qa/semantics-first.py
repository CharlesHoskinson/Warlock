import hashlib
import json
from pathlib import Path
import re
import sys
import time
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def function(source,name):
 match=re.search(r'static [^\n]+\b'+name+r'\([^\n]*\) \{',source);assert match,name
 start=match.start();cursor=match.end();depth=1
 while depth:
  if source[cursor]=='{':depth+=1
  if source[cursor]=='}':depth-=1
  cursor+=1
 return source[start:cursor]
def main():
 out=ROOT/'qa'/('semantics-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[],'inputs':{}}
 try:
  original=(ROOT/'original/parent-input-module.c').read_text();current=(ROOT/'native/parent-input-module.c').read_text()
  for name in ('release_all','resource_destroyed','motion_request','button_request','pointer_capability_request','pointer_burst_request','seat_destroyed','valid_point','focused_pid'):
   assert function(original,name)==function(current,name),name;report['checks'].append({'name':name+'-byte-identical','passed':True})
  original_xml=ET.parse(ROOT/'original/parent-input.xml').getroot();current_xml=ET.parse(ROOT/'native/parent-input.xml').getroot()
  assert ET.tostring(original_xml.find('interface'))==ET.tostring(current_xml.find('interface'));report['checks'].append({'name':'original-input-interface-opcodes-byte-identical','passed':True})
  for p in (ROOT/'original/parent-input-module.c',ROOT/'native/parent-input-module.c',ROOT/'original/parent-input.xml',ROOT/'native/parent-input.xml',Path(__file__)):report['inputs'][str(p)]=sha(p)
  report['passed']=True
 except Exception as error:report['error']=repr(error)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())

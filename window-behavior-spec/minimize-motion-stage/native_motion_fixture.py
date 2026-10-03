#!/usr/bin/env python3
"""Launch explicitly selected disposable native fixture, invoke observer, clean up.

Requires the root-coordinated GUI slot. Supports Qt, GTK, native modal family,
pin and maximize. No pointer/key injection; exact original windows/focus/cursor
and reduced-motion state must survive. Does not alter deployed code/config.
"""
import argparse,json,os,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;QA=Path.home()/'window-integration-qa'

def data(name):return json.loads(subprocess.check_output(['hyprctl',name,'-j'],text=True,timeout=4))
def dispatch(expression):subprocess.run(['hyprctl','dispatch',expression],check=True,stdout=subprocess.DEVNULL,timeout=4)
def wait(predicate,message,duration=8):
 end=time.monotonic()+duration
 while time.monotonic()<end:
  result=predicate()
  if result:return result
  time.sleep(.05)
 raise AssertionError(message)
def exact(w):return {k:w.get(k) for k in ('address','stableId','pid','at','size','workspace','pinned','fullscreen','fullscreenClient','fullscreenHandler')}

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--toolkit',choices=['foot','qt','gtk','family'],required=True)
 parser.add_argument('--output',type=Path,required=True)
 parser.add_argument('--pin',action='store_true');parser.add_argument('--maximize',action='store_true');parser.add_argument('--capture-frames',action='store_true');parser.add_argument('--reduced-motion-trial',action='store_true')
 args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 original=data('clients');focus=data('activewindow');cursor=data('cursorpos')
 processes=[];logs=[];report={'toolkit':args.toolkit,'pin':args.pin,'maximize':args.maximize,'mainOriginal':[exact(w) for w in original]}
 def launch(command):
  log=(args.output/('fixture-'+str(len(logs))+'.log')).open('w');logs.append(log)
  process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);processes.append(process);return process
 try:
  if args.toolkit=='qt':process=launch(['qs','-p',str(HERE/'native_fixtures/qt.qml')])
  elif args.toolkit=='gtk':process=launch(['python3',str(HERE/'native_fixtures/gtk.py')])
  elif args.toolkit=='family':
   control=args.output/'modal-command';control.write_text('')
   process=launch(['python3',str(QA/'modal_probe_gtk.py'),'family',str(control),str(args.output/'modal-events.jsonl')])
  else:process=launch(['foot','--app-id=motion-parity-qa','--title=Motion parity QA Foot','python3','-c','import time; print("Native foot motion fixture",flush=True); time.sleep(180)'])
  owner=wait(lambda:next((w for w in data('clients') if w['pid']==process.pid),None),'fixture map timeout')
  members=[owner]
  if args.toolkit=='family':
   control.write_text('open');child=wait(lambda:next((w for w in data('clients') if w['pid']==process.pid and w['title']=='Modal QA child'),None),'modal child map timeout')
   control.write_text('nested');nested=wait(lambda:next((w for w in data('clients') if w['pid']==process.pid and w['title']=='Modal QA nested'),None),'nested modal map timeout')
   members=[nested,child,owner]
  for index,member in enumerate(members):
   address=member['address']
   if not member['floating']:dispatch(f'hl.dsp.window.float({{action="set",window="address:{address}"}})')
   width,height=(620,380) if member['address']==owner['address'] else (360-index*20,220-index*20)
   dispatch(f'hl.dsp.window.resize({{x={width},y={height},window="address:{address}"}})')
   dispatch(f'hl.dsp.window.move({{x={320+index*55},y={350+index*35},window="address:{address}"}})')
  if args.pin:dispatch(f'hl.dsp.window.pin({{window="address:{owner["address"]}"}})')
  if args.maximize:dispatch(f'hl.dsp.window.fullscreen({{mode="maximized",action="set",window="address:{owner["address"]}"}})')
  dispatch(f'hl.dsp.focus({{window="address:{members[0]["address"]}"}})');time.sleep(1)
  current={w['address']:w for w in data('clients')};members=[current[w['address']] for w in members]
  if args.pin:assert all(w['pinned'] for w in members),'pin did not cover captured modal family'
  if args.maximize:assert current[owner['address']]['fullscreen']==1,'maximize dispatch did not apply'
  report['fixtureBefore']=[exact(w) for w in members]
  command=['python3',str(HERE/'native_motion_trial.py'),'--output',str(args.output)]
  for member in members:command.extend(['--window',member['address']])
  if args.capture_frames:command.append('--capture-frames')
  if args.reduced_motion_trial:command.append('--reduced-motion-trial')
  subprocess.run(command,check=True,timeout=100)
  current={w['address']:w for w in data('clients')};report['fixtureAfter']=[exact(current[w['address']]) for w in members]
  assert report['fixtureAfter']==report['fixtureBefore'],'fixture geometry/pin/desktop/maximize/identity changed'
  report['passed']=True
 except Exception as error:report['passed']=False;report['error']=repr(error);raise
 finally:
  for process in processes:
   process.terminate()
   try:process.wait(timeout=4)
   except subprocess.TimeoutExpired:process.kill();process.wait()
  for log in logs:log.close()
  current=data('clients')
  if any(w.get('stableId')==focus.get('stableId') and w.get('pid')==focus.get('pid') for w in current):dispatch(f'hl.dsp.focus({{window="address:{focus["address"]}"}})')
  dispatch(f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})');time.sleep(.1)
  current={w['address']:w for w in data('clients')}
  report['mainAfter']=[exact(current[w['address']]) for w in original if w['address'] in current]
  report['mainPreserved']=report['mainAfter']==report['mainOriginal']
  after_focus=data('activewindow');report['focusRestored']=not focus or [after_focus.get('stableId'),after_focus.get('pid')]==[focus.get('stableId'),focus.get('pid')]
  report['cursorRestored']=data('cursorpos')==cursor
  (args.output/'fixture-cleanup.json').write_text(json.dumps(report,indent=2))
  assert report['mainPreserved'] and report['focusRestored'] and report['cursorRestored'],'original desktop state was not restored'
 print('Disposable '+args.toolkit+' native motion fixture passed: '+str(args.output))

if __name__=='__main__':main()

"""Actual tuple consistency predicate, captured real build packets; no native effects."""
import copy,hashlib,json,pathlib,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));import tuple as policy

def main():
 out=ROOT/'qa'/('test-'+str(time.time_ns()));out.mkdir();checks=[];report={'passed':False,'nativeAcceptance':False}
 def yes(name,value):assert value,name;checks.append(name)
 def no(name,call):
  try:call()
  except policy.Refused:checks.append(name);return
  raise AssertionError(name)
 try:
  descriptor,packets,inventory,aq=policy.assemble();core,authority,observer=packets
  for name,value in zip(('core307','authority319','observer315'),packets):(out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
  yes('actual-three-build694header-match',policy.check_pair(*packets)==descriptor['owningHeaderTreeSHA256'])
  yes('actual319-core307-not-inherited-prose',authority['core']['path']==core['binary'] and 'Core205' in authority['scope'])
  def changed(index,path,value):
   rows=copy.deepcopy(packets);target=rows[index]
   for key in path[:-1]:target=target[key]
   target[path[-1]]=value;return rows
  for index,path,value,name in [(0,['passed'],1,'boolbuild'),(1,['passed'],False,'failedauthority'),(2,['core','path'],'/usr/bin/Hyprland','installedcore'),(1,['core','sha256'],'0'*64,'wrongcoreSHA'),(2,['missingSymbols'],['missing'],'missingstrong'),(1,['strongUndefinedCount'],True,'boolstrong'),(2,['strongUndefinedCount'],0,'emptystrong'),(0,['owningVersionHeaderSHA256'],'0'*64,'wrongversion'),(2,['owningHeaders','src/version.h'],'0'*64,'headerdivergence'),(0,['unchangedArchiveMembers'],413,'lostancestorobjects')]:
   no(name,lambda rows=changed(index,path,value):policy.check_pair(*rows))
  rows=copy.deepcopy(packets);rows[0]['owningHeaders'].pop('src/version.h');no('missing694header',lambda:policy.check_pair(*rows))
  rows=copy.deepcopy(packets);rows[0]['rebuiltArchiveMembers'].pop(next(iter(rows[0]['rebuiltArchiveMembers'])));no('missing19consumer',lambda:policy.check_pair(*rows))
  yes('AQ155-originalprotectedtuple',aq['librarySHA256']=='bfb0383901822a92f2fe945b4b80048f89cc4ffeeb6e9bb8ab748d57317928cb')
  yes('exactold205-not-selected',descriptor['sha256']!='bda6ce0094961c285673589afa2b61fe2b97321a1d86b248823b482122fec0f5')
  report.update(passed=True,checks=checks,sourceSHA256=policy.sha(ROOT/'qa/tuple.py'),descriptor=descriptor,verifiedFiles=len(inventory))
 except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc(),checks=checks)
 (out/'test.py').write_bytes(pathlib.Path(__file__).read_bytes());(out/'tuple.py').write_bytes((ROOT/'qa/tuple.py').read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(checks),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())

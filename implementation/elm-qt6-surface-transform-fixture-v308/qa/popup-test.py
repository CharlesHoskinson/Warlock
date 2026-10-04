"""Actual popup class/functions with instrumented Qt interfaces; no GUI."""
import hashlib,importlib.util,json,re,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];source=(ROOT/'native/qt-role-client.cpp').read_text();out=ROOT/'qa'/('popup-'+str(time.time_ns()));out.mkdir()
spec=importlib.util.spec_from_file_location('extractor',ROOT/'qa/lifetime-test.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
functions={name:m.extract(source,name) for name in ['currentRole','currentPopupAction','popupTriggered']};popup=re.search(r'class PopupLandmarkMenu final:.*?\};',source).group(0)
prefix=r'''
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <string>
#include <vector>
using quint64=std::uint64_t;
struct QPaintEvent{};struct QWidget{int width()const{return 100;}int height()const{return 40;}};
struct QAction{bool enabled=true,visible=true;bool isEnabled()const{return enabled;}bool isVisible()const{return visible;}};
struct ActionList{std::vector<QAction*>items;bool contains(QAction*a)const{return std::find(items.begin(),items.end(),a)!=items.end();}};
static int basePaints,markers,emitted;
struct QMenu:QWidget{ActionList list;explicit QMenu(QWidget*){} virtual void paintEvent(QPaintEvent*){basePaints++;}ActionList actions()const{return list;}};
struct QRect{int x,y,w,h;QRect(int a,int b,int c,int d):x(a),y(b),w(c),h(d){}};
namespace Qt{enum Color{magenta,yellow};}
struct QPainter{explicit QPainter(QWidget*){}void fillRect(QRect r,Qt::Color color){assert(basePaints>markers);assert(color==Qt::magenta&&r.x==4&&r.y==4&&r.w==8&&r.h==8);markers++;}};
struct Role{QWidget*widget=nullptr;quint64 instance=0;QAction*popupAction=nullptr;};static Role roles[5];
struct Record{int&operator[](const char*){static int cell;return cell;}};
static Record record(const char*name,const Role*r){assert(r->widget);assert(std::string(name)=="draw-queued"||std::string(name)=="popup-action-triggered");return {};}
static void emitRecord(Record){emitted++;}
#define protected public
'''
body=r'''
int main(){QWidget owner;PopupLandmarkMenu menu(&owner,1),stale(&owner,1);QAction action,other;menu.list.items={&action,&other};roles[4]={&menu,1,&action};QPaintEvent event;
menu.paintEvent(&event);assert(basePaints==1&&markers==1&&emitted==1);
stale.paintEvent(&event);assert(basePaints==1&&markers==1&&emitted==1);
roles[4].instance=2;menu.paintEvent(&event);popupTriggered(1,&menu,&action);assert(emitted==1&&basePaints==1);roles[4].instance=1;
popupTriggered(1,&menu,&other);assert(emitted==1);popupTriggered(1,&stale,&action);assert(emitted==1);
action.enabled=false;popupTriggered(1,&menu,&action);assert(emitted==1);action.enabled=true;action.visible=false;popupTriggered(1,&menu,&action);assert(emitted==1);action.visible=true;
menu.list.items={&other};popupTriggered(1,&menu,&action);assert(emitted==1);menu.list.items={&action,&other};
popupTriggered(1,&menu,&action);assert(emitted==2);
roles[4].popupAction=nullptr;popupTriggered(1,&menu,&action);assert(emitted==2);
roles[4].widget=nullptr;menu.paintEvent(&event);popupTriggered(1,&menu,&action);assert(emitted==2&&markers==1&&basePaints==1);
return 0;}
'''
report={'passed':False,'nativeAcceptance':False,'checks':body.count('assert('),'scope':'actual production popup paint/admission callbacks; explicit Qt mocks, no pixel/input proof','sourceSHA256':hashlib.sha256(source.encode()).hexdigest(),'controls':[]}
try:
 def run(name,funcs,cls):
  d=out/name;d.mkdir();(d/'test.cpp').write_text(prefix+'\n'.join(funcs.values())+cls+body)
  p=subprocess.run(['/usr/bin/c++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(d/'test.cpp'),'-o',str(d/'test')],capture_output=True,timeout=20);(d/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
  p=subprocess.run([str(d/'test')],capture_output=True,timeout=3);(d/'execute.stderr').write_bytes(p.stderr);return p.returncode
 assert run('production',functions,popup)==0
 for name,target,before,after in [('missing-instance','currentRole','roles[index].instance==instance&&',''),('foreign-action','currentPopupAction','roles[4].popupAction==action&&',''),('stale-paint','class','if(!currentRole(4,instance,this))return;','')]:
  changed=dict(functions);cls=popup
  if target=='class':assert before in cls;cls=cls.replace(before,after,1)
  else:assert before in changed[target];changed[target]=changed[target].replace(before,after,1)
  code=run(name,changed,cls);assert code!=0;report['controls'].append({'name':name,'behaviorallyRejected':True,'exitCode':code})
 report['passed']=True
finally:
 (out/'qt-role-client.cpp').write_text(source);(out/'popup-test.py').write_bytes(Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')

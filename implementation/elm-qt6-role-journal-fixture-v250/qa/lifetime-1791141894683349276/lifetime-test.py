#!/usr/bin/python3
import hashlib,json,pathlib,re,subprocess,time,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(source,name):
 m=re.search(r'static [^\n{]*\b'+name+r'\([^\n]*?\)\{',source);assert m,name;end=m.end();depth=1
 while depth:
  if source[end]=='{':depth+=1
  if source[end]=='}':depth-=1
  end+=1
 return source[m.start():end]
def main():
 out=ROOT/'qa'/f'lifetime-{time.time_ns()}';out.mkdir();source=(ROOT/'native/qt-role-client.cpp').read_text();shutil.copyfile(ROOT/'native/qt-role-client.cpp',out/'qt-role-client.cpp');shutil.copyfile(__file__,out/'lifetime-test.py')
 functions={name:extract(source,name) for name in ['currentRole','exitIfRetired','retire','retireFamily']}
 prefix=r'''
#include <QCoreApplication>
#include <QEvent>
#include <QObject>
#include <QPointer>
#include <QJsonObject>
#include <QString>
#include <vector>
#include <cassert>
class QWindow:public QObject{};
class QWidget:public QObject{public:explicit QWidget(QObject*parent=nullptr):QObject(parent){} QWindow*windowHandle(){return nullptr;}};
class QLineEdit:public QObject{};
'''+re.search(r'struct Role \{.*?\};',source).group(0)+r'''
static Role roles[5];static int exitCode,retiring,exitCalls;static bool stopping,exitEmitted;static std::vector<QJsonObject>journal;
class QApplication{public:static void exit(int code){assert(code==0);exitCalls++;}};
static quint32 resource(QWindow*){return 0;}
static QJsonObject record(const char*event,const Role*r=nullptr){QJsonObject o{{"event",event}};if(r)o["instance"]=qint64(r->instance);return o;}
static void emitRecord(QJsonObject o){journal.push_back(o);}
'''
 body=r'''
int main(int argc,char**argv){QCoreApplication app(argc,argv);auto*a=new QWidget;roles[0].widget=a;roles[0].instance=1;roles[0].name='A';roles[0].generation=1;
assert(currentRole(0,1,a));assert(!currentRole(-1,1,a));assert(!currentRole(5,1,a));assert(!currentRole(0,0,a));assert(!currentRole(0,2,a));assert(!currentRole(0,1,nullptr));
QPointer<QWidget>old=a;retire(roles[0]);assert(!roles[0].widget&&retiring==1);assert(!currentRole(0,1,a));auto*replacement=new QWidget;roles[0].widget=replacement;roles[0].instance=2;assert(currentRole(0,2,replacement));assert(!currentRole(0,1,replacement));assert(!currentRole(0,1,a));
QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);assert(old.isNull()&&retiring==0&&exitCalls==0);assert(roles[0].widget==replacement);assert(journal.back()["event"]=="local-destroy"&&journal.back()["instance"].toInteger()==1);
roles[1].widget=new QWidget(replacement);roles[1].name='B';roles[1].instance=3;roles[3].widget=new QWidget(roles[1].widget);roles[3].name='D';roles[3].instance=4;roles[4].widget=new QWidget(replacement);roles[4].name='P';roles[4].instance=5;roles[2].widget=new QWidget;roles[2].name='C';roles[2].instance=6;
retireFamily(0);assert(!roles[0].widget&&!roles[1].widget&&!roles[3].widget&&!roles[4].widget&&roles[2].widget);assert(retiring==4);QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);assert(retiring==0&&exitCalls==0&&roles[2].widget);auto count=journal.size();retire(roles[0]);assert(journal.size()==count);
stopping=true;retire(roles[2]);assert(retiring==1&&exitCalls==0);QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);assert(retiring==0&&exitCalls==1&&exitEmitted);exitIfRetired();assert(exitCalls==1);assert(journal.back()["event"]=="normalexit");return 0;}
'''
 report={'passed':False,'nativeAcceptance':False,'scope':'actual extracted lifetime functions with real QtCore QObject/QPointer/deferred-delete; QWidget/QWindow and journal are explicit mocks, no GUI','sourceSHA256':sha(ROOT/'native/qt-role-client.cpp')}
 try:
  flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core'],text=True).split()
  def run(directory,funcs):
   src=directory/'test.cpp';src.write_text(prefix+'\n'.join(funcs.values())+body);p=subprocess.run(['/usr/bin/c++','-std=c++20','-fPIC','-O2','-Wall','-Wextra','-Werror',str(src),*flags,'-o',str(directory/'test')],capture_output=True);(directory/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
   p=subprocess.run([str(directory/'test')],capture_output=True,timeout=3);(directory/'stderr').write_bytes(p.stderr);return p.returncode
  assert run(out,functions)==0;controls=[]
  for name,target,before,after in [('missing-lifetime','currentRole','roles[index].instance==instance&&',''),('premature-local-exit','exitIfRetired','stopping&&!retiring&&!exitEmitted','stopping&&!exitEmitted'),('wrong-destroy-identity','retire','o["instance"]=qint64(instance);','o["instance"]=qint64(instance+1);')]:
   d=dict(functions);assert before in d[target];d[target]=d[target].replace(before,after);directory=out/name;directory.mkdir();code=run(directory,d);assert code!=0,name;controls.append({'name':name,'behaviorallyRejected':True,'exit':code})
  report.update(passed=True,assertions=body.count('assert('),controls=controls,extracted={name:hashlib.sha256(text.encode()).hexdigest() for name,text in functions.items()})
 except Exception as e:report['error']=str(e)[-1600:]
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())


#include <QCoreApplication>
#include <QEvent>
#include <QObject>
#include <QPointer>
#include <QJsonObject>
#include <QString>
#include <vector>
#include <cassert>
class QWindow:public QObject{};
class QWidget:public QObject{public:explicit QWidget(QObject*parent=nullptr):QObject(parent){} QWindow*windowHandle(){return nullptr;} QWidget*parentWidget(){return static_cast<QWidget*>(parent());}};
class QLineEdit:public QObject{};
struct Role {char name=0;quint64 instance=0,generation=0;QPointer<QWidget> widget,landmark;QPointer<QLineEdit> entry;QPointer<QWindow> window;QMetaObject::Connection stateConnection;};
static Role roles[5];static int exitCode,retiring,exitCalls;static bool stopping,exitEmitted;static std::vector<QJsonObject>journal;
class QApplication{public:static void exit(int code){assert(code==0);exitCalls++;}};
static quint32 resource(QWindow*){return 0;}
static QJsonObject record(const char*event,const Role*r=nullptr){QJsonObject o{{"event",event}};if(r)o["instance"]=qint64(r->instance);return o;}
static void emitRecord(QJsonObject o){journal.push_back(o);}
static bool currentRole(int index,quint64 instance,const QWidget*widget){return index>=0&&index<5&&instance!=0&&roles[index].widget&&roles[index].instance==instance&&roles[index].widget==widget;}
static void exitIfRetired(){if(stopping&&!exitEmitted){exitEmitted=true;emitRecord(record(exitCode?"failed-exit":"normalexit"));QApplication::exit(exitCode);}}
static void retire(Role&r){if(!r.widget)return;emitRecord(record("destroy-request",&r));QWidget*widget=r.widget;auto instance=r.instance;auto generation=r.generation;auto surfaceId=resource(r.widget->windowHandle());char name=r.name;QObject::disconnect(r.stateConnection);r.stateConnection={};r.widget=nullptr;r.window=nullptr;r.entry=nullptr;r.landmark=nullptr;retiring++;QObject::connect(widget,&QObject::destroyed,qApp,[instance,name,generation,surfaceId]{auto o=record("local-destroy");o["role"]=QString(QChar(name));o["instance"]=qint64(instance);o["mapGeneration"]=qint64(generation);o["surfaceId"]=qint64(surfaceId);emitRecord(o);retiring--;exitIfRetired();});widget->deleteLater();}
static void retireFamily(int index){if(index<0||index>=5||!roles[index].widget)return;auto*owner=roles[index].widget.data();if(index==0||index==2){if(roles[4].widget&&roles[4].widget->parentWidget()==owner)retire(roles[4]);if(roles[1].widget&&roles[1].widget->parentWidget()==owner){retire(roles[3]);retire(roles[1]);}}else if(index==1)retire(roles[3]);retire(roles[index]);}
int main(int argc,char**argv){QCoreApplication app(argc,argv);auto*a=new QWidget;roles[0].widget=a;roles[0].instance=1;roles[0].name='A';roles[0].generation=1;
assert(currentRole(0,1,a));assert(!currentRole(-1,1,a));assert(!currentRole(5,1,a));assert(!currentRole(0,0,a));assert(!currentRole(0,2,a));assert(!currentRole(0,1,nullptr));
QPointer<QWidget>old=a;retire(roles[0]);assert(!roles[0].widget&&retiring==1);assert(!currentRole(0,1,a));auto*replacement=new QWidget;roles[0].widget=replacement;roles[0].instance=2;assert(currentRole(0,2,replacement));assert(!currentRole(0,1,replacement));assert(!currentRole(0,1,a));
QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);assert(old.isNull()&&retiring==0&&exitCalls==0);assert(roles[0].widget==replacement);assert(journal.back()["event"]=="local-destroy"&&journal.back()["instance"].toInteger()==1);
roles[1].widget=new QWidget(replacement);roles[1].name='B';roles[1].instance=3;roles[3].widget=new QWidget(roles[1].widget);roles[3].name='D';roles[3].instance=4;roles[4].widget=new QWidget(replacement);roles[4].name='P';roles[4].instance=5;roles[2].widget=new QWidget;roles[2].name='C';roles[2].instance=6;
retireFamily(0);assert(!roles[0].widget&&!roles[1].widget&&!roles[3].widget&&!roles[4].widget&&roles[2].widget);assert(retiring==4);QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);assert(retiring==0&&exitCalls==0&&roles[2].widget);auto count=journal.size();retire(roles[0]);assert(journal.size()==count);
auto*newA=new QWidget;roles[0].widget=newA;roles[0].instance=7;roles[0].name='A';roles[1].widget=new QWidget(roles[2].widget);roles[1].instance=8;roles[3].widget=new QWidget(roles[1].widget);roles[3].instance=9;
retireFamily(0);assert(!roles[0].widget&&roles[1].widget&&roles[3].widget&&roles[2].widget);QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);assert(retiring==0);retireFamily(2);assert(!roles[1].widget&&!roles[3].widget&&!roles[2].widget&&retiring==3);QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);assert(retiring==0);roles[2].widget=new QWidget;roles[2].instance=10;
stopping=true;retire(roles[2]);exitIfRetired();assert(retiring==1&&exitCalls==0);QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);assert(retiring==0&&exitCalls==1&&exitEmitted);exitIfRetired();assert(exitCalls==1);assert(journal.back()["event"]=="normalexit");return 0;}

#include "Lifetime.hpp"
#include "ReloadRelay.hpp"
#include <QCoreApplication>
#include <QMetaMethod>
#include <QMetaProperty>
#include <qqml.h>
#include <QQuickWindow>
#include <set>

namespace Lifetime {
namespace {std::atomic_bool processRefused{false};}
void requireOwnerThread(){
 auto*app=QCoreApplication::instance();
 if(!app||QThread::currentThread()!=app->thread()){processRefused.store(true);throw Refused("Actual owning Qt thread required before cache access");}
 if(processRefused.load())throw Refused("Process owning-thread authority retired");
}
QVariantMap WidgetToken::value()const{
 return {{"engineGeneration",qulonglong(engine.generation)},{"engineEpoch",qulonglong(engine.epoch)},{"providerGeneration",qulonglong(engine.provider)},
 {"widgetGeneration",qulonglong(widget)},{"delegateGeneration",qulonglong(delegate)},{"widgetContextGeneration",qulonglong(widgetContext)},{"delegateContextGeneration",qulonglong(delegateContext)},{"windowGeneration",qulonglong(window)},
 {"visualDescendant",visualDescendant},{"windowBound",windowBound}};
}
Registry::Registry(){
 auto*app=QCoreApplication::instance();if(!app)throw Refused("Actual QCoreApplication required");
 owner=app->thread();if(QThread::currentThread()!=owner)throw Refused("Actual owning Qt thread required");
 application=app;context=new QObject;
 QObject::connect(app,&QObject::destroyed,context,[this]{refused.store(true);},Qt::DirectConnection);
}
Registry::~Registry(){delete context;}
uint64_t checkedNext(uint64_t&counter){if(counter==0||counter>=SAFE_MAX)throw Refused("Exact counter representability exhausted");return counter++;}
void checkedCapacity(size_t current,size_t limit){if(current>=limit)throw Refused("Live registry capacity exhausted");}
Registry& Registry::shared(){requireOwnerThread();static Registry*value=new Registry;return *value;}
void Registry::thread(){
 if(QThread::currentThread()!=owner){refused.store(true);throw Refused("Wrong owning Qt thread");}
 if(refused.load()||application.isNull())throw Refused("Retired process registry");
}
uint64_t Registry::allocate(uint64_t&counter){
 thread();try{return checkedNext(counter);}catch(...){refused.store(true);throw;}
}
void Registry::retireObject(QObject*address,uint64_t generation){
 if(QThread::currentThread()!=owner){refused.store(true);return;}
 auto it=objects.find(address);if(it!=objects.end()&&it->second.generation==generation)objects.erase(it);
}
void Registry::retireEngine(QQmlEngine*address,uint64_t generation){
 if(QThread::currentThread()!=owner){refused.store(true);return;}
 auto it=engines.find(address);if(it==engines.end()||it->second.generation!=generation)return;
 QObject::disconnect(it->second.completed);QObject::disconnect(it->second.failed);QObject::disconnect(it->second.coreDestroyed);delete it->second.relay;engines.erase(it);
}
void Registry::retireProvider(QQmlEngine*address,uint64_t generation){
 if(QThread::currentThread()!=owner){refused.store(true);return;}
 auto it=engines.find(address);if(it!=engines.end()&&it->second.providerGen==generation)it->second.provider.clear();
}
void Registry::retireCore(QQmlEngine*address,uint64_t generation){
 if(QThread::currentThread()!=owner){refused.store(true);return;}
 auto it=engines.find(address);if(it==engines.end()||it->second.coreGen!=generation)return;
 QObject::disconnect(it->second.completed);QObject::disconnect(it->second.failed);QObject::disconnect(it->second.coreDestroyed);
 delete it->second.relay;it->second.relay=nullptr;it->second.core.clear();try{it->second.epoch=allocate(nextEpoch);}catch(...){refused.store(true);}
}
void Registry::coreBoundary(QQmlEngine*address,uint64_t generation){
 if(QThread::currentThread()!=owner){refused.store(true);return;}
 auto it=engines.find(address);if(it==engines.end()||it->second.coreGen!=generation||it->second.core.isNull())return;
 try{it->second.epoch=allocate(nextEpoch);}catch(...){refused.store(true);}
}
Registry::Engine& Registry::engine(QQmlEngine*e){
 thread();if(!e||e->thread()!=owner)throw Refused("Actual engine/thread required");
 auto found=engines.find(e);if(found!=engines.end()&&found->second.weak.data()==e)return found->second;
 if(engines.size()>=4096){refused.store(true);throw Refused("Live engine capacity exhausted");}
 Engine value;value.weak=e;value.generation=allocate(nextEngine);value.epoch=allocate(nextEpoch);
 auto[it,inserted]=engines.emplace(e,value);if(!inserted)throw Refused("Engine slot was not retired");
 const auto generation=value.generation;QPointer<QQmlEngine>guard=e;QObject::connect(e,&QObject::destroyed,context,[this,e,generation]{retireEngine(e,generation);},Qt::DirectConnection);
 if(guard.isNull())throw Refused("Engine retired during registration");
 auto current=engines.find(e);if(current==engines.end()||current->second.generation!=generation)throw Refused("Engine registration replaced");return current->second;
}
uint64_t Registry::object(QObject*o){
 thread();if(!o||o->thread()!=owner)throw Refused("Actual object/thread required");
 auto it=objects.find(o);if(it!=objects.end()&&it->second.weak.data()==o){if(it->second.faulted)throw Refused("Observed object scope fault");return it->second.generation;}
 if(objects.size()>=CAPACITY){refused.store(true);throw Refused("Live object capacity exhausted");}
 if(it!=objects.end())throw Refused("Object slot not retired");
 QPointer<QObject>guard=o;const auto generation=allocate(nextObject);objects.emplace(o,Object{QPointer<QObject>(o),generation,false});
 QObject::connect(o,&QObject::destroyed,context,[this,o,generation]{retireObject(o,generation);},Qt::DirectConnection);
 auto current=objects.find(o);if(guard.isNull()||current==objects.end()||current->second.generation!=generation)throw Refused("Object retired during registration");return generation;
}
EngineToken Registry::registerProvider(QQmlEngine*e,QObject*p){
 const auto eg=engine(e).generation;QPointer<QQmlEngine>guard=e;QPointer<QObject>provider=p;
 const auto generation=object(p);
 auto it=engines.find(e);if(guard.isNull()||provider.isNull()||it==engines.end()||it->second.generation!=eg)throw Refused("Provider registration engine changed");
 if(it->second.provider.data()!=p){
  if(it->second.providerGen)it->second.epoch=allocate(nextEpoch);
  it->second.provider=p;it->second.providerGen=generation;
  QObject::connect(p,&QObject::destroyed,context,[this,e,generation]{retireProvider(e,generation);},Qt::DirectConnection);
 }
 if(guard.isNull()||provider.isNull())throw Refused("Provider retired during registration");
 return scope(e,p);
}
EngineToken Registry::scope(QQmlEngine*e,QObject*p){
 thread();auto it=engines.find(e);if(it==engines.end()||it->second.weak.data()!=e||it->second.provider.data()!=p||!p||p->thread()!=owner)throw Refused("Retired actual engine/provider");
 if(object(p)!=it->second.providerGen)throw Refused("Actual provider generation changed");
 return {it->second.generation,it->second.epoch,it->second.providerGen};
}
void Registry::bindCore(QQmlEngine*e,QObject*p,QObject*supplied){
 verifyQuickshellProcess();const auto before=scope(e,p);QPointer<QQmlEngine>guard=e;QPointer<QObject>provider=p,core=supplied;
 if(!supplied||supplied->thread()!=owner)throw Refused("Actual existing Quickshell singleton required");
 // App evaluates its existing singleton first. Query the genuine engine's type,
 // never accept a QML-created lookalike or caller-supplied success header.
 auto*actual=e->singletonInstance<QObject*>("Quickshell","Quickshell");
 if(guard.isNull()||provider.isNull()||core.isNull()||actual!=supplied||scope(e,p)!=before||QByteArray(actual->metaObject()->className())!="QuickshellGlobal")throw Refused("Actual Quickshell singleton/source differs");
 const auto property=actual->metaObject()->indexOfProperty("processId");const auto completed=actual->metaObject()->indexOfSignal("reloadCompleted()");const auto failed=actual->metaObject()->indexOfSignal("reloadFailed(QString)");
 if(property<0||completed<0||failed<0)throw Refused("Actual reload signal ABI unavailable");
 const auto pidProperty=actual->metaObject()->property(property);const auto pid=pidProperty.read(actual);
 if(!pidProperty.isConstant()||!pidProperty.isReadable()||pid.metaType().id()!=QMetaType::Int||pid.toInt()!=QCoreApplication::applicationPid())throw Refused("Actual Quickshell process identity differs");
 if(guard.isNull()||provider.isNull()||core.isNull()||scope(e,p)!=before)throw Refused("Quickshell lookup lifetime changed");
 auto&row=engine(e);const auto generation=object(actual);
 if(row.core.data()==actual&&row.coreGen==generation)return;
 if(row.coreGen){retireCore(e,row.coreGen);}
 row.core=actual;row.coreGen=generation;
 row.relay=new ReloadRelay(context,[this,e,generation]{coreBoundary(e,generation);});
 row.completed=QObject::connect(actual,actual->metaObject()->method(completed),row.relay,row.relay->metaObject()->method(row.relay->metaObject()->indexOfSlot("completed()")),Qt::DirectConnection);
 row.failed=QObject::connect(actual,actual->metaObject()->method(failed),row.relay,row.relay->metaObject()->method(row.relay->metaObject()->indexOfSlot("failed(QString)")),Qt::DirectConnection);
 if(!row.completed||!row.failed){retireCore(e,generation);throw Refused("Actual reload signal connections failed");}
 row.coreDestroyed=QObject::connect(actual,&QObject::destroyed,context,[this,e,generation]{retireCore(e,generation);},Qt::DirectConnection);
}
void Registry::faultObject(QObject*o){auto it=objects.find(o);if(it!=objects.end())it->second.faulted=true;}
WidgetToken Registry::sample(QQmlEngine*e,QObject*p,QQuickItem*w,QQuickItem*d){
 const auto token=scope(e,p);QPointer<QQmlEngine>eg=e;QPointer<QObject>pg=p;QPointer<QQuickItem>wg=w,dg=d;
 if(!w||!d||w==d||w->thread()!=owner||d->thread()!=owner)throw Refused("Actual distinct owning-thread items required");
 auto*wc=QQmlEngine::contextForObject(w);auto*dc=QQmlEngine::contextForObject(d);QPointer<QQmlContext>wcg=wc,dcg=dc;
 const auto wid=object(w);if(wg.isNull()||dg.isNull()||eg.isNull()||pg.isNull()||wcg.isNull()||dcg.isNull())throw Refused("Selected item retired while binding");
 const auto did=object(d);if(wg.isNull()||dg.isNull()||eg.isNull()||pg.isNull()||wcg.isNull()||dcg.isNull())throw Refused("Selected item retired while binding");
 if(!wc||!dc||!wc->isValid()||!dc->isValid()||wc->engine()!=e||dc->engine()!=e||qmlEngine(w)!=e||qmlEngine(d)!=e){faultObject(w);faultObject(d);throw Refused("Actual current item contexts differ");}
 const auto wcID=object(wc);if(wcg.isNull()||dcg.isNull()||wg.isNull()||dg.isNull()||eg.isNull()||pg.isNull())throw Refused("Context retired while binding");
 const auto dcID=object(dc);if(wcg.isNull()||dcg.isNull()||wg.isNull()||dg.isNull()||eg.isNull()||pg.isNull())throw Refused("Context retired while binding");
 std::set<QQuickItem*>seen;bool descendant=false;
 for(auto*item=d->parentItem();item;item=item->parentItem()){
  if(!seen.insert(item).second||seen.size()>4096)throw Refused("Actual item ancestry is cyclic/unbounded");
  if(item==w){descendant=true;break;}
 }
 if(!descendant){faultObject(d);throw Refused("Actual delegate is not a widget descendant");}
 auto*window=w->window();QPointer<QQuickWindow>windowGuard=window;
 if(d->window()!=window)throw Refused("Actual selected window allocation differs");
 uint64_t winID=window?object(window):0;
 if(eg.isNull()||pg.isNull()||wg.isNull()||dg.isNull()||wcg.isNull()||dcg.isNull()||scope(e,p)!=token||QQmlEngine::contextForObject(w)!=wc||QQmlEngine::contextForObject(d)!=dc||object(w)!=wid||object(d)!=did||w->window()!=window||d->window()!=window||(window&&windowGuard.isNull()))throw Refused("Sampled Qt lifetime changed");
 return {token,wid,did,wcID,dcID,winID,true,bool(window)};
}
bool Registry::current(QQmlEngine*e,QObject*p,QQuickItem*w,QQuickItem*d,const WidgetToken&t){try{return sample(e,p,w,d)==t;}catch(...){return false;}}
}

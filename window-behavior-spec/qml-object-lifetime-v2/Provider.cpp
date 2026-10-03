#include "Provider.hpp"
#include <QCoreApplication>
#include <QQmlExtensionPlugin>
#include <qqml.h>
#include <mutex>

Lifetime::Authority ObjectLifetimeProvider::source(){
 Lifetime::requireOwnerThread();
 if(thread()!=QThread::currentThread())throw Lifetime::Refused("Actual provider owning thread differs");
 if(engine.isNull())throw Lifetime::Refused("Actual factory engine retired");
 QPointer<QQmlEngine>guard=engine;QPointer<QObject>self=this;
 auto*current=engine->singletonInstance<QObject*>("WindowObjectLifetimeV1","Lifetime");
 if(guard.isNull()||self.isNull()||current!=this)throw Lifetime::Refused("Retired actual singleton activation");
 try{auto a=Lifetime::authority();Lifetime::Registry::shared().registerProvider(engine.data(),this);return a;}
 catch(...){try{Lifetime::Registry::shared().refuse();}catch(...){}throw;}
}
void ObjectLifetimeProvider::stable(const Lifetime::Authority&a){try{a.verify();}catch(...){Lifetime::Registry::shared().refuse();throw;}}
QVariantMap ObjectLifetimeProvider::engineScope(){
 try{
  const auto a=source();const auto before=Lifetime::Registry::shared().scope(engine.data(),this);stable(a);
  if(engine.isNull()||Lifetime::Registry::shared().scope(engine.data(),this)!=before)throw Lifetime::Refused("Actual engine/provider changed");
  return {{"schema","qml-engine-metadata-v1"},{"kind","metadata-only; no widget/input authority"},{"engineGeneration",qulonglong(before.generation)},{"engineEpoch",qulonglong(before.epoch)},{"providerGeneration",qulonglong(before.provider)},{"processId",a.pid},{"processStart",a.start},{"configSHA256",QString::fromLatin1(a.configSHA)}};
 }catch(const std::exception&e){return {{"schema","qml-engine-metadata-v1"},{"error",QString::fromUtf8(e.what())}};}
}
QVariantMap ObjectLifetimeProvider::observe(QQuickItem*w,QQuickItem*d,QObject*actualQuickshell){
 try{
  const auto a=source();try{Lifetime::verifyQuickshellProcess();}catch(...){Lifetime::Registry::shared().refuse();throw;}
  Lifetime::Registry::shared().bindCore(engine.data(),this,actualQuickshell);
  const auto first=Lifetime::Registry::shared().sample(engine.data(),this,w,d);
  if(!first.windowBound||!first.visualDescendant)throw Lifetime::Refused("Actual taskbar window allocation required");
  const auto second=Lifetime::Registry::shared().sample(engine.data(),this,w,d);stable(a);
  if(first!=second||engine.isNull()||!Lifetime::Registry::shared().current(engine.data(),this,w,d,first))throw Lifetime::Refused("Actual widget/delegate observation changed");
  auto row=first.value();row.insert("schema","qml-object-lifetime-v1");row.insert("relationship","visual-widget-descendant");row.insert("processId",a.pid);row.insert("processStart",a.start);row.insert("configSHA256",QString::fromLatin1(a.configSHA));return row;
 }catch(const std::exception&e){return {{"schema","qml-object-lifetime-v1"},{"error",QString::fromUtf8(e.what())}};}
}
class ObjectLifetimePlugin final:public QQmlExtensionPlugin {
 Q_OBJECT
 Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
 void registerTypes(const char*uri)override{
  if(QByteArray(uri)!="WindowObjectLifetimeV1")qFatal("Exact lifetime module URI required");
  static std::once_flag once;std::call_once(once,[]{qmlRegisterSingletonType<ObjectLifetimeProvider>("WindowObjectLifetimeV1",1,0,"Lifetime",[](QQmlEngine*e,QJSEngine*)->QObject*{return new ObjectLifetimeProvider(e);});});
 }
};
#include "Provider.moc"

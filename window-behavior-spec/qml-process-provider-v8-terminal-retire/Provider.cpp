#include "Provider.hpp"
#include "NativeProcess.hpp"
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
QVariantMap ObjectLifetimeProvider::observePopup(QQuickItem*menu,QQuickItem*row,QObject*popup,QObject*actualQuickshell){
 QVariantMap diagnostics;
 try{
  const auto a=source();try{Lifetime::verifyQuickshellProcess();}catch(...){Lifetime::Registry::shared().refuse();throw;}
  Lifetime::Registry::shared().bindCore(engine.data(),this,actualQuickshell);
  QPointer<QObject>popupGuard=popup;
  if(!popup||popup->thread()!=QThread::currentThread())throw Lifetime::Refused("Actual lexical popup/thread required");
  const QMetaObject*base=nullptr;bool panel=false;
  for(auto*m=popup->metaObject();m;m=m->superClass()){
   if(QByteArray(m->className())=="PanelWindowInterface")panel=true;
   if(QByteArray(m->className())=="WindowInterface"){base=m;break;}
  }
  diagnostics.insert("actualPopupClass",QString::fromUtf8(popup->metaObject()->className()));diagnostics.insert("actualPanelBaseObserved",panel);diagnostics.insert("actualWindowBaseObserved",base!=nullptr);
  if(popupGuard.isNull()||!panel||!base)throw Lifetime::Refused("Actual PanelWindow/WindowInterface native metaobject required");
  const auto first=Lifetime::Registry::shared().samplePopup(engine.data(),this,menu,row,popup,base,&diagnostics);
  if(!first.nativeWindowBound)throw Lifetime::Refused("Actual popup native window/root allocations required");
  const auto second=Lifetime::Registry::shared().samplePopup(engine.data(),this,menu,row,popup,base,&diagnostics);stable(a);
  if(first!=second||popupGuard.isNull()||engine.isNull())throw Lifetime::Refused("Actual popup relationship changed");
  auto value=first.value();value.insert("schema","qml-popup-lifetime-v1");value.insert("relationship","lexical-pin-popup-existing-attached-native-content");value.insert("processId",a.pid);value.insert("processStart",a.start);value.insert("configSHA256",QString::fromLatin1(a.configSHA));value.insert("diagnostics",diagnostics);return value;
 }catch(const std::exception&e){return {{"schema","qml-popup-lifetime-v1"},{"error",QString::fromUtf8(e.what())},{"diagnostics",diagnostics}};}
}
QVariantMap ObjectLifetimeProvider::armProcess(QObject*menu,QObject*row,QObject*popup,QObject*process,QObject*out,QObject*err,const QString&role,const QString&originalJSON,QObject*actualQuickshell){
 try{const auto a=source();Lifetime::verifyQuickshellProcess();Lifetime::Registry::shared().bindCore(engine.data(),this,actualQuickshell);auto spec=Lifetime::nativeProcessArm(engine.data(),this,menu,row,popup,process,out,err,role,originalJSON,a);const auto lease=Lifetime::ProcessRegistry::shared().arm(std::move(spec));stable(a);return {{"schema","qml-pin-process-lifecycle-v1"},{"lease",qulonglong(lease)},{"armed",true},{"nativeWrites",0},{"automaticRetries",0}};}
 catch(const std::exception&e){return {{"schema","qml-pin-process-lifecycle-v1"},{"error",QString::fromUtf8(e.what())}};}
}
QVariantMap ObjectLifetimeProvider::retireProcess(QObject*menu,QObject*row,QObject*popup,QObject*process,QObject*out,QObject*err,const QVariant&lease,QObject*actualQuickshell){
 try{const auto a=source();Lifetime::verifyQuickshellProcess();Lifetime::Registry::shared().bindCore(engine.data(),this,actualQuickshell);const auto scope=Lifetime::nativeProcessRetireScope(engine.data(),this,menu,row,popup,process,out,err,lease,a);auto result=Lifetime::ProcessRegistry::shared().retire(scope);stable(a);return result;}
 catch(const std::exception&e){return {{"schema","qml-pin-process-lifecycle-v1"},{"error",QString::fromUtf8(e.what())},{"nativeWrites",0},{"automaticRetries",0}};}
}
QVariantMap ObjectLifetimeProvider::processState(QObject*process,QObject*actualQuickshell){
 try{const auto a=source();Lifetime::verifyQuickshellProcess();Lifetime::Registry::shared().bindCore(engine.data(),this,actualQuickshell);auto state=Lifetime::ProcessRegistry::shared().state(process);stable(a);state.insert("schema","qml-pin-process-lifecycle-v1");state.insert("processId",a.pid);state.insert("processStart",a.start);return state;}
 catch(const std::exception&e){return {{"schema","qml-pin-process-lifecycle-v1"},{"error",QString::fromUtf8(e.what())}};}
}
QVariantMap ObjectLifetimeProvider::cancelProcess(QObject*process,QObject*actualQuickshell){
 try{const auto a=source();Lifetime::verifyQuickshellProcess();Lifetime::Registry::shared().bindCore(engine.data(),this,actualQuickshell);Lifetime::ProcessRegistry::shared().cancel(process);stable(a);return {{"schema","qml-pin-process-lifecycle-v1"},{"completionRevoked",true},{"nativeWrites",0}};}
 catch(const std::exception&e){return {{"schema","qml-pin-process-lifecycle-v1"},{"error",QString::fromUtf8(e.what())}};}
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

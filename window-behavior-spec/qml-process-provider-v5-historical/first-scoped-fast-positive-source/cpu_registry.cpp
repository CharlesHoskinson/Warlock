#include "Lifetime.hpp"
#include <QCoreApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QQmlContext>
#include <QQmlEngine>
#include <QQuickItem>
#include <memory>
#include <iostream>
#include <thread>
static int checks=0;
void require(bool value,const char*name){if(!value)throw std::runtime_error(name);++checks;}
int main(int argc,char**argv){
 QCoreApplication app(argc,argv);
 try{
  uint64_t edge=Lifetime::SAFE_MAX-1;require(Lifetime::checkedNext(edge)==Lifetime::SAFE_MAX-1&&edge==Lifetime::SAFE_MAX,"exact last numeric allocation");bool overflow=false;try{Lifetime::checkedNext(edge);}catch(const Lifetime::Refused&){overflow=true;}require(overflow&&edge==Lifetime::SAFE_MAX,"overflow refuses without wrapping");
  bool capacity=false;try{Lifetime::checkedCapacity(Lifetime::CAPACITY,Lifetime::CAPACITY);}catch(const Lifetime::Refused&){capacity=true;}require(capacity,"bounded capacity refusal primitive");
  Lifetime::Registry registry;QQmlEngine first,second;QObject provider,provider2;
  const auto a=registry.registerProvider(&first,&provider),b=registry.registerProvider(&second,&provider2);
  require(a.generation!=b.generation&&a.epoch!=b.epoch&&a.provider!=b.provider,"two actual engine identities");
  require(registry.scope(&first,&provider)==a,"unchanged scope does not allocate");
  QQuickItem widget,delegate;delegate.setParentItem(&widget);
  QQmlEngine::setContextForObject(&widget,first.rootContext());QQmlEngine::setContextForObject(&delegate,first.rootContext());
  const auto t=registry.sample(&first,&provider,&widget,&delegate);
  require(t.visualDescendant&&!t.windowBound&&t.window==0,"actual Core-only Items have no native window authority");
  require(registry.current(&first,&provider,&widget,&delegate,t),"actual same sampled objects");
  require(registry.sample(&first,&provider,&widget,&delegate)==t,"same sampled generations");
  auto*p=new QObject;registry.registerProvider(&first,p);const auto pScope=registry.scope(&first,p);delete p;
  bool retired=false;try{registry.scope(&first,&provider);}catch(const Lifetime::Refused&){retired=true;}require(retired,"destroyed current provider cannot leave old provider valid");
  const auto recreated=registry.registerProvider(&first,&provider);require(recreated.generation==a.generation&&recreated.epoch>pScope.epoch&&recreated.provider==a.provider,"same actual engine provider reactivation advances epoch");
  require(!registry.current(&first,&provider,&widget,&delegate,t),"old sampled pair refuses after activation");
  // Actual QObject allocation reuse through placement construction, not a fabricated address token.
  alignas(QQuickItem) unsigned char space[sizeof(QQuickItem)];
  auto*old=new(space)QQuickItem;old->setParentItem(&widget);QQmlEngine::setContextForObject(old,first.rootContext());
  const auto oldPair=registry.sample(&first,&provider,&widget,old);old->~QQuickItem();
  auto*fresh=new(space)QQuickItem;fresh->setParentItem(&widget);QQmlEngine::setContextForObject(fresh,first.rootContext());
  const auto newPair=registry.sample(&first,&provider,&widget,fresh);
  require(fresh==old&&newPair.delegate>oldPair.delegate,"actual same-address QObject replacement gets new generation");
  require(!registry.current(&first,&provider,&widget,fresh,oldPair),"actual replacement refuses old sample");fresh->~QQuickItem();
  QQuickItem otherWidget,otherDelegate;otherDelegate.setParentItem(&otherWidget);QQmlEngine::setContextForObject(&otherWidget,first.rootContext());QQmlEngine::setContextForObject(&otherDelegate,second.rootContext());
  bool wrongEngine=false;try{registry.sample(&first,&provider,&otherWidget,&otherDelegate);}catch(const Lifetime::Refused&){wrongEngine=true;}require(wrongEngine,"actual cross-engine delegate refusal");
  QQuickItem detachedWidget,detached;QQmlEngine::setContextForObject(&detachedWidget,first.rootContext());QQmlEngine::setContextForObject(&detached,first.rootContext());
  bool ancestry=false;try{registry.sample(&first,&provider,&detachedWidget,&detached);}catch(const Lifetime::Refused&){ancestry=true;}require(ancestry,"actual missing visual ancestry refusal");
  auto*dynamic=new QQuickItem;dynamic->setParentItem(&widget);QQmlEngine::setContextForObject(dynamic,first.rootContext());const auto dynamicPair=registry.sample(&first,&provider,&widget,dynamic);QPointer<QQuickItem>weak=dynamic;delete dynamic;
  require(weak.isNull(),"real QPointer clears on destruction");require(!registry.current(&first,&provider,&widget,weak.data(),dynamicPair),"destroyed delegate between snapshots refuses");
  auto*context=new QQmlContext(&first);QQuickItem cw,cd;cd.setParentItem(&cw);QQmlEngine::setContextForObject(&cw,context);QQmlEngine::setContextForObject(&cd,context);const auto contextPair=registry.sample(&first,&provider,&cw,&cd);delete context;
  require(!registry.current(&first,&provider,&cw,&cd,contextPair),"actual context destruction refuses pair");
  auto*engine=new QQmlEngine;QObject ep;const auto oldEngine=registry.registerProvider(engine,&ep);QPointer<QQmlEngine>engineGuard=engine;delete engine;
  require(engineGuard.isNull(),"actual engine QPointer retirement");auto*newEngine=new QQmlEngine;const auto newEngineToken=registry.registerProvider(newEngine,&ep);require(newEngineToken.generation>oldEngine.generation&&newEngineToken.epoch>oldEngine.epoch,"engine recreation has monotonic process identities");delete newEngine;
  auto*oldCallbackProvider=new QObject;auto*replacementProvider=new QObject;
  QObject::connect(oldCallbackProvider,&QObject::destroyed,&app,[&]{registry.registerProvider(&first,replacementProvider);},Qt::DirectConnection);
  registry.registerProvider(&first,oldCallbackProvider);delete oldCallbackProvider;
  const auto callbackScope=registry.scope(&first,replacementProvider);require(callbackScope.provider>recreated.provider,"actual older destruction callback cannot retire replacement provider");
  bool fakeCore=false;QObject fake;try{registry.bindCore(&first,&provider,&fake);}catch(const Lifetime::Refused&){fakeCore=true;}require(fakeCore,"CPU process cannot impersonate frozen Quickshell target authority");
  bool threadRefused=false;std::thread peer([&]{try{registry.scope(&first,replacementProvider);}catch(const Lifetime::Refused&){threadRefused=true;}});peer.join();require(threadRefused&&registry.permanentlyRefused(),"actual foreign Qt thread invalidates registry");delete replacementProvider;
  std::cout<<QJsonDocument(QJsonObject{{"result","pass"},{"checks",checks},{"GUI",false},{"nativeWidgetAccepted",false}}).toJson(QJsonDocument::Compact).constData()<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}

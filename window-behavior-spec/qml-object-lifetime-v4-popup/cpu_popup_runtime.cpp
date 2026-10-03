#include "Lifetime.hpp"
#include <QJsonDocument>
#include <QJsonObject>
#include <QMetaProperty>
#include <QQmlComponent>
#include <qqml.h>
#include <functional>
#include <iostream>
#include <memory>
class CpuWindowInterface;
static int creations=0,checks=0;
class CpuAttached final:public QObject {
 Q_OBJECT
 Q_PROPERTY(QObject* window READ window CONSTANT)
 Q_PROPERTY(QQuickItem* contentItem READ contentItem CONSTANT)
 QPointer<CpuWindowInterface>allocation;
public:
 CpuAttached(QObject*,CpuWindowInterface*);
 QObject*window()const;
 QQuickItem*contentItem()const;
};
class CpuWindowInterface:public QObject {
 Q_OBJECT
 Q_PROPERTY(QQuickItem* contentItem READ contentItem CONSTANT)
 Q_PROPERTY(QObject* owner READ owner WRITE setOwner)
 QML_ATTACHED(CpuAttached)
 QQuickItem*content=new QQuickItem;
 QPointer<QObject>own;
public:
 mutable std::function<void()>ownerFault,contentFault;
 mutable bool staleContent=false;
 mutable QQuickItem*foreignContent=nullptr;
 CpuWindowInterface(){content->setParent(this);}
 QQuickItem*contentItem()const{
  auto*answer=staleContent?foreignContent:content;
  if(contentFault){auto call=std::move(contentFault);contentFault=nullptr;call();}
  return answer;
 }
 QObject*owner()const{auto*answer=own.data();if(ownerFault){auto call=std::move(ownerFault);ownerFault=nullptr;call();}return answer;}
 void setOwner(QObject*o){own=o;}
 static CpuAttached*qmlAttachedProperties(QObject*o){
  ++creations;for(auto*a=o;a;a=a->parent())if(auto*w=qobject_cast<CpuWindowInterface*>(a))return new CpuAttached(o,w);return new CpuAttached(o,nullptr);
 }
};
QML_DECLARE_TYPEINFO(CpuWindowInterface,QML_HAS_ATTACHED_PROPERTIES)
CpuAttached::CpuAttached(QObject*o,CpuWindowInterface*w):QObject(o),allocation(w){}
QObject*CpuAttached::window()const{return allocation.data();}
QQuickItem*CpuAttached::contentItem()const{return allocation?allocation->contentItem():nullptr;}
void require(bool ok,const char*m){if(!ok)throw std::runtime_error(m);++checks;}
struct Fixture {
 QQmlEngine engine;std::unique_ptr<QObject>root;QObject provider;
 QQuickItem*menu=nullptr,*row=nullptr,*missing=nullptr;CpuWindowInterface*popup=nullptr;
 explicit Fixture(Lifetime::Registry&registry){
  QQmlComponent c(&engine);c.setData(R"(import CpuPopupRuntime 1.0
Item {id:menu
 property WindowInterface popupAllocation: WindowInterface {
  id:popup;owner:menu
  default property alias contentItem:holder.children
  property Item holderAllocation:Item{id:holder}
  property Item rowAllocation:Item{property var selected:WindowInterface.window}
  property Item missingAllocation:Item{}
 }
})",QUrl("file:///cpu-only/popup-runtime.qml"));
  require(c.isReady(),qPrintable(c.errorString()));root.reset(c.create());require(bool(root),qPrintable(c.errorString()));
  menu=qobject_cast<QQuickItem*>(root.get());popup=qobject_cast<CpuWindowInterface*>(qvariant_cast<QObject*>(root->property("popupAllocation")));require(menu&&popup,"actual lexical CPU Qt menu/popup allocations");
  row=qvariant_cast<QQuickItem*>(popup->property("rowAllocation"));missing=qvariant_cast<QQuickItem*>(popup->property("missingAllocation"));require(row&&missing,"actual lexical Qt row allocations");
  // App fixture construction only; the observer never parents or assigns context.
  row->setParentItem(popup->contentItem());missing->setParentItem(popup->contentItem());registry.registerProvider(&engine,&provider);
 }
 Lifetime::PopupToken sample(Lifetime::Registry&r,QQuickItem*selected=nullptr,QVariantMap*diag=nullptr){return r.samplePopup(&engine,&provider,menu,selected?selected:row,popup,&CpuWindowInterface::staticMetaObject,diag);}
};
template<class F>void refuses(F f,const char*m){bool denied=false;try{f();}catch(const Lifetime::Refused&){denied=true;}require(denied,m);}
int main(int argc,char**argv){
 QCoreApplication app(argc,argv);
 try{
  qmlRegisterType<CpuWindowInterface>("CpuPopupRuntime",1,0,"WindowInterface");qmlRegisterType<QQuickItem>("CpuPopupRuntime",1,0,"Item");Lifetime::Registry registry;
  {
   Fixture f(registry);QVariantMap diag;const auto t=f.sample(registry,nullptr,&diag);require(!t.nativeWindowBound&&t.objects[5]==0&&t.objects[6]==0,"Core-only CPU sample cannot claim native window/root");
   require(t.objects[0]&&t.objects[1]&&t.objects[2]&&t.objects[3]&&t.objects[4],"actual lexical/attached/content generations captured");require(t.contexts[0]&&t.contexts[1]&&t.contexts[2],"lexical contexts mandatory and actual");
   require(t.contexts[3]==0&&t.contexts[4]==0&&!t.enginePresent[3]&&!t.enginePresent[4],"actual native context absence explicit zero");require(f.sample(registry)==t,"unchanged actual tuple stable");
   const int before=creations;refuses([&]{f.sample(registry,f.missing);},"missing actual attachment refuses");require(creations==before,"observer missing attachment creates nothing");
   const auto native=CpuWindowInterface::staticMetaObject.property(CpuWindowInterface::staticMetaObject.indexOfProperty("contentItem"));const auto dynamic=f.popup->metaObject()->property(f.popup->metaObject()->indexOfProperty("contentItem"));require(native.metaType()!=dynamic.metaType(),"actual list alias cannot replace native property witness");
   f.popup->setOwner(&f.provider);refuses([&]{f.sample(registry);},"different lexical owner refuses");
  }
  {
   Fixture f(registry);auto*original=f.popup->contentItem();f.popup->ownerFault=[&]{QQmlEngine::setContextForObject(original,f.engine.rootContext());};
   refuses([&]{f.sample(registry);},"actual native context appears inside property getter; old tuple refused");
   const auto fresh=f.sample(registry);require(fresh.contexts[4]>0&&fresh.enginePresent[4],"fresh actual present native context authenticated in factory engine");
  }
  {
   Fixture f(registry);auto*content=f.popup->contentItem();f.popup->contentFault=[&]{QQmlEngine::setContextForObject(content,f.engine.rootContext());};
   refuses([&]{f.sample(registry);},"actual native context change in FIRST content getter refuses anchored context");
  }
  {
   Fixture f(registry);QQmlEngine foreign;QQmlEngine::setContextForObject(f.popup->contentItem(),foreign.rootContext());refuses([&]{f.sample(registry);},"actual foreign native context refuses");
  }
  {
   Fixture f(registry);auto*content=f.popup->contentItem();auto*context=new QQmlContext(&f.engine);QQmlEngine::setContextForObject(content,context);
   f.popup->ownerFault=[&]{delete context;};refuses([&]{f.sample(registry);},"actual selected native QQmlContext retirement inside getter refuses");
  }
  {
   Fixture f(registry);auto*content=f.popup->contentItem();f.popup->ownerFault=[&]{delete content;};refuses([&]{f.sample(registry);},"actual content retirement inside getter refuses before dereference");
  }
  {
   Fixture f(registry);f.popup->ownerFault=[&]{delete f.row;};refuses([&]{f.sample(registry);},"actual lexical row retirement inside getter refuses");
  }
  {
   Fixture f(registry);const auto fn=qmlAttachedPropertiesFunction(f.row,&CpuWindowInterface::staticMetaObject);auto*attached=qmlAttachedPropertiesObject(f.row,fn,false);require(attached!=nullptr,"actual preexisting attached fault target");
   f.popup->ownerFault=[&]{delete attached;};refuses([&]{f.sample(registry);},"actual attached retirement inside getter refuses");
  }
  {
   Fixture f(registry);QQuickItem other;f.popup->ownerFault=[&]{f.row->setParentItem(&other);};refuses([&]{f.sample(registry);},"actual row ancestry change inside getter refuses");f.row->setParentItem(nullptr);
  }
  {
   Fixture f(registry);auto*dead=new QQuickItem;delete dead;f.popup->staleContent=true;f.popup->foreignContent=dead;
   refuses([&]{f.sample(registry);},"unanchored stale returned content pointer refuses without QObject conversion/dereference");
  }
  std::cout<<QJsonDocument(QJsonObject{{"result","pass"},{"checks",checks},{"GUI",false},{"nativeWindowCreated",false},{"actualInstalledQSPopupAccepted",false},{"scope","actual CPU Qt allocation/property/context/retirement tests; no native input witness"}}).toJson(QJsonDocument::Compact).constData()<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
#include "cpu_popup_runtime.moc"

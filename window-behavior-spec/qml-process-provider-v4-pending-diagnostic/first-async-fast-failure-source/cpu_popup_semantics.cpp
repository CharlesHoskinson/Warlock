#include <QCoreApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMetaProperty>
#include <QPointer>
#include <QQmlComponent>
#include <QQmlEngine>
#include <QQuickItem>
#include <qqml.h>
#include <iostream>
#include <stdexcept>
class CpuWindowInterface;
static int attachedCreations=0,baseReads=0,checks=0;
class CpuAttached final:public QObject {
 Q_OBJECT
 Q_PROPERTY(QObject* window READ window CONSTANT)
 Q_PROPERTY(QQuickItem* contentItem READ contentItem CONSTANT)
 QPointer<CpuWindowInterface>actual;
public:
 CpuAttached(QObject*,CpuWindowInterface*);
 QObject*window()const;
 QQuickItem*contentItem()const;
};
class CpuWindowInterface:public QObject {
 Q_OBJECT
 Q_PROPERTY(QQuickItem* contentItem READ contentItem CONSTANT)
 Q_PROPERTY(QQuickItem* nativeContent READ contentItem CONSTANT)
 QML_ATTACHED(CpuAttached)
 QQuickItem*item=new QQuickItem;
public:
 CpuWindowInterface(){item->setParent(this);}
 QQuickItem*contentItem()const{++baseReads;return item;}
 static CpuAttached*qmlAttachedProperties(QObject*o){
  ++attachedCreations;
  for(auto*ancestor=o;ancestor;ancestor=ancestor->parent())if(auto*w=qobject_cast<CpuWindowInterface*>(ancestor))return new CpuAttached(o,w);
  return new CpuAttached(o,nullptr);
 }
};
QML_DECLARE_TYPEINFO(CpuWindowInterface,QML_HAS_ATTACHED_PROPERTIES)
CpuAttached::CpuAttached(QObject*o,CpuWindowInterface*w):QObject(o),actual(w){}
QObject*CpuAttached::window()const{return actual.data();}
QQuickItem*CpuAttached::contentItem()const{return actual?actual->contentItem():nullptr;}
void require(bool b,const char*m){if(!b)throw std::runtime_error(m);++checks;}
int main(int argc,char**argv){
 QCoreApplication app(argc,argv);
 try{
  qmlRegisterType<CpuWindowInterface>("CpuPopupSemantics",1,0,"WindowInterface");qmlRegisterType<QQuickItem>("CpuPopupSemantics",1,0,"Item");
  QQmlEngine e;QQmlComponent component(&e);
  component.setData(R"(import CpuPopupSemantics 1.0
WindowInterface {
 id: popup
 default property alias contentItem: holder.children
 property Item holderAllocation: Item {id:holder}
 property Item rowAllocation: Item {
  property var selectedWindow: WindowInterface.window
  property var selectedContent: WindowInterface.contentItem
 }
})",QUrl("file:///cpu-only/popup-semantics.qml"));
  require(component.isReady(),qPrintable(component.errorString()));std::unique_ptr<QObject>root(component.create());require(bool(root),qPrintable(component.errorString()));
  auto*window=qobject_cast<CpuWindowInterface*>(root.get());require(window!=nullptr,"actual registered C++ base object");
  auto*row=qvariant_cast<QQuickItem*>(root->property("rowAllocation"));require(row!=nullptr,"actual QML allocated Item");
  require(QQmlEngine::contextForObject(row)&&qmlEngine(row)==&e&&qmlEngine(root.get())==&e,"actual QML context engine association");
  const auto*base=&CpuWindowInterface::staticMetaObject;const int index=base->indexOfProperty("contentItem");require(index>=0,"actual native base property index");
  const auto native=base->property(index);require(native.isReadable()&&!native.isWritable()&&native.metaType()==QMetaType::fromType<QQuickItem*>(),"native base pointer/readonly definition");
  const auto dynamic=root->metaObject()->property(root->metaObject()->indexOfProperty("contentItem"));require(dynamic.metaType()!=native.metaType(),"actual dynamic contentItem is list alias not pointer");
  const int readsBefore=baseReads;auto*nativeItem=qvariant_cast<QQuickItem*>(native.read(root.get()));require(nativeItem&&nativeItem==window->contentItem()&&baseReads>=readsBefore+2,"native base QMetaProperty invokes native getter beneath dynamic list alias");
  const auto func=qmlAttachedPropertiesFunction(row,base);require(func!=nullptr,"actual registered attached function");
  auto*attached=qmlAttachedPropertiesObject(row,func,false);require(attached!=nullptr,"readonly lookup observes actual existing attached object");
  require(attached->parent()==row&&attached->metaObject()==&CpuAttached::staticMetaObject,"actual attached object allocation and row parent");
  require(qvariant_cast<QObject*>(attached->property("window"))==root.get()&&qvariant_cast<QQuickItem*>(attached->property("contentItem"))==nativeItem,"actual existing attached pointer relationships");
  const QJsonObject contexts{{"menuContextPresent",QQmlEngine::contextForObject(root.get())!=nullptr},{"rowContextPresent",QQmlEngine::contextForObject(row)!=nullptr},{"attachedContextPresent",QQmlEngine::contextForObject(attached)!=nullptr},{"attachedEnginePresent",qmlEngine(attached)!=nullptr},{"nativeContentContextPresent",QQmlEngine::contextForObject(nativeItem)!=nullptr},{"nativeContentEnginePresent",qmlEngine(nativeItem)!=nullptr}};
  QQuickItem missing;QQmlEngine::setContextForObject(&missing,e.rootContext());const int before=attachedCreations;
  auto*absent=qmlAttachedPropertiesObject(&missing,func,false);require(absent==nullptr&&before==attachedCreations,"missing attached lookup create=false creates nothing");
  require(qmlAttachedPropertiesObject(row,func,false)==attached&&before==attachedCreations,"repeated readonly attached lookup reuses actual object");
  QPointer<QObject>guard=attached;QPointer<QObject>rootGuard=root.get();root.reset();require(guard.isNull()&&rootGuard.isNull(),"actual lexical/attached QObject retirement clears QPointers");
  std::cout<<QJsonDocument(QJsonObject{{"result","pass"},{"checks",checks},{"GUI",false},{"nativeWindowCreated",false},{"actualQuickshellPopupAccepted",false},{"scope","Qt public API semantics using CPU stand-ins only"},{"actualContextPresence",contexts}}).toJson(QJsonDocument::Compact).constData()<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
#include "cpu_popup_semantics.moc"

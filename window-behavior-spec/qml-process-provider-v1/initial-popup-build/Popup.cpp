#include "Lifetime.hpp"
#include <QJSValue>
#include <QMetaProperty>
#include <QQuickWindow>
#include <qqml.h>
#include <set>
#include <vector>
namespace Lifetime {
QVariantMap PopupToken::value()const{
 const char*names[]={"menu","row","popup","attached","content","window","nativeRoot"};QVariantMap allocations,contextRows;
 for(size_t i=0;i<objects.size();++i){allocations.insert(QString::fromLatin1(names[i]),qulonglong(objects[i]));contextRows.insert(QString::fromLatin1(names[i]),QVariantMap{{"generation",qulonglong(contexts[i])},{"present",contexts[i]!=0},{"enginePresent",enginePresent[i]}});}
 return {{"engineGeneration",qulonglong(engine.generation)},{"engineEpoch",qulonglong(engine.epoch)},{"providerGeneration",qulonglong(engine.provider)},{"allocations",allocations},{"contexts",contextRows},{"nativeWindowBound",nativeWindowBound}};
}
namespace {
struct ItemGuard{QQuickItem*address;QPointer<QQuickItem>weak;};
struct ContextGuard{QQmlContext*address=nullptr;QPointer<QQmlContext>weak;QQmlEngine*engine=nullptr;uint64_t generation=0;};
QObject*objectValue(const QVariant&v){
 if(v.metaType().flags().testFlag(QMetaType::PointerToQObject))return v.value<QObject*>();
 if(v.metaType()==QMetaType::fromType<QJSValue>()){const auto js=v.value<QJSValue>();if(js.isQObject())return js.toQObject();}
 throw Refused("Actual object property value type required");
}
QMetaProperty property(const QMetaObject*meta,const char*name,QMetaType type,bool constant=false){
 const auto index=meta->indexOfProperty(name);if(index<0)throw Refused("Actual native property missing");const auto p=meta->property(index);
 if(!p.isReadable()||p.isWritable()||p.metaType()!=type||(constant&&!p.isConstant()))throw Refused("Actual native readonly pointer property definition differs");return p;
}
std::vector<ItemGuard>parents(QQuickItem*start){
 std::vector<ItemGuard>result;std::set<QQuickItem*>seen;
 for(auto*p=start;p;p=p->parentItem()){
  if(!seen.insert(p).second||seen.size()>4096)throw Refused("Actual popup visual path cyclic/unbounded");result.push_back({p,QPointer<QQuickItem>(p)});
 }
 return result;
}
}
PopupToken Registry::samplePopup(QQmlEngine*e,QObject*p,QQuickItem*menu,QQuickItem*row,QObject*popup,const QMetaObject*base,QVariantMap*diagnostics){
 const auto token=scope(e,p);QPointer<QQmlEngine>engineGuard=e;QPointer<QObject>providerGuard=p,popupGuard=popup;QPointer<QQuickItem>menuGuard=menu,rowGuard=row;
 if(!menu||!row||!popup||!base||menu==row||popup==menu||popup==row||menu->thread()!=owner||row->thread()!=owner||popup->thread()!=owner)throw Refused("Actual distinct lexical popup objects/thread required");
 bool nativeBase=false;for(auto*m=popup->metaObject();m;m=m->superClass())if(m==base){nativeBase=true;break;}
 if(!nativeBase)throw Refused("Actual popup native base metaobject differs");
 auto path=parents(row);std::vector<QPointer<QObject>>children;
 if(row->children().size()>4096)throw Refused("Actual existing attached child lookup bound exceeded");
 for(auto*c:row->children())children.emplace_back(c);
 auto*window=row->window();QPointer<QQuickWindow>windowGuard=window;auto*nativeRoot=window?window->contentItem():nullptr;QPointer<QQuickItem>rootGuard=nativeRoot;
 auto checkAlive=[&]{
  if(engineGuard.isNull()||providerGuard.isNull()||popupGuard.isNull()||menuGuard.isNull()||rowGuard.isNull()||(window&&windowGuard.isNull())||(nativeRoot&&rootGuard.isNull()))throw Refused("Selected actual popup allocation retired across read");
  for(const auto&i:path)if(i.weak.isNull()||i.weak.data()!=i.address)throw Refused("Selected actual visual path retired across read");
  if(scope(e,p)!=token)throw Refused("Actual popup engine activation changed");
 };
 checkAlive();const auto contentProperty=property(base,"contentItem",QMetaType::fromType<QQuickItem*>(),true);
 if(diagnostics){diagnostics->insert("nativeContentPropertyIndex",contentProperty.propertyIndex());diagnostics->insert("nativeContentPropertyType",QString::fromLatin1(contentProperty.metaType().name()));}
 const auto contentValue=contentProperty.read(popup);checkAlive();auto*content=qvariant_cast<QQuickItem*>(contentValue);
 QPointer<QQuickItem>contentGuard;size_t contentIndex=path.size();
 for(size_t i=0;i<path.size();++i)if(path[i].address==content){contentGuard=path[i].weak;contentIndex=i;break;}
 if(!content||contentIndex==0||contentIndex==path.size()||contentGuard.isNull())throw Refused("Actual native popup content is not an existing row visual ancestor");
 if(content->window()!=window)throw Refused("Actual popup content/window association differs");
 if(window){
  bool rootReached=false;for(size_t i=contentIndex;i<path.size();++i)if(path[i].address==nativeRoot){rootReached=true;break;}
  if(!nativeRoot||!rootReached)throw Refused("Actual native root/content ancestry differs");
 }
 const auto func=qmlAttachedPropertiesFunction(row,base);checkAlive();
 if(!func)throw Refused("Actual registered popup attached function missing");
 auto*attached=qmlAttachedPropertiesObject(row,func,false);checkAlive();QPointer<QObject>attachedGuard;
 // Authenticate the pointer against children captured before lookup; never
 // instantiate or construct a guard from a newly returned unanchored pointer.
 for(const auto&child:children)if(child.data()==attached){attachedGuard=child;break;}
 if(!attached||attachedGuard.isNull()||attached->parent()!=row||attached->thread()!=owner)throw Refused("Actual existing row attached object missing/differs");
 std::array<QObject*,7>selected={menu,row,popup,attached,content,window,nativeRoot};std::array<QPointer<QObject>,7>guards;
 for(size_t i=0;i<selected.size();++i)guards[i]=selected[i];
 auto allAlive=[&]{checkAlive();for(size_t i=0;i<selected.size();++i)if(selected[i]&&(guards[i].isNull()||guards[i].data()!=selected[i]))throw Refused("Actual selected popup tuple retired");};
 PopupToken result;result.engine=token;result.nativeWindowBound=window!=nullptr;std::array<ContextGuard,7>contexts;
 for(size_t i=0;i<selected.size();++i){
  allAlive();auto*o=selected[i];if(!o)continue;if(o->thread()!=owner)throw Refused("Actual popup tuple owning thread differs");
  result.objects[i]=object(o);allAlive();auto*context=QQmlEngine::contextForObject(o);auto*actualEngine=qmlEngine(o);contexts[i].address=context;contexts[i].weak=context;contexts[i].engine=actualEngine;
  if(diagnostics){diagnostics->insert(QString("context%1Present").arg(i),context!=nullptr);diagnostics->insert(QString("context%1EnginePresent").arg(i),actualEngine!=nullptr);}
  if(!context){if(i<3||actualEngine)throw Refused("Lexical context missing or native absent context has conflicting engine");}
  else{
   if(!context->isValid()||context->engine()!=e||actualEngine!=e)throw Refused("Actual popup context/factory engine differs");
   contexts[i].generation=object(context);allAlive();if(contexts[i].weak.isNull())throw Refused("Actual popup context retired during binding");
  }
  result.contexts[i]=contexts[i].generation;result.enginePresent[i]=actualEngine!=nullptr;
 }
 const auto attachedWindow=property(attached->metaObject(),"window",QMetaType::fromType<QObject*>());const auto attachedContent=property(attached->metaObject(),"contentItem",QMetaType::fromType<QQuickItem*>());
 auto readPointer=[&](QObject*object,const QMetaProperty&field){const auto v=field.read(object);allAlive();auto*value=objectValue(v);allAlive();return value;};
 auto verifyRelations=[&]{
  allAlive();if(readPointer(attached,attachedWindow)!=popup||readPointer(attached,attachedContent)!=content)throw Refused("Actual existing attached window/content pointers differ");
  if(readPointer(popup,contentProperty)!=content)throw Refused("Actual native base content changed");
  const auto ownerIndex=popup->metaObject()->indexOfProperty("owner");if(ownerIndex<0)throw Refused("Actual lexical popup owner property missing");
  const auto ownerProperty=popup->metaObject()->property(ownerIndex);if(!ownerProperty.isReadable())throw Refused("Actual popup owner unreadable");
  if(diagnostics)diagnostics->insert("popupOwnerPropertyType",QString::fromLatin1(ownerProperty.metaType().name()));
  if(readPointer(popup,ownerProperty)!=menu)throw Refused("Actual popup lexical owner differs");
  allAlive();if(qmlAttachedPropertiesObject(row,func,false)!=attached||attached->parent()!=row||row->window()!=window||content->window()!=window||(window&&window->contentItem()!=nativeRoot))throw Refused("Actual popup attachment/window association changed");
  const auto current=parents(row);if(current.size()!=path.size())throw Refused("Actual popup visual path changed");
  for(size_t i=0;i<path.size();++i)if(current[i].address!=path[i].address)throw Refused("Actual popup visual path changed");
 };
 auto verifyContexts=[&]{
  allAlive();for(size_t i=0;i<selected.size();++i){
   auto*o=selected[i];if(!o)continue;auto&c=contexts[i];
   if(QQmlEngine::contextForObject(o)!=c.address||qmlEngine(o)!=c.engine||object(o)!=result.objects[i])throw Refused("Actual popup context presence/object allocation changed");
   allAlive();if(c.address&&(c.weak.isNull()||!c.address->isValid()||c.address->engine()!=e||object(c.address)!=c.generation))throw Refused("Actual popup context allocation/engine changed");
  }
 };
 verifyRelations();verifyContexts();verifyRelations();verifyContexts();allAlive();return result;
}
}

#include <QQmlExtensionPlugin>
#include <QQmlEngine>
#include <QQuickWindow>
#include <QQuickItem>
#include <QKeyEvent>
#include <QCoreApplication>
#include <QAccessible>
#include <QPointer>
#include <QtQuick/private/qquickaccessibleattached_p.h>
#include <QJsonDocument>
#include <QJsonObject>
#include <QtQuick/private/qquicktextinput_p.h>
#include <QtQuick/private/qquicktextedit_p.h>
class FixtureKeys final: public QObject {
  Q_OBJECT
  QAccessible::Id retainedId=0;
  QPointer<QObject> retainedObject;
  QAccessibleEditableTextInterface* cachedEditable=nullptr;
public:
  Q_INVOKABLE QString retain(QObject* item) {
    retainedObject=item;auto* iface=QAccessible::queryAccessibleInterface(item);
    cachedEditable=iface ? iface->editableTextInterface() : nullptr;
    retainedId=iface ? QAccessible::uniqueId(iface) : 0;
    return QString::number(retainedId);
  }
  QJsonObject textState() const {
    if(!retainedObject)return {{"objectAlive",false}};
    return {{"objectAlive",true},{"text",retainedObject->property("text").toString()},{"selectionStart",retainedObject->property("selectionStart").toInt()},{"selectionEnd",retainedObject->property("selectionEnd").toInt()},{"cursorPosition",retainedObject->property("cursorPosition").toInt()}};
  }
  Q_INVOKABLE bool prepareText(QString text) {
    if(!retainedObject)return false;
    retainedObject->setProperty("text",text);
    if(auto* item=qobject_cast<QQuickTextInput*>(retainedObject))item->select(0,2);
    if(auto* item=qobject_cast<QQuickTextEdit*>(retainedObject))item->select(0,2);
    return true;
  }
  Q_INVOKABLE bool controlProperty(QString key,QString value) {
    return retainedObject && retainedObject->setProperty(qPrintable(key),QVariant(value=="true"));
  }
  Q_INVOKABLE QString mutate(QString operation) {
    QJsonObject result{{"before",textState()}};
    auto* iface=QAccessible::accessibleInterface(retainedId);
    result["interfaceFound"]=iface!=nullptr;result["objectAlive"]=!retainedObject.isNull();
    if(iface && iface->isValid() && retainedObject) {
      auto state=iface->state();result["invisible"]=bool(state.invisible);result["disabled"]=bool(state.disabled);result["readOnly"]=bool(state.readOnly);
      auto* text=iface->textInterface();result["hasText"]=text!=nullptr;result["hasCurrentEditable"]=iface->editableTextInterface()!=nullptr;result["hasCachedEditable"]=cachedEditable!=nullptr;
      if(operation=="delete" && cachedEditable)cachedEditable->deleteText(1,3);
      else if(operation=="insert" && cachedEditable)cachedEditable->insertText(2,QStringLiteral("X"));
      else if(operation=="replace" && cachedEditable)cachedEditable->replaceText(1,3,QStringLiteral("X"));
      else if(operation=="selection" && text)text->setSelection(0,3,5);
      else if(operation=="addSelection" && text)text->addSelection(3,5);
      else if(operation=="removeSelection" && text)text->removeSelection(0);
      else if(operation=="cursor" && text)text->setCursorPosition(4);
      else if(operation=="setValue")iface->setText(QAccessible::Value,QStringLiteral("X"));
    }
    result["after"]=textState();result["changed"]=result["before"]!=result["after"];
    return QString::fromUtf8(QJsonDocument(result).toJson(QJsonDocument::Compact));
  }
  Q_INVOKABLE QString dispatch(QString action) {
    auto* iface=QAccessible::accessibleInterface(retainedId);
    QJsonObject report{{"objectAlive",!retainedObject.isNull()},{"interfaceFound",iface!=nullptr}};
    if(iface){ auto st=iface->state();report["valid"]=iface->isValid();report["invisible"]=bool(st.invisible);report["disabled"]=bool(st.disabled);report["name"]=iface->text(QAccessible::Name);report["class"]=retainedObject ? retainedObject->metaObject()->className() : "";
      auto* ai=iface->actionInterface();report["hasActionInterface"]=ai!=nullptr;
      if(ai)ai->doAction(action);
    }
    return QString::fromUtf8(QJsonDocument(report).toJson(QJsonDocument::Compact));
  }
  Q_INVOKABLE bool rawAttachedToggle() {
    auto* attached=retainedObject ? QQuickAccessibleAttached::attachedProperties(retainedObject) : nullptr;
    return attached && QMetaObject::invokeMethod(attached,"toggleAction",Qt::DirectConnection);
  }
  Q_INVOKABLE bool rawAttachedPress() {
    auto* attached=retainedObject ? QQuickAccessibleAttached::attachedProperties(retainedObject) : nullptr;
    return attached && QMetaObject::invokeMethod(attached,"pressAction",Qt::DirectConnection);
  }
  Q_INVOKABLE bool tap(QObject* proxy, int key, int modifiers) {
    auto* content = proxy->property("contentItem").value<QQuickItem*>();
    auto* window = content ? content->window() : nullptr;
    if (!window) return false;
    QKeyEvent press(QEvent::KeyPress, key, Qt::KeyboardModifiers(modifiers));
    QKeyEvent release(QEvent::KeyRelease, key, Qt::KeyboardModifiers(modifiers));
    QCoreApplication::sendEvent(window,&press);
    QCoreApplication::sendEvent(window,&release);
    return true;
  }
  Q_INVOKABLE QString focus(QObject* proxy) {
    auto* content=proxy->property("contentItem").value<QQuickItem*>();
    auto* window=content ? content->window() : nullptr;
    auto* item=window ? window->activeFocusItem() : nullptr;
    return item ? item->objectName() : QString();
  }
};
class FixtureKeysPlugin final: public QQmlExtensionPlugin {
  Q_OBJECT
  Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
  void registerTypes(const char* uri) override {
    qmlRegisterSingletonType<FixtureKeys>(uri,1,0,"FixtureKeys",[](QQmlEngine*,QJSEngine*)->QObject* { return new FixtureKeys; });
  }
};
#include "keys.moc"

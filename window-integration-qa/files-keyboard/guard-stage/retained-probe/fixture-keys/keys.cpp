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
class FixtureKeys final: public QObject {
  Q_OBJECT
  QAccessible::Id retainedId=0;
  QPointer<QObject> retainedObject;
public:
  Q_INVOKABLE QString retain(QObject* item) {
    retainedObject=item;auto* iface=QAccessible::queryAccessibleInterface(item);
    retainedId=iface ? QAccessible::uniqueId(iface) : 0;
    return QString::number(retainedId);
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

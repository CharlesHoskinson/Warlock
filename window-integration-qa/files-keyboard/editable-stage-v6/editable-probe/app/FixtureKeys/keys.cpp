#include <QQmlExtensionPlugin>
#include <QQmlEngine>
#include <QQuickWindow>
#include <QQuickItem>
#include <QKeyEvent>
#include <QCoreApplication>
class FixtureKeys final: public QObject {
  Q_OBJECT
public:
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

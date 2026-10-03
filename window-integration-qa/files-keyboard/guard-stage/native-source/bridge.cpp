// Qt Quick factory dispatch adapted from Qt 6.11.2 qquickaccessiblefactory.cpp.
// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LGPL-3.0-only
#include <QQmlExtensionPlugin>
#include <QAccessible>
#include <QGuiApplication>
#include <QQmlEngine>
#include <QJSValue>
#include <QTimer>
#include <QPointer>
#include <QHash>
#include "shutdownfocus.h"
#include <QtQuick/private/qaccessiblequickview_p.h>
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QtQuick/private/qaccessiblequicktextedit_p.h>
#include <QtQuick/private/qaccessiblequicktextinput_p.h>
#include <QtQuick/private/qquickitem_p.h>
#include <QtQuick/private/qquicktextedit_p.h>
#include <QtQuick/private/qquicktextinput_p.h>

namespace {
bool permitted(QQuickItem* item) {
    if (!item || !item->isVisible() || !item->isEnabled() || !item->window() || !item->window()->isVisible()) return false;
    for (auto* ancestor=item; ancestor; ancestor=ancestor->parentItem()) {
        const auto value=ancestor->property("actionOwner");
        auto* owner=value.value<QObject*>();
        if (!owner && value.canConvert<QJSValue>()) owner=value.value<QJSValue>().toQObject();
        if (!owner) continue;
        QVariant result;
        if (!QMetaObject::invokeMethod(owner,"permitsAction",Qt::DirectConnection,
             Q_RETURN_ARG(QVariant,result),Q_ARG(QVariant,QVariant::fromValue(item)))) return false;
        return result.toBool();
    }
    return true;
}
class FocusIntentMonitor final: public QObject {
public:
    quint64 inputEpoch=0;
    quint64 focusEpoch=0;
    explicit FocusIntentMonitor(QQuickWindow* window,QObject* parent):QObject(parent) {if(window)window->installEventFilter(this);}
protected:
    bool eventFilter(QObject*,QEvent* event) override {
        switch(event->type()) {
        case QEvent::KeyPress:case QEvent::MouseButtonPress:case QEvent::TouchBegin:
        case QEvent::TabletPress:case QEvent::Wheel:case QEvent::Hide:
        case QEvent::WindowDeactivate:++inputEpoch;break;
        default:break;
        }
        return false;
    }
};
class ActionState final: public QObject {
    Q_OBJECT
    QHash<QQuickItem*,quint64> requestGenerations;
public:
    Q_INVOKABLE bool allowed(QObject* object) const { return permitted(qobject_cast<QQuickItem*>(object)); }
    Q_INVOKABLE QString focusIdentity(QQuickItem* content) const {
        auto* window=content ? content->window() : nullptr;
        auto* active=window ? window->activeFocusItem() : nullptr;
        bool belongs=false;for(auto* ancestor=active;ancestor;ancestor=ancestor->parentItem())if(ancestor==content){belongs=true;break;}
        // ProxyWindow transfers its backing window before PersistentProperties reads
        // the old state. Never let a new generation overwrite the old focus identity.
        if(!belongs)return {};
        for(auto* item=active;item;item=item->parentItem()) {
            const auto identity=item->property("actionIdentity").toString();
            if (!identity.isEmpty()) return identity;
        }
        return {};
    }
    Q_INVOKABLE void restoreLater(QQuickItem* content,const QString& identity) {
        if(!content || identity.isEmpty())return;
        QPointer<QQuickItem> guard(content);
        QPointer<QQuickWindow> window(content->window());
        const auto generation=++requestGenerations[content];
        connect(content,&QObject::destroyed,this,[this,content]{requestGenerations.remove(content);});
        auto* intent=new FocusIntentMonitor(window,this);
        const auto baseline=focusIdentity(content);
        if(window)connect(window,&QQuickWindow::activeFocusItemChanged,intent,[this,intent,guard,baseline,identity]{
            const auto current=guard ? focusIdentity(guard) : QString();
            if(!current.isEmpty() && current!=baseline && current!=identity)++intent->focusEpoch;
        });
        const auto inputEpoch=intent->inputEpoch,focusEpoch=intent->focusEpoch;
        auto* timer=new QTimer(intent);timer->setInterval(40);
        connect(timer,&QTimer::timeout,intent,[this,timer,intent,guard,window,identity,generation,inputEpoch,focusEpoch,attempts=0]() mutable {
            ++attempts;
            // Content lifetime identifies the reload generation. A newer request,
            // input event or focus choice cancels this generation's restoration.
            const bool current=guard && window && window->isVisible() && guard->window()==window
                && requestGenerations.value(guard)==generation
                && intent->inputEpoch==inputEpoch && intent->focusEpoch==focusEpoch;
            const bool ok=current && restoreFocus(guard,identity);
            if(ok || !current || attempts>=40) {timer->stop();intent->deleteLater();emit focusRestored(identity,ok);}
        });
        timer->start();
    }
    Q_INVOKABLE bool restoreFocus(QQuickItem* content,const QString& identity) const {
        if(!content || identity.isEmpty()) return false;
        if(content->property("actionIdentity").toString()==identity && permitted(content)) {
            content->forceActiveFocus(Qt::OtherFocusReason);return true;
        }
        for(auto* child:content->childItems())if(restoreFocus(child,identity))return true;
        return false;
    }
signals:
    void focusRestored(QString identity,bool restored);
};
class QuickItemWithMenu final : public QAccessibleQuickItem {
public:
    using QAccessibleQuickItem::QAccessibleQuickItem;
    bool isValid() const override {
        // Attached-property construction caches an interface before QML can
        // set Accessible.ignored. Qt keeps that interface in its cache; later
        // focus events must honor the current accessibility flag as well.
        auto* item = qobject_cast<QQuickItem*>(object());
        return QAccessibleQuickItem::isValid() && item
            && QQuickItemPrivate::get(item)->isAccessible;
    }
    bool hasMenu() const {
        return object() && object()->metaObject()->indexOfMethod("accessibleShowMenu()") >= 0;
    }
    QAccessible::State state() const override {
        auto result = QAccessibleQuickItem::state();
        result.hasPopup = hasMenu();
        return result;
    }
    QStringList actionNames() const override {
        auto result = QAccessibleQuickItem::actionNames();
        if (hasMenu()) result.append(QAccessibleActionInterface::showMenuAction());
        return result;
    }
    void doAction(const QString& action) override {
        if(!isValid())return;
        const auto current=state();
        if(current.invisible || current.disabled || !permitted(qobject_cast<QQuickItem*>(object()))) return;
        if (action == QAccessibleActionInterface::showMenuAction()) {
            const auto current = state();
            if (hasMenu() && !current.invisible && !current.disabled)
                QMetaObject::invokeMethod(object(), "accessibleShowMenu", Qt::DirectConnection);
            return;
        }
        QAccessibleQuickItem::doAction(action);
    }
};

class GuardedTextInput final: public QAccessibleQuickTextInput {
public:
    using QAccessibleQuickTextInput::QAccessibleQuickTextInput;
    void doAction(const QString& action) override {if(isValid() && !state().invisible && !state().disabled && permitted(qobject_cast<QQuickItem*>(object()))) QAccessibleQuickTextInput::doAction(action);}
};
class GuardedTextEdit final: public QAccessibleQuickTextEdit {
public:
    using QAccessibleQuickTextEdit::QAccessibleQuickTextEdit;
    void doAction(const QString& action) override {if(isValid() && !state().invisible && !state().disabled && permitted(qobject_cast<QQuickItem*>(object()))) QAccessibleQuickTextEdit::doAction(action);}
};
QAccessibleInterface* quickFactory(const QString& name, QObject* object) {
    if (name == QStringLiteral("QQuickWindow"))
        return new QAccessibleQuickWindow(qobject_cast<QQuickWindow*>(object));
    if (name == QStringLiteral("QQuickTextEdit"))
        return new GuardedTextEdit(qobject_cast<QQuickTextEdit*>(object));
    if (name == QStringLiteral("QQuickTextInput"))
        return new GuardedTextInput(qobject_cast<QQuickTextInput*>(object));
    if (name == QStringLiteral("QQuickItem")) {
        auto* item = qobject_cast<QQuickItem*>(object);
        if (item && QQuickItemPrivate::get(item)->isAccessible)
            return new QuickItemWithMenu(item);
    }
    return nullptr;
}
}

class WindowAccessibilityPlugin final : public QQmlExtensionPlugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
    void registerTypes(const char* uri) override {
        // QCoreApplication teardown clears Qt's constructor-installed factories.
        // A QML plugin runs after Quickshell has created its lasting GUI app.
        const auto built = QString::fromLatin1(QT_VERSION_STR);
        const auto runtime = QString::fromLatin1(qVersion());
        if (runtime != built) {
            qWarning("WindowAccessibility must be rebuilt for this Qt version");
            qmlRegisterModule(uri, 1, 0);
            return;
        }
        QAccessible::installFactory(&quickFactory);
        // Quickshell currently destroys RootWrapper after deleting its GUI app.
        // Remove stored Quick focus while the input-method service is alive.
        // This is a scoped workaround; correct upstream ownership order remains
        // the stronger fix for other engine/application teardown dependencies.
        static bool shutdownHookInstalled = false;
        if (!shutdownHookInstalled && qGuiApp) {
            shutdownHookInstalled = true;
            QObject::connect(qGuiApp, &QCoreApplication::aboutToQuit,
                             qGuiApp, [] { clearQuickShutdownFocus(); },
                             Qt::DirectConnection);
        }
        qmlRegisterSingletonType<ActionState>(uri,1,0,"ActionState",[](QQmlEngine*,QJSEngine*)->QObject* {return new ActionState;});
        qmlRegisterModule(uri, 1, 0);
    }
};

#include "bridge.moc"

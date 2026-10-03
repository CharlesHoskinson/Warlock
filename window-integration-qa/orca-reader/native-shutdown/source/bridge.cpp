// Qt Quick factory dispatch adapted from Qt 6.11.2 qquickaccessiblefactory.cpp.
// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LGPL-3.0-only
#include <QQmlExtensionPlugin>
#include <QAccessible>
#include <QGuiApplication>
#include "shutdownfocus.h"
#include <QtQuick/private/qaccessiblequickview_p.h>
#include <QtQuick/private/qaccessiblequickitem_p.h>
#include <QtQuick/private/qaccessiblequicktextedit_p.h>
#include <QtQuick/private/qaccessiblequicktextinput_p.h>
#include <QtQuick/private/qquickitem_p.h>
#include <QtQuick/private/qquicktextedit_p.h>
#include <QtQuick/private/qquicktextinput_p.h>

namespace {
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
        if (action == QAccessibleActionInterface::showMenuAction()) {
            const auto current = state();
            if (hasMenu() && !current.invisible && !current.disabled)
                QMetaObject::invokeMethod(object(), "accessibleShowMenu", Qt::DirectConnection);
            return;
        }
        QAccessibleQuickItem::doAction(action);
    }
};

QAccessibleInterface* quickFactory(const QString& name, QObject* object) {
    if (name == QStringLiteral("QQuickWindow"))
        return new QAccessibleQuickWindow(qobject_cast<QQuickWindow*>(object));
    if (name == QStringLiteral("QQuickTextEdit"))
        return new QAccessibleQuickTextEdit(qobject_cast<QQuickTextEdit*>(object));
    if (name == QStringLiteral("QQuickTextInput"))
        return new QAccessibleQuickTextInput(qobject_cast<QQuickTextInput*>(object));
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
        qmlRegisterModule(uri, 1, 0);
    }
};

#include "bridge.moc"

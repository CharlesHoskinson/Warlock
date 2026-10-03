#include "source/shutdownfocus.h"
#include <QTimer>
#include <QDebug>
#include <cassert>
#include <cstdio>
#include <QPluginLoader>
#include <QQmlExtensionPlugin>

int main(int argc, char** argv) {
    auto* app = new QGuiApplication(argc, argv);
    QPluginLoader loader(QString::fromLocal8Bit(argv[1]));
    auto* plugin = qobject_cast<QQmlExtensionPlugin*>(loader.instance());
    if (!plugin) { fprintf(stderr, "%s\n", qPrintable(loader.errorString())); return 2; }
    plugin->registerTypes("WindowAccessibilityV4");
    auto* window = new QQuickWindow();
    window->setGeometry(0, 0, 120, 120);
    auto* scope = new QQuickItem(window->contentItem());
    scope->setFlag(QQuickItem::ItemIsFocusScope, true);
    auto* leaf = new QQuickItem(scope);
    window->show();
    window->requestActivate();
    app->processEvents();
    leaf->forceActiveFocus();
    app->processEvents();
    assert(window->activeFocusItem() == leaf);
    assert(leaf->hasActiveFocus());
    QTimer::singleShot(0, app, &QCoreApplication::quit);
    const int code = app->exec();
    assert(!leaf->hasFocus() && !scope->hasFocus());
    assert(!window->contentItem()->hasFocus());
    assert(!window->activeFocusItem());
    fprintf(stderr, "loaded V4 shutdown hook cleared focus leaf/scope/content before GUI app teardown\n");
    delete app;
    // Match the observed Quickshell ownership order, with shutdown cleanup.
    delete window;
    fprintf(stderr, "Quick window/item teardown completed after GUI app deletion\n");
    return code;
}

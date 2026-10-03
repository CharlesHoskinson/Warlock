#include <QGuiApplication>
#include <QQuickWindow>
#include <QAccessible>
#include <QTimer>
#include <QDebug>
#include <cstdio>

int main(int argc, char** argv) {
    if (argc > 1) {
        auto* initial = new QCoreApplication(argc, argv);
        delete initial;
    }
    QGuiApplication app(argc, argv);
    QQuickWindow window;
    window.setTitle("Native accessibility probe");
    window.resize(160, 80);
    window.show();
    QTimer::singleShot(500, [&] {
        auto* wi = QAccessible::queryAccessibleInterface(&window);
        auto* ai = QAccessible::queryAccessibleInterface(&app);
        fprintf(stderr, "active=%d window-interface=%p application-children=%d\n",
                QAccessible::isActive(), static_cast<void*>(wi), ai ? ai->childCount() : -1);
    });
    QTimer::singleShot(3000, &app, &QGuiApplication::quit);
    return app.exec();
}

#pragma once
#include <QGuiApplication>
#include <QQuickItem>
#include <QQuickWindow>

inline void clearItemShutdownFocus(QQuickItem* item) {
    // Inactive focus scopes can retain subFocusItem even after the active leaf
    // loses focus. Clear every focused descendant before its containing scope.
    const auto children = item->childItems();
    for (auto* child : children) clearItemShutdownFocus(child);
    if (item->hasFocus() || item->hasActiveFocus())
        item->setFocus(false, Qt::OtherFocusReason);
}
inline void clearQuickShutdownFocus() {
    for (auto* window : QGuiApplication::allWindows()) {
        if (auto* quick = qobject_cast<QQuickWindow*>(window)) {
            if (auto* content = quick->contentItem())
                clearItemShutdownFocus(content);
        }
    }
}

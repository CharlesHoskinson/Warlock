#pragma once
#include "Lifetime.hpp"
#include <QObject>
class ObjectLifetimeProvider final:public QObject {
 Q_OBJECT
 QPointer<QQmlEngine>engine;
 Lifetime::Authority source();
 void stable(const Lifetime::Authority&);
public:
 explicit ObjectLifetimeProvider(QQmlEngine*e):engine(e){}
 Q_INVOKABLE QVariantMap engineScope();
 Q_INVOKABLE QVariantMap armProcess(QObject*menu,QObject*row,QObject*popup,QObject*process,QObject*out,QObject*err,const QString&role,const QString&originalJSON,QObject*actualQuickshell);
 Q_INVOKABLE QVariantMap processState(QObject*process,QObject*actualQuickshell);
 Q_INVOKABLE QVariantMap cancelProcess(QObject*process,QObject*actualQuickshell);
 Q_INVOKABLE QVariantMap observePopup(QQuickItem*menu,QQuickItem*row,QObject*popup,QObject*actualQuickshell);
 Q_INVOKABLE QVariantMap observe(QQuickItem*widget,QQuickItem*delegate,QObject*actualQuickshell);
};

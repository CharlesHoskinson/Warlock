#pragma once
#include <QObject>
#include <functional>
class ReloadRelay final:public QObject{
 Q_OBJECT
 const std::function<void()>boundary;
public:
 ReloadRelay(QObject*parent,std::function<void()>fn):QObject(parent),boundary(std::move(fn)){}
public slots:
 void completed(){boundary();}
 void failed(const QString&){boundary();}
};

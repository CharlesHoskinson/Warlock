#pragma once
#include <QObject>
#include <QProcess>
#include <functional>
class ProcessRelay final:public QObject {
 Q_OBJECT
 std::function<void(int,int,QProcess::ExitStatus)>observer;
public:
 ProcessRelay(QObject*p,std::function<void(int,int,QProcess::ExitStatus)>f):QObject(p),observer(std::move(f)){}
public slots:
 void started(){observer(0,0,QProcess::NormalExit);}
 void exited(int code,QProcess::ExitStatus status){observer(1,code,status);}
 void outFinished(){observer(2,0,QProcess::NormalExit);}
 void errFinished(){observer(3,0,QProcess::NormalExit);}
};

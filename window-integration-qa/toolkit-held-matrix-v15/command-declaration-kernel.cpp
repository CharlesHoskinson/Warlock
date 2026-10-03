// CPU QCoreApplication/QProcess only. No GUI, QS, compositor or plugin load.
#include <QCoreApplication>
#include <QProcess>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <cstdio>
int main(int argc,char** argv) {
 QCoreApplication app(argc,argv);
 QStringList declared={"/usr/bin/python3","-IS","-c","import sys;print('ready',flush=True);sys.stdin.read()","submitted-original"};
 const auto submitted=declared;QProcess child;QStringList declaredAtStart; qint64 pid=0;
 QObject::connect(&child,&QProcess::started,[&]{declaredAtStart=declared;pid=child.processId();});
 child.start(declared.first(),declared.sliced(1));declared.last()="declared-next";
 if(!child.waitForStarted(3000)||pid<=0)return 2;
 QFile proc(QString("/proc/%1/cmdline").arg(pid));if(!proc.open(QIODevice::ReadOnly))return 3;
 const auto raw=proc.readAll();QStringList actual;for(auto x:raw.split('\0'))if(!x.isEmpty())actual.append(QString::fromUtf8(x));
 bool preserved=actual==submitted,mutableChanged=declaredAtStart==declared&&declaredAtStart!=submitted;
 child.closeWriteChannel();if(!child.waitForFinished(3000))return 4;
 const auto stdoutBytes=child.readAllStandardOutput(),stderrBytes=child.readAllStandardError();
 QJsonObject row{{"actualPID",pid},{"submittedDeclaration",QJsonArray::fromStringList(submitted)},{"declarationAtStarted",QJsonArray::fromStringList(declaredAtStart)},{"actualKernelArgv",QJsonArray::fromStringList(actual)},{"kernelArgvPreserved",preserved},{"declarationChangedAtStarted",mutableChanged},{"exitCode",child.exitCode()},{"exitStatus",int(child.exitStatus())},{"stdout",QString::fromUtf8(stdoutBytes)},{"stderr",QString::fromUtf8(stderrBytes)},{"QCoreOnly",true},{"actualQuickshellExecuted",false}};
 auto out=QJsonDocument(row).toJson(QJsonDocument::Compact);fwrite(out.constData(),1,out.size(),stdout);fputc('\n',stdout);
 return preserved&&mutableChanged&&child.exitCode()==0&&child.exitStatus()==QProcess::NormalExit&&stdoutBytes=="ready\n"&&stderrBytes.isEmpty()?0:5;
}

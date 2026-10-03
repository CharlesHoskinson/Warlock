#include <QCoreApplication>
#include <QQmlEngine>
#include <QQmlComponent>
#include <QJSValue>
#include <QJsonDocument>
#include <QUrl>
#include <cstdio>
int main(int argc,char**argv) {
    QCoreApplication app(argc,argv); // No GUI application, display or window.
    if(argc!=3)return 2;
    QQmlEngine engine;
    QQmlComponent component(&engine,QUrl::fromLocalFile(argv[1]));
    auto object=component.create();
    if(!object){for(const auto&e:component.errors())fprintf(stderr,"%s\n",qPrintable(e.toString()));return 3;}
    auto wrapper=engine.newQObject(object);
    auto result=wrapper.property("runCase").call({QJSValue(QString::fromLocal8Bit(argv[2]))});
    if(result.isError()){fprintf(stderr,"%s\n",qPrintable(result.toString()));return 4;}
    const auto doc=QJsonDocument::fromVariant(result.toVariant());
    if(doc.isNull())return 5;
    const auto bytes=doc.toJson(QJsonDocument::Compact);puts(bytes.constData());
    return result.property("ok").toBool()?0:6;
}

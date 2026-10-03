#include <QCoreApplication>
#include <QJSEngine>
#include <QFile>
#include <QTextStream>
int main(int argc,char**argv){
 QCoreApplication app(argc,argv);if(argc!=3)return 2;
 QJSEngine engine;
 auto eval=[&](const QString&source){auto value=engine.evaluate(source);if(value.isError()){QTextStream(stderr)<<value.toString()<<"\n";return false;}return true;};
 if(!eval("var window={};var listeners={};var performance={timeOrigin:100,now:function(){return 200;}};var document={addEventListener:function(type,fn,capture){var k=type+':'+(capture?'capture':'bubble');(listeners[k]||(listeners[k]=[])).push(fn);}};"))return 3;
 for(int i=1;i<3;++i){QFile file(argv[i]);if(!file.open(QIODevice::ReadOnly))return 4;if(!eval(QString::fromUtf8(file.readAll())))return 5;}
 auto value=engine.evaluate("JSON.stringify(testResult)");if(value.isError())return 6;
 QTextStream(stdout)<<value.toString()<<"\n";return 0;
}

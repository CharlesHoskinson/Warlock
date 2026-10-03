#include <QCoreApplication>
#include <QFile>
#include <QJSEngine>
#include <iostream>
int main(int argc,char**argv){QCoreApplication app(argc,argv);if(argc!=3)return 2;QJSEngine js;
 for(int i=1;i<3;++i){QFile f(argv[i]);if(!f.open(QIODevice::ReadOnly))return 3;QString source=QString::fromUtf8(f.readAll());if(i==1)source.remove(".pragma library");auto r=js.evaluate(source,argv[i]);if(r.isError()){std::cerr<<r.toString().toStdString()<<" line "<<r.property("lineNumber").toInt()<<"\n";return 1;}if(i==2)std::cout<<r.toString().toStdString()<<"\n";}
}

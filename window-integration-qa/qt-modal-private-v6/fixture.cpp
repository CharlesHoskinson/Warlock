#include <QApplication>
#include <QDateTime>
#include <QDialog>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QPointer>
#include <QPushButton>
#include <QSaveFile>
#include <QTimer>
#include <QVBoxLayout>
#include <QWidget>
#include <QWindow>
#include <QEvent>

class Probe final : public QObject {
  QString output;
  QMap<QString,QPointer<QWidget>> windows;
  QMap<QString,int> clicks;
  qint64 commandEpoch=-1;
  void record(QJsonObject value) {
    value["timeMS"]=QDateTime::currentMSecsSinceEpoch();
    QFile f(output+"/events.jsonl");if(f.open(QIODevice::WriteOnly|QIODevice::Append))f.write(QJsonDocument(value).toJson(QJsonDocument::Compact)+"\n");
  }
  void saveState() {
    QJsonObject rows;
    for(auto it=windows.begin();it!=windows.end();++it) {
      auto* widget=it.value().data();if(!widget)continue;
      auto* native=widget->windowHandle();auto* transient=native ? native->transientParent() : nullptr;
      const auto origin=widget->mapToGlobal(QPoint(0,0));auto* button=widget->findChild<QPushButton*>(it.key()+"Button");const auto buttonOrigin=button ? button->mapToGlobal(QPoint(0,0)) : QPoint();const auto buttonClient=button ? button->mapTo(widget,QPoint(0,0)) : QPoint();
      rows[it.key()]=QJsonObject{{"visible",widget->isVisible()},{"modality",int(widget->windowModality())},{"native",native!=nullptr},{"transientParentTitle",transient ? transient->title() : QString()},{"clicks",clicks.value(it.key())},{"active",widget->isActiveWindow()},{"enabled",widget->isEnabled()},{"geometryGlobal",QJsonArray{origin.x(),origin.y(),widget->width(),widget->height()}},{"buttonGlobal",QJsonArray{buttonOrigin.x(),buttonOrigin.y(),button ? button->width() : 0,button ? button->height() : 0}},{"buttonClient",QJsonArray{buttonClient.x(),buttonClient.y(),button ? button->width() : 0,button ? button->height() : 0}}};
    }
    auto* active=QApplication::activeWindow();
    QJsonObject state{{"pid",qint64(QCoreApplication::applicationPid())},{"qtVersion",QString::fromLatin1(qVersion())},{"platform",QGuiApplication::platformName()},{"windows",rows},{"activeWindow",active ? active->objectName() : QString()},{"commandEpoch",commandEpoch}};
    QSaveFile file(output+"/state.json");if(file.open(QIODevice::WriteOnly)){file.write(QJsonDocument(state).toJson(QJsonDocument::Indented));file.commit();}
  }
  QWidget* create(QString name,QWidget* parent=nullptr) {
    QWidget* widget=parent ? static_cast<QWidget*>(new QDialog(parent)) : new QWidget;
    widget->setObjectName(name);widget->setWindowTitle("Qt WindowModal QA "+name);widget->resize(parent ? QSize(320,180) : QSize(460,300));
    widget->setAttribute(Qt::WA_DeleteOnClose);auto* layout=new QVBoxLayout(widget);auto* button=new QPushButton(name+": record actual click",widget);button->setObjectName(name+"Button");layout->addWidget(button);
    connect(button,&QPushButton::clicked,this,[this,name]{clicks[name]++;record({{"event","buttonClicked"},{"window",name},{"count",clicks[name]}});saveState();});
    connect(widget,&QObject::destroyed,this,[this,name]{record({{"event","destroyed"},{"window",name}});QTimer::singleShot(0,this,[this]{saveState();});});
    widget->installEventFilter(this);button->installEventFilter(this);windows[name]=widget;clicks[name]=0;return widget;
  }
  void openDialog(QString name,QString parent) {
    if(windows.value(name))return;
    auto* owner=windows.value(parent).data();if(!owner){record({{"event","commandError"},{"error","missing parent"},{"window",name}});return;}
    auto* dialog=static_cast<QDialog*>(create(name,owner));dialog->open();
    record({{"event","dialogOpened"},{"window",name},{"parent",parent},{"modality",int(dialog->windowModality())}});
  }
  void poll() {
    QFile file(output+"/command.json");if(!file.open(QIODevice::ReadOnly))return;
    auto doc=QJsonDocument::fromJson(file.readAll());if(!doc.isObject())return;auto command=doc.object();auto epoch=qint64(command["epoch"].toDouble(-1));if(epoch<=commandEpoch)return;commandEpoch=epoch;
    auto name=command["command"].toString();
    if(name=="open")openDialog("child","owner");
    else if(name=="nested")openDialog("nested","child");
    else if(name=="closeNested"){if(windows.value("nested"))windows["nested"]->close();}
    else if(name=="closeChild"){if(windows.value("child"))windows["child"]->close();}
    else if(name=="destroyOwner"){if(windows.value("owner"))delete windows["owner"].data();}
    else if(name=="quit")QCoreApplication::quit();
    else record({{"event","commandError"},{"command",name}});
    record({{"event","commandHandled"},{"command",name},{"epoch",epoch}});QTimer::singleShot(0,this,[this]{saveState();});
  }
protected:
  bool eventFilter(QObject* object,QEvent* event) override {
    if(event->type()==QEvent::WindowActivate || event->type()==QEvent::WindowDeactivate || event->type()==QEvent::MouseButtonPress || event->type()==QEvent::MouseButtonRelease || event->type()==QEvent::KeyPress) {
      record({{"event","qtInput"},{"object",object->objectName()},{"eventType",int(event->type())},{"spontaneous",event->spontaneous()}});
      QTimer::singleShot(0,this,[this]{saveState();});
    }
    return QObject::eventFilter(object,event);
  }
public:
  explicit Probe(QString directory):output(std::move(directory)) {
    QApplication::setQuitOnLastWindowClosed(false);create("owner")->show();create("peer")->show();
    auto* timer=new QTimer(this);timer->setInterval(40);connect(timer,&QTimer::timeout,this,[this]{poll();});timer->start();QTimer::singleShot(0,this,[this]{saveState();});
  }
};
int main(int argc,char** argv){QApplication app(argc,argv);if(argc!=2)return 2;Probe probe(QString::fromLocal8Bit(argv[1]));return app.exec();}

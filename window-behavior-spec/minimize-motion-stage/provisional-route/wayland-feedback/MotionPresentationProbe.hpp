#pragma once
#include <QQuickItem>
#include <QQuickWindow>
#include <QScreen>
#include <QPointer>
#include <QGuiApplication>
#include <qpa/qplatformnativeinterface.h>
#include <optional>
#include "WaylandPresentation.hpp"
class MotionPresentationProbe : public QQuickItem {
 Q_OBJECT
 Q_PROPERTY(QVariantMap frameData READ frameData WRITE setFrameData NOTIFY frameDataChanged)
 Q_PROPERTY(QQuickItem* observedItem READ observedItem WRITE setObservedItem NOTIFY observedItemChanged)
 QPointer<QQuickItem> observed;
 QVariantMap fields;
 struct State {
  std::shared_ptr<PresentationLedger> ledger=std::make_shared<PresentationLedger>();
  QMutex mutex;
  std::optional<PresentationLedger::Frame> frame;
  wl_surface* surface=nullptr;wl_output* output=nullptr;
 };
 std::shared_ptr<State> state=std::make_shared<State>();
 std::shared_ptr<WaylandPresentation> service;
 QMetaObject::Connection syncConnection,renderConnection;
 static std::shared_ptr<WaylandPresentation> manager() {
  // Construct on GUI thread; retain for process lifetime, stop before display
  // shutdown. Render callbacks retain shared state and never use a dead item.
  static std::shared_ptr<WaylandPresentation> instance;
  if(!instance) {
   auto* native=QGuiApplication::platformNativeInterface();
   auto* display=native?static_cast<wl_display*>(native->nativeResourceForIntegration("display")):nullptr;
   instance=std::make_shared<WaylandPresentation>(QGuiApplication::platformName()=="wayland"?display:nullptr);
   const auto keep=instance;
   QObject::connect(qApp,&QCoreApplication::aboutToQuit,qApp,[keep]{keep->stop();});
   auto* timer=new QTimer(qApp);timer->setInterval(1000);QObject::connect(timer,&QTimer::timeout,qApp,[keep]{keep->expire();});timer->start();
  }
  return instance;
 }
 void attach(QQuickWindow* window) {
  QObject::disconnect(syncConnection);QObject::disconnect(renderConnection);
  const auto generation=state->ledger->replaceWindow();{QMutexLocker lock(&state->mutex);state->frame.reset();state->surface=nullptr;state->output=nullptr;}
  if(!window)return;const auto captured=state;const auto backend=service;
  syncConnection=QObject::connect(window,&QQuickWindow::beforeSynchronizing,this,[this,window,captured,generation]{
   // GUI is blocked while Qt emits beforeSynchronizing. QPA resource handles,
   // image source/status and public item geometry are sampled for this frame.
   auto* native=QGuiApplication::platformNativeInterface();auto* screen=window->screen();
   auto* surface=native?static_cast<wl_surface*>(native->nativeResourceForWindow("surface",window)):nullptr;
   auto* output=native && screen?static_cast<wl_output*>(native->nativeResourceForScreen("output",screen)):nullptr;
   QVariantMap rect;QString source;bool ready=false;
   if(observed && observed->isVisible() && observed->opacity()>0 && screen && screen->name()==fields.value("output").toString()) {
    const auto r=observed->mapRectToScene(QRectF(0,0,observed->width(),observed->height()));
    rect={{"x",r.x()},{"y",r.y()},{"width",r.width()},{"height",r.height()}};
    source=observed->property("source").toUrl().toString();ready=observed->property("status").toInt()==1;
   }
   auto frame=captured->ledger->synchronize(generation,rect,source,ready);QMutexLocker lock(&captured->mutex);captured->frame=std::move(frame);captured->surface=surface;captured->output=output;
  },Qt::DirectConnection);
  renderConnection=QObject::connect(window,&QQuickWindow::afterRendering,this,[captured,backend]{
   QMutexLocker lock(&captured->mutex);if(!captured->frame)return;
   backend->request(captured->surface,captured->output,captured->ledger,*captured->frame);captured->frame.reset();
  },Qt::DirectConnection);
 }
public:
 explicit MotionPresentationProbe(QQuickItem* parent=nullptr):QQuickItem(parent),service(manager()) {
  setFlag(ItemHasContents,false);setAcceptedMouseButtons(Qt::NoButton);setAcceptHoverEvents(false);setActiveFocusOnTab(false);
  QObject::connect(this,&QQuickItem::windowChanged,this,[this](QQuickWindow* w){attach(w);});if(window())attach(window());
 }
 ~MotionPresentationProbe()override {QObject::disconnect(syncConnection);QObject::disconnect(renderConnection);state->ledger->replaceWindow();}
 QVariantMap frameData()const{return fields;}
 void setFrameData(const QVariantMap& f){fields=f;state->ledger->setInputs(f);emit frameDataChanged();}
 QQuickItem* observedItem()const{return observed;}
 void setObservedItem(QQuickItem* i){if(i==observed)return;observed=i;emit observedItemChanged();}
 Q_INVOKABLE QVariantList allFramesAfter(quint64 sequence=0)const{return service->framesAfter(sequence);}
 Q_INVOKABLE QVariantList framesAfter(quint64 sequence=0)const{return state->ledger->after(sequence);}
signals:
 void frameDataChanged();
 void observedItemChanged();
};

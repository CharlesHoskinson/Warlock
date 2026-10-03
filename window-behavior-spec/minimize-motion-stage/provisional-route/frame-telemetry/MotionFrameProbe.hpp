#pragma once
#include <QQuickItem>
#include <QQuickWindow>
#include <QMetaObject>
#include <QPointer>
#include <chrono>
#include <memory>
#include "FrameLedger.hpp"
class MotionFrameProbe : public QQuickItem {
 Q_OBJECT
 Q_PROPERTY(QVariantMap frameData READ frameData WRITE setFrameData NOTIFY frameDataChanged)
 Q_PROPERTY(QQuickItem* observedItem READ observedItem WRITE setObservedItem NOTIFY observedItemChanged)
 QPointer<QQuickItem> observed;
 struct State {
  FrameLedger ledger;
  const std::chrono::steady_clock::time_point origin=std::chrono::steady_clock::now();
  double now()const {return std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-origin).count();}
 };
 std::shared_ptr<State> state=std::make_shared<State>();
 QMetaObject::Connection syncConnection,swapConnection;
 void attach(QQuickWindow* window) {
  QObject::disconnect(syncConnection);QObject::disconnect(swapConnection);
  const quint64 generation=state->ledger.replaceWindow();if(!window)return;
  const auto captured=state;
  // A direct render-thread callback can overlap GUI destruction. It retains
  // only shared plain state; it never dereferences the QQuickItem afterward.
  syncConnection=QObject::connect(window,&QQuickWindow::beforeSynchronizing,this,[this,captured,generation]{
   // Qt blocks the GUI thread during this signal. Reading the observed item's
   // public frontend geometry here cannot overlap GUI mutation/destruction.
   QVariantMap rect;if(observed) {
    const auto r=observed->mapRectToScene(QRectF(0,0,observed->width(),observed->height()));
    rect={{"x",r.x()},{"y",r.y()},{"width",r.width()},{"height",r.height()},{"visible",observed->isVisible()},{"opacity",observed->opacity()}};
   }
   captured->ledger.synchronize(generation,captured->now(),rect);
  },Qt::DirectConnection);
  swapConnection=QObject::connect(window,&QQuickWindow::frameSwapped,this,[captured,generation]{captured->ledger.swapped(generation,captured->now());},Qt::DirectConnection);
 }
public:
 explicit MotionFrameProbe(QQuickItem* parent=nullptr):QQuickItem(parent) {
  setFlag(ItemHasContents,false);setAcceptedMouseButtons(Qt::NoButton);setAcceptHoverEvents(false);setActiveFocusOnTab(false);
  QObject::connect(this,&QQuickItem::windowChanged,this,[this](QQuickWindow* window){attach(window);});if(window())attach(window());
 }
 ~MotionFrameProbe()override {QObject::disconnect(syncConnection);QObject::disconnect(swapConnection);state->ledger.replaceWindow();}
 QVariantMap frameData()const {return state->ledger.getInputs();}
 QQuickItem* observedItem()const {return observed;}
 void setObservedItem(QQuickItem* item) {if(observed==item)return;observed=item;emit observedItemChanged();}
 void setFrameData(const QVariantMap& data) {state->ledger.setInputs(data);emit frameDataChanged();}
 Q_INVOKABLE QVariantList framesAfter(quint64 sequence=0)const {return state->ledger.after(sequence);}
signals:
 void frameDataChanged();
 void observedItemChanged();
};

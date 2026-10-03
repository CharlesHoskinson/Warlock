#pragma once
#include <QObject>
#include <QGuiApplication>
#include <QTimer>
#include <QMutex>
#include <QMutexLocker>
#include <wayland-client.h>
#include <unordered_map>
#include <memory>
#include <chrono>
#include "presentation-time-client-protocol.h"
#include "PresentationLedger.hpp"
// Qt dispatches the default Wayland event queue. No extra reader or roundtrip.
class WaylandPresentation {
 struct Pending {
  WaylandPresentation* owner;
  std::shared_ptr<PresentationLedger> ledger;
  PresentationLedger::Frame frame;
  struct wp_presentation_feedback* proxy;
  wl_output* expectedOutput;
  bool outputMatches=false;
  std::chrono::steady_clock::time_point requested=std::chrono::steady_clock::now();
 };
 QMutex mutex;
 wl_registry* registry=nullptr;
 wp_presentation* presentation=nullptr;
 uint32_t globalName=0,clockId=0;
 bool hasClock=false,active=true;quint64 observationSequence=0;QVariantList history;
 std::unordered_map<struct wp_presentation_feedback*,std::unique_ptr<Pending>> pending;
 static void global(void* data,wl_registry* registry,uint32_t name,const char* interface,uint32_t version) {
  auto* self=static_cast<WaylandPresentation*>(data);QMutexLocker lock(&self->mutex);
  if(self->active && !self->presentation && std::string(interface)=="wp_presentation") {
   self->globalName=name;self->presentation=static_cast<wp_presentation*>(wl_registry_bind(registry,name,&wp_presentation_interface,std::min(version,uint32_t(1))));
   static const wp_presentation_listener listener={clock};wp_presentation_add_listener(self->presentation,&listener,self);
  }
 }
 static void globalRemove(void* data,wl_registry*,uint32_t name) {
  auto* self=static_cast<WaylandPresentation*>(data);QMutexLocker lock(&self->mutex);
  if(name==self->globalName) {self->clearPending();if(self->presentation)wp_presentation_destroy(self->presentation);self->presentation=nullptr;self->hasClock=false;}
 }
 static void clock(void* data,wp_presentation*,uint32_t id) {auto* self=static_cast<WaylandPresentation*>(data);QMutexLocker lock(&self->mutex);self->clockId=id;self->hasClock=true;}
 static void output(void* data,struct wp_presentation_feedback*,wl_output* output) {auto* p=static_cast<Pending*>(data);QMutexLocker lock(&p->owner->mutex);p->outputMatches=p->outputMatches || output==p->expectedOutput;}
 static void presented(void* data,struct wp_presentation_feedback* proxy,uint32_t hi,uint32_t lo,uint32_t ns,uint32_t,uint32_t seqHi,uint32_t seqLo,uint32_t flags) {
  auto* p=static_cast<Pending*>(data);auto* self=p->owner;QMutexLocker lock(&self->mutex);
  if(self->active && self->hasClock && p->ledger->presented(p->frame,(uint64_t(hi)<<32)|lo,ns,(uint64_t(seqHi)<<32)|seqLo,flags,self->clockId,p->outputMatches)) {
   auto row=p->ledger->after(p->frame.sequence-1).last().toMap();row.insert("observerSequence",QVariant::fromValue(++self->observationSequence));self->history.append(row);if(self->history.size()>512)self->history.removeFirst();
  }
  wp_presentation_feedback_destroy(proxy);self->pending.erase(proxy);
 }
 static void discarded(void* data,struct wp_presentation_feedback* proxy) {auto* p=static_cast<Pending*>(data);auto* self=p->owner;QMutexLocker lock(&self->mutex);wp_presentation_feedback_destroy(proxy);self->pending.erase(proxy);}
 void clearPending() {for(const auto& [proxy,p]:pending)wp_presentation_feedback_destroy(proxy);pending.clear();}
public:
 explicit WaylandPresentation(wl_display* display) {
  if(!display){active=false;return;}registry=wl_display_get_registry(display);
  static const wl_registry_listener listener={global,globalRemove};wl_registry_add_listener(registry,&listener,this);
 }
 ~WaylandPresentation(){stop();}
 void stop() {QMutexLocker lock(&mutex);active=false;clearPending();if(presentation)wp_presentation_destroy(presentation);presentation=nullptr;if(registry)wl_registry_destroy(registry);registry=nullptr;hasClock=false;}
 QVariantList framesAfter(quint64 seq) {QMutexLocker lock(&mutex);QVariantList result;for(const auto& row:history)if(row.toMap().value("observerSequence").toULongLong()>seq)result.append(row);return result;}
 void expire() {QMutexLocker lock(&mutex);const auto now=std::chrono::steady_clock::now();for(auto it=pending.begin();it!=pending.end();)if(now-it->second->requested>std::chrono::seconds(2)){wp_presentation_feedback_destroy(it->first);it=pending.erase(it);}else ++it;}
 bool request(wl_surface* surface,wl_output* output,const std::shared_ptr<PresentationLedger>& ledger,const PresentationLedger::Frame& frame) {
  QMutexLocker lock(&mutex);if(!active || !presentation || !hasClock || !surface || !output || pending.size()>=128)return false;
  auto* proxy=wp_presentation_feedback(presentation,surface);auto p=std::make_unique<Pending>(Pending{this,ledger,frame,proxy,output});
  static const wp_presentation_feedback_listener listener={WaylandPresentation::output,presented,discarded};wp_presentation_feedback_add_listener(proxy,&listener,p.get());pending.emplace(proxy,std::move(p));return true;
 }
};

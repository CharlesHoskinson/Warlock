#pragma once
#include <QVariantMap>
#include <QVariantList>
#include <QMutex>
#include <QMutexLocker>
#include <QRegularExpression>
#include <cmath>
#include <optional>
class FrameLedger {
 mutable QMutex mutex;
 QVariantMap inputs;
 struct Pending {quint64 generation,sequence;double time;QVariantMap fields;};
 std::optional<Pending> pending;
 quint64 generation=0,sequence=0,lastSwapped=0;
 QVariantList records;
 static bool valid(const QVariantMap& f) {
  const auto identity=f.value("identity").toList();const auto rect=f.value("rect").toMap();
  if(identity.size()!=3 || !QRegularExpression("^0x[a-fA-F0-9]+$").match(identity[0].toString()).hasMatch() || !QRegularExpression("^[a-fA-F0-9]+$").match(identity[1].toString()).hasMatch() || identity[2].toLongLong()<=0)return false;
  if(!QRegularExpression("^[a-f0-9]{12}-[1-9][0-9]*$").match(f.value("token").toString()).hasMatch() || !QRegularExpression("^[a-f0-9]{64}$").match(f.value("digest").toString()).hasMatch() || f.value("output").toString().isEmpty())return false;
  for(const auto& name:{"x","y","width","height"}) {bool ok=false;const auto value=rect.value(name).toDouble(&ok);if(!ok || !std::isfinite(value) || ((QString(name)=="width" || QString(name)=="height") && value<=0))return false;}
  bool ok=false;const auto progress=f.value("progress").toDouble(&ok);return ok && std::isfinite(progress) && progress>=0 && progress<=1 && f.value("active").toBool() && f.value("imageReady").toBool();
 }
public:
 void setInputs(const QVariantMap& fields) {
  // Convert only known scalar fields on the GUI thread. Never retain arbitrary
  // QObject/QJSValue payloads for later destruction on the render thread.
  const auto id=fields.value("identity").toList();const auto raw=fields.value("rect").toMap();QVariantMap rect;
  for(const auto& key:{"x","y","width","height"})rect.insert(key,raw.value(key).toDouble());
  QVariantMap clean={{"token",fields.value("token").toString()},{"digest",fields.value("digest").toString()},{"output",fields.value("output").toString()},{"rect",rect},{"progress",fields.value("progress").toDouble()},{"active",fields.value("active").toBool()},{"imageReady",fields.value("imageReady").toBool()}};
  if(id.size()==3)clean.insert("identity",QVariantList{id[0].toString(),id[1].toString(),id[2].toLongLong()});
  QMutexLocker guard(&mutex);inputs=valid(fields)?clean:QVariantMap{};
 }
 QVariantMap getInputs()const {QMutexLocker guard(&mutex);return inputs;}
 quint64 replaceWindow() {QMutexLocker guard(&mutex);pending.reset();return ++generation;}
 bool synchronize(quint64 observedGeneration,double time,const QVariantMap& sceneRect={}) {
  QMutexLocker guard(&mutex);if(observedGeneration!=generation)return false;
  if(!std::isfinite(time) || !valid(inputs)){pending.reset();return false;}
  auto fields=inputs;if(!sceneRect.isEmpty())fields.insert("synchronizedItemSceneRect",sceneRect);
  pending=Pending{generation,++sequence,time,fields};return true;
 }
 bool swapped(quint64 observedGeneration,double time) {
  QMutexLocker guard(&mutex);if(observedGeneration!=generation || !pending || pending->generation!=generation || pending->sequence<=lastSwapped || !std::isfinite(time) || time<pending->time)return false;
  auto row=pending->fields;
  // Deliberately different keys from the coordinator's pixel presentation
  // boundary: raw Qt queued-frame telemetry cannot be forwarded as present().
  row.insert("expectedAtlasDigest",row.take("digest"));row.insert("expectedIdentity",row.take("identity"));row.insert("expectedGlobalRect",row.take("rect"));
  row.insert("sequence",QVariant::fromValue(pending->sequence));row.insert("windowGeneration",QVariant::fromValue(generation));row.insert("syncTimeMs",pending->time);row.insert("queuedTimeMs",time);row.insert("observation","qt-frame-queued");row.insert("pixelProof",false);
  lastSwapped=pending->sequence;records.append(row);if(records.size()>512)records.removeFirst();return true;
 }
 QVariantList after(quint64 afterSequence)const {QMutexLocker guard(&mutex);QVariantList result;for(const auto& row:records)if(row.toMap().value("sequence").toULongLong()>afterSequence)result.append(row);return result;}
};

#pragma once
#include <QVariantMap>
#include <QVariantList>
#include <QMutex>
#include <QMutexLocker>
#include <QRegularExpression>
#include <cmath>
#include <optional>
class PresentationLedger {
 mutable QMutex mutex;
 quint64 generation=0,next=0,lastPresented=0,lastSeconds=0;quint32 lastNs=0,lastClock=0;bool hasTime=false;
 QVariantMap inputs;
 QVariantList records;
 static bool exact(const QString& pattern,const QString& value) {return QRegularExpression("\\A(?:"+pattern+")\\z").match(value).hasMatch();}
public:
 struct Frame {quint64 generation,sequence;QVariantMap fields;};
 static bool valid(const QVariantMap& f) {
  const auto id=f.value("identity").toList();const auto rect=f.value("rect").toMap();
  if(id.size()!=3 || !exact("0x[a-fA-F0-9]+",id[0].toString()) || !exact("[a-fA-F0-9]+",id[1].toString()) || id[2].toLongLong()<=0)return false;
  if(!exact("[a-f0-9]{12}-[1-9][0-9]*",f.value("token").toString()) || !exact("[a-f0-9]{64}",f.value("digest").toString()) || f.value("output").toString().isEmpty() || !f.value("source").toString().startsWith("file:///"))return false;
  for(const auto& k:{"x","y","width","height"}) {bool ok=false;double v=rect.value(k).toDouble(&ok);if(!ok || !std::isfinite(v) || ((QString(k)=="width" || QString(k)=="height") && v<=0))return false;}
  bool ok=false;double progress=f.value("progress").toDouble(&ok);return ok && std::isfinite(progress) && progress>=0 && progress<=1 && f.value("active").toBool() && f.value("imageReady").toBool();
 }
 void setInputs(const QVariantMap& f) {
  QVariantMap c;if(valid(f)) {
   const auto id=f.value("identity").toList();const auto raw=f.value("rect").toMap();QVariantMap rect;
   for(const auto& k:{"x","y","width","height"})rect.insert(k,raw.value(k).toDouble());
   c={{"token",f.value("token").toString()},{"expectedAtlasDigest",f.value("digest").toString()},{"expectedIdentity",QVariantList{id[0].toString(),id[1].toString(),id[2].toLongLong()}},{"expectedGlobalRect",rect},{"output",f.value("output").toString()},{"progress",f.value("progress").toDouble()},{"expectedSource",f.value("source").toString()}};
  }
  QMutexLocker lock(&mutex);inputs=c;
 }
 quint64 replaceWindow() {QMutexLocker lock(&mutex);lastPresented=0;hasTime=false;return ++generation;}
 std::optional<Frame> synchronize(quint64 g,const QVariantMap& sceneRect,const QString& source,bool ready) {
  QMutexLocker lock(&mutex);if(g!=generation || inputs.isEmpty() || !ready || source!=inputs.value("expectedSource").toString() || sceneRect.isEmpty())return {};
  for(const auto& k:{"x","y","width","height"}){bool ok=false;double v=sceneRect.value(k).toDouble(&ok);if(!ok || !std::isfinite(v) || ((QString(k)=="width" || QString(k)=="height") && v<=0))return {};}
  auto c=inputs;c.insert("synchronizedItemSceneRect",sceneRect);c.insert("synchronizedSource",source);return Frame{g,++next,c};
 }
 bool presented(const Frame& frame,quint64 seconds,quint32 ns,quint64 compositorSequence,quint32 flags,quint32 clockId,bool outputMatches) {
  QMutexLocker lock(&mutex);if(frame.generation!=generation || frame.sequence<=lastPresented || ns>=1000000000 || !outputMatches || (hasTime && (clockId!=lastClock || seconds<lastSeconds || (seconds==lastSeconds && ns<=lastNs))))return false;
  auto c=frame.fields;c.insert("sequence",QVariant::fromValue(frame.sequence));c.insert("windowGeneration",QVariant::fromValue(frame.generation));c.insert("presentationSeconds",QVariant::fromValue(seconds));c.insert("presentationNanoseconds",ns);c.insert("compositorSequence",QVariant::fromValue(compositorSequence));c.insert("presentationFlags",flags);c.insert("presentationClockId",clockId);c.insert("observation","wayland-surface-presented");c.insert("pixelProof",false);
  lastPresented=frame.sequence;lastSeconds=seconds;lastNs=ns;lastClock=clockId;hasTime=true;records.append(c);if(records.size()>512)records.removeFirst();return true;
 }
 QVariantList after(quint64 seq)const {QMutexLocker lock(&mutex);QVariantList result;for(const auto& row:records)if(row.toMap().value("sequence").toULongLong()>seq)result.append(row);return result;}
};

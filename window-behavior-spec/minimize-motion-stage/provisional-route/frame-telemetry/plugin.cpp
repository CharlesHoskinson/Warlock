#include <QQmlExtensionPlugin>
#include <qqml.h>
#include "MotionFrameProbe.hpp"
class MotionFrameProbePlugin : public QQmlExtensionPlugin {
 Q_OBJECT
 Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
 void registerTypes(const char* uri)override {
  if(QString::fromLatin1(qVersion())!=QStringLiteral(QT_VERSION_STR))qFatal("MotionFrameProbe runtime Qt differs from compiled Qt");
  qmlRegisterType<MotionFrameProbe>(uri,1,0,"MotionFrameProbe");
 }
};
#include "plugin.moc"

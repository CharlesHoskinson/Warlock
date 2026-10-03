#include <QQmlExtensionPlugin>
#include <qqml.h>
#include "MotionPresentationProbe.hpp"
class MotionPresentationPlugin : public QQmlExtensionPlugin {
 Q_OBJECT
 Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
 void registerTypes(const char* uri)override {
  if(QString::fromLatin1(qVersion())!=QStringLiteral(QT_VERSION_STR))qFatal("MotionPresentationProbe requires exact compiled Qt private QPA ABI");
  qmlRegisterType<MotionPresentationProbe>(uri,1,0,"MotionPresentationProbe");
 }
};
#include "plugin.moc"

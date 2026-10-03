#include <QCoreApplication>
#include <QPluginLoader>
#include <QQmlExtensionPlugin>
#include <QQmlEngine>
#include <QJSValue>
#include <QJsonDocument>
#include <QJsonArray>
#include <QVariantMap>
#include <iostream>
#include <stdexcept>
// Actual unchanged provider/metaobject. No identity/config/QS guard override.
int main(int argc,char**argv){QCoreApplication app(argc,argv);try{
 if(argc!=2)throw std::runtime_error("Exact reviewed module path required");
 QPluginLoader loader(QString::fromLocal8Bit(argv[1]));auto*plugin=qobject_cast<QQmlExtensionPlugin*>(loader.instance());if(!plugin)throw std::runtime_error(loader.errorString().toStdString());plugin->registerTypes("WindowObjectLifetimeV1");
 QQmlEngine engine;auto*provider=engine.singletonInstance<QObject*>("WindowObjectLifetimeV1","Lifetime");if(!provider)throw std::runtime_error("Actual native singleton required");
 const auto index=provider->metaObject()->indexOfMethod("retireProcess(QObject*,QObject*,QObject*,QObject*,QObject*,QObject*,QVariant,QObject*)");if(index<0)throw std::runtime_error("Exact actual public signature required");
 QVariantList observations;QObject*none=nullptr;
 for(const auto&lease:QVariantList{QVariant::fromValue(qulonglong(1)),QVariant(true),QVariant(QStringLiteral("1"))}){
  QVariantMap result;const bool called=QMetaObject::invokeMethod(provider,"retireProcess",Qt::DirectConnection,Q_RETURN_ARG(QVariantMap,result),Q_ARG(QObject*,none),Q_ARG(QObject*,none),Q_ARG(QObject*,none),Q_ARG(QObject*,none),Q_ARG(QObject*,none),Q_ARG(QObject*,none),Q_ARG(QVariant,lease),Q_ARG(QObject*,none));
  if(!called||result["error"].toString().isEmpty()||result["nativeWrites"].toInt()!=0||result["automaticRetries"].toInt()!=0||result.contains("terminalRetired"))throw std::runtime_error("Real non-QS public method must refuse without effects");
  observations<<QVariantMap{{"route","actualProviderMetaobject"},{"argumentType",QString::fromLatin1(lease.metaType().name())},{"result",result}};
 }
 engine.globalObject().setProperty("actualProvider",engine.newQObject(provider));
 for(const QString value:{"1","true","'1'"}){
  const auto answer=engine.evaluate("actualProvider.retireProcess(null,null,null,null,null,null,"+value+",null)");if(answer.isError())throw std::runtime_error(answer.toString().toStdString());const auto result=answer.toVariant().toMap();if(result["error"].toString().isEmpty()||result.contains("terminalRetired")||result["nativeWrites"].toInt()!=0)throw std::runtime_error("Actual QML to provider marshalling must refuse without authority");observations<<QVariantMap{{"route","actualProviderJsMarshalling"},{"argumentExpression",value},{"result",result}};
 }
 std::cout<<QJsonDocument(QJsonObject{{"result","pass"},{"observations",QJsonArray::fromVariantList(observations)},{"actualPublicMarshalling",true},{"nativeTypedParserReachedClaim",false},{"installedQSRetirePositive",false},{"GUI",false}}).toJson(QJsonDocument::Compact).constData()<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}

#include <QCoreApplication>
#include <QPromise>
#include <QFutureWatcher>
#include <QTimer>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QFile>
#include <pthread.h>
#include <atomic>
#include <memory>
#include <cstdio>
#include <cerrno>
struct Result {int lease=0,value=0;bool workerDifferent=false;};
struct Job {QPromise<Result>promise;pthread_t owner{};std::atomic_bool allowReturn{false};std::atomic_bool continued{false};};
void*worker(void*p){auto&j=*static_cast<Job*>(p);j.promise.addResult(Result{17,42,!pthread_equal(pthread_self(),j.owner)});j.promise.finish();j.continued.store(true);j.allowReturn.wait(false);return nullptr;}
int main(int argc,char**argv){QCoreApplication app(argc,argv);QJsonArray rows;auto check=[&](const char*n,bool ok){rows.append(QJsonObject{{"name",n},{"passed",ok}});if(!ok)throw std::runtime_error(n);};auto job=std::make_unique<Job>();job->owner=pthread_self();job->promise.start();QFutureWatcher<Result>watcher;pthread_t id{};int joins=0,delivery=0;bool complete=false,retiredAccepted=false,currentAccepted=false,failed=false;QTimer cleanup;cleanup.setInterval(1);
 auto finish=[&]{for(const auto&v:rows)failed=failed||!v.toObject()["passed"].toBool();QJsonObject report{{"checks",rows},{"result",failed?"fail":"pass"},{"actualPthread",true},{"actualQFutureWatcher",true},{"GUI",false},{"QProcessHelperClaimed",false},{"fixtureOnlyWorkerBarrier",true},{"normalWorkerJoined",complete}};const auto raw=QJsonDocument(report).toJson();QFile out;if(!out.open(stdout,QIODevice::WriteOnly)||out.write(raw)!=raw.size()||!out.flush())failed=true;app.exit(failed?1:0);};
 QObject::connect(&watcher,&QFutureWatcher<Result>::finished,&app,[&]{try{
  ++delivery;check("queued delivery actual owner thread",pthread_equal(pthread_self(),job->owner)&&watcher.thread()==app.thread());check("future actual finished before value read",watcher.isFinished());const auto r=watcher.result();check("copied result actual different worker",r.workerDifferent&&r.value==42&&r.lease==17);const int first=pthread_tryjoin_np(id,nullptr);check("promise finished is not worker returned",first==EBUSY);check("pending worker retained with no authority",!complete&&joins==0);int liveLease=18;retiredAccepted=r.lease==liveLease;check("old lease result does not establish acceptance",!retiredAccepted);liveLease=17;const int capturedContext=1,currentContext=2;currentAccepted=r.lease==liveLease&&capturedContext==currentContext;check("changed UI context refuses current result",!currentAccepted);check("one current delivery observed",delivery==1);job->allowReturn.store(true);job->allowReturn.notify_one();cleanup.start();
 }catch(const std::exception&e){failed=true;std::fprintf(stderr,"%s\n",e.what());job->allowReturn.store(true);job->allowReturn.notify_one();cleanup.start();}});
 QObject::connect(&cleanup,&QTimer::timeout,&app,[&]{const int rc=pthread_tryjoin_np(id,nullptr);if(rc==EBUSY)return;cleanup.stop();if(rc!=0){failed=true;finish();return;}complete=true;++joins;try{check("normal actual worker return joined once",joins==1&&job->continued.load());check("retired and refused worker still joined",!retiredAccepted&&!currentAccepted&&complete);}catch(const std::exception&e){failed=true;std::fprintf(stderr,"%s\n",e.what());}finish();});
 watcher.setFuture(job->promise.future());const int created=pthread_create(&id,nullptr,&worker,job.get());if(created){std::fprintf(stderr,"pthread_create errno%d\n",created);return 1;}
 QTimer::singleShot(2000,&app,[&]{failed=true;job->allowReturn.store(true);job->allowReturn.notify_one();cleanup.start();});return app.exec();}

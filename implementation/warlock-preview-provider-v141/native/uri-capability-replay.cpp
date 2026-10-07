#define main retained_uri_capability_main
#include "uri-capability-test.cpp"
#undef main
#include "preview_wire.hpp"
int main(){try{
 GError* error=nullptr;gsize length=0;auto view=reinterpret_cast<gpointer>(uintptr_t(77));auto realm=std::make_unique<ImageRealm>(1);uint64_t epoch=1;auto owner=preview_uri_router_new();check(owner,"Lifetime replay stable router");auto callback=preview_uri_router_ref(owner);check(preview_uri_router_bind(owner,realm->endpoint.get(),view,epoch,&error) && !error,"Lifetime replay original route");
 GInputStream* reader=nullptr;uint64_t readerEpoch=0;int readerFD=-1,last=0;std::string event;
 auto open=[&]{return preview_uri_router_open(callback,view,realm->image.c_str(),&length,&error);};
 auto errorClear=[&]{check(error && g_error_matches(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED),"Lifetime replay refusal category");g_clear_error(&error);};
 auto close=[&](GInputStream* value){check(g_input_stream_close(value,nullptr,&error) && !error,"Lifetime replay actual reader close");g_object_unref(value);};
 while(std::getline(std::cin,event)){
  last=1;
  if(event=="Open"){check(!reader,"Lifetime replay single held reader");reader=open();if(reader){readerEpoch=epoch;readerFD=realm->descriptor;check(!error && length==16,"Lifetime replay exact mapped image");}else {errorClear();last=-1;}}
  else if(event=="Read"){char byte{};last=g_input_stream_read(reader,&byte,1,nullptr,&error);if(last==-1)errorClear();else check(last==1 && !error,"Lifetime replay actual permitted byte");}
  else if(event=="CloseReader"){close(reader);reader=nullptr;readerEpoch=0;readerFD=-1;}
  else if(event=="DestroyEndpoint")realm->endpoint.reset();
  else if(event=="ReplaceReceiver"){realm->endpoint->unregisterView(77);check(realm->endpoint->registerView(77,{{1},{2},{3}},{1}),"Lifetime replay actual receiver replacement");epoch=realm->endpoint->registeredView(77)->epoch;}
  else if(event=="Bind"){if(!preview_uri_router_bind(callback,realm->endpoint.get(),view,epoch,&error)){errorClear();last=-1;}else check(!error,"Lifetime replay actual successful binding");}
  else if(event=="Clear")check(preview_uri_router_clear(callback,&error) && !error,"Lifetime replay original clear");
  else if(event=="NewRealm"){check(!reader && !realm->endpoint,"Lifetime replay old ownership drained before new fixture");realm=std::make_unique<ImageRealm>(++epoch);}
  else if(event=="Expire")*realm->now=50;
  else if(event=="ForeignBind"){ImageRealm foreign(epoch+1,4);check(!preview_uri_router_bind(callback,foreign.endpoint.get(),view,epoch+1,&error),"Lifetime replay foreign Native binding refusal");errorClear();last=-1;}
  else if(event=="DropOwner"){check(owner,"Lifetime replay original owner reference");preview_uri_router_unref(owner);owner=nullptr;}
  else throw std::runtime_error("Closed lifetime replay event domain");
  bool allowed=false;if(auto probe=open()){check(!error && length==16,"Lifetime replay observed allowed route");allowed=true;close(probe);}else errorClear();
  const bool physical=fcntl(realm->descriptor,F_GETFD)>=0;if(reader)check(fcntl(readerFD,F_GETFD)>=0,"Lifetime replay held physical descriptor");if(realm->endpoint)check(realm->endpoint->readers()==(reader?1:0),"Lifetime replay actual reader count");
  std::cout<<Wire().boolean("live",bool(realm->endpoint)).integer("epoch",epoch).boolean("expired",*realm->now>=50).boolean("reader",reader).integer("readerEpoch",readerEpoch).boolean("physical",physical).boolean("allowed",allowed).boolean("owner",owner).integer("last",last).finish()<<'\n';
 }
 if(reader)close(reader);check(preview_uri_router_clear(callback,&error) && !error,"Lifetime replay clear before final callback teardown");if(owner)preview_uri_router_unref(owner);preview_uri_router_unref(callback);const auto descriptor=realm->descriptor;realm.reset();check(fcntl(descriptor,F_GETFD)==-1 && errno==EBADF,"Lifetime replay actual normal physical closure");return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}

#pragma once
#include <json-c/json.h>
#include <memory>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>
// Encoding and typed equality only. No parser or fallback identity recovery.
class PinJson {
 std::shared_ptr<json_object> object_;
 static std::shared_ptr<json_object> hold(json_object*value){return {value,[](json_object*p){if(p)json_object_put(p);}};}
 explicit PinJson(json_object*value):object_(hold(value)){}
public:
 PinJson():PinJson(nullptr){}
 PinJson(std::nullptr_t):object_(hold(nullptr)){}
 PinJson(bool value):object_(hold(json_object_new_boolean(value))){}
 PinJson(int value):object_(hold(json_object_new_int(value))){}
 PinJson(const char*value):PinJson(std::string(value)){}
 PinJson(const std::string&value):object_(hold(json_object_new_string_len(value.data(),static_cast<int>(value.size())))){}
 PinJson(std::initializer_list<std::pair<std::string,PinJson>> fields):object_(hold(json_object_new_object())){
  for(const auto&[key,value]:fields)json_object_object_add(object_.get(),key.c_str(),json_object_get(value.object_.get()));
 }
 PinJson(const std::vector<PinJson>&values):object_(hold(json_object_new_array())){for(const auto&value:values)json_object_array_add(object_.get(),json_object_get(value.object_.get()));}
 static PinJson object(){return PinJson(json_object_new_object());}
 bool is_null()const{return !object_||json_object_get_type(object_.get())==json_type_null;}
 size_t size()const{return is_null()?0:json_object_object_length(object_.get());}
 PinJson at(const char*key)const{json_object*value=nullptr;if(!object_||!json_object_object_get_ex(object_.get(),key,&value))throw std::out_of_range("Missing structured pin result field");return PinJson(json_object_get(value));}
 template<typename T>T get()const{
  if constexpr(std::is_same_v<T,bool>){if(!object_||json_object_get_type(object_.get())!=json_type_boolean)throw std::runtime_error("Expected exact bool result");return json_object_get_boolean(object_.get());}
  else if constexpr(std::is_same_v<T,std::string>){if(!object_||json_object_get_type(object_.get())!=json_type_string)throw std::runtime_error("Expected exact string result");return std::string(json_object_get_string(object_.get()),json_object_get_string_len(object_.get()));}
 }
 struct Key{
  PinJson&parent;std::string name;
  void operator=(const PinJson&value){json_object_object_add(parent.object_.get(),name.c_str(),json_object_get(value.object_.get()));}
 };
 Key operator[](const std::string&key){return {*this,key};}
 std::string dump()const{return is_null()?"null":json_object_to_json_string_ext(object_.get(),JSON_C_TO_STRING_PLAIN);}
 friend bool operator==(const PinJson&a,const PinJson&b){if(a.is_null()||b.is_null())return a.is_null()&&b.is_null();return json_object_equal(a.object_.get(),b.object_.get());}
};

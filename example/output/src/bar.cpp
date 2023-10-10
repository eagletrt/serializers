#include "bar.hpp"

#include <google/protobuf/util/json_util.h>

namespace Serializers
{
MySmallMessage::MySmallMessage(const bar::MySmallMessage& proto) {
    val = proto.val();
}

MySmallMessage::operator bar::MySmallMessage() const {
    bar::MySmallMessage ret;
    ret.set_val(val);
    return ret;
}

std::string MySmallMessage::serializeAsProtobufString() const {
    bar::MySmallMessage proto(*this);
    return proto.SerializeAsString();
}

bool MySmallMessage::deserializeFromProtobufString(const std::string& str) {
    bar::MySmallMessage proto;
    if(proto.ParseFromString(str)) {
        *this = proto;
        return true;
    } else {
        return false;
    }
}

std::string MySmallMessage::serializeAsJsonString() const {
    bar:MySmallMessage proto(*this);
    std::string ret;
    google::protobuf::util::JsonPrintOptions options;
    options.add_whitespace = true;
    google::protobuf::util::MessageToJsonString(proto, &ret, options);
    return ret;
}

bool MySmallMessage::deserializeFromJsonString(const std::string& str) {
    bar::MySmallMessage proto;
    auto status = google::protobuf::util::JsonStringToMessage(str, &proto);
    if(status.ok()) {
        *this = proto;
        return true;
    } else {
        return false;
    }
}


MyMessage::MyMessage(const bar::MyMessage& proto) {
    val = proto.val();
    str = proto.str();
    enm = static_cast<MyEnum>(proto.enm());
    mySmallMessage = proto.mysmallmessage();
    for(const auto& e : proto.enumvec()) {
        enumVec.push_back(static_cast<MyEnum>(e));
    }
    structVec = {proto.structvec().begin(), proto.structvec().end()};
    stringMap = {proto.stringmap().begin(), proto.stringmap().end()};
    for(const auto& p : proto.enummap()) {
        enumMap.emplace(p.first, static_cast<MyEnum>(p.second));
    }
    structMap = {proto.structmap().begin(), proto.structmap().end()};
}

MyMessage::operator bar::MyMessage() const {
    bar::MyMessage ret;
    ret.set_val(val);
    ret.set_str(str);
    ret.set_enm(static_cast<bar::MyEnum>(enm));
    *(ret.mutable_mysmallmessage()) = mySmallMessage;
    for(const auto& e : enumVec) {
        ret.mutable_enumvec()->Add(static_cast<bar::MyEnum>(e));
    }
    *(ret.mutable_structvec()) = {structVec.begin(), structVec.end()};
    *(ret.mutable_stringmap()) = {stringMap.begin(), stringMap.end()};
    for(const auto& p : enumMap) {
        ret.mutable_enummap()->operator[](p.first) = static_cast<bar::MyEnum>(p.second);
    }
    *(ret.mutable_structmap()) = {structMap.begin(), structMap.end()};
    return ret;
}

std::string MyMessage::serializeAsProtobufString() const {
    bar::MyMessage proto(*this);
    return proto.SerializeAsString();
}

bool MyMessage::deserializeFromProtobufString(const std::string& str) {
    bar::MyMessage proto;
    if(proto.ParseFromString(str)) {
        *this = proto;
        return true;
    } else {
        return false;
    }
}

std::string MyMessage::serializeAsJsonString() const {
    bar:MyMessage proto(*this);
    std::string ret;
    google::protobuf::util::JsonPrintOptions options;
    options.add_whitespace = true;
    google::protobuf::util::MessageToJsonString(proto, &ret, options);
    return ret;
}

bool MyMessage::deserializeFromJsonString(const std::string& str) {
    bar::MyMessage proto;
    auto status = google::protobuf::util::JsonStringToMessage(str, &proto);
    if(status.ok()) {
        *this = proto;
        return true;
    } else {
        return false;
    }
}
}
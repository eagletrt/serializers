#include "foo.h"

#include <google/protobuf/util/json_util.h>

namespace Serializers
{
AnotherSmallMessage::AnotherSmallMessage(const bar::AnotherSmallMessage& proto) {
    val = proto.val();
}

AnotherSmallMessage::operator bar::AnotherSmallMessage() const {
    bar::AnotherSmallMessage ret;
    ret.set_val(val);
    return ret;
}

std::string AnotherSmallMessage::serializeAsProtobufString() const {
    bar::AnotherSmallMessage proto(*this);
    return proto.SerializeAsString();
}

bool AnotherSmallMessage::deserializeFromProtobufString(const std::string& str) {
    bar::AnotherSmallMessage proto;
    if(proto.ParseFromString(str)) {
        *this = proto;
        return true;
    } else {
        return false;
    }
}

std::string AnotherSmallMessage::serializeAsJsonString() const {
    bar::AnotherSmallMessage proto(*this);
    std::string ret;
    google::protobuf::util::JsonPrintOptions options;
    options.add_whitespace = true;
    google::protobuf::util::MessageToJsonString(proto, &ret, options);
    return ret;
}

bool AnotherSmallMessage::deserializeFromJsonString(const std::string& str) {
    bar::AnotherSmallMessage proto;
    auto status = google::protobuf::util::JsonStringToMessage(str, &proto);
    if(status.ok()) {
        *this = proto;
        return true;
    } else {
        return false;
    }
}
}
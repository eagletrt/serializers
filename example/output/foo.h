#ifndef FOO_HPP
#define FOO_HPP

#include "foo.pb.h"

#include <cstdint>
#include <string>
#include <vector>
#include <unordered_map>

namespace Serializers
{
struct AnotherSmallMessage
{
    int64_t val;
    
    AnotherSmallMessage() = default;
    AnotherSmallMessage(const bar::AnotherSmallMessage& proto);
    operator bar::AnotherSmallMessage() const;

    std::string serializeAsProtobufString() const;
    std::string serializeAsJsonString() const;
    bool deserializeFromProtobufString(const std::string& str);
    bool deserializeFromJsonString(const std::string& str);
};
}

#endif
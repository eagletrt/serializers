#ifndef BAR_HPP
#define BAR_HPP

#include "bar.pb.h"

#include <cstdint>
#include <string>
#include <vector>
#include <unordered_map>

namespace Serializers
{
struct MySmallMessage
{
    int64_t val;

    MySmallMessage() = default;
    MySmallMessage(const bar::MySmallMessage& proto);
    operator bar::MySmallMessage() const;

    std::string serializeAsProtobufString() const;
    std::string serializeAsJsonString() const;
    bool deserializeFromProtobufString(const std::string& str);
    bool deserializeFromJsonString(const std::string& str);
};


struct MyMessage
{
    double val;
    std::string str;
    std::vector<MySmallMessage> vec;
    std::unordered_map<uint32_t, std::string> mp;

    MyMessage() = default;
    MyMessage(const bar::MyMessage& proto);
    operator bar::MyMessage() const;

    std::string serializeAsProtobufString() const;
    std::string serializeAsJsonString() const;
    bool deserializeFromProtobufString(const std::string& str);
    bool deserializeFromJsonString(const std::string& str);
};
}

#endif
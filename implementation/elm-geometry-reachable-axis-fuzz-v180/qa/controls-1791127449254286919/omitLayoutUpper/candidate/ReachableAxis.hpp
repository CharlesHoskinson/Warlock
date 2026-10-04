#pragma once
#include <algorithm>
#include <cmath>
#include <climits>
#include <cstdint>
#include <optional>
namespace Elm::ExperimentalReachableAxis {
struct Input { int64_t first,last; double reserved,rawMinimum,rawMaximum,layoutMinimum,layoutMaximum; };
struct Range { int64_t first,last; double firstConfigure,lastConfigure; bool variable() const {return firstConfigure<lastConfigure;} };
inline std::optional<Range> solve(Input x) {
    auto valid=[](double v){return std::isfinite(v)&&v>=0;};
    if(x.first<1||x.last<x.first||x.last>int64_t(INT_MAX)+1||
       !valid(x.reserved)||!valid(x.rawMinimum)||!valid(x.rawMaximum)||
       !valid(x.layoutMinimum)||!valid(x.layoutMaximum)||
       (x.rawMaximum!=0&&x.rawMinimum>=x.rawMaximum)||
       x.layoutMaximum<=0||x.layoutMinimum>=x.layoutMaximum)return {};
    auto real=[&](int64_t n){return double(n)-x.reserved;};
    auto aboveLower=[&](int64_t n){const double r=real(n),c=std::floor(r);return r>0&&c>=1&&c>=x.rawMinimum&&r>=x.layoutMinimum;};
    auto belowUpper=[&](int64_t n){const double r=real(n),c=std::floor(r);return r<=INT_MAX&&(x.rawMaximum==0||c<=x.rawMaximum)&&r<=double(INT_MAX);};
    int64_t lo=x.first,hi=x.last+1;
    while(lo<hi){const auto mid=lo+(hi-lo)/2;if(aboveLower(mid))hi=mid;else lo=mid+1;}
    const auto first=lo;
    lo=x.first;hi=x.last+1;
    while(lo<hi){const auto mid=lo+(hi-lo)/2;if(belowUpper(mid))lo=mid+1;else hi=mid;}
    const auto last=lo-1;
    if(first>last||first>x.last||last<x.first)return {};
    return Range{first,last,std::floor(real(first)),std::floor(real(last))};
}
}

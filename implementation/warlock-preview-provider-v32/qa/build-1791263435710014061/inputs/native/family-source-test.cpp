#include "family_source.hpp"
#include <iostream>

int main(int argc,char** argv) {
    if(argc!=6)return 2;
    using namespace preview;using namespace preview::bridge;
    const Binding owner{{decimal(argv[1])},{decimal(argv[2])},{decimal(argv[3])}};
    const Id<Incarnation> subject{decimal(argv[4])};const uint64_t request=decimal(argv[5]);
    std::string line;std::getline(std::cin,line);
    try {
        Json input(line);const auto result=decodeFamilySource(input,owner,subject,request);
        std::cout<<"{\"accepted\":true,\"memberCount\":"<<result.members.size()<<",\"styleCount\":"<<result.styles.size()<<",\"crop\":{\"pixelX\":\""<<result.crop.x<<"\",\"pixelY\":\""<<result.crop.y<<"\",\"width\":"<<result.crop.width<<",\"height\":"<<result.crop.height<<",\"scale\":"<<result.crop.scale<<"}}\n";
    }catch(const std::exception&){std::cout<<"{\"accepted\":false}\n";}
    return 0;
}

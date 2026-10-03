#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
std::string trim(std::string x) { auto a=x.find_first_not_of(" "); if(a==std::string::npos)return {};return x.substr(a,x.find_last_not_of(" ")-a+1); }
struct ParserFixture { std::vector<std::string> seen;std::string getReply(std::string x){seen.push_back(x); return seen.size()==2?"error: CPU second action":"ok";} } fixture;
ParserFixture* g_pHyprCtl=&fixture;
static std::string dispatchBatch(eHyprCtlOutputFormat format, std::string request) {
    // split by ; ignores ; inside [] and adds ; on last command

    request                     = request.substr(9);
    std::string       reply     = "";
    const std::string DELIMITER = "\n\n\n";
    int               bracket   = 0;
    size_t            idx       = 0;

    for (size_t i = 0; i <= request.size(); ++i) {
        char ch = (i < request.size()) ? request[i] : ';';
        if (ch == '[')
            ++bracket;
        else if (ch == ']')
            --bracket;
        else if (ch == ';' && bracket == 0) {
            if (idx < i)
                reply += g_pHyprCtl->getReply(trim(request.substr(idx, i - idx))).append(DELIMITER);
            idx = i + 1;
            continue;
        }
    }

    return reply.substr(0, std::max(sc<int>(reply.size() - DELIMITER.size()), 0));
}
int main(){std::string x;std::getline(std::cin,x);std::cout<<dispatchBatch(x)<<"\n---fixture-seen---\n"; for(auto& y:fixture.seen)std::cout<<y<<"\n";}

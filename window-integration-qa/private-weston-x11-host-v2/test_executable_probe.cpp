#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <hyprutils/string/VarList.hpp>
using namespace Hyprutils::String;
namespace NFsUtils { bool executableExistsInPath(const std::string&); }
bool NFsUtils::executableExistsInPath(const std::string& exe) {
    if (!getenv("PATH"))
        return false;

    static CVarList paths(getenv("PATH"), 0, ':', true);

    for (auto& p : paths) {
        std::string     path = p + std::string{"/"} + exe;
        std::error_code ec;
        if (!std::filesystem::exists(path, ec) || ec)
            continue;

        if (!std::filesystem::is_regular_file(path, ec) || ec)
            continue;

        auto stat = std::filesystem::status(path, ec);
        if (ec)
            continue;

        auto perms = stat.permissions();

        return std::filesystem::perms::none != (perms & std::filesystem::perms::others_exec);
    }

    return false;
}

int main(){ std::cout << (NFsUtils::executableExistsInPath("Xwayland") ? "true" : "false") << "\n"; }

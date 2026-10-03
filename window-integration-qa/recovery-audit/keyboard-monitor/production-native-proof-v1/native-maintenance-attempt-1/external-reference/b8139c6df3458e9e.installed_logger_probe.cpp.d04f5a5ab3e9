#include <hyprutils/cli/Logger.hpp>
#include <fstream>
#include <iostream>
#include <string>
int main(int argc,char**argv){
    if(argc!=3)return 2;
    const std::string marker="Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend";
    const std::string configure="Output WAYLAND-1: configure surface with 1";
    {
        Hyprutils::CLI::CLogger logger;
        if(!logger.setOutputFile(argv[1]))return 3;
        logger.setEnableStdout(std::string(argv[2])=="stdout");logger.setEnableColor(false);
        logger.log(Hyprutils::CLI::LOG_DEBUG,marker);
        logger.log(Hyprutils::CLI::LOG_DEBUG,configure);
        // Keep the real logger and its actual buffered file stream alive until
        // the independent Python observer has checked disk/stdout visibility.
        std::string line;std::getline(std::cin,line);
    }
    std::ifstream stream(argv[1]);const std::string text((std::istreambuf_iterator<char>(stream)),{});
    return text.find(marker)!=std::string::npos&&text.find(configure)!=std::string::npos?0:4;
}

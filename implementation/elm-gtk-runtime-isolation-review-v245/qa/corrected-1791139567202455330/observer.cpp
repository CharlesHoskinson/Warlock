#include <filesystem>
#include <format>
#include <cstdlib>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <cstdio>
bool privateSession() {
    const auto runtime = std::getenv("XDG_RUNTIME_DIR");
    const auto backend = std::getenv("AQ_BACKENDS");
    if (!runtime || !backend || std::string(backend) != "wayland") return false;
    const std::filesystem::path path(runtime);
    if (path.parent_path() != std::filesystem::path(std::format("/run/user/{}/wqa", geteuid()))) return false;
    if (path.filename() == "." || path.filename() == "..") return false;
    std::error_code error;
    const auto resolved = std::filesystem::canonical(path, error);
    if (error || resolved.native() != path.native()) return false;
    struct stat info;
    return lstat(runtime, &info) == 0 && S_ISDIR(info.st_mode) &&
        info.st_uid == geteuid() && (info.st_mode & 0777) == 0700;
}

int main(){printf("%d\n",privateSession());return 0;}

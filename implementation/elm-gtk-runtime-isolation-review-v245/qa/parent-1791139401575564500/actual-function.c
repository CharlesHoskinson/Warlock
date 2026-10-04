static bool private_socket(void) {
    const char *gate = getenv("ELM_PARENT_INPUT_QA"), *socket = getenv("WAYLAND_DISPLAY"), *runtime = getenv("XDG_RUNTIME_DIR");
    if (!gate || strcmp(gate, "1") || !socket || !*socket) return false;
    char path[4096];
    int count = socket[0] == '/' ? snprintf(path, sizeof path, "%s", socket) :
        runtime ? snprintf(path, sizeof path, "%s/%s", runtime, socket) : -1;
    if (count < 0 || (size_t)count >= sizeof path) return false;
    struct stat info;
    return lstat(path, &info) == 0 && S_ISSOCK(info.st_mode) && info.st_uid == geteuid();
}

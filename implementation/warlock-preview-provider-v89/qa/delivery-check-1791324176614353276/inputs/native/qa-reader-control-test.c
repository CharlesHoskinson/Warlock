#define _GNU_SOURCE
#include <glib.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include "qa-reader-control.h"
int main(void) {
    g_autofree char *dir=g_dir_make_tmp("warlock-reader-control-XXXXXX",NULL);
    g_assert_nonnull(dir);g_assert_cmpint(chmod(dir,0700),==,0);
    g_autofree char *path=g_build_filename(dir,"control",NULL),*alias=g_build_filename(dir,"alias",NULL);
    g_assert_cmpint(qa_reader_control(path),==,QA_READER_INVALID);
    const char *valid[]={"hold\n","probe\n","release\n"};
    for(guint i=0;i<G_N_ELEMENTS(valid);i++) {
        g_assert_true(g_file_set_contents(path,valid[i],-1,NULL));g_assert_cmpint(chmod(path,0600),==,0);
        g_assert_cmpint(qa_reader_control(path),==,QA_READER_HOLD+(int)i);
    }
    const char *invalid[]={"","hold","hold\nextra","release\r\n","probe\n\0x","release\n\n"};
    for(guint i=0;i<G_N_ELEMENTS(invalid);i++) {
        g_assert_true(g_file_set_contents(path,invalid[i],i==4?8:-1,NULL));g_assert_cmpint(chmod(path,0600),==,0);
        g_assert_cmpint(qa_reader_control(path),==,QA_READER_INVALID);
    }
    g_assert_true(g_file_set_contents(path,"hold\n",-1,NULL));g_assert_cmpint(chmod(path,0644),==,0);
    g_assert_cmpint(qa_reader_control(path),==,QA_READER_INVALID);g_assert_cmpint(chmod(path,0600),==,0);
    g_assert_cmpint(link(path,alias),==,0);g_assert_cmpint(qa_reader_control(path),==,QA_READER_INVALID);g_assert_cmpint(unlink(alias),==,0);
    g_assert_cmpint(symlink(path,alias),==,0);g_assert_cmpint(qa_reader_control(alias),==,QA_READER_INVALID);g_assert_cmpint(unlink(alias),==,0);
    g_assert_cmpint(chmod(dir,0755),==,0);g_assert_cmpint(qa_reader_control(path),==,QA_READER_INVALID);g_assert_cmpint(chmod(dir,0700),==,0);
    g_assert_cmpint(unlink(path),==,0);g_assert_cmpint(mkfifo(path,0600),==,0);
    g_assert_cmpint(qa_reader_control(path),==,QA_READER_INVALID);g_assert_cmpint(unlink(path),==,0);
    g_assert_cmpint(rmdir(dir),==,0);g_print("{\"passed\":true,\"checks\":15}\n");return 0;
}

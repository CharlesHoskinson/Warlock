#pragma once
/* Private qualification stimulus; never supplies a grant, URI or policy fact. */
typedef enum { QA_READER_INVALID, QA_READER_HOLD, QA_READER_PROBE, QA_READER_RELEASE } QAReaderControl;
static QAReaderControl qa_reader_control(const char *path) {
    if(!path || !g_path_is_absolute(path))return QA_READER_INVALID;
    g_autofree char *directory=g_path_get_dirname(path),*name=g_path_get_basename(path);
    int parent=open(directory,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);struct stat dir,file;
    if(parent<0)return QA_READER_INVALID;
    int fd=-1;
    if(fstat(parent,&dir)==0 && dir.st_uid==getuid() && (dir.st_mode&0777)==0700)
        fd=openat(parent,name,O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK);
    close(parent);
    if(fd<0)return QA_READER_INVALID;
    char bytes[9]={0};ssize_t count=-1;
    if(fstat(fd,&file)==0 && S_ISREG(file.st_mode) && file.st_uid==getuid() &&
       (file.st_mode&0777)==0600 && file.st_nlink==1 && file.st_size>0 && file.st_size<=8)
        count=read(fd,bytes,sizeof(bytes));
    close(fd);
    if(count==5 && memcmp(bytes,"hold\n",5)==0)return QA_READER_HOLD;
    if(count==6 && memcmp(bytes,"probe\n",6)==0)return QA_READER_PROBE;
    if(count==8 && memcmp(bytes,"release\n",8)==0)return QA_READER_RELEASE;
    return QA_READER_INVALID;
}

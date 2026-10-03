#pragma once
// CPU diagnostic publication copied from reviewed V9 writer; no input authority.
void persistRouteEvidence(const QString&path,const QJsonObject&value){
  const auto evidencePath=path;const auto evidenceParent=QFileInfo(evidencePath).absolutePath();struct stat evidenceDirectory{};
  check((evidencePath==evidenceParent+"/before-hook.json"||evidencePath==evidenceParent+"/before-second-helper.json")&&QFileInfo(evidenceParent).canonicalFilePath()==evidenceParent&&lstat(evidenceParent.toUtf8().constData(),&evidenceDirectory)==0&&S_ISDIR(evidenceDirectory.st_mode)&&evidenceDirectory.st_uid==getuid()&&(evidenceDirectory.st_mode&07777)==0700,"Exact private diagnostic evidence directory required");
  const auto beforeHook=QJsonDocument(value).toJson(QJsonDocument::Compact);
  const int directoryFD=open(evidenceParent.toUtf8().constData(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);struct stat openedDirectory{};
  check(directoryFD>=0&&fstat(directoryFD,&openedDirectory)==0&&openedDirectory.st_dev==evidenceDirectory.st_dev&&openedDirectory.st_ino==evidenceDirectory.st_ino&&openedDirectory.st_uid==getuid()&&(openedDirectory.st_mode&07777)==0700,"Exact opened private evidence directory required");
  const int evidenceFD=openat(directoryFD,QFileInfo(evidencePath).fileName().toUtf8().constData(),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);check(evidenceFD>=0,"Exclusive before-hook evidence FD required");
  qsizetype written=0;while(written<beforeHook.size()){const auto n=write(evidenceFD,beforeHook.constData()+written,size_t(beforeHook.size()-written));if(n<0&&errno==EINTR)continue;check(n>0,"Complete before-hook evidence write required");written+=n;}
  struct stat evidenceFile{},namedDirectory{};check(fstat(evidenceFD,&evidenceFile)==0&&S_ISREG(evidenceFile.st_mode)&&evidenceFile.st_uid==getuid()&&(evidenceFile.st_mode&07777)==0600&&evidenceFile.st_size==beforeHook.size(),"Exact complete diagnostic evidence file required");
  check(fsync(evidenceFD)==0&&close(evidenceFD)==0&&fsync(directoryFD)==0&&lstat(evidenceParent.toUtf8().constData(),&namedDirectory)==0&&namedDirectory.st_dev==openedDirectory.st_dev&&namedDirectory.st_ino==openedDirectory.st_ino&&namedDirectory.st_mode==openedDirectory.st_mode&&namedDirectory.st_uid==openedDirectory.st_uid&&close(directoryFD)==0,"Before-hook evidence file/directory persisted before installation");
}

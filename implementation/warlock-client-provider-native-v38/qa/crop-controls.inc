   r['cropCaptureSamples']=[]
   def cropExchange(op,capture,transfer=0,version=2,expectedStatus=0):
    query=[magic,version,op,lifetime,session,frontend,4000+op,int(capture),int(subject),int(transfer)];count=28 if version==2 else 25
    with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as c:
     c.settimeout(3);c.connect('\0'+attached['previewFdAddress']);credentials=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));child=next(row for _,row in s.host.processes if row['name']=='hyprland');assert credentials[0]==child['pid'] and credentials[1]==os.getuid() and host.original.same_process(child);assert c.send(struct.pack('!10Q',*query))==80
     data,ancillary,flags,address=c.recvmsg(count*8,socket.CMSG_SPACE(8*4),socket.MSG_CMSG_CLOEXEC);rights=[]
     for level,kind,body in ancillary:
      assert level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS and len(body)%4==0;values=array.array('i');values.frombytes(body);rights.extend(values)
     assert len(data)==count*8 and not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC);words=struct.unpack('!'+str(count)+'Q',data);assert words[:3]==(magic,version,expectedStatus) and len(rights)==(1 if op==1 and expectedStatus==0 else 0)
     if expectedStatus==0:assert words[3:6]==(lifetime,session,frontend) and words[6]==4000+op and words[7]==int(capture) and words[8]==int(subject)
     return words,rights
   def cropCapture(name,value,dialog=None):
    beforeWindows=s.data('clients');scope=value['scope'];deadline=int(scope['now'])+2000000000
    captured=request('preview-family-crop-scoped-request',subjectIncarnation=subject,deadlineNs=str(deadline),context=scope['context'])
    check(name+'TypedNativeCropCapture',captured.get('kind')=='preview-family-crop-owned' and captured['planeSpace']=='native-family-cropped-pixels-unqualified' and captured['previewEligible'] is False,reply=captured)
    cropOrigin=[int(captured['pixelX']),int(captured['pixelY'])];scale=captured['pixelScale'];check(name+'NativeOutputScale',scale==1)
    boxes=[row['geometry'][4:8] for row in value['members']];left=math.floor(min(b[0] for b in boxes)*scale);top=math.floor(min(b[1] for b in boxes)*scale);right=math.ceil(max(b[0]+b[2] for b in boxes)*scale);bottom=math.ceil(max(b[1]+b[3] for b in boxes)*scale)
    check(name+'NativeContributorUnionBounds',cropOrigin==[left,top] and [captured['width'],captured['height']]==[right-left,bottom-top],source=value,captured=captured)
    state=request('preview-family-crop-state-request');check(name+'TypedNativeCropState',state.get('kind')=='preview-family-crop-owned' and state['captureRequest']==captured['captureRequest'] and state['pixelX']==captured['pixelX'] and state['pixelY']==captured['pixelY'])
    for op,reason in [('preview-family-state-request','preview-probe-unavailable'),('preview-family-retire-request','preview-probe-plane-mismatch'),('preview-popup-retire-request','preview-probe-plane-mismatch'),('preview-client-retire-request','preview-client-plane-mismatch')]:
     reply=request(op);check(name+op+'CannotAliasCrop',reply.get('reason')==reason,reply=reply)
    refused,_=cropExchange(1,captured['captureRequest'],version=1,expectedStatus=9);check(name+'LegacyFDVersionCannotImportCrop',refused[2]==9)
    h,rights=cropExchange(1,captured['captureRequest']);fd=rights[0];memory=None
    try:
     context=scope['context'];origin=struct.unpack('!2q',struct.pack('!2Q',h[25],h[26]));nativeScale=struct.unpack('!d',struct.pack('!Q',h[27]))[0]
     check(name+'ExactCropPlaneContextOriginDeadline',h[22]==67 and h[23]==deadline and h[10]<deadline and h[11]>=h[10] and list(h[12:14])==[captured['width'],captured['height']] and list(origin)==cropOrigin and nativeScale==scale and [h[3],h[8],h[9],h[18],h[19],h[20],h[21]]==[int(context[k]) for k in ['lifetime','incarnation','output','privacy','rendering','scene','content']],header=list(h))
     seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL;check(name+'ActualCropSealedFD',fcntl.fcntl(fd,fcntl.F_GET_SEALS)&seals==seals and fcntl.fcntl(fd,fcntl.F_GETFD)&fcntl.FD_CLOEXEC and os.fstat(fd).st_size==h[14])
     memory=mmap.mmap(fd,h[14],flags=mmap.MAP_SHARED,prot=mmap.PROT_READ);blob=memory[:];check(name+'CropCRC',zlib.crc32(blob)==h[17]);path=private/(name+'.png');path.write_bytes(blob);path.chmod(0o600)
     rootGeom=next(row['geometry'] for row in value['members'] if row['incarnation']==subject);point=[int(rootGeom[0]+20)-cropOrigin[0],int(rootGeom[1]+20)-cropOrigin[1]]
     argv=[pre['cropPixelOracle'],str(path),*map(str,point)]
     if dialog is not None:
      geom=next(row['geometry'][:4] for row in value['members'] if row['incarnation']==dialog);argv.extend(str(int(x)) for x in [geom[0]-cropOrigin[0],geom[1]-cropOrigin[1],geom[2],geom[3]])
     decoder=s.host.launch('pixels-'+name,argv,env=env);decoder.wait(timeout=5);check(name+'CropDecoderNormalExit',decoder.returncode==0);pixels=json.loads((private/('pixels-'+name+'.log')).read_text())
     check(name+'NativeRootPixelsPeerExcluded',pixels['rootRGBA'][0]>0 and pixels['rootRGBA'][1:]==[0,0,255] and pixels['green']==0,pixels=pixels)
     check(name+'CaptureNeverRelocatesNativeWindows',[(w['address'],w['at'],w['size']) for w in s.data('clients')]==[(w['address'],w['at'],w['size']) for w in beforeWindows])
     check(name+'NativeCropRetainsExactFamilyContext',familyNativeScope()['scope']['context']==scope['context'])
     check(name+'CropHeldExportRefusesRetire',request('preview-family-crop-retire-request').get('reason')=='preview-probe-import-outstanding')
     r['cropCaptureSamples'].append({'name':name,'source':value,'header':list(h),'pixels':pixels,'previewEligible':False,'hardwarePresentation':False})
    finally:
     if memory is not None:memory.close()
     os.close(fd)
    try:fcntl.fcntl(fd,fcntl.F_GETFD);raise RuntimeError('Crop FD unexpectedly live')
    except OSError as error:check(name+'PhysicalCropFDClosed',error.errno==9)
    released,_=cropExchange(2,captured['captureRequest'],h[16]);check(name+'ExactCropExportReleased',released[16]==h[16]);retired=request('preview-family-crop-retire-request');check(name+'NativeCropProducerRetired',retired.get('kind')=='preview-family-crop-retired' and retired['ownedBytes']=='0');return pixels,cropOrigin
   bareCrop,bareOrigin=cropCapture('crop-root',familyNativeScope());check('cropRootMatchesNativeMonitorStyle',bareCrop['rootRGBA']==absent['rootRGBA'] and bareOrigin==[73,73] and [bareCrop['width'],bareCrop['height']]==[334,254])
   n=len(logs());command('modal-create');wait(lambda:any(row['event']=='modal-configured' for row in logs()[n:]));cropDialog=wait(lambda:modalMember(modalFacts()))['incarnation'];command('modal-yellow');command('popup-create');wait(lambda:any(row.get('event')=='popup-buffercommit' and row.get('popupColor')==0xff00ffff for row in logs()))
   combinedCrop,combinedOrigin=cropCapture('crop-popup-modal',familyNativeScope(),cropDialog);check('cropActualRootPopupDialogInOnePlane',combinedCrop['styledCyan']==64*48 and [combinedCrop['styledCyanBox'][i]+combinedOrigin[i] for i in [0,1]]==[371,291] and combinedCrop['interiorYellow']==80*48,pixels=combinedCrop)
   command('popup-destroy');cropModalWindow=next(w for w in s.data('clients') if w['title']=='WARLOCK-MODAL-PROBE');target='address:'+cropModalWindow['address'];check('cropNegativeModalNativeMove',s.ctl('dispatch',"hl.dsp.window.move({x=-40,y=130,window='"+target+"'})").strip()=='ok');wait(lambda:next(w for w in s.data('clients') if w['address']==cropModalWindow['address'])['at']==[-40,130])
   negativeCrop,negativeOrigin=cropCapture('crop-negative-modal',familyNativeScope(),cropDialog);check('cropNegativeOriginRetainsEntireNativeModal',negativeOrigin[0]<0 and negativeCrop['interiorYellow']==80*48,pixels=negativeCrop)
   check('cropFullyOffscreenModalNativeMove',s.ctl('dispatch',"hl.dsp.window.move({x=-180,y=130,window='"+target+"'})").strip()=='ok');wait(lambda:next(w for w in s.data('clients') if w['address']==cropModalWindow['address'])['at']==[-180,130]);offscreen=familyNativeScope();offMember=next(row for row in offscreen['members'] if row['incarnation']==cropDialog);check('cropNativeModalGenuinelyOutsideMonitor',offMember['geometry'][4]+offMember['geometry'][6]<0 and bool(offMember['flags']&16) and not offMember['flags']&32,member=offMember)
   offCrop,offOrigin=cropCapture('crop-offscreen-modal',offscreen,cropDialog);check('cropFullyOffscreenNativeModalRetainsPixels',offOrigin[0]<-180 and offCrop['interiorYellow']==80*48 and offCrop['yellow']==negativeCrop['yellow'] and offCrop['rootRGBA']==negativeCrop['rootRGBA'],pixels=offCrop)
   command('modal-destroy');wait(lambda:modalMember(modalFacts()) is None)

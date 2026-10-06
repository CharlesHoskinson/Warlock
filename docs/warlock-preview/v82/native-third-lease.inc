   # The companion kept its original request1 while its lease2 resume waited.
   # Only a distinct explicit lease3 may replace that expired unissued intent.
   def resumeLocalRows():
    return [event for line in fullLog().splitlines() if line.startswith('native-imported-feedback: ') for event in json.loads(line[len('native-imported-feedback: '):]) if event['kind']=='demand-feedback' and event['subject']==feedbackPeer and event['lease']==nextSeed['lease']]
   expiredResume=wait(lambda:next((event for event in reversed(resumeLocalRows()) if event['outcome']=='expired'),None))
   oldCompanion=next(frame for frame in firstOffers if frame['job']['context']['incarnation']==feedbackPeer)
   statuses=[json.loads(line[len('native-imported-ownership: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ownership: ')]
   oldOwner=next(row for row in statuses[-1] if row['job']['context']['incarnation']==feedbackPeer)
   companionRequests=[event['event']['trigger'] for event in events() if event['kind']=='event' and event['event']['kind']=='request' and event['identity']=='family:'+feedbackPeer]
   check('nextResumeGUIExpiredWaitingIntentKeepsOriginalJobAndCutoff',companionRequests==[oldCompanion['job']] and oldOwner['job']==oldCompanion['job'] and oldOwner['resumeDeadline']==expiredResume['deadline'] and oldOwner['resumeLease']==nextSeed['lease'] and all(event['deadline']==expiredResume['deadline'] for event in resumeLocalRows()),owner=oldOwner,expired=expiredResume)
   check('nextResumeGUIOldPhysicalAndTerminalOwnersDrained',nextPoolDrained() and all(row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] and not row['retirementPending'] for row in statuses[-1]) and sum(json.loads(line[len('native-imported-ack: '):])['job']==oldCompanion['job'] for line in fullLog().splitlines() if line.startswith('native-imported-ack: '))==1,status=statuses[-1])
   closeOffset=len(fullLog());nextIntentClick('resume-close');wait(lambda:'view-commit: popup=0 ' in fullLog()[closeOffset:])
   nextIntentClick('resume-reopen')
   def successorResumeOffer():
    return next((event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer' and event['identity']=='family:'+feedbackPeer and int(event['event']['frame']['job']['request'])>1),None)
   resumedOffer=wait(successorResumeOffer)
   resumedSeed=next(event for event in events() if event['kind']=='source-seed' and event['identity']=='family:'+feedbackPeer and int(event['lease'])>int(expiredResume['lease']))
   resumedJob=resumedOffer['job']
   check('nextResumeGUIExactNextRequestAndLaterPickerLease',resumedJob['request']=='2' and resumedJob['binding']==oldCompanion['job']['binding'] and resumedJob['clock']==oldCompanion['job']['clock'] and resumedJob['context']['incarnation']==feedbackPeer and resumedJob['context']['lifetime']==oldCompanion['job']['context']['lifetime'] and resumedJob['origin']==resumedSeed['lease'] and int(resumedSeed['publication'])>int(expiredResume['publication']) and int(resumedSeed['lease'])>int(expiredResume['lease']),previous=oldCompanion,seed=resumedSeed,offer=resumedOffer)
   check('nextResumeGUIFreshNativeTwoSecondCutoff',int(resumedJob['deadline'])==int(resumedSeed['source']['scope']['now'])+2000000000 and int(resumedJob['deadline'])>int(expiredResume['deadline']),expired=expiredResume['deadline'],current=resumedJob['deadline'])
   resumedURI='elm-shell://preview/'+resumedOffer['handle']
   def resumedImages():
    return next((images for line in reversed(fullLog().splitlines()) if line.startswith('native-imported-image: ') for images in [json.loads(line[len('native-imported-image: '):])] if any(image['uri']==resumedURI for image in images)),None)
   loadedResume=wait(resumedImages)
   check('nextResumeGUIActualOwnedURIComplete',any(image['uri']==resumedURI and image['complete'] and image['naturalWidth']==320 and image['naturalHeight']==240 for image in loadedResume),images=loadedResume)
   wait(lambda:any(json.loads(line[len('native-imported-ack: '):])['job']==resumedJob for line in fullLog().splitlines() if line.startswith('native-imported-ack: ')))
   wait(nextPoolDrained)
   resumedAcquires=[json.loads(line[len('native-imported-command: '):])['job'] for line in fullLog().splitlines() if line.startswith('native-imported-command: ') and json.loads(line[len('native-imported-command: '):])['kind']=='acquire' and json.loads(line[len('native-imported-command: '):])['job']['context']['incarnation']==feedbackPeer]
   check('nextResumeGUIOriginalAndSuccessorCaptureAndACKExactlyOnce',resumedAcquires==[oldCompanion['job'],resumedJob] and sum(json.loads(line[len('native-imported-ack: '):])['job']==resumedJob for line in fullLog().splitlines() if line.startswith('native-imported-ack: '))==1,acquires=resumedAcquires)
   statuses=[json.loads(line[len('native-imported-ownership: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ownership: ')]
   check('nextResumeGUIAllPhysicalAndJournalOwnersDrained',all(row['records']==0 and int(row['charge'])==0 and row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] and not row['retirementPending'] for row in statuses[-1]),status=statuses[-1])
   r['nextResumeGUIEvidence']={'sameHostPID':web.pid,'expired':expiredResume,'previous':oldCompanion,'oldOwner':oldOwner,'seed':resumedSeed,'offer':resumedOffer,'images':loadedResume,'exactACK':True,'finalOwnership':statuses[-1],'hardwarePresentation':False,'assistiveTechnologyAcceptance':False};r['nativeNextResumeIntentGUIBoundedQualified']=True

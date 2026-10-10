import json,os,sys
with open(sys.argv[1],"a") as stream:stream.write(json.dumps({"argv":sys.argv[2:],"pid":os.getpid(),"normalExit":True})+"\n")

# CPU-only controlled QProcess producer. This is not a product Pin helper.
import os,sys,json
# The fixture waits for its test controller, allowing actual kernel witness
# registration. The production observer never writes stdin or starts a child.
mode=sys.argv[1]
os.read(0,1)
if mode=='crash':os.abort()
receipt=json.dumps({'cpuFixture':True,'pid':os.getpid(),'code':2 if mode=='refusal' else 0})+'\n'
if mode=='refusal':sys.stderr.write(receipt)
else:sys.stdout.write(receipt)

sys.exit(2 if mode=='refusal' else 0)

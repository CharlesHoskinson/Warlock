"""Serve the bundled brand preview on loopback only."""
import argparse,functools,http.server,pathlib
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=8404);args=parser.parse_args()
if not 1<=args.port<=65535:parser.error('port must be in 1–65535')
root=pathlib.Path(__file__).resolve().parent.parent
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),handler)
print('Warlock brand preview: http://127.0.0.1:'+str(args.port)+'/v1/',flush=True)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()

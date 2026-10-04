"""Own peer PID/binding for added grab refusal, preserving campaign binding."""
import json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1]);from effect_endpoint import Endpoint
client=Endpoint(**json.loads(Path(sys.argv[2]).read_text()));client.hello();facts=client.scene_facts('1')
print(json.dumps(client.effect({'request':'1','generation':'1','incarnation':sys.argv[3],'operation':'minimize','context':client.context(facts)})))

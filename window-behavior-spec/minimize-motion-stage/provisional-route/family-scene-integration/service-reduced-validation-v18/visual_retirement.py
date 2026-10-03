"""Separate owned visual closure; no request or native validation authority."""
from copy import deepcopy
from dataclasses import dataclass

@dataclass
class VisualRetirement:
    token:str
    session:str
    transport:object
    origin:object
    receipt:int
    members:list
    sources:list
    attempted:bool=False
    queued:bool=False
    acknowledged:bool=False
    uncertain:bool=False
    error:str | None=None

    def snapshot(self):
        return {'token':self.token,'controllerSession':self.session,'receiptAtReservation':self.receipt,
            'members':deepcopy(self.members),'sources':deepcopy(self.sources),'attempted':self.attempted,
            'queued':self.queued,'acknowledged':self.acknowledged,'uncertain':self.uncertain,'error':self.error}

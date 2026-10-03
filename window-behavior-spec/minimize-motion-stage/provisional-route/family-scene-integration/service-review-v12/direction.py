"""Accepted symbolic direction; neither a native observation nor authority."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Direction:
    anchor: str
    inverted: bool = False
    identity: tuple | None = None
    def __post_init__(self):
        if self.anchor not in ('minimize','restore','toggle','activate'):
            raise ValueError('invalid symbolic direction')
    @property
    def constant(self):
        if self.anchor not in ('minimize','restore'):return None
        if not self.inverted:return self.anchor
        return 'restore' if self.anchor=='minimize' else 'minimize'
    def reverse(self):
        constant=self.constant
        return Direction('restore' if constant=='minimize' else 'minimize') if constant else Direction(self.anchor,not self.inverted,self.identity)
    def resolve(self,window,active=None):
        if self.constant:return self.constant
        minimized=window.get('workspace',{}).get('name')=='special:win-minimized'
        if self.anchor=='activate' and active is None:raise ValueError('activation requires fresh active identity observation')
        toward_minimize=(not minimized) if self.anchor=='toggle' else (not minimized and active==window['address'])
        if self.inverted:toward_minimize=not toward_minimize
        return 'minimize' if toward_minimize else 'restore'

def compose(command,previous=None,*,captured=None):
    if command in ('minimize','restore'):return Direction(command)
    if command not in ('toggle','activate'):raise ValueError('invalid direction command')
    return previous.reverse() if previous else Direction(command,identity=captured)

#!/usr/bin/env python3
"""Reject malformed support metadata before source CAS; never authorize or mutate."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import subprocess

SUPPORT_EVIDENCE='.warlock-contributor/evidence/support-custody/'
FIELDS={'path','recordSnapshot','currentSnapshot','claimProof','reviewFile','reason'}

def relative(value,prefix):
    if (not isinstance(value,str)or not value.startswith(prefix)or '\x00'in value or '\\'in value
            or PurePosixPath(value).is_absolute()or '..'in PurePosixPath(value).parts
            or str(PurePosixPath(value))!=value or value.endswith('/')):
        raise ValueError('Noncanonical support metadata path: '+str(value))
    return value

def validate_plan(transition_file,entries,proofs,expected_paths,run,agent,environment):
    relative(transition_file,'.warlock-contributor/')
    if (not isinstance(run,str)or not run or not isinstance(agent,str)or not agent
            or environment.get('AGENTBUS_RUN')!=run or environment.get('AGENTBUS_AGENT')!=agent):
        raise ValueError('Set the exact assigned AgentBus run and actual claim agent before CAS')
    if (not isinstance(entries,list)or not entries or not isinstance(expected_paths,list)or not expected_paths
            or len(set(expected_paths))!=len(expected_paths)
            or any(not isinstance(item,dict)or set(item)!=FIELDS for item in entries)):
        raise ValueError('Exact existing support transition fields and destination batch required')
    names=[item['path']for item in entries]
    if len(set(names))!=len(names)or set(names)!=set(expected_paths):
        raise ValueError('Support destination batch differs from the caller reviewed exact paths')
    for item in entries:
        relative(item['path'],'')
        if not isinstance(item['reason'],str)or not item['reason'].strip():raise ValueError('Support reason required')
        for key in ('recordSnapshot','currentSnapshot','claimProof','reviewFile'):relative(item[key],SUPPORT_EVIDENCE)
        proof=proofs.get(item['claimProof'])
        if (not isinstance(proof,dict)or proof.get('schema')!=1 or proof.get('run')!=run
                or proof.get('claimOwner',proof.get('owner'))!=agent):
            raise ValueError('Frozen proof differs from assigned actual claim actor/run')
    return {'scopePrecheckPassed':True,'paths':names,'assignedRun':run,'assignedAgent':agent,
            'effectsPerformed':False,'ownershipOrExecutionAuthorized':False,
            'remainingChecks':'Keep the existing locks, source edit guard, live claims, snapshot/hash/review checks and canonical reconciliation.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,required=True);parser.add_argument('--transition-file',required=True);parser.add_argument('--run',required=True);parser.add_argument('--claim-owner',required=True);parser.add_argument('--path',action='append',required=True);a=parser.parse_args()
    root=a.repo.resolve();relative(a.transition_file,'.warlock-contributor/')
    entries=json.loads((root/a.transition_file).read_text());proofs={}
    if not isinstance(entries,list):raise ValueError('Transition array required')
    for item in entries:
        if not isinstance(item,dict)or set(item)!=FIELDS:raise ValueError('Exact transition fields required')
        for key in ('recordSnapshot','currentSnapshot','claimProof','reviewFile'):
            name=relative(item[key],SUPPORT_EVIDENCE)
            result=subprocess.run(['/usr/bin/git','-C',str(root),'check-ignore','-q','--',name],check=False)
            if result.returncode!=0:raise ValueError('Support evidence must remain Git-ignored: '+name)
        proof=relative(item['claimProof'],SUPPORT_EVIDENCE);proofs[proof]=json.loads((root/proof).read_text())
    if subprocess.run(['/usr/bin/git','-C',str(root),'check-ignore','-q','--',a.transition_file],check=False).returncode!=0:raise ValueError('Transition file must remain Git-ignored')
    print(json.dumps(validate_plan(a.transition_file,entries,proofs,a.path,a.run,a.claim_owner,os.environ),sort_keys=True))
if __name__=='__main__':main()

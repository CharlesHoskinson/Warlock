"""Apply the explicit user-authorized language revision, preserving original IDs."""
import hashlib,json

def apply_language_revision(document,root):
 revision=json.loads((root/'language-revision.json').read_text())
 baseline=(root/revision['baseline']).read_bytes()
 if hashlib.sha256(baseline).hexdigest()!=revision['baselineSHA256']:
  raise ValueError('Frozen pre-language requirement baseline changed')
 original=json.loads(baseline)
 if document!=original:raise ValueError('Unapproved source drift before language revision; review a new explicit revision instead')
 identity=lambda data:[(r['id'],[s['name'] for s in r['scenarios']]) for r in data['requirements']]
 if identity(document)!=identity(original):raise ValueError('Requirement or scenario identities drifted before language revision')
 for change in revision['changes']:
  parts=change['pointer'].strip('/').split('/');row=document['requirements'][int(parts[1])]
  if row['id']!=change['id']:raise ValueError('Language revision ID mismatch')
  value=document
  for part in parts[:-1]:value=value[int(part)] if isinstance(value,list) else value[part]
  key=int(parts[-1]) if isinstance(value,list) else parts[-1]
  if value[key]!=change['before']:raise ValueError('Language revision precondition failed: '+change['pointer'])
  value[key]=change['after']
 if identity(document)!=identity(original):raise ValueError('Language revision changed identities')
 expected=json.loads(baseline)
 for change in revision['changes']:
  parts=change['pointer'].strip('/').split('/');value=expected
  for part in parts[:-1]:value=value[int(part)] if isinstance(value,list) else value[part]
  key=int(parts[-1]) if isinstance(value,list) else parts[-1];value[key]=change['after']
 if document!=expected:raise ValueError('Language revision changed unapproved fields')
 return document

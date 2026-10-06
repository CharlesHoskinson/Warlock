"""Prepare the exact current public delivery receipt commit."""
import ast,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=r/'docs/warlock-repository/v60/publication'
d=json.loads((base/'delivery.json').read_text());assert d['pushCompleted'] and d['ownedFiles']==8175 and d['sourceCommit']=='a0dd6aeca3b8beaa0266b5f535506f1dc5cc06bb' and d['publishedCommit']=='03582f63a0612b972bf0ad71033e3d4e8b46531b' and d['remoteObserved']==d['publishedCommit']
text=(r/'docs/warlock-repository/v59/publication/commit_receipt.py').read_text()
text=text.replace('83e294879448f428b980001ea80d6ea7b1048133',d['sourceCommit']).replace('ba21f432bdccd8ac82c1e5a461ee6c5b251988cb',d['publishedCommit']).replace("d['ownedFiles']==4548","d['ownedFiles']==8175")
text=text.replace('Record public native window retirement observation qualification','Record public typed C native retirement observation qualification')
ast.parse(text);target=base/'commit_receipt.py';assert not target.exists();target.write_text(text);print(target)

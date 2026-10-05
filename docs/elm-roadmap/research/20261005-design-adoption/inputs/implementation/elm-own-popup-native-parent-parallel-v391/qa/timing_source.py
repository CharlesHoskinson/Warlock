"""QA-only exact declared measurement normalization from timing-test.py."""
import ast,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def original_ast(source):
    tree = ast.parse(source)
    counts = {'calls': 0, 'context': 0, 'import': 0, 'setup': 0}
    allowed = {'preflight': None, 'guardQualification': None, 'initialTuple': 'initial_deadline', 'fullProcessGuard': 'deadline', 'GTKLaunch': 'boot', 'GTKCreateOwners': 'boot', 'GTKInspect': 'boot', 'WebHostLaunch': 'boot', 'privateParentMap': 'boot', 'hostRuntimeGuard': 'boot'}

    class Strip(ast.NodeTransformer):

        def visit_ImportFrom(self, n):
            if n.module == 'budget_timing':
                assert [x.name for x in n.names] == ['BudgetTiming']
                counts['import'] += 1
                return None
            return n

        def visit_Assign(self, n):
            if ast.dump(n) == ast.dump(ast.parse('timing=BudgetTiming(r)').body[0]):
                counts['setup'] += 1
                return None
            if ast.dump(n) == ast.dump(ast.parse("original_wait=globals()['wait']").body[0]):
                counts['setup'] += 1
                return None
            return self.generic_visit(n)

        def visit_FunctionDef(self, n):
            expected = ast.parse("def wait(session,fn,deadline):return timing.call('wait:'+timing.label(fn),deadline,lambda:original_wait(session,fn,deadline))").body[0]
            if ast.dump(n) == ast.dump(expected):
                counts['setup'] += 1
                return None
            return self.generic_visit(n)

        def visit_Call(self, n):
            if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and (n.func.value.id == 'timing'):
                assert not n.keywords and len(n.args) == 3
                if n.func.attr == 'context':
                    assert ast.literal_eval(n.args[0]) == 'privateSession' and ast.literal_eval(n.args[1]) is None
                    counts['context'] += 1
                    return n.args[2]
                assert n.func.attr == 'call'
                counts['calls'] += 1
                if isinstance(n.args[0], ast.Constant):
                    label = n.args[0].value
                    assert label in allowed
                    d = allowed[label]
                    assert isinstance(n.args[1], ast.Constant) and n.args[1].value is None if d is None else isinstance(n.args[1], ast.Name) and n.args[1].id == d
                else:
                    assert ast.dump(n.args[0]) == ast.dump(ast.parse("'queryCallback:'+timing.label(call)", mode='eval').body) and ast.dump(n.args[1]) == ast.dump(ast.parse('bounded.deadline', mode='eval').body)
                call = n.args[2]
                if isinstance(call, ast.Lambda):
                    assert not call.args.args
                    return call.body
                assert isinstance(call, ast.Name) and call.id in ('verify', 'checked_guard', 'call')
                return ast.Call(func=call, args=[], keywords=[])
            return self.generic_visit(n)
    tree = Strip().visit(tree)
    old = ast.parse((ROOT.parent / 'elm-own-popup-native-index-guard-v365/qa/native.py').read_text())
    assert counts == {'calls': 11, 'context': 1, 'import': 1, 'setup': 3}
    assert ast.dump(tree) == ast.dump(old)
    return tree

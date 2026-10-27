import ast
import glob
import os

# translation lookups that cannot work: a message formatted before _() looks
# up the formatted text (bugs/config-i18n/3), and a translated string used as
# an attribute or save name changes with $LANG (bugs/config-i18n/2, 4)


def calls():
    root = os.path.join(os.path.dirname(__file__), "..", "trelby")
    for path in sorted(glob.glob(os.path.join(root, "**", "*.py"), recursive=True)):
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                yield os.path.basename(path), n


def isTranslate(n):
    return (
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_"
    )


def testNoFormatInsideTranslate():
    bad = []
    for name, n in calls():
        if isTranslate(n) and n.args:
            a = n.args[0]
            if isinstance(a, ast.Call) and getattr(a.func, "attr", None) == "format":
                bad.append("%s:%d" % (name, n.lineno))
    assert bad == []


def files():
    root = os.path.join(os.path.dirname(__file__), "..", "trelby")
    for path in sorted(glob.glob(os.path.join(root, "**", "*.py"), recursive=True)):
        with open(path, encoding="utf-8") as f:
            yield os.path.basename(path), ast.parse(f.read())


def hasTranslate(n):
    return any(isTranslate(x) for x in ast.walk(n))


# parameters of a method that end up in a setattr name: {name: [index]}
def nameParams(tree):
    ret = {}
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef):
            continue
        params = [a.arg for a in fn.args.args]
        for n in ast.walk(fn):
            if (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name)
                and n.func.id == "setattr"
                and len(n.args) > 1
            ):
                used = {x.id for x in ast.walk(n.args[1]) if isinstance(x, ast.Name)}
                idx = [i - 1 for i, p in enumerate(params) if p in used and i > 0]
                if idx:
                    ret[fn.name] = idx
    return ret


def testNoTranslatedNames():
    bad = []
    for name, tree in files():
        helpers = nameParams(tree)
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            args = []
            # setattr(obj, <name>, value)
            if isinstance(f, ast.Name) and f.id == "setattr" and len(n.args) > 1:
                args = [n.args[1]]
            # Vars.add*(name, default, saveName, ...) on mypickle's v
            elif (
                isinstance(f, ast.Attribute)
                and isinstance(f.value, ast.Name)
                and f.value.id == "v"
                and f.attr.startswith("add")
                and len(n.args) > 2
            ):
                args = [n.args[0], n.args[2]]
            # self.helper(...) whose argument becomes a setattr name
            elif (
                isinstance(f, ast.Attribute)
                and isinstance(f.value, ast.Name)
                and f.value.id == "self"
                and f.attr in helpers
            ):
                args = [n.args[i] for i in helpers[f.attr] if i < len(n.args)]
            if any(hasTranslate(a) for a in args):
                bad.append("%s:%d" % (name, n.lineno))
    assert bad == []

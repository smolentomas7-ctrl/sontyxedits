"""Static API check: every call from the shot scripts into the scene libraries must match the real signatures.

blender -b --factory-startup -P scenes/tests/api_check.py
Parses scenes/*.py and scenes/lib/rb_montage.py with ast, resolves calls through the module aliases they import
(MT.fx("name", ...) is resolved to rb_vfx.name), and binds the call's positional count / keyword names against
inspect.signature of the target. Prints one line per problem and a summary.
"""
import ast
import glob
import importlib
import inspect
import os
import sys

LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib")
SCN = os.path.dirname(LIB)
sys.path.insert(0, LIB)

mods = {}
for name in ("rb_core", "rb_cam", "rb_montage", "rb_intro", "rb_story", "rb_motion", "rb_actions", "rb_warrior",
             "rb_god", "rb_mat", "rb_shot", "rb_vfx", "rb_props", "rb_env_dungeon", "rb_env_arena", "rb_env_forest",
             "rb_env_heaven", "rb_enemies"):
    try:
        mods[name] = importlib.import_module(name)
    except Exception as e:  # noqa: BLE001
        print("IMPORT FAIL", name, repr(e))


def aliases(tree):
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                out[a.asname or a.name] = a.name
    return out


def check_call(fn, call, label, problems):
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return
    params = sig.parameters
    has_var_kw = any(p.kind == p.VAR_KEYWORD for p in params.values())
    has_var_pos = any(p.kind == p.VAR_POSITIONAL for p in params.values())
    pos_params = [p for p in params.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    npos = len(call.args)
    if any(isinstance(a, ast.Starred) for a in call.args) or any(k.arg is None for k in call.keywords):
        return
    if npos > len(pos_params) and not has_var_pos:
        problems.append("%s: %d positional args, %s takes %d" % (label, npos, getattr(fn, "__name__", fn), len(pos_params)))
    given = {p.name for p in pos_params[:npos]}
    for k in call.keywords:
        if k.arg not in params and not has_var_kw:
            problems.append("%s: unknown keyword '%s' for %s%s" % (label, k.arg, getattr(fn, "__name__", fn), sig))
        elif k.arg in given:
            problems.append("%s: '%s' given positionally and by keyword" % (label, k.arg))
        given.add(k.arg)
    missing = [p.name for p in pos_params if p.default is p.empty and p.name not in given]
    if missing and not has_var_pos:
        problems.append("%s: missing required %s for %s" % (label, missing, getattr(fn, "__name__", fn)))


problems = []
files = sorted(glob.glob(os.path.join(SCN, "*.py"))) + [os.path.join(LIB, "rb_montage.py")]
ncalls = 0
for path in files:
    tree = ast.parse(open(path).read())
    al = aliases(tree)
    if path.endswith("rb_montage.py"):
        al.update({"C": "rb_core", "M": "rb_mat", "MO": "rb_motion", "ST": "rb_story"})
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Attribute):
            continue
        base = n.func.value
        # MT.fx("name", ...) -> rb_vfx.name(...)
        if isinstance(base, ast.Name) and al.get(base.id) == "rb_montage" and n.func.attr == "fx":
            if n.args and isinstance(n.args[0], ast.Constant) and "rb_vfx" in mods:
                tgt = getattr(mods["rb_vfx"], n.args[0].value, None)
                lab = "%s:%d MT.fx(%r)" % (os.path.basename(path), n.lineno, n.args[0].value)
                if tgt is None:
                    problems.append(lab + ": rb_vfx has no %s" % n.args[0].value)
                else:
                    sub = ast.Call(func=n.func, args=n.args[1:], keywords=n.keywords)
                    check_call(tgt, sub, lab, problems)
                    ncalls += 1
            continue
        # MT.MO.x / MT.ST.x style chains
        modname = None
        if isinstance(base, ast.Name):
            modname = al.get(base.id)
        elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name) and al.get(base.value.id) == "rb_montage":
            modname = {"MO": "rb_motion", "ST": "rb_story", "C": "rb_core", "M": "rb_mat"}.get(base.attr)
        if modname not in mods:
            continue
        tgt = getattr(mods[modname], n.func.attr, None)
        lab = "%s:%d %s.%s" % (os.path.basename(path), n.lineno, modname, n.func.attr)
        if tgt is None:
            problems.append(lab + ": no such attribute")
            continue
        if callable(tgt):          # classes: inspect.signature(cls) already drops `self`
            check_call(tgt, n, lab, problems)
            ncalls += 1
for p in problems:
    print("API", p)
print("API_CHECK %d calls checked, %d problems" % (ncalls, len(problems)))
